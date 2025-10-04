# backend/app.py

import os
from flask import Flask, jsonify, request, make_response, g
from dotenv import load_dotenv
import jwt
from flask_cors import CORS
import requests
from functools import wraps
from supabase import create_client, Client

load_dotenv()
app = Flask(__name__)
CORS(app, 
    resources={r"/api/*": {"origins": "http://localhost:8080"}},
    supports_credentials=True
)

# --- FUNCIÓN DE BROADCAST (Sin cambios) ---
def broadcast_change(event_type, new_data=None, old_data=None):
    try:
        supabase_url = os.getenv("SUPABASE_URL")
        service_key = os.getenv("SUPABASE_SERVICE_KEY")
        if not supabase_url or not service_key:
            app.logger.error("Broadcast fallido: Credenciales de Supabase no configuradas.")
            return

        broadcast_url = f"{supabase_url}/realtime/v1/api/broadcast"
        headers = {"apikey": service_key, "Content-Type": "application/json"}
        payload = {
            "messages": [{"topic": "di_changes", "event": "di_update", "payload": {
                "eventType": event_type, "new": new_data, "old": old_data
            }}]
        }
        requests.post(broadcast_url, json=payload, headers=headers, timeout=3)
        app.logger.info(f"Broadcast enviado para evento: {event_type}")
    except Exception as e:
        app.logger.error(f"Error al enviar broadcast: {str(e)}")

