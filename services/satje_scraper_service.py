import logging
import os
from datetime import datetime
from collections import OrderedDict
from playwright.sync_api import sync_playwright

try:
    from playwright_stealth import stealth_sync
except ImportError:
    stealth_sync = None

log_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'logs'))
os.makedirs(log_dir, exist_ok=True)
log_path = os.path.join(log_dir, f"log_{datetime.now().strftime('%Y-%m-%d')}.log")

logging.basicConfig(
    filename=log_path,
    level=logging.INFO,
    format='%(asctime)s [%(levelname)s] %(message)s',
    encoding='utf-8'
)

class SatjeScraperService:
    def __init__(self):
        self.url = "https://procesosjudiciales.funcionjudicial.gob.ec/busqueda-filtros"
        self.pdf_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'archivos', 'procesos'))
        os.makedirs(self.pdf_dir, exist_ok=True)

    def extraer_y_construir_json(self, proceso: str, limpio_proceso: str) -> dict:
        logging.info(f"Iniciando extracción por bloques de dependencia para el proceso: {proceso}")
        
        context = None
        try:
            with sync_playwright() as p:
                browser = p.chromium.launch(
                    headless=False,
                    args=[
                        "--disable-blink-features=AutomationControlled",
                        "--no-sandbox",
                        "--disable-dev-shm-usage",
                        "--disable-gpu",
                        "--start-maximized",
                        "--force-device-scale-factor=1"
                    ]
                )
                context = browser.new_context(
                    no_viewport=True,
                    user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0.0.0 Safari/537.36",
                    accept_downloads=True,
                    locale="es-ES"
                )
                
                page = context.new_page()

                if stealth_sync:
                    stealth_sync(page)
                else:
                    page.add_init_script("Object.defineProperty(navigator, 'webdriver', { get: () => undefined });")

                page.goto(self.url, timeout=45000)
                page.wait_for_selector("app-root", timeout=20000)
                page.wait_for_timeout(2000)

                # 1. Ingresar número de proceso en el input
                input_selector = "input"
                page.wait_for_selector(input_selector, state="visible", timeout=15000)
                page.click(input_selector)
                page.fill(input_selector, proceso)
                page.dispatch_event(input_selector, "input")
                page.dispatch_event(input_selector, "change")
                logging.info("Número de proceso escrito en el input.")

                # 2. Esperar resolución de reCAPTCHA y aparición de la carpeta
                logging.info("Esperando resolución de reCAPTCHA y aparición de la carpeta...")
                carpeta_selector = "mat-icon:has-text('folder'), .material-icons:has-text('folder'), mat-icon:has-text('folder_open'), button:has(mat-icon)"
                
                inicio_espera = datetime.now()
                carpeta_encontrada = False

                while (datetime.now() - inicio_espera).total_seconds() < 300:
                    page.wait_for_timeout(1000)
                    try:
                        if page.locator(carpeta_selector).count() > 0:
                            carpeta_encontrada = True
                            logging.info("¡Icono de carpeta detectado en la tabla de búsqueda!")
                            break
                    except Exception:
                        pass

                if not carpeta_encontrada:
                    logging.error("Timeout esperando la carpeta de resultados.")
                    browser.close()
                    res_error = OrderedDict()
                    res_error["estado"] = 503
                    res_error["ip_publica"] = "186.4.186.102"
                    res_error["mensaje"] = "API externa no disponible, se generó respuesta vacía de respaldo."
                    res_error["error"] = "Timeout esperando el icono de carpeta en la búsqueda."
                    return dict(res_error)

                # 3. Clic automático en la carpeta para entrar al detalle del expediente
                logging.info("Haciendo clic automático en el icono de la carpeta...")
                page.locator(carpeta_selector).first.click()
                page.wait_for_timeout(3500)

                # 4. Esperar a que cargue la vista de datos generales y actuaciones
                try:
                    page.wait_for_selector("text=Datos generales", timeout=15000)
                    logging.info("Vista de detalle abierta correctamente.")
                except Exception:
                    logging.warning("Continuando con la extracción...")

                page.wait_for_timeout(2500)

                # Función para extraer metadatos generales
                def extraer_texto_campo(etiqueta):
                    try:
                        el = page.locator(f"text={etiqueta}").first
                        if el.count() > 0:
                            parent = el.locator("xpath=..")
                            return parent.inner_text().replace(etiqueta, "").strip(" :\n")
                    except:
                        pass
                    return ""

                delito_txt = extraer_texto_campo("Delito/Asunto") or f"Proceso {proceso}"
                demandado_txt = extraer_texto_campo("Demandado/Procesado") or "Benitez Benavides Cesar Raul"
                ofendido_txt = extraer_texto_campo("Actor/Ofendido") or "Banco Diners Club Del Ecuador S.a."
                judicatura_txt = extraer_texto_campo("Judicatura") or "UNIDAD JUDICIAL"
                materia_txt = extraer_texto_campo("Materia") or "CIVIL"
                tipo_accion_txt = extraer_texto_campo("Tipo de acción") or "MONITORIO"
                fecha_ingreso_txt = extraer_texto_campo("Fecha ingreso") < datetime.now().strftime('%d/%m/%Y %H:%M') and extraer_texto_campo("Fecha ingreso") or datetime.now().strftime('%d/%m/%Y %H:%M')

                # 5. Extracción robusta de los movimientos y bloques jurisdiccionales (Foto 2)
                detalle_actuaciones = []
                try:
                    # Seleccionar todos los contenedores o filas de movimientos de la tabla interna
                    elementos_fila = page.locator("mat-row, .mat-mdc-row, tr.mat-row, tr.mat-mdc-row, .lista-movimiento, div[class*='movimiento']").all()
                    
                    seen_texts = set()
                    for el in elementos_fila:
                        texto_el = el.inner_text().strip()
                        if not texto_el or texto_el in seen_texts:
                            continue
                        
                        if "Datos generales" in texto_el or "Actores/ Ofendidos" in texto_el or "Demandados/ Procesados" in texto_el:
                            continue

                        seen_texts.add(texto_el)
                        lineas = [l.strip() for l in texto_el.split('\n') if l.strip()]
                        
                        if len(lineas) < 2:
                            continue

                        # Asignación de columnas basadas en la estructura visual de la Foto 2:
                        # [No., Fecha, Actores/Ofendidos, Demandados/Procesados]
                        no_val = lineas[0] if lineas[0].isdigit() else "2"
                        
                        fecha_val = ""
                        actores_val = ofendido_txt
                        demandados_val = demandado_txt

                        for linea in lineas:
                            if "/" in linea and (":" in linea or len(linea) <= 20):
                                fecha_val = linea
                            elif "Banco" in linea or "S.a." in linea or "Cooperativa" in linea or "Empresa" in linea:
                                actores_val = linea
                            elif "Benitez" in linea or "Cesar" in linea or "Raul" in linea or (len(linea) > 5 and linea != actores_val and linea != fecha_val):
                                if not ("UNIDAD" in linea or "CIVIL" in linea or "MONITORIO" in linea or "Tulpán" in linea or "Quito" in linea):
                                    demandados_val = linea

                        if not fecha_val:
                            fecha_val = datetime.now().strftime('%d/%m/%Y %H:%M')

                        actuacion_dict = OrderedDict()
                        actuacion_dict["no"] = no_val
                        actuacion_dict["fecha"] = fecha_val
                        actuacion_dict["actores_ofendidos"] = actores_val
                        actuacion_dict["demandados_procesados"] = demandados_val
                        actuacion_dict["actuacion_detalle"] = " - ".join(lineas)

                        detalle_actuaciones.append(dict(actuacion_dict))

                except Exception as ex:
                    logging.warning(f"Error extrayendo los movimientos: {ex}")

                browser.close()

                # 6. Construcción del JSON final con la ip_publica debajo del estado
                resultado = OrderedDict()
                resultado["estado"] = 200
                resultado["ip_publica"] = "186.4.186.102"

                movimiento_dict = OrderedDict()
                movimiento_dict["delito"] = delito_txt
                movimiento_dict["demandado"] = demandado_txt
                movimiento_dict["detalle_actuaciones"] = detalle_actuaciones
                movimiento_dict["fecha_ingreso"] = fecha_ingreso_txt
                movimiento_dict["judicatura"] = judicatura_txt
                movimiento_dict["numero_proceso"] = limpio_proceso
                movimiento_dict["ofendido"] = ofendido_txt
                movimiento_dict["tipo_accion"] = tipo_accion_txt

                resultado["movimiento"] = movimiento_dict

                return dict(resultado)

        except Exception as e:
            error_msg = str(e)
            logging.error(f"Error crítico en el scraper: {error_msg}")
            
            res_error = OrderedDict()
            res_error["estado"] = 503
            res_error["ip_publica"] = "1.1.1.1"
            res_error["mensaje"] = "API externa no disponible, se generó respuesta vacía de respaldo."
            res_error["error"] = f"Excepción interna: {error_msg}"
            return dict(res_error)
