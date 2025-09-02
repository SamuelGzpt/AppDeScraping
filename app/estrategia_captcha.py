# estrategias_captcha_policia.py
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException, NoSuchElementException
from webdriver_manager.chrome import ChromeDriverManager
import time
import random


def setup_human_like_browser():
    """Configurar navegador para parecer más humano y evitar CAPTCHA complejo"""
    options = Options()
    
    # Configuraciones para parecer más humano
    options.add_argument("--disable-blink-features=AutomationControlled")
    options.add_experimental_option("excludeSwitches", ["enable-automation"])
    options.add_experimental_option('useAutomationExtension', False)
    
    # Headers más realistas
    options.add_argument("--user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36")
    
    # Configuraciones adicionales
    options.add_argument("--disable-dev-shm-usage")
    options.add_argument("--no-sandbox")
    options.add_argument("--disable-gpu")
    options.add_argument("--disable-extensions")
    
    # Simular comportamiento humano
    options.add_argument("--disable-automation")
    options.add_argument("--disable-infobars")
    
    driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=options)
    
    # Scripts para ocultar automatización
    driver.execute_script("Object.defineProperty(navigator, 'webdriver', {get: () => undefined})")
    driver.execute_script("delete navigator.__proto__.webdriver")
    
    return driver


def consultar_policia_estrategia_humana(cedula, max_intentos=3):
    """
    Estrategia 1: Comportamiento más humano para evitar CAPTCHA complejo
    """
    
    for intento in range(max_intentos):
        print(f"[INFO] Intento {intento + 1} de {max_intentos}")
        
        driver = setup_human_like_browser()
        wait = WebDriverWait(driver, 30)
        
        try:
            # Navegar con pausa humana
            driver.get("https://antecedentes.policia.gov.co:7005/WebJudicial/index.xhtml")
            time.sleep(random.uniform(2, 4))  # Pausa aleatoria humana
            
            # Aceptar términos con movimiento de mouse simulado
            aceptar_radio = wait.until(EC.element_to_be_clickable((By.ID, "aceptaOption:0")))
            driver.execute_script("arguments[0].scrollIntoView(true);", aceptar_radio)
            time.sleep(random.uniform(1, 2))
            driver.execute_script("arguments[0].click();", aceptar_radio)
            
            # Continuar con pausa
            time.sleep(random.uniform(1, 2))
            continuar_btn = wait.until(EC.element_to_be_clickable((By.ID, "continuarBtn")))
            driver.execute_script("arguments[0].click();", continuar_btn)
            
            print("[✓] Términos aceptados con comportamiento humano")
            
            # Ingresar cédula de forma humana
            campo_cedula = wait.until(EC.element_to_be_clickable((By.ID, "cedulaInput")))
            campo_cedula.click()  # Click normal primero
            time.sleep(0.5)
            campo_cedula.clear()
            
            # Escribir la cédula caracter por caracter (más humano)
            for char in str(cedula):
                campo_cedula.send_keys(char)
                time.sleep(random.uniform(0.1, 0.3))
            
            print(f"[✓] Cédula ingresada de forma humana")
            
            # Esperar a que aparezca el CAPTCHA y verificar tipo
            time.sleep(3)
            
            # Detectar tipo de CAPTCHA
            captcha_simple = False
            try:
                # Buscar el checkbox simple
                checkbox_frame = driver.find_element(By.CSS_SELECTOR, "iframe[title='reCAPTCHA']")
                driver.switch_to.frame(checkbox_frame)
                
                checkbox = driver.find_element(By.ID, "recaptcha-anchor")
                if checkbox.is_displayed():
                    print("[✓] CAPTCHA simple detectado (solo checkbox)")
                    captcha_simple = True
                    
                    # Hacer click en el checkbox
                    driver.execute_script("arguments[0].click();", checkbox)
                    time.sleep(2)
                    
                driver.switch_to.default_content()
                
            except:
                driver.switch_to.default_content()
                print("[⚠] No se pudo detectar CAPTCHA simple")
            
            if captcha_simple:
                # Continuar con la consulta
                print("[INFO] Procediendo con consulta...")
                time.sleep(3)
                
                consultar_btn = wait.until(EC.element_to_be_clickable((By.ID, "j_idt17")))
                driver.execute_script("arguments[0].click();", consultar_btn)
                
                resultado_el = wait.until(EC.visibility_of_element_located((By.ID, "form:mensajeCiudadano")))
                texto = resultado_el.text.strip()
                
                driver.quit()
                return {
                    "tiene_antecedentes": "NO TIENE ASUNTOS PENDIENTES CON LAS AUTORIDADES JUDICIALES" not in texto.upper(),
                    "texto": texto,
                    "captcha_type": "simple"
                }
            else:
                print("[⚠] CAPTCHA complejo detectado, reintentando...")
                driver.quit()
                time.sleep(random.uniform(5, 10))  # Esperar antes del siguiente intento
                continue
                
        except Exception as e:
            print(f"[❌] Error en intento {intento + 1}: {e}")
            driver.quit()
            if intento < max_intentos - 1:
                time.sleep(random.uniform(5, 10))
                continue
            else:
                return {"error": f"Error después de {max_intentos} intentos: {str(e)}"}
    
    return {"error": "No se pudo evitar el CAPTCHA complejo después de varios intentos"}


