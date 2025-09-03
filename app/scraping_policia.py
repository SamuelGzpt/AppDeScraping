# scraping_policia.py - Versión Limpia con Solo Audio CAPTCHA Solver
import speech_recognition as sr
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException, WebDriverException
from webdriver_manager.chrome import ChromeDriverManager
import time
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


def consultar_policia(cedula):
    """
    Función principal que usa el solver de audio CAPTCHA
    """
    print(f"[INFO] Iniciando consulta con Audio CAPTCHA Solver para cédula: {cedula}")
    return consultar_policia_con_audio_solver(cedula)


def consultar_policia_con_audio_solver(cedula):
    """
    Consulta de antecedentes policiales con resolución automática de audio CAPTCHA
    """
    print(f"[INFO] Iniciando consulta con audio CAPTCHA para cédula: {cedula}")
    
    # Configurar Chrome con opciones optimizadas
    options = Options()
    options.add_argument("--no-sandbox")
    options.add_argument("--disable-dev-shm-usage")
    options.add_argument("--disable-blink-features=AutomationControlled")
    options.add_experimental_option("excludeSwitches", ["enable-automation"])
    options.add_experimental_option('useAutomationExtension', False)
    options.add_experimental_option('excludeSwitches', ['enable-logging'])
    options.add_argument("--disable-logging")
    options.add_argument("--log-level=3")
    options.add_argument("--user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36")
    
    # Modo headless para servidor (comentar para debugging)
    options.add_argument("--headless=new")
    
    browser = None
    temp_dir = tempfile.mkdtemp()
    recognizer = sr.Recognizer()
    
    try:
        # Inicializar navegador
        browser = webdriver.Chrome(
            service=Service(ChromeDriverManager().install()),
            options=options
        )
        
        # Scripts anti-detección
        browser.execute_script("""
            Object.defineProperty(navigator, 'webdriver', {
                get: () => undefined,
            });
            Object.defineProperty(navigator, 'plugins', {
                get: () => [1, 2, 3, 4, 5],
            });
            window.chrome = { runtime: {} };
        """)
        
        wait = WebDriverWait(browser, 30)
        
        print("[INFO] 🌐 Cargando página de antecedentes...")
        browser.get("https://antecedentes.policia.gov.co:7005/WebJudicial/antecedentes.xhtml")
        time.sleep(3)
        
        # Manejar términos y condiciones
        if _aceptar_terminos(browser, wait):
            print("[✓] ✅ Términos y condiciones aceptados")
        
        # Resolver CAPTCHA de audio
        if not _resolver_audio_captcha(browser, wait, temp_dir, recognizer):
            return {"error": "No se pudo resolver el CAPTCHA de audio", "status": "error"}
        
        # Ingresar cédula y consultar
        if not _ingresar_cedula_y_consultar(browser, wait, cedula):
            return {"error": "No se pudo ingresar la cédula o consultar", "status": "error"}
        
        # Obtener resultado
        texto_resultado = _obtener_resultado(browser, wait)
        if not texto_resultado:
            return {"error": "No se pudo obtener el resultado", "status": "error"}
        
        # Procesar resultado final
        tiene_antecedentes = "NO TIENE ASUNTOS PENDIENTES CON LAS AUTORIDADES JUDICIALES" not in texto_resultado.upper()
        
        resultado_final = {
            "tiene_antecedentes": tiene_antecedentes,
            "texto": texto_resultado,
            "status": "success",
            "metodo": "audio_captcha_solver"
        }
        
        print(f"[✅] 🎉 Consulta completada exitosamente para cédula {cedula}")
        return resultado_final
        
    except Exception as e:
        print(f"[❌] Error general: {e}")
        print(f"[DEBUG] Stack trace: {traceback.format_exc()}")
        return {"error": f"Error al consultar Policía: {str(e)}", "status": "error"}
    
    finally:
        _limpiar_recursos(browser, temp_dir)


def _aceptar_terminos(browser, wait):
    """
    Acepta términos y condiciones si aparecen
    """
    try:
        print("[INFO] 📋 Verificando términos y condiciones...")
        
        aceptar_radio = wait.until(EC.element_to_be_clickable((By.ID, "aceptaOption:0")))
        browser.execute_script("arguments[0].click();", aceptar_radio)
        
        continuar_btn = wait.until(EC.element_to_be_clickable((By.ID, "continuarBtn")))
        browser.execute_script("arguments[0].click();", continuar_btn)
        
        time.sleep(3)
        return True
        
    except TimeoutException:
        print("[INFO] ℹ️ Ya estamos en el formulario principal")
        return True
    except Exception as e:
        print(f"[WARNING] ⚠️ Error manejando términos: {e}")
        return True


