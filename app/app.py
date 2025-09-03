from flask import Flask, render_template, request, session, send_file, jsonify
from scraping_simit import consultar_simit
from scraping_policia import consultar_policia  # Versión con bypass
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
    metodo_bypass = request.form.get("metodo_bypass", "normal")

    print(f"[INFO] {datetime.now()} - Iniciando consulta para {nombre} - Cédula: {cedula}")
    print(f"[INFO] Método de bypass seleccionado: {metodo_bypass}")

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

    # Consultar Policía con bypass de CAPTCHA según método seleccionado
    try:
        print(f"[INFO] Consultando Policía con bypass de CAPTCHA (método: {metodo_bypass})...")
        
        if metodo_bypass == "bypass_simple":
            from scraping_policia import consultar_policia_bypass_captcha
            policia_result = consultar_policia_bypass_captcha(cedula)
        elif metodo_bypass == "bypass_agresivo":
            from scraping_policia import consultar_policia_bypass_avanzado
            policia_result = consultar_policia_bypass_avanzado(cedula)
        elif metodo_bypass == "requests_directo":
            from scraping_policia import consultar_policia_request_directo
            policia_result = consultar_policia_request_directo(cedula)
        elif metodo_bypass == "solver_avanzado":
            from captcha_solver import consultar_policia_con_solver
            policia_result = consultar_policia_con_solver(cedula)
        elif metodo_bypass == "audio_captcha":
            # NUEVO: Resolver CAPTCHA de audio
            policia_result = consultar_policia_con_audio_solver(cedula)
        elif metodo_bypass == "image_solver":
            from captcha_image_solver import consultar_policia_con_image_solver
            policia_result = consultar_policia_con_image_solver(cedula)
        else:
            # Método automático (normal) - usa múltiples estrategias
            policia_result = consultar_policia(cedula)
        
        if not policia_result:
            policia_result = "No se encontraron datos en Policía"
        
        print("[✓] Policía completado con bypass exitoso")
        
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
    session["metodo_usado"] = metodo_bypass
    session["fecha_consulta"] = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    print(f"[✓] {datetime.now()} - Consulta completada, mostrando resultados")

    return render_template(
        "success.html",
        nombre=nombre,
        cedula=cedula,
        simit_result=simit_result,
        policia_result=policia_result,
        metodo_usado=metodo_bypass
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
    (Mantenida por compatibilidad)
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


@app.route("/")
def index():
    """Página principal con formulario de consulta"""
    return render_template("index.html")
