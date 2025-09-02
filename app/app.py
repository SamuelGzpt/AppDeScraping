from flask import Flask, render_template, request, session, send_file
from scraping_simit import consultar_simit
from scraping_policia import consultar_policia  # Importar la versión mejorada
from reportlab.lib.pagesizes import letter
from reportlab.pdfgen import canvas
import io
import textwrap

app = Flask(__name__)
app.secret_key = "supersecreto"  # Necesario para usar session


@app.route("/")
def index():
    return render_template("index.html")


@app.route("/scraping", methods=["POST"])
def scraping():
    nombre = request.form.get("Nombre", "No especificado")
    cedula = request.form.get("cedula", "").strip()
    correo = request.form.get("correo", "")

    print(f"[INFO] Iniciando consulta para {nombre} - Cédula: {cedula}")

    # Consultar SIMIT
    try:
        print("[INFO] Consultando SIMIT...")
        simit_result = consultar_simit(cedula) or "No se encontraron datos en SIMIT"
        print("[✓] SIMIT completado")
    except Exception as e:
        print(f"[❌] Error SIMIT: {e}")
        simit_result = f"Error al consultar SIMIT: {e}"

    # Consultar Policía con método mejorado
    try:
        print("[INFO] Consultando Policía (método directo)...")
        policia_result = consultar_policia(cedula) or "No se encontraron datos en Policía"
        print("[✓] Policía completado")
    except Exception as e:
        print(f"[❌] Error Policía: {e}")
        policia_result = f"Error al consultar Policía: {e}"

    # Guardar en sesión para descargar PDF después
    session["nombre"] = nombre
    session["cedula"] = cedula
    session["correo"] = correo
    session["simit_result"] = simit_result
    session["policia_result"] = policia_result

    print("[✓] Consulta completada, mostrando resultados")

    return render_template(
        "success.html",
        nombre=nombre,
        simit_result=simit_result,
        policia_result=policia_result
    )


@app.route("/consulta_con_token", methods=["POST"])
def consulta_con_token():
    """
    Ruta para consulta con token específico del reCAPTCHA
    """
    nombre = request.form.get("Nombre", "No especificado")
    cedula = request.form.get("cedula", "").strip()
    correo = request.form.get("correo", "")
    recaptcha_token = request.form.get("recaptcha_token", "")

    print(f"[INFO] Iniciando consulta con token para {nombre} - Cédula: {cedula}")

    # Importar función específica
    from scraping_policia import consultar_policia_token_especifico
    
    try:
        simit_result = consultar_simit(cedula) or "No se encontraron datos en SIMIT"
    except Exception as e:
        simit_result = f"Error al consultar SIMIT: {e}"

    try:
        if recaptcha_token:
            policia_result = consultar_policia_token_especifico(cedula, recaptcha_token)
        else:
            policia_result = consultar_policia(cedula)
    except Exception as e:
        policia_result = f"Error al consultar Policía: {e}"

    # Guardar en sesión
    session["nombre"] = nombre
    session["cedula"] = cedula
    session["correo"] = correo
    session["simit_result"] = simit_result
    session["policia_result"] = policia_result

    return render_template(
        "success.html",
        nombre=nombre,
        simit_result=simit_result,
        policia_result=policia_result
    )


def extraer_texto_limpio(resultado):
    """Extrae el texto limpio del resultado, sin estructura de diccionario"""
    if isinstance(resultado, dict):
        if 'texto' in resultado:
            return resultado['texto']
        elif 'error' in resultado:
            return f"Error: {resultado['error']}"
        else:
            return str(resultado)
    else:
        return str(resultado)


def dibujar_texto_multilinea(canvas_obj, texto, x, y, max_width=500, font_size=10):
    """Dibuja texto en múltiples líneas si es necesario"""
    canvas_obj.setFont("Helvetica", font_size)
    
    # Calcular aproximadamente cuántos caracteres caben por línea
    chars_per_line = max_width // (font_size * 0.6)  # Aproximación
    
    # Dividir el texto en líneas
    lineas = textwrap.wrap(texto, width=int(chars_per_line))
    
    # Dibujar cada línea
    line_height = font_size + 4  # Espaciado entre líneas
    current_y = y
    
    for linea in lineas:
        canvas_obj.drawString(x, current_y, linea)
        current_y -= line_height
    
    return current_y  # Retorna la posición Y final


@app.route("/descargar_pdf")
def descargar_pdf():
    nombre = session.get("nombre", "No especificado")
    cedula = session.get("cedula", "Sin datos")
    correo = session.get("correo", "Sin correo")
    simit_result = session.get("simit_result", "Sin datos")
    policia_result = session.get("policia_result", "Sin datos")

    # Extraer texto limpio de los resultados
    texto_simit = extraer_texto_limpio(simit_result)
    texto_policia = extraer_texto_limpio(policia_result)

    buffer = io.BytesIO()
    p = canvas.Canvas(buffer, pagesize=letter)
    width, height = letter

    # Título
    p.setFont("Helvetica-Bold", 16)
    p.drawString(180, height - 50, "Resultados de la Consulta")

    # Información personal
    p.setFont("Helvetica", 12)
    p.drawString(50, height - 80, f"Nombre: {nombre}")
    p.drawString(50, height - 100, f"Cédula: {cedula}")
    if correo != "Sin correo":
        p.drawString(50, height - 120, f"Correo: {correo}")
        y_start = height - 150
    else:
        y_start = height - 130

    # SIMIT
    p.setFont("Helvetica-Bold", 14)
    p.drawString(50, y_start, "SIMIT:")
    
    # Dibujar texto SIMIT en múltiples líneas
    y_position = dibujar_texto_multilinea(p, texto_simit, 50, y_start - 20, max_width=500, font_size=10)
    
    # Espacio entre secciones
    y_position -= 30

    # Antecedentes Policía
    p.setFont("Helvetica-Bold", 14)
    p.drawString(50, y_position, "Antecedentes Policía:")
    
    # Dibujar texto Policía en múltiples líneas
    y_position -= 20
    final_y = dibujar_texto_multilinea(p, texto_policia, 50, y_position, max_width=500, font_size=10)
    
    # Si el contenido es muy largo y se sale de la página, crear nueva página
    if final_y < 100:
        p.showPage()

    p.showPage()
    p.save()

    buffer.seek(0)
    return send_file(
        buffer,
        as_attachment=True,
        download_name=f"consulta_{nombre.replace(' ', '_')}.pdf",
        mimetype="application/pdf"
    )


if __name__ == "__main__":
    app.run(debug=True)