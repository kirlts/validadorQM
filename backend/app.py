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


# --- DECORADOR DE AUTENTICACIÓN Y CONTEXTO DE PETICIÓN ---
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
            if not SUPABASE_JWT_SECRET: raise ValueError("El secreto JWT de Supabase no está configurado en el backend.")
            data = jwt.decode(token, SUPABASE_JWT_SECRET, algorithms=['HS256'], audience='authenticated')
            g.user_id = data['sub']
            SUPABASE_URL = os.getenv("SUPABASE_URL")
            SUPABASE_KEY = os.getenv("SUPABASE_SERVICE_KEY")
            if not SUPABASE_URL or not SUPABASE_KEY: raise ValueError("Las credenciales de Supabase no están configuradas.")
            g.supabase = create_client(SUPABASE_URL, SUPABASE_KEY)
        except jwt.ExpiredSignatureError: return jsonify({'message': 'El token ha expirado.'}), 401
        except Exception as e: return jsonify({'message': f'Token inválido o error de configuración: {str(e)}'}), 401
        return f(*args, **kwargs)
    return decorated

# --- Funciones de Utilidad ---
def trigger_n8n_webhook(webhook_url_env_var, payload):
    n8n_webhook_url = os.getenv(webhook_url_env_var)
    if not n8n_webhook_url:
        app.logger.error(f'La variable de entorno {webhook_url_env_var} no está configurada.')
        return
    try:
        requests.post(n8n_webhook_url, json=payload, timeout=3)
    except requests.exceptions.RequestException as e:
        app.logger.error(f'No se pudo contactar el webhook N8N {webhook_url_env_var}: {str(e)}')

def check_di_ownership(di_id):
    try:
        result = g.supabase.table('disenos_instruccionales').select('id_usuario, nombre_archivo').eq('id_di', str(di_id)).single().execute()
        if result.data and result.data['id_usuario'] == g.user_id:
            return result.data
        return None
    except Exception:
        return None

# --- Rutas de la API ---
@app.route('/api/dis', methods=['GET'])
@token_required
def get_all_dis():
    try:
        result = g.supabase.table('disenos_instruccionales').select('*').eq('id_usuario', g.user_id).order('created_at', desc=True).execute()
        resp = make_response(jsonify(result.data))
        resp.headers['Cache-Control'] = 'no-cache, no-store, must-revalidate'
        return resp
    except Exception as e:
        return jsonify({'message': f'Ocurrió un error al obtener los DIs: {str(e)}'}), 500

@app.route('/api/dis/<uuid:di_id>', methods=['GET'])
@token_required
def get_single_di(di_id):
    if not check_di_ownership(di_id): return jsonify({'message': 'DI no encontrado o no autorizado.'}), 404
    result = g.supabase.table('disenos_instruccionales').select('*').eq('id_di', str(di_id)).single().execute()
    if result.data:
        resp = make_response(jsonify(result.data))
        resp.headers['Cache-Control'] = 'no-cache, no-store, must-revalidate'
        return resp
    return jsonify({'message': 'DI no encontrado.'}), 404

@app.route('/api/dis', methods=['POST'])
@token_required
def upload_di():
    if 'file' not in request.files: return jsonify({'message': 'No se encontró el archivo.'}), 400
    file = request.files['file']
    if file.filename == '': return jsonify({'message': 'No se seleccionó ningún archivo.'}), 400
    
    # --- LÓGICA DE ALMACENAMIENTO CORREGIDA ---
    file_path = f"{g.user_id}/{file.filename}"
    
    try:
        # 1. Intentamos subir el archivo. Si ya existe, Supabase Storage devolverá un error.
        file_content = file.read()
        g.supabase.storage.from_('di-bucket').upload(file=file_content, path=file_path)
        
        # 2. Si la subida fue exitosa (no hay duplicado), creamos el registro en la BD.
        storage_url = f"{os.getenv('SUPABASE_URL')}/storage/v1/object/public/di-bucket/{file_path}"
        new_di_record = { 'id_usuario': g.user_id, 'nombre_archivo': file.filename, 'url_storage': storage_url }
        insert_result = g.supabase.table('disenos_instruccionales').insert(new_di_record).execute()
        created_di = insert_result.data[0]
        
        return jsonify(created_di), 201
    except Exception as e:
        # Detectar si el error es por archivo duplicado (código de error específico de Supabase Storage)
        if 'Duplicate' in str(e) or ('error' in str(e) and 'Duplicate' in str(e)):
             return jsonify({'message': f'Ya existe un archivo con el nombre "{file.filename}".'}), 409 # 409 Conflict
        
        # Si es otro tipo de error, lo manejamos
        app.logger.error(f"Error en upload_di: {str(e)}")
        return jsonify({'message': f'Error inesperado al subir el archivo: {str(e)}'}), 500