def _resolver_audio_captcha(browser, wait, temp_dir, recognizer):
    """
    Resuelve el CAPTCHA de audio automáticamente
    """
    try:
        print("[INFO] 🔍 Buscando reCAPTCHA...")
        
        # Encontrar iframe del reCAPTCHA
        recaptcha_iframe = _encontrar_recaptcha_iframe(browser)
        if not recaptcha_iframe:
            print("[ERROR] ❌ No se encontró iframe de reCAPTCHA")
            return False
        
        # Activar checkbox del reCAPTCHA
        if not _activar_recaptcha_checkbox(browser, wait, recaptcha_iframe):
            return False
        
        # Cambiar al iframe del challenge
        challenge_iframe = _encontrar_challenge_iframe(browser)
        if not challenge_iframe:
            print("[ERROR] ❌ No se encontró iframe del challenge")
            return False
        
        browser.switch_to.frame(challenge_iframe)
        print("[INFO] 🎯 Cambiado al iframe del challenge")
        
        # Activar desafío de audio
        if not _activar_desafio_audio(browser):
            return False
        
        # Descargar y procesar audio
        audio_text = _procesar_audio_captcha(browser, temp_dir, recognizer)
        if not audio_text:
            return False
        
        # Enviar respuesta
        if not _enviar_respuesta_audio(browser, audio_text):
            return False
        
        # Volver al contenido principal
        browser.switch_to.default_content()
        print("[✅] 🎊 CAPTCHA de audio resuelto exitosamente")
        return True
        
    except Exception as e:
        print(f"[ERROR] ❌ Error resolviendo CAPTCHA: {e}")
        browser.switch_to.default_content()
        return False


def _encontrar_recaptcha_iframe(browser):
    """
    Encuentra el iframe principal del reCAPTCHA
    """
    iframes = browser.find_elements(By.TAG_NAME, "iframe")
    
    for iframe in iframes:
        src = iframe.get_attribute("src") or ""
        name = iframe.get_attribute("name") or ""
        title = iframe.get_attribute("title") or ""
        
        if any(keyword in attr.lower() for attr in [src, name, title] 
               for keyword in ["recaptcha", "captcha"]):
            print(f"[✓] 🎯 reCAPTCHA iframe encontrado: {src[:50]}...")
            return iframe
    
    return None


def _activar_recaptcha_checkbox(browser, wait, recaptcha_iframe):
    """
    Hace clic en el checkbox del reCAPTCHA
    """
    try:
        browser.switch_to.frame(recaptcha_iframe)
        print("[INFO] 🖱️ Activando checkbox del reCAPTCHA...")
        
        checkbox = wait.until(EC.element_to_be_clickable((By.CSS_SELECTOR, ".recaptcha-checkbox")))
        browser.execute_script("arguments[0].click();", checkbox)
        print("[✓] ✅ Checkbox activado")
        
        time.sleep(5)  # Esperar a que aparezca el challenge
        browser.switch_to.default_content()
        return True
        
    except Exception as e:
        print(f"[ERROR] ❌ Error activando checkbox: {e}")
        browser.switch_to.default_content()
        return False


def _encontrar_challenge_iframe(browser):
    """
    Encuentra el iframe del challenge de reCAPTCHA
    """
    time.sleep(2)
    iframes = browser.find_elements(By.TAG_NAME, "iframe")
    
    for iframe in iframes:
        src = iframe.get_attribute("src") or ""
        if "bframe" in src or "challenge" in src.lower():
            print(f"[✓] 🎯 Challenge iframe encontrado")
            return iframe
    
    return None


def _activar_desafio_audio(browser):
    """
    Hace clic en el botón de audio del CAPTCHA
    """
    try:
        print("[INFO] 🔊 Activando desafío de audio...")
        
        audio_button = browser.find_element(By.CSS_SELECTOR, '#recaptcha-audio-button')
        audio_button.click()
        print("[✓] 🎵 Desafío de audio activado")
        
        time.sleep(2)
        return True
        
    except Exception as e:
        print(f"[ERROR] ❌ No se encontró el botón de audio: {e}")
        return False


def _procesar_audio_captcha(browser, temp_dir, recognizer):
    """
    Descarga, convierte y reconoce el audio del CAPTCHA
    """
    try:
        # Obtener enlace de descarga del audio
        audio_url = _obtener_enlace_audio(browser)
        if not audio_url:
            return None
        
        # Descargar audio
        audio_file = _descargar_audio(audio_url, temp_dir)
        if not audio_file:
            return None
        
        # Convertir a WAV para mejor reconocimiento
        wav_file = _convertir_a_wav(audio_file, temp_dir)
        if not wav_file:
            return None
        
        # Reconocer texto del audio
        texto = _reconocer_audio(wav_file, recognizer)
        return texto
        
    except Exception as e:
        print(f"[ERROR] ❌ Error procesando audio: {e}")
        return None