# --- DECORADOR DE AUTENTICACIÓN (Sin cambios) ---
def token_required(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        token = None
        auth_header = request.headers.get('Authorization')
        if auth_header and auth_header.startswith('Bearer '):
            token = auth_header.split(' ')[1]
        if not token: return jsonify({'message': 'Token de autorización ausente o inválido.'}), 401
        try:
            SUPABASE_JWT_SECRET = os.getenv('SUPABASE_JWT_SECRET')
            data = jwt.decode(token, SUPABASE_JWT_SECRET, algorithms=['HS256'], audience='authenticated')
            g.user_id = data['sub']
            SUPABASE_URL = os.getenv("SUPABASE_URL")
            SUPABASE_KEY = os.getenv("SUPABASE_SERVICE_KEY")
            g.supabase = create_client(SUPABASE_URL, SUPABASE_KEY)
        except Exception as e:
            return jsonify({'message': f'Token inválido o error: {str(e)}'}), 401
        return f(*args, **kwargs)
    return decorated

# --- Funciones de Utilidad (Sin cambios) ---
def trigger_n8n_webhook(webhook_url_env_var, payload):
    n8n_webhook_url = os.getenv(webhook_url_env_var)
    if not n8n_webhook_url:
        app.logger.error(f'Variable de entorno {webhook_url_env_var} no configurada.')
        return
    try:
        requests.post(n8n_webhook_url, json=payload, timeout=3)
    except Exception as e:
        app.logger.error(f'No se pudo contactar N8N {webhook_url_env_var}: {str(e)}')

def check_di_ownership(di_id):
    try:
        result = g.supabase.table('disenos_instruccionales').select('id_usuario, nombre_archivo').eq('id_di', str(di_id)).single().execute()
        return result.data if result.data and result.data['id_usuario'] == g.user_id else None
    except Exception:
        return None

# --- RUTAS DE LA API (Con /validate añadido) ---

@app.route('/api/dis', methods=['GET'])
@token_required
def get_all_dis():
    result = g.supabase.table('disenos_instruccionales').select('*').eq('id_usuario', g.user_id).order('created_at', desc=True).execute()
    return make_response(jsonify(result.data))

@app.route('/api/dis', methods=['POST'])
@token_required
def upload_di():
    if 'file' not in request.files: return jsonify({'message': 'No se encontró el archivo.'}), 400
    file = request.files['file']
    file_path = f"{g.user_id}/{file.filename}"
    try:
        g.supabase.storage.from_('di-bucket').upload(file=file.read(), path=file_path)
        storage_url = f"{os.getenv('SUPABASE_URL')}/storage/v1/object/public/di-bucket/{file_path}"
        new_di_record = {'id_usuario': g.user_id, 'nombre_archivo': file.filename, 'url_storage': storage_url}
        insert_result = g.supabase.table('disenos_instruccionales').insert(new_di_record).execute()
        created_di = insert_result.data[0]
        broadcast_change("INSERT", new_data=created_di)
        return jsonify(created_di), 201
    except Exception as e:
        if 'Duplicate' in str(e): return jsonify({'message': f'Ya existe un archivo con el nombre "{file.filename}".'}), 409
        return jsonify({'message': 'Error inesperado al subir el archivo.'}), 500

@app.route('/api/dis/<uuid:di_id>', methods=['DELETE'])
@token_required
def delete_di(di_id):
    di_data = check_di_ownership(di_id)
    if not di_data: return jsonify({'message': 'Acción no autorizada.'}), 404
    try:
        file_path = f"{g.user_id}/{di_data['nombre_archivo']}"
        g.supabase.storage.from_('di-bucket').remove([file_path])
        g.supabase.table('disenos_instruccionales').delete().eq('id_di', str(di_id)).execute()
        broadcast_change("DELETE", old_data={'id_di': str(di_id)})
        return jsonify({'message': 'DI eliminado correctamente.'}), 200
    except Exception as e:
        return jsonify({'message': f'Error al eliminar el DI: {str(e)}'}), 500

@app.route('/api/dis/<uuid:di_id>/transform', methods=['POST'])
@token_required
def transform_di(di_id):
    if not check_di_ownership(di_id): return jsonify({'message': 'Acción no autorizada.'}), 403
    try:
        proceso = {"nombre": "transformacion", "estado": "processing"}
        update_result = g.supabase.table('disenos_instruccionales').update({'proceso_actual': proceso, 'contenido_jsonld': None}).eq('id_di', str(di_id)).execute()
        updated_di = update_result.data[0]
        broadcast_change("UPDATE", new_data=updated_di)
        trigger_n8n_webhook('N8N_WEBHOOK_URL_TRANSFORM_DI', {"di_id": str(di_id)})
        return jsonify({'message': 'El proceso de transformación ha comenzado.'}), 202
    except Exception as e:
        proceso_error = {"nombre": "transformacion", "estado": "error", "error_detalle": str(e)}
        error_update = g.supabase.table('disenos_instruccionales').update({'proceso_actual': proceso_error}).eq('id_di', str(di_id)).execute()
        if error_update.data:
            broadcast_change("UPDATE", new_data=error_update.data[0])
        return jsonify({'message': f'No se pudo iniciar la transformación: {str(e)}'}), 500

# --- ¡LA RUTA QUE FALTABA! ---
@app.route('/api/dis/<uuid:di_id>/validate', methods=['POST'])
@token_required
def trigger_di_validation(di_id):
    if not check_di_ownership(di_id): return jsonify({'message': 'Acción no autorizada.'}), 403
    try:
        proceso = {"nombre": "evaluacion", "estado": "processing"}
        update_result = g.supabase.table('disenos_instruccionales').update({'proceso_actual': proceso}).eq('id_di', str(di_id)).execute()
        updated_di = update_result.data[0]
        
        # Notificar al frontend que el proceso ha comenzado
        broadcast_change("UPDATE", new_data=updated_di)
        
        # Iniciar el workflow de n8n
        trigger_n8n_webhook('N8N_WEBHOOK_URL_VALIDATE_DI', {'di_id': str(di_id)})
        
        return jsonify({'message': 'El proceso de validación ha sido iniciado.'}), 202
    except Exception as e:
        proceso_error = {"nombre": "evaluacion", "estado": "error", "error_detalle": str(e)}
        error_update = g.supabase.table('disenos_instruccionales').update({'proceso_actual': proceso_error}).eq('id_di', str(di_id)).execute()
        if error_update.data:
            broadcast_change("UPDATE", new_data=error_update.data[0])
        return jsonify({'message': f'No se pudo iniciar la validación: {str(e)}'}), 500

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)