import os
from flask import Flask, jsonify, request
from dotenv import load_dotenv
import jwt
from flask_cors import CORS
import requests
from functools import wraps

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

@app.route('/api/validate-token', methods=['POST'])
@token_required
def validate_token(current_user_id):
    return jsonify({"status": "token_valid", "user_id": current_user_id}), 200

@app.route('/api/dis', methods=['GET'])
@token_required
def get_dis(current_user_id):
    print("--- INICIANDO /api/dis ---") # Log de inicio
    print(f"Usuario autenticado: {current_user_id}")

    try:
        n8n_webhook_url = os.getenv('N8N_WEBHOOK_URL_GET_DIS')
        if not n8n_webhook_url:
            print("ERROR: La variable de entorno N8N_WEBHOOK_URL_GET_DIS no está configurada.")
            return jsonify({'error': 'La URL del webhook no está configurada en el servidor'}), 500
        
        # Construimos la URL completa con el parámetro
        target_url = f"{n8n_webhook_url}?userId={current_user_id}"
        print(f"Llamando al webhook de N8N en: {target_url}")

        # Hacemos la petición a N8N
        response = requests.get(target_url, timeout=10) # Añadimos un timeout
        
        print(f"N8N respondió con código de estado: {response.status_code}")
        
        # Lanza un error si la respuesta no es 2xx
        response.raise_for_status() 
        
        print("La llamada a N8N fue exitosa. Devolviendo datos al frontend.")
        return jsonify(response.json()), 200

    except requests.exceptions.RequestException as e:
        # Este es el error más probable si hay un problema de red
        print(f"!!! ERROR de Petición a N8N: {e}")
        return jsonify({'error': f'Error al comunicarse con el servicio de orquestación: {e}'}), 500
    except Exception as e:
        print(f"!!! ERROR Inesperado: {e}")
        return jsonify({'error': f'Ocurrió un error inesperado: {e}'}), 500

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)