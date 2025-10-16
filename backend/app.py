# backend/app.py

import os
from datetime import datetime, timezone
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
            # Decodificamos el token para acceder a toda su información
            decoded_token = jwt.decode(token, SUPABASE_JWT_SECRET, algorithms=['HS256'], audience='authenticated')
            
            # Guardamos la info del usuario en el contexto global 'g'
            g.user_id = decoded_token['sub']
            g.user_role = decoded_token.get('user_metadata', {}).get('role', 'docente') # Rol por defecto 'docente'
            
            SUPABASE_URL = os.getenv("SUPABASE_URL")
            SUPABASE_KEY = os.getenv("SUPABASE_SERVICE_KEY")
            g.supabase = create_client(SUPABASE_URL, SUPABASE_KEY)
        except Exception as e:
            return jsonify({'message': f'Token inválido o error: {str(e)}'}), 401
        return f(*args, **kwargs)
    return decorated

# --- NUEVO Decorador para verificar roles ---
def require_role(role_name):
    def decorator(f):
        @wraps(f)
        def decorated_function(*args, **kwargs):
            if g.user_role != role_name:
                return jsonify({'message': 'Acceso denegado: Permisos insuficientes.'}), 403
            return f(*args, **kwargs)
        return decorated_function
    return decorator

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
    
    # --- CAMBIO: Esperar 'estructuraMEI' en lugar de 'paradigma' ---
    estructura_mei = request.form.get('estructuraMEI')
    if not estructura_mei: return jsonify({'message': 'La Estructura MEI es requerida.'}), 400

    file = request.files['file']
    if file.filename == '': return jsonify({'message': 'No se seleccionó ningún archivo.'}), 400
    
    file_path = f"{g.user_id}/{file.filename}"
    
    try:
        file_content = file.read()
        g.supabase.storage.from_('di-bucket').upload(file=file_content, path=file_path, file_options={"content-type": file.content_type})
        
        # --- CAMBIO: Guardar en la columna 'estructura_mei' ---
        new_di_record = {
            'id_usuario': g.user_id, 
            'nombre_archivo': file.filename,
            'estructura_mei': estructura_mei
        }
        insert_result = g.supabase.table('disenos_instruccionales').insert(new_di_record).execute()
        created_di = insert_result.data[0]

        proceso_inicial = {"nombre": "ingesta", "estado": "processing"}
        update_result = g.supabase.table('disenos_instruccionales').update({'proceso_actual': proceso_inicial}).eq('id_di', created_di['id_di']).execute()
        di_para_broadcast = update_result.data[0]

        broadcast_change("INSERT", new_data=di_para_broadcast)
        
        # --- CAMBIO: Enviar 'estructuraMEI' al webhook de n8n ---
        trigger_n8n_webhook('N8N_WEBHOOK_URL_INGESTA_DI', {"di_id": str(created_di['id_di']), "estructuraMEI": estructura_mei})

        return jsonify(created_di), 201
        
    except Exception as e:
        if 'Duplicate' in str(e): return jsonify({'message': f'Ya existe un archivo con el nombre "{file.filename}".'}), 409
        app.logger.error(f"Error en upload_di: {str(e)}")
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
    
@app.route('/api/dis/<uuid:di_id>/interact', methods=['POST'])
@token_required
def interact_with_di(di_id):
    if not check_di_ownership(di_id):
        return jsonify({'message': 'Acción no autorizada o DI no encontrado.'}), 404

    data = request.get_json()
    if not data or 'prompt' not in data:
        return jsonify({'message': 'El prompt es requerido.'}), 400

    try:
        proceso = {"nombre": "consulta", "estado": "processing"}
        update_result = g.supabase.table('disenos_instruccionales').update({
            'proceso_actual': proceso
        }).eq('id_di', str(di_id)).execute()
        updated_di = update_result.data[0]
        
        broadcast_change("UPDATE", new_data=updated_di)

        payload = { "di_id": str(di_id), "prompt": data['prompt'] }
        trigger_n8n_webhook('N8N_WEBHOOK_URL_CONSULTA_DI', payload)

        return jsonify({'message': 'La consulta ha sido enviada para procesamiento.'}), 202
    except Exception as e:
        proceso_error = {
            "nombre": "consulta", 
            "estado": "error", 
            "error_detalle": str(e),
            "timestamp": datetime.now(timezone.utc).isoformat()
        }
        error_update = g.supabase.table('disenos_instruccionales').update({'proceso_actual': proceso_error}).eq('id_di', str(di_id)).execute()
        if error_update.data:
            broadcast_change("UPDATE", new_data=error_update.data[0])
        return jsonify({'message': f'No se pudo iniciar la consulta: {str(e)}'}), 500

