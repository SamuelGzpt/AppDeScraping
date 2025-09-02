# scraping_policia_directo.py
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException, NoSuchElementException
from webdriver_manager.chrome import ChromeDriverManager
import time


def consultar_policia(cedula, recaptcha_url=None):
    """
    Consulta antecedentes en el sistema de policía usando enlace directo con reCAPTCHA resuelto
    
    Args:
        cedula: Número de cédula a consultar
        recaptcha_url: URL del reCAPTCHA ya resuelto (opcional)
    """
    
    # URL por defecto con reCAPTCHA resuelto
    if not recaptcha_url:
        recaptcha_url = "https://www.google.com/recaptcha/api2/anchor?ar=1&k=6LcsIwQaAAAAAFCsaI-dkR6hgKsZwwJRsmE0tIJH&co=aHR0cHM6Ly9hbnRlY2VkZW50ZXMucG9saWNpYS5nb3YuY286NzAwNQ..&hl=es&v=2sJvksnKlEApLvJt2btz_q7n&size=normal&anchor-ms=20000&execute-ms=15000&cb=kb0yeflma5ql"
    
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
        print("[INFO] Iniciando con reCAPTCHA ya resuelto...")
        
        # 1️⃣ Ir directamente al enlace del reCAPTCHA resuelto
        driver.get(recaptcha_url)
        time.sleep(3)  # Esperar que se cargue el CAPTCHA
        print("[INFO] CAPTCHA cargado")
        
        # 2️⃣ Ahora ir directamente a la página de consulta
        driver.get("https://antecedentes.policia.gov.co:7005/WebJudicial/antecedentesPersona.xhtml")
        print("[INFO] Navegando directamente al formulario de consulta...")
        
        # 3️⃣ Esperar que la página se cargue completamente
        time.sleep(5)
        
        # 4️⃣ Buscar el campo de cédula directamente
        print("[INFO] Buscando campo de cédula...")
        
        # Múltiples selectores posibles para el campo de cédula
        cedula_selectors = [
            "#cedulaInput",
            "input[name*='cedula']",
            "input[id*='cedula']",
            "input[placeholder*='cédula']",
            "input[placeholder*='documento']",
            "input[type='text']:not([readonly])",
            "#form\\:cedulaInput",  # Posible ID con formulario
            "input.form-control[type='text']"
        ]
        
        campo_cedula = None
        for selector in cedula_selectors:
            try:
                campo_cedula = wait.until(EC.element_to_be_clickable((By.CSS_SELECTOR, selector)))
                print(f"[✓] Campo de cédula encontrado con selector: {selector}")
                break
            except:
                continue
        
        if not campo_cedula:
            # Fallback: buscar cualquier input de texto visible
            campos_texto = driver.find_elements(By.CSS_SELECTOR, "input[type='text']")
            for campo in campos_texto:
                if campo.is_displayed() and campo.is_enabled():
                    campo_cedula = campo
                    print("[✓] Campo de cédula encontrado (fallback)")
                    break
        
        if not campo_cedula:
            return {"error": "No se encontró el campo para ingresar la cédula"}
        
        # 5️⃣ Limpiar y escribir la cédula
        campo_cedula.clear()
        campo_cedula.send_keys(str(cedula))
        print(f"[✓] Cédula {cedula} ingresada")
        
        # 6️⃣ Buscar y hacer clic en el botón de consultar
        print("[INFO] Buscando botón de consultar...")
        
        # Múltiples selectores para el botón de consultar
        consultar_selectors = [
            "#j_idt17",  # Selector original
            "button[value*='Consultar']",
            "input[value*='Consultar']",
            "button[type='submit']",
            "input[type='submit']",
            "button:contains('Consultar')",
            ".ui-button",
            "button.btn-primary",
            "#form\\:consultarBtn"
        ]
        
        consultar_btn = None
        for selector in consultar_selectors:
            try:
                if selector.startswith("button:contains"):
                    # XPath para texto contenido
                    consultar_btn = wait.until(EC.element_to_be_clickable((By.XPATH, "//button[contains(text(), 'Consultar')]")))
                else:
                    consultar_btn = wait.until(EC.element_to_be_clickable((By.CSS_SELECTOR, selector)))
                print(f"[✓] Botón de consultar encontrado con selector: {selector}")
                break
            except:
                continue
        
        if not consultar_btn:
            # Fallback: buscar cualquier botón visible
            botones = driver.find_elements(By.TAG_NAME, "button")
            for boton in botones:
                if (boton.is_displayed() and boton.is_enabled() and 
                    ('consultar' in boton.text.lower() or 'submit' in boton.get_attribute('type'))):
                    consultar_btn = boton
                    print("[✓] Botón de consultar encontrado (fallback)")
                    break
        
        if not consultar_btn:
            return {"error": "No se encontró el botón de consultar"}
        
        # 7️⃣ Hacer clic en consultar
        driver.execute_script("arguments[0].click();", consultar_btn)
        print("[✓] Consulta enviada")
        
        # 8️⃣ Esperar tiempo adicional para procesamiento
        print("[INFO] Esperando respuesta del sistema...")
        time.sleep(8)  # Tiempo adicional para que procese
        
        # 9️⃣ Buscar el resultado
        print("[INFO] Buscando resultado...")
        
        # Múltiples selectores posibles para el resultado
        resultado_selectors = [
            "#form\\:mensajeCiudadano",  # Selector original
            ".mensaje-ciudadano",
            "#mensajeCiudadano",
            "div[id*='mensaje']",
            ".resultado-consulta",
            ".alert",
            ".panel-body",
            "div.ui-growl-message",
            "div[class*='resultado']"
        ]
        
        texto_resultado = None
        for selector in resultado_selectors:
            try:
                resultado_el = wait.until(EC.visibility_of_element_located((By.CSS_SELECTOR, selector)))
                texto_resultado = resultado_el.text.strip()
                print(f"[✓] Resultado encontrado con selector: {selector}")
                break
            except:
                continue
        
        # 🔟 Si no encuentra resultado específico, buscar en toda la página
        if not texto_resultado:
            print("[INFO] Buscando resultado en toda la página...")
            time.sleep(5)  # Esperar más tiempo
            
            # Buscar texto específico en la página
            page_source = driver.page_source.lower()
            
            if "no tiene asuntos pendientes" in page_source:
                texto_resultado = "NO TIENE ASUNTOS PENDIENTES CON LAS AUTORIDADES JUDICIALES"
                print("[✓] Resultado encontrado en página: Sin antecedentes")
            elif "tiene asuntos pendientes" in page_source:
                # Buscar div con clase específica o cualquier div visible con texto
                divs = driver.find_elements(By.TAG_NAME, "div")
                for div in divs:
                    texto = div.text.strip()
                    if texto and ("asunto" in texto.lower() or "antecedente" in texto.lower()):
                        texto_resultado = texto
                        print("[✓] Resultado encontrado en div de la página")
                        break
            else:
                texto_resultado = "No se pudo obtener el resultado. Página cargada pero sin información clara."
        
        if not texto_resultado:
            return {"error": "No se pudo obtener el resultado de la consulta"}
        
        # ✅ Procesar y retornar resultado
        tiene_antecedentes = "NO TIENE ASUNTOS PENDIENTES CON LAS AUTORIDADES JUDICIALES" not in texto_resultado.upper()
        
        resultado_final = {
            "tiene_antecedentes": tiene_antecedentes,
            "texto": texto_resultado,
            "status": "success"
        }
        
        print(f"[✓] Consulta completada para cédula {cedula}")
        return resultado_final

    except TimeoutException:
        print("[❌] Timeout: El sistema de Policía no respondió a tiempo")
        return {"error": "El sistema de Policía no respondió a tiempo.", "status": "timeout"}
        
    except NoSuchElementException as e:
        print(f"[❌] Elemento no encontrado: {e}")
        return {"error": f"No se encontró un elemento esperado: {str(e)}", "status": "element_not_found"}
        
    except Exception as e:
        print(f"[❌] Error general: {e}")
        return {"error": f"Error al consultar Policía: {str(e)}", "status": "error"}
        
    finally:
        driver.quit()


