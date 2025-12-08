"""
Streamlit App para perfeccionar funcionalidades de n8n
Este frontend permite a Andrea (validadora de calidad) modificar prompts 
y parámetros de los workflows de n8n para mejorar la precisión del sistema.
"""

import streamlit as st
import requests
import os
import json
import sys
import logging
from datetime import datetime

# Configurar logging para que aparezca en docker logs
logging.basicConfig(
    level=logging.DEBUG,
    format='[%(asctime)s] [%(levelname)s] %(message)s',
    datefmt='%Y-%m-%d %H:%M:%S',
    stream=sys.stderr
)
logger = logging.getLogger(__name__)

# Configuración de la URL de n8n
# En Docker, usamos el nombre del servicio como hostname
N8N_BASE_URL = os.getenv('N8N_INTERNAL_URL', 'http://n8n:5678')
N8N_API_KEY = os.getenv('N8N_API_KEY', '')

st.set_page_config(
    page_title="Validador QM - Panel de Desarrollo",
    page_icon="🔧",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Inicializar sesión state
if 'webhook_responses' not in st.session_state:
    st.session_state.webhook_responses = []
if 'widget_version' not in st.session_state:
    st.session_state.widget_version = 0

# Inicializar casos guardados
if 'casos_guardados' not in st.session_state:
    st.session_state.casos_guardados = {}
    # Caso de ejemplo por defecto
    st.session_state.casos_guardados["Caso 1 - Ejemplo MEI Actualizado (Generar)"] = {
        "workflow": "generar-indicadores-v2",
        "estructuraMEI": "MEI-Actualizado",
        "nombre_curso": "Diseño Pedagógico",
        "trimestre": "",
        "metodologia": "",
        "cantidad_indicadores": 3,
        "rf_list": ["Diseñar estrategias pedagógicas y unidades didácticas que integren conocimientos pedagógicos, teorías del aprendizaje, enfoques inclusivos y principios de diversidad educativa, aplicando el análisis de procesos de aprendizaje, necesidades, intereses y características de los estudiantes de educación básica, con el fin de promover su aprendizaje significativo, desarrollo integral, socioemocional, autonomía, pensamiento crítico y habilidades para la convivencia, fortaleciendo la formación ética, reflexiva y profesional del futuro docente en diversos contextos educativos."],
        "ra_list": ["Diseñar unidades didácticas que integren estrategias pedagógicas inclusivas y pertinentes, aplicando el análisis de los procesos de aprendizaje de estudiantes de educación básica, con el fin de promover su desarrollo integral y socioemocional."],
        "ae_list": [],
        "indicadores_list": [],
        "agente_1": "",
        "agente_2": ""
    }
    st.session_state.casos_guardados["Caso 2 - Ejemplo MEI Antiguo (Generar)"] = {
        "workflow": "generar-indicadores-v2",
        "estructuraMEI": "MEI-Antiguo",
        "nombre_curso": "Diseño Pedagógico",
        "trimestre": "",
        "metodologia": "",
        "cantidad_indicadores": 3,
        "rf_list": [],
        "ra_list": ["Integrar conocimientos pedagógicos, estrategias inclusivas y teorías del aprendizaje para planificar y orientar experiencias educativas que promuevan el aprendizaje significativo y el desarrollo integral de los estudiantes en Educación Básica."],
        "ae_list": ["Diseñar unidades didácticas fundamentadas en estrategias pedagógicas inclusivas y teorías del aprendizaje, con el propósito de potenciar el aprendizaje significativo y el desarrollo integral de los estudiantes."],
        "indicadores_list": [],
        "agente_1": "",
        "agente_2": ""
    }
    st.session_state.casos_guardados["Caso 3 - Ejemplo MEI Actualizado (Revisar)"] = {
        "workflow": "revisar-indicadores-v2",
        "estructuraMEI": "MEI-Actualizado",
        "nombre_curso": "Diseño Pedagógico",
        "trimestre": "",
        "metodologia": "",
        "cantidad_indicadores": 3,
        "rf_list": ["Diseñar estrategias pedagógicas y unidades didácticas que integren conocimientos pedagógicos, teorías del aprendizaje, enfoques inclusivos y principios de diversidad educativa, aplicando el análisis de procesos de aprendizaje, necesidades, intereses y características de los estudiantes de educación básica, con el fin de promover su aprendizaje significativo, desarrollo integral, socioemocional, autonomía, pensamiento crítico y habilidades para la convivencia, fortaleciendo la formación ética, reflexiva y profesional del futuro docente en diversos contextos educativos."],
        "ra_list": ["Diseñar unidades didácticas que integren estrategias pedagógicas inclusivas y pertinentes, aplicando el análisis de los procesos de aprendizaje de estudiantes de educación básica, con el fin de promover su desarrollo integral y socioemocional."],
        "ae_list": [],
        "indicadores_list": [
            "Comparar el desempeño, habilidades y necesidades de aprendizaje de los estudiantes de educación básica utilizando registros de aula y resultados de evaluaciones.",
            "Elaborar unidades didácticas que incluyan estrategias pedagógicas inclusivas y pertinentes, ajustadas a la diversidad del grupo de estudiantes.",
            "Argumentar la selección de estrategias y recursos en las unidades didácticas, demostrando cómo estas favorecen el desarrollo integral y socioemocional de los estudiantes."
        ],
        "agente_1": "",
        "agente_2": ""
    }
    st.session_state.casos_guardados["Caso 4 - Ejemplo MEI Antiguo (Revisar)"] = {
        "workflow": "revisar-indicadores-v2",
        "estructuraMEI": "MEI-Antiguo",
        "nombre_curso": "Diseño Pedagógico",
        "trimestre": "",
        "metodologia": "",
        "cantidad_indicadores": 3,
        "rf_list": [],
        "ra_list": ["Integrar conocimientos pedagógicos, estrategias inclusivas y teorías del aprendizaje para planificar y orientar experiencias educativas que promuevan el aprendizaje significativo y el desarrollo integral de los estudiantes en Educación Básica."],
        "ae_list": ["Diseñar unidades didácticas fundamentadas en estrategias pedagógicas inclusivas y teorías del aprendizaje, con el propósito de potenciar el aprendizaje significativo y el desarrollo integral de los estudiantes."],
        "indicadores_list": [
            "Comparan enfoques teóricos del aprendizaje y necesidades educativas de los estudiantes, identificando similitudes y diferencias a partir de registros de aula y resultados de evaluaciones.",
            "Elaboran propuestas de unidades didácticas que integren estrategias pedagógicas inclusivas y principios de diversidad educativa, considerando la realidad y características del grupo de estudiantes.",
            "Argumentan las decisiones pedagógicas tomadas en las unidades didácticas, apoyándose en fundamentos teóricos sobre aprendizaje y desarrollo integral, y demostrando cómo estas favorecen el crecimiento socioemocional de los estudiantes."
        ],
        "agente_1": "",
        "agente_2": ""
    }

# Sidebar - Configuración
st.sidebar.title("⚙️ Configuración")
st.sidebar.info(f"**N8N URL:** `{N8N_BASE_URL}`")

# Verificar conexión
connection_status = st.sidebar.empty()
if st.sidebar.button("🔍 Verificar Conexión"):
    try:
        response = requests.get(f"{N8N_BASE_URL}", timeout=5)
        if response.status_code in [200, 404, 401]:
            connection_status.success("✅ Conexión exitosa con n8n")
        else:
            connection_status.warning(f"⚠️ n8n respondió con código: {response.status_code}")
    except Exception as e:
        connection_status.error(f"❌ Error: {str(e)}")

st.sidebar.markdown("---")
st.sidebar.markdown("### 📚 Webhooks Disponibles")
st.sidebar.markdown("""
- `generar-indicadores-v2`
- `revisar-indicadores-v2`
""")

# Sección Avanzado (colapsada por defecto)
st.sidebar.markdown("---")
with st.sidebar.expander("⚙️ Opciones Avanzadas", expanded=False):
    # Timeout
    if 'timeout' not in st.session_state:
        st.session_state.timeout = 120
    timeout = st.number_input(
        "⏱️ Timeout (segundos):",
        min_value=10,
        max_value=300,
        value=st.session_state.timeout,
        step=10,
        help="Tiempo máximo de espera para la respuesta del workflow"
    )
    st.session_state.timeout = timeout
    
    # Vista previa del payload (se mostrará después de construir el payload)
    st.markdown("---")
    st.markdown("**📋 Vista Previa del Payload**")
    if st.session_state.get('payload_sidebar', None):
        st.json(st.session_state.payload_sidebar)
    else:
        st.caption("Configura el Diseño Instruccional para ver la vista previa")

# Título principal (compacto)
st.title("🔧 Panel de Desarrollo - Validador QM")
st.caption("Itera sobre prompts para generar indicadores pedagógicos alineados con Bloom y Quality Matters")

# Información y Ayuda al principio (robustecida)
with st.expander("ℹ️ Información y Ayuda - Guía Completa", expanded=False):
    st.markdown("""
    ## 🎯 ¿Qué hace este panel?
    
    Este panel te permite **iterar sobre prompts** (instrucciones para los agentes de IA) para generar o revisar indicadores pedagógicos que cumplan con los estándares de **Taxonomía de Bloom** y **Quality Matters**.
    
    ### 📋 Flujo de trabajo paso a paso:
    
    1. **Selecciona el tipo de trabajo:**
       - **Generar Indicadores:** Crea nuevos indicadores desde Resultados de Aprendizaje (RA) o Aprendizajes Esperados (AE)
       - **Revisar Indicadores:** Evalúa y mejora indicadores existentes
    
    2. **Configura el Diseño Instruccional:**
       - Selecciona la **Estructura MEI** (Antiguo o Actualizado)
       - Ingresa los **Resultados Formativos (RF)**, **Resultados de Aprendizaje (RA)** o **Aprendizajes Esperados (AE)**
       - Completa el nombre del curso y otros datos opcionales
    
    3. **Personaliza las prompts (opcional):**
       - Puedes modificar las instrucciones que reciben los agentes de IA
       - Usa la **vista previa** para ver exactamente qué recibirá cada agente
       - Las prompts se guardan automáticamente para cada combinación (tipo de trabajo, MEI, cantidad de agentes)
    
    4. **Ejecuta y revisa resultados:**
       - Haz clic en "Generar Indicadores" o "Revisar Indicadores"
       - Revisa los resultados generados
       - Consulta las **prompts exactas utilizadas** en la sección "Prompts Utilizadas"
    
    5. **Itera y mejora:**
       - Ajusta las prompts según los resultados obtenidos
       - Guarda casos exitosos para reutilizarlos después
    
    ### 💡 Conceptos importantes:
    
    - **MEI-Antiguo:** Estructura con RA → AE → IL (Indicadores de Logro)
    - **MEI-Actualizado:** Estructura con RF → RA → ID (Indicadores de Desempeño)
    - **Agentes de IA:** Puedes usar 1 o 2 agentes. Con 1 agente, hace todo el trabajo. Con 2 agentes, el primero descompone y el segundo evalúa/genera.
    - **Vista Previa:** Muestra exactamente qué recibirá cada agente, incluyendo tus datos y tus instrucciones personalizadas.
    - **Casos Guardados:** Permite guardar y cargar configuraciones completas para reutilizarlas.
    
    ### 🔍 ¿Necesitas ayuda con algún elemento?
    
    Busca los íconos **ℹ️** junto a cada sección o campo. Pasa el mouse sobre ellos para ver explicaciones detalladas.
    """)

# Secciones 1 y 2 combinadas: Workflow y Gestión de Casos lado a lado
st.markdown("---")

# ============================================================================
# SISTEMA SIMPLIFICADO DE CARGA DE CASOS
# ============================================================================
# Cuando se detecta caso_a_cargar, actualizamos TODOS los valores y hacemos rerun
# Después del rerun, todos los widgets usan los valores actualizados de session_state
# ============================================================================

if 'caso_a_cargar' in st.session_state and st.session_state.caso_a_cargar:
    caso_nombre = st.session_state.caso_a_cargar
    
    # DEBUG: Log inicio de carga
    logger.info(f"[DEBUG] Iniciando carga de caso: {caso_nombre}")
    
    if caso_nombre not in st.session_state.casos_guardados:
        logger.error(f"[ERROR] Caso '{caso_nombre}' no encontrado en casos_guardados")
        del st.session_state.caso_a_cargar
        st.error(f"❌ Caso '{caso_nombre}' no encontrado")
        st.rerun()
    
    caso = st.session_state.casos_guardados[caso_nombre]
    
    # DEBUG: Log valores del caso
    logger.info(f"[DEBUG] Caso tiene workflow: {caso.get('workflow', 'NO DEFINIDO')}")
    logger.info(f"[DEBUG] Caso tiene estructuraMEI: {caso.get('estructuraMEI', 'NO DEFINIDO')}")
    logger.info(f"[DEBUG] Caso tiene nombre_curso: {caso.get('nombre_curso', 'NO DEFINIDO')}")
    logger.info(f"[DEBUG] Caso tiene rf_list length: {len(caso.get('rf_list', []))}")
    logger.info(f"[DEBUG] Caso tiene ra_list length: {len(caso.get('ra_list', []))}")
    
    # ACTUALIZAR TODOS LOS VALORES EN SESSION_STATE
    logger.info(f"[CARGA_CASO] Actualizando valores en session_state...")
    
    # 1. Workflow
    if 'workflow' in caso:
        workflow_internal = caso['workflow']
        workflow_anterior = st.session_state.get('workflow_type', 'NO DEFINIDO')
        logger.info(f"[CARGA_CASO]   [1/5] Workflow: {workflow_anterior} -> {workflow_internal}")
        st.session_state.workflow_type = workflow_internal
        st.session_state.last_workflow = workflow_internal
    else:
        logger.warning(f"[CARGA_CASO]   [1/5] Workflow: NO ENCONTRADO en caso")
    
    # 2. Estructura MEI - CRÍTICO: Establecer ANTES de cualquier otra operación
    if 'estructuraMEI' in caso:
        estructura_mei_valor = caso['estructuraMEI']
        estructura_anterior = st.session_state.get('estructura_mei_selector', 'NO DEFINIDO')
        logger.info(f"[CARGA_CASO]   [2/5] Estructura MEI: {estructura_anterior} -> {estructura_mei_valor}")
        # Establecer directamente en session_state - NO usar variables intermedias
        st.session_state.estructura_mei_selector = estructura_mei_valor
        st.session_state.last_estructura = estructura_mei_valor
        logger.info(f"[CARGA_CASO]   [2/5] estructura_mei_selector establecido en session_state: {st.session_state.estructura_mei_selector}")
    else:
        logger.warning(f"[CARGA_CASO]   [2/5] Estructura MEI: NO ENCONTRADO en caso")
    
    # 3. Campos simples
    nombre_curso_anterior = st.session_state.get('nombre_curso', '')
    st.session_state.nombre_curso = caso.get('nombre_curso', '')
    st.session_state.trimestre = caso.get('trimestre', '')
    st.session_state.metodologia = caso.get('metodologia', '')
    st.session_state.cantidad_indicadores = caso.get('cantidad_indicadores', 3)
    st.session_state.cantidad_agentes = caso.get('cantidad_agentes', 2)
    logger.info(f"[CARGA_CASO]   [3/5] Campos simples:")
    logger.info(f"[CARGA_CASO]     - nombre_curso: '{nombre_curso_anterior}' -> '{st.session_state.nombre_curso}'")
    logger.info(f"[CARGA_CASO]     - cantidad_agentes: {st.session_state.cantidad_agentes}")
    logger.info(f"[CARGA_CASO]     - cantidad_indicadores: {st.session_state.cantidad_indicadores}")
    
    # 4. Listas - copiar directamente, usar [""] si están vacías
    rf_list_caso = caso.get('rf_list', [])
    ra_list_caso = caso.get('ra_list', [])
    ae_list_caso = caso.get('ae_list', [])
    indicadores_list_caso = caso.get('indicadores_list', [])
    
    rf_list_anterior_len = len(st.session_state.get('rf_list', []))
    ra_list_anterior_len = len(st.session_state.get('ra_list', []))
    
    st.session_state.rf_list = rf_list_caso.copy() if rf_list_caso else [""]
    st.session_state.ra_list = ra_list_caso.copy() if ra_list_caso else [""]
    st.session_state.ae_list = ae_list_caso.copy() if ae_list_caso else [""]
    st.session_state.indicadores_list = indicadores_list_caso.copy() if indicadores_list_caso else [""]
    
    logger.info(f"[CARGA_CASO]   [4/5] Listas actualizadas:")
    logger.info(f"[CARGA_CASO]     - rf_list: {rf_list_anterior_len} -> {len(st.session_state.rf_list)} elementos")
    logger.info(f"[CARGA_CASO]     - ra_list: {ra_list_anterior_len} -> {len(st.session_state.ra_list)} elementos")
    logger.info(f"[CARGA_CASO]     - ae_list: {len(st.session_state.ae_list)} elementos")
    logger.info(f"[CARGA_CASO]     - indicadores_list: {len(st.session_state.indicadores_list)} elementos")
    if st.session_state.rf_list and st.session_state.rf_list[0]:
        logger.info(f"[CARGA_CASO]     - rf_list[0] preview: {st.session_state.rf_list[0][:50]}...")
    if st.session_state.ra_list and st.session_state.ra_list[0]:
        logger.info(f"[CARGA_CASO]     - ra_list[0] preview: {st.session_state.ra_list[0][:50]}...")
    
    # 5. Prompts de agentes - usar clave única por combinación
    workflow_key = caso.get('workflow', 'generar-indicadores-v2')
    mei_key = caso.get('estructuraMEI', 'MEI-Actualizado')
    prompt_key = f"prompt_{workflow_key}_{mei_key}"
    
    # Cargar prompts del caso o usar las guardadas para esta combinación
    if 'agente_1' in caso and caso['agente_1']:
        st.session_state.agente_1 = caso['agente_1']
    elif f"{prompt_key}_agente_1" in st.session_state:
        st.session_state.agente_1 = st.session_state[f"{prompt_key}_agente_1"]
    else:
        st.session_state.agente_1 = ""
    
    if 'agente_2' in caso and caso['agente_2']:
        st.session_state.agente_2 = caso['agente_2']
    elif f"{prompt_key}_agente_2" in st.session_state:
        st.session_state.agente_2 = st.session_state[f"{prompt_key}_agente_2"]
    else:
        st.session_state.agente_2 = ""
    
    if 'agente_3' in caso:
        st.session_state.agente_3 = caso.get('agente_3', '')
    
    # 6. Limpiar estados de widgets para forzar actualización
    # IMPORTANTE: NO eliminar 'estructura_mei_selector' porque acabamos de establecerlo
    widgets_a_limpiar = ['workflow_radio', 'toggle_1_agente', 'toggle_2_agentes']
    for widget_key in widgets_a_limpiar:
        if widget_key in st.session_state:
            logger.info(f"[CARGA_CASO] Limpiando widget key: {widget_key}")
            del st.session_state[widget_key]
    
    # 7. Incrementar widget_version para forzar actualización de todos los widgets
    widget_version_anterior = st.session_state.widget_version
    st.session_state.widget_version += 1
    logger.info(f"[CARGA_CASO]   [5/5] widget_version: {widget_version_anterior} -> {st.session_state.widget_version}")
    
    # 8. VERIFICACIÓN CRÍTICA: Asegurar que estructura_mei_selector está establecido
    # Esta verificación debe hacerse DESPUÉS de limpiar widgets, pero estructura_mei_selector NO debe limpiarse
    if 'estructuraMEI' in caso:
        estructura_esperada = caso['estructuraMEI']
        # Leer directamente de session_state
        if 'estructura_mei_selector' in st.session_state:
            estructura_actual = st.session_state.estructura_mei_selector
        else:
            estructura_actual = 'NO EXISTE'
            logger.error(f"[CARGA_CASO] ERROR: estructura_mei_selector NO está en session_state después de establecerlo!")
            st.session_state.estructura_mei_selector = estructura_esperada
            logger.info(f"[CARGA_CASO] estructura_mei_selector re-establecido a: {st.session_state.estructura_mei_selector}")
        
        if estructura_actual != estructura_esperada:
            logger.error(f"[CARGA_CASO] ERROR: estructura_mei_selector no coincide! Esperado: {estructura_esperada}, Actual: {estructura_actual}")
            st.session_state.estructura_mei_selector = estructura_esperada
            logger.info(f"[CARGA_CASO] estructura_mei_selector corregido a: {st.session_state.estructura_mei_selector}")
        else:
            logger.info(f"[CARGA_CASO] estructura_mei_selector verificado correctamente: {estructura_actual}")
    
    # 9. Limpiar flag y hacer rerun
    caso_nombre_final = st.session_state.caso_a_cargar
    del st.session_state.caso_a_cargar
    logger.info(f"[CARGA_CASO] Valores finales en session_state ANTES de rerun:")
    logger.info(f"[CARGA_CASO]   - workflow_type: {st.session_state.get('workflow_type', 'NO DEFINIDO')}")
    logger.info(f"[CARGA_CASO]   - estructura_mei_selector: {st.session_state.get('estructura_mei_selector', 'NO DEFINIDO')}")
    logger.info(f"[CARGA_CASO]   - nombre_curso: '{st.session_state.get('nombre_curso', 'NO DEFINIDO')}'")
    logger.info(f"[CARGA_CASO]   - widget_version: {st.session_state.widget_version}")
    logger.info(f"[CARGA_CASO]   - rf_list length: {len(st.session_state.get('rf_list', []))}")
    logger.info(f"[CARGA_CASO]   - ra_list length: {len(st.session_state.get('ra_list', []))}")
    logger.info(f"[CARGA_CASO]   - last_estructura: {st.session_state.get('last_estructura', 'NO DEFINIDO')}")
    
    # VERIFICACIÓN CRÍTICA FINAL: Asegurar que estructura_mei_selector está establecido
    if 'estructuraMEI' in caso:
        estructura_esperada = caso['estructuraMEI']
        estructura_actual = st.session_state.get('estructura_mei_selector', 'NO EXISTE')
        if estructura_actual != estructura_esperada:
            logger.error(f"[CARGA_CASO] ERROR CRÍTICO: estructura_mei_selector no coincide!")
            logger.error(f"[CARGA_CASO]   - Esperado: {estructura_esperada}")
            logger.error(f"[CARGA_CASO]   - Actual: {estructura_actual}")
            st.session_state.estructura_mei_selector = estructura_esperada
            logger.info(f"[CARGA_CASO] estructura_mei_selector corregido a: {st.session_state.estructura_mei_selector}")
        else:
            logger.info(f"[CARGA_CASO] estructura_mei_selector verificado correctamente: {estructura_actual}")
    
    logger.info(f"[CARGA_CASO] Haciendo rerun...")
    logger.info("=" * 80)
    st.success(f"✅ Caso '{caso_nombre_final}' cargado exitosamente")
    st.rerun()

# Este flag ya no se usa - el sistema usa widget_version directamente
# Agregar log al inicio de cada rerun para debugging
logger.info(f"[INICIO_RERUN] Iniciando nuevo ciclo de renderizado")
logger.info(f"[INICIO_RERUN]   - widget_version: {st.session_state.get('widget_version', 0)}")
logger.info(f"[INICIO_RERUN]   - workflow_type: {st.session_state.get('workflow_type', 'NO DEFINIDO')}")
logger.info(f"[INICIO_RERUN]   - estructura_mei_selector: {st.session_state.get('estructura_mei_selector', 'NO DEFINIDO')}")
logger.info(f"[INICIO_RERUN]   - nombre_curso: '{st.session_state.get('nombre_curso', 'NO DEFINIDO')}'")
logger.info(f"[INICIO_RERUN]   - rf_list length: {len(st.session_state.get('rf_list', []))}")
logger.info(f"[INICIO_RERUN]   - ra_list length: {len(st.session_state.get('ra_list', []))}")

col_workflow, col_casos = st.columns([1.2, 1.8])

# Columna izquierda: Selección de Workflow
with col_workflow:
    col_title, col_info = st.columns([1, 0.1])
    with col_title:
        st.markdown("**1️⃣ Workflow**")
    with col_info:
        st.markdown("""
        <div title="Selecciona si quieres GENERAR nuevos indicadores desde RA/AE, o REVISAR indicadores existentes para evaluar su calidad y mejorarlos.">
        ℹ️
        </div>
        """, unsafe_allow_html=True)
    
    # Manejar caso cargado
    if 'caso_workflow_display' in st.session_state:
        workflow_default = st.session_state.caso_workflow_display
        del st.session_state.caso_workflow_display
        if workflow_default == "Generar Indicadores":
            st.session_state.workflow_type = "generar-indicadores-v2"
        else:
            st.session_state.workflow_type = "revisar-indicadores-v2"
        # Forzar actualización del radio button
        if 'workflow_radio' in st.session_state:
            del st.session_state.workflow_radio
    
    if 'workflow_type' not in st.session_state:
        st.session_state.workflow_type = "generar-indicadores-v2"
    
    # Determinar el índice correcto basado en workflow_type
    workflow_index = 0 if st.session_state.workflow_type == "generar-indicadores-v2" else 1
    logger.info(f"[RENDER] Radio button - workflow_type: {st.session_state.workflow_type}, index: {workflow_index}, widget_version: {st.session_state.widget_version}")
    
    # SIEMPRE usar key dinámica basada en widget_version para forzar actualización cuando se carga un caso
    radio_key = f"workflow_radio_v{st.session_state.widget_version}"
    logger.info(f"[RENDER] Radio button - key: {radio_key}")
    
    workflow_display = st.radio(
        "Seleccionar:",
        options=["Generar Indicadores", "Revisar Indicadores"],
        index=workflow_index,
        key=radio_key
    )
    
    if workflow_display == "Generar Indicadores":
        workflow_type = "generar-indicadores-v2"
        st.caption("Crea nuevos indicadores desde RA/AE")
    else:
        workflow_type = "revisar-indicadores-v2"
        st.caption("Revisa y mejora indicadores existentes")
    
    # Detectar si el workflow cambió desde el radio button
    workflow_anterior = st.session_state.get('workflow_type', 'generar-indicadores-v2')
    if workflow_type != workflow_anterior:
        # El workflow cambió desde el radio button, marcar para evitar verificación de caso
        # Esto previene loops infinitos cuando el usuario cambia el workflow manualmente
        st.session_state.workflow_cambiado_por_radio = True
        # Actualizar last_workflow inmediatamente para evitar resets innecesarios
        if 'last_workflow' not in st.session_state:
            st.session_state.last_workflow = workflow_type
    
    st.session_state.workflow_type = workflow_type

# Columna derecha: Gestión de Casos
with col_casos:
    st.markdown("**2️⃣ Gestión de Casos**")
    
    # Primera fila: Cargar caso
    col_caso1, col_caso2, col_caso3 = st.columns([3, 1, 1])
    with col_caso1:
        casos_disponibles = list(st.session_state.casos_guardados.keys())
        caso_1_nombre = "Caso 1 - Ejemplo MEI Actualizado (Generar)"
        if caso_1_nombre in casos_disponibles:
            indice_default = casos_disponibles.index(caso_1_nombre)
        else:
            indice_default = 0 if len(casos_disponibles) > 0 else None
        
    caso_seleccionado = st.selectbox(
            "**Caso:**",
        options=casos_disponibles,
            index=indice_default if indice_default is not None else 0,
            help="Selecciona un caso guardado",
            key="caso_seleccionado_gestor",
            label_visibility="collapsed"
        )
    
    # Log cuando se selecciona un caso
    if caso_seleccionado:
        logger.info(f"[SELECTBOX] Caso seleccionado en dropdown: '{caso_seleccionado}'")
        if caso_seleccionado in st.session_state.casos_guardados:
            caso_temp = st.session_state.casos_guardados[caso_seleccionado]
            logger.info(f"[SELECTBOX]   - workflow del caso: {caso_temp.get('workflow', 'NO DEFINIDO')}")
            logger.info(f"[SELECTBOX]   - workflow actual: {st.session_state.get('workflow_type', 'NO DEFINIDO')}")
    
    # Limpiar el flag de cambio por radio después de verificar
    if 'workflow_cambiado_por_radio' in st.session_state:
        del st.session_state.workflow_cambiado_por_radio
    
    with col_caso2:
        if caso_seleccionado and caso_seleccionado != "":
            if st.button("📂", key="btn_cargar_caso_gestor", help="Cargar caso", use_container_width=True):
                if caso_seleccionado in st.session_state.casos_guardados:
                    logger.info(f"[BOTON] Click en 'Cargar caso' - caso seleccionado: '{caso_seleccionado}'")
                    logger.info(f"[BOTON] Estado ANTES de establecer caso_a_cargar:")
                    logger.info(f"[BOTON]   - workflow_type: {st.session_state.get('workflow_type', 'NO DEFINIDO')}")
                    logger.info(f"[BOTON]   - estructura_mei_selector: {st.session_state.get('estructura_mei_selector', 'NO DEFINIDO')}")
                    logger.info(f"[BOTON]   - widget_version: {st.session_state.get('widget_version', 0)}")
                    
                    # Verificar el workflow del caso antes de cargar
                    caso = st.session_state.casos_guardados[caso_seleccionado]
                    workflow_del_caso = caso.get('workflow', 'generar-indicadores-v2')
                    workflow_actual = st.session_state.get('workflow_type', 'generar-indicadores-v2')
                    logger.info(f"[BOTON]   - workflow del caso: {workflow_del_caso}")
                    logger.info(f"[BOTON]   - workflow actual: {workflow_actual}")
                    
                    # Establecer caso_a_cargar - esto se procesará al inicio del siguiente rerun
                    st.session_state.caso_a_cargar = caso_seleccionado
                    logger.info(f"[BOTON] caso_a_cargar establecido, haciendo rerun...")
                    st.rerun()
                else:
                    logger.error(f"[BOTON] ERROR: Caso '{caso_seleccionado}' no encontrado en casos_guardados")

    with col_caso3:
        if caso_seleccionado and caso_seleccionado != "":
            if st.button("🗑️", key="btn_eliminar_caso_gestor", help="Eliminar caso", use_container_width=True):
                del st.session_state.casos_guardados[caso_seleccionado]
                st.rerun()

    # Segunda fila: Guardar nuevo caso
    col_guardar1, col_guardar2 = st.columns([3, 1])
    with col_guardar1:
        nuevo_caso_nombre = st.text_input(
            "**Guardar:**",
            value="",
            placeholder="Nombre del caso...",
            key="nuevo_caso_nombre_input",
            label_visibility="collapsed"
        )
    with col_guardar2:
        if st.button("💾", key="btn_guardar_caso_gestor", help="Guardar caso", use_container_width=True, disabled=not nuevo_caso_nombre):
            if nuevo_caso_nombre:
                st.session_state.caso_a_guardar = nuevo_caso_nombre
                st.rerun()

# Inicializar listas si no existen (ANTES de cargar casos)
if 'ra_list' not in st.session_state:
    st.session_state.ra_list = [""]
if 'ae_list' not in st.session_state:
    st.session_state.ae_list = [""]
if 'rf_list' not in st.session_state:
    st.session_state.rf_list = [""]
if 'indicadores_list' not in st.session_state:
    st.session_state.indicadores_list = [""]

# NOTA: El procesamiento completo de casos se hace ANTES de renderizar widgets (línea ~172)
# Este bloque duplicado ya no es necesario y se elimina para evitar confusión
# El caso se procesa completamente arriba antes de renderizar cualquier widget

# Obtener workflow_type de session_state (ya establecido en la sección combinada)
workflow_type = st.session_state.get('workflow_type', 'generar-indicadores-v2')

# Resetear campos cuando cambia el workflow (solo si cambió manualmente, no por carga de caso)
# Verificar si el workflow cambió comparando con last_workflow
logger.info(f"[WORKFLOW] Verificando cambio de workflow")
logger.info(f"[WORKFLOW]   - workflow_type actual: {workflow_type}")
logger.info(f"[WORKFLOW]   - last_workflow: {st.session_state.get('last_workflow', 'NO DEFINIDO')}")

if 'last_workflow' not in st.session_state:
    st.session_state.last_workflow = workflow_type
    logger.info(f"[WORKFLOW] Inicializando last_workflow a: {workflow_type}")
elif st.session_state.last_workflow != workflow_type:
    # Solo resetear si el workflow cambió manualmente (no por carga de caso)
    # Si widget_version se incrementó recientemente, probablemente fue por carga de caso
    logger.info(f"[WORKFLOW] Workflow cambió de {st.session_state.last_workflow} a {workflow_type} - reseteando listas")
    if 'ra_list' in st.session_state:
        st.session_state.ra_list = [""]
    if 'ae_list' in st.session_state:
        st.session_state.ae_list = [""]
    if 'rf_list' in st.session_state:
        st.session_state.rf_list = [""]
    if 'indicadores_list' in st.session_state:
        st.session_state.indicadores_list = [""]
    st.session_state.last_workflow = workflow_type

# Sección: Configuración del DI (condensada)
st.subheader("📝 Configuración del Diseño Instruccional")

# Determinar el valor por defecto para estructura MEI
# Priorizar estructura_mei_selector si existe (se establece al cargar un caso)
if 'estructura_mei_selector' in st.session_state:
    estructura_default = st.session_state.estructura_mei_selector
elif 'caso_estructura_mei' in st.session_state:
    estructura_default = st.session_state.caso_estructura_mei
    st.session_state.estructura_mei_selector = estructura_default
    del st.session_state.caso_estructura_mei
else:
    estructura_default = "MEI-Antiguo"
    if 'estructura_mei_selector' not in st.session_state:
        st.session_state.estructura_mei_selector = estructura_default

estructura_index = 0 if estructura_default == "MEI-Antiguo" else 1

# Layout compacto: Primera fila con más elementos
col_mei, col_nombre, col_trimestre = st.columns([1.2, 2, 1])
with col_mei:
    # SIEMPRE usar key dinámica basada en widget_version para forzar actualización
    selector_key = f"estructura_mei_selector_v{st.session_state.widget_version}"
    logger.info(f"[RENDER] Renderizando selectbox MEI con key: {selector_key}, index: {estructura_index}, estructura_default: {estructura_default}")
    estructura_mei = st.selectbox(
        "**Estructura MEI**",
        options=["MEI-Antiguo", "MEI-Actualizado"],
        index=estructura_index,
        help="**MEI-Antiguo:** Estructura con RA → AE → IL (Indicadores de Logro). | **MEI-Actualizado:** Estructura con RF → RA → ID (Indicadores de Desempeño). Selecciona según el modelo educativo que estés utilizando.",
        key=selector_key
    )
    # Actualizar el valor en session_state
    estructura_mei_anterior = st.session_state.get('estructura_mei_selector', 'NO DEFINIDO')
    st.session_state.estructura_mei_selector = estructura_mei
    logger.info(f"[RENDER] Selector MEI renderizado - valor anterior: {estructura_mei_anterior}, valor nuevo: {estructura_mei}, key: {selector_key}")
    logger.info(f"[RENDER] estructura_mei_selector en session_state después de renderizar: {st.session_state.estructura_mei_selector}")
    
with col_nombre:
    if 'nombre_curso' not in st.session_state:
        st.session_state.nombre_curso = ""
    # Usar key dinámica basada en widget_version
    nombre_key = f"nombre_curso_input_v{st.session_state.widget_version}"
    nombre_curso = st.text_input(
        "**Nombre del Curso**",
        value=st.session_state.nombre_curso,
        key=nombre_key,
        placeholder="Ej: Didáctica General"
    )
    st.session_state.nombre_curso = nombre_curso
    logger.info(f"[DEBUG] Campo nombre_curso - valor: {nombre_curso}, key: {nombre_key}")

with col_trimestre:
    if 'trimestre' not in st.session_state:
        st.session_state.trimestre = ""
    trimestre = st.text_input(
        "**Trimestre** (Opcional)",
        value=st.session_state.trimestre,
        key=f"trimestre_input_v{st.session_state.widget_version}",
        placeholder="Ej: 1",
        help="Período académico o trimestre al que pertenece este objetivo. Este dato se incluirá automáticamente en las prompts si lo completas."
    )
    st.session_state.trimestre = trimestre

# Segunda fila: Metodología, Agentes e Indicadores
col_metodologia, col_agentes, col_indicadores = st.columns([2, 1.2, 1])
with col_metodologia:
    if 'metodologia' not in st.session_state:
        st.session_state.metodologia = ""
    metodologia = st.text_input(
        "**Metodología** (Opcional)",
        value=st.session_state.metodologia,
        key=f"metodologia_input_v{st.session_state.widget_version}",
        placeholder="Ej: Aprendizaje basado en proyectos",
        help="Metodología de enseñanza propuesta para este objetivo. Este dato se incluirá automáticamente en las prompts si lo completas."
    )
    st.session_state.metodologia = metodologia

with col_agentes:
    if 'cantidad_agentes' not in st.session_state:
        st.session_state.cantidad_agentes = 2
    
    col_agentes_title, col_agentes_info = st.columns([1, 0.1])
    with col_agentes_title:
        st.markdown("**Agentes IA**")
    with col_agentes_info:
        st.markdown("""
        <div title="**1 Agente:** Un solo agente realiza todo el trabajo (generación o revisión completa). | **2 Agentes:** El primer agente descompone/analiza, el segundo agente genera/evalúa. Permite mayor especialización y control.">
        ℹ️
        </div>
        """, unsafe_allow_html=True)
    # Toggle visual compacto
    toggle_col1, toggle_col2 = st.columns(2)
    cantidad_agentes_actual = st.session_state.cantidad_agentes
    
    with toggle_col1:
        button_style_1 = "primary" if cantidad_agentes_actual == 1 else "secondary"
        if st.button("**1**", key="toggle_1_agente", use_container_width=True, type=button_style_1, help="Un solo agente realiza todo el trabajo"):
            st.session_state.cantidad_agentes = 1
            st.rerun()
    
    with toggle_col2:
        button_style_2 = "primary" if cantidad_agentes_actual == 2 else "secondary"
        if st.button("**2**", key="toggle_2_agentes", use_container_width=True, type=button_style_2, help="Dos agentes trabajan en secuencia: el primero descompone/analiza, el segundo genera/evalúa"):
            st.session_state.cantidad_agentes = 2
            st.rerun()
    
    cantidad_agentes = st.session_state.cantidad_agentes

with col_indicadores:
    if 'cantidad_indicadores' not in st.session_state:
        st.session_state.cantidad_indicadores = 3
    cantidad_indicadores = st.number_input(
        "**Indicadores**",
        min_value=1,
        max_value=10,
        value=st.session_state.cantidad_indicadores,
        step=1,
        key="cantidad_indicadores_input",
        help="Cantidad de indicadores que deseas generar. Recomendado: 3-5 indicadores por RA/AE para mantener un buen balance entre cobertura y especificidad."
    )
    st.session_state.cantidad_indicadores = cantidad_indicadores

# Resetear campos cuando cambia la estructura MEI (solo si cambió manualmente, no por carga de caso)
# Verificar si la estructura cambió comparando con last_estructura
logger.info(f"[ESTRUCTURA] Verificando cambio de estructura MEI")
logger.info(f"[ESTRUCTURA]   - estructura_mei actual: {estructura_mei}")
logger.info(f"[ESTRUCTURA]   - last_estructura: {st.session_state.get('last_estructura', 'NO DEFINIDO')}")

if 'last_estructura' not in st.session_state:
    st.session_state.last_estructura = estructura_mei
    logger.info(f"[ESTRUCTURA] Inicializando last_estructura a: {estructura_mei}")
elif st.session_state.last_estructura != estructura_mei:
    # Solo resetear si la estructura cambió manualmente (no por carga de caso)
    # Si widget_version se incrementó recientemente, probablemente fue por carga de caso
    logger.info(f"[ESTRUCTURA] Estructura MEI cambió de {st.session_state.last_estructura} a {estructura_mei} - reseteando listas")
    st.session_state.ra_list = [""]
    st.session_state.ae_list = [""]
    st.session_state.rf_list = [""]
    st.session_state.indicadores_list = [""]
    st.session_state.last_estructura = estructura_mei
    st.session_state.widget_version += 1

# Campos dinámicos según estructura MEI
# Asegurarse de que las listas tengan al menos un elemento para renderizar
logger.info(f"[RENDER] Verificando listas antes de renderizar campos dinámicos:")
logger.info(f"[RENDER]   - ra_list length: {len(st.session_state.get('ra_list', []))}")
logger.info(f"[RENDER]   - ae_list length: {len(st.session_state.get('ae_list', []))}")
logger.info(f"[RENDER]   - rf_list length: {len(st.session_state.get('rf_list', []))}")
logger.info(f"[RENDER]   - indicadores_list length: {len(st.session_state.get('indicadores_list', []))}")

if len(st.session_state.ra_list) == 0:
    st.session_state.ra_list = [""]
    logger.info(f"[RENDER] Inicializando ra_list vacía")
if len(st.session_state.ae_list) == 0:
    st.session_state.ae_list = [""]
    logger.info(f"[RENDER] Inicializando ae_list vacía")
if len(st.session_state.rf_list) == 0:
    st.session_state.rf_list = [""]
    logger.info(f"[RENDER] Inicializando rf_list vacía")
if len(st.session_state.indicadores_list) == 0:
    st.session_state.indicadores_list = [""]
    logger.info(f"[RENDER] Inicializando indicadores_list vacía")

# Separador visual antes de campos dinámicos
st.markdown("---")

if estructura_mei == "MEI-Antiguo":
    col_mei_antiguo_title, col_mei_antiguo_info = st.columns([1, 0.1])
    with col_mei_antiguo_title:
        st.markdown("### 📚 MEI Antiguo (RA - AE - IL)")
    with col_mei_antiguo_info:
        st.markdown("""
        <div title="**MEI-Antiguo:** Estructura con Resultado de Aprendizaje (RA) → Aprendizaje Esperado (AE) → Indicadores de Logro (IL). El RA es el contexto superior, el AE es el objetivo específico, y los IL son los peldaños para alcanzar el AE.">
        ℹ️
        </div>
        """, unsafe_allow_html=True)
    
    # Columnas lado a lado: RA (izquierda) y AE (derecha)
    col_ra, col_ae = st.columns(2)  # type: ignore
    
    # Columna izquierda: Resultados de Aprendizaje (RA)
    with col_ra:
        col_ra_title, col_ra_info = st.columns([1, 0.1])
        with col_ra_title:
            st.markdown("#### Resultados de Aprendizaje (RA)")
        with col_ra_info:
            st.markdown("""
            <div title="**Resultado de Aprendizaje (RA):** Objetivo principal que el estudiante debe lograr. En MEI-Antiguo, el RA es el contexto superior del Aprendizaje Esperado (AE).">
            ℹ️
            </div>
            """, unsafe_allow_html=True)
        
        for idx, ra in enumerate(st.session_state.ra_list):
            col1, col2 = st.columns([10, 1])
            with col1:
                # Usar key dinámica basada en widget_version
                ra_key = f"ra_{idx}_v{st.session_state.widget_version}"
                valor_ra = ra if ra else ""
                st.session_state.ra_list[idx] = st.text_area(
                    f"**RA {idx + 1}:**",
                    value=valor_ra,
                    key=ra_key,
                    height=60
                )
                logger.info(f"[DEBUG] RA {idx} (MEI-Antiguo) - valor length: {len(valor_ra)}, key: {ra_key}")
            with col2:
                if len(st.session_state.ra_list) > 1:
                    if st.button("🗑️", key=f"remove_ra_{idx}", help="Eliminar este RA"):
                        st.session_state.ra_list.pop(idx)
                        st.rerun()
        
        col_btn1, col_btn2, col_btn3 = st.columns([1, 2, 1])
        with col_btn2:
            if st.button("➕ Agregar RA", key="add_ra"):
                st.session_state.ra_list.append("")
                st.rerun()
    
    # Columna derecha: Aprendizajes Esperados (AE)
    with col_ae:  # type: ignore
        col_ae_title, col_ae_info = st.columns([1, 0.1])
        with col_ae_title:
            st.markdown("#### Aprendizajes Esperados (AE)")
        with col_ae_info:
            st.markdown("""
            <div title="**Aprendizaje Esperado (AE):** Objetivo específico que el estudiante debe lograr. En MEI-Antiguo, el AE es el objetivo inmediato que se descompone en Indicadores de Logro (IL).">
            ℹ️
            </div>
            """, unsafe_allow_html=True)
        
        for idx, ae in enumerate(st.session_state.ae_list):
            col1, col2 = st.columns([10, 1])
            with col1:
                st.session_state.ae_list[idx] = st.text_area(
                    f"**AE {idx + 1}:**",
                    value=ae,
                    key=f"ae_{idx}_v{st.session_state.widget_version}",
                    height=60
                )
            with col2:
                if len(st.session_state.ae_list) > 1:
                    if st.button("🗑️", key=f"remove_ae_{idx}", help="Eliminar este AE"):
                        st.session_state.ae_list.pop(idx)
                        st.rerun()
        
        col_btn1, col_btn2, col_btn3 = st.columns([1, 2, 1])
        with col_btn2:
            if st.button("➕ Agregar AE", key="add_ae"):
                st.session_state.ae_list.append("")
                st.rerun()
    
    # Para revisar indicadores, necesitamos indicadores a revisar
    if workflow_type == "revisar-indicadores-v2":
        col_ind_title, col_ind_info = st.columns([1, 0.1])
        with col_ind_title:
            st.markdown("#### Indicadores a Revisar")
        with col_ind_info:
            st.markdown("""
            <div title="**Indicadores a Revisar:** Lista de indicadores existentes que deseas evaluar y mejorar. El sistema analizará cada indicador según los estándares de Quality Matters y la Taxonomía de Bloom.">
            ℹ️
            </div>
            """, unsafe_allow_html=True)
        
        for idx, ind in enumerate(st.session_state.indicadores_list):
            col1, col2 = st.columns([10, 1])
            with col1:
                st.session_state.indicadores_list[idx] = st.text_area(
                    f"**Indicador {idx + 1}:**",
                    value=ind,
                    key=f"ind_{idx}_v{st.session_state.widget_version}",
                    height=50
                )
            with col2:
                if len(st.session_state.indicadores_list) > 1:
                    if st.button("🗑️", key=f"remove_ind_{idx}", help="Eliminar este indicador"):
                        st.session_state.indicadores_list.pop(idx)
                        st.rerun()
        
        col1, col2 = st.columns([1, 10])
        with col1:
            if st.button("➕ Agregar Indicador", key="add_ind"):
                st.session_state.indicadores_list.append("")
                st.rerun()

else:  # MEI-Actualizado
    logger.info(f"[RENDER] Renderizando campos MEI-Actualizado")
    st.markdown("### 📚 MEI Actualizado (RF - RA - ID)")
    
    # Columnas lado a lado: RF (izquierda) y RA (derecha)
    col_rf, col_ra = st.columns(2)
    
    # Columna izquierda: Resultados Formativos (RF)
    with col_rf:
        col_rf_title, col_rf_info = st.columns([1, 0.1])
        with col_rf_title:
            st.markdown("#### Resultados Formativos (RF)")
        with col_rf_info:
            st.markdown("""
            <div title="**Resultado Formativo (RF):** Contexto superior que enmarca el objetivo de aprendizaje. En MEI-Actualizado, el RF es el contexto del Resultado de Aprendizaje (RA).">
            ℹ️
            </div>
            """, unsafe_allow_html=True)
        
        for idx, rf in enumerate(st.session_state.rf_list):
            col1, col2 = st.columns([10, 1])
            with col1:
                # Si se cargó un caso recientemente, usar key dinámica para forzar actualización
                usar_key_dinamica_rf = 'caso_recien_cargado' in st.session_state and st.session_state.caso_recien_cargado
                rf_key = f"rf_{idx}_v{st.session_state.widget_version}" if usar_key_dinamica_rf else f"rf_{idx}"
                st.session_state.rf_list[idx] = st.text_area(
                    f"**RF {idx + 1}:**",
                    value=rf,
                    key=rf_key,
                    height=60
                )
            with col2:
                if len(st.session_state.rf_list) > 1:
                    if st.button("🗑️", key=f"remove_rf_{idx}", help="Eliminar este RF"):
                        st.session_state.rf_list.pop(idx)
                        st.rerun()
        
        col_btn1, col_btn2, col_btn3 = st.columns([1, 2, 1])
        with col_btn2:
            if st.button("➕ Agregar RF", key="add_rf"):
                st.session_state.rf_list.append("")
                st.rerun()
    
    # Columna derecha: Resultados de Aprendizaje (RA)
    with col_ra:
        col_ra_title, col_ra_info = st.columns([1, 0.1])
        with col_ra_title:
            st.markdown("#### Resultados de Aprendizaje (RA)")
        with col_ra_info:
            st.markdown("""
            <div title="**Resultado de Aprendizaje (RA):** Objetivo principal que el estudiante debe lograr. En MEI-Actualizado, el RA se descompone en Indicadores de Desempeño (ID).">
            ℹ️
            </div>
            """, unsafe_allow_html=True)
        
        for idx, ra in enumerate(st.session_state.ra_list):
            col1, col2 = st.columns([10, 1])
            with col1:
                # Usar key dinámica basada en widget_version
                ra_key_mei = f"ra_mei_{idx}_v{st.session_state.widget_version}"
                valor_ra = ra if ra else ""
                st.session_state.ra_list[idx] = st.text_area(
                    f"**RA {idx + 1}:**",
                    value=valor_ra,
                    key=ra_key_mei,
                    height=60
                )
                logger.info(f"[DEBUG] RA {idx} (MEI-Actualizado) - valor length: {len(valor_ra)}, key: {ra_key_mei}")
            with col2:
                if len(st.session_state.ra_list) > 1:
                    if st.button("🗑️", key=f"remove_ra_{idx}", help="Eliminar este RA"):
                        st.session_state.ra_list.pop(idx)
                        st.rerun()
        
        col_btn1, col_btn2, col_btn3 = st.columns([1, 2, 1])
        with col_btn2:
            if st.button("➕ Agregar RA", key="add_ra"):
                st.session_state.ra_list.append("")
                st.rerun()
    
    # Para revisar indicadores, necesitamos indicadores a revisar
    if workflow_type == "revisar-indicadores-v2":
        col_ind_title, col_ind_info = st.columns([1, 0.1])
        with col_ind_title:
            st.markdown("#### Indicadores a Revisar")
        with col_ind_info:
            st.markdown("""
            <div title="**Indicadores a Revisar:** Lista de indicadores existentes que deseas evaluar y mejorar. El sistema analizará cada indicador según los estándares de Quality Matters y la Taxonomía de Bloom.">
            ℹ️
            </div>
            """, unsafe_allow_html=True)
        
        for idx, ind in enumerate(st.session_state.indicadores_list):
            col1, col2 = st.columns([10, 1])
            with col1:
                st.session_state.indicadores_list[idx] = st.text_area(
                    f"**Indicador {idx + 1}:**",
                    value=ind,
                    key=f"ind_{idx}_v{st.session_state.widget_version}",
                    height=50
                )
            with col2:
                if len(st.session_state.indicadores_list) > 1:
                    if st.button("🗑️", key=f"remove_ind_{idx}", help="Eliminar este indicador"):
                        st.session_state.indicadores_list.pop(idx)
                        st.rerun()
        
        col1, col2 = st.columns([1, 10])
        with col1:
            if st.button("➕ Agregar Indicador", key="add_ind"):
                st.session_state.indicadores_list.append("")
                st.rerun()

# El flag caso_recien_cargado ya no se usa - el sistema usa widget_version directamente

# Guardar caso si hay uno pendiente (DESPUÉS de que se definan todas las variables)
if 'caso_a_guardar' in st.session_state and st.session_state.caso_a_guardar:
    nuevo_caso_nombre = st.session_state.caso_a_guardar
    # Guardar caso actual (usar valores de session_state para listas)
    caso_actual = {
        "workflow": workflow_type,
        "estructuraMEI": estructura_mei,
        "nombre_curso": st.session_state.nombre_curso if 'nombre_curso' in st.session_state else "",
        "trimestre": st.session_state.trimestre if 'trimestre' in st.session_state else "",
        "metodologia": st.session_state.metodologia if 'metodologia' in st.session_state else "",
        "cantidad_indicadores": st.session_state.cantidad_indicadores if 'cantidad_indicadores' in st.session_state else 3,
        "cantidad_agentes": st.session_state.cantidad_agentes if 'cantidad_agentes' in st.session_state else 2,
        "rf_list": st.session_state.rf_list.copy() if 'rf_list' in st.session_state else [],
        "ra_list": st.session_state.ra_list.copy() if 'ra_list' in st.session_state else [],
        "ae_list": st.session_state.ae_list.copy() if 'ae_list' in st.session_state else [],
        "indicadores_list": st.session_state.indicadores_list.copy() if 'indicadores_list' in st.session_state else [],
        "agente_1": st.session_state.agente_1 if 'agente_1' in st.session_state else "",
        "agente_2": st.session_state.agente_2 if 'agente_2' in st.session_state else ""
    }
    st.session_state.casos_guardados[nuevo_caso_nombre] = caso_actual
    del st.session_state.caso_a_guardar
    st.success(f"✅ Caso '{nuevo_caso_nombre}' guardado exitosamente")
    st.rerun()

# Funciones para obtener instrucciones de ejemplo y persistencia
def obtener_clave_persistencia(workflow_type, cantidad_agentes, estructura_mei):
    """Genera una clave única para persistir prompts según la combinación"""
    # Normalizar estructura_mei para la clave
    mei_key = estructura_mei.replace("-", "_") if estructura_mei else "MEI_Actualizado"
    return f"prompt_{workflow_type}_{cantidad_agentes}_{mei_key}"

def obtener_instrucciones_ejemplo(workflow_type, cantidad_agentes, estructura_mei, agente_num):
    """Obtiene las instrucciones de ejemplo para un agente según la combinación"""
    if workflow_type == "generar-indicadores-v2":
        if cantidad_agentes == 1:
            if estructura_mei == 'MEI-Actualizado':
                if agente_num == 1:
                    return """### [INSTRUCCIONES]

Eres un experto en diseño instruccional y evaluación pedagógica, especializado en la Taxonomía de Bloom revisada y los estándares de Quality Matters.

Tu tarea es generar Indicadores de Desempeño (ID) que sean:
- **Observables y medibles** (Quality Matters Standard 3.1)
- **Alineados con el Resultado de Aprendizaje (RA)** (Quality Matters Standard 2.1)
- **Progresivos en complejidad cognitiva** (Taxonomía de Bloom)
- **Libres de finalidad** (describen evidencias, no propósitos)

Genera EXACTAMENTE 3 Indicadores de Desempeño (ID) que cumplan con los estándares de Quality Matters y la Taxonomía de Bloom.

Para cada indicador, describe:
1. El texto completo del indicador (debe comenzar con el verbo en TERCERA PERSONA PLURAL INDICATIVO PRESENTE, ej. "EXPLICAN", "DIFERENCIAN", "INTEGRAN")
2. El verbo principal utilizado (en infinitivo, ej. "EXPLICAR", "DIFERENCIAR")
3. El Nivel Taxonómico de Bloom (1-6) de ese verbo, justificando por qué corresponde a ese nivel
4. Una justificación pedagógica breve (1 frase) explicando cómo este ID es necesario para construir el RA principal

**PROHIBICIÓN ABSOLUTA:** El indicador NO debe contener finalidad. Está terminantemente prohibido usar: "para", "con el fin de", "con el propósito de", "a fin de", "con la intención de" o sinónimos.

Responde de forma clara y estructurada, describiendo cada indicador con precisión. NO uses formato JSON, solo texto descriptivo."""
            else:  # MEI-Antiguo
                if agente_num == 1:
                    return """### [INSTRUCCIONES]

Eres un experto en diseño instruccional y evaluación pedagógica, especializado en la Taxonomía de Bloom revisada y los estándares de Quality Matters.

Tu tarea es generar Indicadores de Logro (IL) que sean:
- **Observables y medibles** (Quality Matters Standard 3.1)
- **Alineados con el Aprendizaje Esperado (AE)** (Quality Matters Standard 2.1)
- **Progresivos en complejidad cognitiva** (Taxonomía de Bloom)
- **Libres de finalidad** (describen evidencias, no propósitos)

Genera EXACTAMENTE 3 Indicadores de Logro (IL) que cumplan con los estándares de Quality Matters y la Taxonomía de Bloom.

Para cada indicador, describe:
1. La habilidad (verbo de acción principal en TERCERA PERSONA PLURAL INDICATIVO PRESENTE, ej. "DIFERENCIAN", "EXPLICAN") y su nivel de Bloom correspondiente
2. El contenido (el "qué" se evalúa - el objeto directo del verbo)
3. La condición/contexto (el "cómo" o "dónde" se realiza la acción)
4. Una justificación pedagógica breve (1 frase) explicando cómo este IL es necesario para construir el AE principal

**PROHIBICIÓN ABSOLUTA:** El indicador NO debe contener finalidad. Está terminantemente prohibido usar: "para", "con el fin de", "con el propósito de", "a fin de", "con la intención de" o sinónimos.

Responde de forma clara y estructurada, describiendo cada indicador con precisión. NO uses formato JSON, solo texto descriptivo."""
        else:  # cantidad_agentes == 2
            if agente_num == 1:
                return """### [INSTRUCCIONES]

Eres un experto en diseño instruccional y evaluación pedagógica, especializado en la Taxonomía de Bloom y los estándares de Quality Matters.

Tu tarea es analizar el objetivo de aprendizaje proporcionado y generar un contexto pedagógico que facilite la creación de indicadores alineados con estándares de calidad.

Proporciona un análisis pedagógico del objetivo de aprendizaje que incluya:
1. La estructura cognitiva requerida para alcanzar el objetivo (identifica los niveles de Bloom necesarios)
2. Los prerrequisitos o conocimientos base que el estudiante debe tener
3. El contexto académico y profesional relevante para este objetivo
4. Consideraciones sobre la progresión de aprendizaje (desde habilidades básicas hacia complejas)

Responde de forma clara y estructurada, sin formato JSON."""
            else:  # agente_num == 2
                if estructura_mei == 'MEI-Actualizado':
                    return """### [INSTRUCCIONES]

Eres un experto en diseño instruccional y evaluación pedagógica, especializado en la Taxonomía de Bloom revisada y los estándares de Quality Matters.

Tu tarea es generar Indicadores de Desempeño (ID) que sean:
- **Observables y medibles** (Quality Matters Standard 3.1)
- **Alineados con el Resultado de Aprendizaje (RA)** (Quality Matters Standard 2.1)
- **Progresivos en complejidad cognitiva** (Taxonomía de Bloom)
- **Libres de finalidad** (describen evidencias, no propósitos)

Genera EXACTAMENTE 3 Indicadores de Desempeño (ID) que funcionen como "peldaños" para el RA.

Para cada indicador, describe:
1. El texto completo del indicador (debe comenzar con el verbo en TERCERA PERSONA PLURAL INDICATIVO PRESENTE, ej. "EXPLICAN", "DIFERENCIAN", "INTEGRAN")
2. El verbo principal utilizado (en infinitivo, ej. "EXPLICAR", "DIFERENCIAR")
3. El Nivel Taxonómico de Bloom (1-6) de ese verbo
4. Una justificación pedagógica breve (1 frase) explicando cómo este ID actúa como un "peldaño" necesario para construir el RA principal

IMPORTANTE: Debes generar EXACTAMENTE 3 indicadores, ni más ni menos.

Responde de forma natural y creativa, describiendo cada indicador con claridad. NO uses formato JSON, solo texto descriptivo."""
                else:  # MEI-Antiguo
                    return """### [INSTRUCCIONES]

Eres un experto en diseño instruccional y evaluación pedagógica, especializado en la Taxonomía de Bloom revisada y los estándares de Quality Matters.

Tu tarea es generar Indicadores de Logro (IL) que sean:
- **Observables y medibles** (Quality Matters Standard 3.1)
- **Alineados con el Aprendizaje Esperado (AE)** (Quality Matters Standard 2.1)
- **Progresivos en complejidad cognitiva** (Taxonomía de Bloom)
- **Libres de finalidad** (describen evidencias, no propósitos)

Genera EXACTAMENTE 3 Indicadores de Logro (IL) que funcionen como "peldaños" para el AE.

Para cada indicador, describe:
1. La habilidad (verbo de acción principal en TERCERA PERSONA PLURAL INDICATIVO PRESENTE, ej. "DIFERENCIAN", "EXPLICAN")
2. El contenido (el "qué" se evalúa - el objeto directo del verbo)
3. La condición/contexto (el "cómo" o "dónde" se realiza la acción)
4. Una justificación pedagógica breve (1 frase) explicando cómo este IL actúa como un "peldaño" necesario para construir el AE principal

IMPORTANTE: Debes generar EXACTAMENTE 3 indicadores, ni más ni menos.

Responde de forma natural y creativa, describiendo cada indicador con claridad. NO uses formato JSON, solo texto descriptivo."""
    else:  # workflow_type == "revisar-indicadores-v2"
        if cantidad_agentes == 1:
            if estructura_mei == 'MEI-Actualizado':
                if agente_num == 1:
                    return """### [INSTRUCCIONES]

Eres un experto en auditoría pedagógica y evaluación de indicadores, especializado en la Taxonomía de Bloom revisada y los estándares de Quality Matters.

Tu tarea es REVISAR Indicadores de Desempeño (ID) existentes y evaluar si cumplen con:
- **Observabilidad y medibilidad** (Quality Matters Standard 3.1)
- **Alineación con el Resultado de Aprendizaje (RA)** (Quality Matters Standard 2.1)
- **Progresión en complejidad cognitiva** (Taxonomía de Bloom)
- **Ausencia de finalidad** (describen evidencias, no propósitos)
- **Estructura correcta** (verbo observable + producto/proceso + condición/contexto)

Revisa CADA uno de los Indicadores de Desempeño (ID) proporcionados y evalúa si cumplen con los estándares de Quality Matters y la Taxonomía de Bloom.

Para cada indicador, proporciona:
1. **Deconstrucción estructural:** Extrae el verbo_detectado, producto_proceso_detectado y condicion_contexto_detectada
2. **Evaluación del verbo:** Identifica el verbo principal y su nivel de Bloom (1-6). Justifica por qué corresponde a ese nivel.
3. **Observabilidad y medibilidad:** Evalúa si el indicador es observable y medible según Quality Matters Standard 3.1.
4. **Alineación con el RA:** Evalúa si el indicador está directamente alineado con el RA principal (Quality Matters Standard 2.1).
5. **Presencia de finalidad:** Identifica si el indicador contiene frases de finalidad (ej. "para", "con el fin de", "con el propósito de"). Si las contiene, es un FALLO ESTRUCTURAL.
6. **Progresión cognitiva:** Evalúa si el indicador forma parte de una progresión lógica desde habilidades básicas hacia complejas.
7. **Recomendaciones:** Si el indicador tiene problemas, proporciona recomendaciones específicas de mejora.

**PROHIBICIÓN ABSOLUTA:** El indicador NO debe contener finalidad. Está terminantemente prohibido usar: "para", "con el fin de", "con el propósito de", "a fin de", "con la intención de" o sinónimos.

Responde de forma clara y estructurada, describiendo cada indicador con precisión. NO uses formato JSON, solo texto descriptivo."""
            else:  # MEI-Antiguo
                if agente_num == 1:
                    return """### [INSTRUCCIONES]

Eres un experto en auditoría pedagógica y evaluación de indicadores, especializado en la Taxonomía de Bloom revisada y los estándares de Quality Matters.

Tu tarea es REVISAR Indicadores de Logro (IL) existentes y evaluar si cumplen con:
- **Observabilidad y medibilidad** (Quality Matters Standard 3.1)
- **Alineación con el Aprendizaje Esperado (AE)** (Quality Matters Standard 2.1)
- **Progresión en complejidad cognitiva** (Taxonomía de Bloom)
- **Ausencia de finalidad** (describen evidencias, no propósitos)
- **Estructura correcta** (habilidad + contenido + condición/contexto)

Revisa CADA uno de los Indicadores de Logro (IL) proporcionados y evalúa si cumplen con los estándares de Quality Matters y la Taxonomía de Bloom.

Para cada indicador, proporciona:
1. **Deconstrucción estructural:** Extrae el verbo_detectado (habilidad), producto_proceso_detectado (contenido) y condicion_contexto_detectada
2. **Evaluación del verbo:** Identifica el verbo principal y su nivel de Bloom (1-6). Justifica por qué corresponde a ese nivel.
3. **Observabilidad y medibilidad:** Evalúa si el indicador es observable y medible según Quality Matters Standard 3.1.
4. **Alineación con el AE:** Evalúa si el indicador está directamente alineado con el AE principal (Quality Matters Standard 2.1).
5. **Presencia de finalidad:** Identifica si el indicador contiene frases de finalidad (ej. "para", "con el fin de", "con el propósito de"). Si las contiene, es un FALLO ESTRUCTURAL.
6. **Progresión cognitiva:** Evalúa si el indicador forma parte de una progresión lógica desde habilidades básicas hacia complejas.
7. **Recomendaciones:** Si el indicador tiene problemas, proporciona recomendaciones específicas de mejora.

**PROHIBICIÓN ABSOLUTA:** El indicador NO debe contener finalidad. Está terminantemente prohibido usar: "para", "con el fin de", "con el propósito de", "a fin de", "con la intención de" o sinónimos.

Responde de forma clara y estructurada, describiendo cada indicador con precisión. NO uses formato JSON, solo texto descriptivo."""
        else:  # cantidad_agentes == 2
            if agente_num == 1:
                if estructura_mei == 'MEI-Actualizado':
                    return """### [INSTRUCCIONES]

Eres un "Analista Estructural de Indicadores" de UNAB. Tu única tarea es "desarmar" (deconstruir) una lista de indicadores en sus 3 componentes estructurales.
NO debes emitir juicios, NO debes analizar la calidad, NO debes corregir. Solo debes CLASIFICAR y EXTRAER las piezas.

### REGLAS DE DECONSTRUCCIÓN (MEI ACTUALIZADO):
1. **"verbo_detectado":** Extrae el primer verbo conjugado (ej. "ANALIZAN").
2. **"producto_proceso_detectado":** Extrae el objeto directo del verbo (el "qué" se mide).
3. **"condicion_contexto_detectada":** Extrae el resto de la frase (el "cómo", "cuándo" o "dónde"). Si no existe, usa null.

### TU TAREA:
Analiza CADA indicador de la lista "INDICADORES A DECONSTRUIR".
Devuelve ÚNICAMENTE un array JSON con los objetos deconstruidos, siguiendo las reglas.
El array de salida debe tener EXACTAMENTE el mismo número de objetos que el array de entrada."""
                else:  # MEI-Antiguo
                    return """### [INSTRUCCIONES]

Eres un "Analista Estructural de Indicadores" de UNAB. Tu única tarea es "desarmar" (deconstruir) una lista de indicadores en sus 3 componentes estructurales.
NO debes emitir juicios, NO debes analizar la calidad, NO debes corregir. Solo debes CLASIFICAR y EXTRAER las piezas.

### REGLAS DE DECONSTRUCCIÓN (MEI ANTIGUO):
1. **"verbo_detectado":** Extrae el primer verbo conjugado (ej. "ANALIZAN").
2. **"producto_proceso_detectado":** Extrae el objeto directo del verbo (el "qué").
3. **"condicion_contexto_detectada":** Extrae el resto de la frase (el "cómo", "cuándo" o "dónde"). Si no existe, usa null.

### TU TAREA:
Analiza CADA indicador de la lista "INDICADORES A DECONSTRUIR".
Devuelve ÚNICAMENTE un array JSON con los objetos deconstruidos, siguiendo las reglas.
El array de salida debe tener EXACTAMENTE el mismo número de objetos que el array de entrada."""
            else:  # agente_num == 2
                return """### [INSTRUCCIONES]

Eres un "Auditor de Calidad Pedagógica" de UNAB, experto en el estándar 2.2 de Quality Matters.

Tu tarea es auditar un set de indicadores basándote en un análisis estructural y taxonómico pre-procesado.

### PRINCIPIOS DE REVISIÓN (TU LÓGICA DE AUDITORÍA INTERNA)

1. **Análisis de Finalidad:** El RA/AE describe el *propósito*. El Indicador describe la *EVIDENCIA*. Si un indicador contiene frases de finalidad (ej. "para", "con el fin de", "con el propósito de"), es un FALLO ESTRUCTURAL.

2. **Análisis de Observabilidad:** Los indicadores deben ser "medibles" y "observables". Verbos abstractos (ej. 'REFLEXIONAR', 'PENSAR', 'COMPRENDER', 'SABER', 'CONOCER') o Nivel 0 son procesos internos y NO son observables. Un verbo abstracto solo se vuelve medible si el contexto lo "ancla" a un producto tangible (ej. "REFLEXIONAR... *mediante un ensayo escrito*"). Si no está anclado, es un FALLO DE OBSERVABILIDAD.

3. **Análisis de Progresividad:** El alineamiento es pedagógico. Un indicador de nivel bajo (ej. Nivel 2 'COMPARAR') SÍ tiene **ALINEAMIENTO ALTO** si es un "peldaño" lógico y coherente ("smaller, discrete pieces") para un RA de nivel alto (ej. Nivel 6 'DISEÑAR'). El alineamiento es BAJO solo si el indicador falla el Análisis 1 o 2, o si es pedagógicamente irrelevante.

### TU PROCESO DE ANÁLISIS (Chain-of-Thought Interno)
Para CADA indicador, debes pensar en 3 pasos antes de escribir tu reporte:
1. **Paso 1 (Finalidad):** ¿El "indicador_original" contiene una frase de finalidad?
2. **Paso 2 (Observabilidad):** Revisa 'verbo_detectado', 'verbo_infinitivo' y 'nivel_verbo_detectado'.
3. **Paso 3 (Progresividad):** Asumiendo que P1 y P2 pasan, ¿es el "nivel_verbo_detectado" un "peldaño" lógico para el "NIVEL DEL RA/AE ESPERADO"?

### FORMATO DE REPORTE DE SALIDA (4 Claves, LENGUAJE DE USUARIO)
Basado en tu análisis de 3 pasos, genera el reporte final con las claves: "verbo_observable", "producto_o_proceso", "condicion_de_calidad_o_contexto", "alineamiento".

### FORMATO DE SALIDA OBLIGATORIO:
Devuelve ÚNICAMENTE un array JSON con los reportes. Cada objeto debe tener EXACTAMENTE estas 4 claves.

### TU TAREA:
Genera el array JSON de reportes (un reporte por cada indicador en los datos pre-procesados)."""
    return ""

def obtener_clave_persistencia(workflow_type, cantidad_agentes, estructura_mei):
    """Obtiene la clave única para persistir prompts según la combinación"""
    # Normalizar estructura_mei para la clave
    mei_key = estructura_mei.replace("-", "_") if estructura_mei else "MEI_Actualizado"
    return f"prompt_{workflow_type}_{cantidad_agentes}_{mei_key}"

def cargar_prompts_persistentes(workflow_type, cantidad_agentes, estructura_mei):
    """Carga las prompts persistentes para una combinación específica"""
    clave = obtener_clave_persistencia(workflow_type, cantidad_agentes, estructura_mei)
    logger.info(f"[DEBUG] Cargando prompts persistentes - clave: {clave}, workflow: {workflow_type}, agentes: {cantidad_agentes}, MEI: {estructura_mei}")
    if clave not in st.session_state:
        st.session_state[clave] = {"agente_1": "", "agente_2": ""}
        logger.info(f"[DEBUG] Clave nueva, inicializando con valores vacíos")
    else:
        agente_1_len = len(st.session_state[clave].get('agente_1', ''))
        agente_2_len = len(st.session_state[clave].get('agente_2', ''))
        logger.info(f"[DEBUG] Clave existente - agente_1 length: {agente_1_len}, agente_2 length: {agente_2_len}")
    return st.session_state[clave]

def guardar_prompts_persistentes(workflow_type, cantidad_agentes, estructura_mei, agente_1, agente_2):
    """Guarda las prompts persistentes para una combinación específica"""
    clave = obtener_clave_persistencia(workflow_type, cantidad_agentes, estructura_mei)
    logger.info(f"[DEBUG] Guardando prompts persistentes - clave: {clave}, agente_1 length: {len(agente_1)}, agente_2 length: {len(agente_2)}")
    st.session_state[clave] = {
        "agente_1": agente_1,
        "agente_2": agente_2,
        "ultima_actualizacion": datetime.now().isoformat()
    }

# Sección 4: Personalización de Prompts (opcional)
st.markdown("---")
st.subheader("4️⃣ Personalizar Prompts de los Agentes (Opcional)")
st.caption("Deja vacío para usar la prompt por defecto. Los datos automáticos (RF/RA, curso, etc.) siempre se incluyen. Usa la vista previa para ver la prompt completa.")

# Obtener workflow y cantidad de agentes
workflow_type = st.session_state.get('workflow_type', 'generar-indicadores-v2')
cantidad_agentes = st.session_state.get('cantidad_agentes', 2)

# Función para construir preview de prompt del Agente 1
def construir_preview_agente_1():
    """Construye una preview de la prompt completa del Agente 1"""
    # Obtener estructura MEI
    estructura_mei = st.session_state.get('estructura_mei_selector', 'MEI-Actualizado')
    if not estructura_mei or estructura_mei not in ['MEI-Actualizado', 'MEI-Antiguo']:
        estructura_mei = 'MEI-Actualizado'
    
    # Obtener cantidad de agentes y cantidad de indicadores
    cantidad_agentes = st.session_state.get('cantidad_agentes', 2)
    cantidad_indicadores = st.session_state.get('cantidad_indicadores', 3)
    
    # Prompt personalizado (si existe)
    prompt_personalizado = st.session_state.get('agente_1', '').strip()
    
    # PROMPT BASE: Vacío (solo se muestran los datos automáticos)
    prompt_base = ""
    
    # DATOS AUTOMÁTICOS: Los datos reales que se inyectan
    if estructura_mei == 'MEI-Actualizado':
        rf_texto = st.session_state.rf_list[0] if st.session_state.get('rf_list') and len(st.session_state.rf_list) > 0 and st.session_state.rf_list[0] else "No disponible"
        ra_texto = st.session_state.ra_list[0] if st.session_state.get('ra_list') and len(st.session_state.ra_list) > 0 and st.session_state.ra_list[0] else "No disponible"
        datos_automaticos = f"""### DATOS DE ENTRADA:

- **Resultado Formativo (RF):**
  "{rf_texto}"
  
- **Resultado de Aprendizaje (RA):**
  "{ra_texto}"
  
- **Nombre del Curso:**
  "{st.session_state.get('nombre_curso', 'Nombre de curso no disponible')}"
"""
    else:  # MEI-Antiguo
        ra_texto = st.session_state.ra_list[0] if st.session_state.get('ra_list') and len(st.session_state.ra_list) > 0 and st.session_state.ra_list[0] else "No disponible"
        ae_texto = st.session_state.ae_list[0] if st.session_state.get('ae_list') and len(st.session_state.ae_list) > 0 and st.session_state.ae_list[0] else "No disponible"
        datos_automaticos = f"""### DATOS DE ENTRADA:

- **Resultado de Aprendizaje (RA):**
  "{ra_texto}"
  
- **Aprendizaje Esperado (AE):**
  "{ae_texto}"
  
- **Nombre del Curso:**
  "{st.session_state.get('nombre_curso', 'Nombre de curso no disponible')}"
"""
    
    # Agregar trimestre solo si existe
    trimestre = st.session_state.get('trimestre', '').strip()
    if trimestre:
        datos_automaticos += f"\n- **Trimestre:**\n  {trimestre}"
    
    # Agregar metodología solo si existe
    metodologia = st.session_state.get('metodologia', '').strip()
    if metodologia:
        datos_automaticos += f"\n\n- **Metodología Propuesta:**\n  \"{metodologia}\""
    
    # [INSTRUCCIONES]: La tarea que debe realizar el agente (aquí impacta la prompt personalizada)
    if prompt_personalizado:
        # Si hay prompt personalizada, agregar encabezado si no lo tiene
        if not prompt_personalizado.strip().startswith("### INSTRUCCIONES") and not prompt_personalizado.strip().startswith("### [INSTRUCCIONES]"):
            instrucciones = f"### INSTRUCCIONES:\n\n{prompt_personalizado}"
        else:
            instrucciones = prompt_personalizado
    else:
        # Si no hay prompt personalizada, usar instrucciones por defecto
        if cantidad_agentes == 1:
            # 1 agente: generar indicadores directamente
            if estructura_mei == 'MEI-Actualizado':
                rf_texto = st.session_state.rf_list[0] if st.session_state.get('rf_list') and len(st.session_state.rf_list) > 0 and st.session_state.rf_list[0] else "No disponible"
                instrucciones = f"""### [INSTRUCCIONES]

Eres un experto en diseño instruccional y evaluación pedagógica, especializado en la Taxonomía de Bloom revisada y los estándares de Quality Matters.

Tu tarea es generar Indicadores de Desempeño (ID) que sean:
- **Observables y medibles** (Quality Matters Standard 3.1)
- **Alineados con el Resultado de Aprendizaje (RA)** (Quality Matters Standard 2.1)
- **Progresivos en complejidad cognitiva** (Taxonomía de Bloom)
- **Libres de finalidad** (describen evidencias, no propósitos)

### CONTEXTO SUPERIOR (RF):
{rf_texto}

### TU TAREA (MEI ACTUALIZADO):
Genera EXACTAMENTE {cantidad_indicadores} Indicadores de Desempeño (ID) que cumplan con los estándares de Quality Matters y la Taxonomía de Bloom.

**REQUISITOS DE CALIDAD (Quality Matters):**
- Cada indicador debe ser observable y medible
- Debe usar verbos de acción específicos y apropiados para el nivel de Bloom
- Debe estar directamente alineado con el RA
- Debe evitar ambigüedad y subjetividad

**PROGRESIÓN COGNITIVA (Taxonomía de Bloom):**
Los indicadores deben mostrar una progresión lógica desde niveles básicos (recordar, comprender) hacia niveles superiores (aplicar, analizar, evaluar, crear).

Para cada indicador, describe:
1. El texto completo del indicador (debe comenzar con el verbo en TERCERA PERSONA PLURAL INDICATIVO PRESENTE, ej. "EXPLICAN", "DIFERENCIAN", "INTEGRAN")
2. El verbo principal utilizado (en infinitivo, ej. "EXPLICAR", "DIFERENCIAR")
3. El Nivel Taxonómico de Bloom (1-6) de ese verbo, justificando por qué corresponde a ese nivel
4. Una justificación pedagógica breve (1 frase) explicando cómo este ID es necesario para construir el RA principal y cómo cumple con los estándares de Quality Matters

**PROHIBICIÓN ABSOLUTA:** El indicador NO debe contener finalidad. Está terminantemente prohibido usar: "para", "con el fin de", "con el propósito de", "a fin de", "con la intención de" o sinónimos.

IMPORTANTE: Debes generar EXACTAMENTE {cantidad_indicadores} indicadores, ni más ni menos.

Responde de forma clara y estructurada, describiendo cada indicador con precisión. NO uses formato JSON, solo texto descriptivo."""
            else:  # MEI-Antiguo
                ra_texto = st.session_state.ra_list[0] if st.session_state.get('ra_list') and len(st.session_state.ra_list) > 0 and st.session_state.ra_list[0] else "No disponible"
                instrucciones = f"""### [INSTRUCCIONES]

Eres un experto en diseño instruccional y evaluación pedagógica, especializado en la Taxonomía de Bloom revisada y los estándares de Quality Matters.

Tu tarea es generar Indicadores de Logro (IL) que sean:
- **Observables y medibles** (Quality Matters Standard 3.1)
- **Alineados con el Aprendizaje Esperado (AE)** (Quality Matters Standard 2.1)
- **Progresivos en complejidad cognitiva** (Taxonomía de Bloom)
- **Libres de finalidad** (describen evidencias, no propósitos)

### CONTEXTO SUPERIOR (RA):
{ra_texto}

### TU TAREA (MEI ANTIGUO):
Genera EXACTAMENTE {cantidad_indicadores} Indicadores de Logro (IL) que cumplan con los estándares de Quality Matters y la Taxonomía de Bloom.

**REQUISITOS DE CALIDAD (Quality Matters):**
- Cada indicador debe ser observable y medible
- Debe usar verbos de acción específicos y apropiados para el nivel de Bloom
- Debe estar directamente alineado con el AE
- Debe evitar ambigüedad y subjetividad

**PROGRESIÓN COGNITIVA (Taxonomía de Bloom):**
Los indicadores deben mostrar una progresión lógica desde niveles básicos (recordar, comprender) hacia niveles superiores (aplicar, analizar, evaluar, crear).

Para cada indicador, describe:
1. La habilidad (verbo de acción principal en TERCERA PERSONA PLURAL INDICATIVO PRESENTE, ej. "DIFERENCIAN", "EXPLICAN") y su nivel de Bloom correspondiente
2. El contenido (el "qué" se evalúa - el objeto directo del verbo)
3. La condición/contexto (el "cómo" o "dónde" se realiza la acción)
4. Una justificación pedagógica breve (1 frase) explicando cómo este IL es necesario para construir el AE principal y cómo cumple con los estándares de Quality Matters

**PROHIBICIÓN ABSOLUTA:** El indicador NO debe contener finalidad. Está terminantemente prohibido usar: "para", "con el fin de", "con el propósito de", "a fin de", "con la intención de" o sinónimos.

IMPORTANTE: Debes generar EXACTAMENTE {cantidad_indicadores} indicadores, ni más ni menos.

Responde de forma clara y estructurada, describiendo cada indicador con precisión. NO uses formato JSON, solo texto descriptivo."""
        else:
            # 2 agentes: solo análisis pedagógico
            instrucciones = """### [INSTRUCCIONES]

Eres un experto en diseño instruccional y evaluación pedagógica, especializado en la Taxonomía de Bloom y los estándares de Quality Matters.

Tu tarea es analizar el objetivo de aprendizaje proporcionado y generar un contexto pedagógico que facilite la creación de indicadores alineados con estándares de calidad.

Proporciona un análisis pedagógico del objetivo de aprendizaje que incluya:
1. La estructura cognitiva requerida para alcanzar el objetivo (identifica los niveles de Bloom necesarios)
2. Los prerrequisitos o conocimientos base que el estudiante debe tener
3. El contexto académico y profesional relevante para este objetivo
4. Consideraciones sobre la progresión de aprendizaje (desde habilidades básicas hacia complejas)

Responde de forma clara y estructurada, sin formato JSON."""
    
    # Construir prompt completa final: PROMPT BASE + DATOS AUTOMÁTICOS + [INSTRUCCIONES]
    # Construir prompt completa: solo datos automáticos + instrucciones
    # Asegurar que las instrucciones tengan el encabezado
    if not instrucciones.strip().startswith("### INSTRUCCIONES") and not instrucciones.strip().startswith("### [INSTRUCCIONES]"):
        instrucciones_con_encabezado = f"### INSTRUCCIONES:\n\n{instrucciones}"
    else:
        instrucciones_con_encabezado = instrucciones
    
    if prompt_base.strip():
        prompt_completa = f"""{prompt_base}

{datos_automaticos}

{instrucciones_con_encabezado}"""
    else:
        prompt_completa = f"""{datos_automaticos}

{instrucciones_con_encabezado}"""
    
    return {
        'completa': prompt_completa,
        'personalizado': prompt_personalizado,
        'datos_automaticos': datos_automaticos
    }

# Funciones para persistencia de prompts
def obtener_instrucciones_ejemplo(workflow_type, cantidad_agentes, estructura_mei, agente_num):
    """
    Obtiene las instrucciones de ejemplo para un agente específico.
    
    Args:
        workflow_type: "generar-indicadores-v2" o "revisar-indicadores-v2"
        cantidad_agentes: 1 o 2
        estructura_mei: "MEI-Actualizado" o "MEI-Antiguo"
        agente_num: 1 o 2
    
    Returns:
        str: Instrucciones de ejemplo para el agente
    """
    if workflow_type == "generar-indicadores-v2":
        if cantidad_agentes == 1:
            # Un solo agente: prompt completa
            if estructura_mei == "MEI-Actualizado":
                return """Genera 3 Indicadores de Desempeño (ID) que funcionen como peldaños para alcanzar el RA.

Para cada indicador, proporciona:
- El texto completo del indicador (verbo en tercera persona plural)
- El verbo principal (en infinitivo)
- El nivel de Bloom (1-6)
- Una justificación pedagógica breve"""
            else:  # MEI-Antiguo
                return """Genera 3 Indicadores de Logro (IL) que funcionen como peldaños para alcanzar el AE.

Para cada indicador, proporciona:
- El texto completo del indicador (verbo en tercera persona plural)
- El verbo principal (en infinitivo)
- El nivel de Bloom (1-6)
- Una justificación pedagógica breve"""
        else:  # cantidad_agentes == 2
            if agente_num == 1:
                # Agente 1: generación
                if estructura_mei == "MEI-Actualizado":
                    return """Genera 3 Indicadores de Desempeño (ID) que funcionen como peldaños para alcanzar el RA.

Para cada indicador, proporciona:
- El texto completo del indicador (verbo en tercera persona plural)
- El verbo principal (en infinitivo)
- El nivel de Bloom (1-6)
- Una justificación pedagógica breve"""
                else:  # MEI-Antiguo
                    return """Genera 3 Indicadores de Logro (IL) que funcionen como peldaños para alcanzar el AE.

Para cada indicador, proporciona:
- El texto completo del indicador (verbo en tercera persona plural)
- El verbo principal (en infinitivo)
- El nivel de Bloom (1-6)
- Una justificación pedagógica breve"""
            else:  # agente_num == 2
                # Agente 2: evaluación
                if estructura_mei == "MEI-Actualizado":
                    return """Evalúa los Indicadores de Desempeño (ID) generados por el Agente 1.

Para cada indicador, verifica:
- Observabilidad y medibilidad
- Alineación con el RA
- Progresión en complejidad cognitiva
- Ausencia de finalidad
- Estructura correcta

Proporciona recomendaciones de mejora si es necesario."""
                else:  # MEI-Antiguo
                    return """Evalúa los Indicadores de Logro (IL) generados por el Agente 1.

Para cada indicador, verifica:
- Observabilidad y medibilidad
- Alineación con el AE
- Progresión en complejidad cognitiva
- Ausencia de finalidad
- Estructura correcta

Proporciona recomendaciones de mejora si es necesario."""
    else:  # workflow_type == "revisar-indicadores-v2"
        if cantidad_agentes == 1:
            # Un solo agente: prompt completa
            if estructura_mei == "MEI-Actualizado":
                return """Revisa cada Indicador de Desempeño (ID) proporcionado y evalúa si cumple con los estándares de calidad.

Para cada indicador, proporciona:
- Deconstrucción estructural (verbo, producto/proceso, condición/contexto)
- Evaluación del verbo y su nivel de Bloom
- Observabilidad y medibilidad
- Alineación con el RA
- Presencia de finalidad (debe estar ausente)
- Progresión cognitiva
- Recomendaciones de mejora si es necesario"""
            else:  # MEI-Antiguo
                return """Revisa cada Indicador de Logro (IL) proporcionado y evalúa si cumple con los estándares de calidad.

Para cada indicador, proporciona:
- Deconstrucción estructural (habilidad, contenido, condición/contexto)
- Evaluación del verbo y su nivel de Bloom
- Observabilidad y medibilidad
- Alineación con el AE
- Presencia de finalidad (debe estar ausente)
- Progresión cognitiva
- Recomendaciones de mejora si es necesario"""
        else:  # cantidad_agentes == 2
            if agente_num == 1:
                # Agente 1: deconstrucción
                if estructura_mei == "MEI-Actualizado":
                    return """Descompón cada Indicador de Desempeño (ID) proporcionado en sus 3 componentes estructurales:
- Verbo observable (en tercera persona plural)
- Producto o Proceso
- Condición de Calidad o Contexto

Solo clasifica y extrae las piezas. No emitas juicios ni analices la calidad."""
                else:  # MEI-Antiguo
                    return """Descompón cada Indicador de Logro (IL) proporcionado en sus 3 componentes estructurales:
- Habilidad (verbo en tercera persona plural)
- Contenido
- Condición/Contexto

Solo clasifica y extrae las piezas. No emitas juicios ni analices la calidad."""
            else:  # agente_num == 2
                # Agente 2: evaluación
                if estructura_mei == "MEI-Actualizado":
                    return """Evalúa los Indicadores de Desempeño (ID) que fueron deconstruidos por el Agente 1.

Para cada indicador, verifica:
- Observabilidad y medibilidad
- Alineación con el RA
- Progresión en complejidad cognitiva
- Ausencia de finalidad
- Estructura correcta

Proporciona recomendaciones de mejora si es necesario."""
                else:  # MEI-Antiguo
                    return """Evalúa los Indicadores de Logro (IL) que fueron deconstruidos por el Agente 1.

Para cada indicador, verifica:
- Observabilidad y medibilidad
- Alineación con el AE
- Progresión en complejidad cognitiva
- Ausencia de finalidad
- Estructura correcta

Proporciona recomendaciones de mejora si es necesario."""
    return ""


def cargar_prompts_persistentes(workflow_type, cantidad_agentes, estructura_mei):
    """
    Carga los prompts persistentes para una combinación específica.
    
    Args:
        workflow_type: "generar-indicadores-v2" o "revisar-indicadores-v2"
        cantidad_agentes: 1 o 2
        estructura_mei: "MEI-Actualizado" o "MEI-Antiguo"
    
    Returns:
        dict: {"agente_1": str, "agente_2": str} con los prompts guardados (pueden estar vacíos)
    """
    key = f"prompts_{workflow_type}_{cantidad_agentes}_{estructura_mei}"
    if key in st.session_state:
        return st.session_state[key]
    return {"agente_1": "", "agente_2": ""}


def guardar_prompts_persistentes(workflow_type, cantidad_agentes, estructura_mei, agente_1, agente_2):
    """
    Guarda los prompts persistentes para una combinación específica.
    
    Args:
        workflow_type: "generar-indicadores-v2" o "revisar-indicadores-v2"
        cantidad_agentes: 1 o 2
        estructura_mei: "MEI-Actualizado" o "MEI-Antiguo"
        agente_1: str - Prompt del agente 1
        agente_2: str - Prompt del agente 2
    """
    key = f"prompts_{workflow_type}_{cantidad_agentes}_{estructura_mei}"
    st.session_state[key] = {
        "agente_1": agente_1,
        "agente_2": agente_2
    }


# Funciones para construir previews de prompts de Revisar Indicadores
def construir_preview_agente_1_revisar():
    """Construye una preview de la prompt completa del Agente 1 (Revisar Indicadores)"""
    estructura_mei = st.session_state.get('estructura_mei_selector', 'MEI-Actualizado')
    if not estructura_mei or estructura_mei not in ['MEI-Actualizado', 'MEI-Antiguo']:
        estructura_mei = 'MEI-Actualizado'
    
    cantidad_agentes = st.session_state.get('cantidad_agentes', 2)
    prompt_personalizado = st.session_state.get('agente_1', '').strip()
    
    # Datos automáticos (se inyectan SIEMPRE)
    nombre_curso = st.session_state.get('nombre_curso', '')
    trimestre = st.session_state.get('trimestre', '').strip()
    metodologia = st.session_state.get('metodologia', '').strip()
    
    if estructura_mei == 'MEI-Actualizado':
        rf_texto = st.session_state.rf_list[0] if st.session_state.get('rf_list') and len(st.session_state.rf_list) > 0 and st.session_state.rf_list[0] else "No disponible"
        ra_texto = st.session_state.ra_list[0] if st.session_state.get('ra_list') and len(st.session_state.ra_list) > 0 and st.session_state.ra_list[0] else "No disponible"
        datos_automaticos = f"""### DATOS DE ENTRADA:

- **Resultado Formativo (RF):**
  "{rf_texto}"
  
- **Resultado de Aprendizaje (RA):**
  "{ra_texto}"
  
- **Nombre del Curso:**
  "{nombre_curso or 'Nombre de curso no disponible'}" """
    else:  # MEI-Antiguo
        ra_texto = st.session_state.ra_list[0] if st.session_state.get('ra_list') and len(st.session_state.ra_list) > 0 and st.session_state.ra_list[0] else "No disponible"
        ae_texto = st.session_state.ae_list[0] if st.session_state.get('ae_list') and len(st.session_state.ae_list) > 0 and st.session_state.ae_list[0] else "No disponible"
        datos_automaticos = f"""### DATOS DE ENTRADA:

- **Resultado de Aprendizaje (RA):**
  "{ra_texto}"
  
- **Aprendizaje Esperado (AE):**
  "{ae_texto}"
  
- **Nombre del Curso:**
  "{nombre_curso or 'Nombre de curso no disponible'}" """
    
    # Agregar trimestre solo si existe
    if trimestre:
        datos_automaticos += f"\n\n- **Trimestre:**\n  {trimestre}"
    
    # Agregar metodología solo si existe
    if metodologia:
        datos_automaticos += f'\n\n- **Metodología Propuesta:**\n  "{metodologia}"'
    
    # Indicadores a revisar (placeholder)
    indicadores_placeholder = st.session_state.get('indicadores_list', [])
    if not indicadores_placeholder:
        indicadores_placeholder = ["[Los indicadores a revisar se incluirán aquí automáticamente]"]
    
    # Agregar indicadores a datos automáticos
    datos_automaticos += f"""

- **Indicadores a Revisar:**
{json.dumps(indicadores_placeholder[:3], indent=2, ensure_ascii=False) if len(indicadores_placeholder) <= 3 else json.dumps(indicadores_placeholder[:3] + ["..."], indent=2, ensure_ascii=False)}"""
    
    # PROMPT BASE: Vacío (solo se muestran los datos automáticos)
    prompt_base = ""
    
    # [INSTRUCCIONES]: La tarea que debe realizar el agente (aquí impacta la prompt personalizada)
    if prompt_personalizado:
        # Si hay prompt personalizada, agregar encabezado si no lo tiene
        if not prompt_personalizado.strip().startswith("### INSTRUCCIONES") and not prompt_personalizado.strip().startswith("### [INSTRUCCIONES]"):
            instrucciones = f"### INSTRUCCIONES:\n\n{prompt_personalizado}"
        else:
            instrucciones = prompt_personalizado
    else:
        # Si no hay prompt personalizada, usar instrucciones por defecto
        if cantidad_agentes == 1:
            # Si cantidad_agentes = 1, el prompt base debe ser COMPLETO (deconstrucción + evaluación)
            if estructura_mei == 'MEI-Actualizado':
                prompt_base = """Eres un experto en auditoría pedagógica y evaluación de indicadores, especializado en la Taxonomía de Bloom revisada y los estándares de Quality Matters.

Tu tarea es REVISAR Indicadores de Desempeño (ID) existentes y evaluar si cumplen con:
- **Observabilidad y medibilidad** (Quality Matters Standard 3.1)
- **Alineación con el Resultado de Aprendizaje (RA)** (Quality Matters Standard 2.1)
- **Progresión en complejidad cognitiva** (Taxonomía de Bloom)
- **Ausencia de finalidad** (describen evidencias, no propósitos)
- **Estructura correcta** (verbo observable + producto/proceso + condición/contexto)

### REGLAS CRÍTICAS DE REVISIÓN:

1. **Taxonomía de Bloom - Niveles Cognitivos:**
   - Nivel 1 (Reconocer): ANOTAR, CITAR, DEFINIR, DENOMINAR, DESCRIBIR, ENUMERAR, IDENTIFICAR, INDICAR, LISTAR, MARCAR, MENCIONAR, MOSTRAR, NOMBRAR, RECONOCER, RECORDAR, ROTULAR, SEÑALAR, UBICAR
   - Nivel 2 (Entender): ASOCIAR, CLASIFICAR, COMPARAR, DISTINGUIR, EJEMPLIFICAR, EXPLICAR, INTERPRETAR, ORGANIZAR, RELACIONAR, RESUMIR
   - Nivel 3 (Aplicar): APLICAR, CALCULAR, COMPUTAR, DEMOSTRAR, EJECUTAR, EMPLEAR, EXPERIMENTAR, HACER USO, IMPLEMENTAR, MANEJAR, MANIPULAR, MODELAR, OPERAR, REALIZAR, RESOLVER, SELECCIONAR, SIMULAR, SOLUCIONAR, USAR, UTILIZAR
   - Nivel 4 (Analizar): CONTRASTAR, DEDUCIR, DETERMINAR, DIFERENCIAR, DISCRIMINAR, ESTRUCTURAR, EXAMINAR, INSPECCIONAR, INTEGRAR
   - Nivel 5 (Evaluar): ARGUMENTAR, CATEGORIZAR, CHEQUEAR, COMPROBAR, CONCLUIR, CRITICAR, DECIDIR, DEFENDER, DETECTAR, DIAGNOSTICAR, ESCOGER, EVALUAR, FUNDAMENTAR, JERARQUIZAR, JUZGAR, JUSTIFICAR, MEDIR, MONITOREAR, PRIORIZAR, PROBAR, SINTETIZAR
   - Nivel 6 (Crear): CONCEBIR, CONFECCIONAR, CONSTRUIR, CREAR, DESARROLLAR, DISEÑAR, ELABORAR, FORMAR, FORMULAR, GENERAR, IDEAR, PLANIFICAR, PRODUCIR, PROGRAMAR, PROPONER, PROYECTAR, TRANSFORMAR

2. **Quality Matters - Criterios de Calidad:**
   - Verbos de acción específicos y medibles
   - Evidencia observable del aprendizaje
   - Criterios de evaluación claros
   - Alineación con el RA principal

3. **PROHIBICIÓN ABSOLUTA DE FINALIDAD:**
   El indicador describe LO QUE EL ESTUDIANTE HACE/DEMUESTRA, no para qué lo hace.
   Está **TERMINANTEMENTE PROHIBIDO** usar: "para", "con el fin de", "con el propósito de", "a fin de", "con la intención de" o cualquier sinónimo.

4. **Análisis Estructural:**
   Cada indicador debe tener:
   - Verbo observable (en tercera persona plural, ej. "COMPARAN", "ELABORAN")
   - Producto o Proceso (el objeto directo del verbo, el "qué" se mide)
   - Condición de Calidad o Contexto (el "cómo", "cuándo" o "dónde", puede ser null)

5. **Progresión Lógica:**
   Los indicadores deben formar una secuencia lógica que construya hacia el RA principal, desde habilidades básicas hacia habilidades complejas."""
            else:  # MEI-Antiguo
                prompt_base = """Eres un experto en auditoría pedagógica y evaluación de indicadores, especializado en la Taxonomía de Bloom revisada y los estándares de Quality Matters.

Tu tarea es REVISAR Indicadores de Logro (IL) existentes y evaluar si cumplen con:
- **Observabilidad y medibilidad** (Quality Matters Standard 3.1)
- **Alineación con el Aprendizaje Esperado (AE)** (Quality Matters Standard 2.1)
- **Progresión en complejidad cognitiva** (Taxonomía de Bloom)
- **Ausencia de finalidad** (describen evidencias, no propósitos)
- **Estructura correcta** (habilidad + contenido + condición/contexto)

### REGLAS CRÍTICAS DE REVISIÓN:

1. **Taxonomía de Bloom - Niveles Cognitivos:**
   - Nivel 1 (Reconocer): ANOTAR, CITAR, DEFINIR, DENOMINAR, DESCRIBIR, ENUMERAR, IDENTIFICAR, INDICAR, LISTAR, MARCAR, MENCIONAR, MOSTRAR, NOMBRAR, RECONOCER, RECORDAR, ROTULAR, SEÑALAR, UBICAR
   - Nivel 2 (Entender): ASOCIAR, CLASIFICAR, COMPARAR, DISTINGUIR, EJEMPLIFICAR, EXPLICAR, INTERPRETAR, ORGANIZAR, RELACIONAR, RESUMIR
   - Nivel 3 (Aplicar): APLICAR, CALCULAR, COMPUTAR, DEMOSTRAR, EJECUTAR, EMPLEAR, EXPERIMENTAR, HACER USO, IMPLEMENTAR, MANEJAR, MANIPULAR, MODELAR, OPERAR, REALIZAR, RESOLVER, SELECCIONAR, SIMULAR, SOLUCIONAR, USAR, UTILIZAR
   - Nivel 4 (Analizar): CONTRASTAR, DEDUCIR, DETERMINAR, DIFERENCIAR, DISCRIMINAR, ESTRUCTURAR, EXAMINAR, INSPECCIONAR, INTEGRAR
   - Nivel 5 (Evaluar): ARGUMENTAR, CATEGORIZAR, CHEQUEAR, COMPROBAR, CONCLUIR, CRITICAR, DECIDIR, DEFENDER, DETECTAR, DIAGNOSTICAR, ESCOGER, EVALUAR, FUNDAMENTAR, JERARQUIZAR, JUZGAR, JUSTIFICAR, MEDIR, MONITOREAR, PRIORIZAR, PROBAR, SINTETIZAR
   - Nivel 6 (Crear): CONCEBIR, CONFECCIONAR, CONSTRUIR, CREAR, DESARROLLAR, DISEÑAR, ELABORAR, FORMAR, FORMULAR, GENERAR, IDEAR, PLANIFICAR, PRODUCIR, PROGRAMAR, PROPONER, PROYECTAR, TRANSFORMAR

2. **Quality Matters - Criterios de Calidad:**
   - Verbos de acción específicos y medibles
   - Evidencia observable del aprendizaje
   - Criterios de evaluación claros
   - Alineación con el AE principal

3. **PROHIBICIÓN ABSOLUTA DE FINALIDAD:**
   El indicador describe LO QUE EL ESTUDIANTE HACE/DEMUESTRA, no para qué lo hace.
   Está **TERMINANTEMENTE PROHIBIDO** usar: "para", "con el fin de", "con el propósito de", "a fin de", "con la intención de" o cualquier sinónimo.

4. **Análisis Estructural:**
   Cada indicador debe tener:
   - Habilidad (verbo de acción en tercera persona plural, ej. "DIFERENCIAN", "ANALIZAN")
   - Contenido (el objeto directo del verbo, el "qué")
   - Condición/Contexto (el "cómo", "cuándo" o "dónde", puede ser null)

5. **Progresión Lógica:**
   Los indicadores deben formar una secuencia lógica que construya hacia el AE principal, desde habilidades básicas hacia habilidades complejas."""
            
            # Tarea completa para 1 agente (deconstrucción + evaluación)
            if estructura_mei == 'MEI-Actualizado':
                rf_texto = st.session_state.rf_list[0] if st.session_state.get('rf_list') and len(st.session_state.rf_list) > 0 and st.session_state.rf_list[0] else "No disponible"
                tarea_texto = f"""{datos_automaticos}

### CONTEXTO SUPERIOR (RF):
{rf_texto}

### INDICADORES A REVISAR:
{json.dumps(indicadores_placeholder[:3], indent=2, ensure_ascii=False) if len(indicadores_placeholder) <= 3 else json.dumps(indicadores_placeholder[:3] + ["..."], indent=2, ensure_ascii=False)}

### TU TAREA (MEI ACTUALIZADO):
Revisa CADA uno de los Indicadores de Desempeño (ID) proporcionados y evalúa si cumplen con los estándares de Quality Matters y la Taxonomía de Bloom.

Para cada indicador, proporciona:
1. **Deconstrucción estructural:** Extrae el verbo_detectado, producto_proceso_detectado y condicion_contexto_detectada
2. **Evaluación del verbo:** Identifica el verbo principal y su nivel de Bloom (1-6). Justifica por qué corresponde a ese nivel.
3. **Observabilidad y medibilidad:** Evalúa si el indicador es observable y medible según Quality Matters Standard 3.1.
4. **Alineación con el RA:** Evalúa si el indicador está directamente alineado con el RA principal (Quality Matters Standard 2.1).
5. **Presencia de finalidad:** Identifica si el indicador contiene frases de finalidad (ej. "para", "con el fin de", "con el propósito de"). Si las contiene, es un FALLO ESTRUCTURAL.
6. **Progresión cognitiva:** Evalúa si el indicador forma parte de una progresión lógica desde habilidades básicas hacia complejas.
7. **Recomendaciones:** Si el indicador tiene problemas, proporciona recomendaciones específicas de mejora.

**PROHIBICIÓN ABSOLUTA:** El indicador NO debe contener finalidad. Está terminantemente prohibido usar: "para", "con el fin de", "con el propósito de", "a fin de", "con la intención de" o sinónimos.

Responde de forma clara y estructurada, describiendo cada indicador con precisión. NO uses formato JSON, solo texto descriptivo."""
                instrucciones = tarea_texto
            else:  # MEI-Antiguo
                ra_texto = st.session_state.ra_list[0] if st.session_state.get('ra_list') and len(st.session_state.ra_list) > 0 and st.session_state.ra_list[0] else "No disponible"
                tarea_texto = f"""{datos_automaticos}

### CONTEXTO SUPERIOR (RA):
{ra_texto}

### INDICADORES A REVISAR:
{json.dumps(indicadores_placeholder[:3], indent=2, ensure_ascii=False) if len(indicadores_placeholder) <= 3 else json.dumps(indicadores_placeholder[:3] + ["..."], indent=2, ensure_ascii=False)}

### TU TAREA (MEI ANTIGUO):
Revisa CADA uno de los Indicadores de Logro (IL) proporcionados y evalúa si cumplen con los estándares de Quality Matters y la Taxonomía de Bloom.

Para cada indicador, proporciona:
1. **Deconstrucción estructural:** Extrae el verbo_detectado (habilidad), producto_proceso_detectado (contenido) y condicion_contexto_detectada
2. **Evaluación del verbo:** Identifica el verbo principal y su nivel de Bloom (1-6). Justifica por qué corresponde a ese nivel.
3. **Observabilidad y medibilidad:** Evalúa si el indicador es observable y medible según Quality Matters Standard 3.1.
4. **Alineación con el AE:** Evalúa si el indicador está directamente alineado con el AE principal (Quality Matters Standard 2.1).
5. **Presencia de finalidad:** Identifica si el indicador contiene frases de finalidad (ej. "para", "con el fin de", "con el propósito de"). Si las contiene, es un FALLO ESTRUCTURAL.
6. **Progresión cognitiva:** Evalúa si el indicador forma parte de una progresión lógica desde habilidades básicas hacia complejas.
7. **Recomendaciones:** Si el indicador tiene problemas, proporciona recomendaciones específicas de mejora.

**PROHIBICIÓN ABSOLUTA:** El indicador NO debe contener finalidad. Está terminantemente prohibido usar: "para", "con el fin de", "con el propósito de", "a fin de", "con la intención de" o sinónimos.

Responde de forma clara y estructurada, describiendo cada indicador con precisión. NO uses formato JSON, solo texto descriptivo."""
                instrucciones = tarea_texto
        else:  # cantidad_agentes == 2
            # cantidad_agentes = 2, prompt base para deconstrucción solamente
            if estructura_mei == 'MEI-Actualizado':
                prompt_base = """Eres un "Analista Estructural de Indicadores" de UNAB. Tu única tarea es "desarmar" (deconstruir) una lista de indicadores en sus 3 componentes estructurales.
NO debes emitir juicios, NO debes analizar la calidad, NO debes corregir. Solo debes CLASIFICAR y EXTRAER las piezas."""
            else:  # MEI-Antiguo
                prompt_base = """Eres un "Analista Estructural de Indicadores" de UNAB. Tu única tarea es "desarmar" (deconstruir) una lista de indicadores en sus 3 componentes estructurales.
NO debes emitir juicios, NO debes analizar la calidad, NO debes corregir. Solo debes CLASIFICAR y EXTRAER las piezas."""
        
        # Tarea para deconstrucción solamente
        if estructura_mei == 'MEI-Actualizado':
            formato_clave = "Formato MEI-Actualizado: \"Verbo observable\" (3ra p. plural) + \"Producto o Proceso\" + \"Condición de Calidad o Contexto\"."
            ejemplo_salida = """[
  {
    "indicador_original": "COMPARAN el desempeño, habilidades y necesidades de aprendizaje de los estudiantes de educación básica utilizando registros de aula y resultados de evaluaciones.",
    "verbo_detectado": "COMPARAN",
    "producto_proceso_detectado": "el desempeño, habilidades y necesidades de aprendizaje de los estudiantes de educación básica",
    "condicion_contexto_detectada": "utilizando registros de aula y resultados de evaluaciones"
  }
]"""
            tarea_texto = f"""{datos_automaticos}

### ESTRUCTURA ESPERADA
{formato_clave}

### INDICADORES A DECONSTRUIR:
{json.dumps(indicadores_placeholder[:3], indent=2, ensure_ascii=False) if len(indicadores_placeholder) <= 3 else json.dumps(indicadores_placeholder[:3] + ["..."], indent=2, ensure_ascii=False)}

### REGLAS DE DECONSTRUCCIÓN (MEI ACTUALIZADO):
1. **"verbo_detectado":** Extrae el primer verbo conjugado (ej. "ANALIZAN").
2. **"producto_proceso_detectado":** Extrae el objeto directo del verbo (el "qué" se mide).
3. **"condicion_contexto_detectada":** Extrae el resto de la frase (el "cómo", "cuándo" o "dónde"). Si no existe, usa null.

### EJEMPLO DE SALIDA (JSON Array):
{ejemplo_salida}

### TU TAREA:
Analiza CADA indicador de la lista "INDICADORES A DECONSTRUIR".
Devuelve ÚNICAMENTE un array JSON con los objetos deconstruidos, siguiendo las reglas y el ejemplo.
El array de salida debe tener EXACTAMENTE el mismo número de objetos que el array de entrada."""
        else:  # MEI-Antiguo
            formato_clave = "Formato MEI-Antiguo: \"Habilidad\" (verbo plural), \"Contenido\" (qué), \"Condicion_Contexto\" (cómo/cuándo)."
            ejemplo_salida = """[
  {
    "indicador_original": "DIFERENCIAN las teorías del comercio internacional, aplicando un marco comparativo.",
    "verbo_detectado": "DIFERENCIAN",
    "producto_proceso_detectado": "las teorías del comercio internacional",
    "condicion_contexto_detectada": "aplicando un marco comparativo"
  }
]"""
            tarea_texto = f"""{datos_automaticos}

### ESTRUCTURA ESPERADA
{formato_clave}

### INDICADORES A DECONSTRUIR:
{json.dumps(indicadores_placeholder[:3], indent=2, ensure_ascii=False) if len(indicadores_placeholder) <= 3 else json.dumps(indicadores_placeholder[:3] + ["..."], indent=2, ensure_ascii=False)}

### REGLAS DE DECONSTRUCCIÓN (MEI ANTIGUO):
1. **"verbo_detectado":** Extrae el primer verbo conjugado (ej. "ANALIZAN").
2. **"producto_proceso_detectado":** Extrae el objeto directo del verbo (el "qué").
3. **"condicion_contexto_detectada":** Extrae el resto de la frase (el "cómo", "cuándo" o "dónde"). Si no existe, usa null.

### EJEMPLO DE SALIDA (JSON Array):
{ejemplo_salida}

### TU TAREA:
Analiza CADA indicador de la lista "INDICADORES A DECONSTRUIR".
Devuelve ÚNICAMENTE un array JSON con los objetos deconstruidos, siguiendo las reglas y el ejemplo.
El array de salida debe tener EXACTAMENTE el mismo número de objetos que el array de entrada."""
    
    # [INSTRUCCIONES]: La tarea que debe realizar el agente (aquí impacta la prompt personalizada)
    if prompt_personalizado:
        # Si hay prompt personalizada, agregar encabezado si no lo tiene
        if not prompt_personalizado.strip().startswith("### INSTRUCCIONES") and not prompt_personalizado.strip().startswith("### [INSTRUCCIONES]"):
            instrucciones = f"### INSTRUCCIONES:\n\n{prompt_personalizado}"
        else:
            instrucciones = prompt_personalizado
    else:
        # Si no hay prompt personalizada, usar instrucciones por defecto (ya están en tarea_texto)
        instrucciones = tarea_texto.replace(datos_automaticos, "").strip()
        # Extraer solo la parte de instrucciones de tarea_texto
        if "### ESTRUCTURA ESPERADA" in tarea_texto or "### CONTEXTO SUPERIOR" in tarea_texto or "### INDICADORES" in tarea_texto:
            # Extraer desde la primera sección relevante
            if "### ESTRUCTURA ESPERADA" in tarea_texto:
                instrucciones = "### [INSTRUCCIONES]\n\n" + tarea_texto.split("### ESTRUCTURA ESPERADA")[1].strip()
            elif "### CONTEXTO SUPERIOR" in tarea_texto:
                instrucciones = "### [INSTRUCCIONES]\n\n" + tarea_texto.split("### CONTEXTO SUPERIOR")[1].strip()
            elif "### INDICADORES" in tarea_texto:
                instrucciones = "### [INSTRUCCIONES]\n\n" + tarea_texto.split("### INDICADORES")[1].strip()
        else:
            instrucciones = f"### [INSTRUCCIONES]\n\n{tarea_texto.replace(datos_automaticos, '').strip()}"
    
    # PROMPT BASE: Vacío (solo se muestran los datos automáticos)
    prompt_base_nuevo = ""
    
    # Agregar indicadores a datos automáticos
    datos_automaticos += f"""

- **Indicadores a Revisar:**
{json.dumps(indicadores_placeholder[:3], indent=2, ensure_ascii=False) if len(indicadores_placeholder) <= 3 else json.dumps(indicadores_placeholder[:3] + ["..."], indent=2, ensure_ascii=False)}"""
    
    # Construir prompt completa final: DATOS AUTOMÁTICOS + [INSTRUCCIONES]
    # Asegurar que las instrucciones tengan el encabezado
    if not instrucciones.strip().startswith("### INSTRUCCIONES") and not instrucciones.strip().startswith("### [INSTRUCCIONES]"):
        instrucciones_con_encabezado = f"### INSTRUCCIONES:\n\n{instrucciones}"
    else:
        instrucciones_con_encabezado = instrucciones
    
    if prompt_base_nuevo.strip():
        prompt_completa = f"""{prompt_base_nuevo}

{datos_automaticos}

{instrucciones_con_encabezado}"""
    else:
        prompt_completa = f"""{datos_automaticos}

{instrucciones_con_encabezado}"""
    
    return {
        'completa': prompt_completa,
        'personalizado': prompt_personalizado,
        'datos_automaticos': datos_automaticos
    }

def construir_preview_agente_2_revisar():
    """Construye una preview de la prompt completa del Agente 2 (Revisar Indicadores)"""
    estructura_mei = st.session_state.get('estructura_mei_selector', 'MEI-Actualizado')
    if not estructura_mei or estructura_mei not in ['MEI-Actualizado', 'MEI-Antiguo']:
        estructura_mei = 'MEI-Actualizado'
    
    prompt_personalizado = st.session_state.get('agente_2', '').strip()
    
    # PROMPT BASE: Vacío (solo se muestran los datos automáticos)
    prompt_base = ""
    
    # DATOS AUTOMÁTICOS: Los datos reales que se inyectan
    nombre_curso = st.session_state.get('nombre_curso', '')
    trimestre = st.session_state.get('trimestre', '').strip()
    metodologia = st.session_state.get('metodologia', '').strip()
    
    if estructura_mei == 'MEI-Actualizado':
        rf_texto = st.session_state.rf_list[0] if st.session_state.get('rf_list') and len(st.session_state.rf_list) > 0 and st.session_state.rf_list[0] else "No disponible"
        ra_texto = st.session_state.ra_list[0] if st.session_state.get('ra_list') and len(st.session_state.ra_list) > 0 and st.session_state.ra_list[0] else "No disponible"
        datos_automaticos = f"""### DATOS DE ENTRADA:

- **Resultado Formativo (RF):**
  "{rf_texto}"
  
- **Resultado de Aprendizaje (RA):**
  "{ra_texto}"
  
- **Nombre del Curso:**
  "{nombre_curso or 'Nombre de curso no disponible'}"
  
- **NIVEL DEL RA ESPERADO:** [Se determinará automáticamente]"""
    else:  # MEI-Antiguo
        ra_texto = st.session_state.ra_list[0] if st.session_state.get('ra_list') and len(st.session_state.ra_list) > 0 and st.session_state.ra_list[0] else "No disponible"
        ae_texto = st.session_state.ae_list[0] if st.session_state.get('ae_list') and len(st.session_state.ae_list) > 0 and st.session_state.ae_list[0] else "No disponible"
        datos_automaticos = f"""### DATOS DE ENTRADA:

- **Resultado de Aprendizaje (RA):**
  "{ra_texto}"
  
- **Aprendizaje Esperado (AE):**
  "{ae_texto}"
  
- **Nombre del Curso:**
  "{nombre_curso or 'Nombre de curso no disponible'}"
  
- **NIVEL DEL AE ESPERADO:** [Se determinará automáticamente]"""
    
    if trimestre:
        datos_automaticos += f"\n\n- **Trimestre:**\n  {trimestre}"
    if metodologia:
        datos_automaticos += f'\n\n- **Metodología Propuesta:**\n  "{metodologia}"'
    
    # Indicadores a revisar (placeholder)
    indicadores_placeholder = st.session_state.get('indicadores_list', [])
    if not indicadores_placeholder:
        indicadores_placeholder = ["[Los indicadores a revisar se incluirán aquí automáticamente]"]
    
    datos_automaticos += f"""

- **Indicadores a Revisar:**
{json.dumps(indicadores_placeholder[:3], indent=2, ensure_ascii=False) if len(indicadores_placeholder) <= 3 else json.dumps(indicadores_placeholder[:3] + ["..."], indent=2, ensure_ascii=False)}"""
    
    # [RESPUESTA DEL AGENTE 1]: Placeholder para la respuesta del agente anterior
    respuesta_agente_1 = """### [RESPUESTA DEL AGENTE 1]

[La respuesta del Agente 1 (análisis estructural de los indicadores) se incluirá aquí automáticamente durante la ejecución]"""
    
    # [INSTRUCCIONES]: La tarea que debe realizar el agente (aquí impacta la prompt personalizada)
    if prompt_personalizado:
        # Si hay prompt personalizada, agregar encabezado si no lo tiene
        if not prompt_personalizado.strip().startswith("### INSTRUCCIONES") and not prompt_personalizado.strip().startswith("### [INSTRUCCIONES]"):
            instrucciones = f"### INSTRUCCIONES:\n\n{prompt_personalizado}"
        else:
            instrucciones = prompt_personalizado
    else:
        # Si no hay prompt personalizada, usar instrucciones por defecto
        if estructura_mei == 'MEI-Actualizado':
            instrucciones = """### [INSTRUCCIONES]

Eres un "Auditor de Calidad Pedagógica" de UNAB, experto en el estándar 2.2 de Quality Matters.

Tu tarea es auditar un set de indicadores basándote en un análisis estructural y taxonómico pre-procesado.

### PRINCIPIOS DE REVISIÓN (TU LÓGICA DE AUDITORÍA INTERNA)

1. **Análisis de Finalidad:** El RA describe el *propósito*. El Indicador describe la *EVIDENCIA*. Si un indicador contiene frases de finalidad (ej. "para", "con el fin de", "con el propósito de"), es un FALLO ESTRUCTURAL.

2. **Análisis de Observabilidad:** Los indicadores deben ser "medibles" y "observables". Verbos abstractos (ej. 'REFLEXIONAR', 'PENSAR', 'COMPRENDER', 'SABER', 'CONOCER') o Nivel 0 son procesos internos y NO son observables. Un verbo abstracto solo se vuelve medible si el contexto lo "ancla" a un producto tangible (ej. "REFLEXIONAR... *mediante un ensayo escrito*"). Si no está anclado, es un FALLO DE OBSERVABILIDAD.

3. **Análisis de Progresividad:** El alineamiento es pedagógico. Un indicador de nivel bajo (ej. Nivel 2 'COMPARAR') SÍ tiene **ALINEAMIENTO ALTO** si es un "peldaño" lógico y coherente ("smaller, discrete pieces") para un RA de nivel alto (ej. Nivel 6 'DISEÑAR'). El alineamiento es BAJO solo si el indicador falla el Análisis 1 o 2, o si es pedagógicamente irrelevante.

### TU PROCESO DE ANÁLISIS (Chain-of-Thought Interno)
Para CADA indicador, debes pensar en 3 pasos antes de escribir tu reporte:
1. **Paso 1 (Finalidad):** ¿El "indicador_original" contiene una frase de finalidad?
2. **Paso 2 (Observabilidad):** Revisa 'verbo_detectado', 'verbo_infinitivo' y 'nivel_verbo_detectado'.
   * ¿Es el 'nivel_verbo_detectado' 0? Si es 0, ¿POR QUÉ? ¿Es el 'verbo_detectado' un verbo abstracto (como 'REFLEXIONAR'), o no es un verbo (como 'asd'), o es un verbo no listado?
   * Si es abstracto (Nivel 0 o verbos como 'COMPRENDER'), ¿el 'condicion_contexto_detectada' lo "ancla" a un producto tangible? Si no lo ancla, es un fallo.
3. **Paso 3 (Progresividad):** Asumiendo que P1 y P2 pasan, ¿es el "nivel_verbo_detectado" (ej. Nivel 2) un "peldaño" lógico para el "NIVEL DEL RA ESPERADO"?

### FORMATO DE REPORTE DE SALIDA (4 Claves, LENGUAJE DE USUARIO)
Basado en tu análisis de 3 pasos, genera el reporte final.

1. **Clave "verbo_observable":**
   * **Si Pasa:** "'...' (Nivel X) es un verbo observable y medible."
   * **Si Falla (Paso 2):** "FALLA: [Analiza el 'verbo_detectado' y explica POR QUÉ no es válido. Usa una de estas lógicas]:
       * *Si es un verbo abstracto:* "El verbo '...' (ej. 'REFLEXIONAR', 'CONOCER') es un proceso mental interno y no es directamente observable ni medible. Debe ser anclado a un producto tangible (ej. '...mediante un informe escrito')."
       * *Si no es un verbo o es ilegible:* "La palabra '...' no es un verbo de acción observable válido o no se pudo reconocer."
       * *Si es un verbo de actividad (no resultado):* "El verbo '...' (ej. 'INVESTIGAR', 'INDAGAR') describe una actividad, no un resultado de aprendizaje medible."
       * *Si es un verbo Nivel 0 (no listado):* "El verbo '...' no se encuentra en la taxonomía oficial de verbos observables."

2. **Clave "producto_o_proceso":**
   * **Si Falla (Paso 2):** "Incompleto. El verbo '...' (ej. 'REFLEXIONAR') no genera un producto o evidencia medible por sí mismo."
   * **Si Pasa:** "Sí, '...' es un producto/proceso claro y específico."

3. **Clave "condicion_de_calidad_o_contexto":**
   * **Si Falla (Paso 1):** "FALLA ESTRUCTURAL: El indicador incluye una frase de finalidad ('...'). El indicador solo debe describir la evidencia (el qué/cómo), no el propósito, que ya está en el RA/AE."
   * **Si es 'null':** "Ausente. El indicador está estructuralmente incompleto, falta una condición o contexto."
   * **Si Pasa:** "Presente. '...' es un contexto o condición clara."

4. **Clave "alineamiento":**
   * **Si Falla (Paso 1 o 2):** "BAJO. El indicador no es válido. [Explica la razón del fallo, ej: 'No es medible porque usa un verbo abstracto ('REFLEXIONAR') sin un producto tangible.' o 'Incluye una frase de finalidad que lo invalida.' o 'La palabra ('...') no es un verbo observable.']"
   * **Si Pasa (Paso 3) pero está incompleto:** "MEDIO. El verbo (Nivel X) es un peldaño coherente, pero la estructura es incompleta (falta contexto), lo que dificulta su medición."
   * **Si Pasa (Paso 3) y está completo:** "ALTO. Es un 'peldaño' pedagógico (Nivel X) coherente y necesario para construir el RA/AE (Nivel [NIVEL_RA])."

### FORMATO DE SALIDA OBLIGATORIO:
Devuelve ÚNICAMENTE un array JSON con los reportes. Cada objeto debe tener EXACTAMENTE estas 4 claves.

### TU TAREA:
Genera el array JSON de reportes (un reporte por cada indicador en los datos pre-procesados)."""
        else:  # MEI-Antiguo
            instrucciones = """### [INSTRUCCIONES]

Eres un "Auditor de Calidad Pedagógica" de UNAB, experto en el estándar 2.2 de Quality Matters.

Tu tarea es auditar un set de indicadores basándote en un análisis estructural y taxonómico pre-procesado.

### PRINCIPIOS DE REVISIÓN (TU LÓGICA DE AUDITORÍA INTERNA)

1. **Análisis de Finalidad:** El AE describe el *propósito*. El IL describe la *EVIDENCIA*. Si un indicador contiene frases de finalidad (ej. "para", "con el fin de", "con el propósito de"), es un FALLO ESTRUCTURAL.

2. **Análisis de Observabilidad:** Los indicadores deben ser "medibles" y "observables". Verbos abstractos (ej. 'REFLEXIONAR', 'PENSAR', 'COMPRENDER', 'SABER', 'CONOCER') o Nivel 0 son procesos internos y NO son observables. Un verbo abstracto solo se vuelve medible si el contexto lo "ancla" a un producto tangible (ej. "REFLEXIONAR... *mediante un ensayo escrito*"). Si no está anclado, es un FALLO DE OBSERVABILIDAD.

3. **Análisis de Progresividad:** El alineamiento es pedagógico. Un indicador de nivel bajo (ej. Nivel 2 'COMPARAR') SÍ tiene **ALINEAMIENTO ALTO** si es un "peldaño" lógico y coherente ("smaller, discrete pieces") para un AE de nivel alto (ej. Nivel 6 'DISEÑAR'). El alineamiento es BAJO solo si el indicador falla el Análisis 1 o 2, o si es pedagógicamente irrelevante.

### TU PROCESO DE ANÁLISIS (Chain-of-Thought Interno)
Para CADA indicador, debes pensar en 3 pasos antes de escribir tu reporte:
1. **Paso 1 (Finalidad):** ¿El "indicador_original" contiene una frase de finalidad?
2. **Paso 2 (Observabilidad):** Revisa 'verbo_detectado', 'verbo_infinitivo' y 'nivel_verbo_detectado'.
   * ¿Es el 'nivel_verbo_detectado' 0? Si es 0, ¿POR QUÉ? ¿Es el 'verbo_detectado' un verbo abstracto (como 'REFLEXIONAR'), o no es un verbo (como 'asd'), o es un verbo no listado?
   * Si es abstracto (Nivel 0 o verbos como 'COMPRENDER'), ¿el 'condicion_contexto_detectada' lo "ancla" a un producto tangible? Si no lo ancla, es un fallo.
3. **Paso 3 (Progresividad):** Asumiendo que P1 y P2 pasan, ¿es el "nivel_verbo_detectado" (ej. Nivel 2) un "peldaño" lógico para el "NIVEL DEL AE ESPERADO"?

### FORMATO DE REPORTE DE SALIDA (4 Claves, LENGUAJE DE USUARIO)
Basado en tu análisis de 3 pasos, genera el reporte final.

1. **Clave "verbo_observable":**
   * **Si Pasa:** "'...' (Nivel X) es un verbo observable y medible."
   * **Si Falla (Paso 2):** "FALLA: [Analiza el 'verbo_detectado' y explica POR QUÉ no es válido. Usa una de estas lógicas]:
       * *Si es un verbo abstracto:* "El verbo '...' (ej. 'REFLEXIONAR', 'CONOCER') es un proceso mental interno y no es directamente observable ni medible. Debe ser anclado a un producto tangible (ej. '...mediante un informe escrito')."
       * *Si no es un verbo o es ilegible:* "La palabra '...' no es un verbo de acción observable válido o no se pudo reconocer."
       * *Si es un verbo de actividad (no resultado):* "El verbo '...' (ej. 'INVESTIGAR', 'INDAGAR') describe una actividad, no un resultado de aprendizaje medible."
       * *Si es un verbo Nivel 0 (no listado):* "El verbo '...' no se encuentra en la taxonomía oficial de verbos observables."

2. **Clave "producto_o_proceso":**
   * **Si Falla (Paso 2):** "Incompleto. El verbo '...' (ej. 'REFLEXIONAR') no genera un producto o evidencia medible por sí mismo."
   * **Si Pasa:** "Sí, '...' es un producto/proceso claro y específico."

3. **Clave "condicion_de_calidad_o_contexto":**
   * **Si Falla (Paso 1):** "FALLA ESTRUCTURAL: El indicador incluye una frase de finalidad ('...'). El indicador solo debe describir la evidencia (el qué/cómo), no el propósito, que ya está en el RA/AE."
   * **Si es 'null':** "Ausente. El indicador está estructuralmente incompleto, falta una condición o contexto."
   * **Si Pasa:** "Presente. '...' es un contexto o condición clara."

4. **Clave "alineamiento":**
   * **Si Falla (Paso 1 o 2):** "BAJO. El indicador no es válido. [Explica la razón del fallo, ej: 'No es medible porque usa un verbo abstracto ('REFLEXIONAR') sin un producto tangible.' o 'Incluye una frase de finalidad que lo invalida.' o 'La palabra ('...') no es un verbo observable.']"
   * **Si Pasa (Paso 3) pero está incompleto:** "MEDIO. El verbo (Nivel X) es un peldaño coherente, pero la estructura es incompleta (falta contexto), lo que dificulta su medición."
   * **Si Pasa (Paso 3) y está completo:** "ALTO. Es un 'peldaño' pedagógico (Nivel X) coherente y necesario para construir el AE (Nivel [NIVEL_AE])."

### FORMATO DE SALIDA OBLIGATORIO:
Devuelve ÚNICAMENTE un array JSON con los reportes. Cada objeto debe tener EXACTAMENTE estas 4 claves.

### TU TAREA:
Genera el array JSON de reportes (un reporte por cada indicador en los datos pre-procesados)."""
    
    # Construir prompt completa final: PROMPT BASE + DATOS AUTOMÁTICOS + [RESPUESTA DEL AGENTE 1] + [INSTRUCCIONES]
    # Asegurar que las instrucciones tengan el encabezado
    if not instrucciones.strip().startswith("### INSTRUCCIONES") and not instrucciones.strip().startswith("### [INSTRUCCIONES]"):
        instrucciones_con_encabezado = f"### INSTRUCCIONES:\n\n{instrucciones}"
    else:
        instrucciones_con_encabezado = instrucciones
    
    prompt_completa = f"""{prompt_base}

{datos_automaticos}

{respuesta_agente_1}

{instrucciones_con_encabezado}"""
    
    return {
        'completa': prompt_completa,
        'personalizado': prompt_personalizado,
        'datos_automaticos': datos_automaticos
    }

def construir_preview_agente_3_revisar():
    """Construye una preview de la prompt completa del Agente 3 (Revisar Indicadores)"""
    estructura_mei = st.session_state.get('estructura_mei_selector', 'MEI-Actualizado')
    if not estructura_mei or estructura_mei not in ['MEI-Actualizado', 'MEI-Antiguo']:
        estructura_mei = 'MEI-Actualizado'
    
    prompt_personalizado = st.session_state.get('agente_3', '')
    
    # Prompt base según MEI
    if estructura_mei == 'MEI-Actualizado':
        prompt_base = """Eres un experto en auditoría de calidad pedagógica, especializado en el estándar 2.2 de Quality Matters y la Taxonomía de Bloom.

Tu tarea es auditar Indicadores de Desempeño (ID) basándote en un análisis estructural y taxonómico pre-procesado.

### PRINCIPIOS FUNDAMENTALES:

1. **Análisis de Finalidad:** El RA describe el *propósito*. El ID describe la *EVIDENCIA*. Si un indicador contiene frases de finalidad (ej. "para", "con el fin de"), es un FALLO ESTRUCTURAL.

2. **Análisis de Observabilidad:** Los indicadores deben ser "medibles" y "observables". Verbos abstractos (ej. 'REFLEXIONAR', 'PENSAR', 'COMPRENDER') o Nivel 0 son procesos internos y NO son observables. Un verbo abstracto solo se vuelve medible si el contexto lo "ancla" a un producto tangible.

3. **Análisis de Progresividad:** El alineamiento es pedagógico. Un indicador de nivel bajo (ej. Nivel 2 'COMPARAR') SÍ tiene **ALINEAMIENTO ALTO** si es un "peldaño" lógico y coherente para un RA de nivel alto (ej. Nivel 6 'DISEÑAR'). El alineamiento es BAJO solo si el indicador falla el Análisis 1 o 2, o si es pedagógicamente irrelevante.

Tu reporte final debe ser preciso, pedagógicamente sólido y estar escrito en un lenguaje claro y directo para docentes, evitando jerga técnica interna."""
    else:
        prompt_base = """Eres un experto en auditoría de calidad pedagógica, especializado en el estándar 2.2 de Quality Matters y la Taxonomía de Bloom.

Tu tarea es auditar Indicadores de Logro (IL) basándote en un análisis estructural y taxonómico pre-procesado.

### PRINCIPIOS FUNDAMENTALES:

1. **Análisis de Finalidad:** El AE describe el *propósito*. El IL describe la *EVIDENCIA*. Si un indicador contiene frases de finalidad (ej. "para", "con el fin de"), es un FALLO ESTRUCTURAL.

2. **Análisis de Observabilidad:** Los indicadores deben ser "medibles" y "observables". Verbos abstractos (ej. 'REFLEXIONAR', 'PENSAR', 'COMPRENDER') o Nivel 0 son procesos internos y NO son observables. Un verbo abstracto solo se vuelve medible si el contexto lo "ancla" a un producto tangible.

3. **Análisis de Progresividad:** El alineamiento es pedagógico. Un indicador de nivel bajo (ej. Nivel 2 'COMPARAR') SÍ tiene **ALINEAMIENTO ALTO** si es un "peldaño" lógico y coherente para un AE de nivel alto (ej. Nivel 6 'DISEÑAR'). El alineamiento es BAJO solo si el indicador falla el Análisis 1 o 2, o si es pedagógicamente irrelevante.

Tu reporte final debe ser preciso, pedagógicamente sólido y estar escrito en un lenguaje claro y directo para docentes, evitando jerga técnica interna."""
    
    # Datos automáticos
    nombre_curso = st.session_state.get('nombre_curso', '')
    trimestre = st.session_state.get('trimestre', '')
    metodologia = st.session_state.get('metodologia', '')
    
    if estructura_mei == 'MEI-Actualizado':
        rf_texto = st.session_state.rf_list[0] if st.session_state.get('rf_list') and len(st.session_state.rf_list) > 0 and st.session_state.rf_list[0] else "No disponible"
        ra_texto = st.session_state.ra_list[0] if st.session_state.get('ra_list') and len(st.session_state.ra_list) > 0 and st.session_state.ra_list[0] else "No disponible"
        datos_automaticos = f"""### CONTEXTO PEDAGÓGICO DE LA REVISIÓN

- **Resultado Formativo (RF) Superior:**
  {rf_texto}

- **Resultado de Aprendizaje (RA) a Lograr:**
  "{ra_texto}"

- **NIVEL DEL RA ESPERADO:** [Se determinará automáticamente]

- **Nombre del Curso:**
  "{nombre_curso or 'Nombre de curso no disponible'}" """
    else:
        ra_texto = st.session_state.ra_list[0] if st.session_state.get('ra_list') and len(st.session_state.ra_list) > 0 and st.session_state.ra_list[0] else "No disponible"
        ae_texto = st.session_state.ae_list[0] if st.session_state.get('ae_list') and len(st.session_state.ae_list) > 0 and st.session_state.ae_list[0] else "No disponible"
        datos_automaticos = f"""### CONTEXTO PEDAGÓGICO DE LA REVISIÓN

- **Resultado de Aprendizaje (RA) Superior:**
  {ra_texto}

- **Aprendizaje Esperado (AE) a Lograr:**
  "{ae_texto}"

- **NIVEL DEL AE ESPERADO:** [Se determinará automáticamente]

- **Nombre del Curso:**
  "{nombre_curso or 'Nombre de curso no disponible'}" """
    
    if trimestre and str(trimestre).strip():
        datos_automaticos += f"\n\n- **Trimestre:**\n  {trimestre}"
    if metodologia and str(metodologia).strip():
        datos_automaticos += f'\n\n- **Metodología Propuesta:**\n  "{metodologia}"'
    
    # Placeholder para análisis de Agentes 1 y 2
    analisis_agentes_placeholder = "[Los análisis de los Agentes 1 y 2 se incluirán aquí automáticamente durante la ejecución]"
    
    datos_automaticos += f"""

### DATOS PRE-PROCESADOS (Input de Agentes 1 y 2):
{analisis_agentes_placeholder}

### TU PROCESO DE ANÁLISIS (Chain-of-Thought Interno)
Para CADA indicador, debes pensar en 3 pasos antes de escribir tu reporte:
1. **Paso 1 (Finalidad):** ¿El "indicador_original" contiene una frase de finalidad?
2. **Paso 2 (Observabilidad):** Revisa 'verbo_detectado', 'verbo_infinitivo' y 'nivel_verbo_detectado'.
3. **Paso 3 (Progresividad):** ¿Es el "nivel_verbo_detectado" un "peldaño" lógico para el objetivo?

### FORMATO DE REPORTE DE SALIDA (4 Claves, LENGUAJE DE USUARIO)
Basado en tu análisis de 3 pasos, genera el reporte final.

1. **Clave "verbo_observable":** Análisis del verbo y su observabilidad
2. **Clave "producto_o_proceso":** Análisis del producto o proceso
3. **Clave "condicion_de_calidad_o_contexto":** Análisis de la condición o contexto
4. **Clave "alineamiento":** Nivel de alineamiento (ALTO, MEDIO, BAJO)

### FORMATO DE SALIDA OBLIGATORIO:
Devuelve ÚNICAMENTE un array JSON con los reportes. Cada objeto debe tener EXACTAMENTE estas 4 claves.

### TU TAREA:
Genera el array JSON de reportes (un reporte por cada indicador en los datos pre-procesados)."""
    
    # Construir prompt completa
    if prompt_personalizado and prompt_personalizado.strip():
        # Asegurar que la prompt personalizada tenga el encabezado
        if not prompt_personalizado.strip().startswith("### INSTRUCCIONES") and not prompt_personalizado.strip().startswith("### [INSTRUCCIONES]"):
            instrucciones_con_encabezado = f"### INSTRUCCIONES:\n\n{prompt_personalizado}"
        else:
            instrucciones_con_encabezado = prompt_personalizado
        prompt_completa = f"{instrucciones_con_encabezado}\n\n{datos_automaticos}"
    else:
        # Si prompt_base está vacío, solo usar datos automáticos
        if prompt_base.strip():
            prompt_completa = f"{prompt_base}\n\n{datos_automaticos}"
        else:
            prompt_completa = datos_automaticos
    
    return {
        'completa': prompt_completa,
        'personalizado': prompt_personalizado,
        'datos_automaticos': datos_automaticos
    }

# Función para construir preview de prompt del Agente 2
def construir_preview_agente_2():
    """Construye una preview de la prompt completa del Agente 2"""
    # Obtener estructura MEI
    estructura_mei = st.session_state.get('estructura_mei_selector', 'MEI-Actualizado')
    if not estructura_mei or estructura_mei not in ['MEI-Actualizado', 'MEI-Antiguo']:
        estructura_mei = 'MEI-Actualizado'
    
    cantidad_indicadores = st.session_state.get('cantidad_indicadores', 3)
    
    # Prompt personalizado (si existe)
    prompt_personalizado = st.session_state.get('agente_2', '').strip()
    
    # PROMPT BASE: Vacío (solo se muestran los datos automáticos)
    prompt_base = ""
    
    # DATOS AUTOMÁTICOS: Los datos reales que se inyectan
    if estructura_mei == 'MEI-Actualizado':
        rf_texto = st.session_state.rf_list[0] if st.session_state.get('rf_list') and len(st.session_state.rf_list) > 0 and st.session_state.rf_list[0] else "No disponible"
        ra_texto = st.session_state.ra_list[0] if st.session_state.get('ra_list') and len(st.session_state.ra_list) > 0 and st.session_state.ra_list[0] else "No disponible"
        datos_automaticos = f"""### DATOS DE ENTRADA:

- **Resultado Formativo (RF):**
  "{rf_texto}"
  
- **Resultado de Aprendizaje (RA):**
  "{ra_texto}"
  
- **Nombre del Curso:**
  "{st.session_state.get('nombre_curso', 'Nombre de curso no disponible')}"
"""
    else:  # MEI-Antiguo
        ra_texto = st.session_state.ra_list[0] if st.session_state.get('ra_list') and len(st.session_state.ra_list) > 0 and st.session_state.ra_list[0] else "No disponible"
        ae_texto = st.session_state.ae_list[0] if st.session_state.get('ae_list') and len(st.session_state.ae_list) > 0 and st.session_state.ae_list[0] else "No disponible"
        datos_automaticos = f"""### DATOS DE ENTRADA:

- **Resultado de Aprendizaje (RA):**
  "{ra_texto}"
  
- **Aprendizaje Esperado (AE):**
  "{ae_texto}"
  
- **Nombre del Curso:**
  "{st.session_state.get('nombre_curso', 'Nombre de curso no disponible')}"
"""
    
    # Agregar trimestre solo si existe
    trimestre = st.session_state.get('trimestre', '').strip()
    if trimestre:
        datos_automaticos += f"\n- **Trimestre:**\n  {trimestre}"
    
    # Agregar metodología solo si existe
    metodologia = st.session_state.get('metodologia', '').strip()
    if metodologia:
        datos_automaticos += f"\n\n- **Metodología Propuesta:**\n  \"{metodologia}\""
    
    # [RESPUESTA DEL AGENTE 1]: Placeholder para la respuesta del agente anterior
    respuesta_agente_1 = """### [RESPUESTA DEL AGENTE 1]

[La respuesta del Agente 1 se incluirá aquí automáticamente durante la ejecución]"""
    
    # [INSTRUCCIONES]: La tarea que debe realizar el agente (aquí impacta la prompt personalizada)
    if prompt_personalizado:
        # Si hay prompt personalizada, agregar encabezado si no lo tiene
        if not prompt_personalizado.strip().startswith("### INSTRUCCIONES") and not prompt_personalizado.strip().startswith("### [INSTRUCCIONES]"):
            instrucciones = f"### INSTRUCCIONES:\n\n{prompt_personalizado}"
        else:
            instrucciones = prompt_personalizado
    else:
        # Si no hay prompt personalizada, usar instrucciones por defecto
        if estructura_mei == 'MEI-Actualizado':
            rf_texto = st.session_state.rf_list[0] if st.session_state.get('rf_list') and len(st.session_state.rf_list) > 0 and st.session_state.rf_list[0] else "No disponible"
            instrucciones = f"""### [INSTRUCCIONES]

Eres un experto en diseño instruccional y evaluación pedagógica, especializado en la Taxonomía de Bloom revisada y los estándares de Quality Matters.

Tu tarea es generar Indicadores de Desempeño (ID) que sean:
- **Observables y medibles** (Quality Matters Standard 3.1)
- **Alineados con el Resultado de Aprendizaje (RA)** (Quality Matters Standard 2.1)
- **Progresivos en complejidad cognitiva** (Taxonomía de Bloom)
- **Libres de finalidad** (describen evidencias, no propósitos)

### CONTEXTO SUPERIOR (RF):
{rf_texto}

### TU TAREA (MEI ACTUALIZADO):
Genera EXACTAMENTE {cantidad_indicadores} Indicadores de Desempeño (ID) que funcionen como "peldaños" para el RA.

Para cada indicador, describe:
1. El texto completo del indicador (debe comenzar con el verbo en TERCERA PERSONA PLURAL INDICATIVO PRESENTE, ej. "EXPLICAN", "DIFERENCIAN", "INTEGRAN")
2. El verbo principal utilizado (en infinitivo, ej. "EXPLICAR", "DIFERENCIAR")
3. El Nivel Taxonómico de Bloom (1-6) de ese verbo
4. Una justificación pedagógica breve (1 frase) explicando cómo este ID actúa como un "peldaño" necesario para construir el RA principal

IMPORTANTE: Debes generar EXACTAMENTE {cantidad_indicadores} indicadores, ni más ni menos.

Responde de forma natural y creativa, describiendo cada indicador con claridad. NO uses formato JSON, solo texto descriptivo."""
        else:  # MEI-Antiguo
            ra_texto = st.session_state.ra_list[0] if st.session_state.get('ra_list') and len(st.session_state.ra_list) > 0 and st.session_state.ra_list[0] else "No disponible"
            instrucciones = f"""### [INSTRUCCIONES]

Eres un experto en diseño instruccional y evaluación pedagógica, especializado en la Taxonomía de Bloom revisada y los estándares de Quality Matters.

Tu tarea es generar Indicadores de Logro (IL) que sean:
- **Observables y medibles** (Quality Matters Standard 3.1)
- **Alineados con el Aprendizaje Esperado (AE)** (Quality Matters Standard 2.1)
- **Progresivos en complejidad cognitiva** (Taxonomía de Bloom)
- **Libres de finalidad** (describen evidencias, no propósitos)

### CONTEXTO SUPERIOR (RA):
{ra_texto}

### TU TAREA (MEI ANTIGUO):
Genera EXACTAMENTE {cantidad_indicadores} Indicadores de Logro (IL) que funcionen como "peldaños" para el AE.

Para cada indicador, describe:
1. La habilidad (verbo de acción principal en TERCERA PERSONA PLURAL INDICATIVO PRESENTE, ej. "DIFERENCIAN", "EXPLICAN")
2. El contenido (el "qué" se evalúa - el objeto directo del verbo)
3. La condición/contexto (el "cómo" o "dónde" se realiza la acción)
4. Una justificación pedagógica breve (1 frase) explicando cómo este IL actúa como un "peldaño" necesario para construir el AE principal

IMPORTANTE: Debes generar EXACTAMENTE {cantidad_indicadores} indicadores, ni más ni menos.

Responde de forma natural y creativa, describiendo cada indicador con claridad. NO uses formato JSON, solo texto descriptivo."""
    
    # Construir prompt completa final: PROMPT BASE + DATOS AUTOMÁTICOS + [RESPUESTA DEL AGENTE 1] + [INSTRUCCIONES]
    # Asegurar que las instrucciones tengan el encabezado
    if not instrucciones.strip().startswith("### INSTRUCCIONES") and not instrucciones.strip().startswith("### [INSTRUCCIONES]"):
        instrucciones_con_encabezado = f"### INSTRUCCIONES:\n\n{instrucciones}"
    else:
        instrucciones_con_encabezado = instrucciones
    
    prompt_completa = f"""{prompt_base}

{datos_automaticos}

{respuesta_agente_1}

{instrucciones_con_encabezado}"""
    
    return {
        'completa': prompt_completa,
        'personalizado': prompt_personalizado,
        'datos_automaticos': datos_automaticos
    }

# Campos de edición de prompts
# Cargar prompts persistentes para esta combinación
prompts_persistentes = cargar_prompts_persistentes(workflow_type, cantidad_agentes, estructura_mei)

# Obtener instrucciones de ejemplo
instrucciones_ejemplo_1 = obtener_instrucciones_ejemplo(workflow_type, cantidad_agentes, estructura_mei, 1)
instrucciones_ejemplo_2 = obtener_instrucciones_ejemplo(workflow_type, cantidad_agentes, estructura_mei, 2)

# Inicializar prompts: usar persistentes si existen, sino usar instrucciones de ejemplo
# Si se cargó un caso, los valores ya están en session_state, no sobrescribirlos
# Si no hay valor persistente y no hay valor en session_state, usar instrucciones de ejemplo
if 'agente_1' not in st.session_state or not st.session_state.agente_1.strip():
    prompt_persistente_1 = prompts_persistentes.get('agente_1', '')
    if prompt_persistente_1:
        st.session_state.agente_1 = prompt_persistente_1
        logger.info(f"[DEBUG] Cargando prompt persistente para agente_1 - length: {len(prompt_persistente_1)}")
    else:
        st.session_state.agente_1 = instrucciones_ejemplo_1
        logger.info(f"[DEBUG] Usando instrucciones de ejemplo para agente_1 - length: {len(instrucciones_ejemplo_1)}")

if 'agente_2' not in st.session_state or not st.session_state.agente_2.strip():
    prompt_persistente_2 = prompts_persistentes.get('agente_2', '')
    if prompt_persistente_2:
        st.session_state.agente_2 = prompt_persistente_2
        logger.info(f"[DEBUG] Cargando prompt persistente para agente_2 - length: {len(prompt_persistente_2)}")
    else:
        st.session_state.agente_2 = instrucciones_ejemplo_2
        logger.info(f"[DEBUG] Usando instrucciones de ejemplo para agente_2 - length: {len(instrucciones_ejemplo_2)}")

# Layout de prompts según workflow y cantidad de agentes
if workflow_type == "revisar-indicadores-v2":
    # Workflow de Revisar: 1 o 2 agentes (igual que Generar)
    if cantidad_agentes == 1:
        # Un solo agente: ocupa todo el ancho
        st.markdown("#### Agente 1")
        agente_1 = st.text_area(
            "**Prompt personalizada** (opcional):",
            value=st.session_state.agente_1,
            height=150,
            help="**¿Qué es esto?** Aquí puedes escribir instrucciones personalizadas para el Agente 1. Si lo dejas vacío, se usará la prompt por defecto. | **¿Cómo funciona?** Tu prompt se combinará automáticamente con los datos de entrada (RF/RA, curso, etc.) para formar la prompt completa. Usa la vista previa para ver exactamente qué recibirá el agente. | **Tip:** Las prompts se guardan automáticamente para cada combinación (tipo de trabajo, MEI, cantidad de agentes).",
            key=f"agente_1_input_v{st.session_state.widget_version}",
            placeholder=instrucciones_ejemplo_1
        )
        st.session_state.agente_1 = agente_1
        
        # Vista previa - SIEMPRE expandida si hay prompt personalizada
        preview_1 = construir_preview_agente_1_revisar()
        expanded_1 = bool(preview_1['personalizado'])
        with st.expander("👁️ Ver prompt completa que recibirá el Agente 1", expanded=expanded_1):
            st.markdown("**Esta es la prompt completa que recibirá el Agente 1:**")
            st.code(preview_1['completa'], language='markdown')
            if preview_1['personalizado']:
                st.success("✅ Se está usando una prompt personalizada")
            else:
                st.info("ℹ️ Se está usando la prompt por defecto")
        
        # Agente 2 no se muestra cuando cantidad_agentes = 1
        agente_2 = ""
        if 'agente_2' in st.session_state:
            st.session_state.agente_2 = ""
    else:
        # Dos agentes: lado a lado
        col1, col2 = st.columns(2)

        with col1:
            st.markdown("#### Agente 1")
            agente_1 = st.text_area(
                "**Prompt personalizada** (opcional):",
                value=st.session_state.agente_1,
                height=150,
                help="**¿Qué es esto?** Aquí puedes escribir instrucciones personalizadas para el Agente 1. Si lo dejas vacío, se usará la prompt por defecto. | **¿Cómo funciona?** Tu prompt se combinará automáticamente con los datos de entrada (RF/RA, curso, etc.) para formar la prompt completa. Usa la vista previa para ver exactamente qué recibirá el agente. | **Tip:** Las prompts se guardan automáticamente para cada combinación (tipo de trabajo, MEI, cantidad de agentes).",
                key=f"agente_1_input_v{st.session_state.widget_version}",
                placeholder="Deja vacío para usar la prompt por defecto..."
            )
            st.session_state.agente_1 = agente_1
            
            # Vista previa - SIEMPRE expandida si hay prompt personalizada
            preview_1 = construir_preview_agente_1_revisar()
            expanded_1 = bool(preview_1['personalizado'])
            with st.expander("👁️ Ver prompt completa que recibirá el Agente 1", expanded=expanded_1):
                st.markdown("**Esta es la prompt completa que recibirá el Agente 1:**")
                st.code(preview_1['completa'], language='markdown')
                if preview_1['personalizado']:
                    st.success("✅ Se está usando una prompt personalizada")
                else:
                    st.info("ℹ️ Se está usando la prompt por defecto")

        with col2:
            st.markdown("#### Agente 2")
            agente_2 = st.text_area(
                "**Prompt personalizada** (opcional):",
                value=st.session_state.agente_2,
                height=150,
                help="**¿Qué es esto?** Aquí puedes escribir instrucciones personalizadas para el Agente 2. Si lo dejas vacío, se usará la prompt por defecto. | **¿Cómo funciona?** Tu prompt se combinará automáticamente con la respuesta del Agente 1 y los datos de entrada (RF/RA, curso, etc.) para formar la prompt completa. Usa la vista previa para ver exactamente qué recibirá el agente. | **Tip:** Las prompts se guardan automáticamente para cada combinación (tipo de trabajo, MEI, cantidad de agentes).",
                key=f"agente_2_input_v{st.session_state.widget_version}",
                placeholder=instrucciones_ejemplo_2
            )
            st.session_state.agente_2 = agente_2

            # Vista previa - SIEMPRE expandida si hay prompt personalizada
            preview_2 = construir_preview_agente_2_revisar()
            expanded_2 = bool(preview_2['personalizado'])
            with st.expander("👁️ Ver prompt completa que recibirá el Agente 2", expanded=expanded_2):
                st.markdown("**Esta es la prompt completa que recibirá el Agente 2:**")
                st.code(preview_2['completa'], language='markdown')
                st.caption("💡 Nota: La respuesta del Agente 1 se incluirá automáticamente en la sección 'SALIDA DEL AGENTE ANTERIOR' durante la ejecución")
                if preview_2['personalizado']:
                    st.success("✅ Se está usando una prompt personalizada")
                else:
                    st.info("ℹ️ Se está usando la prompt por defecto")

elif cantidad_agentes == 1:
    # Un solo agente: ocupa todo el ancho
    st.markdown("#### Agente 1")
    agente_1 = st.text_area(
        "**Prompt personalizada** (opcional):",
        value=st.session_state.agente_1,
        height=150,
        help="Si está vacío, se usará la prompt por defecto. Si escribes algo, se usará tu prompt personalizada junto con los datos automáticos.",
        key=f"agente_1_input_v{st.session_state.widget_version}",
        placeholder="Deja vacío para usar la prompt por defecto..."
    )
    st.session_state.agente_1 = agente_1
    
    # Vista previa - SIEMPRE expandida si hay prompt personalizada
    preview_1 = construir_preview_agente_1()
    expanded_1 = bool(preview_1['personalizado'])
    with st.expander("👁️ Ver prompt completa que recibirá el Agente 1", expanded=expanded_1):
        st.markdown("**Esta es la prompt completa que recibirá el Agente 1:**")
        st.code(preview_1['completa'], language='markdown')
        if preview_1['personalizado']:
            st.success("✅ Se está usando una prompt personalizada")
        else:
            st.info("ℹ️ Se está usando la prompt por defecto")
    
    # Agente 2 no se muestra cuando cantidad_agentes = 1
    agente_2 = ""
    if 'agente_2' in st.session_state:
        st.session_state.agente_2 = ""
else:
    # Dos agentes: lado a lado
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown("#### Agente 1")
        agente_1 = st.text_area(
            "**Prompt personalizada** (opcional):",
            value=st.session_state.agente_1,
            height=150,
            help="**¿Qué es esto?** Aquí puedes escribir instrucciones personalizadas para el Agente 1. Si lo dejas vacío, se usará la prompt por defecto. | **¿Cómo funciona?** Tu prompt se combinará automáticamente con los datos de entrada (RF/RA, curso, etc.) para formar la prompt completa. Usa la vista previa para ver exactamente qué recibirá el agente. | **Tip:** Las prompts se guardan automáticamente para cada combinación (tipo de trabajo, MEI, cantidad de agentes).",
            key=f"agente_1_input_v{st.session_state.widget_version}",
            placeholder=instrucciones_ejemplo_1
        )
        st.session_state.agente_1 = agente_1
        
        # Vista previa - SIEMPRE expandida si hay prompt personalizada
        preview_1 = construir_preview_agente_1()
        expanded_1 = bool(preview_1['personalizado'])
        with st.expander("👁️ Ver prompt completa que recibirá el Agente 1", expanded=expanded_1):
            st.markdown("**Esta es la prompt completa que recibirá el Agente 1:**")
            st.code(preview_1['completa'], language='markdown')
            if preview_1['personalizado']:
                st.success("✅ Se está usando una prompt personalizada")
            else:
                st.info("ℹ️ Se está usando la prompt por defecto")
    
    with col2:
        st.markdown("#### Agente 2")
        agente_2 = st.text_area(
            "**Prompt personalizada** (opcional):",
            value=st.session_state.agente_2,
            height=150,
            help="**¿Qué es esto?** Aquí puedes escribir instrucciones personalizadas para el Agente 2. Si lo dejas vacío, se usará la prompt por defecto. | **¿Cómo funciona?** Tu prompt se combinará automáticamente con la respuesta del Agente 1 y los datos de entrada (RF/RA, curso, etc.) para formar la prompt completa. Usa la vista previa para ver exactamente qué recibirá el agente. | **Tip:** Las prompts se guardan automáticamente para cada combinación (tipo de trabajo, MEI, cantidad de agentes).",
            key=f"agente_2_input_v{st.session_state.widget_version}",
            placeholder="Deja vacío para usar la prompt por defecto..."
        )
        st.session_state.agente_2 = agente_2
        
        # Vista previa - SIEMPRE expandida si hay prompt personalizada
        preview_2 = construir_preview_agente_2()
        expanded_2 = bool(preview_2['personalizado'])
        with st.expander("👁️ Ver prompt completa que recibirá el Agente 2", expanded=expanded_2):
            st.markdown("**Esta es la prompt completa que recibirá el Agente 2:**")
            st.code(preview_2['completa'], language='markdown')
            st.caption("💡 Nota: La respuesta del Agente 1 se incluirá automáticamente en la sección 'SALIDA DEL AGENTE ANTERIOR' durante la ejecución")
            if preview_2['personalizado']:
                st.success("✅ Se está usando una prompt personalizada")
            else:
                st.info("ℹ️ Se está usando la prompt por defecto")

# Construir payload
def build_payload():
    """Construye el payload según el workflow y la estructura MEI"""
    # Obtener valores de agentes según el workflow
    agente_1_val = st.session_state.get('agente_1', '')
    agente_2_val = st.session_state.get('agente_2', '')
    
    payload = {
        "estructuraMEI": estructura_mei,
        "Agente_1": agente_1_val,
        "Agente_2": agente_2_val,
        "cantidad_indicadores": cantidad_indicadores,
        "cantidad_agentes": cantidad_agentes  # 1 o 2 agentes (tanto para generar como para revisar)
    }
    
    # Agregar campos opcionales si tienen valor
    if nombre_curso:
        payload["nombre_curso"] = nombre_curso
    if metodologia:
        payload["metodologia"] = metodologia
    if trimestre:
        payload["trimestre"] = trimestre
    
    # Función auxiliar para convertir strings a objetos con id y texto
    def string_to_obj(texto, prefix, index):
        """Convierte un string a objeto con id y texto"""
        if isinstance(texto, dict):
            # Si ya es un objeto, verificar que tenga texto
            if 'texto' in texto:
                return texto
            # Si tiene solo id, usar el texto del string original
            return {'id': texto.get('id', f'{prefix}-{index + 1}'), 'texto': str(texto)}
        # Si es string, convertirlo a objeto
        return {'id': f'{prefix}-{index + 1}', 'texto': texto.strip()}
    
    # Agregar arrays según estructura MEI
    if estructura_mei == "MEI-Antiguo":
        # Filtrar RAs vacíos y convertir a array de objetos
        ra_filtered = [ra for ra in st.session_state.ra_list if ra and str(ra).strip()]
        payload["resultadosAprendizaje"] = [
            string_to_obj(ra, "RA", idx) 
            for idx, ra in enumerate(ra_filtered)
        ]
        
        if workflow_type == "generar-indicadores-v2":
            # Filtrar AEs vacíos y convertir a array de objetos
            ae_filtered = [ae for ae in st.session_state.ae_list if ae and str(ae).strip()]
            payload["aprendizajesEsperados"] = [
                string_to_obj(ae, "AE", idx)
                for idx, ae in enumerate(ae_filtered)
            ]
        else:  # revisar-indicadores-v2
            # Para revisar, necesitamos AEs con indicadores
            ae_filtered = [ae for ae in st.session_state.ae_list if ae and str(ae).strip()]
            payload["aprendizajesEsperados"] = [
                string_to_obj(ae, "AE", idx)
                for idx, ae in enumerate(ae_filtered)
            ]
            # Los indicadores se envían por separado
            if 'indicadores_list' in st.session_state:
                indicadores_array = [ind.strip() for ind in st.session_state.indicadores_list if ind and str(ind).strip()]
                payload["indicadores_a_revisar"] = indicadores_array
    
    else:  # MEI-Actualizado
        # Filtrar RFs vacíos y convertir a array de objetos
        rf_filtered = [rf for rf in st.session_state.rf_list if rf and str(rf).strip()]
        payload["resultadosFormativos"] = [
            string_to_obj(rf, "RF", idx)
            for idx, rf in enumerate(rf_filtered)
        ]
        
        if workflow_type == "generar-indicadores-v2":
            # Filtrar RAs vacíos y convertir a array de objetos
            ra_filtered = [ra for ra in st.session_state.ra_list if ra and str(ra).strip()]
            payload["resultadosAprendizaje"] = [
                string_to_obj(ra, "RA", idx)
                for idx, ra in enumerate(ra_filtered)
            ]
        else:  # revisar-indicadores-v2
            # Para revisar, necesitamos RAs con indicadores
            ra_filtered = [ra for ra in st.session_state.ra_list if ra and str(ra).strip()]
            payload["resultadosAprendizaje"] = [
                string_to_obj(ra, "RA", idx)
                for idx, ra in enumerate(ra_filtered)
            ]
            # Los indicadores se envían por separado
            if 'indicadores_list' in st.session_state:
                indicadores_array = [ind.strip() for ind in st.session_state.indicadores_list if ind and str(ind).strip()]
                payload["indicadores_a_revisar"] = indicadores_array
    
    return payload

# Construir payload y guardarlo para el sidebar
try:
    payload_sidebar = build_payload()
    st.session_state.payload_sidebar = payload_sidebar
except:
    st.session_state.payload_sidebar = None

# Botón para enviar (prominente y destacado)
button_text = "🧪 Generar Indicadores" if workflow_type == "generar-indicadores-v2" else "🔍 Revisar Indicadores"
button_help = "Envía la configuración al workflow de N8N para generar nuevos indicadores. El proceso puede tardar unos segundos. Revisa los resultados y las prompts utilizadas al finalizar." if workflow_type == "generar-indicadores-v2" else "Envía la configuración al workflow de N8N para revisar los indicadores existentes. El proceso puede tardar unos segundos. Revisa los resultados y las prompts utilizadas al finalizar."
send_button = st.button(button_text, type="primary", use_container_width=True, help=button_help)

# Enviar a n8n
if send_button:
    # Guardar prompts persistentes antes de ejecutar
    agente_1_val = st.session_state.get('agente_1', '').strip()
    agente_2_val = st.session_state.get('agente_2', '').strip()
    guardar_prompts_persistentes(workflow_type, cantidad_agentes, estructura_mei, agente_1_val, agente_2_val)
    
    # Reconstruir payload con los valores actuales de los agentes
    payload = build_payload()
    
    webhook_path = f"/webhook/{workflow_type}"
    webhook_url = f"{N8N_BASE_URL.rstrip('/')}{webhook_path}"
    
    with st.spinner(f"⏳ Enviando a {webhook_path}..."):
        try:
            response = requests.post(
                webhook_url, 
                json=payload, 
                timeout=timeout,
                headers={'Content-Type': 'application/json'}
            )
            
            # Guardar respuesta en el historial
            response_data = {
                "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                "workflow": workflow_type,
                "webhook": webhook_path,
                "status_code": response.status_code,
                "payload": payload,
                "response": None
            }
            
            try:
                response_data["response"] = response.json()
            except:
                response_data["response"] = response.text
            
            st.session_state.webhook_responses.insert(0, response_data)
            
            # Mostrar resultado
            st.markdown("---")
            st.subheader("📊 Resultado")
            
            if response.status_code in [200, 202]:
                st.success(f"✅ Respuesta exitosa (código: {response.status_code})")
                
                # Mostrar respuesta de forma simplificada
                try:
                    response_data = response.json()
                    
                    # Manejar respuesta que puede venir como array o dict
                    if isinstance(response_data, list) and len(response_data) > 0:
                        response_json = response_data[0]  # Tomar el primer elemento si es array
                    elif isinstance(response_data, dict):
                        response_json = response_data
                    else:
                        st.json(response_data)
                        st.info("ℹ️ Formato de respuesta no reconocido.")
                        response_json = None
                    
                    # Función para mostrar indicadores de forma visual
                    if response_json:
                        # Detectar si es modo "revisar" o "generar"
                        es_modo_revisar = workflow_type == "revisar-indicadores-v2"
                        
                        def mostrar_indicadores_mei_actualizado(analisis_list):
                            """Muestra indicadores para MEI-Actualizado"""
                            for idx, analisis in enumerate(analisis_list, 1):
                                # Obtener el texto del RA si está disponible
                                ra_texto = analisis.get('texto', f'RA {idx}')
                                if 'id' in analisis:
                                    ra_id = analisis.get('id', f'RA-{idx}')
                                    st.markdown(f"### 🎯 {ra_id}: {ra_texto}")
                                else:
                                    st.markdown(f"### 🎯 Resultado de Aprendizaje {idx}")
                                    if ra_texto != f'RA {idx}':
                                        st.markdown(f"*{ra_texto}*")
                                
                                indicadores = analisis.get('indicadoresGenerados', [])
                                if indicadores:
                                    if es_modo_revisar:
                                        st.markdown("#### 📝 Indicadores Revisados:")
                                    else:
                                        st.markdown("#### 📝 Indicadores Generados:")
                                    
                                    for ind_idx, indicador in enumerate(indicadores, 1):
                                        with st.container():
                                            if es_modo_revisar:
                                                # Formato para REVISAR: mostrar todos los campos disponibles de forma flexible
                                                import re
                                                # Intentar obtener el texto del indicador de diferentes campos posibles
                                                indicador_texto = (
                                                    indicador.get('indicador_original') or 
                                                    indicador.get('indicador') or 
                                                    indicador.get('texto')
                                                )
                                                
                                                # Si no hay texto directo, construir una descripción a partir de los campos disponibles
                                                if not indicador_texto:
                                                    # Intentar construir el texto a partir de verbo_observable, producto_o_proceso y condicion_de_calidad_o_contexto
                                                    verbo_info = indicador.get('verbo_observable', '')
                                                    producto_info = indicador.get('producto_o_proceso', '')
                                                    condicion_info = indicador.get('condicion_de_calidad_o_contexto', '')
                                                    
                                                    partes = []
                                                    
                                                    # Extraer el verbo del campo verbo_observable
                                                    if verbo_info:
                                                        verbo_match = re.search(r"'([^']+)'", verbo_info)
                                                        if verbo_match:
                                                            verbo = verbo_match.group(1)
                                                            partes.append(verbo.upper())
                                                    
                                                    # Extraer el producto/proceso
                                                    if producto_info:
                                                        producto_match = re.search(r"'([^']+)'", producto_info)
                                                        if producto_match:
                                                            partes.append(producto_match.group(1))
                                                    
                                                    # Extraer la condición/contexto
                                                    if condicion_info:
                                                        condicion_match = re.search(r"'([^']+)'", condicion_info)
                                                        if condicion_match:
                                                            partes.append(condicion_match.group(1))
                                                    
                                                    if partes:
                                                        indicador_texto = ', '.join(partes)
                                                    else:
                                                        indicador_texto = f"Indicador {ind_idx} (revisado)"
                                                
                                                st.markdown(f"**{ind_idx}.** {indicador_texto}")
                                                
                                                # Mostrar todos los campos disponibles de forma genérica
                                                campos_mostrar = []
                                                
                                                # Campos comunes que podrían estar presentes
                                                if indicador.get('verbo_detectado') or indicador.get('verbo'):
                                                    verbo = indicador.get('verbo_detectado') or indicador.get('verbo')
                                                    nivel = indicador.get('nivel_verbo') or indicador.get('nivel')
                                                    if nivel:
                                                        campos_mostrar.append(f"🔍 **Verbo:** {verbo} | **Bloom:** Nivel {nivel}")
                                                    else:
                                                        campos_mostrar.append(f"🔍 **Verbo:** {verbo}")
                                                
                                                if indicador.get('observabilidad'):
                                                    campos_mostrar.append(f"📊 **Observabilidad:** {indicador.get('observabilidad')}")
                                                
                                                if indicador.get('alineamiento'):
                                                    # Extraer solo la parte "ALTO", "MEDIO", "BAJO" del alineamiento
                                                    alineamiento_texto = indicador.get('alineamiento', '')
                                                    if alineamiento_texto:
                                                        alineamiento_match = re.search(r'\b(ALTO|MEDIO|BAJO)\b', alineamiento_texto)
                                                        if alineamiento_match:
                                                            nivel_alineamiento = alineamiento_match.group(1)
                                                            campos_mostrar.append(f"📊 **Alineamiento:** {nivel_alineamiento}")
                                                        else:
                                                            campos_mostrar.append(f"📊 **Alineamiento:** {alineamiento_texto}")
                                                
                                                if indicador.get('tiene_finalidad') is not None:
                                                    if indicador.get('tiene_finalidad'):
                                                        st.warning("⚠️ El indicador contiene finalidad (debe estar ausente)")
                                                
                                                if indicador.get('recomendaciones'):
                                                    st.info(f"💡 **Recomendación:** {indicador.get('recomendaciones')}")
                                                
                                                # Mostrar todos los campos encontrados
                                                for campo in campos_mostrar:
                                                    st.caption(campo)
                                                
                                                # Mostrar otros campos que no sean los comunes (verbo_observable, producto_o_proceso, etc.)
                                                campos_ignorados = {
                                                    'indicador_original', 'indicador', 'texto', 
                                                    'verbo_detectado', 'verbo', 'nivel_verbo', 'nivel',
                                                    'observabilidad', 'alineamiento', 'tiene_finalidad', 'recomendaciones'
                                                }
                                                otros_campos = {k: v for k, v in indicador.items() if k not in campos_ignorados and v is not None and v != ''}
                                                
                                                if otros_campos:
                                                    with st.expander("📋 Ver detalles adicionales"):
                                                        for key, value in otros_campos.items():
                                                            st.caption(f"**{key}:** {value}")
                                            else:
                                                # Formato para GENERAR: mostrar id_texto
                                                st.markdown(f"**{ind_idx}.** {indicador.get('id_texto', 'N/A')}")
                                                col1, col2 = st.columns([3, 1])
                                                with col1:
                                                    if indicador.get('justificacion_pedagogica'):
                                                        st.caption(f"💡 {indicador.get('justificacion_pedagogica')}")
                                                with col2:
                                                    nivel = indicador.get('nivel_verbo', 'N/A')
                                                    verbo = indicador.get('verbo_utilizado', 'N/A')
                                                    st.caption(f"Bloom {nivel} | {verbo}")
                                            st.markdown("---")
                                else:
                                    if es_modo_revisar:
                                        st.info("No se encontraron indicadores para revisar en este objetivo.")
                                    else:
                                        st.info("No se generaron indicadores para este objetivo.")
                        
                        def mostrar_indicadores_mei_antiguo(analisis_list):
                            """Muestra indicadores para MEI-Antiguo"""
                            for idx, analisis in enumerate(analisis_list, 1):
                                # Obtener el texto del AE si está disponible
                                ae_texto = analisis.get('texto', f'AE {idx}')
                                if 'id' in analisis:
                                    ae_id = analisis.get('id', f'AE-{idx}')
                                    st.markdown(f"### 🎯 {ae_id}: {ae_texto}")
                                else:
                                    st.markdown(f"### 🎯 Aprendizaje Esperado {idx}")
                                    if ae_texto != f'AE {idx}':
                                        st.markdown(f"*{ae_texto}*")
                                
                                indicadores = analisis.get('indicadoresGenerados', [])
                                if indicadores:
                                    if es_modo_revisar:
                                        st.markdown("#### 📝 Indicadores Revisados:")
                                    else:
                                        st.markdown("#### 📝 Indicadores Generados:")
                                    
                                    for ind_idx, indicador in enumerate(indicadores, 1):
                                        with st.container():
                                            if es_modo_revisar:
                                                # Formato para REVISAR: mostrar todos los campos disponibles de forma flexible
                                                import re
                                                # Intentar obtener el texto del indicador de diferentes campos posibles
                                                indicador_texto = (
                                                    indicador.get('indicador_original') or 
                                                    indicador.get('indicador') or 
                                                    indicador.get('texto')
                                                )
                                                
                                                # Si no hay texto directo, construir una descripción a partir de los campos disponibles
                                                if not indicador_texto:
                                                    # Intentar construir el texto a partir de verbo_observable, producto_o_proceso y condicion_de_calidad_o_contexto
                                                    verbo_info = indicador.get('verbo_observable', '')
                                                    producto_info = indicador.get('producto_o_proceso', '')
                                                    condicion_info = indicador.get('condicion_de_calidad_o_contexto', '')
                                                    
                                                    partes = []
                                                    
                                                    # Extraer el verbo del campo verbo_observable
                                                    if verbo_info:
                                                        verbo_match = re.search(r"'([^']+)'", verbo_info)
                                                        if verbo_match:
                                                            verbo = verbo_match.group(1)
                                                            partes.append(verbo.upper())
                                                    
                                                    # Extraer el producto/proceso
                                                    if producto_info:
                                                        producto_match = re.search(r"'([^']+)'", producto_info)
                                                        if producto_match:
                                                            partes.append(producto_match.group(1))
                                                    
                                                    # Extraer la condición/contexto
                                                    if condicion_info:
                                                        condicion_match = re.search(r"'([^']+)'", condicion_info)
                                                        if condicion_match:
                                                            partes.append(condicion_match.group(1))
                                                    
                                                    if partes:
                                                        indicador_texto = ', '.join(partes)
                                                    else:
                                                        indicador_texto = f"Indicador {ind_idx} (revisado)"
                                                
                                                st.markdown(f"**{ind_idx}.** {indicador_texto}")
                                                
                                                # Mostrar todos los campos disponibles de forma genérica
                                                campos_mostrar = []
                                                
                                                # Campos comunes que podrían estar presentes
                                                if indicador.get('verbo_detectado') or indicador.get('verbo'):
                                                    verbo = indicador.get('verbo_detectado') or indicador.get('verbo')
                                                    nivel = indicador.get('nivel_verbo') or indicador.get('nivel')
                                                    if nivel:
                                                        campos_mostrar.append(f"🔍 **Verbo:** {verbo} | **Bloom:** Nivel {nivel}")
                                                    else:
                                                        campos_mostrar.append(f"🔍 **Verbo:** {verbo}")
                                                
                                                if indicador.get('observabilidad'):
                                                    campos_mostrar.append(f"📊 **Observabilidad:** {indicador.get('observabilidad')}")
                                                
                                                if indicador.get('alineamiento'):
                                                    # Extraer solo la parte "ALTO", "MEDIO", "BAJO" del alineamiento
                                                    alineamiento_texto = indicador.get('alineamiento', '')
                                                    if alineamiento_texto:
                                                        alineamiento_match = re.search(r'\b(ALTO|MEDIO|BAJO)\b', alineamiento_texto)
                                                        if alineamiento_match:
                                                            nivel_alineamiento = alineamiento_match.group(1)
                                                            campos_mostrar.append(f"📊 **Alineamiento:** {nivel_alineamiento}")
                                                        else:
                                                            campos_mostrar.append(f"📊 **Alineamiento:** {alineamiento_texto}")
                                                
                                                if indicador.get('tiene_finalidad') is not None:
                                                    if indicador.get('tiene_finalidad'):
                                                        st.warning("⚠️ El indicador contiene finalidad (debe estar ausente)")
                                                
                                                if indicador.get('recomendaciones'):
                                                    st.info(f"💡 **Recomendación:** {indicador.get('recomendaciones')}")
                                                
                                                # Mostrar todos los campos encontrados
                                                for campo in campos_mostrar:
                                                    st.caption(campo)
                                                
                                                # Mostrar otros campos que no sean los comunes (verbo_observable, producto_o_proceso, etc.)
                                                campos_ignorados = {
                                                    'indicador_original', 'indicador', 'texto', 
                                                    'verbo_detectado', 'verbo', 'nivel_verbo', 'nivel',
                                                    'observabilidad', 'alineamiento', 'tiene_finalidad', 'recomendaciones'
                                                }
                                                otros_campos = {k: v for k, v in indicador.items() if k not in campos_ignorados and v is not None and v != ''}
                                                
                                                if otros_campos:
                                                    with st.expander("📋 Ver detalles adicionales"):
                                                        for key, value in otros_campos.items():
                                                            st.caption(f"**{key}:** {value}")
                                            else:
                                                # Formato para GENERAR: construir texto del indicador
                                                habilidad = indicador.get('habilidad', '')
                                                contenido = indicador.get('contenido', '')
                                                condicion = indicador.get('condicion_contexto', '')
                                                texto_completo = f"{habilidad} {contenido} {condicion}".strip()
                                                st.markdown(f"**{ind_idx}.** {texto_completo}")
                                                col1, col2 = st.columns([3, 1])
                                                with col1:
                                                    if indicador.get('justificacion_pedagogica'):
                                                        st.caption(f"💡 {indicador.get('justificacion_pedagogica')}")
                                                with col2:
                                                    st.caption("")
                                            st.markdown("---")
                                else:
                                    if es_modo_revisar:
                                        st.info("No se encontraron indicadores para revisar en este objetivo.")
                                    else:
                                        st.info("No se generaron indicadores para este objetivo.")
                        
                        # Mostrar indicadores según la estructura MEI
                        estructura_mei = response_json.get('estructuraMEI', 'MEI-Antiguo')
                        
                        if "analisisResultadosAprendizaje" in response_json:
                            mostrar_indicadores_mei_actualizado(
                                response_json.get("analisisResultadosAprendizaje", [])
                            )
                        
                        if "analisisAprendizajesEsperados" in response_json:
                            mostrar_indicadores_mei_antiguo(
                                response_json.get("analisisAprendizajesEsperados", [])
                            )
                        
                        # Si no hay análisis, mostrar mensaje
                        if "analisisResultadosAprendizaje" not in response_json and "analisisAprendizajesEsperados" not in response_json:
                            st.info("ℹ️ La respuesta no contiene análisis de indicadores.")
                        
                        # Mostrar prompts utilizadas si están disponibles
                        if "prompts_utilizadas" in response_json:
                            st.markdown("---")
                            st.subheader("📋 Prompts Utilizadas en esta Ejecución")
                            st.markdown("Aquí puedes ver exactamente qué prompts se usaron para generar estos indicadores. Útil para iterar y mejorar.")
                            
                            prompts_meta = response_json["prompts_utilizadas"]
                            
                            if "agente_1" in prompts_meta:
                                with st.expander("📝 Agente 1 - Prompt Utilizada", expanded=False):
                                    meta_1 = prompts_meta["agente_1"]
                                    st.markdown("**Prompt completa que recibió el Agente 1:**")
                                    st.code(meta_1.get("prompt_completa", "No disponible"), language="markdown")
                                    if meta_1.get("prompt_personalizado"):
                                        st.success("✅ Se usó una prompt personalizada")
                                    else:
                                        st.info("ℹ️ Se usó la prompt por defecto")
                            
                            if "agente_2" in prompts_meta:
                                with st.expander("📝 Agente 2 - Prompt Utilizada", expanded=False):
                                    meta_2 = prompts_meta["agente_2"]
                                    st.markdown("**Prompt completa que recibió el Agente 2:**")
                                    st.code(meta_2.get("prompt_completa", "No disponible"), language="markdown")
                                    if meta_2.get("prompt_personalizado"):
                                        st.success("✅ Se usó una prompt personalizada")
                                    else:
                                        st.info("ℹ️ Se usó la prompt por defecto")
                        
                except Exception as e:
                    st.error(f"❌ Error al procesar la respuesta: {str(e)}")
                    st.text(response.text)
            else:
                st.error(f"❌ Error (código: {response.status_code})")
                st.text(response.text)
                
        except requests.exceptions.Timeout:
            st.error(f"⏱️ La solicitud tardó más de {timeout} segundos. El workflow puede estar procesando, intenta aumentar el timeout.")
        except requests.exceptions.RequestException as e:
            st.error(f"❌ Error de conexión: {str(e)}")
            st.info("💡 Verifica que n8n esté corriendo y que el webhook esté activo")

# Historial de respuestas
if st.session_state.webhook_responses:
    st.markdown("---")
    st.subheader("📜 Historial de Respuestas")
    
    for idx, resp in enumerate(st.session_state.webhook_responses[:5]):  # Mostrar últimas 5
        with st.expander(f"🕐 {resp['timestamp']} - {resp['workflow']} (Código: {resp['status_code']})"):
            col1, col2 = st.columns(2)
            
            with col1:
                st.markdown("**📤 Payload enviado:**")
                st.json(resp['payload'])
            
            with col2:
                st.markdown("**📥 Respuesta recibida:**")
                if isinstance(resp['response'], dict):
                    st.json(resp['response'])
                else:
                    st.text(resp['response'])
            
            st.markdown(f"**🔗 Webhook:** `{resp['webhook']}`")
    
    if st.button("🗑️ Limpiar Historial"):
        st.session_state.webhook_responses = []
        st.rerun()
