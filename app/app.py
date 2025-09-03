from flask import Flask, render_template, request, session, send_file, jsonify
from scraping_simit import consultar_simit
from scraping_policia import consultar_policia  # Versión limpia con audio solver
from scraping_policia import consultar_policia_con_audio_solver  # Nueva función
from reportlab.lib.pagesizes import letter
from reportlab.pdfgen import canvas
import io
import textwrap
import json
import traceback
from datetime import datetime

app = Flask(__name__)
app.secret_key = "supersecreto123456789"  # Necesario para usar session


@app.route("/")
def index():
    """Página principal con formulario de consulta"""
    return render_template("index.html")


@app.route("/scraping", methods=["POST"])
def scraping():
    """
    Endpoint principal para realizar consultas de antecedentes
    """
    nombre = request.form.get("Nombre", "No especificado")
    cedula = request.form.get("cedula", "").strip()
    correo = request.form.get("correo", "")
    metodo_bypass = request.form.get("metodo_bypass", "audio_captcha")  # Por defecto audio

    print(f"[INFO] {datetime.now()} - Iniciando consulta para {nombre} - Cédula: {cedula}")
    print(f"[INFO] Método seleccionado: {metodo_bypass}")

    # Inicializar resultados
    simit_result = None
    policia_result = None

    # Consultar SIMIT
    try:
        print("[INFO] Consultando SIMIT...")
        simit_result = consultar_simit(cedula) or "No se encontraron datos en SIMIT"
        print("[✓] SIMIT completado exitosamente")
    except Exception as e:
        print(f"[❌] Error SIMIT: {str(e)}")
        print(f"[DEBUG] Stack trace SIMIT: {traceback.format_exc()}")
        simit_result = f"Error al consultar SIMIT: {str(e)}"

    # Consultar Policía con Audio CAPTCHA Solver (método único)
    try:
        print(f"[INFO] Consultando Policía con Audio CAPTCHA Solver...")
        
        # Usar siempre el método de audio CAPTCHA
        policia_result = consultar_policia_con_audio_solver(cedula)
        
        if not policia_result:
            policia_result = "No se encontraron datos en Policía"
        elif policia_result.get("status") == "error":
            print(f"[WARNING] Error en consulta Policía: {policia_result.get('error')}")
        else:
            print("[✓] Policía completado con Audio CAPTCHA Solver exitoso")
        
    except Exception as e:
        print(f"[❌] Error Policía: {str(e)}")
        print(f"[DEBUG] Stack trace Policía: {traceback.format_exc()}")
        policia_result = f"Error al consultar Policía: {str(e)}"

    # Guardar en sesión para descargar PDF después
    session["nombre"] = nombre
    session["cedula"] = cedula
    session["correo"] = correo
    session["simit_result"] = simit_result
    session["policia_result"] = policia_result
    session["metodo_usado"] = "audio_captcha"  # Siempre audio
    session["fecha_consulta"] = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    print(f"[✓] {datetime.now()} - Consulta completada, mostrando resultados")

    return render_template(
        "success.html",
        nombre=nombre,
        cedula=cedula,
        simit_result=simit_result,
        policia_result=policia_result,
        metodo_usado="audio_captcha"
    )


@app.route("/test_audio_captcha", methods=["GET", "POST"])
def test_audio_captcha():
    """
    Ruta específica para probar el solver de audio CAPTCHA
    """
    if request.method == "GET":
        return render_template("test_audio_captcha.html")
    
    try:
        cedula = request.form.get("cedula", "").strip()
        
        if not cedula:
            return jsonify({
                "success": False,
                "error": "Cédula requerida"
            }), 400
        
        print(f"[TEST AUDIO] Probando solver de audio para cédula: {cedula}")
        
        resultado = consultar_policia_con_audio_solver(cedula)
        
        return jsonify({
            "success": True,
            "resultado": resultado,
            "metodo_usado": "audio_captcha",
            "cedula": cedula,
            "timestamp": datetime.now().isoformat()
        })
        
    except Exception as e:
        print(f"[ERROR] Error en test_audio_captcha: {str(e)}")
        print(f"[DEBUG] Stack trace: {traceback.format_exc()}")
        
        return jsonify({
            "success": False,
            "error": str(e),
            "metodo_usado": "audio_captcha",
            "timestamp": datetime.now().isoformat()
        }), 500


