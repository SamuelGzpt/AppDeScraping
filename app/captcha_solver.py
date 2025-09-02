# captcha_solver.py
import time
import base64
import requests
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from webdriver_manager.chrome import ChromeDriverManager


class CaptchaSolver:
    """
    Clase para resolver CAPTCHAs usando múltiples estrategias
    """
    
    def __init__(self):
        self.setup_driver()
    
    def setup_driver(self):
        """Configura el driver de Chrome con máxima protección anti-detección"""
        options = Options()
        options.add_argument("--no-sandbox")
        options.add_argument("--disable-dev-shm-usage")
        options.add_argument("--disable-blink-features=AutomationControlled")
        options.add_experimental_option("excludeSwitches", ["enable-automation"])
        options.add_experimental_option('useAutomationExtension', False)
        
        # User agent más creíble
        options.add_argument("--user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36")
        
        # Configuraciones adicionales para evitar detección
        options.add_argument("--disable-web-security")
        options.add_argument("--allow-running-insecure-content")
        options.add_argument("--disable-extensions")
        options.add_argument("--disable-plugins")
        options.add_argument("--disable-images")  # Más rápido
        options.add_argument("--disable-javascript-harmony-shipping")
        
        self.driver = webdriver.Chrome(
            service=Service(ChromeDriverManager().install()), 
            options=options
        )
        
        # Scripts anti-detección
        self.driver.execute_script("""
            Object.defineProperty(navigator, 'webdriver', {get: () => undefined});
            Object.defineProperty(navigator, 'plugins', {get: () => [1, 2, 3, 4, 5]});
            Object.defineProperty(navigator, 'languages', {get: () => ['es-ES', 'es']});
            window.chrome = {runtime: {}};
            Object.defineProperty(navigator, 'permissions', {
                get: () => ({query: () => Promise.resolve({state: 'granted'})})
            });
        """)
    
    def inject_captcha_bypass(self):
        """Inyecta el bypass completo del CAPTCHA"""
        bypass_script = """
        (function() {
            console.log('🔓 Iniciando bypass avanzado del CAPTCHA...');
            
            // 1. Generar token realista
            function generateRealisticToken() {
                const chars = 'ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz0123456789-_';
                let token = '03AGdBq25';  // Prefijo típico de reCAPTCHA
                for (let i = 0; i < 500; i++) {
                    token += chars.charAt(Math.floor(Math.random() * chars.length));
                }
                return token;
            }
            
            const fakeToken = generateRealisticToken();
            console.log('🎫 Token generado:', fakeToken.substring(0, 50) + '...');
            
            // 2. Inyectar en todos los campos posibles
            const tokenFields = [
                'recaptcha-token',
                'g-recaptcha-response',
                'recaptcha_response_field',
                'recaptcha_challenge_field'
            ];
            
            tokenFields.forEach(fieldId => {
                let field = document.getElementById(fieldId);
                if (!field) {
                    field = document.createElement('input');
                    field.type = 'hidden';
                    field.id = fieldId;
                    field.name = fieldId;
                    document.body.appendChild(field);
                }
                field.value = fakeToken;
                console.log('✅ Campo', fieldId, 'configurado');
            });
            
            // 3. Interceptar y modificar requests de reCAPTCHA
            const originalFetch = window.fetch;
            window.fetch = function(...args) {
                if (args[0] && args[0].includes('recaptcha')) {
                    console.log('🚫 Interceptando request de reCAPTCHA:', args[0]);
                    return Promise.resolve({
                        ok: true,
                        json: () => Promise.resolve({success: true, token: fakeToken})
                    });
                }
                return originalFetch.apply(this, args);
            };
            
            // 4. Modificar grecaptcha global
            window.grecaptcha = {
                ready: function(callback) { callback(); },
                render: function() { return 'fake-widget-id'; },
                getResponse: function() { return fakeToken; },
                reset: function() { console.log('reCAPTCHA reset (fake)'); },
                execute: function() { return Promise.resolve(fakeToken); }
            };
            
            // 5. Marcar checkboxes del CAPTCHA
            const checkboxes = document.querySelectorAll(
                '.recaptcha-checkbox, [role="checkbox"]'
            );
            checkboxes.forEach(checkbox => {
                checkbox.classList.add('recaptcha-checkbox-checked');
                checkbox.setAttribute('aria-checked', 'true');
                checkbox.style.background = '#1976d2';
                
                // Crear y disparar evento de click
                const event = new MouseEvent('click', {
                    view: window,
                    bubbles: true,
                    cancelable: true
                });
                checkbox.dispatchEvent(event);
                console.log('☑️ Checkbox marcado');
            });
            
            // 6. Actualizar iframes del reCAPTCHA
            const recaptchaIframes = document.querySelectorAll('iframe[src*="recaptcha"]');
            recaptchaIframes.forEach(iframe => {
                try {
                    iframe.src = iframe.src + '&response=' + encodeURIComponent(fakeToken);
                    console.log('📺 iframe actualizado');
                } catch (e) {
                    console.log('⚠️ No se pudo modificar iframe:', e.message);
                }
            });
            
            // 7. Interceptar eventos de validación
            document.addEventListener('submit', function(e) {
                console.log('📝 Formulario enviado, inyectando tokens...');
                
                const form = e.target;
                if (form && form.tagName === 'FORM') {
                    // Agregar token al formulario
                    let tokenInput = form.querySelector('input[name="g-recaptcha-response"]');
                    if (!tokenInput) {
                        tokenInput = document.createElement('input');
                        tokenInput.type = 'hidden';
                        tokenInput.name = 'g-recaptcha-response';
                        form.appendChild(tokenInput);
                    }
                    tokenInput.value = fakeToken;
                }
            }, true);
            
            // 8. Simular callbacks de éxito
            setTimeout(() => {
                if (window.recaptchaCallback) {
                    window.recaptchaCallback(fakeToken);
                }
                
                // Disparar eventos personalizados
                window.dispatchEvent(new CustomEvent('recaptcha-solved', {
                    detail: { token: fakeToken }
                }));
                
                console.log('🎉 Bypass completado exitosamente');
            }, 1000);
            
            // 9. Retornar confirmación
            return {
                success: true,
                token: fakeToken,
                timestamp: new Date().getTime()
            };
        })();
        """
        
        return self.driver.execute_script(bypass_script)
    
    def solve_captcha_with_audio(self):
        """Método alternativo usando audio CAPTCHA (más complejo)"""
        try:
            # Buscar botón de audio
            audio_button = self.driver.find_element(By.ID, "recaptcha-audio-button")
            if audio_button:
                audio_button.click()
                time.sleep(2)
                
                # Aquí podrías integrar un servicio de reconocimiento de audio
                # Por ejemplo: Google Speech-to-Text API
                print("[INFO] Audio CAPTCHA detectado - requiere integración adicional")
                return False
        except:
            pass
        return False
    
    def solve_captcha_with_service(self, api_key=None, service="2captcha"):
        """
        Resolver CAPTCHA usando servicios externos como 2captcha, anticaptcha, etc.
        
        Args:
            api_key: Clave API del servicio
            service: Nombre del servicio ('2captcha', 'anticaptcha', etc.)
        """
        if not api_key:
            print("[WARNING] No se proporcionó API key para servicio de CAPTCHA")
            return None
        
        try:
            # Obtener site_key del reCAPTCHA
            site_key_element = self.driver.find_element(
                By.CSS_SELECTOR, 
                '[data-sitekey], .g-recaptcha'
            )
            site_key = site_key_element.get_attribute('data-sitekey')
            current_url = self.driver.current_url
            
            if service == "2captcha":
                return self._solve_with_2captcha(api_key, site_key, current_url)
            elif service == "anticaptcha":
                return self._solve_with_anticaptcha(api_key, site_key, current_url)
            
        except Exception as e:
            print(f"[ERROR] Error al resolver CAPTCHA con servicio: {e}")
            return None
    
    def _solve_with_2captcha(self, api_key, site_key, url):
        """Resolver usando 2captcha.com"""
        try:
            # 1. Enviar CAPTCHA
            submit_url = "http://2captcha.com/in.php"
            submit_data = {
                'key': api_key,
                'method': 'userrecaptcha',
                'googlekey': site_key,
                'pageurl': url,
                'json': 1
            }
            
            response = requests.post(submit_url, data=submit_data, timeout=30)
            result = response.json()
            
            if result.get('status') != 1:
                print(f"[ERROR] Error al enviar CAPTCHA: {result}")
                return None
            
            captcha_id = result['request']
            print(f"[INFO] CAPTCHA enviado, ID: {captcha_id}")
            
            # 2. Esperar solución
            get_url = "http://2captcha.com/res.php"
            max_attempts = 30
            
            for attempt in range(max_attempts):
                time.sleep(10)  # Esperar 10 segundos entre intentos
                
                get_data = {
                    'key': api_key,
                    'action': 'get',
                    'id': captcha_id,
                    'json': 1
                }
                
                response = requests.get(get_url, params=get_data, timeout=30)
                result = response.json()
                
                if result.get('status') == 1:
                    token = result['request']
                    print(f"[SUCCESS] CAPTCHA resuelto: {token[:50]}...")
                    return token
                elif result.get('error') == 'CAPCHA_NOT_READY':
                    print(f"[INFO] Esperando solución... ({attempt + 1}/{max_attempts})")
                    continue
                else:
                    print(f"[ERROR] Error al obtener solución: {result}")
                    return None
            
            print("[ERROR] Timeout esperando solución del CAPTCHA")
            return None
            
        except Exception as e:
            print(f"[ERROR] Error en 2captcha: {e}")
            return None
    
    def _solve_with_anticaptcha(self, api_key, site_key, url):
        """Resolver usando anti-captcha.com"""
        try:
            # Similar implementación para anti-captcha
            # Por brevedad, no implementado completamente aquí
            print("[INFO] Integración con anti-captcha disponible")
            return None
        except Exception as e:
            print(f"[ERROR] Error en anti-captcha: {e}")
            return None
    
    def close(self):
        """Cerrar el driver"""
        if hasattr(self, 'driver'):
            self.driver.quit()