@app.route('/api/dis/<uuid:di_id>/download-url', methods=['GET'])
@token_required
def get_download_url(di_id):
    # Usamos la función check_di_ownership que ya tenemos
    di_info = check_di_ownership(di_id)
    if not di_info:
        return jsonify({'message': 'No autorizado o DI no encontrado'}), 404
    
    try:
        # Construimos la ruta del archivo como lo espera Supabase Storage
        file_path = f"{g.user_id}/{di_info['nombre_archivo']}"
        
        # Usamos el cliente de Supabase del contexto global 'g'
        # para crear una URL firmada y segura con 60 segundos de validez.
        signed_url_response = g.supabase.storage.from_('di-bucket').create_signed_url(file_path, 60)
        
        return jsonify(signed_url_response), 200
    except Exception as e:
        return jsonify({'error': f'Error al generar URL de descarga: {e}'}), 500
    
# --- NUEVAS RUTAS DE ADMINISTRADOR ---

@app.route('/api/sync/domain-glossary', methods=['POST'])
@token_required
@require_role('admin')
def sync_domain_glossary():
    # El cuerpo del request puede estar vacío o contener el archivo del glosario
    # Por ahora, solo disparamos el webhook
    trigger_n8n_webhook('N8N_WEBHOOK_URL_SYNC_DOMAIN', {})
    return jsonify({'message': 'Proceso de sincronización del glosario de dominio iniciado.'}), 202

@app.route('/api/sync/vocabulary-glossary', methods=['POST'])
@token_required
@require_role('admin')
def sync_vocabulary_glossary():
    trigger_n8n_webhook('N8N_WEBHOOK_URL_SYNC_VOCABULARY', {})
    return jsonify({'message': 'Proceso de sincronización del vocabulario técnico iniciado.'}), 202

@app.route('/api/dis/<uuid:di_id>/analyze-alignment', methods=['POST'])
@token_required
def trigger_alignment_analysis(di_id):
    # Primero, verificamos la propiedad del DI
    di_info = check_di_ownership(di_id)
    if not di_info: 
        return jsonify({'message': 'Acción no autorizada.'}), 403
    
    try:
        # Leemos el registro completo del DI para obtener la estructura MEI
        di_record = g.supabase.table('disenos_instruccionales').select('estructura_mei').eq('id_di', str(di_id)).single().execute().data
        if not di_record:
            return jsonify({'message': 'DI no encontrado.'}), 404
        
        estructura_mei = di_record['estructura_mei']
        
        # --- CAMBIO: Lógica basada en la nueva terminología ---
        if estructura_mei == 'MEI-Antiguo':
            terminos_vocabulario = "resultadoAprendizaje, aprendizajeEsperado, indicadorDeLogro"
            terminos_dominio = "Definición de Aprendizaje Esperado, Indicador de Logro, y todos los verbos de la taxonomía UNAB"
        elif estructura_mei == 'MEI-Actualizado':
            terminos_vocabulario = "resultadoFormativo, resultadoAprendizaje, indicadorDesempeno"
            terminos_dominio = "Definición de Resultado Formativo, Resultado de Aprendizaje, Indicador de Desempeño, y todos los verbos de la taxonomía UNAB"
        else:
            return jsonify({'message': f'Estructura MEI desconocida: {estructura_mei}'}), 400

        # --- CAMBIO: Enviar 'estructuraMEI' en el payload de n8n ---
        n8n_payload = {
            "di_id": str(di_id),
            "estructuraMEI": estructura_mei,
            "terminosVocabulario": terminos_vocabulario,
            "terminosDominio": terminos_dominio
        }
        
        proceso = {"nombre": "analisis_alineamiento", "estado": "processing"}
       
        update_result = g.supabase.table('disenos_instruccionales').update({'proceso_actual': proceso,'analisis_alineamiento': None}).eq('id_di', str(di_id)).execute()
        
        broadcast_change("UPDATE", new_data=update_result.data[0])
        
        trigger_n8n_webhook('N8N_WEBHOOK_URL_ANALYZE_ALIGNMENT', n8n_payload)
        
        return jsonify({'message': 'El análisis de alineamiento ha comenzado.'}), 202
    
    except Exception as e:
        app.logger.error(f"Error al iniciar análisis de alineamiento: {str(e)}")
        proceso_error = {"nombre": "analisis_alineamiento", "estado": "error", "error_detalle": "No se pudo iniciar el proceso."}
        error_update = g.supabase.table('disenos_instruccionales').update({'proceso_actual': proceso_error}).eq('id_di', str(di_id)).execute()
        if error_update.data:
            broadcast_change("UPDATE", new_data=error_update.data[0])
        return jsonify({'message': f'No se pudo iniciar el análisis: {str(e)}'}), 500

