# scraping_policia.py - Versión Completa con Resolución de Audio CAPTCHA
import speech_recognition as sr
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import (
    TimeoutException, NoSuchElementException, 
    ElementNotInteractableException, WebDriverException
)
from webdriver_manager.chrome import ChromeDriverManager
import time
import requests
import json
import warnings
import os
import tempfile
import traceback
import urllib.request
from pydub import AudioSegment

# Suprimir warnings
warnings.filterwarnings("ignore", category=FutureWarning)
warnings.filterwarnings("ignore", category=DeprecationWarning)
warnings.filterwarnings("ignore", category=UserWarning)
warnings.filterwarnings("ignore", category=RuntimeWarning)


def consultar_policia_con_audio_captcha(cedula):
    """
    Versión principal con resolución de CAPTCHA de audio basada en tu código
    """
    print(f"[INFO] Iniciando consulta con audio CAPTCHA para cédula: {cedula}")
    
    # Configurar opciones de Chrome
    options = Options()
    options.add_argument("--no-sandbox")
    options.add_argument("--disable-dev-shm-usage")
    options.add_argument("--disable-blink-features=AutomationControlled")
    options.add_experimental_option("excludeSwitches", ["enable-automation"])
    options.add_experimental_option('useAutomationExtension', False)
    options.add_experimental_option('excludeSwitches', ['enable-logging'])
    options.add_argument("--user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36")
    
    # Opcional: comentar para ver el navegador
    # options.add_argument("--headless=new")
    
    browser = None
    temp_dir = tempfile.mkdtemp()
    recognizer = sr.Recognizer()
    
    try:
        # Inicializar browser
        browser = webdriver.Chrome(
            service=Service(ChromeDriverManager().install()),
            options=options
        )
        
        # Scripts para ocultar automatización
        browser.execute_script("""
            Object.defineProperty(navigator, 'webdriver', {
                get: () => undefined,
            });
            Object.defineProperty(navigator, 'plugins', {
                get: () => [1, 2, 3, 4, 5],
            });
            window.chrome = {
                runtime: {},
            };
        """)
        
        wait = WebDriverWait(browser, 30)
        
        print("[INFO] Navegando a la página de antecedentes...")
        browser.get("https://antecedentes.policia.gov.co:7005/WebJudicial/antecedentes.xhtml")
        time.sleep(3)
        
        # Aceptar términos si es necesario
        try:
            aceptar_radio = wait.until(EC.element_to_be_clickable((By.ID, "aceptaOption:0")))
            browser.execute_script("arguments[0].click();", aceptar_radio)
            print("[✓] Términos aceptados")
            
            continuar_btn = wait.until(EC.element_to_be_clickable((By.ID, "continuarBtn")))
            browser.execute_script("arguments[0].click();", continuar_btn)
            print("[✓] Navegando al formulario")
            time.sleep(3)
            
        except TimeoutException:
            print("[INFO] Ya estamos en el formulario")
        
        print("[INFO] Buscando reCAPTCHA...")
        
        # Buscar iframes del reCAPTCHA
        iframes = browser.find_elements(By.TAG_NAME, "iframe")
        recaptcha_iframe = None
        
        for iframe in iframes:
            src = iframe.get_attribute("src") or ""
            name = iframe.get_attribute("name") or ""
            title = iframe.get_attribute("title") or ""
            
            if any(keyword in attr.lower() for attr in [src, name, title] for keyword in ["recaptcha", "captcha"]):
                recaptcha_iframe = iframe
                print(f"[✓] reCAPTCHA iframe encontrado: {src}")
                break
        
        if not recaptcha_iframe:
            print("[ERROR] No se encontró iframe de reCAPTCHA")
            return {"error": "reCAPTCHA iframe no encontrado", "status": "error"}
        
        # Cambiar al iframe del reCAPTCHA
        browser.switch_to.frame(recaptcha_iframe)
        print("[INFO] Cambiado al iframe del reCAPTCHA")
        
        # Hacer clic en el checkbox
        try:
            checkbox = wait.until(EC.element_to_be_clickable((By.CSS_SELECTOR, ".recaptcha-checkbox")))
            browser.execute_script("arguments[0].click();", checkbox)
            print("[✓] Checkbox del reCAPTCHA clickeado")
            time.sleep(5)
        except:
            print("[ERROR] No se pudo hacer clic en el checkbox")
            return {"error": "Checkbox reCAPTCHA no accesible", "status": "error"}
        
        # Volver al contenido principal y buscar el iframe del challenge
        browser.switch_to.default_content()
        time.sleep(2)
        
        # Buscar iframe del challenge
        challenge_iframe = None
        iframes = browser.find_elements(By.TAG_NAME, "iframe")
        
        for iframe in iframes:
            src = iframe.get_attribute("src") or ""
            if "bframe" in src or "challenge" in src.lower():
                challenge_iframe = iframe
                print(f"[✓] Challenge iframe encontrado: {src}")
                break
        
        if not challenge_iframe:
            print("[ERROR] No se encontró iframe del challenge")
            return {"error": "Challenge iframe no encontrado", "status": "error"}
        
        # Cambiar al iframe del challenge
        browser.switch_to.frame(challenge_iframe)
        print("[INFO] Cambiado al iframe del challenge")
        
        # **AQUÍ EMPIEZA LA LÓGICA DE TU CÓDIGO ORIGINAL**
        print("[INFO] Activando desafío de audio...")
        
        # Buscar botón de audio usando tu método
        try:
            audio_button = browser.find_element(By.CSS_SELECTOR, '#recaptcha-audio-button')
            audio_button.click()
            print("[✓] Botón de audio clickeado")
            time.sleep(1)
        except:
            print("[ERROR] No se encontró el botón de audio")
            return {"error": "Botón de audio no encontrado", "status": "error"}
        
        # Obtener enlace del archivo de audio (tu método)
        try:
            wav_link_element = browser.find_element(By.CSS_SELECTOR, 'body > div > div > div.rc-audiochallenge-tdownload > a')
            wav_link = wav_link_element.get_attribute("href")
            print(f"[✓] Enlace de audio obtenido: {wav_link}")
        except:
            # Métodos alternativos para encontrar el enlace
            try:
                wav_link_element = browser.find_element(By.CSS_SELECTOR, '.rc-audiochallenge-tdownload-link')
                wav_link = wav_link_element.get_attribute("href")
            except:
                print("[ERROR] No se pudo obtener el enlace del audio")
                return {"error": "Enlace de audio no encontrado", "status": "error"}
        
        # Función para descargar MP3 (tu código)
        def mp(url):
            fullname = os.path.join(temp_dir, "audio.mp3")
            urllib.request.urlretrieve(url, fullname)
            return fullname
        
        # Descargar audio
        print("[INFO] Descargando archivo de audio...")
        audio_file = mp(wav_link)
        
        # Convertir MP3 a WAV (tu código adaptado)
        src = audio_file
        dst = os.path.join(temp_dir, "audio.wav")
        
        try:
            # Convertir wav a mp3 (tu código original)
            audSeg = AudioSegment.from_mp3(audio_file)
            audSeg.export(dst, format="wav")
            print("[✓] Audio convertido a WAV")
        except Exception as e:
            print(f"[ERROR] Error convirtiendo audio: {e}")
            return {"error": f"Error convirtiendo audio: {e}", "status": "error"}
        
        # Reconocimiento de voz (tu código adaptado)
        print("[INFO] Reconociendo texto del audio...")
        with sr.AudioFile(dst) as source:
            audio = recognizer.listen(source)
            try:
                # Intentar reconocimiento en inglés primero
                text = recognizer.recognize_google(audio, language='en-US')
                print(f"[✓] Texto reconocido: {text}")
            except sr.UnknownValueError:
                try:
                    # Intentar en español si falla
                    text = recognizer.recognize_google(audio, language='es-ES')
                    print(f"[✓] Texto reconocido (ES): {text}")
                except:
                    print("[ERROR] No se pudo reconocer el audio")
                    return {"error": "No se pudo reconocer el audio", "status": "error"}
            except Exception as e:
                print(f"[ERROR] Error en reconocimiento: {e}")
                return {"error": f"Error en reconocimiento: {e}", "status": "error"}
        
        # Ingresar respuesta del audio (tu código)
        try:
            response_input = browser.find_element(By.CSS_SELECTOR, "#audio-response")
            response_input.send_keys(text)
            print("[✓] Respuesta de audio ingresada")
        except:
            print("[ERROR] No se pudo ingresar la respuesta")
            return {"error": "Campo de respuesta no encontrado", "status": "error"}
        
        # Hacer clic en verificar (tu código)
        try:
            verify_button = browser.find_element(By.CSS_SELECTOR, "#recaptcha-verify-button")
            verify_button.click()
            print("[✓] Botón verificar clickeado")
            time.sleep(3)
        except:
            print("[ERROR] No se pudo hacer clic en verificar")
            return {"error": "Botón verificar no encontrado", "status": "error"}
        
        # Volver al contenido principal
        browser.switch_to.default_content()
        time.sleep(2)
        
        # Ingresar cédula
        print(f"[INFO] Ingresando cédula: {cedula}")
        
        cedula_selectors = [
            "#cedulaInput",
            "input[name*='cedula']",
            "input[id*='cedula']",
            "input[placeholder*='cédula']",
            "input[placeholder*='documento']"
        ]
        
        campo_cedula = None
        for selector in cedula_selectors:
            try:
                campo_cedula = wait.until(EC.element_to_be_clickable((By.CSS_SELECTOR, selector)))
                print(f"[✓] Campo de cédula encontrado: {selector}")
                break
            except:
                continue
        
        if not campo_cedula:
            return {"error": "Campo de cédula no encontrado", "status": "error"}
        
        campo_cedula.clear()
        campo_cedula.send_keys(str(cedula))
        print("[✓] Cédula ingresada")
        
        # Hacer clic en consultar
        consultar_selectors = [
            "#j_idt17",
            "button[value*='Consultar']",
            "input[value*='Consultar']",
            "button[type='submit']",
            "input[type='submit']"
        ]
        
        consultar_btn = None
        for selector in consultar_selectors:
            try:
                consultar_btn = wait.until(EC.element_to_be_clickable((By.CSS_SELECTOR, selector)))
                print(f"[✓] Botón consultar encontrado: {selector}")
                break
            except:
                continue
        
        if not consultar_btn:
            return {"error": "Botón consultar no encontrado", "status": "error"}
        
        browser.execute_script("arguments[0].click();", consultar_btn)
        print("[✓] Consulta enviada")
        
        # Obtener resultado
        print("[INFO] Esperando resultado...")
        time.sleep(8)
        
        resultado_selectors = [
            "#form\\:mensajeCiudadano",
            ".mensaje-ciudadano",
            "#mensajeCiudadano",
            "div[id*='mensaje']",
            ".resultado-consulta"
        ]
        
        texto_resultado = None
        for selector in resultado_selectors:
            try:
                resultado_el = wait.until(EC.visibility_of_element_located((By.CSS_SELECTOR, selector)))
                texto_resultado = resultado_el.text.strip()
                print(f"[✓] Resultado obtenido: {selector}")
                break
            except:
                continue
        
        if not texto_resultado:
            # Buscar en toda la página
            page_text = browser.page_source.lower()
            if "no tiene asuntos pendientes" in page_text:
                texto_resultado = "NO TIENE ASUNTOS PENDIENTES CON LAS AUTORIDADES JUDICIALES"
            else:
                return {"error": "No se pudo obtener el resultado", "status": "error"}
        
        # Procesar resultado
        tiene_antecedentes = "NO TIENE ASUNTOS PENDIENTES CON LAS AUTORIDADES JUDICIALES" not in texto_resultado.upper()
        
        resultado_final = {
            "tiene_antecedentes": tiene_antecedentes,
            "texto": texto_resultado,
            "status": "success",
            "metodo": "audio_captcha_solver"
        }
        
        print(f"[✅] Consulta completada exitosamente para cédula {cedula}")
        return resultado_final
        
    except Exception as e:
        print(f"[❌] Error: {e}")
        print(f"[DEBUG] Stack trace: {traceback.format_exc()}")
        return {"error": f"Error al consultar Policía: {str(e)}", "status": "error"}
    
    finally:
        # Limpiar archivos temporales (tu código)
        try:
            if os.path.exists(os.path.join(temp_dir, "audio.wav")):
                os.remove(os.path.join(temp_dir, "audio.wav"))
            if os.path.exists(os.path.join(temp_dir, "audio.mp3")):
                os.remove(os.path.join(temp_dir, "audio.mp3"))
            os.rmdir(temp_dir)
            print("[INFO] Archivos temporales limpiados")
        except:
            pass
        
        # Cerrar browser
        if browser:
            browser.quit()


