# scraping_simit.py
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException, NoSuchElementException
from webdriver_manager.chrome import ChromeDriverManager


def consultar_simit(cedula):
    options = Options()
    # Si quieres ocultar el navegador, descomenta:
    # options.add_argument("--headless=new")
    options.add_argument("--no-sandbox")
    options.add_argument("--disable-dev-shm-usage")

    driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=options)
    wait = WebDriverWait(driver, 20)

    try:
        driver.get("https://www.fcm.org.co/simit/#/home-public")

        # 1️⃣ Esperar campo de búsqueda y escribir la cédula
        campo_busqueda = wait.until(EC.element_to_be_clickable((By.ID, "txtBusqueda")))
        campo_busqueda.clear()
        campo_busqueda.send_keys(cedula)

        # 2️⃣ Enviar la búsqueda (ENTER o click en el botón de búsqueda)
        campo_busqueda.submit()

        # 3️⃣ Esperar a que aparezca el texto de resultado
        resultado_div = wait.until(EC.visibility_of_element_located((
            By.CSS_SELECTOR,
            "div.col-lg-6.text-lg-left.text-center.px-lg-5.px-3.mt-lg-0.mt-md-5.mt-3"
        )))
        texto = resultado_div.text.strip()

        return {
            "tiene_multas": "NO TIENES COMPARENDOS" not in texto.upper(),
            "texto": texto
        }

    except TimeoutException:
        return {"error": "El sistema del SIMIT no respondió a tiempo."}
    except NoSuchElementException:
        return {"error": "No se encontró un elemento esperado en la página del SIMIT."}
    except Exception as e:
        return {"error": f"Error al consultar SIMIT: {str(e)}"}
    finally:
        driver.quit()