def consultar_policia_con_proxy_rotacion(cedula):
    """
    Estrategia 2: Cambiar IP/User-Agent para conseguir CAPTCHA simple
    """
    user_agents = [
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
        "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
        "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:109.0) Gecko/20100101 Firefox/121.0",
        "Mozilla/5.0 (Macintosh; Intel Mac OS X 10.15; rv:109.0) Gecko/20100101 Firefox/121.0"
    ]
    
    for ua in user_agents:
        print(f"[INFO] Intentando con User-Agent: {ua[:50]}...")
        
        options = Options()
        options.add_argument(f"--user-agent={ua}")
        options.add_argument("--disable-blink-features=AutomationControlled")
        options.add_experimental_option("excludeSwitches", ["enable-automation"])
        options.add_experimental_option('useAutomationExtension', False)
        options.add_argument("--no-sandbox")
        options.add_argument("--disable-dev-shm-usage")
        
        driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=options)
        driver.execute_script("Object.defineProperty(navigator, 'webdriver', {get: () => undefined})")
        
        try:
            resultado = intentar_consulta_simple(driver, cedula)
            if resultado and "error" not in resultado:
                return resultado
            else:
                driver.quit()
                continue
                
        except Exception as e:
            print(f"[❌] Error con este User-Agent: {e}")
            driver.quit()
            continue
    
    return {"error": "No se pudo conseguir CAPTCHA simple con diferentes User-Agents"}


def intentar_consulta_simple(driver, cedula):
    """Función helper para intentar consulta con CAPTCHA simple"""
    wait = WebDriverWait(driver, 20)
    
    try:
        driver.get("https://antecedentes.policia.gov.co:7005/WebJudicial/index.xhtml")
        time.sleep(random.uniform(3, 5))
        
        # Aceptar términos
        aceptar_radio = wait.until(EC.element_to_be_clickable((By.ID, "aceptaOption:0")))
        driver.execute_script("arguments[0].click();", aceptar_radio)
        
        time.sleep(random.uniform(1, 3))
        continuar_btn = wait.until(EC.element_to_be_clickable((By.ID, "continuarBtn")))
        driver.execute_script("arguments[0].click();", continuar_btn)

        # Ingresar cédula
        campo_cedula = wait.until(EC.element_to_be_clickable((By.ID, "cedulaInput")))
        campo_cedula.clear()
        campo_cedula.send_keys(str(cedula))

        # Verificar tipo de CAPTCHA antes de proceder
        time.sleep(3)
        
        # Buscar iframe del CAPTCHA
        captcha_frames = driver.find_elements(By.CSS_SELECTOR, "iframe[src*='recaptcha']")
        
        if len(captcha_frames) > 1:
            print("[⚠] Múltiples iframes detectados - posible CAPTCHA complejo")
            return {"error": "CAPTCHA complejo detectado"}
        elif len(captcha_frames) == 1:
            print("[✓] CAPTCHA simple detectado")
            
            # Intentar resolver CAPTCHA simple
            frame = captcha_frames[0]
            driver.switch_to.frame(frame)
            
            try:
                checkbox = wait.until(EC.element_to_be_clickable((By.ID, "recaptcha-anchor")))
                driver.execute_script("arguments[0].click();", checkbox)
                time.sleep(2)
                driver.switch_to.default_content()
                
                # Esperar verificación
                time.sleep(5)
                
                # Proceder con consulta
                consultar_btn = wait.until(EC.element_to_be_clickable((By.ID, "j_idt17")))
                driver.execute_script("arguments[0].click();", consultar_btn)
                
                resultado_el = wait.until(EC.visibility_of_element_located((By.ID, "form:mensajeCiudadano")))
                texto = resultado_el.text.strip()
                
                return {
                    "tiene_antecedentes": "NO TIENE ASUNTOS PENDIENTES CON LAS AUTORIDADES JUDICIALES" not in texto.upper(),
                    "texto": texto,
                    "captcha_type": "simple_auto"
                }
                
            except Exception as e:
                driver.switch_to.default_content()
                print(f"[❌] Error al resolver CAPTCHA: {e}")
                return {"error": "Error al resolver CAPTCHA automáticamente"}
        else:
            print("[❌] No se detectó CAPTCHA")
            return {"error": "No se detectó CAPTCHA en la página"}

    except Exception as e:
        return {"error": f"Error en consulta simple: {str(e)}"}


