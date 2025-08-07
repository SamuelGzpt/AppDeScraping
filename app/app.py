import html
from flask import Flask, render_template, request, jsonify, send_file, redirect, url_for
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

@app.route("/success")
def success():
    # Obtener parámetros de la URL
    nombre = request.args.get('nombre', '')
    cedula = request.args.get('cedula', '')
    fecha_consulta = request.args.get('fecha_consulta', '')
    consultas_exitosas = request.args.get('consultas_exitosas', '0')
    total_multas = request.args.get('total_multas', '0')
    tiene_antecedentes = request.args.get('tiene_antecedentes', 'false') == 'true'
    pdf_generado = request.args.get('pdf_generado', '')
    
    return render_template("success.html",
                         nombre=nombre,
                         cedula=cedula,
                         fecha_consulta=fecha_consulta,
                         consultas_exitosas=consultas_exitosas,
                         total_multas=total_multas,
                         tiene_antecedentes=tiene_antecedentes,
                         pdf_generado=pdf_generado)
    
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
    total_multas = 0
    tiene_antecedentes = False
    consultas_exitosas = 0

    # SIMIT por documento
    if "simit_documento" in sites and cedula:
        simit_result = scrape_simit_por_documento(cedula, headless=headless)
        if "error" not in simit_result:
            consultas_exitosas += 1
            if simit_result.get("multas_encontradas") and simit_result.get("comparendos"):
                total_multas += len(simit_result["comparendos"])
        
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
        
        if "error" not in antecedentes_result:
            consultas_exitosas += 1
            if antecedentes_result.get("tiene_antecedentes"):
                tiene_antecedentes = True
        
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
    pdf_filename = None
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
            
            pdf_filename = f"reporte_integral_{cedula}_{int(time.time())}.pdf"
            
            # Opciones para mejorar el PDF
            options = {
                'page-size': 'A4',
                'margin-top': '0.5in',
                'margin-right': '0.5in',
                'margin-bottom': '0.5in',
                'margin-left': '0.5in',
                'encoding': "UTF-8",
                'no-outline': None,
                'enable-local-file-access': None,
                'print-media-type': None
            }
            
            pdfkit.from_string(html_content, pdf_filename, configuration=config, options=options)
            
        except Exception as e:
            print(f"Error generando PDF: {str(e)}")
            pdf_filename = None

    # Si todo es exitoso, redirigir a página de éxito
    if success and resultados:
        fecha_consulta = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        return redirect(url_for('success', 
                              nombre=nombre or '',
                              cedula=cedula,
                              fecha_consulta=fecha_consulta,
                              consultas_exitosas=consultas_exitosas,
                              total_multas=total_multas,
                              tiene_antecedentes=str(tiene_antecedentes).lower(),
                              pdf_generado=pdf_filename or ''))
    
    # Si hay errores, devolver JSON como antes
    return jsonify({
        "success": success,
        "resultados": resultados,
        "nombre": nombre,
        "timestamp": int(time.time()),
        "pdf_generado": pdf_filename,
        "error": error
    })

@app.route("/api/jobs/simit/pdf/<filename>")
def descargar_pdf(filename):
    try:
        return send_file(filename, as_attachment=True, download_name=f"reporte_integral_{filename}")
    except FileNotFoundError:
        return jsonify({"error": "Archivo PDF no encontrado"}), 404

if __name__ == "__main__":
    app.run(debug=True)