def _obtener_enlace_audio(browser):
    """
    Obtiene el enlace de descarga del archivo de audio
    """
    audio_selectors = [
        'body > div > div > div.rc-audiochallenge-tdownload > a',
        '.rc-audiochallenge-tdownload-link',
        'a[href*="payload"]',
        '.rc-audiochallenge-tdownload a'
    ]
    
    for selector in audio_selectors:
        try:
            element = browser.find_element(By.CSS_SELECTOR, selector)
            url = element.get_attribute("href")
            if url:
                print("[✓] 🔗 Enlace de audio obtenido")
                return url
        except:
            continue
    
    print("[ERROR] ❌ No se pudo obtener enlace de audio")
    return None


def _descargar_audio(url, temp_dir):
    """
    Descarga el archivo de audio
    """
    try:
        print("[INFO] ⬇️ Descargando archivo de audio...")
        audio_path = os.path.join(temp_dir, "audio.mp3")
        urllib.request.urlretrieve(url, audio_path)
        print("[✓] 💾 Audio descargado")
        return audio_path
    except Exception as e:
        print(f"[ERROR] ❌ Error descargando audio: {e}")
        return None


def _convertir_a_wav(audio_file, temp_dir):
    """
    Convierte el audio MP3 a WAV optimizado para reconocimiento
    """
    try:
        print("[INFO] 🔄 Convirtiendo audio a WAV...")
        wav_path = os.path.join(temp_dir, "audio.wav")
        
        # Cargar y optimizar audio
        audio_segment = AudioSegment.from_mp3(audio_file)
        audio_segment = audio_segment.set_frame_rate(16000)  # Frecuencia óptima
        audio_segment = audio_segment.set_channels(1)        # Mono
        audio_segment.export(wav_path, format="wav")
        
        print("[✓] 🎵 Audio convertido exitosamente")
        return wav_path
        
    except Exception as e:
        print(f"[ERROR] ❌ Error convirtiendo audio: {e}")
        return None


def _reconocer_audio(wav_file, recognizer):
    """
    Reconoce el texto del archivo de audio usando speech recognition
    """
    try:
        print("[INFO] 🎤 Reconociendo texto del audio...")
        
        with sr.AudioFile(wav_file) as source:
            # Ajustar para ruido ambiente
            recognizer.adjust_for_ambient_noise(source, duration=0.5)
            audio = recognizer.listen(source)
            
            # Intentar reconocimiento en múltiples idiomas
            idiomas = ['en-US', 'es-ES', 'en-GB']
            
            for idioma in idiomas:
                try:
                    text = recognizer.recognize_google(audio, language=idioma)
                    print(f"[✓] 🗣️ Texto reconocido ({idioma}): '{text}'")
                    return text
                except sr.UnknownValueError:
                    continue
                except Exception as e:
                    print(f"[WARNING] ⚠️ Error en reconocimiento {idioma}: {e}")
                    continue
            
            print("[ERROR] ❌ No se pudo reconocer el audio en ningún idioma")
            return None
            
    except Exception as e:
        print(f"[ERROR] ❌ Error en reconocimiento de audio: {e}")
        return None


def _enviar_respuesta_audio(browser, texto):
    """
    Ingresa la respuesta del audio y hace clic en verificar
    """
    try:
        print(f"[INFO] ⌨️ Enviando respuesta: '{texto}'")
        
        # Ingresar respuesta
        response_input = browser.find_element(By.CSS_SELECTOR, "#audio-response")
        response_input.clear()
        response_input.send_keys(texto.lower())
        
        # Hacer clic en verificar
        verify_button = browser.find_element(By.CSS_SELECTOR, "#recaptcha-verify-button")
        verify_button.click()
        
        print("[✓] ✅ Respuesta enviada")
        time.sleep(3)
        return True
        
    except Exception as e:
        print(f"[ERROR] ❌ Error enviando respuesta: {e}")
        return False


