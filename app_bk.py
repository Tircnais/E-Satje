from urllib.request import Request
from flask import Flask, flash, session, abort, request, jsonify, render_template, url_for, redirect
# render_template, para el renderizado a VIEW (hmtl)
import pyodbc
#import pymssql
import ujson as json
import os
import requests
import json
import re
from datetime import date, datetime, timedelta

# encriptacion y desencriptacion
from Crypto.Cipher import AES
from Crypto.Random import get_random_bytes
from Crypto.Util.Padding import pad, unpad
import base64

# session
from flask_session import Session

# carga y manejo de archivos
from openpyxl import load_workbook
from openpyxl.utils.dataframe import dataframe_to_rows
from openpyxl.utils.exceptions import InvalidFileException
import pandas as pd



app = Flask(__name__)
# Configuración para manejar archivos estáticos
app.static_folder = 'static'
app.config['SECRET_KEY'] = 'ff1ca3b075d337b5aecb91355657b691'
# Config. session
app.config['SESSION_TYPE'] = 'filesystem'
# Configura la carpeta de carga de archivos
UPLOAD_FOLDER = 'archivos'
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

Session(app)

def encriptar_clave(clave):
    try:
        # Genera una clave de cifrado, una sola vez y guárdala de forma segura
        key = b'\xad\xfeK~\xd91H\xdf\xa2\xfeB\x08Z\x98\xa1+'
        # Crea un objeto AES con la clave y el modo ECB
        cipher = AES.new(key, AES.MODE_ECB)
        # Asegúrate de que el mensaje tenga un tamaño múltiplo de 16 (bloque AES)
        message = pad(clave.encode('utf-8'), 16)
        # Cifra el mensaje con el modo ECB
        clave_encriptada = cipher.encrypt(message)
        # Convierte la salida en una cadena antes de devolverla
        return base64.b64encode(clave_encriptada).decode('utf-8')
    except Exception as ex:
        # Manejo de excepciones en caso de error
        return "Eror al encriptar: ".str(ex)

def desencriptar_clave(clave_encriptada):
    #clave_encriptada = b"'"+ clave_encriptada +"'"
    key = b'\xad\xfeK~\xd91H\xdf\xa2\xfeB\x08Z\x98\xa1+'
    # Para descifrar, simplemente utiliza el mismo IV y clave
    decipher = AES.new(key, AES.MODE_ECB)
    clave_desencriptada = unpad(decipher.decrypt(clave_encriptada), 16).decode('utf-8')
    return clave_desencriptada

def connection():
    conn = ""
    try:
        # conn = pyodbc.connect('DRIVER={SQL Server};SERVER=Cristian;DATABASE=Juicios;UID=sa;PWD=gscjudicial')
        s = 'Cristian' #Your server name 
        d = 'Juicios' # Database
        u = 'sa' #Your login
        p = 'gscjudicial' #Your login password
        cstr = 'DRIVER={SQL Server};SERVER='+s+';DATABASE='+d+';UID='+u+';PWD='+ p
        conn = pyodbc.connect(cstr)
    except Exception as ex:
        print(f"Error al establecer la conexion DB: { ex }")
    return conn


