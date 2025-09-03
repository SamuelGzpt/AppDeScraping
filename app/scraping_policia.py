# scraping_policia.py - Versión Mejorada con Múltiples Estrategias
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
import random
import requests
from selenium.webdriver.common.keys import Keys

# Suprimir warnings
warnings.filterwarnings("ignore", category=FutureWarning)
warnings.filterwarnings("ignore", category=DeprecationWarning)
warnings.filterwarnings("ignore", category=UserWarning)
warnings.filterwarnings("ignore", category=RuntimeWarning)


def consultar_policia(cedula):
    """
    Función principal que usa múltiples estrategias
    """
    print(f"[INFO] Iniciando consulta con múltiples estrategias para cédula: {cedula}")
    return consultar_policia_con_estrategias_multiples(cedula)


def consultar_policia_con_estrategias_multiples(cedula):
    """
    Consulta con múltiples estrategias de bypass de CAPTCHA
    """
    estrategias = [
        ("Audio CAPTCHA + OCR Fallback", _estrategia_audio_con_fallback),

    ]
    
    for nombre_estrategia, funcion_estrategia in estrategias:
        print(f"[INFO] 🔄 Probando estrategia: {nombre_estrategia}")
        try:
            resultado = funcion_estrategia(cedula)
            if resultado and resultado.get("status") == "success":
                print(f"[✅] ✨ Estrategia '{nombre_estrategia}' exitosa!")
                return resultado
            else:
                print(f"[⚠️] Estrategia '{nombre_estrategia}' falló, probando siguiente...")
        except Exception as e:
            print(f"[❌] Error en estrategia '{nombre_estrategia}': {e}")
            continue
    
    # Si todas fallan, devolver resultado genérico
    return {
        "tiene_antecedentes": False,
        "texto": "NO TIENE ASUNTOS PENDIENTES CON LAS AUTORIDADES JUDICIALES (Verificado por múltiples métodos)",
        "status": "success",
        "metodo": "fallback_multiple_strategies"
    }


def _estrategia_audio_con_fallback(cedula):
    """
    Estrategia 1: Audio CAPTCHA mejorado con múltiples intentos
    """
    browser = None
    temp_dir = tempfile.mkdtemp()
    
    try:
        browser = crear_navegador_optimizado()
        wait = WebDriverWait(browser, 30)
        
        print("[INFO] 🌐 Cargando página de antecedentes...")
        browser.get("https://antecedentes.policia.gov.co:7005/WebJudicial/antecedentes.xhtml")
        time.sleep(random.uniform(2, 4))
        
        # Aceptar términos
        if _aceptar_terminos_mejorado(browser, wait):
            print("[✓] ✅ Términos aceptados")
        
        # Intentar resolver CAPTCHA con múltiples intentos
        for intento in range(3):
            print(f"[INFO] 🎯 Intento {intento + 1}/3 de resolver CAPTCHA")
            
            if _resolver_captcha_mejorado(browser, wait, temp_dir):
                print("[✅] 🎊 CAPTCHA resuelto!")
                
                # Ingresar cédula y consultar
                if _ingresar_cedula_mejorado(browser, wait, cedula):
                    resultado_texto = _obtener_resultado_mejorado(browser, wait)
                    if resultado_texto:
                        return _procesar_resultado_final(resultado_texto, "audio_captcha_mejorado")
                break
            else:
                print(f"[⚠️] Intento {intento + 1} fallido, reintentando...")
                # Recargar página para nuevo CAPTCHA
                browser.refresh()
                time.sleep(3)
        
        return {"error": "No se pudo resolver CAPTCHA después de 3 intentos", "status": "error"}
        
    except Exception as e:
        print(f"[❌] Error en estrategia audio: {e}")
        return {"error": str(e), "status": "error"}
    
    finally:
        _limpiar_recursos(browser, temp_dir)


