from flask import Blueprint, jsonify, request
from services.satje_scraper_service import SatjeScraperService

consulta_bp = Blueprint('consulta_bp', __name__)
scraper_service = SatjeScraperService()

@consulta_bp.route('/api/consultar', methods=['GET'])
def consultar():
    """
    Endpoint exclusivo de consulta.
    Ejemplo: /api/consultar?criterio=0932201915797
    """
    criterio = request.args.get('criterio')
    
    if not criterio:
        return jsonify({"status": "error", "message": "El parámetro 'criterio' es obligatorio."}), 400

    # Llamada al servicio de automatización
    resultado = scraper_service.ejecutar_consulta(criterio)

    if resultado["status"] == "error":
        return jsonify(resultado), 500

    return jsonify(resultado), 200