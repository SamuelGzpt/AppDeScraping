from flask import Flask, render_template, request, session, send_file
from scraping_simit import consultar_simit
from scraping_policia import consultar_policia
from reportlab.lib.pagesizes import letter
from reportlab.pdfgen import canvas
import io

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

    try:
        simit_result = consultar_simit(cedula) or "No se encontraron datos en SIMIT"
    except Exception as e:
        simit_result = f"Error al consultar SIMIT: {e}"

    try:
        policia_result = consultar_policia(cedula) or "No se encontraron datos en Policía"
    except Exception as e:
        policia_result = f"Error al consultar Policía: {e}"

    # Guardar en sesión para descargar PDF después
    session["nombre"] = nombre
    session["cedula"] = cedula
    session["simit_result"] = simit_result
    session["policia_result"] = policia_result

    return render_template(
        "success.html",
        nombre=nombre,
        simit_result=simit_result,
        policia_result=policia_result
    )


@app.route("/descargar_pdf")
def descargar_pdf():
    nombre = session.get("nombre", "No especificado")
    cedula = session.get("cedula", "Sin datos")
    simit_result = session.get("simit_result", "Sin datos")
    policia_result = session.get("policia_result", "Sin datos")

    buffer = io.BytesIO()
    p = canvas.Canvas(buffer, pagesize=letter)
    width, height = letter

    # Título
    p.setFont("Helvetica-Bold", 16)
    p.drawString(180, height - 50, "Resultados de la Consulta")

    # Nombre
    p.setFont("Helvetica", 12)
    p.drawString(50, height - 80, f"Nombre: {nombre}")

    #Cedula
    p.setFont("Helvetica", 12)
    p.drawString(50, height - 100, f"Cedula: {cedula}")

    # SIMIT
    p.setFont("Helvetica-Bold", 14)
    p.drawString(50, height - 120, "SIMIT:")
    p.setFont("Helvetica", 10)
    text_obj = p.beginText(50, height - 140)
    text_obj.textLines(str(simit_result))
    p.drawText(text_obj)

    # Antecedentes Policía
    p.setFont("Helvetica-Bold", 14)
    p.drawString(50, height - 300, "Antecedentes Policía:")
    p.setFont("Helvetica", 10)
    text_obj = p.beginText(50, height - 320)
    text_obj.textLines(str(policia_result))
    p.drawText(text_obj)

    p.showPage()
    p.save()

    buffer.seek(0)
    return send_file(
        buffer,
        as_attachment=True,
        download_name=f"consulta_{nombre}.pdf",
        mimetype="application/pdf"
    )


if __name__ == "__main__":
    app.run(debug=True)
