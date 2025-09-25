# backend/app.py

import os
from flask import Flask, jsonify, request, make_response
from dotenv import load_dotenv
import jwt
from flask_cors import CORS
import requests
from functools import wraps
from supabase import create_client, Client
from uuid import UUID

load_dotenv()
app = Flask(__name__)
CORS(app, 
    resources={r"/api/*": {"origins": "http://localhost:8080"}},
    supports_credentials=True
)


# --- Configuración de Supabase ---
SUPABASE_URL = os.getenv("SUPABASE_URL")
SUPABASE_KEY = os.getenv("SUPABASE_SERVICE_KEY")
supabase: Client = create_client(SUPABASE_URL, SUPABASE_KEY)

# --- Decorador de Autenticación ---
def token_required(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        token = None
        auth_header = request.headers.get('Authorization')
        if auth_header and auth_header.startswith('Bearer '):
            token = auth_header.split(' ')[1]
        
        if not token:
            return jsonify({'message': 'Token de autorización ausente o inválido.'}), 401
            
        try:
            SUPABASE_JWT_SECRET = os.getenv('SUPABASE_JWT_SECRET')
            if not SUPABASE_JWT_SECRET:
                raise ValueError("El secreto JWT de Supabase no está configurado en el backend.")
            
            data = jwt.decode(token, SUPABASE_JWT_SECRET, algorithms=['HS256'], audience='authenticated')
            current_user_id = data['sub']
        except jwt.ExpiredSignatureError:
            return jsonify({'message': 'El token ha expirado.'}), 401
        except Exception as e:
            return jsonify({'message': f'Token inválido: {str(e)}'}), 401
            
        return f(current_user_id, *args, **kwargs)
    return decorated

# --- Funciones de Utilidad ---
def trigger_n8n_webhook(webhook_url_env_var, payload):
    n8n_webhook_url = os.getenv(webhook_url_env_var)
    if not n8n_webhook_url:
        raise Exception(f'La variable de entorno {webhook_url_env_var} no está configurada.')
    try:
        requests.post(n8n_webhook_url, json=payload, timeout=5)
    except requests.exceptions.ReadTimeout:
        pass
    except requests.exceptions.RequestException as e:
        raise Exception(f'Error de conexión con N8N: {str(e)}')

def check_di_ownership(user_id, di_id):
    try:
        result = supabase.table('disenos_instruccionales').select('id_usuario, nombre_archivo').eq('id_di', str(di_id)).single().execute()
        if result.data and result.data['id_usuario'] == user_id:
            return result.data
        return None
    except Exception:
        return None

# --- Rutas de la API ---

@app.route('/api/dis', methods=['GET'])
@token_required
def get_all_dis(current_user_id):
    try:
        result = supabase.table('disenos_instruccionales').select('*').eq('id_usuario', current_user_id).order('created_at', desc=True).execute()
        resp = make_response(jsonify(result.data))
        resp.headers['Cache-Control'] = 'no-cache, no-store, must-revalidate'
        return resp
    except Exception as e:
        return jsonify({'message': f'Ocurrió un error al obtener los DIs: {str(e)}'}), 500

@app.route('/api/dis', methods=['POST'])
@token_required
def upload_di(current_user_id):
    if 'file' not in request.files: return jsonify({'message': 'No se encontró el archivo.'}), 400
    file = request.files['file']
    if file.filename == '': return jsonify({'message': 'No se seleccionó ningún archivo.'}), 400
    try:
        n8n_webhook_url = os.getenv('N8N_WEBHOOK_URL_UPLOAD_DI')
        if not n8n_webhook_url: return jsonify({'message': 'El endpoint de subida no está configurado.'}), 500
        files = {'file': (file.filename, file.stream, file.content_type)}
        response = requests.post(f"{n8n_webhook_url}?userId={current_user_id}", files=files)
        response.raise_for_status()
        return jsonify(response.json()), response.status_code
    except requests.exceptions.HTTPError as http_err:
        try: error_json = http_err.response.json()
        except ValueError: error_json = {'message': http_err.response.text or 'Error desconocido en el workflow.'}
        return jsonify(error_json), http_err.response.status_code
    except Exception as e:
        return jsonify({'message': f'Error inesperado: {str(e)}'}), 500

@app.route('/api/dis/<uuid:di_id>', methods=['DELETE'])
@token_required
def delete_di(current_user_id, di_id):
    di_data = check_di_ownership(current_user_id, di_id)
    if not di_data:
        return jsonify({'message': 'Acción no autorizada o DI no encontrado.'}), 404
    try:
        file_path = f"{current_user_id}/{di_data['nombre_archivo']}"
        supabase.storage.from_('di-bucket').remove([file_path])
        supabase.table('disenos_instruccionales').delete().eq('id_di', str(di_id)).execute()
        return jsonify({'message': 'DI eliminado correctamente.'}), 200
    except Exception as e:
        return jsonify({'message': f'Error al eliminar el DI: {str(e)}'}), 500

@app.route('/api/dis/<uuid:di_id>/transform', methods=['POST'])
@token_required
def transform_di(current_user_id, di_id):
    if not check_di_ownership(current_user_id, di_id): return jsonify({'message': 'Acción no autorizada.'}), 403
    try:
        supabase.table('disenos_instruccionales').update({'estado_transformacion': 'processing', 'error_transformacion': None, 'contenido_jsonld': None}).eq('id_di', str(di_id)).execute()
        trigger_n8n_webhook('N8N_WEBHOOK_URL_TRANSFORM_DI', {"di_id": str(di_id)})
        return jsonify({'message': 'El proceso de transformación ha comenzado.'}), 202
    except Exception as e:
        supabase.table('disenos_instruccionales').update({'estado_transformacion': 'error', 'error_transformacion': f'Fallo al iniciar el workflow: {str(e)}'}).eq('id_di', str(di_id)).execute()
        return jsonify({'message': f'No se pudo iniciar la transformación: {str(e)}'}), 500

@app.route('/api/dis/<uuid:di_id>/validate', methods=['POST'])
@token_required
def trigger_di_validation(current_user_id, di_id):
    if not check_di_ownership(current_user_id, di_id): return jsonify({'message': 'Acción no autorizada.'}), 403
    try:
        supabase.table('disenos_instruccionales').update({'estado_evaluacion': 'processing', 'error_evaluacion': None}).eq('id_di', str(di_id)).execute()
        trigger_n8n_webhook('N8N_WEBHOOK_URL_VALIDATE_DI', {'di_id': str(di_id)})
        return jsonify({'message': 'El proceso de validación ha sido iniciado.'}), 202
    except Exception as e:
        supabase.table('disenos_instruccionales').update({'estado_evaluacion': 'error', 'error_evaluacion': f'Fallo al iniciar el workflow: {str(e)}'}).eq('id_di', str(di_id)).execute()
        return jsonify({'message': f'No se pudo iniciar la validación: {str(e)}'}), 500

@app.route('/api/dis/<uuid:di_id>/validation', methods=['GET'])
@token_required
def get_di_validation(current_user_id, di_id):
    if not check_di_ownership(current_user_id, di_id): return jsonify({'message': 'Acción no autorizada.'}), 403
    try:
        result = supabase.table('disenos_instruccionales').select('nombre_archivo, evaluacion_di, estado_evaluacion, error_evaluacion').eq('id_di', str(di_id)).single().execute()
        if not result.data: return jsonify({'message': 'DI no encontrado.'}), 404
        resp = make_response(jsonify(result.data))
        resp.headers['Cache-Control'] = 'no-cache, no-store, must-revalidate'
        return resp
    except Exception as e:
        return jsonify({'message': f'Error al obtener la validación: {str(e)}'}), 500

@app.route('/api/dis/<uuid:di_id>/download-url', methods=['GET'])
@token_required
def get_download_url(current_user_id, di_id):
    try:
        di = check_di_ownership(current_user_id, di_id)
        if not di: return jsonify({'message': 'No autorizado o DI no encontrado'}), 404
        file_path = f"{current_user_id}/{di['nombre_archivo']}"
        signed_url = supabase.storage.from_('di-bucket').create_signed_url(file_path, 60)
        return jsonify(signed_url), 200
    except Exception as e:
        return jsonify({'message': f'Error al generar URL: {str(e)}'}), 500

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)