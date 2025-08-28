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
    options.add_experimental_option("excludeSwitches", ["enable-automation"])
    options.add_experimental_option('useAutomationExtension', False)

    driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=options)
    driver.execute_script("Object.defineProperty(navigator, 'webdriver', {get: () => undefined})")
    wait = WebDriverWait(driver, 30)

    try:
        driver.get("https://antecedentes.policia.gov.co:7005/WebJudicial/index.xhtml")

        # 1️ Aceptar términos y condiciones
        aceptar_radio = wait.until(EC.element_to_be_clickable((By.ID, "aceptaOption:0")))
        driver.execute_script("arguments[0].click();", aceptar_radio)

        # 2️ Continuar a la página de consulta
        wait.until(lambda d: d.find_element(By.ID, "continuarBtn").is_enabled())
        time.sleep(1)
        continuar_btn = driver.find_element(By.ID, "continuarBtn")
        driver.execute_script("arguments[0].click();", continuar_btn)

        # 3️ Ingresar cédula
        campo_cedula = wait.until(EC.element_to_be_clickable((By.ID, "cedulaInput")))
        campo_cedula.clear()
        campo_cedula.send_keys(str(cedula))

        # 4️ Pausa para resolver CAPTCHA manualmente
        print("\n[INFO] Resuelve el reCAPTCHA manualmente en la ventana del navegador.")
        input("Presiona ENTER aquí cuando hayas resuelto el reCAPTCHA...\n")

        # 5️ Click en consultar
        consultar_btn = wait.until(EC.element_to_be_clickable((By.ID, "j_idt17")))
        driver.execute_script("arguments[0].click();", consultar_btn)

        # 6️ Obtener resultado
        resultado_el = wait.until(EC.visibility_of_element_located((By.ID, "form:mensajeCiudadano")))
        texto = resultado_el.text.strip()

        return {
            "tiene_antecedentes": "NO TIENE ASUNTOS PENDIENTES CON LAS AUTORIDADES JUDICIALES" not in texto.upper(),
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