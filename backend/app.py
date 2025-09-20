import os
from flask import Flask, jsonify, request
from dotenv import load_dotenv
import jwt # ◀️ 1. Importar la nueva librería

# Cargar las variables de entorno desde el archivo .env
load_dotenv()

# Crear la instancia de la aplicación Flask
app = Flask(__name__)

# Imprimir la URL de la base de datos para confirmar que se cargó (opcional, para depuración)
print(f"CONECTANDO A: {os.getenv('DATABASE_URL')}")


@app.route('/')
def index():
    """Ruta de bienvenida básica."""
    return jsonify({"message": "Bienvenido al Backend del Validador QM!"})


@app.route('/api/ping')
def ping_pong():
    """Ruta simple para verificar que el servidor está vivo."""
    return jsonify({"status": "ok", "message": "pong!"})


# --- NUEVO ENDPOINT PARA VAL-17 ---
@app.route('/api/validate-token', methods=['POST'])
def validate_token():
    """
    Endpoint para validar un token JWT emitido por Supabase.
    Espera una cabecera 'Authorization: Bearer <TOKEN>'.
    """
    # 2. Leer el secreto desde las variables de entorno
    SUPABASE_JWT_SECRET = os.getenv('SUPABASE_JWT_SECRET')
    if not SUPABASE_JWT_SECRET:
        return jsonify({"error": "JWT Secret no configurado en el servidor"}), 500

    # 3. Obtener el token de la cabecera
    auth_header = request.headers.get('Authorization')
    if not auth_header or not auth_header.startswith('Bearer '):
        return jsonify({"error": "Cabecera de autorización ausente o mal formada"}), 401
    
    token = auth_header.split(' ')[1]

    try:
        # 4. Decodificar y validar el token
        jwt.decode(token, SUPABASE_JWT_SECRET, algorithms=['HS256'])
        # Si la línea anterior no lanza una excepción, el token es válido
        return jsonify({"status": "token_valid"}), 200

    except jwt.ExpiredSignatureError:
        return jsonify({"error": "El token ha expirado"}), 401
    except jwt.InvalidTokenError:
        return jsonify({"error": "Token inválido"}), 401
    # --- FIN DEL NUEVO ENDPOINT ---


# Esto es útil para el desarrollo local, aunque 'flask run' es el método preferido
if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)