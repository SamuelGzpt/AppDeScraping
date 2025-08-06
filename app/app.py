import html
from flask import Flask, render_template, request, jsonify, send_file
from scraping_documento_simit import scrape_simit_por_documento
from scraping_documento_policia import antecedentes_judiciales
import pdfkit
import os
import time

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
        primer_apellido = nombre.split()[-1]
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

    # Puedes agregar otros sitios aquí...

    # Generación PDF (opcional)
    pdf_file = None
    if generar_pdf and resultados:
        from flask import render_template_string
        html = render_template_string("""
        <h1>Resultados de Consulta</h1>
        <ul>
        {% for r in resultados %}
            <li>
                <strong>{{ r.tipo }}:</strong> {{ r.identificador }}
                {% if r.success %}
                    <pre>{{ r.resultados }}</pre>
                {% else %}
                    <span style="color: red;">{{ r.error }}</span>
                {% endif %}
            </li>
        {% endfor %}
        </ul>
        """, resultados=resultados)
        pdf_file = f"resultados_{int(time.time())}.pdf"
        pdfkit.from_string(html, pdf_file, configuration=config)

    return jsonify({
        "success": success,
        "resultados": resultados,
        "nombre": nombre,
        "timestamp": int(time.time()),
        "pdf_generado": pdf_file
    })

@app.route("/api/jobs/simit/pdf/<filename>")
def descargar_pdf(filename):
    return send_file(filename, as_attachment=True)

if __name__ == "__main__":
    app.run(debug=True)