from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

def scrape_simit_por_documento(numero_doc, headless=True):
    """
    Consulta comparendos/multas en el SIMIT usando Selenium.
    - numero_doc: str (puede ser cédula, placa, comparendo o resolución)
    - headless: bool (True para no mostrar el navegador)
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
        driver.get("https://www.fcm.org.co/simit/#/home-public")
        wait = WebDriverWait(driver, 15)

        # Espera el campo de texto único
        campo = wait.until(EC.visibility_of_element_located(
            (By.XPATH, "//input[@placeholder='Ingrese su número de documento, placa, comparendo o resolución']")
        ))
        campo.clear()
        campo.send_keys(numero_doc)

        # Haz clic en el botón "Consultar"
        boton = wait.until(EC.element_to_be_clickable(
            (By.XPATH, "//button[contains(., 'Consultar')]")
        ))
        boton.click()

        # Espera algún resultado (tabla o mensaje)
        wait.until(
            EC.any_of(
                EC.visibility_of_element_located((By.XPATH, "//table")),
                EC.visibility_of_element_located((By.XPATH, "//*[contains(., 'No se encontraron resultados')]"))
            )
        )

        # Extrae los resultados
        rows = driver.find_elements(By.XPATH, "//table//tbody/tr")
        comparendos = []
        for row in rows:
            celdas = row.find_elements(By.TAG_NAME, "td")
            if celdas:
                comparendo = {
                    "fecha": celdas[0].text,
                    "numero": celdas[1].text,
                    "secretaria": celdas[2].text,
                    "valor": celdas[3].text,
                    "estado": celdas[4].text
                }
                comparendos.append(comparendo)

        resultado = {
            "numero_documento": numero_doc,
            "comparendos": comparendos,
            "multas_encontradas": bool(comparendos)
        }
    except Exception as e:
        resultado = {"error": str(e)}
    finally:
        driver.quit()
    return resultado