def consultar_policia_con_cache_session(cedula):
    """
    Estrategia 3: Usar cookies/session de navegador real para evitar CAPTCHA
    """
    options = Options()
    
    # Usar perfil de usuario existente (si tienes Chrome instalado)
    # options.add_argument(r"--user-data-dir=C:\Users\TU_USUARIO\AppData\Local\Google\Chrome\User Data")
    # options.add_argument("--profile-directory=Default")
    
    # O usar directorio temporal para mantener cookies
    options.add_argument("--user-data-dir=/tmp/chrome_profile_captcha")
    
    options.add_argument("--disable-blink-features=AutomationControlled")
    options.add_experimental_option("excludeSwitches", ["enable-automation"])
    options.add_experimental_option('useAutomationExtension', False)
    options.add_argument("--no-sandbox")
    options.add_argument("--disable-dev-shm-usage")
    
    driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=options)
    driver.execute_script("Object.defineProperty(navigator, 'webdriver', {get: () => undefined})")
    wait = WebDriverWait(driver, 30)

    try:
        # Primera visita para establecer cookies
        print("[INFO] Estableciendo sesión...")
        driver.get("https://www.google.com/")
        time.sleep(2)
        
        # Ahora ir al sitio de policía
        driver.get("https://antecedentes.policia.gov.co:7005/WebJudicial/index.xhtml")
        time.sleep(random.uniform(3, 5))

        # Proceso normal
        aceptar_radio = wait.until(EC.element_to_be_clickable((By.ID, "aceptaOption:0")))
        driver.execute_script("arguments[0].click();", aceptar_radio)
        
        continuar_btn = wait.until(EC.element_to_be_clickable((By.ID, "continuarBtn")))
        driver.execute_script("arguments[0].click();", continuar_btn)

        campo_cedula = wait.until(EC.element_to_be_clickable((By.ID, "cedulaInput")))
        campo_cedula.clear()
        campo_cedula.send_keys(str(cedula))

        print("[INFO] Resuelve el CAPTCHA (debería ser más simple con cookies)...")
        input("Presiona ENTER cuando hayas resuelto el CAPTCHA...")

        consultar_btn = wait.until(EC.element_to_be_clickable((By.ID, "j_idt17")))
        driver.execute_script("arguments[0].click();", consultar_btn)

        resultado_el = wait.until(EC.visibility_of_element_located((By.ID, "form:mensajeCiudadano")))
        texto = resultado_el.text.strip()

        return {
            "tiene_antecedentes": "NO TIENE ASUNTOS PENDIENTES CON LAS AUTORIDADES JUDICIALES" not in texto.upper(),
            "texto": texto
        }

    except Exception as e:
        return {"error": f"Error con estrategia de cookies: {str(e)}"}
    finally:
        driver.quit()