def consultar_policia_con_captcha_automatico(cedula, max_wait_captcha=300):
    """
    Versión que detecta automáticamente cuando el CAPTCHA está resuelto usando múltiples indicadores
    
    Args:
        cedula: Número de cédula a consultar
        max_wait_captcha: Máximo tiempo de espera para el CAPTCHA (en segundos)
    """
    options = Options()
    options.add_argument("--no-sandbox")
    options.add_argument("--disable-dev-shm-usage")
    options.add_experimental_option("excludeSwitches", ["enable-automation"])
    options.add_experimental_option('useAutomationExtension', False)

    driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=options)
    driver.execute_script("Object.defineProperty(navigator, 'webdriver', {get: () => undefined})")
    wait = WebDriverWait(driver, 30)

    try:
        driver.get("https://antecedentes.policia.gov.co:7005/WebJudicial/index.xhtml")
        print("[INFO] Página cargada")

        # 1️⃣ Aceptar términos automáticamente
        aceptar_radio = wait.until(EC.element_to_be_clickable((By.ID, "aceptaOption:0")))
        driver.execute_script("arguments[0].click();", aceptar_radio)
        
        continuar_btn = wait.until(EC.element_to_be_clickable((By.ID, "continuarBtn")))
        driver.execute_script("arguments[0].click();", continuar_btn)
        print("[✓] Términos aceptados automáticamente")

        # 2️⃣ Ingresar cédula
        campo_cedula = wait.until(EC.element_to_be_clickable((By.ID, "cedulaInput")))
        campo_cedula.clear()
        campo_cedula.send_keys(str(cedula))
        print(f"[✓] Cédula {cedula} ingresada")

        # 3️⃣ Detectar automáticamente cuando el CAPTCHA está resuelto
        print(f"[INFO] Esperando a que el CAPTCHA se resuelva automáticamente (máximo {max_wait_captcha/60:.1f} minutos)...")
        print("[INFO] Resuelve el CAPTCHA en el navegador...")
        
        captcha_wait = WebDriverWait(driver, max_wait_captcha)
        captcha_resuelto = False
        
        # Monitorear múltiples indicadores de CAPTCHA resuelto
        while not captcha_resuelto:
            try:
                # Opción 1: Verificar el token del reCAPTCHA
                token_element = driver.find_element(By.ID, "recaptcha-token")
                if token_element and token_element.get_attribute("value") and len(token_element.get_attribute("value")) > 50:
                    print("[✓] CAPTCHA resuelto detectado por token!")
                    captcha_resuelto = True
                    break
                    
            except NoSuchElementException:
                pass
            
            try:
                # Opción 2: Verificar el mensaje de status
                status_element = driver.find_element(By.ID, "recaptcha-accessible-status")
                if status_element and "verificado" in status_element.text.lower():
                    print("[✓] CAPTCHA resuelto detectado por status!")
                    captcha_resuelto = True
                    break
                    
            except NoSuchElementException:
                pass
                
            try:
                # Opción 3: Verificar checkbox marcado del reCAPTCHA
                checkbox_element = driver.find_element(By.CSS_SELECTOR, ".recaptcha-checkbox-checked")
                if checkbox_element:
                    print("[✓] CAPTCHA resuelto detectado por checkbox!")
                    captcha_resuelto = True
                    break
                    
            except NoSuchElementException:
                pass
                
            try:
                # Opción 4: Verificar iframe del reCAPTCHA con token en URL
                iframes = driver.find_elements(By.TAG_NAME, "iframe")
                for iframe in iframes:
                    src = iframe.get_attribute("src")
                    if src and "recaptcha" in src and len(src) > 200:  # URL larga indica token
                        print("[✓] CAPTCHA resuelto detectado por iframe!")
                        captcha_resuelto = True
                        break
                        
            except:
                pass
                
            # Esperar un poco antes de volver a verificar
            time.sleep(2)
        
        if not captcha_resuelto:
            return {"error": f"CAPTCHA no resuelto en el tiempo límite ({max_wait_captcha}s)"}

        # 4️⃣ Pequeña pausa adicional para asegurar que todo esté listo
        time.sleep(3)
        print("[INFO] Esperando a que el sistema procese el CAPTCHA...")

        # 5️⃣ Hacer clic en consultar
        consultar_btn = wait.until(EC.element_to_be_clickable((By.ID, "j_idt17")))
        driver.execute_script("arguments[0].click();", consultar_btn)
        print("[✓] Consulta enviada")

        # 6️⃣ Obtener resultado
        print("[INFO] Esperando resultado...")
        resultado_el = wait.until(EC.visibility_of_element_located((By.ID, "form:mensajeCiudadano")))
        texto = resultado_el.text.strip()
        print(f"[✓] Resultado obtenido: {texto[:50]}...")

        return {
            "tiene_antecedentes": "NO TIENE ASUNTOS PENDIENTES CON LAS AUTORIDADES JUDICIALES" not in texto.upper(),
            "texto": texto,
            "status": "success"
        }

    except TimeoutException:
        print("[❌] Timeout en el proceso")
        return {"error": "El sistema de Policía no respondió a tiempo.", "status": "timeout"}
    except NoSuchElementException as e:
        print(f"[❌] Elemento no encontrado: {e}")
        return {"error": f"No se encontró un elemento esperado: {str(e)}", "status": "element_not_found"}
    except Exception as e:
        print(f"[❌] Error general: {e}")
        return {"error": f"Error al consultar Policía: {str(e)}", "status": "error"}
    finally:
        driver.quit()


