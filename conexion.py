import sqlalchemy as sa
from sqlalchemy import create_engine
import urllib
import pyodbc


conn = urllib.parse.quote_plus(
    'Data Source Name=CRISTIAN;'
    'Driver={SQL Server};'
    'Server=CRISTIAN;'
    'Database=Juicios;'
    'Trusted_connection=yes;'
)
coxn = ""
try:
    coxn = create_engine('mssql-pyodbc:///?odbc_connect={}'.format(conn))
    print("Conectado")
except:
    print("Fallido")

