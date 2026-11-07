import os
import json
from datetime import datetime

class SatjeModel:
    def __init__(self):
        self.json_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'archivos', 'json'))
        os.makedirs(self.json_dir, exist_ok=True)

    def buscar_archivo_existente(self, limpio_proceso: str):
        """Busca el archivo JSON más reciente que coincida con el número de proceso."""
        if not os.path.exists(self.json_dir):
            return None
        
        archivos_coincidentes = []
        for archivo in os.listdir(self.json_dir):
            if archivo.endswith('.json') and archivo.startswith(limpio_proceso):
                ruta_completa = os.path.join(self.json_dir, archivo)
                archivos_coincidentes.append(ruta_completa)
                
        if not archivos_coincidentes:
            return None
            
        # Retorna el archivo con fecha de modificación más reciente
        archivos_coincidentes.sort(key=lambda x: os.path.getmtime(x), reverse=True)
        return archivos_coincidentes[0]

    def obtener_tiempo_modificacion(self, ruta_archivo: str) -> float:
        """Devuelve el timestamp de modificación del archivo."""
        return os.path.getmtime(ruta_archivo)

    def leer_json(self, ruta_archivo: str):
        """Lee y carga el contenido de un archivo JSON existente."""
        with open(ruta_archivo, 'r', encoding='utf-8') as f:
            return json.load(f)

    def guardar_y_validar_json(self, limpio_proceso: str, datos_json: dict) -> tuple[bool, str]:
        """
        Guarda el JSON usando el formato {numeroproceso}_{yyyy-mm-dd}_{hhmm}.json
        y verifica que el archivo haya sido escrito físicamente en disco.
        """
        ahora = datetime.now()
        yyyy = ahora.strftime('%Y')
        mm = ahora.strftime('%m')
        dd = ahora.strftime('%d')
        hhmm = ahora.strftime('%H%M')
        
        nombre_archivo = f"{limpio_proceso}_{yyyy}-{mm}-{dd}_{hhmm}.json"
        ruta_completa = os.path.join(self.json_dir, nombre_archivo)

        try:
            with open(ruta_completa, 'w', encoding='utf-8') as f:
                json.dump(datos_json, f, ensure_ascii=False, indent=4)
            
            # Validación de guardado físico en disco
            if os.path.exists(ruta_completa) and os.path.getsize(ruta_completa) > 0:
                return True, ruta_completa
            else:
                return False, ""
        except Exception:
            return False, ""