def ejecutaProcedimiento(nombre, lista):
    listado = []
    try:
        conn = connection()
        cursor = conn.cursor()
        # print("Consulta exitosa")
        # Puedes desempaquetarla en tres variables
        iduser = session.get('userid')
        # print("Consulta exitosa")
        if (nombre == 'InsertarCliente') :
            variable1, variable2, variable3, variable4 = lista
            sentencia = "EXEC " + nombre + " '" + variable1 + "', '" + variable2 + "', '" + variable3 + "', '" + variable4 + "', " + str(iduser) + ";"
            # print(f'Sentencia A: {sentencia}')
            callbacks = cursor.execute(sentencia)
            
            if callbacks is not None:
                column_names = [column[0] for column in callbacks.description]  # Obtiene los nombres de las columnas
                for elemento in callbacks:
                    data = dict(zip(column_names, elemento))
                    # print(f"Tipo {type(data)} Tam.: {len(data)} Valor: {data}")
                    listado.append(data)  
        elif (nombre ==  'InsertarDeprecatorio'):
            variable1, variable2, variable3, variable4, variable5, variable6, variable7, variable8 = lista
            sentencia = "EXEC " + nombre + " '" + variable1 + "', '" + variable2 + "', '" + variable3 + "', '" + variable4 + "', '" + variable5 + "', '" + variable6 + "', '" + variable7 + "', '" + variable8 + "', " + str(iduser) + ";"
            # print(f'Sentencia B: {sentencia}')
            callbacks = cursor.execute(sentencia)
            
            column_names = [column[0] for column in callbacks.description]  # Obtiene los nombres de las columnas
            for elemento in callbacks:
                data = dict(zip(column_names, elemento))
                # print(f"Tipo {type(data)} Tam.: {len(data)} Valor: {data}")
                listado.append(data)
        elif (nombre ==  'InsertarDetalle'):
            variable1, variable2, variable3, variable4, variable5, variable6, variable7 = lista
            sentencia = "EXEC " + nombre + " '" + variable1 + "', '" + variable2 + "', '" + variable3 + "', '" + variable4 + "', '" + variable5 + "', '" + variable6 + "', '" + variable7 + "', " + str(iduser) + ";"
            # print(f'Sentencia C: {sentencia}')
            callbacks = cursor.execute(sentencia)
            
            column_names = [column[0] for column in callbacks.description]  # Obtiene los nombres de las columnas
            for elemento in callbacks:
                data = dict(zip(column_names, elemento))
                # print(f"Tipo {type(data)} Tam.: {len(data)} Valor: {data}")
                listado.append(data)
        elif (nombre == 'InsertarActualizaCliente') :
            variable1, variable2, variable3, variable4 = lista
            sentencia = "EXEC " + nombre + " '" + variable1 + "', '" + variable2 + "', '" + variable3 + "', '" + variable4 + "', " + str(iduser) + ";"
            # print(f'Sentencia D: {sentencia}')
            callbacks = cursor.execute(sentencia)
            
            if callbacks is not None:
                column_names = [column[0] for column in callbacks.description]  # Obtiene los nombres de las columnas
                for elemento in callbacks:
                    data = dict(zip(column_names, elemento))
                    # print(f"Tipo {type(data)} Tam.: {len(data)} Valor: {data}")
                    listado.append(data)  
        elif (nombre ==  'InsertarActualizaDeprecatorio'):
            variable1, variable2, variable3, variable4, variable5, variable6, variable7, variable8 = lista
            sentencia = "EXEC " + nombre + " '" + variable1 + "', '" + variable2 + "', '" + variable3 + "', '" + variable4 + "', '" + variable5 + "', '" + variable6 + "', '" + variable7 + "', '" + variable8 + "', " + str(iduser) + ";"
            # print(f'Sentencia E: {sentencia}')
            callbacks = cursor.execute(sentencia)
            
            column_names = [column[0] for column in callbacks.description]  # Obtiene los nombres de las columnas
            for elemento in callbacks:
                data = dict(zip(column_names, elemento))
                # print(f"Tipo {type(data)} Tam.: {len(data)} Valor: {data}")
                listado.append(data)
        elif (nombre ==  'InsertarActualizaDetalle'):
            variable1, variable2, variable3, variable4, variable5, variable6, variable7 = lista
            sentencia = "EXEC " + nombre + " '" + variable1 + "', '" + variable2 + "', '" + variable3 + "', '" + variable4 + "', '" + variable5 + "', '" + variable6 + "', '" + variable7 + "', " + str(iduser) + ";"
            # print(f'Sentencia f: {sentencia}')
            callbacks = cursor.execute(sentencia)
            
            column_names = [column[0] for column in callbacks.description]  # Obtiene los nombres de las columnas
            for elemento in callbacks:
                data = dict(zip(column_names, elemento))
                # print(f"Tipo {type(data)} Tam.: {len(data)} Valor: {data}")
                listado.append(data)
        elif (nombre == 'InsertarCarga'):
            # cedente, cedula, numproceso, cuenta, nombres, tipo, fecha_actuacion, etapa1, etapa2, etapa3, observaciones, iduser
            # InsertarCarga cedente, cedula, numproceso, cuenta, nombres, tipo, fecha_actuacion, etapa1, etapa2, etapa3, observaciones, iduser
            # Asegúrate de que la lista tenga al menos 11 elementos
            if len(lista) == 12:
                variable1, variable2, variable3, variable4, variable5, variable6, variable7, variable8, variable9, variable10, variable11, variable12 = lista
                sentencia = f"EXEC {nombre} '{variable1}', '{variable2}', '{variable3}', '{variable4}', '{variable5}', '{variable6}', '{variable7}', '{variable8}', '{variable9}', '{variable10}', '{variable11}', '{variable12}', {str(iduser)};"
                #sentencia = "EXEC " + nombre + " '" + variable1 + "', '" + variable2 + "', '" + variable3 + "', '" + variable4 + "', '" + variable5 + "', '" + variable6 + "', '" + variable7 + "', '" + variable8 + "', '" + variable9 + "', '" + variable10 + "', '" + variable11 + "', " + str(iduser) + ";"
                print(f'Sentencia G: {sentencia}')
                callbacks = cursor.execute(sentencia)
                
                column_names = [column[0] for column in callbacks.description]  # Obtiene los nombres de las columnas
                for elemento in callbacks:
                    data = dict(zip(column_names, elemento))
                    # print(f"Tipo {type(data)} Tam.: {len(data)} Valor: {data}")
                    listado.append(data)
            else:
                print("La lista no tiene suficientes elementos.")
        elif (nombre == 'ActualizaCarga'):
            # cedente, cedula, numproceso, cuenta, nombres, tipo, fecha_actuacion, etapa1, etapa2, etapa3, observaciones, iduser
            # InsertarCarga cedente, cedula, numproceso, cuenta, nombres, tipo, fecha_actuacion, etapa1, etapa2, etapa3, observaciones, iduser
            # Asegúrate de que la lista tenga al menos 11 elementos
            if len(lista) == 12:
                variable1, variable2, variable3, variable4, variable5, variable6, variable7, variable8, variable9, variable10, variable11, variable12 = lista
                sentencia = f"EXEC {nombre} '{variable1}', '{variable2}', '{variable3}', '{variable4}', '{variable5}', '{variable6}', '{variable7}', '{variable8}', '{variable9}', '{variable10}', '{variable11}', '{variable12}', {str(iduser)};"
                #sentencia = "EXEC " + nombre + " '" + variable1 + "', '" + variable2 + "', '" + variable3 + "', '" + variable4 + "', '" + variable5 + "', '" + variable6 + "', '" + variable7 + "', '" + variable8 + "', '" + variable9 + "', '" + variable10 + "', '" + variable11 + "', " + str(iduser) + ";"
                print(f'Sentencia H: {sentencia}')
                callbacks = cursor.execute(sentencia)
                
                column_names = [column[0] for column in callbacks.description]  # Obtiene los nombres de las columnas
                for elemento in callbacks:
                    data = dict(zip(column_names, elemento))
                    # print(f"Tipo {type(data)} Tam.: {len(data)} Valor: {data}")
                    listado.append(data)
            else:
                print("La lista no tiene suficientes elementos.")
        elif (nombre == 'InsertarPaleta'):
            if len(lista) == 6:
                variable1, variable2, variable3, variable4, variable5, variable6 = lista
                sentencia = f"EXEC {nombre} '{variable1}', '{variable2}', '{variable3}', '{variable4}', '{variable5}', '{variable6}', {str(iduser)};"
                #sentencia = "EXEC " + nombre + " '" + variable1 + "', '" + variable2 + "', '" + variable3 + "', '" + variable4 + "', '" + variable5 + "', '" + variable6 + "', '" + variable7 + "', '" + variable8 + "', '" + variable9 + "', '" + variable10 + "', '" + variable11 + "', " + str(iduser) + ";"
                # print(f'Sentencia I: {sentencia}')
                callbacks = cursor.execute(sentencia)
                
                column_names = [column[0] for column in callbacks.description]  # Obtiene los nombres de las columnas
                for elemento in callbacks:
                    data = dict(zip(column_names, elemento))
                    # print(f"Tipo {type(data)} Tam.: {len(data)} Valor: {data}")
                    listado.append(data)
            else:
                print("La lista no tiene suficientes elementos.")
        else:
            variable1, variable2, variable3, variable4, variable5, variable6, variable7 = lista
            sentencia = "EXEC " + nombre + " '" + variable1 + "', '" + variable2 + "', '" + variable3 + "', '" + variable4 + "', '" + variable5 + "', '" + variable6 + "', '" + variable7 + "', " + str(iduser) + ";"
            print(f'Sentencia J: {sentencia}')
            callbacks = cursor.execute(sentencia)

            column_names = [column[0] for column in callbacks.description]  # Obtiene los nombres de las columnas
            for elemento in callbacks:
                data = dict(zip(column_names, elemento))
                # print(f"Tipo {type(data)} Tam.: {len(data)} Valor: {data}")
                listado.append(data)
        cursor.commit()
        cursor.close()
        conn.close()        
    except Exception as ex:
        sqlstate = ex.args[0]
        errormessage = ex
        # print(f"Error de conexión SQL Server (SQLState: {sqlstate}): {errormessage}")
        diccionario = {"state": sqlstate, "error": errormessage}
        listado.append(diccionario)
    return listado

