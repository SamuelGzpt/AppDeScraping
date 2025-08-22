# scraping_policia.py
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException, NoSuchElementException
from webdriver_manager.chrome import ChromeDriverManager
import time


def consultar_policia(cedula):
    options = Options()
    # Si quieres ocultar el navegador, descomenta:
    # options.add_argument("--headless=new")
    options.add_argument("--no-sandbox")
    options.add_argument("--disable-dev-shm-usage")

    driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=options)
    wait = WebDriverWait(driver, 20)

    try:
        driver.get("https://antecedentes.policia.gov.co:7005/WebJudicial/index.xhtml")

        # 1️ Seleccionar aceptar términos
        aceptar_radio = wait.until(EC.element_to_be_clickable((By.ID, "aceptaOption:0")))
        driver.execute_script("arguments[0].click();", aceptar_radio)

        # 2️ Esperar a que el botón 'continuarBtn' se habilite
        wait.until(lambda d: d.find_element(By.ID, "continuarBtn").is_enabled())
        continuar_btn = driver.find_element(By.ID, "continuarBtn")
        driver.execute_script("arguments[0].click();", continuar_btn)

        # 3️ Esperar campo de cédula
        campo_cedula = wait.until(EC.element_to_be_clickable((By.ID, "form:cedula")))
        campo_cedula.clear()
        campo_cedula.send_keys(cedula)

        # 4️ Pausa para resolver el CAPTCHA manualmente
        print("\n[INFO] Resuelve el CAPTCHA manualmente en la ventana del navegador.")
        input("Presiona ENTER aquí cuando hayas resuelto el CAPTCHA...\n")

        # 5️ Click en 'Enviar' (por si no se envía solo)
        try:
            enviar_btn = wait.until(EC.element_to_be_clickable((By.ID, "continuarBtn")))
            driver.execute_script("arguments[0].click();", enviar_btn)
        except TimeoutException:
            pass  # en algunos casos la página carga automáticamente después del captcha

        # 6️ Esperar y obtener resultado
        resultado_el = wait.until(EC.visibility_of_element_located((By.ID, "form:j_idt8_content")))
        texto = resultado_el.text.strip()

        return {
            "tiene_antecedentes": "ANTECEDENTES" in texto.upper(),
            "texto": texto
        }

    except TimeoutException:
        return {"error": "El sistema de Policía no respondió a tiempo."}
    except NoSuchElementException:
        return {"error": "No se encontró un elemento esperado en la página de la Policía."}
    except Exception as e:
        return {"error": f"Error al consultar Policía: {str(e)}"}
    finally:
        driver.quit()