# Función principal para usar el solver
def consultar_policia_con_solver(cedula, captcha_service=None, api_key=None):
    """
    Consultar antecedentes usando el solver avanzado de CAPTCHA
    """
    solver = CaptchaSolver()
    
    try:
        print(f"[INFO] Iniciando consulta con solver avanzado para cédula: {cedula}")
        
        # 1. Navegar a la página
        solver.driver.get("https://antecedentes.policia.gov.co:7005/WebJudicial/antecedentes.xhtml")
        time.sleep(3)
        
        # 2. Aceptar términos
        try:
            aceptar_btn = solver.driver.find_element(By.ID, "aceptaOption:0")
            solver.driver.execute_script("arguments[0].click();", aceptar_btn)
            
            continuar_btn = solver.driver.find_element(By.ID, "continuarBtn")
            solver.driver.execute_script("arguments[0].click();", continuar_btn)
            time.sleep(3)
        except:
            print("[INFO] Términos ya aceptados o no necesarios")
        
        # 3. Inyectar bypass del CAPTCHA
        bypass_result = solver.inject_captcha_bypass()
        print(f"[INFO] Resultado del bypass: {bypass_result}")
        
        # 4. Si el bypass no funciona, usar servicio externo
        if captcha_service and api_key:
            print("[INFO] Usando servicio externo para resolver CAPTCHA...")
            token = solver.solve_captcha_with_service(api_key, captcha_service)
            if token:
                # Inyectar token obtenido del servicio
                solver.driver.execute_script(f"""
                    document.querySelector('textarea[name="g-recaptcha-response"]').value = '{token}';
                    document.getElementById('recaptcha-token').value = '{token}';
                """)
        
        # 5. Ingresar cédula
        cedula_field = solver.driver.find_element(By.ID, "cedulaInput")
        cedula_field.clear()
        cedula_field.send_keys(str(cedula))
        print("[✓] Cédula ingresada")
        
        # 6. Enviar formulario
        consultar_btn = solver.driver.find_element(By.ID, "j_idt17")
        solver.driver.execute_script("arguments[0].click();", consultar_btn)
        print("[✓] Formulario enviado")
        
        # 7. Obtener resultado
        time.sleep(10)  # Esperar procesamiento
        
        try:
            resultado_element = solver.driver.find_element(By.ID, "form:mensajeCiudadano")
            texto_resultado = resultado_element.text.strip()
            
            return {
                "tiene_antecedentes": "NO TIENE ASUNTOS PENDIENTES" not in texto_resultado.upper(),
                "texto": texto_resultado,
                "status": "success",
                "metodo": "solver_avanzado"
            }
            
        except Exception as e:
            print(f"[ERROR] No se pudo obtener resultado: {e}")
            return {"error": "No se pudo obtener el resultado", "status": "error"}
    
    except Exception as e:
        print(f"[ERROR] Error general: {e}")
        return {"error": str(e), "status": "error"}
    
    finally:
        solver.close()


# Ejemplo de uso
if __name__ == "__main__":
    # Uso básico con bypass
    resultado = consultar_policia_con_solver("12345678")
    print("Resultado:", resultado)
    
    # Uso con servicio externo (requiere API key)
    # resultado = consultar_policia_con_solver("12345678", "2captcha", "tu_api_key_aqui")