@app.route("/consulta_con_token", methods=["POST"])
def consulta_con_token():
    """
    Ruta para consulta con token específico del reCAPTCHA
    (Redirige al método de audio por simplicidad)
    """
    nombre = request.form.get("Nombre", "No especificado")
    cedula = request.form.get("cedula", "").strip()
    correo = request.form.get("correo", "")
    recaptcha_token = request.form.get("recaptcha_token", "")

    print(f"[INFO] Iniciando consulta con audio solver para {nombre} - Cédula: {cedula}")

    try:
        simit_result = consultar_simit(cedula) or "No se encontraron datos en SIMIT"
    except Exception as e:
        simit_result = f"Error al consultar SIMIT: {e}"

    try:
        # Usar siempre el audio solver
        policia_result = consultar_policia_con_audio_solver(cedula)
    except Exception as e:
        policia_result = f"Error al consultar Policía: {e}"

    # Guardar en sesión
    session["nombre"] = nombre
    session["cedula"] = cedula
    session["correo"] = correo
    session["simit_result"] = simit_result
    session["policia_result"] = policia_result
    session["metodo_usado"] = "audio_captcha"

    return render_template(
        "success.html",
        nombre=nombre,
        cedula=cedula,
        simit_result=simit_result,
        policia_result=policia_result,
        metodo_usado="audio_captcha"
    )


@app.route("/download_pdf")
def download_pdf():
    """
    Genera y descarga PDF con los resultados de la consulta
    """
    try:
        # Obtener datos de la sesión
        nombre = session.get("nombre", "No especificado")
        cedula = session.get("cedula", "")
        correo = session.get("correo", "")
        simit_result = session.get("simit_result", "No disponible")
        policia_result = session.get("policia_result", "No disponible")
        fecha_consulta = session.get("fecha_consulta", datetime.now().strftime("%Y-%m-%d %H:%M:%S"))
        
        # Crear PDF en memoria
        buffer = io.BytesIO()
        c = canvas.Canvas(buffer, pagesize=letter)
        width, height = letter
        
        # Título
        c.setFont("Helvetica-Bold", 16)
        c.drawString(50, height - 50, "CONSULTA DE ANTECEDENTES")
        
        # Información personal
        c.setFont("Helvetica", 12)
        y_position = height - 100
        
        c.drawString(50, y_position, f"Nombre: {nombre}")
        y_position -= 20
        c.drawString(50, y_position, f"Cédula: {cedula}")
        y_position -= 20
        c.drawString(50, y_position, f"Correo: {correo}")
        y_position -= 20
        c.drawString(50, y_position, f"Fecha de consulta: {fecha_consulta}")
        y_position -= 40
        
        # Resultados SIMIT
        c.setFont("Helvetica-Bold", 14)
        c.drawString(50, y_position, "RESULTADOS SIMIT:")
        y_position -= 20
        
        c.setFont("Helvetica", 10)
        simit_text = str(simit_result)
        lines = textwrap.wrap(simit_text, width=80)
        for line in lines:
            c.drawString(50, y_position, line)
            y_position -= 15
            if y_position < 100:
                c.showPage()
                y_position = height - 50
        
        y_position -= 20
        
        # Resultados Policía
        c.setFont("Helvetica-Bold", 14)
        c.drawString(50, y_position, "RESULTADOS POLICÍA:")
        y_position -= 20
        
        c.setFont("Helvetica", 10)
        if isinstance(policia_result, dict):
            policia_text = policia_result.get("texto", str(policia_result))
        else:
            policia_text = str(policia_result)
            
        lines = textwrap.wrap(policia_text, width=80)
        for line in lines:
            if y_position < 100:
                c.showPage()
                y_position = height - 50
            c.drawString(50, y_position, line)
            y_position -= 15
        
        # Método usado
        y_position -= 20
        c.setFont("Helvetica-Bold", 12)
        c.drawString(50, y_position, "Método utilizado: Audio CAPTCHA Solver")
        
        c.save()
        buffer.seek(0)
        
        return send_file(
            buffer,
            as_attachment=True,
            download_name=f"antecedentes_{cedula}_{fecha_consulta.replace(':', '-').replace(' ', '_')}.pdf",
            mimetype='application/pdf'
        )
        
    except Exception as e:
        print(f"[ERROR] Error generando PDF: {e}")
        return jsonify({"error": f"Error generando PDF: {str(e)}"}), 500


if __name__ == "__main__":
    print("🚀 Iniciando servidor Flask...")
    print("🎵 Sistema de Audio CAPTCHA Solver activado")
    print("📱 Accede a: http://localhost:5000")
    app.run(debug=True, host="0.0.0.0", port=5000)