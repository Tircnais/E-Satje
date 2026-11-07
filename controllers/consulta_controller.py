import time
from flask import Blueprint, jsonify, request
from collections import OrderedDict
from models.satje_model import SatjeModel
from services.satje_scraper_service import SatjeScraperService

consulta_bp = Blueprint('consulta_bp', __name__)
satje_model = SatjeModel()
scraper_service = SatjeScraperService()

@consulta_bp.route('/api/consultar', methods=['GET'])
def consultar():
    proceso = request.args.get('proceso', '').strip()
    
    if not proceso:
        res_error = OrderedDict()
        res_error["estado"] = 400
        res_error["mensaje"] = "Parámetro incompleto."
        res_error["error"] = "El parámetro 'proceso' es obligatorio."
        return jsonify(dict(res_error)), 400

    limpio_proceso = proceso.replace("-", "").strip()

    try:
        # 1. Buscar archivo guardado previamente en caché local
        archivo_existente = satje_model.buscar_archivo_existente(limpio_proceso)

        if archivo_existente:
            tiempo_mod = satje_model.obtener_tiempo_modificacion(archivo_existente)
            horas_transcurridas = (time.time() - tiempo_mod) / 3600.0
            
            contenido_guardado = satje_model.leer_json(archivo_existente)
            
            # Obtener el estado guardado de forma segura
            estado_guardado = None
            if isinstance(contenido_guardado, dict):
                estado_guardado = contenido_guardado.get("estado")
            elif isinstance(contenido_guardado, list):
                estado_guardado = 200 # Compatibilidad con listas de respaldo antiguas

            # REGLA CLAVE: Solo usa la caché si tiene menos de 24h Y el estado fue estrictamente exitoso (200)
            # Si el archivo anterior tiene un error (ej. 503), esta condición falla y obliga a reintentar el scraping.
            if horas_transcurridas < 24.0 and estado_guardado == 200:
                return jsonify(contenido_guardado), 200

        # 2. Si no hay caché válida o la anterior registró un error, se ejecuta el scraping nuevamente
        nuevo_json = scraper_service.extraer_y_construir_json(proceso, limpio_proceso)

        # 3. Guardar el nuevo resultado y validar su persistencia física en disco
        guardado_exitoso, ruta_guardada = satje_model.guardar_y_validar_json(limpio_proceso, nuevo_json)

        if not guardado_exitoso:
            res_error = OrderedDict()
            res_error["estado"] = 500
            res_error["mensaje"] = "Error interno de almacenamiento."
            res_error["error"] = "No se pudo guardar ni validar la creación del archivo JSON de respaldo."
            return jsonify(dict(res_error)), 500

        codigo_estado = nuevo_json.get("estado", 503) if isinstance(nuevo_json, dict) else 200
        return jsonify(nuevo_json), codigo_estado

    except Exception as e:
        res_error = OrderedDict()
        res_error["estado"] = 500
        res_error["mensaje"] = "Error crítico en el controlador de consultas."
        res_error["error"] = str(e)
        return jsonify(dict(res_error)), 500
