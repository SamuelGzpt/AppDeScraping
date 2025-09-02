from flask import Flask, render_template, request, session, send_file, jsonify
from scraping_simit import consultar_simit
from scraping_policia import consultar_policia  # Importar la versión con bypass
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
        elif metodo_bypass == "image_solver":
            from captcha_image import consultar_policia_con_image_solver
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


@app.route("/consulta_bypass_agresivo", methods=["POST"])
def consulta_bypass_agresivo():
    """
    Ruta alternativa para casos donde el bypass normal no funciona
    """
    nombre = request.form.get("Nombre", "No especificado")
    cedula = request.form.get("cedula", "").strip()
    correo = request.form.get("correo", "")

    print(f"[INFO] Iniciando consulta con bypass agresivo para {nombre} - Cédula: {cedula}")

    # Importar función específica
    from scraping_policia import consultar_policia_bypass_avanzado
    
    try:
        simit_result = consultar_simit(cedula) or "No se encontraron datos en SIMIT"
    except Exception as e:
        print(f"[ERROR] SIMIT: {e}")
        simit_result = f"Error al consultar SIMIT: {e}"

    try:
        policia_result = consultar_policia_bypass_avanzado(cedula)
    except Exception as e:
        print(f"[ERROR] Policía bypass agresivo: {e}")
        policia_result = f"Error al consultar Policía: {e}"

    # Guardar en sesión
    session["nombre"] = nombre
    session["cedula"] = cedula
    session["correo"] = correo
    session["simit_result"] = simit_result
    session["policia_result"] = policia_result
    session["metodo_usado"] = "bypass_agresivo"

    return render_template(
        "success.html",
        nombre=nombre,
        simit_result=simit_result,
        policia_result=policia_result,
        metodo_usado="bypass_agresivo"
    )


@app.route("/test_bypass")
def test_bypass():
    """
    Ruta para probar el bypass del CAPTCHA con una cédula de prueba
    """
    return render_template("test_bypass.html")


@app.route("/test_consulta", methods=["POST"])
def test_consulta():
    """
    Endpoint para probar el bypass con diferentes métodos via AJAX
    """
    try:
        cedula = request.form.get("cedula", "").strip()
        metodo = request.form.get("metodo", "normal")
        
        if not cedula:
            return jsonify({
                "success": False,
                "error": "Cédula requerida"
            }), 400
        
        print(f"[TEST] Probando método '{metodo}' para cédula: {cedula}")
        
        # Ejecutar según método seleccionado
        if metodo == "bypass_simple":
            from scraping_policia import consultar_policia_bypass_captcha
            resultado = consultar_policia_bypass_captcha(cedula)
        elif metodo == "bypass_agresivo":
            from scraping_policia import consultar_policia_bypass_avanzado
            resultado = consultar_policia_bypass_avanzado(cedula)
        elif metodo == "requests_directo":
            from scraping_policia import consultar_policia_request_directo
            resultado = consultar_policia_request_directo(cedula)
        elif metodo == "solver_avanzado":
            try:
                from captcha_solver import consultar_policia_con_solver
                resultado = consultar_policia_con_solver(cedula)
            except ImportError:
                resultado = {"error": "Solver avanzado no disponible", "status": "error"}
        elif metodo == "image_solver":
            try:
                from captcha_image_solver import consultar_policia_con_image_solver
                resultado = consultar_policia_con_image_solver(cedula)
            except ImportError:
                resultado = {"error": "Solver de imágenes no disponible", "status": "error"}
        else:
            # Método normal (automático)
            from scraping_policia import consultar_policia
            resultado = consultar_policia(cedula)
        
        return jsonify({
            "success": True,
            "resultado": resultado,
            "metodo_usado": metodo,
            "cedula": cedula,
            "timestamp": datetime.now().isoformat()
        })
        
    except Exception as e:
        print(f"[ERROR] Error en test_consulta: {str(e)}")
        print(f"[DEBUG] Stack trace: {traceback.format_exc()}")
        
        return jsonify({
            "success": False,
            "error": str(e),
            "metodo_usado": metodo if 'metodo' in locals() else 'desconocido',
            "timestamp": datetime.now().isoformat()
        }), 500


