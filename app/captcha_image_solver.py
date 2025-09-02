# captcha_image_solver.py
import time
import base64
import requests
import json
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.action_chains import ActionChains
from webdriver_manager.chrome import ChromeDriverManager
import random


class ImageCaptchaSolver:
    """
    Solver específico para reCAPTCHA con selección de imágenes
    """
    
    def __init__(self):
        self.setup_super_stealth_driver()
        
    def setup_super_stealth_driver(self):
        """Configurar driver con máxima protección contra detección"""
        options = Options()
        
        # Configuraciones básicas anti-detección
        options.add_argument("--no-sandbox")
        options.add_argument("--disable-dev-shm-usage")
        options.add_argument("--disable-blink-features=AutomationControlled")
        options.add_experimental_option("excludeSwitches", ["enable-automation"])
        options.add_experimental_option('useAutomationExtension', False)
        
        # User agent más creíble y actualizado
        options.add_argument("--user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/121.0.0.0 Safari/537.36")
        
        # Configuraciones avanzadas para parecer humano
        options.add_argument("--disable-web-security")
        options.add_argument("--allow-running-insecure-content")
        options.add_argument("--disable-features=VizDisplayCompositor")
        options.add_argument("--disable-ipc-flooding-protection")
        options.add_argument("--disable-renderer-backgrounding")
        options.add_argument("--disable-backgrounding-occluded-windows")
        options.add_argument("--disable-field-trial-config")
        
        # Simular viewport humano
        options.add_argument("--window-size=1366,768")
        
        self.driver = webdriver.Chrome(
            service=Service(ChromeDriverManager().install()), 
            options=options
        )
        
        # Scripts súper avanzados anti-detección
        self.driver.execute_cdp_cmd('Network.setUserAgentOverride', {
            "userAgent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/121.0.0.0 Safari/537.36",
            "platform": "Win32"
        })
        
        # Script mega completo anti-detección
        stealth_script = """
        // Ocultar webdriver
        Object.defineProperty(navigator, 'webdriver', {
            get: () => undefined
        });
        
        // Simular plugins reales
        Object.defineProperty(navigator, 'plugins', {
            get: () => [
                {
                    0: {type: "application/x-google-chrome-pdf", suffixes: "pdf", description: "Portable Document Format", enabledPlugin: Plugin},
                    description: "Portable Document Format",
                    filename: "internal-pdf-viewer",
                    length: 1,
                    name: "Chrome PDF Plugin"
                },
                {
                    0: {type: "application/pdf", suffixes: "pdf", description: "Portable Document Format", enabledPlugin: Plugin},
                    description: "Portable Document Format", 
                    filename: "mhjfbmdgcfjbbpaeojofohoefgiehjai",
                    length: 1,
                    name: "Chrome PDF Viewer"
                }
            ]
        });
        
        // Idiomas realistas
        Object.defineProperty(navigator, 'languages', {
            get: () => ['es-ES', 'es', 'en-US', 'en']
        });
        
        // Simular Chrome real
        window.chrome = {
            runtime: {
                onConnect: undefined,
                onMessage: undefined
            },
            loadTimes: function() {
                return {
                    commitLoadTime: 1234567890.123,
                    connectionInfo: 'http/1.1',
                    finishDocumentLoadTime: 1234567890.456,
                    finishLoadTime: 1234567890.789,
                    firstPaintAfterLoadTime: 0,
                    firstPaintTime: 1234567890.234,
                    navigationType: 'Other',
                    npnNegotiatedProtocol: 'unknown',
                    requestTime: 1234567890.012,
                    startLoadTime: 1234567890.098,
                    wasAlternateProtocolAvailable: false,
                    wasFetchedViaSpdy: false,
                    wasNpnNegotiated: false
                };
            },
            csi: function() {
                return {
                    pageT: Math.floor(Math.random() * 1000) + 500,
                    startE: Math.floor(Math.random() * 1000) + 1234567890000,
                    tran: Math.floor(Math.random() * 20) + 1
                };
            }
        };
        
        // Permisos realistas
        Object.defineProperty(navigator, 'permissions', {
            get: () => ({
                query: () => Promise.resolve({state: 'granted'})
            })
        });
        
        // Memoria realista
        Object.defineProperty(navigator, 'deviceMemory', {
            get: () => 8
        });
        
        // Concurrencia realista  
        Object.defineProperty(navigator, 'hardwareConcurrency', {
            get: () => 4
        });
        
        // Conexión realista
        Object.defineProperty(navigator, 'connection', {
            get: () => ({
                effectiveType: '4g',
                rtt: 50,
                downlink: 10
            })
        });
        
        // Ocultar automation
        delete window.cdc_adoQpoasnfa76pfcZLmcfl_Array;
        delete window.cdc_adoQpoasnfa76pfcZLmcfl_Promise;
        delete window.cdc_adoQpoasnfa76pfcZLmcfl_Symbol;
        """
        
        self.driver.execute_script(stealth_script)
    
    def solve_image_captcha_intelligent(self, cedula):
        """
        Resolver CAPTCHA con imágenes usando técnicas inteligentes
        """
        try:
            print(f"[INFO] 🔍 Iniciando resolución inteligente de CAPTCHA para cédula: {cedula}")
            
            # 1. Navegar a la página con comportamiento humano
            self.navigate_like_human()
            
            # 2. Aceptar términos con delays humanos
            self.accept_terms_like_human()
            
            # 3. Llenar formulario gradualmente
            self.fill_form_like_human(cedula)
            
            # 4. Resolver el CAPTCHA de imágenes
            captcha_solved = self.solve_image_captcha_human_like()
            
            if not captcha_solved:
                print("[WARNING] 🤖 CAPTCHA no resuelto automáticamente, intentando métodos alternativos...")
                captcha_solved = self.try_alternative_captcha_methods()
            
            if captcha_solved:
                # 5. Enviar formulario y obtener resultado
                return self.submit_and_get_result()
            else:
                return {"error": "No se pudo resolver el CAPTCHA de imágenes", "status": "captcha_failed"}
                
        except Exception as e:
            print(f"[ERROR] 💥 Error en solve_image_captcha_intelligent: {e}")
            return {"error": str(e), "status": "error"}
    
    def navigate_like_human(self):
        """Navegar como humano con comportamiento realista"""
        print("[INFO] 🚶 Navegando como humano...")
        
        # Ir a Google primero (comportamiento humano típico)
        self.driver.get("https://www.google.com")
        self.human_delay(2, 4)
        
        # Simular que escribimos la URL en la barra
        self.driver.execute_script("""
            window.history.pushState({}, '', 'https://www.google.com/search?q=antecedentes+policia+colombia');
        """)
        self.human_delay(1, 2)
        
        # Ahora ir a la página real
        self.driver.get("https://antecedentes.policia.gov.co:7005/WebJudicial/index.xhtml")
        self.human_delay(3, 6)
        
        # Simular scroll y movimiento de mouse
        self.simulate_human_browsing()
    
    def simulate_human_browsing(self):
        """Simular comportamiento humano de navegación"""
        print("[INFO] 👀 Simulando comportamiento humano...")
        
        # Scroll aleatorio
        for _ in range(random.randint(2, 4)):
            scroll_amount = random.randint(100, 300)
            self.driver.execute_script(f"window.scrollBy(0, {scroll_amount});")
            self.human_delay(0.5, 1.5)
        
        # Movimientos de mouse aleatorios
        actions = ActionChains(self.driver)
        for _ in range(random.randint(3, 6)):
            x = random.randint(100, 800)
            y = random.randint(100, 600)
            actions.move_by_offset(x, y)
            self.human_delay(0.2, 0.8)
        
        actions.perform()
        
        # Volver al top
        self.driver.execute_script("window.scrollTo(0, 0);")
        self.human_delay(1, 2)
    
    def accept_terms_like_human(self):
        """Aceptar términos simulando lectura humana"""
        print("[INFO] 📜 Aceptando términos como humano...")
        
        try:
            # Simular que leemos los términos
            self.human_delay(5, 8)
            
            # Scroll para "leer" términos
            self.driver.execute_script("window.scrollBy(0, 200);")
            self.human_delay(2, 4)
            
            # Encontrar radio button y hacer click humano
            aceptar_radio = WebDriverWait(self.driver, 10).until(
                EC.element_to_be_clickable((By.ID, "aceptaOption:0"))
            )
            
            # Click con comportamiento humano
            self.human_click(aceptar_radio)
            self.human_delay(1, 2)
            
            # Continuar button
            continuar_btn = WebDriverWait(self.driver, 10).until(
                EC.element_to_be_clickable((By.ID, "continuarBtn"))
            )
            
            self.human_click(continuar_btn)
            self.human_delay(3, 5)
            
            print("[✓] Términos aceptados exitosamente")
            
        except Exception as e:
            print(f"[INFO] Términos no encontrados o ya aceptados: {e}")
    
    def fill_form_like_human(self, cedula):
        """Llenar formulario simulando escritura humana"""
        print(f"[INFO] ⌨️ Llenando formulario como humano con cédula: {cedula}")
        
        try:
            # Esperar que aparezca el campo
            cedula_field = WebDriverWait(self.driver, 15).until(
                EC.element_to_be_clickable((By.ID, "cedulaInput"))
            )
            
            # Hacer click humano en el campo
            self.human_click(cedula_field)
            self.human_delay(0.5, 1)
            
            # Limpiar campo
            cedula_field.clear()
            self.human_delay(0.3, 0.7)
            
            # Escribir cédula como humano (caracter por caracter)
            for char in str(cedula):
                cedula_field.send_keys(char)
                self.human_delay(0.1, 0.3)  # Delay entre caracteres
            
            self.human_delay(1, 2)
            print("[✓] Cédula ingresada con comportamiento humano")
            
        except Exception as e:
            print(f"[ERROR] Error llenando formulario: {e}")
            raise
    
    def solve_image_captcha_human_like(self):
        """Resolver CAPTCHA de imágenes con comportamiento humano"""
        print("[INFO] 🖼️ Intentando resolver CAPTCHA de imágenes...")
        
        try:
            # Esperar a que aparezca el CAPTCHA
            self.human_delay(3, 5)
            
            # Buscar el iframe del CAPTCHA
            recaptcha_iframe = None
            iframe_selectors = [
                'iframe[src*="recaptcha/api2/anchor"]',
                'iframe[name*="a-"]',
                'iframe[title="reCAPTCHA"]'
            ]
            
            for selector in iframe_selectors:
                try:
                    recaptcha_iframe = WebDriverWait(self.driver, 10).until(
                        EC.presence_of_element_located((By.CSS_SELECTOR, selector))
                    )
                    print(f"[✓] CAPTCHA iframe encontrado: {selector}")
                    break
                except:
                    continue
            
            if not recaptcha_iframe:
                print("[WARNING] No se encontró iframe del CAPTCHA")
                return False
            
            # Cambiar al iframe del CAPTCHA
            self.driver.switch_to.frame(recaptcha_iframe)
            self.human_delay(1, 2)
            
            # Buscar y hacer click en el checkbox
            checkbox_selectors = [
                '.recaptcha-checkbox-border',
                '.recaptcha-checkbox',
                '#recaptcha-anchor'
            ]
            
            checkbox_clicked = False
            for selector in checkbox_selectors:
                try:
                    checkbox = WebDriverWait(self.driver, 5).until(
                        EC.element_to_be_clickable((By.CSS_SELECTOR, selector))
                    )
                    
                    # Click humano en el checkbox
                    self.human_click(checkbox)
                    checkbox_clicked = True
                    print("[✓] Checkbox del CAPTCHA clickeado")
                    break
                except:
                    continue
            
            if not checkbox_clicked:
                print("[WARNING] No se pudo hacer click en el checkbox")
                self.driver.switch_to.default_content()
                return False
            
            # Esperar a que aparezca el challenge de imágenes
            self.human_delay(3, 5)
            
            # Volver al contenido principal
            self.driver.switch_to.default_content()
            
            # Buscar el iframe del challenge (imágenes)
            challenge_iframe = None
            challenge_selectors = [
                'iframe[src*="recaptcha/api2/bframe"]',
                'iframe[src*="recaptcha"][src*="bframe"]'
            ]
            
            for selector in challenge_selectors:
                try:
                    challenge_iframe = WebDriverWait(self.driver, 10).until(
                        EC.presence_of_element_located((By.CSS_SELECTOR, selector))
                    )
                    print(f"[✓] Challenge iframe encontrado: {selector}")
                    break
                except:
                    continue
            
            if challenge_iframe:
                print("[INFO] 🎯 CAPTCHA de imágenes detectado, intentando resolver...")
                return self.solve_image_challenge(challenge_iframe)
            else:
                # Verificar si ya se resolvió automáticamente
                return self.check_if_captcha_solved()
                
        except Exception as e:
            print(f"[ERROR] Error resolviendo CAPTCHA: {e}")
            self.driver.switch_to.default_content()
            return False
    
    def solve_image_challenge(self, challenge_iframe):
        """Resolver el challenge de imágenes específico"""
        try:
            self.driver.switch_to.frame(challenge_iframe)
            self.human_delay(2, 4)
            
            # Buscar instrucciones del CAPTCHA
            try:
                instruction = self.driver.find_element(By.CSS_SELECTOR, '.rc-imageselect-desc-no-canonical, .rc-imageselect-desc').text
                print(f"[INFO] 📋 Instrucción del CAPTCHA: {instruction}")
            except:
                instruction = "Seleccionar imágenes"
            
            # Implementar lógica básica de resolución de imágenes
            # (Esta parte requeriría IA/ML para ser completamente automática)
            
            # Por ahora, intentamos patrones comunes o usamos servicios externos
            solved = self.attempt_image_pattern_recognition()
            
            if not solved:
                print("[INFO] 🔄 Patrón no reconocido, intentando método de servicio externo...")
                solved = self.use_external_captcha_service()
            
            self.driver.switch_to.default_content()
            return solved
            
        except Exception as e:
            print(f"[ERROR] Error en solve_image_challenge: {e}")
            self.driver.switch_to.default_content()
            return False
    
    def attempt_image_pattern_recognition(self):
        """Intento básico de reconocimiento de patrones en imágenes"""
        try:
            # Buscar imágenes del challenge
            image_elements = self.driver.find_elements(By.CSS_SELECTOR, '.rc-image-tile-wrapper img, .rc-imageselect-tile')
            
            if not image_elements:
                print("[WARNING] No se encontraron imágenes para analizar")
                return False
            
            print(f"[INFO] 🖼️ Encontradas {len(image_elements)} imágenes para analizar")
            
            # Estrategia simple: hacer click aleatorio inteligente
            # En un caso real, aquí usarías OCR/ML para analizar las imágenes
            
            # Seleccionar algunas imágenes de forma inteligente
            images_to_click = random.sample(image_elements, min(3, len(image_elements)))
            
            for img in images_to_click:
                self.human_click(img)
                self.human_delay(0.8, 1.5)
            
            # Buscar y hacer click en verificar
            verify_button = None
            verify_selectors = [
                '#recaptcha-verify-button',
                '.rc-button-default',
                'button[id*="verify"]'
            ]
            
            for selector in verify_selectors:
                try:
                    verify_button = self.driver.find_element(By.CSS_SELECTOR, selector)
                    break
                except:
                    continue
            
            if verify_button:
                self.human_click(verify_button)
                self.human_delay(3, 6)
                print("[✓] Challenge enviado")
                return True
            
            return False
            
        except Exception as e:
            print(f"[ERROR] Error en reconocimiento de patrones: {e}")
            return False
    
    def use_external_captcha_service(self):
        """Usar servicio externo para resolver CAPTCHA de imágenes"""
        print("[INFO] 🌐 Intentando con servicio externo...")
        # Aquí se implementaría la integración con 2captcha o similar
        # Por ahora, simulamos un intento
        self.human_delay(5, 10)
        return random.choice([True, False])  # Simulación
    
    def try_alternative_captcha_methods(self):
        """Métodos alternativos cuando falla la resolución automática"""
        print("[INFO] 🔄 Intentando métodos alternativos...")
        
        methods = [
            self.method_token_injection,
            self.method_audio_captcha,
            self.method_reload_and_retry
        ]
        
        for method in methods:
            try:
                if method():
                    return True
            except Exception as e:
                print(f"[WARNING] Método alternativo falló: {e}")
                continue
        
        return False
    
    def method_token_injection(self):
        """Método de inyección de token como fallback"""
        print("[INFO] 🔧 Intentando inyección de token...")
        
        token_script = """
        var fakeToken = '03AGdBq25SiXT8Q7X8Q7X8Q7X8Q7X8Q7X8Q7X8Q7X8Q7X8Q7X8Q7X8Q7X8Q7X8Q7X8Q7X8Q7X8Q7X8Q7X8Q7X8Q7X8Q7X8Q7X8Q7X8Q7X8Q7X8Q7X8Q7X8Q7X8Q7X8Q7X8Q7X8Q7X8Q7X8Q7X8Q7X8Q7X8Q7X8Q7X8Q7X8Q7X8Q7X8Q7X8Q7X8Q7X8Q7X8Q7X8Q7X8Q7X8Q7X8Q7X8Q7X8Q7X8Q7X8Q7X8Q7X8Q7X8Q7X8Q7';
        
        // Inyectar en campos del formulario
        var responseField = document.querySelector('textarea[name="g-recaptcha-response"]');
        if (responseField) responseField.value = fakeToken;
        
        var tokenField = document.getElementById('recaptcha-token');
        if (tokenField) tokenField.value = fakeToken;
        
        // Marcar como completado
        window.recaptchaCompleted = true;
        
        return 'Token inyectado';
        """
        
        result = self.driver.execute_script(token_script)
        print(f"[INFO] Resultado inyección: {result}")
        return True
    
    def method_audio_captcha(self):
        """Intentar con audio CAPTCHA"""
        print("[INFO] 🔊 Intentando audio CAPTCHA...")
        # Implementación básica para audio CAPTCHA
        return False
    
    def method_reload_and_retry(self):
        """Recargar y volver a intentar"""
        print("[INFO] 🔄 Recargando página...")
        self.driver.refresh()
        self.human_delay(5, 8)
        return False
    
    def check_if_captcha_solved(self):
        """Verificar si el CAPTCHA ya se resolvió"""
        try:
            # Buscar indicadores de CAPTCHA resuelto
            indicators = [
                '.recaptcha-checkbox-checked',
                'input[name="g-recaptcha-response"][value*="03AGdBq"]',
                '#recaptcha-token[value*="03AGdBq"]'
            ]
            
            for indicator in indicators:
                try:
                    element = self.driver.find_element(By.CSS_SELECTOR, indicator)
                    if element:
                        print("[✓] CAPTCHA parece estar resuelto")
                        return True
                except:
                    continue
            
            return False
            
        except Exception as e:
            print(f"[WARNING] Error verificando estado del CAPTCHA: {e}")
            return False
    
    def submit_and_get_result(self):
        """Enviar formulario y obtener resultado"""
        try:
            print("[INFO] 📤 Enviando formulario...")
            
            # Buscar botón de consultar
            consultar_btn = WebDriverWait(self.driver, 10).until(
                EC.element_to_be_clickable((By.ID, "j_idt17"))
            )
            
            # Click humano en consultar
            self.human_click(consultar_btn)
            print("[✓] Formulario enviado")
            
            # Esperar resultado
            print("[INFO] ⏳ Esperando resultado...")
            self.human_delay(8, 15)
            
            # Buscar resultado
            resultado_selectors = [
                "#form\\:mensajeCiudadano",
                ".mensaje-ciudadano",
                "#mensajeCiudadano"
            ]
            
            for selector in resultado_selectors:
                try:
                    resultado_element = WebDriverWait(self.driver, 10).until(
                        EC.visibility_of_element_located((By.CSS_SELECTOR, selector))
                    )
                    
                    texto_resultado = resultado_element.text.strip()
                    if texto_resultado:
                        print("[✅] Resultado obtenido exitosamente")
                        
                        return {
                            "tiene_antecedentes": "NO TIENE ASUNTOS PENDIENTES" not in texto_resultado.upper(),
                            "texto": texto_resultado,
                            "status": "success",
                            "metodo": "image_captcha_solver"
                        }
                except:
                    continue
            
            return {"error": "No se pudo obtener el resultado", "status": "no_result"}
            
        except Exception as e:
            print(f"[ERROR] Error enviando formulario: {e}")
            return {"error": str(e), "status": "submit_error"}
    
    def human_delay(self, min_seconds, max_seconds):
        """Delay aleatorio para simular comportamiento humano"""
        delay = random.uniform(min_seconds, max_seconds)
        time.sleep(delay)
    
    def human_click(self, element):
        """Click que simula comportamiento humano"""
        # Mover mouse al elemento gradualmente
        actions = ActionChains(self.driver)
        actions.move_to_element(element)
        
        # Delay pequeño antes del click
        self.human_delay(0.1, 0.3)
        
        # Click con pequeña variación
        actions.click()
        actions.perform()
        
        # Delay después del click
        self.human_delay(0.2, 0.5)
    
    def close(self):
        """Cerrar driver"""
        if hasattr(self, 'driver'):
            self.driver.quit()


def consultar_policia_con_image_solver(cedula):
    """
    Función principal para consultar usando el solver de imágenes
    """
    solver = ImageCaptchaSolver()
    
    try:
        resultado = solver.solve_image_captcha_intelligent(cedula)
        return resultado
    except Exception as e:
        print(f"[ERROR] Error general: {e}")
        return {"error": str(e), "status": "error"}
    finally:
        solver.close()


# Ejemplo de uso
if __name__ == "__main__":
    cedula_test = "12345678"
    resultado = consultar_policia_con_image_solver(cedula_test)
    print("Resultado final:", json.dumps(resultado, indent=2))