@app.route('/ver_detalle/<int:id>')
def ver_detalle(id):
    # Aquí debes consultar tu base de datos o fuente de datos para obtener el detalle del registro con el ID proporcionado.
    # Luego, puedes pasar esos datos a tu plantilla HTML de detalles.
    # print("Det.Entro")
    listado = []
    try:
        conn = connection()
        cursor = conn.cursor()
        # print(f"Tipo {type(id)} Valor: {id}")
        #sentencia = "EXEC ListarDeprecatorios ?"
        sentencia = "EXEC ListarDeprecatorios " + str(id) + ";"
        #parametros = (id) # parametro1, parametro2
        # print(sentencia)
        #print(sentencia, parametros)
        #callbacks = conn.execute(sentencia)
        #cursor.execute(sentencia, parametros)
        cursor.execute(sentencia)
        
        # Como hemos modificado el procedimiento almacenado para devolver un conjunto de resultados, ahora podemos usar fetchall().
        results = cursor.fetchall()
        
        if results:
            column_names = [column[0] for column in cursor.description]
            # print("column_names", column_names)
            #listado.append(column_names)
            for row in results:
                data = dict(zip(column_names, row))
                # print(f"Tipo {type(data)} Tam.: {len(data)} Valor: {data}")
                listado.append(data)
        # else:
            # print("La consulta no retornó resultados.")

        cursor.close()
        conn.close()
    except Exception as ex:
        print(f"Error al consultar el detalle: { ex }")

    datos = {
        'title': 'Detalle del proceso',
        'listado': listado
    }
    return render_template('detalleproceso.html', datos=datos)

# funcion para obtener datos
def getProcesos(nombresp):
    dic = {}
    listado = []
    try:
        conn = connection()
        cursor = conn.cursor()
        # print("Consulta exitosa")
        callbacks = cursor.execute('EXEC '+ nombresp)
        column_names = [column[0] for column in callbacks.description]  # Obtiene los nombres de las columnas
        #print(f'column_names: {column_names}')
        dic = {'column_names': column_names}
        for elemento in callbacks:
            data = dict(zip(column_names, elemento))
            # print(f"Tipo {type(data)} Tam.: {len(data)} Valor: {data}")
            listado.append(data)
        dic = {'datos': listado}
        cursor.close()
        conn.close()
    except Exception as ex:
        print(f"Error al consultar procesos a DB: { ex }")
    return dic

# presenta la info recuperada usando AJAX para visualizar en tiempo real
@app.route('/data', methods=['GET'])
def get_data():
    # Lógica para obtener datos de la base de datos
    listado = getProcesos("ListarClientes")
    return jsonify(listado)

@app.route('/dataCtas', methods=['GET'])
def get_dataCtas():
    # Lógica para obtener datos de la base de datos
    listado = getProcesos("ListaCuentas")
    return jsonify(listado)

# presentar el index
@app.route('/dashboard')
def dashboard():
    datos = {
        'title': 'PANEL'
    }
    return render_template('dashboard.html', datos=datos)

@app.route('/dudas')
def dudas():
    datos = {
        'title': 'Preguntas recuentas'
    }
    return render_template('pages-faq.html', datos=datos)

# presentar el index
@app.route('/index')
def index():
    datos = {
        'title': 'Extracción E-SATJE'
    }
    return render_template('index.html', datos=datos)

# presentar el index
@app.route('/procesos')
def procesos():
    listado = getProcesos("ListarClientes")
    datos = {
        'title': 'Procesos',
        'listado': listado
    }
    return render_template('procesos.html', datos=datos)

# MODULO DE CARGAS - CUENTAS (PROCESOS)
@app.route('/cargamasiva')
def cargamasiva():
    datos = {
        # 'title': 'Modulo de carga másiva.',
        'title': 'Modulo de carga másiva. TRABAJANDO (NO DISPINIBLE).....',
    }
    datos['mensaje'] = "Seleccione un archivo."
    return render_template('cargacuentas.html', datos=datos)

# VERIFICACION DEL FORMATO PARA CARGA - CUENTAS
def check_sheet_and_columns(sheet):
    # Verifica si la hoja se llama "Hoja 1" o "Sheet 1"
    if sheet.title not in ["Hoja1", "Sheet1"]:
        return False

    # Verifica que las columnas tengan los nombres deseados
    expected_columns = []
    expected_columns.append("cedente")
    expected_columns.append("cedula")
    expected_columns.append("proceso")
    expected_columns.append("procedimiento")
    expected_columns.append("cuenta")
    expected_columns.append("fecha_satje")
    expected_columns.append("observaciones")
    # print("valores: ", zip(sheet.iter_rows(min_row=1, max_row=1, values_only=True)))
    
    for cell_value in zip(sheet.iter_rows(min_row=1, max_row=1, values_only=True)):
        # Convertir todos los valores a minúsculas
        column_name = tuple(tuple(valor.lower() for valor in sub_tupla) for sub_tupla in cell_value)
        print(f"Valores de la cabecera {column_name} {expected_columns}")
        # Convertir a conjuntos y comparar
        conjunto_a = set(column_name[0])
        conjunto_b = set(expected_columns)
        if conjunto_a == conjunto_b:
            print("Los conjuntos son iguales")
            return False
        else:
            return True

