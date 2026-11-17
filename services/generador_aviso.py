# services/generador_aviso.py
# Capa: Servicio - crea el aviso de renovacion en PDF con fpdf2 (A4 vertical).
# Devuelve el PDF en bytes (no guarda archivo en disco).

from fpdf import FPDF


def _latin1(texto):
    """Convierte texto a una cadena segura en latin-1 para que las tildes no fallen."""
    if texto is None:
        return ""
    return str(texto).encode("latin-1", errors="replace").decode("latin-1")


def crear_aviso_pdf(poliza):
    """Crea un aviso de renovacion de poliza en PDF (A4 vertical) y lo devuelve en bytes.

    Diseno:
    - Banda superior roja (#AE1800) con "Corredora de Seguros Horizonte" y
      "Aviso de renovacion de poliza".
    - Saludo "Estimado(a) {nombre}".
    - Parrafo distinto segun estado: Vencida o Por vencer.
    - Tabla con numero de poliza, aseguradora, ramo, cedula, vigencia,
      prima anual (o "No registrada") y forma de pago.
    - Pie de pagina en gris: documento ficticio academico.

    Ladrillos:
    - variable: pdf (objeto FPDF), rojo (tupla), gris (tupla), nombre (texto),
      estado (texto), hasta (date), dias_hasta (numero), asesor (texto),
      salida (bytes)
    - tipo: objeto FPDF, tuple, str, date, int, bytes
    - funcion: FPDF() crea el documento, rect() dibuja la banda, cell() y
      multi_cell() escriben texto y tablas, output() devuelve los bytes
    """
    pdf = FPDF(orientation="P", unit="mm", format="A4")
    pdf.add_page()

    # Colores
    rojo = (174, 24, 0)      # #AE1800
    gris = (100, 100, 100)   # gris para el pie

    # ---------- Banda superior roja ----------
    pdf.set_fill_color(*rojo)
    pdf.rect(0, 0, 210, 25, style="F")

    pdf.set_text_color(255, 255, 255)  # texto blanco sobre rojo
    pdf.set_font("Helvetica", "B", 14)
    pdf.set_xy(10, 8)
    pdf.cell(0, 8, _latin1("Corredora de Seguros Horizonte"), ln=True, align="C")
    pdf.set_font("Helvetica", "B", 12)
    pdf.cell(0, 8, _latin1("Aviso de renovacion de poliza"), ln=True, align="C")

    # ---------- Contenido ----------
    pdf.set_text_color(0, 0, 0)  # volver a negro
    pdf.ln(12)

    nombre = poliza.get("nombre", "Cliente")
    pdf.set_font("Helvetica", size=12)
    pdf.cell(0, 10, _latin1(f"Estimado(a) {nombre}:"), ln=True)
    pdf.ln(6)

    estado = poliza.get("estado")
    hasta = poliza.get("hasta")
    dias_hasta = poliza.get("dias_hasta")
    asesor = poliza.get("asesor", "su asesor")

    if estado == "Vencida":
        fecha_str = hasta.strftime("%d/%m/%Y") if hasta else "fecha desconocida"
        pdf.set_font("Helvetica", size=11)
        pdf.multi_cell(
            0,
            8,
            _latin1(f"Su poliza vencio el {fecha_str}. Por favor, comuniquese con nosotros para renovarla."),
        )
    elif estado == "Por vencer":
        fecha_str = hasta.strftime("%d/%m/%Y") if hasta else "fecha desconocida"
        pdf.set_font("Helvetica", size=11)
        pdf.multi_cell(
            0,
            8,
            _latin1(
                f"Su poliza vence el {fecha_str} (en {dias_hasta} dias). "
                f"Su asesor {asesor} se comunicara con usted."
            ),
        )
    else:
        pdf.set_font("Helvetica", size=11)
        pdf.multi_cell(
            0,
            8,
            _latin1("Su poliza esta vigente. No es necesario renovar en este momento."),
        )

    pdf.ln(10)

    # ---------- Tabla ----------
    pdf.set_font("Helvetica", "B", 10)
    pdf.cell(45, 8, _latin1("Campo"), border=1)
    pdf.cell(155, 8, _latin1("Valor"), border=1)
    pdf.ln()

    desde = poliza.get("desde")
    if desde and hasta:
        vigencia = f"{desde.strftime('%d/%m/%Y')} al {hasta.strftime('%d/%m/%Y')}"
    else:
        vigencia = "No registrada"

    prima = poliza.get("prima")
    prima_str = f"CRC {prima:,.2f}" if prima is not None else "No registrada"

    filas = [
        ("Numero de poliza", poliza.get("numero", "")),
        ("Aseguradora", poliza.get("aseguradora", "")),
        ("Ramo", poliza.get("ramo", "")),
        ("Cedula", poliza.get("cedula", "")),
        ("Vigencia", vigencia),
        ("Prima anual", prima_str),
        ("Forma de pago", poliza.get("pago", "")),
    ]

    pdf.set_font("Helvetica", size=10)
    for campo, valor in filas:
        pdf.cell(45, 8, _latin1(campo), border=1)
        pdf.cell(155, 8, _latin1(valor), border=1)
        pdf.ln()

    pdf.ln(15)

    # ---------- Pie de pagina en gris ----------
    pdf.set_text_color(*gris)
    pdf.set_font("Helvetica", "I", 8)
    pdf.cell(
        0,
        10,
        _latin1("Documento ficticio para fines academicos."),
        ln=True,
        align="C",
    )

    # ---------- Devolver bytes ----------
    salida = pdf.output(dest="S")
    if isinstance(salida, str):
        return salida.encode("latin-1")
    return bytes(salida)