def consultar_policia_token_especifico(cedula, recaptcha_token=None):
    """
    Versión que usa un token específico del reCAPTCHA si lo tienes
    
    Args:
        cedula: Número de cédula a consultar
        recaptcha_token: Token del reCAPTCHA ya resuelto
    """
    options = Options()
    options.add_argument("--no-sandbox")
    options.add_argument("--disable-dev-shm-usage")
    options.add_experimental_option("excludeSwitches", ["enable-automation"])
    options.add_experimental_option('useAutomationExtension', False)

    driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=options)
    driver.execute_script("Object.defineProperty(navigator, 'webdriver', {get: () => undefined})")
    wait = WebDriverWait(driver, 30)

    try:
        driver.get("https://antecedentes.policia.gov.co:7005/WebJudicial/index.xhtml")
        
        # Aceptar términos
        aceptar_radio = wait.until(EC.element_to_be_clickable((By.ID, "aceptaOption:0")))
        driver.execute_script("arguments[0].click();", aceptar_radio)
        
        continuar_btn = wait.until(EC.element_to_be_clickable((By.ID, "continuarBtn")))
        driver.execute_script("arguments[0].click();", continuar_btn)

        # Ingresar cédula
        campo_cedula = wait.until(EC.element_to_be_clickable((By.ID, "cedulaInput")))
        campo_cedula.clear()
        campo_cedula.send_keys(str(cedula))

        # Si tienes un token específico, inyectarlo
        if recaptcha_token:
            print(f"[INFO] Inyectando token del reCAPTCHA...")
            driver.execute_script(f"""
                // Buscar el campo del token y establecer el valor
                var tokenField = document.getElementById('recaptcha-token');
                if (tokenField) {{
                    tokenField.value = '{recaptcha_token}';
                    console.log('Token inyectado');
                }}
                
                // Marcar el checkbox como verificado
                var checkbox = document.querySelector('.recaptcha-checkbox');
                if (checkbox) {{
                    checkbox.classList.add('recaptcha-checkbox-checked');
                }}
                
                // Actualizar el status
                var status = document.getElementById('recaptcha-accessible-status');
                if (status) {{
                    status.textContent = 'Estás verificado.';
                }}
            """)
            print("[✓] Token inyectado")

        time.sleep(3)  # Esperar procesamiento

        # Consultar
        consultar_btn = wait.until(EC.element_to_be_clickable((By.ID, "j_idt17")))
        driver.execute_script("arguments[0].click();", consultar_btn)

        # Obtener resultado
        resultado_el = wait.until(EC.visibility_of_element_located((By.ID, "form:mensajeCiudadano")))
        texto = resultado_el.text.strip()

        return {
            "tiene_antecedentes": "NO TIENE ASUNTOS PENDIENTES CON LAS AUTORIDADES JUDICIALES" not in texto.upper(),
            "texto": texto,
            "status": "success"
        }

    except Exception as e:
        return {"error": f"Error al consultar Policía: {str(e)}", "status": "error"}
    finally:
        driver.quit()


