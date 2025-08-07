import html
from flask import Flask, render_template, request, jsonify, send_file
from scraping_documento_simit import scrape_simit_por_documento
from scraping_documento_policia import antecedentes_judiciales
import pdfkit
import os
import time
from datetime import datetime

app = Flask(__name__)
path_wkhtmltopdf = r'C:\Program Files\wkhtmltopdf\bin\wkhtmltopdf.exe'
config = pdfkit.configuration(wkhtmltopdf=path_wkhtmltopdf)

@app.route("/genera_pdf")
def genera_pdf():
    html = render_template("mi_template.html")
    pdf_file = "salida.pdf"
    pdfkit.from_string(html, pdf_file, configuration=config)
    return "PDF generado"

@app.route("/")
def home():
    return render_template("index.html")
    
@app.route("/api/jobs/simit/completo", methods=["POST"])
def simit_completo():
    nombre = request.form.get("nombre")
    cedula = request.form.get("cedula")
    correo = request.form.get("correo")
    tipo_consulta = request.form.get("tipo_consulta")
    sites = request.form.getlist("sites")
    generar_pdf = request.form.get("generar_pdf") == "on"
    headless = request.form.get("headless") == "on"

    resultados = []
    success = True
    error = None

    # SIMIT por documento
    if "simit_documento" in sites and cedula:
        simit_result = scrape_simit_por_documento(cedula, headless=headless)
        resultados.append({
            "tipo": "documento",
            "identificador": cedula,
            "success": "error" not in simit_result,
            "resultados": simit_result if "error" not in simit_result else None,
            "error": simit_result.get("error") if "error" in simit_result else ""
        })
        if "error" in simit_result:
            success = False
            error = simit_result["error"]

    # Antecedentes Policía
    if "antecedentes_policia" in sites and cedula and nombre:
        primer_nombre = nombre.split()[0]
        primer_apellido = nombre.split()[-1] if len(nombre.split()) > 1 else ""
        antecedentes_result = antecedentes_judiciales("Cédula de Ciudadanía", cedula, primer_apellido, primer_nombre, headless=headless)
        resultados.append({
            "tipo": "antecedentes",
            "identificador": cedula,
            "success": "error" not in antecedentes_result,
            "resultados": antecedentes_result if "error" not in antecedentes_result else None,
            "error": antecedentes_result.get("error") if "error" in antecedentes_result else ""
        })
        if "error" in antecedentes_result:
            success = False
            error = antecedentes_result["error"]

    # Generación PDF (opcional)
    pdf_file = None
    if generar_pdf and resultados:
        try:
            fecha_actual = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            
            # Usar el template mejorado
            html_content = render_template("pdf.html", 
                                         resultados=resultados,
                                         nombre=nombre,
                                         cedula=cedula,
                                         correo=correo,
                                         fecha_consulta=fecha_actual,
                                         fecha_generacion=fecha_actual)
            
            pdf_filename = f"reporte_simit_{cedula}_{int(time.time())}.pdf"
            
            # Opciones para mejorar el PDF
            options = {
                'page-size': 'A4',
                'margin-top': '0.75in',
                'margin-right': '0.75in',
                'margin-bottom': '0.75in',
                'margin-left': '0.75in',
                'encoding': "UTF-8",
                'no-outline': None,
                'enable-local-file-access': None
            }
            
            pdfkit.from_string(html_content, pdf_filename, configuration=config, options=options)
            pdf_file = pdf_filename
            
        except Exception as e:
            print(f"Error generando PDF: {str(e)}")
            pdf_file = None

    return jsonify({
        "success": success,
        "resultados": resultados,
        "nombre": nombre,
        "timestamp": int(time.time()),
        "pdf_generado": pdf_file
    })

@app.route("/api/jobs/simit/pdf/<filename>")
def descargar_pdf(filename):
    try:
        return send_file(filename, as_attachment=True, download_name=f"reporte_simit_{filename}")
    except FileNotFoundError:
        return jsonify({"error": "Archivo PDF no encontrado"}), 404

if __name__ == "__main__":
    app.run(debug=True)