def consultar_policia_bypass_captcha(cedula):
    """
    Estrategia 4: Intentar bypass del CAPTCHA usando el token que obtuviste
    """
    options = Options()
    options.add_argument("--disable-blink-features=AutomationControlled")
    options.add_experimental_option("excludeSwitches", ["enable-automation"])
    options.add_experimental_option('useAutomationExtension', False)
    options.add_argument("--no-sandbox")
    options.add_argument("--disable-dev-shm-usage")

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

        # Esperar a que aparezca el CAPTCHA
        time.sleep(5)
        
        # Inyectar el token que obtuviste manualmente
        token_largo = "03AFcWeA7hXyfxnY5zH4yRJx99d9dVdEewYpgxc6j3s8JxDXSOH32fGJDQ9fD8v-V_0Qn7tkyEJPHARB55JjC9Pvnh3gfj3K7B6pBe2yFWrCNlcv1PoBfzelAY1sYPFGxrXi3c2UKRLI7zVL5idOjHvJPrP-oLKw1LplqtCs7rLRYHaHg-9gJ8VB-lNPlhyoQPHiQgZCZoqSKSKC6CbpA4vIHBo-RHWR91PQZMfkw33saXmGUR5V5yFVWSNMXWYweAZ6VbizwusEPoDaxTF9v7BOc8F2kCowC-yqgxCOUX2c2ThZ-KRp2G8kL6Lm8iSfaMIQRgC4PLCa6t_gBA2ECMG6ww2Q7Y_BIkhTyRqf8F4-2YG1ld4LhlXK04Tb4EodTh7JSjc2-TnIaO7jftTcZmBOBeWeynnFNc3l0NHSyS2KnNvZScxClyTErfM_XEc6RkW3tWfzm4uLDoT16sdWVphfIeLidBZM9UYreTx_mTG600I-PCIO-EmKpNDifzNPb5UhIeUO9QhoREbiLLGKOwb_5zuZtxfIEqAHCEFhvbaEz_ecu_9Nu8h-o3FkuLN7FRnuWf_DgG82F5cvvpX_2vi-T5S2_cSseANeIx0SB0yg9Vham7LtUYq7J8V9sv7LtAEI_AhCg4Mpmqicyj3PsFeSKBZmequ83fCfLE6BVOn3AymLFAud9HrAXtxl6Uv4c1g2E6F8LIdOy4uQU7Khno0VgzP1vqUvmndZdg27-FXtNCBRuDwqaeHGGs-ygJBvl6j0xVp-u5Z_VZK7SoOtrr-lX3mhA-fg7ht23WAxGpnol_ZImQjHKxrbCQh5az_U47jCgrPVW8sedS4k8UTuzG69GsP_NFy327o5w-FPW8_x57VRFpxUlawVggwDXCSXRl48DeG9mb6Np_0JI46jczP6DQVdEjM2GEJr33JvbzxOukXPJ22odN92JHO2TyukQE5mmJYdVUqXQWZF0A4mv22UXV_xOjOJsGiolnssBNXyFAmzAeMKU9PPnSybFS0Ziq_egvP7Zt7gR3X2o_kgXc4SFHcEsQawmKOmRWl8NJoFHUo65msEP-RMaj0cuQJUF9_oZwPWXvhsQa5GzdMtNhrXjLGmkiMR_VzpoNZ_SZDDmho5dQaCEYeMCiaHRX5WWaUCtBTgAEtbBsnTehWobnMxjpDPB21vyAzdqJR_Q1PLIv00rqGqovV_eZNezjsIlAZkODQ75SEKSXWMfbl2QqQfvtHoup_DxalKFzGJRq0oAgBJuJFd1eZoq1bNERzJ9X65jTZCu6erB_ZN2aMG_eVdU_bntenlpDoZJDrHg1VLZOwC_0-aLxm1iqZIi9cASGfxAcsQzUBbM4N9T4MQA3Kz_qtJz57-O1ZeW5FwWty5inPqaFYMrbAM6_8lLRlPrQZuhvtbdEwNNDPsd2itt_dtc7KpDmyqFiqju8GPxOvlKLsGruIfESbSEXNR5Mxz56jv0tozByLAQw6NMAYKOrzSUNGH3DjU5CjD6hjMf_uLNoCZr7-rmYJ5jMXQ7yl3a1lI1CRBh2Ax6BxlEXboGJj7_JuOmhSqf-Dg"
        
        print("[INFO] Intentando inyectar token válido...")
        
        # Inyectar el token y marcar como verificado
        driver.execute_script(f"""
            // Crear o actualizar el campo del token
            var tokenField = document.getElementById('recaptcha-token') || document.createElement('input');
            tokenField.type = 'hidden';
            tokenField.id = 'recaptcha-token';
            tokenField.name = 'g-recaptcha-response';
            tokenField.value = '{token_largo}';
            
            if (!document.getElementById('recaptcha-token')) {{
                document.body.appendChild(tokenField);
            }}
            
            // Crear el div de status si no existe
            var statusDiv = document.getElementById('recaptcha-accessible-status') || document.createElement('div');
            statusDiv.id = 'recaptcha-accessible-status';
            statusDiv.className = 'rc-anchor-aria-status';
            statusDiv.setAttribute('aria-hidden', 'true');
            statusDiv.textContent = 'Estás verificado.';
            
            if (!document.getElementById('recaptcha-accessible-status')) {{
                document.body.appendChild(statusDiv);
            }}
            
            // Simular evento de CAPTCHA resuelto
            window.grecaptcha = {{
                getResponse: function() {{ return '{token_largo}'; }}
            }};
            
            console.log('Token y verificación inyectados');
        """)
        
        time.sleep(3)
        
        # Intentar consultar
        try:
            consultar_btn = wait.until(EC.element_to_be_clickable((By.ID, "j_idt17")))
            driver.execute_script("arguments[0].click();", consultar_btn)
            
            resultado_el = wait.until(EC.visibility_of_element_located((By.ID, "form:mensajeCiudadano")))
            texto = resultado_el.text.strip()
            
            return {
                "tiene_antecedentes": "NO TIENE ASUNTOS PENDIENTES CON LAS AUTORIDADES JUDICIALES" not in texto.upper(),
                "texto": texto,
                "method": "token_injection"
            }
            
        except:
            return {"error": "El token inyectado no fue aceptado por el servidor"}

    except Exception as e:
        return {"error": f"Error en bypass: {str(e)}"}


