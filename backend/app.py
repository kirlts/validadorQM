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
CORS(app, resources={r"/api/*": {"origins": "http://localhost:8080"}})

def token_required(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        token = None
        if 'Authorization' in request.headers and request.headers['Authorization'].startswith('Bearer '):
            token = request.headers['Authorization'].split(' ')[1]
        if not token:
            return jsonify({'error': 'Token ausente'}), 401
        try:
            SUPABASE_JWT_SECRET = os.getenv('SUPABASE_JWT_SECRET')
            data = jwt.decode(token, SUPABASE_JWT_SECRET, algorithms=['HS256'], audience='authenticated')
            current_user_id = data['sub']
        except Exception as e:
            return jsonify({'error': f'Token inválido: {e}'}), 401
        return f(current_user_id, *args, **kwargs)
    return decorated

@app.route('/api/dis/<uuid:di_id>/transform', methods=['POST'])
@token_required
def transform_di(current_user_id, di_id):
    try:
        n8n_webhook_url = os.getenv('N8N_WEBHOOK_URL_TRANSFORM_DI')
        if not n8n_webhook_url:
            return jsonify({'error': 'La URL del webhook de transformación no está configurada'}), 500

        payload = {"di_id": str(di_id), "user_id": current_user_id}
        response = requests.post(n8n_webhook_url, json=payload)
        response.raise_for_status()
        
        # CORRECCIÓN: Se valida explícitamente la estructura de la respuesta de N8N
        try:
            data = response.json()
            # Si N8N devuelve una lista, tomamos el primer objeto
            if isinstance(data, list) and len(data) > 0:
                data = data[0]

            if 'status' in data and 'message' in data:
                return jsonify(data), response.status_code
            else:
                # Si el JSON no tiene la estructura esperada, se devuelve un error
                return jsonify({
                    'status': 'error_inesperado', 
                    'message': 'La respuesta del workflow no tuvo el formato esperado (status, message).'
                }), 502 # 502 Bad Gateway
        except ValueError:
            return jsonify({
                'status': 'error_inesperado', 
                'message': 'La respuesta del workflow no fue un JSON válido.'
            }), 502
    
    except requests.exceptions.HTTPError as http_err:
        try:
            error_json = http_err.response.json()
        except ValueError:
            error_json = {'error': http_err.response.text or 'Error desconocido del servidor'}
        return jsonify(error_json), http_err.response.status_code
    except Exception as e:
        return jsonify({'error': f'No se pudo iniciar la transformación: {e}'}), 500

@app.route('/api/validate-token', methods=['POST'])
@token_required
def validate_token(current_user_id):
    return jsonify({"status": "token_valid", "user_id": current_user_id}), 200

@app.route('/api/dis', methods=['GET', 'POST'])
@token_required
def handle_dis(current_user_id):
    if request.method == 'GET':
        try:
            n8n_webhook_url = os.getenv('N8N_WEBHOOK_URL_GET_DIS')
            response = requests.get(f"{n8n_webhook_url}?userId={current_user_id}")
            response.raise_for_status()
            
            # SOLUCIÓN: Añadir cabeceras para deshabilitar la caché
            resp = make_response(jsonify(response.json()))
            resp.headers['Cache-Control'] = 'no-cache, no-store, must-revalidate'
            resp.headers['Pragma'] = 'no-cache'
            resp.headers['Expires'] = '0'
            return resp
            
        except Exception as e:
            return jsonify({'error': f'Ocurrió un error al obtener los DIs: {e}'}), 500
    if request.method == 'POST':
        if 'file' not in request.files: return jsonify({'error': 'No se encontró el archivo'}), 400
        file = request.files['file']
        if file.filename == '': return jsonify({'error': 'No se seleccionó ningún archivo'}), 400
        try:
            n8n_webhook_url = os.getenv('N8N_WEBHOOK_URL_UPLOAD_DI')
            files = {'file': (file.filename, file.stream, file.content_type)}
            response = requests.post(f"{n8n_webhook_url}?userId={current_user_id}", files=files)
            response.raise_for_status()
            return jsonify(response.json()), 200
        except requests.exceptions.HTTPError as http_err:
            try: error_json = http_err.response.json()
            except ValueError: error_json = {'error': http_err.response.text}
            return jsonify(error_json), http_err.response.status_code
        except Exception as e:
            return jsonify({'error': f'Ocurrió un error inesperado: {e}'}), 500

@app.route('/api/dis/<uuid:di_id>', methods=['DELETE'])
@token_required
def delete_di(current_user_id, di_id):
    try:
        n8n_base_url = os.getenv('N8N_WEBHOOK_URL_DELETE_DI')
        full_url = f"{n8n_base_url}/delete-di/{di_id}?userId={current_user_id}"
        response = requests.delete(full_url)
        response.raise_for_status()
        return jsonify(response.json()), 200
    except Exception as e:
        return jsonify({'error': f'Ocurrió un error al eliminar el DI: {e}'}), 500

@app.route('/api/dis/<uuid:di_id>/download-url', methods=['GET'])
@token_required
def get_download_url(current_user_id, di_id):
    try:
        url = os.getenv("SUPABASE_URL")
        key = os.getenv("SUPABASE_SERVICE_KEY")
        supabase = create_client(url, key)
        di_result = supabase.table('disenos_instruccionales').select('id_usuario, nombre_archivo').eq('id_di', str(di_id)).single().execute()
        if not di_result.data: return jsonify({'error': 'DI no encontrado'}), 404
        if di_result.data['id_usuario'] != current_user_id: return jsonify({'error': 'No autorizado'}), 403
        file_path = f"{current_user_id}/{di_result.data['nombre_archivo']}"
        signed_url_response = supabase.storage.from_('di-bucket').create_signed_url(file_path, 60)
        return jsonify(signed_url_response), 200
    except Exception as e:
        return jsonify({'error': f'Error al generar URL de descarga: {e}'}), 500

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)