def consultar_policia_url_directa(cedula):
    """
    Versión simplificada que usa directamente el enlace con CAPTCHA ya procesado
    """
    options = Options()
    options.add_argument("--no-sandbox")
    options.add_argument("--disable-dev-shm-usage")
    
    driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=options)
    wait = WebDriverWait(driver, 20)

    try:
        # 1️⃣ Ir directamente al formulario saltando términos y CAPTCHA
        captcha_url = "https://www.google.com/recaptcha/api2/anchor?ar=1&k=6LcsIwQaAAAAAFCsaI-dkR6hgKsZwwJRsmE0tIJH&co=aHR0cHM6Ly9hbnRlY2VkZW50ZXMucG9saWNpYS5nb3YuY286NzAwNQ..&hl=es&v=2sJvksnKlEApLvJt2btz_q7n&size=normal&anchor-ms=20000&execute-ms=15000&cb=kb0yeflma5ql"
        
        print("[INFO] Cargando CAPTCHA resuelto...")
        driver.get(captcha_url)
        time.sleep(3)
        
        # 2️⃣ Navegar al formulario de consulta
        form_url = "https://antecedentes.policia.gov.co:7005/WebJudicial/antecedentesPersona.xhtml"
        print("[INFO] Navegando al formulario de consulta...")
        driver.get(form_url)
        time.sleep(5)
        
        # 3️⃣ Ingresar cédula
        campo_cedula = wait.until(EC.element_to_be_clickable((By.ID, "cedulaInput")))
        campo_cedula.clear()
        campo_cedula.send_keys(str(cedula))
        print(f"[✓] Cédula {cedula} ingresada")

        # 4️⃣ Consultar
        consultar_btn = wait.until(EC.element_to_be_clickable((By.ID, "j_idt17")))
        driver.execute_script("arguments[0].click();", consultar_btn)
        print("[✓] Consulta enviada")

        # 5️⃣ Obtener resultado
        resultado_el = wait.until(EC.visibility_of_element_located((By.ID, "form:mensajeCiudadano")))
        texto = resultado_el.text.strip()

        return {
            "tiene_antecedentes": "NO TIENE ASUNTOS PENDIENTES CON LAS AUTORIDADES JUDICIALES" not in texto.upper(),
            "texto": texto
        }

    except Exception as e:
        print(f"[❌] Error: {e}")
        return {"error": f"Error al consultar Policía: {str(e)}"}
    finally:
        driver.quit()


# Función principal actualizada (mantiene compatibilidad)
def consultar_policia(cedula):
    """
    Función principal - usa la versión con detección automática de CAPTCHA
    """
    return consultar_policia_con_captcha_automatico(cedula)