@app.route("/consulta_api", methods=["POST"])
def consulta_api():
    """
    Endpoint API para consultas programáticas (JSON)
    """
    try:
        # Obtener datos del JSON o form-data
        if request.is_json:
            data = request.get_json()
        else:
            data = request.form.to_dict()
        
        cedula = data.get("cedula", "").strip()
        consultar_simit_flag = data.get("consultar_simit", True)
        consultar_policia_flag = data.get("consultar_policia", True)
        metodo_bypass = data.get("metodo_bypass", "normal")
        
        if not cedula:
            return jsonify({
                "success": False,
                "error": "Cédula es requerida"
            }), 400
        
        resultados = {}
        
        # Consultar SIMIT si está habilitado
        if consultar_simit_flag:
            try:
                print(f"[API] Consultando SIMIT para cédula: {cedula}")
                simit_result = consultar_simit(cedula)
                resultados["simit"] = {
                    "success": True,
                    "data": simit_result or "No se encontraron datos"
                }
            except Exception as e:
                print(f"[API ERROR] SIMIT: {e}")
                resultados["simit"] = {
                    "success": False,
                    "error": str(e)
                }
        
        # Consultar Policía si está habilitado
        if consultar_policia_flag:
            try:
                print(f"[API] Consultando Policía para cédula: {cedula} (método: {metodo_bypass})")
                
                if metodo_bypass == "bypass_simple":
                    from scraping_policia import consultar_policia_bypass_captcha
                    policia_result = consultar_policia_bypass_captcha(cedula)
                elif metodo_bypass == "bypass_agresivo":
                    from scraping_policia import consultar_policia_bypass_avanzado
                    policia_result = consultar_policia_bypass_avanzado(cedula)
                elif metodo_bypass == "requests_directo":
                    from scraping_policia import consultar_policia_request_directo
                    policia_result = consultar_policia_request_directo(cedula)
                else:
                    from scraping_policia import consultar_policia
                    if metodo_bypass == "image_solver":
                        from captcha_image_solver import consultar_policia_con_image_solver
                        policia_result = consultar_policia_con_image_solver(cedula)
                    else:
                        policia_result = consultar_policia(cedula)
                    
                    resultados["policia"] = {
                        "success": True,
                    "data": policia_result or "No se encontraron datos"
                }
                
            except Exception as e:
                print(f"[API ERROR] Policía: {e}")
                resultados["policia"] = {
                    "success": False,
                    "error": str(e)
                }
        
        return jsonify({
            "success": True,
            "cedula": cedula,
            "metodo_bypass": metodo_bypass,
            "resultados": resultados,
            "timestamp": datetime.now().isoformat()
        })
        
    except Exception as e:
        print(f"[API ERROR] Error general: {e}")
        return jsonify({
            "success": False,
            "error": f"Error interno del servidor: {str(e)}",
            "timestamp": datetime.now().isoformat()
        }), 500


