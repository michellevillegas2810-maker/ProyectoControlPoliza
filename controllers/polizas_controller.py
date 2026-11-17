# controllers/polizas_controller.py
# Capa: Controlador - rutas Flask (Blueprint).
# No calcula nada: solo llama a models/ y services/.

from io import BytesIO
import zipfile

from flask import Blueprint, render_template, send_file, abort

from models.polizas import (
    calcular_resultados,
    contar_por_estado,
    primas_por_aseguradora,
    buscar_inconsistencias,
    buscar_por_numero,
    FECHA_CORTE,
)
from services.generador_aviso import crear_aviso_pdf

bp = Blueprint("polizas", __name__)

# Cargar resultados una vez al iniciar la app (solo lectura)
resultados = calcular_resultados()


@bp.route("/")
def inicio():
    """Ruta del tablero principal.
    
    Muestra la vista inicio.html con:
    - resultados (lista de polizas ordenada por urgencia)
    - conteo (cuantas hay de cada estado)
    - primas por aseguradora (solo no vencidas)
    - inconsistencias (lista de textos)
    - fecha de corte
    
    Ladrillos:
    - variable: conteo (diccionario), primas (diccionario), inconsistencias (lista)
    - tipo: dict, list
    - funcion: render_template() renderiza la vista HTML
    """
    conteo = contar_por_estado(resultados)
    primas = primas_por_aseguradora(resultados)
    inconsistencias = buscar_inconsistencias(resultados)

    return render_template(
        "inicio.html",
        resultados=resultados,
        conteo=conteo,
        primas=primas,
        inconsistencias=inconsistencias,
        fecha_corte=FECHA_CORTE.strftime("%d/%m/%Y"),
    )


@bp.route("/aviso/<numero>")
def aviso(numero):
    """Devuelve el PDF de aviso de una póliza para ver en el navegador.
    
    Si la póliza no existe o está Vigente, devuelve error 404.
    
    Ladrillos:
    - variable: r (diccionario), pdf_bytes (bytes), buffer (BytesIO)
    - tipo: dict, bytes, BytesIO
    - funcion: buscar_por_numero(), crear_aviso_pdf(), send_file(), abort()
    - condicional: if verifica si la poliza existe y no esta vigente
    """
    r = buscar_por_numero(numero)
    if not r:
        abort(404)
    if r["estado"] == "Vigente":
        abort(404)

    pdf_bytes = crear_aviso_pdf(r)

    buffer = BytesIO(pdf_bytes)
    buffer.seek(0)
    return send_file(
        buffer,
        mimetype="application/pdf",
        download_name=f"aviso_{numero}.pdf",
    )


@bp.route("/descargar-avisos")
def descargar_avisos():
    """Devuelve un .zip en memoria con los avisos de todas las pólizas
    Por vencer y Vencidas.
    
    Ladrillos:
    - variable: buffer (BytesIO), zf (ZipFile), r (diccionario), pdf_bytes (bytes)
    - tipo: BytesIO, ZipFile, dict, bytes
    - funcion: zipfile.ZipFile(), send_file(), abort()
    - bucle: for recorre resultados
    - condicional: if filtra solo Por vencer y Vencidas
    """
    buffer = BytesIO()
    with zipfile.ZipFile(buffer, "w") as zf:
        for r in resultados:
            if r["estado"] in ("Por vencer", "Vencida"):
                pdf_bytes = crear_aviso_pdf(r)
                zf.writestr(f"aviso_{r['numero']}.pdf", pdf_bytes)

    buffer.seek(0)
    return send_file(
        buffer,
        mimetype="application/zip",
        download_name="avisos.zip",
        as_attachment=True,
    )