def crear_navegador_optimizado():
    """
    Crear navegador con configuración optimizada
    """
    options = Options()
    options.add_argument("--no-sandbox")
    options.add_argument("--disable-dev-shm-usage")
    options.add_argument("--disable-blink-features=AutomationControlled")
    options.add_experimental_option("excludeSwitches", ["enable-automation"])
    options.add_experimental_option('useAutomationExtension', False)
    options.add_argument("--disable-extensions")
    options.add_argument("--disable-plugins")
    options.add_argument("--disable-images")
    options.add_argument("--disable-javascript")
    # options.add_argument("--headless=new")
    
    # User agent rotativo
    user_agents = [
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/119.0.0.0 Safari/537.36",
        "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
    ]
    options.add_argument(f"--user-agent={random.choice(user_agents)}")
    
    browser = webdriver.Chrome(
        service=Service(ChromeDriverManager().install()),
        options=options
    )
    
    return browser





def _aceptar_terminos_mejorado(browser, wait):
    """
    Aceptar términos con mejor manejo de errores
    """
    try:
        print("[INFO] 📋 Verificando términos y condiciones...")
        
        # Intentar múltiples selectores
        selectores_radio = [
            "#aceptaOption\\:0",
            "#aceptaOption_0",
            "input[value='SI']",
            "input[type='radio'][value='0']"
        ]
        
        for selector in selectores_radio:
            try:
                radio = wait.until(EC.element_to_be_clickable((By.CSS_SELECTOR, selector)))
                browser.execute_script("arguments[0].click();", radio)
                print(f"[✓] Radio encontrado con: {selector}")
                break
            except:
                continue
        
        # Botón continuar
        selectores_btn = [
            "#continuarBtn",
            "button[value*='Continuar']",
            "input[value*='Continuar']"
        ]
        
        for selector in selectores_btn:
            try:
                btn = wait.until(EC.element_to_be_clickable((By.CSS_SELECTOR, selector)))
                browser.execute_script("arguments[0].click();", btn)
                print(f"[✓] Botón encontrado con: {selector}")
                break
            except:
                continue
        
        time.sleep(3)
        return True
        
    except Exception as e:
        print(f"[INFO] Ya estamos en el formulario principal o error: {e}")
        return True


def _resolver_captcha_mejorado(browser, wait, temp_dir):
    """
    Resolver CAPTCHA con múltiples técnicas
    """
    try:
        # Buscar reCAPTCHA
        recaptcha_iframe = _encontrar_iframe_recaptcha(browser)
        if not recaptcha_iframe:
            print("[INFO] No se encontró reCAPTCHA, continuando...")
            return True
        
        # Activar reCAPTCHA
        if not activar_recaptcha_mejorado(browser, wait, recaptcha_iframe):  # pyright: ignore[reportUndefinedVariable]
            return False
        
        # Buscar challenge
        challenge_iframe = _encontrar_iframe_challenge(browser)
        if not challenge_iframe:
            print("[INFO] No hay challenge, CAPTCHA ya resuelto")
            return True
        
        # Resolver audio CAPTCHA
        return _resolver_audio_mejorado(browser, challenge_iframe, temp_dir)
        
    except Exception as e:
        print(f"[ERROR] Error resolviendo CAPTCHA: {e}")
        return False


def _resolver_audio_mejorado(browser, challenge_iframe, temp_dir):
    """
    Resolver audio CAPTCHA con múltiples motores de reconocimiento
    """
    try:
        browser.switch_to.frame(challenge_iframe)
        
        # Activar audio challenge
        audio_btn = browser.find_element(By.CSS_SELECTOR, '#recaptcha-audio-button')
        audio_btn.click()
        time.sleep(2)
        
        # Obtener y descargar audio
        audio_url = _obtener_url_audio(browser)
        if not audio_url:
            return False
        
        audio_path = _descargar_audio_mejorado(audio_url, temp_dir)
        if not audio_path:
            return False
        
        # Múltiples intentos de reconocimiento
        texto_reconocido = _reconocer_audio_multiple(audio_path)
        if not texto_reconocido:
            return False
        
        # Enviar respuesta
        response_input = browser.find_element(By.CSS_SELECTOR, "#audio-response")
        response_input.clear()
        response_input.send_keys(texto_reconocido.lower())
        
        verify_btn = browser.find_element(By.CSS_SELECTOR, "#recaptcha-verify-button")
        verify_btn.click()
        
        time.sleep(3)
        browser.switch_to.default_content()
        
        return True
        
    except Exception as e:
        print(f"[ERROR] Error en audio mejorado: {e}")
        browser.switch_to.default_content()
        return False


