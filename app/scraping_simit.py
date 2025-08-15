# scraping_simit.py
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException, NoSuchElementException
from webdriver_manager.chrome import ChromeDriverManager
import time


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

        # 🔹 CERRAR MODAL SI APARECE
        try:
            # Esperar más tiempo para que el modal aparezca
            time.sleep(5)
            
            # Imprimir todos los elementos de la página para debug
            print("Buscando modal en la página...")
            
            # Buscar por texto '×' que es común en botones de cerrar
            close_buttons = driver.find_elements(By.XPATH, "//*[contains(text(), '×')]")
            print(f"Encontrados {len(close_buttons)} elementos con '×'")
            
            # Buscar por diferentes atributos específicos del botón
            modal_close_selectors = [
                "//button[@data-dismiss='modal']",
                "//button[contains(@class, 'modal-info-close')]",
                "//button[contains(@class, 'close')]",
                "//span[contains(@class, 'modal-info-close')]/..",
                "//button[@aria-label='Cerrar.']",
                "//*[@data-insuit-click]",
                "//*[contains(@data-insuit-click, 'modalInformation')]",
                "//span[text()='×']/..",
                "//*[contains(@class, 'modal')]//button",
            ]
            
            modal_closed = False
            
            # Intentar con XPath
            for xpath in modal_close_selectors:
                try:
                    elements = driver.find_elements(By.XPATH, xpath)
                    print(f"Selector '{xpath}': encontrados {len(elements)} elementos")
                    for element in elements:
                        try:
                            if element.is_displayed() and element.is_enabled():
                                print(f"Intentando hacer clic en elemento: {element.tag_name}")
                                driver.execute_script("arguments[0].click();", element)
                                time.sleep(2)
                                modal_closed = True
                                print("¡Modal cerrado exitosamente!")
                                break
                        except Exception as click_error:
                            print(f"Error al hacer clic: {click_error}")
                            continue
                    if modal_closed:
                        break
                except Exception as search_error:
                    print(f"Error buscando con '{xpath}': {search_error}")
                    continue
            
            # Si no funciona, intentar ejecutar JavaScript directamente
            if not modal_closed:
                print("Intentando cerrar modal con JavaScript...")
                js_scripts = [
                    "document.querySelector('button.close')?.click();",
                    "document.querySelector('.modal-info-close')?.click();",
                    "document.querySelector('[data-dismiss=\"modal\"]')?.click();",
                    "$('.modal').modal('hide');",  # Si usan Bootstrap/jQuery
                    "document.querySelector('#modalInformation')?.remove();",
                ]
                
                for script in js_scripts:
                    try:
                        driver.execute_script(script)
                        time.sleep(1)
                        print(f"Ejecutado: {script}")
                    except Exception as js_error:
                        print(f"Error con script '{script}': {js_error}")
                
                modal_closed = True
                print("Scripts de JavaScript ejecutados")
            
            if not modal_closed:
                print("No se pudo cerrar el modal automáticamente")
                
        except Exception as e:
            print(f"Error general al manejar modal: {e}")

        # 1️⃣ Esperar campo de búsqueda y escribir la cédula
        campo_busqueda = wait.until(EC.element_to_be_clickable((By.ID, "txtBusqueda")))
        campo_busqueda.clear()
        campo_busqueda.send_keys(cedula)

        # 2️⃣ Buscar y hacer clic en el botón de búsqueda específico
        try:
            # Buscar el botón por el ícono bx-search
            boton_buscar_selectors = [
                "//em[contains(@class, 'bx-search')]/..",  # Botón padre del ícono
                "//button[.//em[contains(@class, 'bx-search')]]",  # Botón que contiene el ícono
                "//*[contains(@class, 'bx-search')]/..",
                "//em[@class='bx bx-search align-middle fs-27']/..",
                "button:has(em.bx-search)",  # CSS selector alternativo
            ]
            
            boton_encontrado = False
            for selector in boton_buscar_selectors:
                try:
                    if selector.startswith("//"):  # XPath
                        boton_buscar = driver.find_element(By.XPATH, selector)
                    else:  # CSS Selector
                        boton_buscar = driver.find_element(By.CSS_SELECTOR, selector)
                    
                    if boton_buscar.is_displayed() and boton_buscar.is_enabled():
                        print(f"Botón de búsqueda encontrado con selector: {selector}")
                        driver.execute_script("arguments[0].click();", boton_buscar)
                        boton_encontrado = True
                        break
                        
                except NoSuchElementException:
                    continue
                except Exception as e:
                    print(f"Error con selector '{selector}': {e}")
                    continue
            
            if not boton_encontrado:
                print("No se encontró el botón de búsqueda específico, usando submit()")
                campo_busqueda.submit()
                
        except Exception as e:
            print(f"Error al buscar botón de búsqueda: {e}")
            # Fallback al método original
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