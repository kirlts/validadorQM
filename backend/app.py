import os
from flask import Flask, jsonify
from dotenv import load_dotenv

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

# Esto es útil para el desarrollo local, aunque 'flask run' es el método preferido
if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)