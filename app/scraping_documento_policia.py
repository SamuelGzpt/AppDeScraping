from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

def antecedentes_judiciales(tipo_doc, numero_doc, primer_apellido, primer_nombre, headless=True):
    """
    Consulta antecedentes judiciales en la página de la Policía Nacional de Colombia.
    Requiere resolver el captcha manualmente si headless=False.
    """
    options = Options()
    if headless:
        options.add_argument("--headless")
    options.add_argument("--disable-gpu")
    options.add_argument("--window-size=1920,1080")
    service = Service("C:/chromedriver/chromedriver-win64/chromedriver.exe")
    driver = webdriver.Chrome(options=options, service=service)
    resultado = {}
    try:
        driver.get('https://antecedentes.policia.gov.co:7005/WebJudicial/')
        wait = WebDriverWait(driver, 15)

        # Selecciona el tipo de documento
        sel_tipo_doc = wait.until(EC.presence_of_element_located((By.ID, "cbotipodocumento")))
        for option in sel_tipo_doc.find_elements(By.TAG_NAME, 'option'):
            if tipo_doc.lower() in option.text.lower():
                option.click()
                break

        # Llena los campos
        wait.until(EC.presence_of_element_located((By.ID, "NoDocumento"))).send_keys(numero_doc)
        wait.until(EC.presence_of_element_located((By.ID, "PrimerNombre"))).send_keys(primer_nombre)
        wait.until(EC.presence_of_element_located((By.ID, "PrimerApellido"))).send_keys(primer_apellido)

        # Captcha manual
        if not headless:
            input("Resuelve el captcha en el navegador y presiona Enter para continuar...")

        # Enviar el formulario
        btn = wait.until(EC.element_to_be_clickable((By.ID, "btnConsultar")))
        btn.click()

        # Espera el mensaje de resultado
        try:
            mensaje = WebDriverWait(driver, 10).until(
                EC.visibility_of_element_located((By.ID, "mensaje"))
            ).text
            resultado["mensaje"] = mensaje
        except Exception:
            resultado["mensaje"] = "No se pudo extraer el resultado. Verifica manualmente."
    except Exception as e:
        resultado = {"error": str(e)}
    finally:
        driver.quit()
    return resultado