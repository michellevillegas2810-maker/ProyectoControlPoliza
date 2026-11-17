# models/polizas.py
# Capa: Modelo (reglas del negocio) - no abre archivos directamente,
# pero usa las funciones de models/datos.py para obtener los datos.

from datetime import date, timedelta

from models.datos import cargar_clientes, cargar_polizas

# Variables de negocio (constantes)
FECHA_CORTE = date(2026, 11, 9)
DIAS_AVISO = 30


def estado_poliza(hasta, fecha_corte=FECHA_CORTE):
    """Devuelve el estado de una poliza segun su fecha de vigencia hasta.
    
    Reglas:
    - "Sin fecha" si hasta es None
    - "Vencida": hasta < fecha_corte
    - "Por vencer": 0 <= dias hasta vencer <= DIAS_AVISO
    - "Vigente": mas de DIAS_AVISO dias
    
    Ladrillos:
    - variable: hasta (date o None), fecha_corte (date), dias (numero entero)
    - tipo: date, NoneType, int, str
    - condicional: if / elif / else
    """
    if hasta is None:
        return "Sin fecha"
    if hasta < fecha_corte:
        return "Vencida"
    dias = (hasta - fecha_corte).days
    if 0 <= dias <= DIAS_AVISO:
        return "Por vencer"
    return "Vigente"


def calcular_resultados(fecha_corte=FECHA_CORTE):
    """Cruza cada poliza con el maestro por cedula.
    
    Agrega correo y campo en_maestro (verdadero/falso), calcula los dias
    hasta vencer y el estado. Devuelve una lista de diccionarios ordenada
    de menos a mas dias (lo urgente primero). Las que no tienen fecha van al final.
    
    Ladrillos:
    - variable: clientes_df (DataFrame), polizas (lista de diccionarios), clientes_por_cedula (diccionario), resultados (lista), poliza (diccionario), correo (texto), en_maestro (booleano), dias_hasta (numero o None)
    - tipo: DataFrame, list, dict, str, bool, int, NoneType, date
    - bucle: for recorre clientes y polizas
    - condicional: if verifica si cedula esta en el maestro
    - funcion: estado_poliza() calcula el estado
    """
    clientes_df = cargar_clientes()
    polizas = cargar_polizas()

    # Indexar clientes por cedula para buscar el correo rapidamente
    clientes_por_cedula = {}
    for _, fila in clientes_df.iterrows():
        cedula = str(fila["Cedula"]).strip()
        clientes_por_cedula[cedula] = fila.get("Correo", "")

    resultados = []
    for poliza in polizas:
        cedula = poliza.get("cedula") or ""
        cedula = cedula.strip()
        correo = clientes_por_cedula.get(cedula, "")
        en_maestro = cedula in clientes_por_cedula

        hasta = poliza.get("hasta")
        desde = poliza.get("desde")
        prima = poliza.get("prima")

        if hasta is not None:
            dias_hasta = (hasta - fecha_corte).days
        else:
            dias_hasta = None

        estado = estado_poliza(hasta, fecha_corte)

        resultado = {
            "archivo": poliza.get("archivo"),
            "aseguradora": poliza.get("aseguradora"),
            "numero": poliza.get("numero"),
            "ramo": poliza.get("ramo"),
            "nombre": poliza.get("nombre"),
            "cedula": cedula,
            "correo": correo,
            "en_maestro": en_maestro,
            "desde": desde,
            "hasta": hasta,
            "dias_hasta": dias_hasta,
            "prima": prima,
            "pago": poliza.get("pago"),
            "suma": poliza.get("suma"),
            "asesor": poliza.get("asesor"),
            "estado": estado,
        }
        resultados.append(resultado)

    # Ordenar de menos a mas dias (urgente primero). None al final.
    resultados.sort(
        key=lambda r: (
            r["dias_hasta"] is None,
            r["dias_hasta"] if r["dias_hasta"] is not None else 999999,
        )
    )
    return resultados