def consultar_policia_manual_optimizado(cedula):
    """
    Estrategia 5: Manual pero optimizada para detectar cuando está listo
    """
    driver = setup_human_like_browser()
    wait = WebDriverWait(driver, 30)

    try:
        driver.get("https://antecedentes.policia.gov.co:7005/WebJudicial/index.xhtml")
        
        # Términos automáticos
        aceptar_radio = wait.until(EC.element_to_be_clickable((By.ID, "aceptaOption:0")))
        driver.execute_script("arguments[0].click();", aceptar_radio)
        
        continuar_btn = wait.until(EC.element_to_be_clickable((By.ID, "continuarBtn")))
        driver.execute_script("arguments[0].click();", continuar_btn)

        # Cédula
        campo_cedula = wait.until(EC.element_to_be_clickable((By.ID, "cedulaInput")))
        campo_cedula.clear()
        campo_cedula.send_keys(str(cedula))

        print("\n" + "="*50)
        print("🤖 CAPTCHA LISTO - Resuelve en el navegador")
        print("="*50)
        print("✅ Cuando veas SOLO el checkbox ✓ (sin imágenes)")
        print("✅ Márcalo y presiona ENTER aquí")
        print("❌ Si ves imágenes, cierra y reintenta")
        print("="*50)
        
        # Esperar confirmación manual
        input("Presiona ENTER cuando el CAPTCHA esté ✅ resuelto (solo checkbox)...")

        # Monitorear que realmente esté resuelto
        print("[INFO] Verificando que el CAPTCHA esté resuelto...")
        
        captcha_ok = False
        for _ in range(10):  # 10 intentos de verificación
            try:
                # Verificar token
                token_field = driver.find_element(By.ID, "recaptcha-token")
                if token_field.get_attribute("value"):
                    print("[✓] Token detectado")
                    captcha_ok = True
                    break
            except:
                pass
                
            try:
                # Verificar status
                status = driver.find_element(By.ID, "recaptcha-accessible-status")
                if "verificado" in status.text.lower():
                    print("[✓] Status verificado")
                    captcha_ok = True
                    break
            except:
                pass
                
            time.sleep(1)
        
        if not captcha_ok:
            return {"error": "CAPTCHA no parece estar resuelto correctamente"}

        # Proceder con consulta
        time.sleep(2)
        consultar_btn = wait.until(EC.element_to_be_clickable((By.ID, "j_idt17")))
        driver.execute_script("arguments[0].click();", consultar_btn)

        resultado_el = wait.until(EC.visibility_of_element_located((By.ID, "form:mensajeCiudadano")))
        texto = resultado_el.text.strip()

        return {
            "tiene_antecedentes": "NO TIENE ASUNTOS PENDIENTES CON LAS AUTORIDADES JUDICIALES" not in texto.upper(),
            "texto": texto
        }

    except Exception as e:
        return {"error": f"Error en consulta manual optimizada: {str(e)}"}
    finally:
        driver.quit()