def extraer_texto_limpio(resultado):
    """Extrae el texto limpio del resultado, sin estructura de diccionario"""
    if isinstance(resultado, dict):
        if 'texto' in resultado:
            return resultado['texto']
        elif 'error' in resultado:
            return f"Error: {resultado['error']}"
        elif 'data' in resultado:
            return str(resultado['data'])
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
    """Genera y descarga un PDF con los resultados de la consulta"""
    try:
        nombre = session.get("nombre", "No especificado")
        cedula = session.get("cedula", "Sin datos")
        correo = session.get("correo", "Sin correo")
        simit_result = session.get("simit_result", "Sin datos")
        policia_result = session.get("policia_result", "Sin datos")
        metodo_usado = session.get("metodo_usado", "No especificado")
        fecha_consulta = session.get("fecha_consulta", datetime.now().strftime("%Y-%m-%d %H:%M:%S"))

        # Extraer texto limpio de los resultados
        texto_simit = extraer_texto_limpio(simit_result)
        texto_policia = extraer_texto_limpio(policia_result)

        buffer = io.BytesIO()
        p = canvas.Canvas(buffer, pagesize=letter)
        width, height = letter

        # Título
        p.setFont("Helvetica-Bold", 18)
        p.drawString(150, height - 50, "Consulta de Antecedentes")
        
        # Subtítulo
        p.setFont("Helvetica", 10)
        p.drawString(200, height - 70, f"Generado el: {fecha_consulta}")

        # Información personal
        p.setFont("Helvetica-Bold", 12)
        p.drawString(50, height - 100, "DATOS PERSONALES")
        
        p.setFont("Helvetica", 11)
        p.drawString(50, height - 120, f"Nombre: {nombre}")
        p.drawString(50, height - 140, f"Cédula: {cedula}")
        
        if correo and correo != "Sin correo":
            p.drawString(50, height - 160, f"Correo: {correo}")
            y_start = height - 180
        else:
            y_start = height - 160
        
        p.drawString(50, y_start, f"Método usado: {metodo_usado}")
        y_start -= 30

        # Línea separadora
        p.line(50, y_start, width - 50, y_start)
        y_start -= 20

        # SIMIT
        p.setFont("Helvetica-Bold", 14)
        p.drawString(50, y_start, "CONSULTA SIMIT")
        y_start -= 5
        p.line(50, y_start, 200, y_start)
        y_start -= 15
        
        # Dibujar texto SIMIT en múltiples líneas
        y_position = dibujar_texto_multilinea(p, texto_simit, 50, y_start, max_width=500, font_size=10)
        
        # Espacio entre secciones
        y_position -= 30

        # Verificar si necesitamos nueva página
        if y_position < 200:
            p.showPage()
            y_position = height - 50

        # Antecedentes Policía
        p.setFont("Helvetica-Bold", 14)
        p.drawString(50, y_position, "ANTECEDENTES POLICÍA")
        y_position -= 5
        p.line(50, y_position, 250, y_position)
        y_position -= 15
        
        # Dibujar texto Policía en múltiples líneas
        final_y = dibujar_texto_multilinea(p, texto_policia, 50, y_position, max_width=500, font_size=10)
        
        # Footer
        if final_y > 100:
            p.setFont("Helvetica", 8)
            p.drawString(50, 50, f"Documento generado automáticamente - {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
            p.drawString(50, 35, "Este documento es solo informativo y no constituye un certificado oficial")

        p.save()
        buffer.seek(0)
        
        # Nombre del archivo
        nombre_archivo = f"consulta_{cedula}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.pdf"
        
        return send_file(
            buffer,
            as_attachment=True,
            download_name=nombre_archivo,
            mimetype="application/pdf"
        )
        
    except Exception as e:
        print(f"[ERROR] Error generando PDF: {e}")
        return f"Error generando PDF: {str(e)}", 500


@app.route("/status")
def status():
    """Endpoint para verificar el estado de la aplicación"""
    try:
        return jsonify({
            "status": "online",
            "timestamp": datetime.now().isoformat(),
            "version": "2.0.0-bypass",
            "methods_available": [
                "normal",
                "bypass_simple", 
                "bypass_agresivo",
                "requests_directo",
                "solver_avanzado",
                "image_solver"
            ]
        })
    except Exception as e:
        return jsonify({
            "status": "error",
            "error": str(e),
            "timestamp": datetime.now().isoformat()
        }), 500


@app.route("/limpiar_sesion")
def limpiar_sesion():
    """Limpia los datos de la sesión"""
    session.clear()
    return jsonify({
        "success": True,
        "message": "Sesión limpiada exitosamente"
    })


@app.errorhandler(404)
def not_found(error):
    """Manejador de errores 404"""
    return render_template("error.html", 
                        error_code=404, 
                        error_message="Página no encontrada"), 404


@app.errorhandler(500)
def internal_error(error):
    """Manejador de errores 500"""
    return render_template("error.html", 
                        error_code=500, 
                        error_message="Error interno del servidor"), 500


if __name__ == "__main__":
    print("🚀 Iniciando servidor Flask con bypass CAPTCHA...")
    print("📍 Endpoints disponibles:")
    print("   - GET  /                    - Página principal")
    print("   - POST /scraping            - Consulta normal")
    print("   - GET  /test_bypass         - Interfaz de testing")
    print("   - POST /test_consulta       - Testing AJAX")
    print("   - POST /consulta_api        - API JSON")
    print("   - GET  /descargar_pdf       - Descargar PDF")
    print("   - GET  /status              - Estado del servidor")
    print("   - GET  /limpiar_sesion      - Limpiar sesión")
    print("\n🔧 Métodos de bypass disponibles:")
    print("   - normal: Automático (requests + selenium)")
    print("   - bypass_simple: Inyección de token")
    print("   - bypass_agresivo: Máximo stealth")
    print("   - requests_directo: Solo HTTP")
    print("   - solver_avanzado: Servicios externos")
    
    app.run(debug=True, host='0.0.0.0', port=5000)