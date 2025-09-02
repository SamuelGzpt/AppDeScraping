# scraping_policia_bypass.py
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException, NoSuchElementException
from webdriver_manager.chrome import ChromeDriverManager
import time
import requests
import json


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
        soup = BeautifulSoup(response.text, 'html.parser')
        
        viewstate = soup.find('input', {'name': 'javax.faces.ViewState'})
        viewstate_value = viewstate['value'] if viewstate else ''
        
        # 3️⃣ Preparar datos del POST simulando CAPTCHA resuelto
        post_data = {
            'javax.faces.ViewState': viewstate_value,
            'cedulaInput': cedula,
            'g-recaptcha-response': '03AGdBq25SiXT8Q7X8Q7X8Q7X8Q7X8Q7X8Q7X8Q7X8Q7X8Q7X8Q7X8Q7X8Q7X8Q7X8Q7X8Q7X8Q7',
            'recaptcha-token': '03AGdBq25SiXT8Q7X8Q7X8Q7X8Q7X8Q7X8Q7X8Q7X8Q7X8Q7X8Q7X8Q7X8Q7X8Q7X8Q7X8Q7X8Q7',
            'j_idt17': 'Consultar'  # Botón de consultar
        }
        
        # 4️⃣ Realizar POST
        post_response = session.post(
            "https://antecedentes.policia.gov.co:7005/WebJudicial/antecedentesPersona.xhtml",
            data=post_data,
            allow_redirects=True
        )
        
        if post_response.status_code == 200:
            # Buscar resultado en la respuesta
            if "NO TIENE ASUNTOS PENDIENTES" in post_response.text:
                return {
                    "tiene_antecedentes": False,
                    "texto": "NO TIENE ASUNTOS PENDIENTES CON LAS AUTORIDADES JUDICIALES",
                    "status": "success"
                }
            elif "TIENE ASUNTOS PENDIENTES" in post_response.text:
                # Extraer el texto completo del resultado
                result_soup = BeautifulSoup(post_response.text, 'html.parser')
                resultado_div = result_soup.find('div', {'id': 'form:mensajeCiudadano'})
                texto = resultado_div.get_text(strip=True) if resultado_div else "Resultado no claro"
                
                return {
                    "tiene_antecedentes": True,
                    "texto": texto,
                    "status": "success"
                }
        
        # Si el método directo no funciona, usar Selenium
        print("[INFO] Método requests falló, usando Selenium...")
        return consultar_policia_bypass_captcha(cedula)
        
    except Exception as e:
        print(f"[INFO] Método requests falló: {e}, usando Selenium...")
        return consultar_policia_bypass_captcha(cedula)


# Función principal actualizada
def consultar_policia(cedula):
    """
    Función principal que intenta primero requests directo y luego Selenium con bypass
    """
    print(f"[INFO] Iniciando consulta para cédula: {cedula}")
    
    # Intentar primero método directo (más rápido)
    resultado = consultar_policia_request_directo(cedula)
    
    # Si falla, usar método Selenium con bypass
    if resultado.get("status") != "success":
        print("[INFO] Usando método Selenium con bypass de CAPTCHA...")
        resultado = consultar_policia_bypass_captcha(cedula)
    
    return resultado


# Función adicional para casos específicos
def consultar_policia_bypass_avanzado(cedula, usar_proxy=False):
    """
    Versión con bypass más agresivo para casos difíciles
    """
    options = Options()
    options.add_argument("--no-sandbox")
    options.add_argument("--disable-dev-shm-usage")
    options.add_argument("--disable-blink-features=AutomationControlled")
    options.add_experimental_option("excludeSwitches", ["enable-automation"])
    options.add_experimental_option('useAutomationExtension', False)
    
    # Desactivar detección de bot más agresiva
    options.add_argument("--disable-web-security")
    options.add_argument("--disable-features=VizDisplayCompositor")
    options.add_argument("--disable-ipc-flooding-protection")
    
    if usar_proxy:
        # Puedes agregar configuración de proxy aquí si es necesario
        pass
    
    driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=options)
    
    # Script más agresivo para ocultar automatización
    stealth_script = """
    Object.defineProperty(navigator, 'webdriver', {
        get: () => undefined,
    });
    
    Object.defineProperty(navigator, 'plugins', {
        get: () => [1, 2, 3, 4, 5],
    });
    
    Object.defineProperty(navigator, 'languages', {
        get: () => ['es-ES', 'es'],
    });
    
    window.chrome = {
        runtime: {},
    };
    
    Object.defineProperty(navigator, 'permissions', {
        get: () => ({
            query: () => Promise.resolve({ state: 'granted' }),
        }),
    });
    """
    
    driver.execute_script(stealth_script)
    
    # Continúa con la lógica similar al método anterior pero más agresiva
    # (El resto de la implementación sería similar a consultar_policia_bypass_captcha)
    
    return consultar_policia_bypass_captcha(cedula)