# SUBIDA DEL ARCHIVO AL SISTEMA
@app.route('/cargar_archivo', methods=['POST'])
def cargar_archivo():
    respuesta = ""
    print('Ingreso')
    archivo = ""
    # Verifica si se ha proporcionado un archivo
    if 'archivo' not in request.files:
        respuesta = "No se ha proporcionado un archivo"

    archivo = request.files['archivo']

    # Verifica si se proporciona un archivo y si el nombre del archivo no está vacío
    if archivo and archivo.filename != '':
        # Aquí puedes trabajar con el archivo, por ejemplo, guardarlo en una carpeta
        # archivo.save('archivos/carga' + archivo.filename)
        respuesta = 'Archivo guardado con éxito.'

    else:
        respuesta = 'Nombre de archivo vacío.'

    if archivo and archivo.filename.endswith('.xlsx'):
        # Guarda el archivo en la carpeta de archivos
        archivo.save(os.path.join(app.config['UPLOAD_FOLDER'] + "/carga", archivo.filename))
        # Abre el archivo Excel
        workbook = load_workbook(os.path.join(app.config['UPLOAD_FOLDER'] + "/carga", archivo.filename))
        sheet = workbook.active
        if check_sheet_and_columns(sheet):
            # Lee los datos del archivo
            data = list(dataframe_to_rows(pd.DataFrame(sheet.values), index=True, header=True))
            # print(f"Datos {data}")

            # Itera a través de las filas del archivo Excel
            for row in sheet.iter_rows(values_only=True):
                # CEDENTE, CEDULA, PROCESO, CUENTA, NOMBRE , PROCEDIMIENTO, FECHA_SATJE, DIAS_ TRANS_SATJE, FECHA_SATJE, ETAPA 1, ETAPA 2, ETAPA 3, OBSERVACIONES
                cedente, cedula, num_proceso, cuenta, nombre, tipo_juicio, fechasatje, dias, etapa1, etapa2, etapa3, observaciones, observacionesAud = row
                try:
                    if fechasatje is None:
                        fechasatje = '1990-01-01' 
                    if isinstance(fechasatje, (date, datetime)):
                        # print("La variable es de tipo date o datetime.")
                        # Convierte la fecha a una cadena con formato 'YYYY-MM-DD'
                        fechasatje = fechasatje.strftime('%Y-%m-%d')
                    elif fechasatje.isdigit():
                        # print("La variable contiene solo dígitos.")
                        fechasatje = int(fechasatje)
                        # Fecha base (puedes ajustarla según tus necesidades)
                        fecha_base = datetime(1900, 1, 1)
                        # Convertir el número de días a un objeto datetime
                        fecha_resultante = fecha_base + timedelta(days=fechasatje)
                        # Formatear la fecha según 'dd/mm/yyyy'
                        #formato_fecha_dd_mm_yyyy = fecha_resultante.strftime('%d/%m/%Y')
                        #print("Fecha en formato 'dd/mm/yyyy':", formato_fecha_dd_mm_yyyy)
                        # Formatear la fecha según 'yyyy-mm-dd'
                        formato_fecha_yyyy_mm_dd = fecha_resultante.strftime('%Y-%m-%d')
                        print("Fecha en formato 'yyyy-mm-dd':", formato_fecha_yyyy_mm_dd)
                        fechasatje = formato_fecha_yyyy_mm_dd
                        # print(f"La cadena '{fechasatje}' se convirtió a un entero: {fechasatje}")
                    else:
                        fechasatje = '1990-01-01'
                        # print("La variable contiene caracteres que no son dígitos.")
                except ValueError as e:
                    fechasatje = '1990-01-01'
                    print(f"Error al convertir la cadena a entero: {e}")

                if (etapa1 is None):
                    etapa1 = ''
                if (etapa2 is None):
                    etapa2 = ''
                if (etapa3 is None):
                    etapa3 = ''
                if (observaciones is None):
                    observaciones = ''
                if (observacionesAud is None):
                    observacionesAud = ''

                num_proceso = num_proceso.replace("-", "")
                parametrosCarga = []
                parametrosCarga.append(cedente)
                parametrosCarga.append(cedula)
                parametrosCarga.append(num_proceso)
                parametrosCarga.append(cuenta)
                parametrosCarga.append(nombre)
                parametrosCarga.append(tipo_juicio)
                parametrosCarga.append(fechasatje)
                parametrosCarga.append(etapa1)
                parametrosCarga.append(etapa2)
                parametrosCarga.append(etapa3)
                parametrosCarga.append(observaciones)
                parametrosCarga.append(observacionesAud)
                # print(f'Lista de argumentos: {parametrosCarga} Tam {len(parametrosCarga)}')
                # InsertarCarga cedente, cedula, numproceso, cuenta, nombres, tipo, fecha_actuacion, etapa1, etapa2, etapa3, observaciones, iduser
                resultado = ejecutaProcedimiento('InsertarCarga', parametrosCarga)
                print(f'Resultado Carga cuentas: {resultado}')
                if (resultado[0]['Resultado'] == "1" or resultado[0]['Resultado'] == "2"):
                    respuesta = "Leyendo el archivo"
                    #print(respuesta)

                    # Llama a los metodos de consulta, para consultar masivamente
                    if (num_proceso.isdigit()):
                        # consulta el API retorno el JSON o el error contemplado
                        datosApiJson = consultaAPI(num_proceso)
                        # retorno el nombre del archivo o un mensaje de error
                        archivoJson = guardaArchivo(datosApiJson)
                        # Puedes acceder a los datos en el objeto JSON de respuesta
                        if "error" in archivoJson.lower():
                            # print("La palabra 'Error' no está en el texto.")
                            respuesta = f'No se pudo  el número de proceso {num_proceso}.' + archivoJson
                        else:
                            # print("La palabra 'Error' está en el texto.")
                            # Itera a través de las claves (nombres de campo) y valores en el JSON
                            respuesta = leeJsonProceso(archivoJson)
                            if ("error" not in respuesta.lower()):
                                parametrosCarga = []
                                parametrosCarga.append(cedente)
                                parametrosCarga.append(cedula)
                                parametrosCarga.append(num_proceso)
                                parametrosCarga.append(cuenta)
                                parametrosCarga.append(nombre)
                                parametrosCarga.append(tipo_juicio)
                                parametrosCarga.append(fechasatje)
                                parametrosCarga.append(etapa1)
                                parametrosCarga.append(etapa2)
                                parametrosCarga.append(etapa3)
                                parametrosCarga.append(observaciones)
                                parametrosCarga.append(observacionesAud)
                                resultado = ejecutaProcedimiento('ActualizaCarga', parametrosCarga)
                                respuesta = leeJsonProceso(archivoJson)
                else:
                    respuesta = "Error"
                    #print(resultado)
            # Los datos ahora están en la variable 'data' y cumplen con los requisitos
            # AKI llamar al proceso para consulta y guardado del juicio
        else:
            flash("El nombre de la hoja o las columnas no son válidas.", 'error')
            respuesta = 'El nombre de la hoja o el formato no es valido.'
    else:
        respuesta = 'Extensión de archivo no válida. Debe ser un archivo Excel (.xlsx).'
            
    dicResp = {"salida" : respuesta}
    print(f'Resultado del proceso {dicResp}')
    return dicResp

# MODULO DE CARGAS - PALETA
@app.route('/cargapaleta')
def cargapaleta():
    datos = {
        # 'title': 'Modulo de carga másiva.',
        'title': 'Modulo de carga de la paleta',
    }
    datos['mensaje'] = "Seleccione un archivo."
    return render_template('cargapaleta.html', datos=datos)

# VALIDA FORMATA CARGA PALETA
def check_sheet_and_columns_paleta(sheet):
    # Verifica si la hoja se llama "Hoja 1" o "Sheet 1"
    if sheet.title not in ["Hoja1", "Sheet1"]:
        return False

    # Verifica que las columnas tengan los nombres deseados
    expected_columns = []
    expected_columns.append("etapa")
    expected_columns.append("respuesta")
    expected_columns.append("glosario")
    expected_columns.append("v")
    expected_columns.append("a")
    expected_columns.append("r")
    # print("valores: ", zip(sheet.iter_rows(min_row=1, max_row=1, values_only=True)))
    
    for cell_value in zip(sheet.iter_rows(min_row=1, max_row=1, values_only=True)):
        # Convertir todos los valores a minúsculas
        column_name = tuple(tuple(valor.lower() for valor in sub_tupla) for sub_tupla in cell_value)
        print(f"Valores de la cabecera {column_name} {expected_columns}")
        # Convertir a conjuntos y comparar
        conjunto_a = set(column_name[0])
        conjunto_b = set(expected_columns)
        if conjunto_a == conjunto_b:
            print("Los conjuntos son iguales")
            return True
        else:
            print("Los conjuntos no son iguales")
            return False