def contar_por_estado(resultados):
    """Devuelve un diccionario con cuantas polizas hay de cada estado.
    
    Ladrillos:
    - variable: contadores (diccionario), r (diccionario), estado (texto)
    - tipo: dict, str, int
    - bucle: for recorre resultados
    """
    contadores = {}
    for r in resultados:
        estado = r["estado"]
        contadores[estado] = contadores.get(estado, 0) + 1
    return contadores


def primas_por_aseguradora(resultados):
    """Devuelve un diccionario aseguradora -> suma de primas de polizas no vencidas,
    ordenado de mayor a menor prima.
    
    Ladrillos:
    - variable: primas (diccionario), r (diccionario), aseguradora (texto), prima (numero)
    - tipo: dict, str, float
    - bucle: for recorre resultados
    - condicional: if ignora las vencidas
    """
    primas = {}
    for r in resultados:
        if r["estado"] == "Vencida":
            continue
        aseguradora = r["aseguradora"] or "Desconocida"
        prima = r["prima"] if r["prima"] is not None else 0
        primas[aseguradora] = primas.get(aseguradora, 0) + prima

    # Ordenar de mayor a menor
    primas_ordenadas = dict(sorted(primas.items(), key=lambda x: x[1], reverse=True))
    return primas_ordenadas


def buscar_inconsistencias(resultados):
    """Devuelve una lista de textos con los 3 tipos de problema:
    1. Cliente del maestro sin ninguna poliza.
    2. Poliza cuya cedula no esta en el maestro.
    3. Poliza sin prima o con fecha ilegible.
    
    Ladrillos:
    - variable: inconsistencias (lista), clientes_df (DataFrame), clientes_por_cedula (diccionario), cedulas_maestro (conjunto), cedulas_en_polizas (conjunto), r (diccionario), cedula (texto), numero (texto), nombre (texto)
    - tipo: list, DataFrame, dict, set, str
    - bucle: for recorre clientes y resultados
    - condicional: if detecta cada tipo de inconsistencia
    """
    inconsistencias = []

    # Cargar clientes del maestro para detectar tipo 1
    clientes_df = cargar_clientes()
    clientes_por_cedula = {}
    cedulas_maestro = set()
    for _, fila in clientes_df.iterrows():
        cedula = str(fila["Cedula"]).strip()
        nombre = fila.get("Nombre_Completo", cedula)
        clientes_por_cedula[cedula] = nombre
        cedulas_maestro.add(cedula)

    # Cedulas que aparecen al menos en una poliza
    cedulas_en_polizas = set()
    for r in resultados:
        if r["cedula"]:
            cedulas_en_polizas.add(r["cedula"])

    # Tipo 1: cliente del maestro sin ninguna poliza
    for cedula in cedulas_maestro:
        if cedula not in cedulas_en_polizas:
            nombre = clientes_por_cedula.get(cedula, cedula)
            inconsistencias.append(
                f"Cliente sin poliza: cedula {cedula} ({nombre}) no tiene ninguna poliza"
            )

    # Tipo 2 y 3: revisar cada poliza
    for r in resultados:
        cedula = r["cedula"]
        numero = r["numero"]

        # Tipo 2: cedula no registrada en el maestro
        if cedula and cedula not in cedulas_maestro:
            inconsistencias.append(
                f"Cedula no registrada: poliza {numero} tiene cedula {cedula} no registrada en el maestro"
            )

        # Tipo 3: poliza sin prima o con fecha ilegible
        if r["prima"] is None or r["hasta"] is None:
            inconsistencias.append(
                f"Poliza invalida: {numero} sin prima o fecha ilegible"
            )

    return inconsistencias


def buscar_por_numero(numero):
    """Busca una poliza por su numero en los resultados calculados.
    
    Devuelve el diccionario de la poliza o None si no existe.
    
    Ladrillos:
    - variable: numero (texto), resultados (lista), r (diccionario)
    - tipo: str, list, dict, NoneType
    - bucle: for recorre resultados
    - condicional: if compara el numero
    """
    resultados = calcular_resultados()
    for r in resultados:
        if r["numero"] == numero:
            return r
    return None