# Función principal con múltiples estrategias
def consultar_policia(cedula):
    """
    Función principal que intenta múltiples estrategias para evitar CAPTCHA complejo
    """
    print(f"[INFO] Iniciando consulta para cédula {cedula}")
    
    # Estrategia 1: Comportamiento humano
    print("\n[INFO] Estrategia 1: Comportamiento humano...")
    resultado = consultar_policia_estrategia_humana(cedula, max_intentos=2)
    
    if resultado and "error" not in resultado:
        print("[✓] ¡Éxito con estrategia humana!")
        return resultado
    
    # Estrategia 2: Diferentes User-Agents
    print("\n[INFO] Estrategia 2: Rotación de User-Agents...")
    resultado = consultar_policia_con_proxy_rotacion(cedula)
    
    if resultado and "error" not in resultado:
        print("[✓] ¡Éxito con rotación de User-Agents!")
        return resultado
    
    # Estrategia 3: Bypass con token
    print("\n[INFO] Estrategia 3: Bypass con token...")
    resultado = consultar_policia_bypass_captcha(cedula)
    
    if resultado and "error" not in resultado:
        print("[✓] ¡Éxito con bypass de token!")
        return resultado
    
    # Estrategia 4: Manual optimizada (último recurso)
    print("\n[INFO] Estrategia 4: Manual optimizada (último recurso)...")
    resultado = consultar_policia_manual_optimizado(cedula)
    
    if resultado and "error" not in resultado:
        print("[✓] ¡Éxito con método manual optimizado!")
        return resultado
    
    # Si todas fallan
    print("[❌] Todas las estrategias fallaron")
    return {"error": "No se pudo completar la consulta con ninguna estrategia"}


def force_simple_captcha_tricks(driver):
    """
    Trucos adicionales para forzar CAPTCHA simple
    """
    try:
        # Truco 1: Simular historial de navegación confiable
        driver.execute_script("""
            // Simular historial de navegación
            window.history.pushState({}, '', window.location.href);
            
            // Simular tiempo en la página
            window.startTime = Date.now() - (Math.random() * 30000 + 10000);
            
            // Agregar eventos de mouse simulados
            document.addEventListener('mousemove', function(e) {
                window.lastMouseMove = Date.now();
            });
            
            // Simular scroll
            window.scrollTo(0, Math.random() * 100);
        """)
        
        # Truco 2: Configurar cookies que sugieren comportamiento humano
        driver.add_cookie({
            'name': '_human_behavior',
            'value': 'true',
            'domain': '.policia.gov.co'
        })
        
        # Truco 3: Simular tiempo de lectura
        time.sleep(random.uniform(3, 8))
        
        print("[✓] Trucos aplicados para CAPTCHA simple")
        
    except Exception as e:
        print(f"[⚠] Error aplicando trucos: {e}")


