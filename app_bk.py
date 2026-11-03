from flask import Flask, jsonify, request
import os
import requests
import json
import logging
from datetime import datetime

app = Flask(__name__)

# Configuración de carpetas necesarias
LOGS_DIR = 'logs'
JSON_DIR = os.path.join('archivos', 'json')
os.makedirs(LOGS_DIR, exist_ok=True)
os.makedirs(JSON_DIR, exist_ok=True)

# Configuración del sistema de logs diario: \logs\log_{fecha}.log
fecha_actual = datetime.now().strftime('%Y-%m-%d')
log_filename = os.path.join(LOGS_DIR, f'log_{fecha_actual}.log')

logging.basicConfig(
    filename=log_filename,
    level=logging.INFO,
    format='%(asctime)s [%(levelname)s] %(message)s',
    encoding='utf-8'
)

def consultar_y_guardar_proceso(numero_proceso):
    """Consulta al API externo, guarda el JSON resultante o el error, y registra en los logs."""
    limpio_proceso = numero_proceso.replace("-", "").strip()
    url = f'http://186.3.198.68:89/ApirestProcesosJudicialesJSON?url={limpio_proceso}'
    
    timestamp_archivo = datetime.now().strftime('%d-%m-%Y_%H%M')
    nombre_archivo = f"{limpio_proceso}_{timestamp_archivo}.json"
    ruta_archivo = os.path.join(JSON_DIR, nombre_archivo)
    
    resultado_datos = None
    estado_exitoso = False

    try:
        logging.info(f"Iniciando consulta al API para el proceso: {limpio_proceso}")
        response = requests.get(url, timeout=15)
        
        if response.status_code == 200:
            datos_json = response.json()
            # Guardar el archivo JSON con la estructura esperada
            with open(ruta_archivo, 'w', encoding='utf-8') as f:
                json.dump(datos_json, f, ensure_ascii=False, indent=4)
            
            mensaje = f"Consulta exitosa y JSON guardado: {nombre_archivo}"
            logging.info(mensaje)
            resultado_datos = datos_json
            estado_exitoso = True
        else:
            mensaje = f"Error en API. Código de estado: {response.status_code}"
            logging.error(f"Proceso {limpio_proceso} - {mensaje}")
            resultado_datos = {"error": mensaje, "status_code": response.status_code}
            
            # Guardar también el registro de la respuesta fallida
            with open(ruta_archivo, 'w', encoding='utf-8') as f:
                json.dump(resultado_datos, f, ensure_ascii=False, indent=4)

    except requests.exceptions.RequestException as e:
        mensaje = f"Excepción de conexión con el API: {e}"
        logging.error(f"Proceso {limpio_proceso} - {mensaje}")
        resultado_datos = {"error": mensaje}
        with open(ruta_archivo, 'w', encoding='utf-8') as f:
            json.dump(resultado_datos, f, ensure_ascii=False, indent=4)
            
    except Exception as e:
        mensaje = f"Error interno inesperado: {e}"
        logging.error(f"Proceso {limpio_proceso} - {mensaje}")
        resultado_datos = {"error": mensaje}
        with open(ruta_archivo, 'w', encoding='utf-8') as f:
            json.dump(resultado_datos, f, ensure_ascii=False, indent=4)

    return resultado_datos, estado_exitoso


@app.route('/api/consultar/<string:numero_proceso>', methods=['GET'])
def api_consultar_get(numero_proceso):
    """Endpoint por GET para consultar mediante URL."""
    datos, exito = consultar_y_guardar_proceso(numero_proceso)
    if exito:
        return jsonify(datos), 200
    else:
        return jsonify(datos), 500


@app.route('/api/consultar', methods=['GET', 'POST'])
def api_consultar():
    """Endpoint unificado que soporta tanto parámetros por URL (?criterio=...) como JSON por POST."""
    numero_proceso = ""
    
    # 1. Obtener el número de proceso dependiendo de si es GET (?criterio=...) o POST (JSON)
    if request.method == 'GET':
        numero_proceso = request.args.get('criterio', '')
    else:  # POST
        req_data = request.get_json(silent=True) or {}
        numero_proceso = req_data.get('num_proceso', '') or req_data.get('criterio', '')

    if not numero_proceso:
        return jsonify({"error": "Falta proporcionar el parámetro del número de proceso (ej: ?criterio=17230-2022-19079)"}), 400

    # Limpiar guiones para la consulta y búsqueda de archivos
    limpio_proceso = numero_proceso.replace("-", "").strip()
    url = f'http://186.3.198.68:89/ApirestProcesosJudicialesJSON?url={limpio_proceso}'
    
    timestamp_archivo = datetime.now().strftime('%d-%m-%Y_%H%M')
    nombre_archivo = f"{limpio_proceso}_{timestamp_archivo}.json"
    ruta_archivo = os.path.join(JSON_DIR, nombre_archivo)
    
    resultado_datos = None
    estado_exitoso = False

    try:
        logging.info(f"Iniciando consulta al API para el proceso: {limpio_proceso}")
        response = requests.get(url, timeout=10)
        
        if response.status_code == 200:
            datos_json = response.json()
            with open(ruta_archivo, 'w', encoding='utf-8') as f:
                json.dump(datos_json, f, ensure_ascii=False, indent=4)
            
            logging.info(f"Consulta exitosa y JSON guardado: {nombre_archivo}")
            resultado_datos = datos_json
            estado_exitoso = True
        else:
            mensaje = f"Error en API. Código de estado: {response.status_code}"
            logging.error(f"Proceso {limpio_proceso} - {mensaje}")
            resultado_datos = {"error": mensaje, "status_code": response.status_code}

    except requests.exceptions.RequestException as e:
        mensaje_error = f"Excepción de conexión con el API: {e}"
        logging.error(f"Proceso {limpio_proceso} - {mensaje_error}")
        
        # BÚSQUEDA INTELIGENTE DE RESPALDO LOCAL:
        # Busca cualquier archivo en archivos/json/ que comience con el número de proceso (limpio o con guiones)
        archivo_encontrado = None
        if os.path.exists(JSON_DIR):
            for archivo in os.listdir(JSON_DIR):
                # Compara si el archivo empieza con el número de proceso limpio
                if archivo.startswith(limpio_proceso) and archivo.endswith('.json'):
                    archivo_encontrado = os.path.join(JSON_DIR, archivo)
                    break
        
        if archivo_encontrado:
            logging.info(f"Cargando datos desde respaldo local: {archivo_encontrado}")
            with open(archivo_encontrado, 'r', encoding='utf-8') as f:
                resultado_datos = json.load(f)
            estado_exitoso = True
        else:
            # Si no hay conexión ni respaldo local, creamos un JSON simulado de respuesta para que no falle feo
            resultado_datos = {
                "aviso": "API externa no disponible, se generó respuesta vacía de respaldo.",
                "error": mensaje_error
            }
            # Opcional: guardarlo como respaldo de error en la carpeta json
            with open(ruta_archivo, 'w', encoding='utf-8') as f:
                json.dump(resultado_datos, f, ensure_ascii=False, indent=4)
            estado_exitoso = True  # Para que devuelva HTTP 200 con el aviso y no rompa el flujo

    if estado_exitoso:
        return jsonify(resultado_datos), 200
    else:
        return jsonify(resultado_datos), 500


@app.route('/')
def home():
    return jsonify({
        "estado": "Servicio Endpoint E-SATJE activo",
        "uso_get": "/api/consultar/<numero_proceso>",
        "uso_post": "/api/consultar (enviar JSON con {'num_proceso': '...'})"
    })


if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)