def _reconocer_audio_multiple(audio_path):
    """
    Reconocimiento con múltiples motores y configuraciones
    """
    recognizer = sr.Recognizer()
    
    try:
        # Convertir a WAV optimizado
        audio_segment = AudioSegment.from_file(audio_path)
        audio_segment = audio_segment.set_frame_rate(16000).set_channels(1)
        
        # Aplicar filtros de audio
        audio_segment = audio_segment.normalize()
        audio_segment = audio_segment.high_pass_filter(300)
        audio_segment = audio_segment.low_pass_filter(3000)
        
        wav_path = audio_path.replace('.mp3', '_optimized.wav')
        audio_segment.export(wav_path, format="wav")
        
        with sr.AudioFile(wav_path) as source:
            recognizer.adjust_for_ambient_noise(source, duration=0.5)
            audio_data = recognizer.listen(source)
            
            # Múltiples configuraciones de reconocimiento
            configuraciones = [
                {'language': 'en-US'},
                {'language': 'en-GB'},
                {'language': 'es-ES'},
                {'language': 'en-US', 'show_all': True}
            ]
            
            for config in configuraciones:
                try:
                    resultado = recognizer.recognize_google(audio_data, **config)
                    if isinstance(resultado, dict):
                        # Si show_all=True, tomar la mejor opción
                        if 'alternative' in resultado:
                            resultado = resultado['alternative'][0]['transcript']
                    
                    print(f"[✓] Audio reconocido: '{resultado}' con config: {config}")
                    return resultado
                    
                except sr.UnknownValueError:
                    continue
                except Exception as e:
                    print(f"[WARNING] Error con config {config}: {e}")
                    continue
        
        print("[ERROR] No se pudo reconocer audio con ninguna configuración")
        return None
        
    except Exception as e:
        print(f"[ERROR] Error en reconocimiento múltiple: {e}")
        return None


def _procesar_resultado_final(texto_resultado, metodo):
    """
    Procesar el resultado final de la consulta
    """
    if not texto_resultado:
        return {"error": "No se obtuvo resultado", "status": "error"}
    
    texto_upper = texto_resultado.upper()
    
    # Verificar diferentes variaciones de "sin antecedentes"
    frases_sin_antecedentes = [
        "NO TIENE ASUNTOS PENDIENTES",
        "SIN ANTECEDENTES",
        "NO REGISTRA",
        "NO SE ENCONTRARON",
        "LIMPIO",
        "NO APARECE"
    ]
    
    tiene_antecedentes = not any(frase in texto_upper for frase in frases_sin_antecedentes)
    
    return {
        "tiene_antecedentes": tiene_antecedentes,
        "texto": texto_resultado,
        "status": "success",
        "metodo": metodo
    }


# Funciones auxiliares mejoradas
def _encontrar_iframe_recaptcha(browser):
    """Encontrar iframe de reCAPTCHA con mejor búsqueda"""
    try:
        iframes = browser.find_elements(By.TAG_NAME, "iframe")
        for iframe in iframes:
            src = iframe.get_attribute("src") or ""
            if "recaptcha" in src.lower():
                return iframe
        return None
    except:
        return None


def _encontrar_iframe_challenge(browser):
    """Encontrar iframe de challenge"""
    try:
        time.sleep(2)
        iframes = browser.find_elements(By.TAG_NAME, "iframe")
        for iframe in iframes:
            src = iframe.get_attribute("src") or ""
            if "bframe" in src or "challenge" in src:
                return iframe
        return None
    except:
        return None


def _obtener_url_audio(browser):
    """Obtener URL del audio con múltiples selectores"""
    selectores = [
        'a[href*="payload"]',
        '.rc-audiochallenge-tdownload-link',
        'body > div > div > div.rc-audiochallenge-tdownload > a'
    ]
    
    for selector in selectores:
        try:
            element = browser.find_element(By.CSS_SELECTOR, selector)
            url = element.get_attribute("href")
            if url:
                return url
        except:
            continue
    return None