@app.route('/api/generate/indicators', methods=['POST'])
@token_required
def generate_indicators():
    """
    Endpoint para generar indicadores pedagógicos de forma síncrona.
    """
    data = request.get_json()
    if not data:
        return jsonify({"error": "No se proporcionaron datos"}), 400

    # 1. Validación básica del payload de entrada
    required_fields = ['estructuraMEI']
    if not all(field in data for field in required_fields):
        return jsonify({"error": "Faltan campos requeridos en el payload"}), 400

    # 2. Llamada síncrona al webhook de n8n
    n8n_webhook_url = os.environ.get('N8N_GENERATE_INDICATORS_URL')
    if not n8n_webhook_url:
        return jsonify({"error": "La URL del webhook no está configurada en el servidor"}), 500

    try:
        # Aumentamos el timeout para dar tiempo al workflow a ejecutarse
        response = requests.post(n8n_webhook_url, json=data, timeout=120) 
        response.raise_for_status()  # Lanza una excepción para códigos de error HTTP (4xx o 5xx)
        
        output_data = response.json()

        # 3. Guardar la entrada y la salida en la nueva tabla de Supabase
        try:
            g.supabase.table('generaciones_ia').insert({
                'user_id': g.user_id,
                'input_data': data,
                'output_data': output_data
            }).execute()
        except Exception as e:
            # Si falla la inserción en DB, no detenemos el flujo.
            # Es más importante devolver el resultado al usuario.
            # Se loggea el error para monitoreo.
            app.logger.warning(f"ADVERTENCIA: No se pudo guardar la generación en la DB: {e}")

        # 4. Devolver la respuesta de n8n al frontend
        return jsonify(output_data), 200

    except requests.exceptions.Timeout:
        return jsonify({"error": "La solicitud al motor de generación tardó demasiado en responder"}), 504
    except requests.exceptions.RequestException as e:
        # Captura errores de red, HTTP, etc.
        error_message = f"Error al comunicarse con el motor de generación: {e}"
        if e.response is not None:
            try:
                n8n_error = e.response.json()
                return jsonify(n8n_error), e.response.status_code
            except:
                 return jsonify({"error": error_message, "details": e.response.text}), 500
        return jsonify({"error": error_message}), 500

@app.route('/api/generations', methods=['GET'])
@token_required
def get_user_generations(): # Se elimina 'current_user'
    """
    Obtiene todas las generaciones de IA del usuario actual.
    """
    try:
        response = g.supabase.table('generaciones_ia').select('*').eq('user_id', g.user_id).order('created_at', desc=True).execute()
        return jsonify(response.data), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route('/api/generations/<uuid:generation_id>', methods=['DELETE'])
@token_required
def delete_user_generation(generation_id): # Se elimina 'current_user'
    """
    Elimina una generación de IA específica del usuario actual.
    """
    try:
        g.supabase.table('generaciones_ia').delete().match({'id': str(generation_id), 'user_id': g.user_id}).execute()
        return jsonify({"message": "Generación eliminada correctamente"}), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route('/api/generations/<uuid:generation_id>', methods=['PATCH'])
@token_required
def rename_user_generation(generation_id):
    """
    Renombra una generación de IA específica del usuario actual.
    """
    data = request.get_json()
    new_name = data.get('nombre_generacion')

    if not new_name or not new_name.strip():
        return jsonify({"error": "El nombre no puede estar vacío"}), 400

    try:
        response = g.supabase.table('generaciones_ia').update({
            'nombre_generacion': new_name.strip()
        }).match({
            'id': str(generation_id),
            'user_id': g.user_id
        }).execute()

        if not response.data:
            return jsonify({"error": "Generación no encontrada o no tienes permiso para modificarla"}), 404

        return jsonify(response.data[0]), 200
        
    except Exception as e:
        app.logger.error(f"!!! ERROR en rename_user_generation: {e}")
        return jsonify({"error": "Ocurrió un error interno en el servidor al intentar renombrar."}), 500

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)