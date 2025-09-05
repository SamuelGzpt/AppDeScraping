import undetected_chromedriver as uc
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.chrome.options import Options as ChromeOptions
from selenium.common.exceptions import TimeoutException, NoSuchElementException
import speech_recognition as sr
from pydub import AudioSegment
import urllib.request
import time
import os
import traceback
from datetime import datetime
import warnings
import random
import ssl

warnings.filterwarnings("ignore")


def delay_random(min_sec=1, max_sec=3):
    """Pausa aleatoria para simular comportamiento humano"""
    time.sleep(random.uniform(min_sec, max_sec))


def type_human_like(element, text):
    """Escritura simulando velocidad humana"""
    element.clear()
    for char in text:
        element.send_keys(char)
        time.sleep(random.uniform(0.05, 0.15))


def recognize_audio_captcha(audio_path):
    """Reconoce audio CAPTCHA con múltiples estrategias"""
    if not os.path.exists(audio_path):
        return None
    
    strategies = [
        {"energy": 300, "pause": 0.8, "phrase": 0.3, "ambient": 0.5, "langs": ['en-US']},
        {"energy": 50, "pause": 0.1, "phrase": 0.01, "ambient": 2.0, "langs": ['en-US', 'es-ES']},
        {"energy": 20, "pause": 0.02, "phrase": 0.001, "ambient": 4.0, "langs": ['en-US'], "process": True}
    ]
    
    for strategy in strategies:
        try:
            r = sr.Recognizer()
            r.energy_threshold = strategy['energy']
            r.pause_threshold = strategy['pause']
            r.phrase_threshold = strategy['phrase']
            r.dynamic_energy_threshold = True
            
            audio_file = audio_path
            if strategy.get('process'):
                try:
                    audio_seg = AudioSegment.from_wav(audio_path)
                    audio_seg = audio_seg.normalize().high_pass_filter(100) + 12
                    processed_path = audio_path.replace('.wav', '_proc.wav')
                    audio_seg.export(processed_path, format="wav")
                    audio_file = processed_path
                except:
                    continue
            
            for lang in strategy['langs']:
                try:
                    with sr.AudioFile(audio_file) as source:
                        r.adjust_for_ambient_noise(source, duration=strategy['ambient'])
                        audio_data = r.listen(source, timeout=15)
                        text = r.recognize_google(audio_data, language=lang)
                    
                    if text and text.strip():
                        clean_text = ''.join(c for c in text.lower() if c.isalnum())
                        if len(clean_text) >= 2:
                            if audio_file != audio_path and os.path.exists(audio_file):
                                os.remove(audio_file)
                            return clean_text
                except:
                    continue
            
            if audio_file != audio_path and os.path.exists(audio_file):
                try:
                    os.remove(audio_file)
                except:
                    pass
                    
        except:
            continue
    
    return None


def download_audio(url):
    """Descarga audio del CAPTCHA"""
    ssl_context = ssl.create_default_context()
    ssl_context.check_hostname = False
    ssl_context.verify_mode = ssl.CERT_NONE
    
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36'
    }
    
    try:
        req = urllib.request.Request(url, headers=headers)
        with urllib.request.urlopen(req, timeout=30, context=ssl_context) as response:
            if response.status == 200:
                audio_data = response.read()
                if len(audio_data) > 1024:
                    with open("temp_audio.mp3", "wb") as f:
                        f.write(audio_data)
                    return True
    except:
        pass
    
    return False


def convert_audio():
    """Convierte MP3 a WAV"""
    try:
        audio_seg = AudioSegment.from_file("temp_audio.mp3")
        audio_seg.export("temp_audio.wav", format="wav")
        return True
    except:
        return False


def get_audio_url(driver):
    """Obtiene URL del audio CAPTCHA con múltiples estrategias"""
    strategies = [
        # Estrategia 1: Selectores estándar
        ".rc-audiochallenge-tdownload-link",
        ".rc-audiochallenge-tdownload a",
        "a[href*='audio']",
        "a[href*='mp3']",
        "a[href*='wav']",
        
        # Estrategia 2: Audio element
        "audio[src]",
        
        # Estrategia 3: Download links
        "a[download]",
        "a[href*='recaptcha']"
    ]
    
    for selector in strategies:
        try:
            if selector == "audio[src]":
                js = f"var element = document.querySelector('{selector}'); return element ? element.src : null;"
            else:
                js = f"var element = document.querySelector('{selector}'); return element ? element.href : null;"
                
            audio_url = driver.execute_script(js)
            if audio_url and 'http' in audio_url and ('audio' in audio_url or 'mp3' in audio_url or 'wav' in audio_url or 'recaptcha' in audio_url):
                return audio_url
        except:
            continue
    
    # Búsqueda exhaustiva en HTML
    try:
        js = """
        var html = document.documentElement.innerHTML;
        var patterns = [
            /https?:\/\/[^"'\s]+\.mp3[^"'\s]*/gi,
            /https?:\/\/[^"'\s]+\.wav[^"'\s]*/gi,
            /https?:\/\/[^"'\s]+audio[^"'\s]*/gi,
            /https?:\/\/[^"'\s]*recaptcha[^"'\s]*audio[^"'\s]*/gi
        ];
        
        for (var i = 0; i < patterns.length; i++) {
            var matches = html.match(patterns[i]);
            if (matches && matches.length > 0) {
                return matches[0].replace(/['"]/g, '');
            }
        }
        return null;
        """
        
        result = driver.execute_script(js)
        if result:
            return result
            
    except:
        pass
    
    return None


