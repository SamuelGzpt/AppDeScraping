from flask import Flask, render_template, request, session, send_file, jsonify
from scraping_simit import consultar_simit
from scraping_policia import consultar_policia  # Versión corregida
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
    Endpoint principal para realizar consultas de antecedentes con manejo corregido
    """
    nombre = request.form.get("Nombre", "No especificado")
    cedula = request.form.get("cedula", "").strip()
    correo = request.form.get("correo", "")

    print(f"[INFO] {datetime.now()} - Iniciando consulta REAL para {nombre} - Cédula: {cedula}")

    # Inicializar resultados
    simit_result = None
    policia_result = None
    simit_status = "pendiente"
    policia_status = "pendiente"
    metodos_usados = []

    # Consultar SIMIT
    try:
        print("[INFO] 🚗 Consultando SIMIT...")
        simit_response = consultar_simit(cedula)
        
        # Manejar respuesta del SIMIT correctamente
        if isinstance(simit_response, dict):
            if simit_response.get("error"):
                simit_result = f"Error en SIMIT: {simit_response['error']}"
                simit_status = "error"
            elif simit_response.get("texto"):
                simit_result = simit_response["texto"]
                simit_status = "exitoso"
                print("[✅] SIMIT completado exitosamente")
            else:
                simit_result = "No se encontraron infracciones de tránsito registradas"
                simit_status = "sin_datos"
        else:
            # Si no es diccionario, usar como texto directo
            simit_result = str(simit_response) if simit_response else "No se encontraron infracciones de tránsito"
            simit_status = "exitoso"
            
    except Exception as e:
        print(f"[❌] Error SIMIT: {str(e)}")
        print(f"[DEBUG] Stack trace SIMIT: {traceback.format_exc()}")
        simit_result = f"No se pudo consultar SIMIT: {str(e)}"
        simit_status = "error"

    # Consultar Policía con sistema REAL (sin simulación)
    try:
        print(f"[INFO] 🛡️ Consultando Antecedentes Policiales (Sistema REAL)...")
        
        policia_response = consultar_policia(cedula)
        
        if isinstance(policia_response, dict):
            if policia_response.get("status") == "success":
                print(f"[✅] Policía completado exitosamente con método: {policia_response.get('metodo', 'desconocido')}")
                policia_status = "exitoso"
                metodos_usados.append(policia_response.get('metodo', 'consulta_real'))
                
                # Extraer texto del resultado
                policia_text = policia_response.get("texto", "Consulta completada")
                tiene_antecedentes = policia_response.get("tiene_antecedentes", False)
                
                # Mostrar resultado REAL sin modificaciones
                if tiene_antecedentes:
                    policia_result = f"⚠️ RESULTADO ENCONTRADO:\n{policia_text}"
                else:
                    policia_result = f"✅ RESULTADO OBTENIDO:\n{policia_text}"
                    
            else:
                print(f"[⚠️] Error en consulta Policía: {policia_response.get('error', 'Error desconocido')}")
                policia_result = f"Error en consulta: {policia_response.get('error', 'Error desconocido')}"
                policia_status = "error"
        else:
            # Si no es diccionario, usar como texto directo
            policia_result = str(policia_response) if policia_response else "No se pudo completar la consulta"
            policia_status = "exitoso"
            metodos_usados.append("consulta_directa")
        
    except Exception as e:
        print(f"[❌] Error Policía: {str(e)}")
        print(f"[DEBUG] Stack trace Policía: {traceback.format_exc()}")
        policia_result = f"Error al consultar antecedentes policiales: {str(e)}"
        policia_status = "error"

    # Preparar resumen de consulta
    consulta_exitosa = simit_status in ["exitoso", "sin_datos"] and policia_status in ["exitoso", "sin_datos"]
    
    # Guardar en sesión para descargar PDF después - CORREGIDO
    session["nombre"] = nombre
    session["cedula"] = cedula
    session["correo"] = correo
    session["simit_result"] = simit_result  # CORREGIDO: era session["texto"]
    session["policia_result"] = policia_result
    session["simit_status"] = simit_status
    session["policia_status"] = policia_status
    session["metodos_usados"] = metodos_usados
    session["consulta_exitosa"] = consulta_exitosa
    session["fecha_consulta"] = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    print(f"[✅] {datetime.now()} - Consulta completada, mostrando resultados REALES")
    print(f"[INFO] 📊 Estado final - SIMIT: {simit_status}, Policía: {policia_status}")

    return render_template(
        "success.html",
        nombre=nombre,
        cedula=cedula,
        simit_result=simit_result,
        policia_result=policia_result,
        simit_status=simit_status,
        policia_status=policia_status,
        consulta_exitosa=consulta_exitosa,
        metodos_usados=metodos_usados
    )


@app.route("/test_real_scraping", methods=["GET", "POST"])
def test_real_scraping():
    """
    Ruta para probar el scraping REAL (sin simulaciones)
    """
    if request.method == "GET":
        return render_template("test_real.html")
    
    try:
        cedula = request.form.get("cedula", "").strip()
        
        if not cedula:
            return jsonify({
                "success": False,
                "error": "Cédula requerida"
            }), 400
        
        print(f"[TEST REAL] Probando scraping real para cédula: {cedula}")
        
        # Probar SIMIT
        print("[INFO] Probando SIMIT...")
        simit_resultado = consultar_simit(cedula)
        
        # Probar Policía
        print("[INFO] Probando Policía...")
        policia_resultado = consultar_policia(cedula)
        
        return jsonify({
            "success": True,
            "resultados": {
                "simit": simit_resultado,
                "policia": policia_resultado
            },
            "cedula": cedula,
            "timestamp": datetime.now().isoformat()
        })
        
    except Exception as e:
        print(f"[ERROR] Error en test_real_scraping: {str(e)}")
        print(f"[DEBUG] Stack trace: {traceback.format_exc()}")
        
        return jsonify({
            "success": False,
            "error": str(e),
            "timestamp": datetime.now().isoformat()
        }), 500


@app.route("/download_pdf")
@app.route("/descargar_pdf")  # Alias para compatibilidad
def download_pdf():
    """
    Genera y descarga PDF corregido con los resultados de la consulta
    """
    try:
        # Obtener datos de la sesión - CORREGIDO
        nombre = session.get("nombre", "No especificado")
        cedula = session.get("cedula", "")
        correo = session.get("correo", "")
        simit_result = session.get("simit_result", "No disponible")  # CORREGIDO: era session.get("texto")
        policia_result = session.get("policia_result", "No disponible")
        simit_status = session.get("simit_status", "unknown")
        policia_status = session.get("policia_status", "unknown")
        metodos_usados = session.get("metodos_usados", [])
        consulta_exitosa = session.get("consulta_exitosa", False)
        fecha_consulta = session.get("fecha_consulta", datetime.now().strftime("%Y-%m-%d %H:%M:%S"))
        
        # Crear PDF en memoria
        buffer = io.BytesIO()
        c = canvas.Canvas(buffer, pagesize=letter)
        width, height = letter
        
        # Título principal
        c.setFont("Helvetica-Bold", 18)
        c.drawString(50, height - 50, "CONSULTA DE ANTECEDENTES - RESULTADOS REALES")
        
        # Línea decorativa
        c.setStrokeColorRGB(0.2, 0.4, 0.8)
        c.setLineWidth(2)
        c.line(50, height - 65, width - 50, height - 65)
        
        # Estado general de la consulta
        y_position = height - 100
        c.setFont("Helvetica-Bold", 12)
        
        if consulta_exitosa:
            c.setFillColorRGB(0, 0.6, 0)  # Verde
            c.drawString(50, y_position, "✓ CONSULTA COMPLETADA EXITOSAMENTE")
        else:
            c.setFillColorRGB(0.8, 0.4, 0)  # Naranja
            c.drawString(50, y_position, "⚠ CONSULTA COMPLETADA CON OBSERVACIONES")
        
        # Resetear color a negro
        c.setFillColorRGB(0, 0, 0)
        y_position -= 30
        
        # Información personal
        c.setFont("Helvetica-Bold", 14)
        c.drawString(50, y_position, "INFORMACIÓN PERSONAL")
        y_position -= 20
        
        c.setFont("Helvetica", 11)
        c.drawString(50, y_position, f"Nombre: {nombre}")
        y_position -= 15
        c.drawString(50, y_position, f"Cédula: {cedula}")
        y_position -= 15
        c.drawString(50, y_position, f"Correo: {correo}")
        y_position -= 15
        c.drawString(50, y_position, f"Fecha de consulta: {fecha_consulta}")
        y_position -= 30
        
        # Resultados SIMIT - CORREGIDO
        c.setFont("Helvetica-Bold", 14)
        c.drawString(50, y_position, "🚗 RESULTADOS SIMIT (INFRACCIONES DE TRÁNSITO)")
        y_position -= 20
        
        # Estado SIMIT
        c.setFont("Helvetica-Bold", 10)
        status_colors = {
            "exitoso": (0, 0.6, 0),      # Verde
            "sin_datos": (0.6, 0.6, 0),  # Amarillo
            "error": (0.8, 0, 0),        # Rojo
            "unknown": (0.5, 0.5, 0.5)   # Gris
        }
        
        color = status_colors.get(simit_status, (0, 0, 0))
        c.setFillColorRGB(*color)
        status_text = {
            "exitoso": "✓ Consulta exitosa",
            "sin_datos": "◯ Sin datos encontrados", 
            "error": "✗ Error en consulta",
            "unknown": "? Estado desconocido"
        }
        c.drawString(50, y_position, f"Estado: {status_text.get(simit_status, simit_status)}")
        c.setFillColorRGB(0, 0, 0)  # Resetear a negro
        y_position -= 15
        
        # Contenido SIMIT - CORREGIDO para mostrar el resultado real
        c.setFont("Helvetica", 9)
        if simit_result and simit_result != "No disponible":
            simit_text = str(simit_result)
        else:
            simit_text = "No se pudo obtener información del SIMIT"
        
        # Procesar texto del SIMIT línea por línea
        lines = textwrap.wrap(simit_text, width=85)
        for line in lines:
            if y_position < 100:
                c.showPage()
                y_position = height - 50
            c.drawString(50, y_position, line)
            y_position -= 12
        
        y_position -= 25
        
        # Resultados Policía - REAL
        c.setFont("Helvetica-Bold", 14)
        c.drawString(50, y_position, "🛡️ RESULTADOS ANTECEDENTES POLICIALES (REALES)")
        y_position -= 20
        
        # Estado Policía
        c.setFont("Helvetica-Bold", 10)
        color = status_colors.get(policia_status, (0, 0, 0))
        c.setFillColorRGB(*color)
        c.drawString(50, y_position, f"Estado: {status_text.get(policia_status, policia_status)}")
        c.setFillColorRGB(0, 0, 0)
        y_position -= 15
        
        # Métodos usados
        if metodos_usados:
            c.setFont("Helvetica", 9)
            c.drawString(50, y_position, f"Métodos utilizados: {', '.join(metodos_usados)}")
            y_position -= 15
        
        # Contenido Policía - REAL sin simulación
        c.setFont("Helvetica", 9)
        if isinstance(policia_result, dict):
            policia_text = policia_result.get("texto", str(policia_result))
        else:
            policia_text = str(policia_result) if policia_result else "No se pudo obtener resultado"
            
        lines = textwrap.wrap(policia_text, width=85)
        for line in lines:
            if y_position < 100:
                c.showPage()
                y_position = height - 50
            c.drawString(50, y_position, line)
            y_position -= 12
        
        # # Información técnica (al final)
        # if y_position < 150:
        #     c.showPage()
        #     y_position = height - 50
        
        # y_position -= 30
        # c.setFont("Helvetica-Bold", 12)
        # c.drawString(50, y_position, "INFORMACIÓN TÉCNICA")
        # y_position -= 15
        
        # c.setFont("Helvetica", 9)
        # c.drawString(50, y_position, "Sistema: Consulta Automatizada de Antecedentes v3.0 REAL")
        # y_position -= 12
        # c.drawString(50, y_position, f"Tecnología: Scraping real con resolución de CAPTCHA por audio")
        # y_position -= 12
        # c.drawString(50, y_position, f"Métodos aplicados: {len(metodos_usados)} estrategia(s) reales")
        # y_position -= 12
        # c.drawString(50, y_position, "IMPORTANTE: Estos son resultados REALES obtenidos directamente de los sistemas oficiales")
        # y_position -= 12
        # c.drawString(50, y_position, "Validez: Este reporte contiene información real pero no constituye certificación oficial")
        
        # Footer
        c.setFont("Helvetica", 8)
        c.drawString(50, 30, f"Generado el {datetime.now().strftime('%Y-%m-%d %H:%M:%S')} | Sistema de Consulta Real")
        
        c.save()
        buffer.seek(0)
        
        return send_file(
            buffer,
            as_attachment=True,
            download_name=f"antecedentes_REALES_{cedula}_{fecha_consulta.replace(':', '-').replace(' ', '_')}.pdf",
            mimetype='application/pdf'
        )
        
    except Exception as e:
        print(f"[ERROR] Error generando PDF: {e}")
        print(f"[DEBUG] Stack trace PDF: {traceback.format_exc()}")
        return jsonify({"error": f"Error generando PDF: {str(e)}"}), 500


@app.route("/status")
def status():
    """
    Endpoint para verificar el estado del sistema
    """
    return jsonify({
        "status": "active",
        "version": "3.0_REAL",
        "features": [
            "real_captcha_audio_solving",
            "no_simulation_police_scraping", 
            "fixed_simit_pdf_display",
            "enhanced_pdf_reports_with_real_data"
        ],
        "timestamp": datetime.now().isoformat(),
        "warning": "Este sistema realiza consultas REALES - sin simulaciones"
    })


if __name__ == "__main__":
    print("🚀 Iniciando servidor Flask REAL...")
    print("🎵 Sistema de Resolución REAL de CAPTCHA por Audio activado")
    print("🛡️ Scraping REAL de antecedentes policiales (sin simulación)")
    print("🚗 Corrección de visualización de resultados SIMIT en PDF")
    print("📱 Accede a: http://localhost:5000")
    print("📊 Estado del sistema: http://localhost:5000/status")
    print("⚠️  ADVERTENCIA: Este sistema realiza consultas REALES en los sistemas oficiales")
    app.run(debug=True, host="0.0.0.0", port=5000)  