@app.route('/api/dis/<uuid:di_id>', methods=['DELETE'])
@token_required
def delete_di(di_id):
    di_data = check_di_ownership(di_id)
    if not di_data: return jsonify({'message': 'Acción no autorizada o DI no encontrado.'}), 404
    try:
        # --- RUTA DE ARCHIVO CORREGIDA ---
        file_path = f"{g.user_id}/{di_data['nombre_archivo']}"
        g.supabase.storage.from_('di-bucket').remove([file_path])
        g.supabase.table('disenos_instruccionales').delete().eq('id_di', str(di_id)).execute()
        return jsonify({'message': 'DI eliminado correctamente.'}), 200
    except Exception as e:
        return jsonify({'message': f'Error al eliminar el DI: {str(e)}'}), 500

@app.route('/api/dis/<uuid:di_id>/transform', methods=['POST'])
@token_required
def transform_di(di_id):
    if not check_di_ownership(di_id): return jsonify({'message': 'Acción no autorizada.'}), 403
    try:
        g.supabase.table('disenos_instruccionales').update({'estado_transformacion': 'processing', 'error_transformacion': None, 'contenido_jsonld': None}).eq('id_di', str(di_id)).execute()
        trigger_n8n_webhook('N8N_WEBHOOK_URL_TRANSFORM_DI', {"di_id": str(di_id)})
        return jsonify({'message': 'El proceso de transformación ha comenzado.'}), 202
    except Exception as e:
        g.supabase.table('disenos_instruccionales').update({'estado_transformacion': 'error', 'error_transformacion': f'Fallo al iniciar el workflow: {str(e)}'}).eq('id_di', str(di_id)).execute()
        return jsonify({'message': f'No se pudo iniciar la transformación: {str(e)}'}), 500

@app.route('/api/dis/<uuid:di_id>/validate', methods=['POST'])
@token_required
def trigger_di_validation(di_id):
    if not check_di_ownership(di_id): return jsonify({'message': 'Acción no autorizada.'}), 403
    try:
        g.supabase.table('disenos_instruccionales').update({'estado_evaluacion': 'processing', 'error_evaluacion': None}).eq('id_di', str(di_id)).execute()
        trigger_n8n_webhook('N8N_WEBHOOK_URL_VALIDATE_DI', {'di_id': str(di_id)})
        return jsonify({'message': 'El proceso de validación ha sido iniciado.'}), 202
    except Exception as e:
        g.supabase.table('disenos_instruccionales').update({'estado_evaluacion': 'error', 'error_evaluacion': f'Fallo al iniciar el workflow: {str(e)}'}).eq('id_di', str(di_id)).execute()
        return jsonify({'message': f'No se pudo iniciar la validación: {str(e)}'}), 500
        
@app.route('/api/dis/<uuid:di_id>/download-url', methods=['GET'])
@token_required
def get_download_url(di_id):
    di = check_di_ownership(di_id)
    if not di: return jsonify({'message': 'No autorizado o DI no encontrado'}), 404
    # --- RUTA DE ARCHIVO CORREGIDA ---
    file_path = f"{g.user_id}/{di['nombre_archivo']}"
    signed_url = g.supabase.storage.from_('di-bucket').create_signed_url(file_path, 60)
    return jsonify(signed_url), 200

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)