def create_driver():
    """Crea driver con configuración optimizada"""
    try:
        options = uc.ChromeOptions()
        
        basic_args = [
            '--no-sandbox',
            '--disable-dev-shm-usage',
            '--disable-logging',
            '--disable-gpu',
            '--disable-web-security',
            '--disable-blink-features=AutomationControlled',
            '--disable-extensions',
            '--disable-images',
            '--window-size=1920,1080'
        ]
        
        for arg in basic_args:
            options.add_argument(arg)
        
        options.add_experimental_option("excludeSwitches", ["enable-automation"])
        options.add_experimental_option('useAutomationExtension', False)
        
        prefs = {
            "profile.default_content_setting_values": {"notifications": 2, "geolocation": 2}
        }
        options.add_experimental_option("prefs", prefs)
        
        driver = uc.Chrome(options=options, headless=False)
        driver.implicitly_wait(10)
        driver.set_page_load_timeout(30)
        
        # Scripts anti-detección básicos
        driver.execute_script("Object.defineProperty(navigator, 'webdriver', {get: () => undefined})")
        
        return driver
        
    except Exception as e:
        # Fallback a Selenium estándar
        try:
            options = ChromeOptions()
            for arg in basic_args:
                options.add_argument(arg)
            
            driver = webdriver.Chrome(options=options)
            driver.implicitly_wait(10)
            return driver
        except:
            return None


