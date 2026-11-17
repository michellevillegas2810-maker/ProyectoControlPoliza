# models/datos.py
# Capa: Modelo (datos) - es el UNICO lugar que abre archivos.
# No contiene reglas de negocio, solo lectura de Excel y PDF.

import os
from datetime import datetime

import pandas as pd
import pdfplumber

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DATA_DIR = os.path.join(BASE_DIR, "data")
EXCEL_PATH = os.path.join(DATA_DIR, "Maestro_Clientes.xlsx")
POLIZAS_DIR = os.path.join(DATA_DIR, "polizas")

# Diccionario CAMPOS: etiqueta del PDF -> nombre del campo en el diccionario de salida
CAMPOS = {
    "Numero de poliza": "numero",
    "Ramo": "ramo",
    "Tomador / Asegurado": "nombre",
    "Cedula": "cedula",
    "Vigencia desde": "desde",
    "Vigencia hasta": "hasta",
    "Prima anual": "prima",
    "Forma de pago": "pago",
    "Suma asegurada": "suma",
    "Asesor": "asesor",
}

CAMPOS_FECHA = {"desde", "hasta"}
CAMPOS_MONTO = {"prima", "suma"}


def _parse_fecha(texto):
    """Convierte texto dd/mm/aaaa a objeto date. Devuelve None si esta vacio o invalido."""
    if not texto or not texto.strip():
        return None
    try:
        return datetime.strptime(texto.strip(), "%d/%m/%Y").date()
    except ValueError:
        return None


def _parse_monto(texto):
    """Convierte 'CRC 228,000.00' a numero float. Devuelve None si esta vacio o invalido."""
    if not texto or not texto.strip():
        return None
    try:
        limpio = texto.replace("CRC", "").replace(",", "").strip()
        return float(limpio)
    except ValueError:
        return None


def cargar_clientes():
    """Lee data/Maestro_Clientes.xlsx (hoja Clientes) con pandas.
    
    Devuelve el DataFrame con Cedula como texto sin espacios.
    
    Ladrillos:
    - variable: df (DataFrame), EXCEL_PATH (texto)
    - tipo: DataFrame, str
    - funcion: pd.read_excel() abre el archivo Excel
    """
    df = pd.read_excel(EXCEL_PATH, sheet_name="Clientes", dtype={"Cedula": str})
    df["Cedula"] = df["Cedula"].str.strip()
    return df


def leer_poliza(ruta_pdf):
    """Abre el PDF con pdfplumber, toma el texto de la primera pagina.
    
    Guarda la primera linea como "aseguradora" y recorre las demas lineas
    con un bucle: si la linea tiene ":" y su etiqueta esta en CAMPOS,
    guarda el valor. Convierte fechas y montos.
    
    Devuelve un diccionario con: archivo, aseguradora, numero, ramo, nombre,
    cedula, desde, hasta, prima, pago, suma, asesor.
    
    Ladrillos:
    - variable: ruta_pdf (texto), texto (texto), lineas (lista de texto), etiqueta (texto), valor (texto), campo (texto)
    - tipo: str, list, dict, date, float, None
    - funcion: pdfplumber.open() abre el PDF
    - bucle: for recorre las lineas del texto
    - condicional: if revisa si la linea tiene ":" y si la etiqueta esta en CAMPOS
    """
    nombre_archivo = os.path.basename(ruta_pdf)

    datos = {
        "archivo": nombre_archivo,
        "aseguradora": "",
        "numero": None,
        "ramo": None,
        "nombre": None,
        "cedula": None,
        "desde": None,
        "hasta": None,
        "prima": None,
        "pago": None,
        "suma": None,
        "asesor": None,
    }

    with pdfplumber.open(ruta_pdf) as pdf:
        pagina = pdf.pages[0]
        texto = pagina.extract_text() or ""

    lineas = texto.split("\n")

    # Primera linea es el nombre de la aseguradora
    if lineas:
        datos["aseguradora"] = lineas[0].strip()

    # Recorrer las demas lineas con un bucle
    for linea in lineas[1:]:
        if ":" in linea:
            etiqueta, valor = linea.split(":", 1)
            etiqueta = etiqueta.strip()
            valor = valor.strip()
            if etiqueta in CAMPOS:
                campo = CAMPOS[etiqueta]
                if campo in CAMPOS_FECHA:
                    datos[campo] = _parse_fecha(valor)
                elif campo in CAMPOS_MONTO:
                    datos[campo] = _parse_monto(valor)
                else:
                    datos[campo] = valor

    return datos


def cargar_polizas():
    """Recorre data/polizas en orden alfabetico y devuelve una lista
    con el diccionario de cada PDF.
    
    Ladrillos:
    - variable: polizas (lista), nombre_archivo (texto), ruta (texto), poliza (diccionario)
    - tipo: list, str, dict
    - funcion: os.listdir() lista los archivos de la carpeta
    - bucle: for recorre cada archivo
    - condicional: if termina en .pdf
    """
    polizas = []
    for nombre_archivo in sorted(os.listdir(POLIZAS_DIR)):
        if nombre_archivo.endswith(".pdf"):
            ruta = os.path.join(POLIZAS_DIR, nombre_archivo)
            poliza = leer_poliza(ruta)
            polizas.append(poliza)
    return polizas