def _ingresar_cedula_y_consultar(browser, wait, cedula):
    """
    Ingresa la cédula y hace la consulta
    """
    try:
        print(f"[INFO] 🆔 Ingresando cédula: {cedula}")
        
        # Buscar campo de cédula
        cedula_selectors = [
            "#cedulaInput",
            "input[name*='cedula']",
            "input[id*='cedula']",
            "input[placeholder*='cédula']",
            "input[placeholder*='documento']",
            "input[type='text']"
        ]
        
        campo_cedula = None
        for selector in cedula_selectors:
            try:
                campo_cedula = wait.until(EC.element_to_be_clickable((By.CSS_SELECTOR, selector)))
                print(f"[✓] 📝 Campo encontrado: {selector}")
                break
            except:
                continue
        
        if not campo_cedula:
            print("[ERROR] ❌ Campo de cédula no encontrado")
            return False
        
        # Ingresar cédula
        campo_cedula.clear()
        campo_cedula.send_keys(str(cedula))
        print("[✓] ✅ Cédula ingresada")
        
        # Buscar y hacer clic en consultar
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
                print(f"[✓] 🔍 Botón encontrado: {selector}")
                break
            except:
                continue
        
        if not consultar_btn:
            print("[ERROR] ❌ Botón consultar no encontrado")
            return False
        
        # Hacer clic en consultar
        browser.execute_script("arguments[0].click();", consultar_btn)
        print("[✓] 🚀 Consulta enviada")
        return True
        
    except Exception as e:
        print(f"[ERROR] ❌ Error ingresando cédula: {e}")
        return False


def _obtener_resultado(browser, wait):
    """
    Obtiene el resultado de la consulta
    """
    try:
        print("[INFO] ⏳ Esperando resultado...")
        time.sleep(8)  # Tiempo para que procese la consulta
        
        # Selectores para encontrar el resultado
        resultado_selectors = [
            "#form\\:mensajeCiudadano",
            ".mensaje-ciudadano",
            "#mensajeCiudadano",
            "div[id*='mensaje']",
            ".resultado-consulta",
            "div[class*='mensaje']"
        ]
        
        # Buscar resultado en elementos específicos
        for selector in resultado_selectors:
            try:
                resultado_el = wait.until(EC.visibility_of_element_located((By.CSS_SELECTOR, selector)))
                texto = resultado_el.text.strip()
                if texto and len(texto) > 10:
                    print(f"[✓] 📄 Resultado obtenido con: {selector}")
                    return texto
            except:
                continue
        
        # Buscar en toda la página como fallback
        page_text = browser.page_source.lower()
        if "no tiene asuntos pendientes" in page_text:
            texto = "NO TIENE ASUNTOS PENDIENTES CON LAS AUTORIDADES JUDICIALES"
            print("[✓] 📄 Resultado encontrado en página completa")
            return texto
        elif "error" in page_text or "captcha" in page_text:
            print("[ERROR] ❌ Error en validación detectado")
            return None
        
        print("[ERROR] ❌ No se pudo obtener el resultado")
        return None
        
    except Exception as e:
        print(f"[ERROR] ❌ Error obteniendo resultado: {e}")
        return None


def _limpiar_recursos(browser, temp_dir):
    """
    Limpia archivos temporales y cierra el navegador
    """
    try:
        # Limpiar archivos temporales
        archivos_temp = ["audio.wav", "audio.mp3"]
        for archivo in archivos_temp:
            ruta = os.path.join(temp_dir, archivo)
            if os.path.exists(ruta):
                os.remove(ruta)
        
        if os.path.exists(temp_dir):
            os.rmdir(temp_dir)
        
        print("[INFO] 🧹 Archivos temporales limpiados")
        
    except Exception as e:
        print(f"[WARNING] ⚠️ Error limpiando archivos temporales: {e}")
    
    # Cerrar navegador
    if browser:
        try:
            browser.quit()
            print("[INFO] 🔒 Navegador cerrado")
        except:
            pass


# Funciones de compatibilidad con app.py
def consultar_policia_con_audio_captcha(cedula):
    """Alias para compatibilidad"""
    return consultar_policia_con_audio_solver(cedula)


def consultar_policia_bypass_captcha(cedula):
    """Redirige al método principal"""
    return consultar_policia_con_audio_solver(cedula)


def consultar_policia_bypass_avanzado(cedula):
    """Redirige al método principal"""
    return consultar_policia_con_audio_solver(cedula)


def consultar_policia_request_directo(cedula):
    """Redirige al método principal"""
    return consultar_policia_con_audio_solver(cedula)


def consultar_policia_token_especifico(cedula, token):
    """Redirige al método principal"""
    return consultar_policia_con_audio_solver(cedula)


if __name__ == "__main__":
    # Código de prueba
    cedula_test = "12345678"
    print(f"🧪 Probando consulta para cédula: {cedula_test}")
    
    resultado = consultar_policia(cedula_test)
    print(f"📋 Resultado final: {resultado}")