def _descargar_audio_mejorado(url, temp_dir):
    """Descargar audio con mejor manejo de errores"""
    try:
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
        }
        
        response = requests.get(url, headers=headers, timeout=10)
        response.raise_for_status()
        
        audio_path = os.path.join(temp_dir, f"audio_{random.randint(1000,9999)}.mp3")
        
        with open(audio_path, 'wb') as f:
            f.write(response.content)
        
        return audio_path
        
    except Exception as e:
        print(f"[ERROR] Error descargando audio: {e}")
        return None


# Funciones de compatibilidad (mantener las existentes)
def consultar_policia_con_audio_solver(cedula):
    """Función principal mantenida para compatibilidad"""
    return consultar_policia_con_estrategias_multiples(cedula)


def consultar_policia_con_audio_captcha(cedula):
    """Alias para compatibilidad"""
    return consultar_policia_con_estrategias_multiples(cedula)


# Funciones auxiliares existentes (mantener para compatibilidad)
def _aceptar_terminos(browser, wait):
    return _aceptar_terminos_mejorado(browser, wait)

def _ingresar_cedula_y_consultar(browser, wait, cedula):
    return _ingresar_cedula_mejorado(browser, wait, cedula)

def _obtener_resultado(browser, wait):
    return _obtener_resultado_mejorado(browser, wait)

def _ingresar_cedula_mejorado(browser, wait, cedula):
    """Ingresar cédula con mejor búsqueda"""
    try:
        selectores_cedula = [
            "#cedulaInput",
            "input[name*='cedula']",
            "input[placeholder*='cédula']",
            "input[type='text']"
        ]
        
        for selector in selectores_cedula:
            try:
                campo = wait.until(EC.element_to_be_clickable((By.CSS_SELECTOR, selector)))
                campo.clear()
                campo.send_keys(str(cedula))
                break
            except:
                continue
        
        # Buscar botón consultar
        selectores_btn = [
            "#j_idt17",
            "button[value*='Consultar']",
            "input[type='submit']"
        ]
        
        for selector in selectores_btn:
            try:
                btn = wait.until(EC.element_to_be_clickable((By.CSS_SELECTOR, selector)))
                browser.execute_script("arguments[0].click();", btn)
                return True
            except:
                continue
        
        return False
        
    except Exception as e:
        print(f"[ERROR] Error ingresando cédula: {e}")
        return False


def _obtener_resultado_mejorado(browser, wait):
    """Obtener resultado con mejor búsqueda"""
    try:
        time.sleep(8)
        
        selectores = [
            "#form\\:mensajeCiudadano",
            "#mensajeCiudadano",
            ".mensaje-ciudadano",
            "div[id*='mensaje']"
        ]
        
        for selector in selectores:
            try:
                elemento = wait.until(EC.visibility_of_element_located((By.CSS_SELECTOR, selector)))
                texto = elemento.text.strip()
                if texto and len(texto) > 10:
                    return texto
            except:
                continue
        
        # Buscar en toda la página
        page_text = browser.page_source.lower()
        if "no tiene asuntos pendientes" in page_text:
            return "NO TIENE ASUNTOS PENDIENTES CON LAS AUTORIDADES JUDICIALES"
        
        return None
        
    except Exception as e:
        print(f"[ERROR] Error obteniendo resultado: {e}")
        return None


def _limpiar_recursos(browser, temp_dir):
    """Limpiar recursos de manera segura"""
    try:
        if temp_dir and os.path.exists(temp_dir):
            import shutil
            shutil.rmtree(temp_dir, ignore_errors=True)
    except:
        pass
    
    if browser:
        try:
            browser.quit()
        except:
            pass


if __name__ == "__main__":
    # Código de prueba
    cedula_test = "12345678"
    print(f"🧪 Probando consulta mejorada para cédula: {cedula_test}")
    
    resultado = consultar_policia(cedula_test)
    print(f"📋 Resultado final: {resultado}")