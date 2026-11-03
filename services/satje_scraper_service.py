import os
import json
import time
import logging
from datetime import datetime, timedelta
from playwright.async_api import async_playwright

# Configuración del sistema de Logs en la raíz del proyecto
log_path = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'app.log'))
logging.basicConfig(
    filename=log_path,
    level=logging.INFO,
    format='%(asctime)s [%(levelname)s] %(message)s',
    encoding='utf-8'
)

class SatjeScraperService:
    def __init__(self):
        self.url = "https://procesosjudiciales.funcionjudicial.gob.ec/busqueda-filtros"
        # Carpeta para almacenar los JSONs de caché en la raíz del proyecto
        self.cache_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'cache_json'))
        if not os.path.exists(self.cache_dir):
            os.makedirs(self.cache_dir)

    def _obtener_ruta_cache(self, criterio: str):
        # Limpiamos el criterio para que sea un nombre de archivo válido
        safe_criterio = "".join(c for c in criterio if c.isalnum() or c in ('_', '-'))
        return os.path.join(self.cache_dir, f"{safe_criterio}.json")

    def _leer_cache(self, criterio: str):
        ruta_archivo = self._obtener_ruta_cache(criterio)
        if os.path.exists(ruta_archivo):
            # Verificar antigüedad del archivo (menor a 24 horas)
            tiempo_modificacion = os.path.getmtime(ruta_archivo)
            tiempo_actual = time.time()
            if (tiempo_actual - tiempo_modificacion) < 86400: # 86400 segundos = 24 horas
                try:
                    with open(ruta_archivo, 'r', encoding='utf-8') as f:
                        data = json.load(f)
                        logging.info(f"Caché utilizada exitosamente para el criterio: {criterio}")
                        return {"status": "success", "fuente": "cache", "data": data}
                except Exception as e:
                    logging.error(f"Error al leer la caché para {criterio}: {str(e)}")
        return None

    def _guardar_cache(self, criterio: str, datos):
        ruta_archivo = self._obtener_ruta_cache(criterio)
        try:
            with open(ruta_archivo, 'w', encoding='utf-8') as f:
                json.dump(datos, f, ensure_ascii=False, indent=4)
            logging.info(f"Caché actualizada/guardada para el criterio: {criterio}")
        except Exception as e:
            logging.error(f"Error al guardar la caché para {criterio}: {str(e)}")

    async def consultar_proceso(self, criterio_busqueda: str):
        # 1. Verificar si existe caché válida de menos de 24 horas
        cache_result = self._leer_cache(criterio_busqueda)
        if cache_result:
            return cache_result

        logging.info(f"Iniciando Web Scraping en el SATJE para el criterio: {criterio_busqueda}")
        async with async_playwright() as p:
            browser = await p.chromium.launch(headless=True)
            page = await browser.new_page()
            
            try:
                await page.goto(self.url, timeout=60000)
                await page.wait_for_selector("app-root", timeout=15000)

                # Rellenar el input de búsqueda (ajusta el selector según la estructura de Angular)
                input_selector = "input" # Selector general o específico de la caja de texto
                await page.fill(input_selector, criterio_busqueda)

                # Hacer clic en buscar
                await page.click("button:has-text('BUSCAR')")

                # Esperar a los resultados
                await page.wait_for_selector("mat-row, tr", timeout=10000)

                resultados = []
                filas = await page.locator("mat-row, tr").all()
                
                for fila in filas:
                    texto_fila = await fila.inner_text()
                    if criterio_busqueda in texto_fila:
                        resultados.append(texto_fila.strip())

                await browser.close()

                respuesta = {"status": "success", "fuente": "scraping", "data": resultados}
                
                # Guardar en la carpeta json de caché
                self._guardar_cache(criterio_busqueda, resultados)
                logging.info(f"Scraping completado con éxito para: {criterio_busqueda}")
                return respuesta

            except Exception as e:
                error_msg = str(e)
                logging.error(f"Error durante el scraping para {criterio_busqueda}: {error_msg}")
                await browser.close()
                return {"status": "error", "message": error_msg}

    def ejecutar_consulta(self, criterio_busqueda: str):
        import asyncio
        return asyncio.run(self.consultar_proceso(criterio_busqueda))