def consultar_policia(cedula):
    """Consulta antecedentes policiales - versión simplificada"""
    
    driver = None
    
    try:
        driver = create_driver()
        if not driver:
            return {"status": "error", "error": "No se pudo inicializar driver", "metodo": "driver_init_error"}
        
        # Acceder al sitio
        driver.get("https://antecedentes.policia.gov.co:7005/WebJudicial/")
        time.sleep(3)
        
        # Navegar al formulario si es necesario
        current_url = driver.current_url
        if "antecedentes.xhtml" not in current_url:
            try:
                driver.get("https://antecedentes.policia.gov.co:7005/WebJudicial/antecedentes.xhtml")
                time.sleep(3)
            except:
                pass
        
        # Aceptar términos con detección robusta
        max_attempts = 5
        form_found = False
        
        for attempt in range(max_attempts):
            try:
                # Verificar si ya estamos en el formulario
                cedula_fields = driver.find_elements(By.ID, "cedulaInput")
                if cedula_fields and cedula_fields[0].is_displayed():
                    form_found = True
                    break
                
                # Verificar si existe página de términos
                radio_elements = driver.find_elements(By.ID, "aceptaOption:0")
                if not radio_elements:
                    # No hay términos, verificar si hay otro indicador
                    delay_random(2, 3)
                    continue
                
                # Marcar radio button si existe y no está marcado
                radio_js = """
                var radio = document.getElementById('aceptaOption:0');
                if (radio && !radio.checked) {
                    radio.checked = true;
                    radio.dispatchEvent(new Event('change'));
                    radio.dispatchEvent(new Event('click'));
                    return 'marked';
                } else if (radio && radio.checked) {
                    return 'already_marked';
                }
                return 'not_found';
                """
                
                radio_result = driver.execute_script(radio_js)
                
                if radio_result in ['marked', 'already_marked']:
                    delay_random(1, 2)
                    
                    # Verificar si botón continuar está habilitado
                    btn_check_js = """
                    var btn = document.getElementById('continuarBtn');
                    if (btn) {
                        return {
                            exists: true,
                            enabled: !btn.disabled,
                            visible: btn.offsetParent !== null
                        };
                    }
                    return {exists: false};
                    """
                    
                    btn_status = driver.execute_script(btn_check_js)
                    
                    if btn_status.get('exists'):
                        if not btn_status.get('enabled'):
                            # Intentar habilitar botón
                            enable_js = """
                            var btn = document.getElementById('continuarBtn');
                            if (btn) {
                                btn.disabled = false;
                                btn.removeAttribute('disabled');
                                btn.classList.remove('ui-state-disabled');
                            }
                            """
                            driver.execute_script(enable_js)
                            delay_random(0.5, 1)
                        
                        # Hacer clic en continuar
                        continue_js = """
                        var btn = document.getElementById('continuarBtn');
                        if (btn) {
                            btn.click();
                            return true;
                        }
                        return false;
                        """
                        
                        click_result = driver.execute_script(continue_js)
                        
                        if click_result:
                            # Esperar y verificar transición múltiples veces
                            for check in range(8):
                                delay_random(1, 2)
                                
                                # Verificar múltiples indicadores de formulario
                                form_indicators = [
                                    driver.find_elements(By.ID, "cedulaInput"),
                                    driver.find_elements(By.ID, "captchaAntecedentes"),
                                    driver.find_elements(By.XPATH, "//input[@placeholder*='cedula' or @placeholder*='Cedula']"),
                                    driver.find_elements(By.XPATH, "//label[contains(text(), 'Cedula') or contains(text(), 'cédula')]")
                                ]
                                
                                form_detected = any(
                                    indicator and indicator[0].is_displayed() 
                                    for indicator in form_indicators 
                                    if indicator
                                )
                                
                                if form_detected:
                                    form_found = True
                                    break
                                
                                # Verificar si seguimos en términos
                                still_terms = driver.find_elements(By.ID, "aceptaOption:0")
                                if still_terms and still_terms[0].is_displayed():
                                    break  # Salir del check loop, reintentar
                            
                            if form_found:
                                break
                        else:
                            # Si no se pudo hacer clic, reintentar
                            delay_random(1, 2)
                    else:
                        # Botón no encontrado, puede que ya hayamos pasado
                        delay_random(2, 3)
                else:
                    # Radio no encontrado o error
                    delay_random(1, 2)
                
            except Exception as e:
                if attempt < max_attempts - 1:
                    delay_random(2, 4)
                    continue
                else:
                    return {"status": "error", "error": f"Error aceptando términos tras {max_attempts} intentos", "metodo": "terminos_error"}
        
        if not form_found:
            return {"status": "error", "error": "No se detectó transición al formulario", "metodo": "form_transition_failed"}
        
        # Ingresar cédula
        try:
            WebDriverWait(driver, 15).until(
                EC.presence_of_element_located((By.ID, "cedulaInput"))
            )
            
            delay_random(1, 2)
            
            cedula_js = f"""
            var input = document.getElementById('cedulaInput');
            if (input) {{
                input.value = '{cedula}';
                input.dispatchEvent(new Event('input', {{bubbles: true}}));
                input.dispatchEvent(new Event('change', {{bubbles: true}}));
            }}
            """
            driver.execute_script(cedula_js)
            
            delay_random(2, 3)
            
        except Exception as e:
            return {"status": "error", "error": "Error ingresando cédula", "metodo": "input_error"}
        
        # Manejar CAPTCHA
        try:
            # Buscar iframe de CAPTCHA
            captcha_iframe = WebDriverWait(driver, 10).until(
                EC.presence_of_element_located((By.XPATH, '//*[@id="captchaAntecedentes"]//iframe'))
            )
            
            driver.switch_to.frame(captcha_iframe)
            time.sleep(2)
            
            # Marcar checkbox
            checkbox_js = """
            var checkbox = document.getElementById('recaptcha-anchor');
            if (checkbox) {
                checkbox.click();
                return true;
            }
            return false;
            """
            checkbox_clicked = driver.execute_script(checkbox_js)
            
            if not checkbox_clicked:
                driver.switch_to.default_content()
                return {"status": "error", "error": "No se pudo marcar checkbox CAPTCHA", "metodo": "captcha_checkbox_error"}
            
            time.sleep(4)
            driver.switch_to.default_content()
            
            # Verificar si aparece challenge (desafío)
            challenge_detected = False
            try:
                challenge_iframe = WebDriverWait(driver, 3).until(
                    EC.presence_of_element_located((By.XPATH, "//iframe[contains(@title, 'challenge') or contains(@src, 'bframe')]"))
                )
                challenge_detected = True
            except TimeoutException:
                # No hay challenge, CAPTCHA resuelto automáticamente
                challenge_detected = False
            
            # Solo procesar audio si hay challenge
            if challenge_detected:
                try:
                    driver.switch_to.frame(challenge_iframe)
                    time.sleep(2)
                    
                    # Verificar si hay botón de audio disponible
                    audio_available_js = """
                    var audioBtn = document.getElementById('recaptcha-audio-button');
                    return audioBtn && audioBtn.offsetParent !== null;
                    """
                    
                    if driver.execute_script(audio_available_js):
                        # Activar audio
                        audio_js = """
                        var audioBtn = document.getElementById('recaptcha-audio-button');
                        if (audioBtn) {
                            audioBtn.click();
                            return true;
                        }
                        return false;
                        """
                        
                        if driver.execute_script(audio_js):
                            time.sleep(3)
                            
                            # Obtener y procesar audio
                            audio_url = get_audio_url(driver)
                            if audio_url:
                                if download_audio(audio_url) and convert_audio():
                                    text = recognize_audio_captcha("temp_audio.wav")
                                    
                                    if text:
                                        # Ingresar respuesta
                                        response_js = f"""
                                        var input = document.getElementById('audio-response');
                                        if (input) {{
                                            input.value = '{text}';
                                            input.dispatchEvent(new Event('input', {{bubbles: true}}));
                                            return true;
                                        }}
                                        return false;
                                        """
                                        
                                        if driver.execute_script(response_js):
                                            time.sleep(2)
                                            
                                            # Verificar respuesta
                                            verify_js = """
                                            var btn = document.getElementById('recaptcha-verify-button');
                                            if (btn) {
                                                btn.click();
                                                return true;
                                            }
                                            return false;
                                            """
                                            driver.execute_script(verify_js)
                                            time.sleep(3)
                    
                    driver.switch_to.default_content()
                    
                except Exception as challenge_error:
                    driver.switch_to.default_content()
                    # Continuar aunque falle el challenge
                    pass
            
            # Limpiar archivos temporales
            for file in ["temp_audio.mp3", "temp_audio.wav"]:
                try:
                    if os.path.exists(file):
                        os.remove(file)
                except:
                    pass
            
        except Exception as e:
            try:
                driver.switch_to.default_content()
                # Limpiar archivos en caso de error
                for file in ["temp_audio.mp3", "temp_audio.wav"]:
                    try:
                        if os.path.exists(file):
                            os.remove(file)
                    except:
                        pass
            except:
                pass
            return {"status": "error", "error": "Error procesando CAPTCHA", "metodo": "captcha_error"}
        
        # Limpiar archivos temporales
        for file in ["temp_audio.mp3", "temp_audio.wav"]:
            try:
                if os.path.exists(file):
                    os.remove(file)
            except:
                pass
        
        # Hacer clic en consultar
        time.sleep(3)
        
        try:
            consultar_js = """
            var btn = document.getElementById('j_idt17');
            if (btn) {
                btn.click();
                return true;
            }
            return false;
            """
            
            if driver.execute_script(consultar_js):
                time.sleep(8)
            else:
                return {"status": "error", "error": "No se pudo hacer clic en consultar", "metodo": "consultar_error"}
        
        except Exception as e:
            return {"status": "error", "error": "Error haciendo clic en consultar", "metodo": "consultar_error"}
        
        # Obtener resultado
        try:
            resultado_text = ""
            
            selectors = [
                (By.ID, "form:mensajeCiudadano"),
                (By.CLASS_NAME, "mensajeCiudadano"),
                (By.XPATH, "//div[contains(@class, 'mensaje')]"),
                (By.XPATH, "//div[contains(text(), 'antecedentes') or contains(text(), 'registra')]")
            ]
            
            for selector_type, selector_value in selectors:
                try:
                    element = WebDriverWait(driver, 5).until(
                        EC.presence_of_element_located((selector_type, selector_value))
                    )
                    resultado_text = element.text.strip()
                    if resultado_text:
                        break
                except:
                    continue
            
            if not resultado_text:
                body_text = driver.find_element(By.TAG_NAME, "body").text
                lines = body_text.split('\n')
                for line in lines:
                    if any(word in line.upper() for word in ['ANTECEDENTES', 'REGISTRA', 'POLICIA']):
                        resultado_text = line.strip()
                        break
            
            if not resultado_text:
                return {"status": "error", "error": "No se pudo extraer resultado", "metodo": "no_result"}
            
            tiene_antecedentes = not any(phrase in resultado_text.upper() for phrase in [
                "NO REGISTRA ANTECEDENTES",
                "SIN ANTECEDENTES", 
                "NO TIENE ANTECEDENTES"
            ])
            
            return {
                "status": "success",
                "texto": resultado_text,
                "tiene_antecedentes": tiene_antecedentes,
                "metodo": "simplified_scraping",
                "timestamp": datetime.now().isoformat()
            }
            
        except Exception as e:
            return {"status": "error", "error": "Error extrayendo resultado", "metodo": "extraction_error"}
    
    except Exception as e:
        return {"status": "error", "error": f"Error: {str(e)}", "metodo": "general_error"}
    
    finally:
        if driver:
            try:
                driver.quit()
            except:
                pass


if __name__ == "__main__":
    resultado = consultar_policia("1234567890")
    print("=" * 50)
    print("RESULTADO:")
    print(f"Estado: {resultado.get('status')}")
    print(f"Texto: {resultado.get('texto', 'N/A')}")
    print(f"Tiene antecedentes: {resultado.get('tiene_antecedentes')}")
    print(f"Método: {resultado.get('metodo')}")
    print("=" * 50)