# SUBIDA DEL ARCHIVO AL SISTEMA
@app.route('/cargar_paleta', methods=['POST'])
def cargar_pelta():
    respuesta = ""
    print('Ingreso')
    archivo = ""
    # Verifica si se ha proporcionado un archivo
    if 'archivo' not in request.files:
        respuesta = "No se ha proporcionado un archivo"

    archivo = request.files['archivopaleta']

    # Verifica si se proporciona un archivo y si el nombre del archivo no está vacío
    if archivo and archivo.filename != '':
        # Aquí puedes trabajar con el archivo, por ejemplo, guardarlo en una carpeta
        # archivo.save('archivos/carga' + archivo.filename)
        respuesta = 'Archivo guardado con éxito.'

    else:
        respuesta = 'Nombre de archivo vacío.'

    if archivo and archivo.filename.endswith('.xlsx'):
        # Guarda el archivo en la carpeta de archivos
        archivo.save(os.path.join(app.config['UPLOAD_FOLDER'] + "/paleta", archivo.filename))
        # Abre el archivo Excel
        workbook = load_workbook(os.path.join(app.config['UPLOAD_FOLDER'] + "/paleta", archivo.filename))
        sheet = workbook.active
        if check_sheet_and_columns_paleta(sheet):
            # Lee los datos del archivo
            data = list(dataframe_to_rows(pd.DataFrame(sheet.values), index=True, header=True))
            # print(f"Datos {data}")

            # Itera a través de las filas del archivo Excel
            for row in sheet.iter_rows(values_only=True):
                # ETAPA	RESPUESTA	GLOSARIO (ACTUACIÓN SATJE)	V	A	R
                etapa, respuesta, glosario, tiempo1, tiempo2, tiempo3 = row
                if (tiempo1 is None):
                    tiempo1 = 0
                if (tiempo2 is None):
                    tiempo2 = 0
                if (tiempo3 is None):
                    tiempo3 = 0
                
                parametrosCarga = []
                parametrosCarga.append(etapa)
                parametrosCarga.append(respuesta)
                parametrosCarga.append(glosario)
                parametrosCarga.append(tiempo1)
                parametrosCarga.append(tiempo2)
                parametrosCarga.append(tiempo3)
                # print(f'Lista de argumentos: {parametrosCarga} Tam {len(parametrosCarga)}')
                if (type(tiempo1) == int and type(tiempo2) == int and type(tiempo3) == int):
                    resultado = ejecutaProcedimiento('InsertarPaleta', parametrosCarga)
                    # print(f'Resultado Carga paleta: {resultado}')
                    if (resultado[0]['Resultado'] == "1" or resultado[0]['Resultado'] == "2"):
                        respuesta = "Cargando paleta"
                    else:
                        respuesta = "No cargado"
                else:
                    respuesta = "Error"
                    #print(resultado)
            if (respuesta == 'Cargando paleta'):
                respuesta= 'Paleta cargada'
            # Los datos ahora están en la variable 'data' y cumplen con los requisitos
            # AKI llamar al proceso para consulta y guardado del juicio
        else:
            flash("El nombre de la hoja o las columnas no son válidas.", 'error')
            respuesta = 'El nombre de la hoja o el formato no es valido.'
    else:
        respuesta = 'Extensión de archivo no válida. Debe ser un archivo Excel (.xlsx).'
            
    dicResp = {"salida" : respuesta}
    print(f'Resultado del proceso {dicResp}')
    return jsonify(dicResp)

def consultaAPI(numeroproceso):
    """Esta funcion consulta el API proporcionada y retorna un JSON usando el numero de proceso

    Args:
        numeroproceso (str): Numero de proceso sin guiones

    Returns:
        respone: Retorno un respone que de ser tratado como un JSON
    """
    response = ""
    try:
        url = f'http://186.3.198.68:89/ApirestProcesosJudicialesJSON?url={numeroproceso}'
        response = requests.get(url)
        # print(f'API {url}')
        # print(f'Consultando {numeroproceso}')
    except requests.exceptions.RequestException as e:
        # Maneja excepciones en caso de errores de solicitud
        mensaje = f'Error de solicitud: {e}'
        response = mensaje
        # print(mensaje)
    return response

def guardaArchivo(response):
    # TODO Probar otro codigo, genera un error pesé a guardar el archivo, aunque lee el archivo que se guarda, no el del almacenamiento
    salida = ""
    try:
        # Verifica si la solicitud fue exitosa
        if response.status_code == 200:
            # La respuesta es un objeto JSON, puedes obtener sus datos así:
            datos_json = response.json()
            # guarda el json
            fecha_sistema_arch = datetime.today().strftime('%d-%m-%Y_%H%M') #formato dd-mm-yyyy_HHMM
            numproceso = datos_json[0]['movimiento']['numero_proceso']
            archivoJson = numproceso + "_" + fecha_sistema_arch + ".json"
            # archivoJson = numproceso + ".json"
            archivo_pdf_path = os.path.join('archivos/json', archivoJson)
            with open(archivo_pdf_path, 'w') as archivo:
                # Escribir el diccionario en formato JSON en el archivo
                json.dump(datos_json, archivo)
            salida = archivoJson
            print(f"JSON de {numproceso} guardado")
        else:
            # En caso de un código de estado no exitoso, puedes manejarlo aquí
            salida = f'Error. Solicitud fallida al API (código de estado): {response.status_code}'
    except IOError as e:
        # Manejar la excepción específica relacionada con la escritura del archivo
        salida = f"Error de escritura en el archivo JSON: {e}"
        # print(salida) 
    except Exception as e:
        # Manejar otras excepciones
        salida = f"Error al guardar el archivo JSON: {e}"
        # print(salida) 
    return salida