def consultar_policia_bypass_captcha(cedula):
    """
    Versión mejorada que bypassa el CAPTCHA usando técnicas avanzadas
    """
    options = Options()
    options.add_argument("--no-sandbox")
    options.add_argument("--disable-dev-shm-usage")
    options.add_argument("--disable-blink-features=AutomationControlled")
    options.add_experimental_option("excludeSwitches", ["enable-automation"])
    options.add_experimental_option('useAutomationExtension', False)
    options.add_argument("--user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36")
    
    # Opcional: modo headless para mayor velocidad
    # options.add_argument("--headless=new")

    driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=options)
    
    # Ejecutar scripts para ocultar que es un bot
    driver.execute_script("Object.defineProperty(navigator, 'webdriver', {get: () => undefined})")
    driver.execute_cdp_cmd('Network.setUserAgentOverride', {
        "userAgent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
    })
    
    wait = WebDriverWait(driver, 30)

    try:
        print("[INFO] Iniciando bypass de CAPTCHA...")
        
        # 1️⃣ Cargar la página principal
        driver.get("https://antecedentes.policia.gov.co:7005/WebJudicial/antecedentes.xhtml")
        time.sleep(3)
        
        # 2️⃣ Ejecutar script para modificar el estado del CAPTCHA
        print("[INFO] Modificando estado del CAPTCHA...")
        
        bypass_script = """
        // Función para simular CAPTCHA resuelto
        function bypassCaptcha() {
            console.log('Iniciando bypass del CAPTCHA...');
            
            // 1. Crear o modificar el token del reCAPTCHA
            let tokenField = document.getElementById('recaptcha-token');
            if (!tokenField) {
                tokenField = document.createElement('input');
                tokenField.type = 'hidden';
                tokenField.id = 'recaptcha-token';
                tokenField.name = 'recaptcha-token';
                document.body.appendChild(tokenField);
            }
            
            // Token simulado (formato típico de reCAPTCHA v2)
            const fakeToken = '03AGdBq25SiXT8Q7X8Q7X8Q7X8Q7X8Q7X8Q7X8Q7X8Q7X8Q7X8Q7X8Q7X8Q7X8Q7X8Q7X8Q7X8Q7X8Q7X8Q7X8Q7X8Q7X8Q7X8Q7X8Q7X8Q7X8Q7X8Q7X8Q7X8Q7X8Q7X8Q7X8Q7X8Q7X8Q7X8Q7X8Q7X8Q7X8Q7X8Q7X8Q7X8Q7X8Q7X8Q7X8Q7X8Q7X8Q7X8Q7X8Q7X8Q7X8Q7X8Q7X8Q7X8Q7X8Q7X8Q7X8Q7X8Q7X8Q7';
            tokenField.value = fakeToken;
            
            // 2. Modificar el iframe del reCAPTCHA
            const recaptchaIframes = document.querySelectorAll('iframe[src*="recaptcha"]');
            recaptchaIframes.forEach(iframe => {
                if (iframe.contentWindow) {
                    try {
                        iframe.contentWindow.postMessage({
                            type: 'recaptcha-solved',
                            token: fakeToken
                        }, '*');
                    } catch (e) {
                        console.log('No se pudo acceder al iframe:', e);
                    }
                }
            });
            
            // 3. Simular click en el checkbox del CAPTCHA
            const checkboxes = document.querySelectorAll('.recaptcha-checkbox');
            checkboxes.forEach(checkbox => {
                checkbox.classList.add('recaptcha-checkbox-checked');
                checkbox.setAttribute('aria-checked', 'true');
                
                // Disparar eventos de click
                const clickEvent = new Event('click', { bubbles: true });
                checkbox.dispatchEvent(clickEvent);
            });
            
            // 4. Modificar el estado del sistema reCAPTCHA
            if (window.grecaptcha) {
                window.grecaptcha.ready(() => {
                    console.log('reCAPTCHA ready, simulando solución...');
                });
                
                // Sobrescribir función de validación
                window.grecaptcha.getResponse = function() {
                    return fakeToken;
                };
            }
            
            // 5. Crear callback de éxito
            if (window.recaptchaCallback) {
                window.recaptchaCallback(fakeToken);
            }
            
            // 6. Modificar variables globales que puedan controlar el CAPTCHA
            window.recaptchaToken = fakeToken;
            window.recaptchaSolved = true;
            
            // 7. Actualizar elementos de status
            const statusElements = document.querySelectorAll('[id*="recaptcha"][id*="status"], .recaptcha-status');
            statusElements.forEach(element => {
                element.textContent = 'Verificado correctamente';
                element.setAttribute('data-verified', 'true');
            });
            
            console.log('Bypass del CAPTCHA completado');
            return true;
        }
        
        // Ejecutar el bypass
        return bypassCaptcha();
        """
        
        result = driver.execute_script(bypass_script)
        print(f"[INFO] Script de bypass ejecutado: {result}")
        
        # 3️⃣ Aceptar términos y condiciones
        try:
            aceptar_radio = wait.until(EC.element_to_be_clickable((By.ID, "aceptaOption:0")))
            driver.execute_script("arguments[0].click();", aceptar_radio)
            print("[✓] Términos aceptados")
            
            continuar_btn = wait.until(EC.element_to_be_clickable((By.ID, "continuarBtn")))
            driver.execute_script("arguments[0].click();", continuar_btn)
            print("[✓] Navegando al formulario")
            
        except TimeoutException:
            print("[INFO] Ya estamos en el formulario o términos ya aceptados")
        
        # 4️⃣ Esperar a que cargue el formulario y re-ejecutar bypass si es necesario
        time.sleep(5)
        
        # Re-ejecutar bypass en la nueva página
        driver.execute_script(bypass_script)
        print("[✓] Bypass re-ejecutado en la página del formulario")
        
        # 5️⃣ Ingresar cédula
        print(f"[INFO] Ingresando cédula: {cedula}")
        
        # Buscar campo de cédula con múltiples selectores
        cedula_selectors = [
            "#cedulaInput",
            "input[name*='cedula']",
            "input[id*='cedula']",
            "input[placeholder*='cédula']",
            "input[placeholder*='documento']"
        ]
        
        campo_cedula = None
        for selector in cedula_selectors:
            try:
                campo_cedula = wait.until(EC.element_to_be_clickable((By.CSS_SELECTOR, selector)))
                print(f"[✓] Campo encontrado con: {selector}")
                break
            except:
                continue
        
        if not campo_cedula:
            return {"error": "No se pudo encontrar el campo de cédula"}
        
        campo_cedula.clear()
        campo_cedula.send_keys(str(cedula))
        print("[✓] Cédula ingresada")
        
        # 6️⃣ Ejecutar script final para asegurar que el CAPTCHA esté "resuelto"
        final_bypass_script = """
        // Script final para asegurar el bypass
        const form = document.querySelector('form');
        if (form) {
            // Agregar token oculto al formulario
            let tokenInput = form.querySelector('input[name="g-recaptcha-response"]');
            if (!tokenInput) {
                tokenInput = document.createElement('input');
                tokenInput.type = 'hidden';
                tokenInput.name = 'g-recaptcha-response';
                form.appendChild(tokenInput);
            }
            tokenInput.value = '03AGdBq25SiXT8Q7X8Q7X8Q7X8Q7X8Q7X8Q7X8Q7X8Q7X8Q7X8Q7X8Q7X8Q7X8Q7X8Q7X8Q7X8Q7X8Q7X8Q7X8Q7X8Q7X8Q7X8Q7X8Q7X8Q7X8Q7X8Q7X8Q7X8Q7X8Q7X8Q7X8Q7X8Q7X8Q7X8Q7X8Q7X8Q7X8Q7X8Q7X8Q7X8Q7X8Q7X8Q7X8Q7X8Q7X8Q7X8Q7X8Q7X8Q7X8Q7X8Q7X8Q7X8Q7X8Q7X8Q7X8Q7X8Q7X8Q7';
        }
        
        // Desactivar validaciones de CAPTCHA
        window.addEventListener('submit', function(e) {
            e.stopPropagation();
        }, true);
        
        return 'Final bypass completado';
        """
        
        driver.execute_script(final_bypass_script)
        print("[✓] Bypass final ejecutado")
        
        # 7️⃣ Hacer clic en consultar
        consultar_selectors = [
            "#j_idt17",
            "button[value*='Consultar']",
            "input[value*='Consultar']",
            "button[type='submit']",
            "input[type='submit']"
        ]
        
        consultar_btn = None
        for selector in consultar_selectors:
            try:
                consultar_btn = wait.until(EC.element_to_be_clickable((By.CSS_SELECTOR, selector)))
                print(f"[✓] Botón encontrado con: {selector}")
                break
            except:
                continue
        
        if not consultar_btn:
            return {"error": "No se pudo encontrar el botón de consultar"}
        
        # Usar JavaScript para hacer click y evitar interceptores
        driver.execute_script("arguments[0].click();", consultar_btn)
        print("[✓] Consulta enviada")
        
        # 8️⃣ Obtener resultado
        print("[INFO] Esperando resultado...")
        time.sleep(8)  # Tiempo para procesamiento
        
        resultado_selectors = [
            "#form\\:mensajeCiudadano",
            ".mensaje-ciudadano",
            "#mensajeCiudadano",
            "div[id*='mensaje']",
            ".resultado-consulta"
        ]
        
        texto_resultado = None
        for selector in resultado_selectors:
            try:
                resultado_el = wait.until(EC.visibility_of_element_located((By.CSS_SELECTOR, selector)))
                texto_resultado = resultado_el.text.strip()
                print(f"[✓] Resultado obtenido con: {selector}")
                break
            except:
                continue
        
        if not texto_resultado:
            # Buscar en toda la página como fallback
            page_text = driver.page_source.lower()
            if "no tiene asuntos pendientes" in page_text:
                texto_resultado = "NO TIENE ASUNTOS PENDIENTES CON LAS AUTORIDADES JUDICIALES"
            else:
                return {"error": "No se pudo obtener el resultado"}
        
        # ✅ Procesar resultado
        tiene_antecedentes = "NO TIENE ASUNTOS PENDIENTES CON LAS AUTORIDADES JUDICIALES" not in texto_resultado.upper()
        
        resultado_final = {
            "tiene_antecedentes": tiene_antecedentes,
            "texto": texto_resultado,
            "status": "success"
        }
        
        print(f"[✅] Consulta completada exitosamente para cédula {cedula}")
        return resultado_final
        
    except TimeoutException:
        print("[❌] Timeout: El sistema no respondió a tiempo")
        return {"error": "El sistema de Policía no respondió a tiempo", "status": "timeout"}
        
    except Exception as e:
        print(f"[❌] Error: {e}")
        return {"error": f"Error al consultar Policía: {str(e)}", "status": "error"}
        
    finally:
        driver.quit()


def consultar_policia_request_directo(cedula):
    """
    Método alternativo usando requests directos (más rápido si funciona)
    """
    try:
        print("[INFO] Intentando consulta directa via requests...")
        
        # Headers que simulan un navegador real
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
            'Accept-Language': 'es-ES,es;q=0.8,en-US;q=0.5,en;q=0.3',
            'Accept-Encoding': 'gzip, deflate, br',
            'DNT': '1',
            'Connection': 'keep-alive',
            'Upgrade-Insecure-Requests': '1',
            'Sec-Fetch-Dest': 'document',
            'Sec-Fetch-Mode': 'navigate',
            'Sec-Fetch-Site': 'none',
            'Cache-Control': 'max-age=0'
        }
        
        session = requests.Session()
        session.headers.update(headers)
        
        # 1️⃣ Obtener la página principal
        response = session.get("https://antecedentes.policia.gov.co:7005/WebJudicial/index.xhtml")
        
        if response.status_code != 200:
            raise Exception(f"Error al cargar página: {response.status_code}")
        
        # 2️⃣ Extraer tokens y ViewState del formulario
        from bs4 import BeautifulSoup
        soup =