def consultar_policia_session_previa(cedula):
    """
    Estrategia 6: Usar sesión previa donde ya resolviste CAPTCHA
    """
    options = Options()
    
    # Usar directorio de datos persistente
    options.add_argument("--user-data-dir=./chrome_data_captcha")
    options.add_argument("--disable-blink-features=AutomationControlled")
    options.add_experimental_option("excludeSwitches", ["enable-automation"])
    options.add_experimental_option('useAutomationExtension', False)
    
    driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=options)
    driver.execute_script("Object.defineProperty(navigator, 'webdriver', {get: () => undefined})")
    wait = WebDriverWait(driver, 30)

    try:
        print("[INFO] Usando sesión con historial previo...")
        
        # Ir directamente al formulario (saltando términos si ya fueron aceptados)
        driver.get("https://antecedentes.policia.gov.co:7005/WebJudicial/antecedentesPersona.xhtml")
        time.sleep(5)
        
        # Verificar si ya estamos en el formulario
        try:
            campo_cedula = driver.find_element(By.ID, "cedulaInput")
            print("[✓] Ya estamos en el formulario, saltando términos")
        except:
            # Si no, hacer proceso normal
            print("[INFO] Aceptando términos...")
            driver.get("https://antecedentes.policia.gov.co:7005/WebJudicial/index.xhtml")
            
            aceptar_radio = wait.until(EC.element_to_be_clickable((By.ID, "aceptaOption:0")))
            driver.execute_script("arguments[0].click();", aceptar_radio)
            
            continuar_btn = wait.until(EC.element_to_be_clickable((By.ID, "continuarBtn")))
            driver.execute_script("arguments[0].click();", continuar_btn)

        # Ingresar cédula
        campo_cedula = wait.until(EC.element_to_be_clickable((By.ID, "cedulaInput")))
        campo_cedula.clear()
        campo_cedula.send_keys(str(cedula))

        # Aplicar trucos para CAPTCHA simple
        force_simple_captcha_tricks(driver)

        print("\n" + "🎯 CAPTCHA SIMPLIFICADO" + "="*30)
        print("✅ Resuelve el CAPTCHA (debería ser solo checkbox)")
        print("✅ Esta sesión tiene historial, más probabilidad de ser simple")
        print("="*50)
        
        input("Presiona ENTER cuando el CAPTCHA esté resuelto...")

        # Verificar resolución
        captcha_resuelto = False
        for _ in range(5):
            try:
                token_field = driver.find_element(By.ID, "recaptcha-token")
                if token_field.get_attribute("value"):
                    captcha_resuelto = True
                    break
            except:
                pass
            time.sleep(1)

        if not captcha_resuelto:
            print("[⚠] Advertencia: No se detectó token de CAPTCHA, pero continuando...")

        # Consultar
        consultar_btn = wait.until(EC.element_to_be_clickable((By.ID, "j_idt17")))
        driver.execute_script("arguments[0].click();", consultar_btn)

        resultado_el = wait.until(EC.visibility_of_element_located((By.ID, "form:mensajeCiudadano")))
        texto = resultado_el.text.strip()

        return {
            "tiene_antecedentes": "NO TIENE ASUNTOS PENDIENTES CON LAS AUTORIDADES JUDICIALES" not in texto.upper(),
            "texto": texto,
            "method": "session_previa"
        }

    except Exception as e:
        return {"error": f"Error con sesión previa: {str(e)}"}
    finally:
        driver.quit()


def detectar_tipo_captcha(driver):
    """
    Detecta qué tipo de CAPTCHA está mostrando
    """
    try:
        time.sleep(3)  # Esperar que cargue completamente
        
        # Buscar iframes del reCAPTCHA
        captcha_iframes = driver.find_elements(By.CSS_SELECTOR, "iframe[src*='recaptcha']")
        
        print(f"[INFO] Detectados {len(captcha_iframes)} iframes de reCAPTCHA")
        
        if len(captcha_iframes) == 1:
            return "simple"  # Solo checkbox
        elif len(captcha_iframes) >= 2:
            return "complejo"  # Checkbox + imágenes
        else:
            return "ninguno"
            
    except Exception as e:
        print(f"[ERROR] Error detectando tipo de CAPTCHA: {e}")
        return "desconocido"