def leeJsonProceso(nombreArchJson):
    respuesta = ""
    print(f'Archivo a leer: archivos/json/{nombreArchJson}')
    with open('archivos/json/' + nombreArchJson) as procesoJson:
        datos = json.load(procesoJson)
        for elemento in datos:
            #print(f"Elemento: {elemento}")
            cedula = ''
            no_obligacion = ''
            movimiento = elemento['movimiento']
            delito = movimiento['delito']
            demandado = movimiento['demandado']
            detalle_actuaciones = movimiento['detalle_actuaciones']
            fecha_ingreso = movimiento['fecha_ingreso']
            judicatura = movimiento['judicatura']
            materia = movimiento['materia']
            numero_proceso = movimiento['numero_proceso']
            ofendido = movimiento['ofendido']
            tipo_accion = movimiento['tipo_accion']
            # Convierte la fecha en el formato correcto para SQL Server
            fecha_ingresoS = datetime.strptime(fecha_ingreso, '%d/%m/%Y %H:%M').strftime('%Y-%m-%d %H:%M:%S.%f')[:-3]
            # print(f"Delito: {delito}")
            # print(f"Demandado: {demandado}")
            # print(f"Fecha de Ingreso: {fecha_ingresoS}")
            # print(f"Judicatura: {judicatura}")
            # print(f"Materia: {materia}")
            print(f"Número de Proceso: {numero_proceso}")
            # print(f"Ofendido: {ofendido}")
            # print(f"Tipo de Acción: {tipo_accion}")

            # Puedes agregar cualquier otro procesamiento que desees aquí
            # @cedula VARCHAR(15), @nombres VARCHAR(255), @no_obligacion VARCHAR(100), @numproceso VARCHAR(20)
            parametrosCliente = []
            parametrosCliente.append(cedula)
            parametrosCliente.append(demandado)
            parametrosCliente.append(no_obligacion)
            parametrosCliente.append(numero_proceso)
            resultado = ejecutaProcedimiento('InsertarActualizaCliente', parametrosCliente)
            print(f'Resultado Cliente {resultado}')
            # inserta/actualiza los deprecatorios
            if (resultado[0]['Resultado'] == 1 or resultado[0]['Resultado'] == 2):
                # {'Resultado': 2}
                respuesta = "Registro/Actualización del demandado realizado"
                # print(respuesta)

                # se insertan el deprecatorio
                # InsertarDeprecatorio
                # @numproceso VARCHAR(20), @demandado VARCHAR(255), @ofendido VARCHAR(255), @delito VARCHAR(255),
                # @fecha_ingreso DATETIME, @judicatura VARCHAR(255), @materia VARCHAR(255), @tipoaccion VARCHAR(255)
                parametrosDeprecatorio = []
                parametrosDeprecatorio.append(numero_proceso)
                parametrosDeprecatorio.append(demandado)
                parametrosDeprecatorio.append(ofendido)
                parametrosDeprecatorio.append(delito)
                parametrosDeprecatorio.append(fecha_ingresoS)
                parametrosDeprecatorio.append(judicatura)
                parametrosDeprecatorio.append(materia)
                parametrosDeprecatorio.append(tipo_accion)
                resultado = ejecutaProcedimiento('InsertarDeprecatorio', parametrosDeprecatorio)
                print(f'Resultado Deprecatorio {resultado}')
                
                # inserta/actualiza el detalle de actuaciones
                if (resultado[0]['Resultado'] == '1' or resultado[0]['Resultado'] == '2'):
                    respuesta = "Registra/Actualiza el deprecatorio"
                    for actuacion in detalle_actuaciones:
                        actuar = actuacion['actuacion']
                        act_detalle = actuacion['actuacion_detalle']
                        fecha_actuacion = actuacion['fecha_actucion']
                        
                        actuar = actuar.replace("\n", " ")
                        actuar = actuar.replace("  ", " ")
                        act_detalle = act_detalle.replace("\n", " ")
                        act_detalle = act_detalle.replace("  ", " ")
                        # Convierte la fecha en el formato correcto para SQL Server
                        fecha_actuacionS = datetime.strptime(fecha_actuacion, '%d/%m/%Y %H:%M').strftime('%Y-%m-%d %H:%M:%S.%f')[:-3]
                        """
                        print(f"Actuación: {act}")
                        print(f"Detalle de Actuación: {act_detalle}")
                        print(f"Fecha de Actuación: {fecha_actuacion}")
                        """
                        # se inserta el datelle
                        # InsertarDetalle
                        # @demandado VARCHAR(255), @ofendido VARCHAR(255), @judicatura VARCHAR(255),
                        # @numproceso VARCHAR(255), @actuacion VARCHAR(255), @detalle VARCHAR(255), @fecha_actuacion DATETIME
                        parametrosDetalle = []
                        parametrosDetalle.append(demandado)
                        parametrosDetalle.append(ofendido)
                        parametrosDetalle.append(judicatura)
                        parametrosDetalle.append(numero_proceso)
                        parametrosDetalle.append(actuar)
                        parametrosDetalle.append(act_detalle)
                        parametrosDetalle.append(fecha_actuacionS)
                        resultado = ejecutaProcedimiento('InsertarDetalle', parametrosDetalle)
                        print(f'Resultado Detalle {resultado}')
                        # ALERTAS
                        # ARCHIVO, INADMISION, ESCRITO
                        # COMPLETAR Y/O ACLARAR
                        # Luego, envía una respuesta de vuelta a la página web
                        if (resultado[0]['Resultado'] == '1' or resultado[0]['Resultado'] == '2'):
                            respuesta = f"Número de proceso {numero_proceso} encontrado y registrado con éxito"
                            # respuesta = "Registro/Actualización exitoso"
                            # print(resultado)
                        else:
                            respuesta = "Error al Registra/Actualiza la actuación"
                            # print(resultado)

                else:
                    respuesta = "Error al Registra/Actualiza el deprecatorio"
                    # print(resultado)
            else:
                respuesta = "Error al Registra/Actualiza el demandado"
                # print(resultado)
    return respuesta

