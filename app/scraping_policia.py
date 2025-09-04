import undetected_chromedriver as uc
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException, NoSuchElementException
import speech_recognition as sr
from pydub import AudioSegment
import urllib.request
import time
import os
import traceback
from datetime import datetime
import warnings

warnings.filterwarnings("ignore")


def consultar_policia(cedula):
    """Consulta antecedentes policiales - versión simplificada y robusta"""
    
    driver = None
    
    try:
        # Usar undetected_chromedriver que es más estable
        options = uc.ChromeOptions()
        options.add_argument('--no-sandbox')
        options.add_argument('--disable-dev-shm-usage')
        options.add_experimental_option('excludeSwitches', ['enable-logging'])
        
        driver = uc.Chrome(options=options)
        driver.implicitly_wait(10)
        
        print("Accediendo al sitio...")
        driver.get("https://antecedentes.policia.gov.co:7005/WebJudicial/")
        time.sleep(5)
        
        # Paso 1: Aceptar términos con espera robusta
        print("Aceptando términos...")
        try:
            # Esperar y marcar radio button
            WebDriverWait(driver, 10).until(
                EC.presence_of_element_located((By.ID, "aceptaOption:0"))
            )
            
            accept_js = """
            var radio = document.getElementById('aceptaOption:0');
            if (radio) {
                radio.checked = true;
                radio.dispatchEvent(new Event('change'));
            }
            """
            driver.execute_script(accept_js)
            time.sleep(2)
            
            # Hacer clic en continuar
            continue_js = """
            var btn = document.getElementById('continuarBtn');
            if (btn) {
                btn.click();
            }
            """
            driver.execute_script(continue_js)
            time.sleep(5)
            
        except Exception as e:
            print(f"Error aceptando términos: {e}")
            return {"status": "error", "error": "Error aceptando términos", "metodo": "terminos_error"}
        
        # Paso 2: Esperar formulario y ingresar cédula
        print("Ingresando cédula...")
        try:
            WebDriverWait(driver, 15).until(
                EC.presence_of_element_located((By.ID, "cedulaInput"))
            )
            time.sleep(3)
            
            cedula_js = f"""
            var input = document.getElementById('cedulaInput');
            if (input) {{
                input.value = '{cedula}';
                input.dispatchEvent(new Event('input'));
                input.dispatchEvent(new Event('change'));
            }}
            """
            driver.execute_script(cedula_js)
            time.sleep(2)
            
        except Exception as e:
            print(f"Error ingresando cédula: {e}")
            return {"status": "error", "error": "Error ingresando cédula", "metodo": "input_error"}
        
        # Paso 3: Manejar CAPTCHA
        print("Procesando CAPTCHA...")
        try:
            # Buscar iframe de CAPTCHA
            captcha_iframe = WebDriverWait(driver, 10).until(
                EC.presence_of_element_located((By.XPATH, '//*[@id="captchaAntecedentes"]//iframe'))
            )
            
            # Cambiar a iframe
            driver.switch_to.frame(captcha_iframe)
            time.sleep(2)
            
            # Marcar checkbox
            checkbox_js = """
            var checkbox = document.getElementById('recaptcha-anchor');
            if (checkbox) {
                checkbox.click();
            }
            """
            driver.execute_script(checkbox_js)
            time.sleep(4)
            
            # Volver al contenido principal
            driver.switch_to.default_content()
            
            # Buscar iframe de desafío
            challenge_iframe = WebDriverWait(driver, 10).until(
                EC.presence_of_element_located((By.XPATH, "//iframe[contains(@title, 'challenge') or contains(@src, 'bframe')]"))
            )
            
            driver.switch_to.frame(challenge_iframe)
            time.sleep(2)
            
            # Hacer clic en audio
            audio_js = """
            var audioBtn = document.getElementById('recaptcha-audio-button');
            if (audioBtn) {
                audioBtn.click();
            }
            """
            driver.execute_script(audio_js)
            time.sleep(3)
            
            # Obtener enlace de audio
            audio_link_js = """
            var link = document.querySelector('.rc-audiochallenge-tdownload a');
            return link ? link.href : null;
            """
            
            audio_url = driver.execute_script(audio_link_js)
            
            if audio_url:
                print("Procesando audio CAPTCHA...")
                
                # Descargar audio
                urllib.request.urlretrieve(audio_url, "temp_audio.mp3")
                
                # Convertir a WAV
                audio_seg = AudioSegment.from_mp3("temp_audio.mp3")
                audio_seg.export("temp_audio.wav", format="wav")
                
                # Reconocer
                r = sr.Recognizer()
                with sr.AudioFile("temp_audio.wav") as source:
                    audio_data = r.listen(source)
                    texto = r.recognize_google(audio_data, language='en-US')
                
                print(f"Texto reconocido: {texto}")
                
                # Ingresar respuesta
                response_js = f"""
                var input = document.getElementById('audio-response');
                if (input) {{
                    input.value = '{texto.lower()}';
                    input.dispatchEvent(new Event('input'));
                }}
                """
                driver.execute_script(response_js)
                time.sleep(1)
                
                # Verificar
                verify_js = """
                var btn = document.getElementById('recaptcha-verify-button');
                if (btn) {
                    btn.click();
                }
                """
                driver.execute_script(verify_js)
                time.sleep(3)
                
                # Limpiar archivos
                os.remove("temp_audio.mp3")
                os.remove("temp_audio.wav")
                
            else:
                print("No se pudo obtener audio CAPTCHA")
                driver.switch_to.default_content()
                return {"status": "error", "error": "CAPTCHA no disponible", "metodo": "captcha_error"}
            
            # Volver al contenido principal
            driver.switch_to.default_content()
            
        except Exception as e:
            print(f"Error en CAPTCHA: {e}")
            try:
                driver.switch_to.default_content()
                os.remove("temp_audio.mp3")
                os.remove("temp_audio.wav")
            except:
                pass
            return {"status": "error", "error": "Error procesando CAPTCHA", "metodo": "captcha_error"}
        
        # Paso 4: Enviar formulario
        print("Enviando formulario...")
        time.sleep(3)
        
        submit_js = """
        var form = document.querySelector('form');
        if (form) {
            form.submit();
        }
        """
        driver.execute_script(submit_js)
        time.sleep(8)
        
        # Paso 5: Obtener resultado
        print("Obteniendo resultado...")
        try:
            resultado_element = WebDriverWait(driver, 15).until(
                EC.presence_of_element_located((By.ID, "form:mensajeCiudadano"))
            )
            
            texto_resultado = resultado_element.text.strip()
            
            if not texto_resultado:
                return {"status": "error", "error": "Resultado vacío", "metodo": "empty_result"}
            
            # Analizar resultado
            tiene_antecedentes = not any(frase in texto_resultado.upper() for frase in [
                "NO REGISTRA ANTECEDENTES",
                "SIN ANTECEDENTES",
                "NO TIENE ANTECEDENTES"
            ])
            
            return {
                "status": "success",
                "texto": texto_resultado,
                "tiene_antecedentes": tiene_antecedentes,
                "metodo": "undetected_chrome",
                "timestamp": datetime.now().isoformat()
            }
            
        except TimeoutException:
            return {"status": "error", "error": "Timeout obteniendo resultado", "metodo": "timeout_result"}
    
    except Exception as e:
        print(f"Error general: {e}")
        return {"status": "error", "error": f"Error: {str(e)}", "metodo": "general_error"}
    
    finally:
        if driver:
            try:
                driver.quit()
            except:
                pass


if __name__ == "__main__":
    resultado = consultar_policia("1234567890")
    print(resultado)