def leeActualizaJsonProceso(nombreArchJson):
    respuesta = ""
    print(f'Archivo a leer: archivos/json/{nombreArchJson}')
    with open('archivos/json/' + nombreArchJson) as procesoJson:
        datos = json.load(procesoJson)
        for elemento in datos:
            #print(f"Elemento: {elemento}")
            cedula = ''
            no_obligacion = ''
            movimiento = elemento['movimiento']
            delito = movimiento['delito']
            demandado = movimiento['demandado']
            detalle_actuaciones = movimiento['detalle_actuaciones']
            fecha_ingreso = movimiento['fecha_ingreso']
            judicatura = movimiento['judicatura']
            materia = movimiento['materia']
            numero_proceso = movimiento['numero_proceso']
            ofendido = movimiento['ofendido']
            tipo_accion = movimiento['tipo_accion']
            # Convierte la fecha en el formato correcto para SQL Server
            fecha_ingresoS = datetime.strptime(fecha_ingreso, '%d/%m/%Y %H:%M').strftime('%Y-%m-%d %H:%M:%S.%f')[:-3]
            # print(f"Delito: {delito}")
            # print(f"Demandado: {demandado}")
            # print(f"Fecha de Ingreso: {fecha_ingresoS}")
            # print(f"Judicatura: {judicatura}")
            # print(f"Materia: {materia}")
            print(f"Número de Proceso: {numero_proceso}")
            # print(f"Ofendido: {ofendido}")
            # print(f"Tipo de Acción: {tipo_accion}")

            # Puedes agregar cualquier otro procesamiento que desees aquí
            # @cedula VARCHAR(15), @nombres VARCHAR(255), @no_obligacion VARCHAR(100), @numproceso VARCHAR(20)
            parametrosCliente = []
            parametrosCliente.append(cedula)
            parametrosCliente.append(demandado)
            parametrosCliente.append(no_obligacion)
            parametrosCliente.append(numero_proceso)
            resultado = ejecutaProcedimiento('InsertarActualizaCliente', parametrosCliente)
            print(f'Resultado I/A Cliente {resultado}')
            # inserta/actualiza los deprecatorios
            if (resultado[0]['Resultado'] == 1 or resultado[0]['Resultado'] == 2):
                # {'Resultado': 2}
                respuesta = "Registro/Actualización del demandado realizado"
                # print(respuesta)

                # se insertan el deprecatorio
                # InsertarDeprecatorio
                # @numproceso VARCHAR(20), @demandado VARCHAR(255), @ofendido VARCHAR(255), @delito VARCHAR(255),
                # @fecha_ingreso DATETIME, @judicatura VARCHAR(255), @materia VARCHAR(255), @tipoaccion VARCHAR(255)
                parametrosDeprecatorio = []
                parametrosDeprecatorio.append(numero_proceso)
                parametrosDeprecatorio.append(demandado)
                parametrosDeprecatorio.append(ofendido)
                parametrosDeprecatorio.append(delito)
                parametrosDeprecatorio.append(fecha_ingresoS)
                parametrosDeprecatorio.append(judicatura)
                parametrosDeprecatorio.append(materia)
                parametrosDeprecatorio.append(tipo_accion)
                resultado = ejecutaProcedimiento('InsertarActualizaDeprecatorio', parametrosDeprecatorio)
                print(f'Resultado I/A Deprecatorio {resultado}')
                
                # inserta/actualiza el detalle de actuaciones
                if (resultado[0]['Resultado'] == '1' or resultado[0]['Resultado'] == '2'):
                    respuesta = "Registra/Actualiza el deprecatorio"
                    for actuacion in detalle_actuaciones:
                        actuar = actuacion['actuacion']
                        act_detalle = actuacion['actuacion_detalle']
                        fecha_actuacion = actuacion['fecha_actucion']
                        
                        actuar = actuar.replace("\n", " ")
                        actuar = actuar.replace("  ", " ")
                        act_detalle = act_detalle.replace("\n", " ")
                        act_detalle = act_detalle.replace("  ", " ")
                        # Convierte la fecha en el formato correcto para SQL Server
                        fecha_actuacionS = datetime.strptime(fecha_actuacion, '%d/%m/%Y %H:%M').strftime('%Y-%m-%d %H:%M:%S.%f')[:-3]
                        """
                        print(f"Actuación: {act}")
                        print(f"Detalle de Actuación: {act_detalle}")
                        print(f"Fecha de Actuación: {fecha_actuacion}")
                        """
                        # se inserta el datelle
                        # InsertarDetalle
                        # @demandado VARCHAR(255), @ofendido VARCHAR(255), @judicatura VARCHAR(255),
                        # @numproceso VARCHAR(255), @actuacion VARCHAR(255), @detalle VARCHAR(255), @fecha_actuacion DATETIME
                        parametrosDetalle = []
                        parametrosDetalle.append(demandado)
                        parametrosDetalle.append(ofendido)
                        parametrosDetalle.append(judicatura)
                        parametrosDetalle.append(numero_proceso)
                        parametrosDetalle.append(actuar)
                        parametrosDetalle.append(act_detalle)
                        parametrosDetalle.append(fecha_actuacionS)
                        resultado = ejecutaProcedimiento('InsertarActualizaDetalle', parametrosDetalle)
                        #print(f'Resultado I/A Detalle {resultado}')
                        # ALERTAS
                        # ARCHIVO, INADMISION, ESCRITO
                        # COMPLETAR Y/O ACLARAR
                        # Luego, envía una respuesta de vuelta a la página web
                        if (resultado[0]['Resultado'] == '1' or resultado[0]['Resultado'] == '2'):
                            respuesta = f"Número de proceso {numero_proceso} encontrado y registrado con éxito"
                            # respuesta = "Registro/Actualización exitoso"
                            # print(resultado)
                        else:
                            respuesta = "Error al Registra/Actualiza la actuación"
                            # print(resultado)

                else:
                    respuesta = "Error al Registra/Actualiza el deprecatorio"
                    # print(resultado)
            else:
                respuesta = "Error al Registra/Actualiza el demandado"
                # print(resultado)
    return respuesta

@app.route('/extraeinfo', methods=['POST'])
def extraeinfo():
    data = request.get_json()  # Obtiene los datos enviados desde la página web
    numero_proceso = data.get('num_proceso', '')
    numero_proceso = numero_proceso.replace("-", "")
    respuesta = ""
    # consulta el API retorno el JSON o el error contemplado
    datosApiJson = consultaAPI(numero_proceso)
    # retorno el nombre del archivo o un mensaje de error
    archivoJson = guardaArchivo(datosApiJson)
    # Puedes acceder a los datos en el objeto JSON de respuesta
    if "error" in archivoJson.lower():
        # print("La palabra 'Error' no está en el texto.")
        respuesta = f'No se pudo  el número de proceso {numero_proceso}.' + archivoJson
    else:
        # print("La palabra 'Error' está en el texto.")
        # Itera a través de las claves (nombres de campo) y valores en el JSON
        respuesta = leeActualizaJsonProceso(archivoJson)
    dicResp = {"salida" : respuesta}
    return dicResp

def pagina_no_encontrada(error):
    datos = {
        'title': "Pagina no encontrada",
        'mensaje': "No existe la pagina que busca<br>" + str(error)
    }
    return render_template('404.html', datos= datos), 404
    #return redirect(url_for('index'))


@app.route('/')
def home():
    username = session.get('name')
    a = session.get('loggedin')
    print(f'Home usuario logeado: {username} {a}')
    if session.get('loggedin') != 1:
        # return render_template('auth/login.html')
        return redirect(url_for('login'))
    else:
        # return render_template('index.html')
        return redirect(url_for('perfil'))
    
@app.route('/cuentascargadas')
def cuentascargadas():
    listado = getProcesos("ListaCuentas")
    datos = {
        'title': 'Cuentas',
        'Description': 'Detalle de cuentas o procesos provenientes del modulo de carga',
        'listado': listado
    }
    datos['mensaje'] = "hola."
    return render_template('cuentas.html', datos=datos)
    
@app.route('/perfil')
def perfil():
    username = session.get('name')
    userlastname = session.get('lastname')
    a = session.get('loggedin')
    print(f'Perfil usuario logeado: {username} {userlastname} {a}')
    if session.get('loggedin') != 1:
        # return render_template('auth/login.html')
        return redirect(url_for('login'))
    else:
        return render_template('auth/users-profile.html')

@app.route('/login', methods =['GET', 'POST'])
def login():
    mesage = ''
    if request.method == 'POST' and 'email' in request.form and 'password' in request.form:
        email = request.form['email']
        password = request.form['password']
        try:
            conn = connection()
            cursor = conn.cursor()

            if not re.match(r'[^@]+@[^@]+\.[^@]+', email) and len(email) > 4:
                mesage = '¡Ingrese un correo invalido!'
            elif not email or not password:
                mesage = '¡Rellene todo el formulario!'
            else:
                # Codifica el texto como bytes usando UTF-8
                email = email.replace("'", "")
                password = password.replace("'", "")

                pswd_encrypted = encriptar_clave(password)
                sentencia = "EXEC LoginUser '" + email + "', '" + pswd_encrypted + "';"
                # print(f"Sentencia busq. Login: { sentencia }")
                cursor.execute(sentencia)
                #cursor.execute('Exec LoginUser % s % s', (email, password, ))
                user = cursor.fetchone()
                # print(f'Usuario: {user} {user[0]}')
                if user[0] != '0':
                    # print(user)
                    # 0 id, 1 'nombre', 2 apellidos, 3 correo, 4 estado, 5 pass, 6 login_attempts
                    # 7 is_blocked, 8 blocked_until, 9 CreacionUsuarioID, 10 CreadorNombre, 11 CreadorApellido, 12 CreadorCorreo
                    # 13 ModificacionUsuarioID, 14 ModificadorNombre, 15 ModificadorApellido, 16 ModificadorCorreo
                    # 17 FechaCreacion, 18 FechaModificacion;
                    session['loggedin'] = 1
                    session['userid'] = user[0]
                    session['userNombre'] = user[1]
                    session['userApellido'] = user[2]
                    session['email'] = user[3]
                    mesage = '¡Inicio sesión corectamente!'
                    # return render_template('auth/user.html', mesage = mesage, session = session)
                    return redirect(url_for('perfil'))
                else:
                    mesage = user[1] #+ " " + user[2]
        except Exception as ex:
            mesage = f"Error al consultar login: { ex }"
            print(mesage)
    return render_template('auth/pages-login.html', mesage = mesage)

@app.route('/logout')
def logout():
    nombr = session.get('name')
    print(f'El usuario {nombr} ha cerrado sessión con exito.')
    session.pop('loggedin', None)
    session.pop('userid', None)
    session.pop('name', None)
    session.pop('email', None)
    return redirect(url_for('login'))

@app.route('/register', methods =['GET', 'POST'])
def register():
    mesage = ''
    if request.method == 'POST' and 'name' in request.form and 'lastname' in request.form and 'password' in request.form and 'email' in request.form :
        userName = request.form['name']
        userLastname = request.form['lastname']
        email = request.form['email']
        clave = request.form['password']

        # print("Reg.Entro")
        try:
            conn = connection()
            cursor = conn.cursor()
            # Verifica si existe una cuenta
            sentencia = "SELECT * FROM USUARIOS WHERE correo = '" + email + "';"
            # 'SELECT * FROM USUARIOS WHERE correo = % s', (email, )
            cursor.execute(sentencia)
            # sentencia = "SELECT * FROM USUARIOS WHERE correo = ?;"
            print(f'Sentencia Busq. registro: {sentencia}')
            #cursor.execute(sentencia, email)
            account = cursor.fetchone()
            print(f"Cuenta: {account}")
            if account:
                mesage = '¡La cuenta, ya existe!'
            elif not re.match(r'[^@]+@[^@]+\.[^@]+', email) and len(email) > 4:
                mesage = '¡Ingrese un correo invalido!'
            elif not userName or not userLastname or not clave or not email:
                mesage = '¡Rellene todo el formulario!'
            else:
                print(f"Quita inyeccion SQL")
                userName = userName.replace("'", "")
                userLastname = userLastname.replace("'", "")
                email = email.replace("'", "")
                clave = clave.replace("'", "")
                print(f"Clave: {clave} {len(clave)}")
                clave_encrypted = encriptar_clave(clave)
                print(f"Clave_cifrada: {clave_encrypted} {len(clave_encrypted)}")
                sentencia = "EXEC InsertarUsuario '" + userName + "', '"+ userLastname + "', '"+ email + "', '"+ clave_encrypted + "';"
                print(f'Sentencia InsertarUsuario: {sentencia}')
                cursor.execute(sentencia)
                #cursor.execute('EXEC InsertarUsuario % s % s % s % s', (userName, userLastname, email, clave_encrypted, ))
                
                results = cursor.fetchone()
                print(f'Resultados del insert {results}')
                if results.__contains__('1'):
                    mesage = '¡Se ha registrado exitosamente!'
                elif results.__contains__('1'):
                    mesage = 'La consulta no retornó resultados.'
                    print(mesage)
                else:
                    mesage = ''
                cursor.commit()
                cursor.close()
                conn.close()
            return render_template('auth/pages-login.html', mesage = mesage)
        except Exception as ex:
            mesage = f"Error al realizar el registro: { ex }"
            #print(mesage)
    elif request.method == 'POST':
        #print("No Entro")
        mesage = '¡Rellene todo el formulario!'
    #print("Finaliza")
    return render_template('auth/pages-register.html', mesage = mesage)

@app.route('/alterUser', methods =['GET', 'POST'])
def alterUser():
    mesage = ''
    if request.method == 'POST' and 'name' in request.form and 'lastname' in request.form and 'password' in request.form and 'email' in request.form :
        userName = request.form['name']
        userLastname = request.form['lastname']
        email = request.form['email']
        clave = request.form['password']

        # print("Reg.Entro")
        try:
            conn = connection()
            cursor = conn.cursor()
            # Verifica si existe una cuenta
            sentencia = "SELECT * FROM USUARIOS WHERE correo = '" + email + "';"
            # 'SELECT * FROM USUARIOS WHERE correo = % s', (email, )
            cursor.execute(sentencia)
            # sentencia = "SELECT * FROM USUARIOS WHERE correo = ?;"
            print(f'Sentencia Busq. registro: {sentencia}')
            #cursor.execute(sentencia, email)
            account = cursor.fetchone()
            print(f"Cuenta: {account}")
            if account:
                mesage = '¡La cuenta, ya existe!'
            elif not re.match(r'[^@]+@[^@]+\.[^@]+', email) and len(email) > 4:
                mesage = '¡Ingrese un correo invalido!'
            elif not userName or not userLastname or not clave or not email:
                mesage = '¡Rellene todo el formulario!'
            else:
                print(f"Quita inyeccion SQL")
                userName = userName.replace("'", "")
                userLastname = userLastname.replace("'", "")
                email = email.replace("'", "")
                clave = clave.replace("'", "")
                print(f"Clave: {clave} {len(clave)}")
                clave_encrypted = encriptar_clave(clave)
                print(f"Clave_cifrada: {clave_encrypted} {len(clave_encrypted)}")
                sentencia = "EXEC InsertarUsuario '" + userName + "', '"+ userLastname + "', '"+ email + "', '"+ clave_encrypted + "';"
                print(f'Sentencia InsertarUsuario: {sentencia}')
                cursor.execute(sentencia)
                #cursor.execute('EXEC InsertarUsuario % s % s % s % s', (userName, userLastname, email, clave_encrypted, ))
                
                results = cursor.fetchone()
                print(f'Resultados del insert {results}')
                if results.__contains__('1'):
                    mesage = '¡Se ha registrado exitosamente!'
                elif results.__contains__('1'):
                    mesage = 'La consulta no retornó resultados.'
                    print(mesage)
                else:
                    mesage = ''
                cursor.commit()
                cursor.close()
                conn.close()
            return render_template('auth/pages-login.html', mesage = mesage)
        except Exception as ex:
            mesage = f"Error al realizar el registro: { ex }"
            #print(mesage)
    elif request.method == 'POST':
        #print("No Entro")
        mesage = '¡Rellene todo el formulario!'
    #print("Finaliza")
    return render_template('auth/pages-register.html', mesage = mesage)

# inicia la app
if __name__ == '__main__':
    # manejo de errores
    app.register_error_handler(404, pagina_no_encontrada)
    #prod
    #app.run(host='0.0.0.0', port=5000)
    #pruebas
    app.run(host='0.0.0.0', port=5001, debug=True)