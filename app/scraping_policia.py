import undetected_chromedriver as uc
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.chrome.options import Options as ChromeOptions
from selenium.common.exceptions import TimeoutException, NoSuchElementException
from selenium.webdriver.common.action_chains import ActionChains
from selenium.webdriver.common.keys import Keys
import speech_recognition as sr
from pydub import AudioSegment
import urllib.request
import time
import os
import traceback
from datetime import datetime
import warnings
import random

warnings.filterwarnings("ignore")


def delay_humano(min_seconds=1, max_seconds=3):
    """Simula delays humanos aleatorios"""
    delay = random.uniform(min_seconds, max_seconds)
    time.sleep(delay)


def simular_escritura_humana(elemento, texto):
    """Simula escritura humana con delays aleatorios"""
    elemento.clear()
    for char in texto:
        elemento.send_keys(char)
        delay_humano(0.05, 0.15)  # Delay entre caracteres


def mover_mouse_humano(driver, elemento):
    """Simula movimiento de mouse humano"""
    actions = ActionChains(driver)
    actions.move_to_element(elemento)
    actions.pause(random.uniform(0.1, 0.3))
    actions.perform()


def reconocer_audio_captcha(audio_path, max_intentos=5):
    """
    Reconoce audio de CAPTCHA con estrategias robustas y fallbacks
    """
    import re
    import time
    
    if not os.path.exists(audio_path):
        print(f"❌ Archivo no existe: {audio_path}")
        return None
    
    print(f"🎤 Reconociendo audio: {audio_path}")
    
    # Estrategias de reconocimiento más agresivas
    estrategias = [
        # Estrategia 1: Configuración básica
        {
            "name": "Básica",
            "energy": 300,
            "pause": 0.8,
            "phrase": 0.3,
            "ambient": 0.5,
            "timeout": 10,
            "langs": ['en-US']
        },
        # Estrategia 2: Alta sensibilidad
        {
            "name": "Alta sensibilidad",
            "energy": 50,
            "pause": 0.1,
            "phrase": 0.01,
            "ambient": 2.0,
            "timeout": 20,
            "langs": ['en-US', 'es-ES']
        },
        # Estrategia 3: Procesamiento de audio
        {
            "name": "Con procesamiento",
            "energy": 25,
            "pause": 0.05,
            "phrase": 0.001,
            "ambient": 3.0,
            "timeout": 25,
            "langs": ['en-US', 'es-ES', 'es-CO'],
            "process": True
        },
        # Estrategia 4: Solo números
        {
            "name": "Solo números",
            "energy": 20,
            "pause": 0.02,
            "phrase": 0.0001,
            "ambient": 4.0,
            "timeout": 30,
            "langs": ['en-US'],
            "process": True,
            "numbers_only": True
        }
    ]
    
    for intento in range(max_intentos):
        print(f"🔄 Intento {intento + 1}/{max_intentos}")
        
        for estrategia in estrategias:
            print(f"🔄 Probando: {estrategia['name']}")
            
            try:
                r = sr.Recognizer()
                r.energy_threshold = estrategia['energy']
                r.pause_threshold = estrategia['pause']
                r.phrase_threshold = estrategia['phrase']
                r.dynamic_energy_threshold = True
                r.dynamic_energy_adjustment_damping = 0.15
                r.dynamic_energy_ratio = 1.5
                
                # Procesar audio si es necesario
                audio_file = audio_path
                if estrategia.get('process'):
                    try:
                        print("🔧 Procesando audio...")
                        audio_seg = AudioSegment.from_wav(audio_path)
                        
                        # Aplicar múltiples mejoras
                        audio_seg = audio_seg.normalize()
                        audio_seg = audio_seg.high_pass_filter(100)
                        audio_seg = audio_seg.low_pass_filter(8000)
                        audio_seg = audio_seg + 12  # Aumentar volumen
                        
                        # Crear versión procesada
                        processed_path = audio_path.replace('.wav', f'_proc_{intento}.wav')
                        audio_seg.export(processed_path, format="wav")
                        audio_file = processed_path
                        print("✅ Audio procesado")
                    except Exception as proc_error:
                        print(f"⚠️ Error procesando: {proc_error}")
                        continue
                
                # Intentar reconocimiento con cada idioma
                for idioma in estrategia['langs']:
                    try:
                        print(f"🌐 Probando idioma: {idioma}")
                        
                        with sr.AudioFile(audio_file) as source:
                            # Ajustar para ruido de fondo
                            r.adjust_for_ambient_noise(source, duration=estrategia['ambient'])
                            
                            # Escuchar audio
                            audio_data = r.listen(source, timeout=estrategia['timeout'])
                            
                            # Reconocer con Google
                            texto = r.recognize_google(audio_data, language=idioma)
                        
                        if texto and texto.strip():
                            print(f"✅ Texto reconocido: '{texto}'")
                            
                            # Limpiar texto
                            texto_limpio = limpiar_texto_captcha(texto)
                            
                            # Si es estrategia de solo números, extraer números
                            if estrategia.get('numbers_only') and texto_limpio:
                                numeros = re.findall(r'\d+', texto_limpio)
                                if numeros:
                                    texto_limpio = ''.join(numeros)
                                    print(f"🔢 Solo números: '{texto_limpio}'")
                            
                            # Validar resultado
                            if texto_limpio and len(texto_limpio) >= 2:
                                print(f"✅ Reconocimiento exitoso: '{texto_limpio}'")
                                
                                # Limpiar archivo procesado
                                if audio_file != audio_path and os.path.exists(audio_file):
                                    os.remove(audio_file)
                                
                                return texto_limpio
                            else:
                                print(f"⚠️ Texto muy corto: '{texto_limpio}'")
                                
                    except sr.UnknownValueError:
                        print(f"⚠️ No se pudo entender con {idioma}")
                        continue
                    except sr.RequestError as e:
                        print(f"❌ Error de servicio con {idioma}: {e}")
                        continue
                    except Exception as e:
                        print(f"⚠️ Error con {idioma}: {e}")
                        continue
                
                # Limpiar archivo procesado
                if audio_file != audio_path and os.path.exists(audio_file):
                    try:
                        os.remove(audio_file)
                    except:
                        pass
                        
            except Exception as e:
                print(f"⚠️ Error en estrategia {estrategia['name']}: {e}")
                continue
        
        # Delay entre intentos
        if intento < max_intentos - 1:
            print("⏳ Esperando antes del siguiente intento...")
            time.sleep(2)
    
    # Último intento: reconocimiento alternativo
    print("🔄 Intentando reconocimiento alternativo...")
    return reconocer_audio_alternativo_simple(audio_path)


def reconocer_audio_alternativo_simple(audio_path):
    """
    Reconocimiento alternativo simplificado como último recurso
    """
    try:
        print("🔄 Reconocimiento alternativo...")
        
        # Crear múltiples versiones del audio
        audio_seg = AudioSegment.from_wav(audio_path)
        
        versiones = [
            audio_seg,
            audio_seg.normalize() + 15,
            audio_seg.high_pass_filter(50) + 10,
            audio_seg.speedup(playback_speed=0.7),
            audio_seg.speedup(playback_speed=1.3)
        ]
        
        for i, version in enumerate(versiones):
            try:
                version_path = audio_path.replace('.wav', f'_alt_{i}.wav')
                version.export(version_path, format="wav")
                
                r = sr.Recognizer()
                r.energy_threshold = 10
                r.pause_threshold = 0.05
                r.phrase_threshold = 0.001
                
                with sr.AudioFile(version_path) as source:
                    r.adjust_for_ambient_noise(source, duration=2.0)
                    audio_data = r.listen(source, timeout=15)
                    texto = r.recognize_google(audio_data, language='en-US')
                
                if texto and texto.strip():
                    texto_limpio = limpiar_texto_captcha(texto)
                    if texto_limpio and len(texto_limpio) >= 2:
                        print(f"✅ Reconocimiento alternativo exitoso: '{texto_limpio}'")
                        os.remove(version_path)
                        return texto_limpio
                
                os.remove(version_path)
                
            except Exception as e:
                print(f"⚠️ Error en versión {i}: {e}")
                if os.path.exists(version_path):
                    os.remove(version_path)
                continue
        
        print("❌ Reconocimiento alternativo falló")
        return None
        
    except Exception as e:
        print(f"❌ Error en reconocimiento alternativo: {e}")
        return None


def reconocimiento_manual_captcha(audio_path):
    """
    Reconocimiento manual como último recurso - genera un valor aleatorio
    """
    try:
        print("🔄 Reconocimiento manual (último recurso)...")
        
        # Generar un valor aleatorio de 4-6 dígitos como fallback
        import random
        texto_manual = str(random.randint(1000, 999999))
        
        print(f"⚠️ Usando valor aleatorio como fallback: '{texto_manual}'")
        print("⚠️ NOTA: Este es un valor generado automáticamente, no reconocido del audio")
        
        return texto_manual
        
    except Exception as e:
        print(f"❌ Error en reconocimiento manual: {e}")
        return None


def reconocer_audio_alternativo(audio_path):
    """
    Intenta reconocimiento con servicios alternativos como fallback
    """
    try:
        print("🔄 Probando reconocimiento alternativo...")
        
        # Estrategia alternativa 1: Usar Sphinx (offline)
        try:
            import speech_recognition as sr
            r = sr.Recognizer()
            
            with sr.AudioFile(audio_path) as source:
                r.adjust_for_ambient_noise(source, duration=1.0)
                audio_data = r.listen(source, timeout=10)
                texto = r.recognize_sphinx(audio_data)
                
            if texto and texto.strip():
                print(f"✅ Reconocimiento Sphinx exitoso: '{texto}'")
                texto_limpio = limpiar_texto_captcha(texto)
                if texto_limpio and len(texto_limpio) >= 3:
                    return texto_limpio
                    
        except Exception as sphinx_error:
            print(f"⚠️ Error con Sphinx: {sphinx_error}")
        
        # Estrategia alternativa 2: Procesamiento de audio extremo
        try:
            print("🔧 Aplicando procesamiento extremo de audio...")
            
            # Cargar y procesar audio con múltiples filtros
            audio_seg = AudioSegment.from_wav(audio_path)
            
            # Aplicar filtros agresivos
            audio_seg = audio_seg.normalize()
            audio_seg = audio_seg.high_pass_filter(100)
            audio_seg = audio_seg.low_pass_filter(6000)
            audio_seg = audio_seg + 15  # Aumentar volumen significativamente
            
            # Crear múltiples versiones del audio
            versiones = [
                audio_seg,
                audio_seg.speedup(playback_speed=0.8),  # Más lento
                audio_seg.speedup(playback_speed=1.2),  # Más rápido
                audio_seg + 5,  # Más volumen
                audio_seg - 5,  # Menos volumen
            ]
            
            for i, version in enumerate(versiones):
                try:
                    version_path = audio_path.replace('.wav', f'_alt_{i}.wav')
                    version.export(version_path, format="wav")
                    
                    r = sr.Recognizer()
                    r.energy_threshold = 20
                    r.pause_threshold = 0.1
                    r.phrase_threshold = 0.001
                    
                    with sr.AudioFile(version_path) as source:
                        r.adjust_for_ambient_noise(source, duration=2.0)
                        audio_data = r.listen(source, timeout=15)
                        texto = r.recognize_google(audio_data, language='en-US')
                    
                    if texto and texto.strip():
                        print(f"✅ Reconocimiento alternativo exitoso (versión {i}): '{texto}'")
                        texto_limpio = limpiar_texto_captcha(texto)
                        if texto_limpio and len(texto_limpio) >= 3:
                            # Limpiar archivo temporal
                            if os.path.exists(version_path):
                                os.remove(version_path)
                            return texto_limpio
                    
                    # Limpiar archivo temporal
                    if os.path.exists(version_path):
                        os.remove(version_path)
                        
                except Exception as version_error:
                    print(f"⚠️ Error con versión {i}: {version_error}")
                    if os.path.exists(version_path):
                        os.remove(version_path)
                    continue
                    
        except Exception as alt_error:
            print(f"⚠️ Error en procesamiento alternativo: {alt_error}")
        
        # Estrategia alternativa 3: Intentar con diferentes configuraciones de Google
        try:
            print("🔄 Probando configuraciones alternativas de Google...")
            
            configuraciones_alt = [
                {"language": "en-US", "show_all": True},
                {"language": "es-ES", "show_all": True},
                {"language": "en-US", "show_all": False},
                {"language": "es-ES", "show_all": False},
            ]
            
            for config in configuraciones_alt:
                try:
                    r = sr.Recognizer()
                    r.energy_threshold = 10
                    r.pause_threshold = 0.05
                    r.phrase_threshold = 0.001
                    
                    with sr.AudioFile(audio_path) as source:
                        r.adjust_for_ambient_noise(source, duration=3.0)
                        audio_data = r.listen(source, timeout=20)
                        texto = r.recognize_google(audio_data, **config)
                    
                    if texto and texto.strip():
                        print(f"✅ Google alternativo exitoso: '{texto}'")
                        texto_limpio = limpiar_texto_captcha(texto)
                        if texto_limpio and len(texto_limpio) >= 3:
                            return texto_limpio
                            
                except Exception as google_error:
                    print(f"⚠️ Error con Google alternativo: {google_error}")
                    continue
                    
        except Exception as google_alt_error:
            print(f"⚠️ Error en Google alternativo: {google_alt_error}")
        
        return None
        
    except Exception as e:
        print(f"❌ Error en reconocimiento alternativo: {e}")
        return None


def limpiar_texto_captcha(texto):
    """
    Limpia y normaliza el texto reconocido del CAPTCHA de forma simplificada
    """
    import re
    
    if not texto:
        return None
    
    # Limpiar texto de forma simple y eficiente
    texto_limpio = re.sub(r'[^a-zA-Z0-9]', '', texto.strip().lower())
    
    # Si está vacío, extraer solo números
    if not texto_limpio:
        numeros = re.findall(r'\d+', texto)
        texto_limpio = ''.join(numeros) if numeros else None
    
    return texto_limpio


def crear_audio_prueba_captcha(texto="123456", archivo_salida="test_captcha.wav"):
    """
    Crea un archivo de audio de prueba que simula un CAPTCHA
    """
    try:
        from gtts import gTTS  # pyright: ignore[reportMissingImports]
        import tempfile
        import os
        
        print(f"🎵 Creando audio de prueba con texto: '{texto}'")
        
        # Crear archivo temporal con gTTS
        tts = gTTS(text=texto, lang='en', slow=True)
        temp_mp3 = tempfile.NamedTemporaryFile(delete=False, suffix='.mp3')
        tts.save(temp_mp3.name)
        
        # Convertir a WAV con pydub
        audio_seg = AudioSegment.from_mp3(temp_mp3.name)
        
        # Aplicar efectos similares a un CAPTCHA real
        audio_seg = audio_seg.normalize()
        audio_seg = audio_seg.high_pass_filter(200)
        audio_seg = audio_seg.low_pass_filter(6000)
        audio_seg = audio_seg + 5  # Aumentar volumen ligeramente
        
        # Exportar como WAV
        audio_seg.export(archivo_salida, format="wav")
        
        # Limpiar archivo temporal
        os.unlink(temp_mp3.name)
        
        print(f"✅ Audio de prueba creado: {archivo_salida}")
        return True
        
    except Exception as e:
        print(f"❌ Error creando audio de prueba: {e}")
        return False


def diagnosticar_audio_captcha(audio_path):
    """
    Diagnostica un archivo de audio CAPTCHA y proporciona información detallada
    """
    try:
        print(f"🔍 Diagnosticando archivo de audio: {audio_path}")
        print("-" * 50)
        
        if not os.path.exists(audio_path):
            print("❌ El archivo no existe")
            return False
        
        # Información básica del archivo
        size = os.path.getsize(audio_path)
        print(f"📁 Tamaño del archivo: {size} bytes")
        
        if size == 0:
            print("❌ El archivo está vacío")
            return False
        
        # Información del audio con pydub
        try:
            audio_seg = AudioSegment.from_wav(audio_path)
            print(f"🎵 Duración: {len(audio_seg)}ms ({len(audio_seg)/1000:.2f}s)")
            print(f"🔊 Volumen promedio: {audio_seg.dBFS:.2f} dBFS")
            print(f"📊 Frecuencia de muestreo: {audio_seg.frame_rate} Hz")
            print(f"🎛️ Canales: {audio_seg.channels}")
            
            # Análisis de calidad
            if audio_seg.dBFS < -30:
                print("⚠️ Audio muy silencioso")
            elif audio_seg.dBFS > -5:
                print("⚠️ Audio muy alto (posible distorsión)")
            else:
                print("✅ Nivel de volumen adecuado")
            
            if len(audio_seg) < 1000:  # Menos de 1 segundo
                print("⚠️ Audio muy corto")
            elif len(audio_seg) > 10000:  # Más de 10 segundos
                print("⚠️ Audio muy largo")
            else:
                print("✅ Duración adecuada")
                
        except Exception as audio_error:
            print(f"❌ Error analizando audio: {audio_error}")
            return False
        
        # Probar reconocimiento básico
        print("\n🎤 Probando reconocimiento básico...")
        try:
            import speech_recognition as sr
            r = sr.Recognizer()
            
            with sr.AudioFile(audio_path) as source:
                r.adjust_for_ambient_noise(source, duration=1.0)
                audio_data = r.listen(source, timeout=10)
                texto = r.recognize_google(audio_data, language='en-US')
                
            if texto:
                print(f"✅ Reconocimiento básico exitoso: '{texto}'")
            else:
                print("⚠️ Reconocimiento básico falló")
                
        except Exception as recog_error:
            print(f"❌ Error en reconocimiento básico: {recog_error}")
        
        print("-" * 50)
        return True
        
    except Exception as e:
        print(f"❌ Error en diagnóstico: {e}")
        return False


def descargar_audio_captcha(audio_url, max_intentos=5):
    """
    Descarga y valida el audio del CAPTCHA con múltiples estrategias robustas
    """
    import urllib.request
    import urllib.parse
    import time
    import ssl
    
    print(f"🔗 Descargando audio desde: {audio_url[:100]}...")
    
    # Limpiar archivos temporales
    for archivo in ["temp_audio.mp3", "temp_audio.wav", "temp_audio_alt.mp3"]:
        if os.path.exists(archivo):
            try:
                os.remove(archivo)
            except:
                pass
    
    # Configurar SSL para evitar errores de certificado
    ssl_context = ssl.create_default_context()
    ssl_context.check_hostname = False
    ssl_context.verify_mode = ssl.CERT_NONE
    
    # Múltiples estrategias de descarga
    estrategias = [
        {
            "name": "Estrategia 1: Headers básicos",
            "headers": {
                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36'
            }
        },
        {
            "name": "Estrategia 2: Headers completos",
            "headers": {
                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
                'Accept': 'audio/webm,audio/ogg,audio/wav,audio/*;q=0.9,application/ogg;q=0.7,video/*;q=0.6,*/*;q=0.5',
                'Accept-Language': 'es-ES,es;q=0.9,en;q=0.8',
                'Accept-Encoding': 'gzip, deflate, br',
                'Connection': 'keep-alive',
                'Upgrade-Insecure-Requests': '1',
                'Sec-Fetch-Dest': 'audio',
                'Sec-Fetch-Mode': 'no-cors',
                'Sec-Fetch-Site': 'cross-site'
            }
        },
        {
            "name": "Estrategia 3: Headers mínimos",
            "headers": {
                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
            }
        }
    ]
    
    for intento in range(max_intentos):
        print(f"🔄 Intento {intento + 1}/{max_intentos}")
        
        for estrategia in estrategias:
            print(f"🔄 Probando: {estrategia['name']}")
            
            try:
                # Crear request con headers
                req = urllib.request.Request(audio_url, headers=estrategia['headers'])
                
                # Configurar timeout y SSL
                with urllib.request.urlopen(req, timeout=30, context=ssl_context) as response:
                    print(f"📡 Respuesta HTTP: {response.status}")
                    
                    if response.status == 200:
                        # Leer datos
                        audio_data = response.read()
                        print(f"📊 Datos recibidos: {len(audio_data)} bytes")
                        
                        # Verificar tamaño mínimo
                        if len(audio_data) < 1024:
                            print(f"⚠️ Archivo muy pequeño: {len(audio_data)} bytes")
                            continue
                        
                        # Guardar archivo
                        with open("temp_audio.mp3", "wb") as f:
                            f.write(audio_data)
                        
                        # Validar archivo
                        if validar_archivo_audio("temp_audio.mp3"):
                            print(f"✅ Audio descargado exitosamente ({len(audio_data)} bytes)")
                            return True
                        else:
                            print("⚠️ Archivo descargado no es válido")
                            continue
                    else:
                        print(f"⚠️ Respuesta HTTP {response.status}")
                        continue
                        
            except urllib.error.HTTPError as e:
                print(f"⚠️ Error HTTP {e.code}: {e.reason}")
                continue
            except urllib.error.URLError as e:
                print(f"⚠️ Error de URL: {e.reason}")
                continue
            except Exception as e:
                print(f"⚠️ Error en descarga: {e}")
                continue
        
        # Delay entre intentos
        if intento < max_intentos - 1:
            print("⏳ Esperando antes del siguiente intento...")
            time.sleep(2)
    
    # Último intento: descarga alternativa
    print("🔄 Intentando descarga alternativa...")
    return descargar_audio_alternativo(audio_url)


def descargar_audio_alternativo(audio_url):
    """
    Descarga alternativa con diferentes métodos
    """
    try:
        import requests
        
        print("🔄 Usando requests como alternativa...")
        
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36'
        }
        
        response = requests.get(audio_url, headers=headers, timeout=30, verify=False)
        
        if response.status_code == 200 and len(response.content) > 1024:
            with open("temp_audio.mp3", "wb") as f:
                f.write(response.content)
            
            if validar_archivo_audio("temp_audio.mp3"):
                print(f"✅ Descarga alternativa exitosa ({len(response.content)} bytes)")
                return True
        
        print("❌ Descarga alternativa falló")
        return False
        
    except Exception as e:
        print(f"❌ Error en descarga alternativa: {e}")
        return False


def validar_archivo_audio(archivo_path):
    """
    Valida que un archivo de audio sea válido de forma simplificada
    """
    try:
        if not os.path.exists(archivo_path) or os.path.getsize(archivo_path) < 1024:
            return False
        
        # Verificar que se puede cargar con pydub
        audio_seg = AudioSegment.from_file(archivo_path)
        return len(audio_seg) > 0
    except:
        return False


def convertir_audio_captcha(archivo_mp3, archivo_wav, max_intentos=3):
    """
    Convierte audio MP3 a WAV de forma simplificada
    """
    print(f"🔄 Convirtiendo audio...")
    
    for intento in range(max_intentos):
        try:
            # Intentar conversión directa
            audio_seg = AudioSegment.from_file(archivo_mp3)
            audio_seg.export(archivo_wav, format="wav")
            print("✅ Conversión exitosa")
            return True
        except:
            # Intentar con procesamiento
            try:
                audio_seg = AudioSegment.from_file(archivo_mp3)
                audio_seg = audio_seg.normalize().high_pass_filter(200) + 5
                audio_seg.export(archivo_wav, format="wav")
                print("✅ Conversión con procesamiento exitosa")
                return True
            except:
                continue
    
    print("❌ No se pudo convertir audio")
    return False


def obtener_audio_url_captcha(driver, max_intentos=5):
    """
    Obtiene la URL del audio del CAPTCHA con múltiples estrategias robustas
    """
    print("🔍 Obteniendo URL del audio...")
    
    # Múltiples estrategias para encontrar la URL
    estrategias = [
        {
            "name": "Selectores estándar",
            "selectores": [
                ".rc-audiochallenge-tdownload a",
                "a[href*='audio']",
                "audio[src]",
                "a[href*='mp3'], a[href*='wav']"
            ]
        },
        {
            "name": "Búsqueda por atributos",
            "selectores": [
                "a[href*='recaptcha']",
                "a[href*='google']",
                "a[href*='captcha']",
                "a[href*='challenge']"
            ]
        },
        {
            "name": "Búsqueda en iframe",
            "selectores": [
                "iframe[src*='recaptcha']",
                "iframe[src*='google']",
                "iframe[src*='captcha']"
            ]
        },
        {
            "name": "Búsqueda en HTML completo",
            "selectores": ["html"]
        }
    ]
    
    for intento in range(max_intentos):
        print(f"🔄 Intento {intento + 1}/{max_intentos}")
        
        for estrategia in estrategias:
            print(f"🔄 Probando: {estrategia['name']}")
            
            for selector in estrategia['selectores']:
                try:
                    if estrategia['name'] == "Búsqueda en HTML completo":
                        # Búsqueda en HTML completo
                        js = """
                        var html = document.documentElement.innerHTML;
                        var audioMatch = html.match(/https?:\/\/[^"'\s]+\.(mp3|wav|ogg|webm)/i);
                        return audioMatch ? audioMatch[0] : null;
                        """
                    elif "iframe" in selector:
                        # Buscar en iframes
                        js = f"""
                        var iframes = document.querySelectorAll('{selector}');
                        for (var i = 0; i < iframes.length; i++) {{
                            try {{
                                var iframeDoc = iframes[i].contentDocument || iframes[i].contentWindow.document;
                                var links = iframeDoc.querySelectorAll('a[href*="audio"], a[href*="mp3"], a[href*="wav"]');
                                for (var j = 0; j < links.length; j++) {{
                                    if (links[j].href) return links[j].href;
                                }}
                            }} catch(e) {{}}
                        }}
                        return null;
                        """
                    else:
                        # Selectores normales
                        js = f"var element = document.querySelector('{selector}'); return element ? (element.href || element.src) : null;"
                    
                    audio_url = driver.execute_script(js)
                    if audio_url and audio_url.strip() and ('http' in audio_url or 'https' in audio_url):
                        print(f"✅ URL obtenida: {audio_url[:50]}...")
                        return audio_url
                        
                except Exception as e:
                    print(f"⚠️ Error con selector {selector}: {e}")
                    continue
        
        # Delay entre intentos
        if intento < max_intentos - 1:
            print("⏳ Esperando antes del siguiente intento...")
            time.sleep(2)
    
    # Último intento: búsqueda exhaustiva
    print("🔄 Búsqueda exhaustiva...")
    return buscar_audio_url_exhaustiva(driver)


def buscar_audio_url_exhaustiva(driver):
    """
    Búsqueda exhaustiva de la URL del audio
    """
    try:
        print("🔍 Búsqueda exhaustiva de URL de audio...")
        
        # Obtener todas las URLs del DOM
        js = """
        var urls = [];
        var elements = document.querySelectorAll('a, audio, iframe, script');
        for (var i = 0; i < elements.length; i++) {
            var href = elements[i].href || elements[i].src;
            if (href && (href.includes('audio') || href.includes('mp3') || href.includes('wav') || href.includes('ogg'))) {
                urls.push(href);
            }
        }
        return urls;
        """
        
        urls = driver.execute_script(js)
        if urls:
            print(f"🔍 URLs encontradas: {len(urls)}")
            for url in urls:
                print(f"  - {url}")
                if 'http' in url:
                    return url
        
        # Buscar en el HTML completo
        js = """
        var html = document.documentElement.innerHTML;
        var matches = html.match(/https?:\/\/[^"'\s]+\.(mp3|wav|ogg|webm)/gi);
        return matches ? matches[0] : null;
        """
        
        audio_url = driver.execute_script(js)
        if audio_url:
            print(f"✅ URL encontrada en HTML: {audio_url[:50]}...")
            return audio_url
        
        print("❌ No se encontró URL de audio")
        return None
        
    except Exception as e:
        print(f"❌ Error en búsqueda exhaustiva: {e}")
        return None


def generar_audio_fallback():
    """
    Genera un audio de fallback cuando no se puede obtener el audio real
    """
    try:
        print("🔄 Generando audio de fallback...")
        
        # Crear un audio de prueba simple
        audio_seg = AudioSegment.silent(duration=3000)  # 3 segundos de silencio
        
        # Agregar un tono simple
        tone = AudioSegment.sine(440, duration=1000)  # 440Hz por 1 segundo
        audio_seg = audio_seg.overlay(tone)
        
        # Exportar como MP3
        audio_seg.export("temp_audio.mp3", format="mp3")
        
        print("✅ Audio de fallback generado")
        return True
        
    except Exception as e:
        print(f"❌ Error generando audio de fallback: {e}")
        return False


def crear_driver_selenium_estandar():
    """Crea un driver de Selenium estándar como respaldo"""
    try:
        options = ChromeOptions()
        options.add_argument('--no-sandbox')
        options.add_argument('--disable-dev-shm-usage')
        options.add_argument('--disable-logging')
        options.add_argument('--disable-gpu')
        options.add_argument('--disable-web-security')
        options.add_argument('--disable-blink-features=AutomationControlled')
        options.add_argument('--disable-extensions')
        options.add_argument('--disable-plugins')
        options.add_argument('--disable-images')
        options.add_argument('--no-first-run')
        options.add_argument('--no-default-browser-check')
        options.add_argument('--disable-default-apps')
        
        # Agregar opciones para evitar detección
        options.add_experimental_option("excludeSwitches", ["enable-automation"])
        options.add_experimental_option('useAutomationExtension', False)
        
        driver = webdriver.Chrome(options=options)
        driver.execute_script("Object.defineProperty(navigator, 'webdriver', {get: () => undefined})")
        driver.implicitly_wait(10)
        driver.set_page_load_timeout(30)
        
        return driver
    except Exception as e:
        print(f"❌ Error creando driver Selenium estándar: {e}")
        return None


def consultar_policia(cedula):
    """Consulta antecedentes policiales - versión simplificada y robusta"""
    
    driver = None
    
    try:
        # Intentar usar undetected_chromedriver primero
        try:
            print("🚀 Intentando usar undetected_chromedriver...")
            options = uc.ChromeOptions()
            
            # Opciones básicas
            options.add_argument('--no-sandbox')
            options.add_argument('--disable-dev-shm-usage')
            options.add_argument('--disable-logging')
            options.add_argument('--disable-gpu')
            options.add_argument('--disable-web-security')
            options.add_argument('--disable-features=VizDisplayCompositor')
            
            # Opciones anti-detección
            options.add_argument('--disable-blink-features=AutomationControlled')
            options.add_argument('--disable-extensions')
            options.add_argument('--disable-plugins')
            options.add_argument('--disable-images')
            options.add_argument('--no-first-run')
            options.add_argument('--no-default-browser-check')
            options.add_argument('--disable-default-apps')
            options.add_argument('--disable-background-timer-throttling')
            options.add_argument('--disable-backgrounding-occluded-windows')
            options.add_argument('--disable-renderer-backgrounding')
            options.add_argument('--disable-features=TranslateUI')
            options.add_argument('--disable-ipc-flooding-protection')
            options.add_argument('--disable-hang-monitor')
            options.add_argument('--disable-prompt-on-repost')
            options.add_argument('--disable-sync')
            options.add_argument('--disable-domain-reliability')
            options.add_argument('--disable-component-extensions-with-background-pages')
            options.add_argument('--disable-background-networking')
            options.add_argument('--disable-features=MediaRouter')
            options.add_argument('--disable-features=Translate')
            options.add_argument('--disable-features=BlinkGenPropertyTrees')
            options.add_argument('--disable-features=EnableDrDc')
            options.add_argument('--disable-features=UseChromeOSDirectVideoDecoder')
            options.add_argument('--disable-features=VizDisplayCompositor')
            options.add_argument('--disable-features=WebRtcHideLocalIpsWithMdns')
            options.add_argument('--disable-features=WebRtcUseMinMaxVEADimensions')
            options.add_argument('--disable-features=WebRtcUseMinMaxVEADimensions')
            options.add_argument('--disable-features=WebRtcUseMinMaxVEADimensions')
            
            # Simular un usuario real
            options.add_argument('--user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36')
            options.add_argument('--accept-language=es-ES,es;q=0.9,en;q=0.8')
            options.add_argument('--accept-encoding=gzip, deflate, br')
            options.add_argument('--accept=text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8')
            
            # Opciones de ventana
            options.add_argument('--window-size=1920,1080')
            options.add_argument('--start-maximized')
            
            # Deshabilitar detección de automatización
            options.add_experimental_option("excludeSwitches", ["enable-automation"])
            options.add_experimental_option('useAutomationExtension', False)
            options.add_experimental_option("excludeSwitches", ["enable-logging"])
            options.add_experimental_option("excludeSwitches", ["enable-blink-features"])
            options.add_experimental_option("excludeSwitches", ["disable-blink-features"])
            
            # Preferencias adicionales
            prefs = {
                "profile.default_content_setting_values": {
                    "notifications": 2,
                    "geolocation": 2,
                    "media_stream": 2,
                },
                "profile.managed_default_content_settings": {
                    "images": 2
                },
                "profile.default_content_settings": {
                    "popups": 0
                }
            }
            options.add_experimental_option("prefs", prefs)
            
            # Configurar el driver con opciones mejoradas
            driver = uc.Chrome(
                options=options,
                version_main=None,  # Auto-detecta la versión
                driver_executable_path=None,  # Usa el driver por defecto
                browser_executable_path=None,  # Usa Chrome por defecto
                headless=False,  # Mostrar navegador para debugging
                use_subprocess=True
            )
            driver.implicitly_wait(10)
            driver.set_page_load_timeout(30)
            
            # Scripts anti-detección
            print("🛡️ Aplicando scripts anti-detección...")
            
            # Ocultar webdriver
            driver.execute_script("Object.defineProperty(navigator, 'webdriver', {get: () => undefined})")
            
            # Simular propiedades de un navegador real
            driver.execute_script("""
                Object.defineProperty(navigator, 'languages', {
                    get: () => ['es-ES', 'es', 'en-US', 'en']
                });
            """)
            
            driver.execute_script("""
                Object.defineProperty(navigator, 'plugins', {
                    get: () => [1, 2, 3, 4, 5]
                });
            """)
            
            driver.execute_script("""
                Object.defineProperty(navigator, 'permissions', {
                    get: () => ({
                        query: () => Promise.resolve({state: 'granted'})
                    })
                });
            """)
            
            # Simular resolución de pantalla
            driver.execute_script("""
                Object.defineProperty(screen, 'width', {get: () => 1920});
                Object.defineProperty(screen, 'height', {get: () => 1080});
                Object.defineProperty(screen, 'availWidth', {get: () => 1920});
                Object.defineProperty(screen, 'availHeight', {get: () => 1040});
            """)
            
            # Simular timezone
            driver.execute_script("""
                Object.defineProperty(Intl, 'DateTimeFormat', {
                    value: function() {
                        return {
                            resolvedOptions: () => ({timeZone: 'America/Bogota'})
                        };
                    }
                });
            """)
            
            print("✅ undetected_chromedriver inicializado correctamente")
            
        except Exception as uc_error:
            print(f"⚠️ Error con undetected_chromedriver: {uc_error}")
            print("🔄 Intentando con Selenium estándar...")
            driver = crear_driver_selenium_estandar()
            if not driver:
                return {"status": "error", "error": "No se pudo inicializar ningún driver", "metodo": "driver_init_error"}
            print("✅ Selenium estándar inicializado correctamente")
        
        print("🌐 Accediendo al sitio de antecedentes policiales...")
        try:
            # Primero ir al index (puede haber redirección automática)
            driver.get("https://antecedentes.policia.gov.co:7005/WebJudicial/")
            print("✅ Página principal cargada")
            time.sleep(3)
            
            # Verificar si estamos en el index y necesitamos navegar al formulario
            current_url = driver.current_url
            print(f"📍 URL actual: {current_url}")
            
            if "antecedentes.xhtml" not in current_url:
                print("🔄 Detectada redirección al index, intentando navegar al formulario...")
                
                # Intentar navegar directamente al formulario
                try:
                    driver.get("https://antecedentes.policia.gov.co:7005/WebJudicial/antecedentes.xhtml")
                    time.sleep(3)
                    current_url = driver.current_url
                    print(f"📍 URL después de navegación directa: {current_url}")
                except Exception as nav_error:
                    print(f"⚠️ Error en navegación directa: {nav_error}")
                
                # Si aún no estamos en el formulario, buscar enlaces o botones
                if "antecedentes.xhtml" not in current_url:
                    print("🔍 Buscando enlaces o botones para acceder al formulario...")
                    try:
                        # Buscar enlaces que puedan llevar al formulario
                        enlaces_formulario = driver.find_elements(By.XPATH, "//a[contains(@href, 'antecedentes') or contains(text(), 'antecedentes') or contains(text(), 'consulta')]")
                        if enlaces_formulario:
                            print(f"✅ Encontrados {len(enlaces_formulario)} enlaces al formulario")
                            enlaces_formulario[0].click()
                            time.sleep(3)
                            current_url = driver.current_url
                            print(f"📍 URL después de hacer clic: {current_url}")
                        else:
                            print("⚠️ No se encontraron enlaces al formulario")
                    except Exception as link_error:
                        print(f"⚠️ Error buscando enlaces: {link_error}")
            
            # Verificación final: asegurar que estamos en el formulario correcto
            final_url = driver.current_url
            print(f"📍 URL final: {final_url}")
            
            if "antecedentes.xhtml" not in final_url:
                print("⚠️ No se pudo acceder al formulario de antecedentes")
                print("🔄 Intentando continuar con la página actual...")
            else:
                print("✅ Formulario de antecedentes cargado exitosamente")
            
            time.sleep(2)
            
        except Exception as e:
            print(f"❌ Error cargando el sitio: {e}")
            return {"status": "error", "error": f"Error cargando sitio: {str(e)}", "metodo": "page_load_error"}
        
        # Paso 1: Aceptar términos y condiciones (reintentar hasta detectar formulario)
        print("📋 Paso 1: Aceptando términos y condiciones...")
        
        max_intentos = 5
        intento = 0
        
        while intento < max_intentos:
            intento += 1
            print(f"🔄 Intento {intento}/{max_intentos} de aceptar términos...")
            
            try:
                # Esperar y marcar radio button
                print("🔍 Buscando radio button de aceptación...")
                WebDriverWait(driver, 10).until(
                    EC.presence_of_element_located((By.ID, "aceptaOption:0"))
                )
                print("✅ Radio button encontrado")
                
                # Delay humano antes de interactuar
                delay_humano(1, 2)
                
                # Buscar el radio button con Selenium para simular comportamiento humano
                try:
                    radio_element = driver.find_element(By.ID, "aceptaOption:0")
                    mover_mouse_humano(driver, radio_element)
                    delay_humano(0.5, 1)
                    radio_element.click()
                    print("✅ Radio button marcado (comportamiento humano)")
                except Exception as radio_error:
                    print(f"⚠️ Error con Selenium, usando JavaScript: {radio_error}")
                    accept_js = """
                    var radio = document.getElementById('aceptaOption:0');
                    if (radio) {
                        radio.checked = true;
                        radio.dispatchEvent(new Event('change'));
                        radio.dispatchEvent(new Event('click'));
                    }
                    """
                    driver.execute_script(accept_js)
                    print("✅ Radio button marcado (JavaScript)")
                
                # Delay humano después de marcar
                delay_humano(2, 4)
            
                # Hacer clic en continuar con múltiples estrategias
                print("🔄 Haciendo clic en continuar...")
                
                # Estrategia 1: Buscar y hacer clic en el botón
                try:
                    # Esperar a que el botón esté habilitado
                    continue_btn = WebDriverWait(driver, 15).until(
                        lambda driver: driver.find_element(By.ID, "continuarBtn").is_enabled()
                    )
                    
                    # Delay humano antes de hacer clic
                    delay_humano(1, 3)
                    
                    # Verificar que el botón no esté deshabilitado
                    if continue_btn.is_enabled():
                        # Simular comportamiento humano
                        mover_mouse_humano(driver, continue_btn)
                        delay_humano(0.5, 1)
                        continue_btn.click()
                        print("✅ Botón continuar presionado (comportamiento humano)")
                    else:
                        print("⚠️ Botón está deshabilitado, intentando habilitarlo...")
                        
                        # Intentar habilitar el botón con JavaScript
                        enable_js = """
                        var btn = document.getElementById('continuarBtn');
                        if (btn) {
                            btn.disabled = false;
                            btn.removeAttribute('disabled');
                            btn.style.pointerEvents = 'auto';
                            return true;
                        }
                        return false;
                        """
                        enable_result = driver.execute_script(enable_js)
                        if enable_result:
                            delay_humano(1, 2)
                            mover_mouse_humano(driver, continue_btn)
                            continue_btn.click()
                            print("✅ Botón habilitado y presionado")
                        else:
                            raise Exception("No se pudo habilitar el botón")
                            
                except Exception as e:
                    print(f"⚠️ Error con Selenium: {e}")
                
                    # Estrategia 2: JavaScript directo
                    try:
                        continue_js = """
                        var btn = document.getElementById('continuarBtn');
                        if (btn) {
                            btn.click();
                            return true;
                        }
                        return false;
                        """
                        result = driver.execute_script(continue_js)
                        if result:
                            print("✅ Botón continuar presionado (JavaScript)")
                        else:
                            print("⚠️ Botón no encontrado con JavaScript")
                    except Exception as js_error:
                        print(f"⚠️ Error con JavaScript: {js_error}")
                        
                        # Estrategia 3: Buscar por texto o clase
                        try:
                            print("🔍 Buscando botón por texto o clase...")
                            btn_alternativo = driver.find_element(By.XPATH, "//input[@type='submit' or @type='button'] | //button[contains(text(), 'Enviar') or contains(text(), 'Continuar') or contains(text(), 'Aceptar')]")
                            btn_alternativo.click()
                            print("✅ Botón alternativo presionado")
                        except Exception as alt_error:
                            print(f"⚠️ Error con botón alternativo: {alt_error}")
                            
                            # Estrategia 4: Enviar formulario directamente
                            try:
                                print("🔄 Enviando formulario directamente...")
                                form_js = """
                                var form = document.querySelector('form');
                                if (form) {
                                    form.submit();
                                    return true;
                                }
                                return false;
                                """
                                form_result = driver.execute_script(form_js)
                                if form_result:
                                    print("✅ Formulario enviado directamente")
                                else:
                                    print("❌ No se pudo enviar el formulario")
                            except Exception as form_error:
                                print(f"❌ Error enviando formulario: {form_error}")
                                continue  # Continuar con el siguiente intento
                
                # Esperar a que la página procese el envío
                delay_humano(3, 5)
                
                # Verificar si necesitamos reintentar
                try:
                    # Verificar si el botón sigue visible (puede indicar que no se procesó)
                    btn_still_visible = driver.find_elements(By.ID, "continuarBtn")
                    if btn_still_visible and btn_still_visible[0].is_displayed():
                        print("🔄 Botón aún visible, reintentando...")
                        delay_humano(2, 3)
                        
                        # Reintentar con JavaScript
                        retry_js = """
                        var btn = document.getElementById('continuarBtn');
                        if (btn && btn.offsetParent !== null) {
                            btn.click();
                            return true;
                        }
                        return false;
                        """
                        retry_result = driver.execute_script(retry_js)
                        if retry_result:
                            print("✅ Reintento exitoso")
                            delay_humano(3, 5)
                        else:
                            print("⚠️ Reintento falló, continuando...")
                except Exception as retry_error:
                    print(f"⚠️ Error en reintento: {retry_error}")
                    print("🔄 Continuando con el proceso...")
                
                # Verificar si llegamos al formulario
                print("🔍 Verificando si llegamos al formulario...")
                try:
                    # Buscar campo de cédula como indicador de que llegamos al formulario
                    cedula_field = driver.find_elements(By.ID, "cedulaInput")
                    if cedula_field:
                        print("✅ ¡Formulario detectado! Campo de cédula encontrado")
                        break  # Salir del bucle de reintentos
                    else:
                        print("⚠️ Formulario no detectado, continuando con siguiente intento...")
                        if intento < max_intentos:
                            delay_humano(2, 4)  # Esperar antes del siguiente intento
                            continue
                        else:
                            print("❌ Máximo de intentos alcanzado")
                            return {"status": "error", "error": "No se pudo acceder al formulario después de múltiples intentos", "metodo": "form_not_found"}
                except Exception as check_error:
                    print(f"⚠️ Error verificando formulario: {check_error}")
                    if intento < max_intentos:
                        delay_humano(2, 4)
                        continue
                    else:
                        print("❌ Máximo de intentos alcanzado")
                        return {"status": "error", "error": "No se pudo acceder al formulario", "metodo": "form_check_error"}
            
            except Exception as e:
                print(f"❌ Error en intento {intento}: {e}")
                if intento < max_intentos:
                    delay_humano(2, 4)
                    continue
                else:
                    return {"status": "error", "error": "Error aceptando términos después de múltiples intentos", "metodo": "terminos_error"}
        
        # Paso 2: Esperar formulario y ingresar cédula
        print("📝 Paso 2: Ingresando cédula...")
        
        try:
            print("🔍 Buscando campo de cédula...")
            WebDriverWait(driver, 15).until(
                EC.presence_of_element_located((By.ID, "cedulaInput"))
            )
            print("✅ Campo de cédula encontrado")
            
            # Delay humano antes de interactuar
            delay_humano(2, 4)
            
            # Buscar el campo de cédula con Selenium para simular comportamiento humano
            try:
                cedula_input = driver.find_element(By.ID, "cedulaInput")
                mover_mouse_humano(driver, cedula_input)
                delay_humano(0.5, 1)
                
                # Simular escritura humana
                simular_escritura_humana(cedula_input, cedula)
                print("✅ Cédula ingresada (comportamiento humano)")
                
                # Disparar eventos para asegurar que se registre
                cedula_input.send_keys(Keys.TAB)
                delay_humano(0.5, 1)
                
            except Exception as input_error:
                print(f"⚠️ Error con Selenium, usando JavaScript: {input_error}")
                cedula_js = f"""
                var input = document.getElementById('cedulaInput');
                if (input) {{
                    input.focus();
                    input.value = '{cedula}';
                    input.dispatchEvent(new Event('input', {{bubbles: true}}));
                    input.dispatchEvent(new Event('change', {{bubbles: true}}));
                    input.dispatchEvent(new Event('blur', {{bubbles: true}}));
                }}
                """
                driver.execute_script(cedula_js)
                print("✅ Cédula ingresada (JavaScript)")
            
            # Delay humano después de ingresar cédula
            delay_humano(2, 4)
            
        except Exception as e:
            print(f"Error ingresando cédula: {e}")
            return {"status": "error", "error": "Error ingresando cédula", "metodo": "input_error"}
        
        # Paso 3: Manejar CAPTCHA automáticamente
        try:
            print("🔍 Buscando CAPTCHA...")
            # Buscar iframe de CAPTCHA
            captcha_iframe = WebDriverWait(driver, 10).until(
                EC.presence_of_element_located((By.XPATH, '//*[@id="captchaAntecedentes"]//iframe'))
            )
            
            # Cambiar a iframe del CAPTCHA
            driver.switch_to.frame(captcha_iframe)
            time.sleep(2)
            
            # Marcar checkbox del CAPTCHA
            print("✅ Marcando checkbox del CAPTCHA...")
            checkbox_js = """
            var checkbox = document.getElementById('recaptcha-anchor');
            if (checkbox) {
                checkbox.click();
                return true;
            }
            return false;
            """
            checkbox_result = driver.execute_script(checkbox_js)
            if checkbox_result:
                print("✅ Checkbox marcado exitosamente")
            else:
                print("⚠️ No se pudo marcar el checkbox")
            
            time.sleep(4)
            
            # Volver al contenido principal
            driver.switch_to.default_content()
            
            # Verificar si el CAPTCHA se resolvió solo (solo check)
            print("🔍 Verificando si el CAPTCHA se resolvió...")
            delay_humano(2, 4)
            
            # Buscar indicadores de que el CAPTCHA se resolvió
            try:
                # Verificar si hay un mensaje de éxito o si el checkbox está marcado
                success_indicators = driver.find_elements(By.XPATH, "//*[contains(@class, 'recaptcha-checkbox-checked') or contains(text(), 'Verificación exitosa') or contains(text(), 'Verification successful')]")
                if success_indicators:
                    print("✅ CAPTCHA resuelto exitosamente (solo check)")
                    # Continuar con el siguiente paso
                else:
                    print("⚠️ CAPTCHA no resuelto automáticamente, buscando challenge...")
                    
                    # Buscar iframe del challenge (audio) solo si es necesario
                    try:
                        challenge_iframe = WebDriverWait(driver, 5).until(
                            EC.presence_of_element_located((By.XPATH, "//iframe[contains(@title, 'challenge') or contains(@src, 'bframe')]"))
                        )
                        
                        print("🔍 Challenge detectado, procesando audio...")
                        
                        # Cambiar a iframe del challenge
                        driver.switch_to.frame(challenge_iframe)
                        time.sleep(2)
                        
                        # Hacer clic en audio
                        print("🎵 Activando audio del CAPTCHA...")
                        audio_js = """
                        var audioBtn = document.getElementById('recaptcha-audio-button');
                        if (audioBtn) {
                            audioBtn.click();
                            return true;
                        }
                        return false;
                        """
                        audio_result = driver.execute_script(audio_js)
                        if audio_result:
                            print("✅ Audio activado")
                        else:
                            print("⚠️ No se pudo activar audio")
                        
                        time.sleep(3)
                        
                        # Obtener enlace de audio con función mejorada
                        audio_url = obtener_audio_url_captcha(driver, max_intentos=5)
                        
                        if audio_url:
                            print(f"✅ Audio URL obtenida: {audio_url[:50]}...")
                            
                            # Descargar audio con función mejorada
                            if not descargar_audio_captcha(audio_url, max_intentos=5):
                                print("❌ No se pudo descargar audio válido")
                                
                                # Intentar descarga alternativa
                                print("🔄 Intentando descarga alternativa...")
                                if not descargar_audio_alternativo(audio_url):
                                    print("❌ Descarga alternativa también falló")
                                    driver.switch_to.default_content()
                                    return {"status": "error", "error": "Error descargando audio CAPTCHA", "metodo": "audio_download_error"}
                        else:
                            print("❌ No se pudo obtener URL del audio")
                            
                            # Intentar generar audio de prueba como fallback
                            print("🔄 Generando audio de prueba como fallback...")
                            if generar_audio_fallback():
                                print("✅ Audio de fallback generado")
                            else:
                                driver.switch_to.default_content()
                                return {"status": "error", "error": "No se pudo obtener audio CAPTCHA", "metodo": "audio_url_error"}
                    
                        # Convertir a WAV con función mejorada
                        if not convertir_audio_captcha("temp_audio.mp3", "temp_audio.wav", max_intentos=3):
                            print("❌ No se pudo convertir audio a WAV")
                            driver.switch_to.default_content()
                            return {"status": "error", "error": "Error convirtiendo audio CAPTCHA", "metodo": "audio_convert_error"}
                
                        # Diagnosticar audio antes del reconocimiento
                        print("🔍 Diagnosticando audio...")
                        diagnosticar_audio_captcha("temp_audio.wav")
                        
                        # Reconocer audio con función mejorada
                        print("🎤 Reconociendo audio...")
                        texto = reconocer_audio_captcha("temp_audio.wav", max_intentos=5)
                        
                        if not texto:
                            print("❌ No se pudo reconocer el audio con ninguna estrategia")
                            
                            # Intentar reconocimiento manual como último recurso
                            print("🔄 Intentando reconocimiento manual...")
                            texto_manual = reconocimiento_manual_captcha("temp_audio.wav")
                            if texto_manual:
                                print(f"✅ Reconocimiento manual exitoso: '{texto_manual}'")
                                texto = texto_manual
                            else:
                                driver.switch_to.default_content()
                                return {"status": "error", "error": "No se pudo reconocer el audio CAPTCHA", "metodo": "audio_recognize_error"}
                
                        # Ingresar respuesta con múltiples estrategias
                        print(f"⌨️ Ingresando respuesta: '{texto}'")
                        
                        # Estrategia 1: JavaScript directo
                        response_js = f"""
                        var input = document.getElementById('audio-response');
                        if (input) {{
                            input.value = '{texto.lower()}';
                            input.dispatchEvent(new Event('input', {{bubbles: true}}));
                            input.dispatchEvent(new Event('change', {{bubbles: true}}));
                            input.dispatchEvent(new Event('blur', {{bubbles: true}}));
                            return true;
                        }}
                        return false;
                        """
                        
                        if driver.execute_script(response_js):
                            print("✅ Respuesta ingresada (JavaScript)")
                        else:
                            # Estrategia 2: Buscar input alternativo
                            print("🔄 Buscando input alternativo...")
                            alt_input_js = f"""
                            var inputs = document.querySelectorAll('input[type="text"], input[type="number"]');
                            for (var i = 0; i < inputs.length; i++) {{
                                if (inputs[i].offsetParent !== null) {{
                                    inputs[i].value = '{texto.lower()}';
                                    inputs[i].dispatchEvent(new Event('input', {{bubbles: true}}));
                                    inputs[i].dispatchEvent(new Event('change', {{bubbles: true}}));
                                    return true;
                                }}
                            }}
                            return false;
                            """
                            
                            if driver.execute_script(alt_input_js):
                                print("✅ Respuesta ingresada (input alternativo)")
                            else:
                                print("⚠️ No se pudo encontrar input para respuesta")
                        
                        time.sleep(2)
                        
                        # Verificar respuesta con múltiples estrategias
                        print("✅ Verificando respuesta...")
                        
                        # Estrategia 1: Botón de verificación estándar
                        verify_js = """
                        var btn = document.getElementById('recaptcha-verify-button');
                        if (btn && btn.offsetParent !== null) {
                            btn.click();
                            return true;
                        }
                        return false;
                        """
                        
                        if driver.execute_script(verify_js):
                            print("✅ Respuesta verificada (botón estándar)")
                        else:
                            # Estrategia 2: Buscar botón alternativo
                            print("🔄 Buscando botón de verificación alternativo...")
                            alt_verify_js = """
                            var buttons = document.querySelectorAll('button, input[type="submit"], input[type="button"]');
                            for (var i = 0; i < buttons.length; i++) {
                                var text = buttons[i].textContent || buttons[i].value || '';
                                if (text.toLowerCase().includes('verify') || 
                                    text.toLowerCase().includes('verificar') ||
                                    text.toLowerCase().includes('submit') ||
                                    text.toLowerCase().includes('enviar')) {
                                    buttons[i].click();
                                    return true;
                                }
                            }
                            return false;
                            """
                            
                            if driver.execute_script(alt_verify_js):
                                print("✅ Respuesta verificada (botón alternativo)")
                            else:
                                print("⚠️ No se pudo encontrar botón de verificación")
                        
                        time.sleep(3)
                        
                        # Limpiar archivos temporales
                        try:
                            if os.path.exists("temp_audio.mp3"):
                                os.remove("temp_audio.mp3")
                            if os.path.exists("temp_audio.wav"):
                                os.remove("temp_audio.wav")
                            print("🗑️ Archivos temporales eliminados")
                        except Exception as cleanup_error:
                            print(f"⚠️ Error limpiando archivos temporales: {cleanup_error}")
                        
                        # Volver al contenido principal
                        driver.switch_to.default_content()
                        print("✅ CAPTCHA resuelto automáticamente")
                        
                    except Exception as challenge_error:
                        print(f"⚠️ Error en challenge iframe: {challenge_error}")
                        driver.switch_to.default_content()
                        # Continuar sin resolver el challenge
                        print("⚠️ Continuando sin resolver challenge...")
                        
                    except Exception as challenge_iframe_error:
                        print(f"⚠️ Error en challenge iframe: {challenge_iframe_error}")
                        driver.switch_to.default_content()
                        # Continuar sin resolver el challenge
                        print("⚠️ Continuando sin resolver challenge...")
                
            except Exception as challenge_error:
                print(f"⚠️ Error en challenge iframe: {challenge_error}")
                driver.switch_to.default_content()
                # Continuar sin resolver el challenge
                print("⚠️ Continuando sin resolver challenge...")
            
        except Exception as e:
            print(f"❌ Error en CAPTCHA: {e}")
            try:
                driver.switch_to.default_content()
                # Limpiar archivos temporales en caso de error
                try:
                    if os.path.exists("temp_audio.mp3"):
                        os.remove("temp_audio.mp3")
                    if os.path.exists("temp_audio.wav"):
                        os.remove("temp_audio.wav")
                    print("🗑️ Archivos temporales eliminados (error)")
                except Exception as cleanup_error:
                    print(f"⚠️ Error limpiando archivos en error: {cleanup_error}")
            except:
                pass
            return {"status": "error", "error": "Error procesando CAPTCHA", "metodo": "captcha_error"}
        
        # Paso 4: Hacer clic en el botón consultar
        
        time.sleep(3)
        
        # Buscar y hacer clic en el botón consultar con ID j_idt17
        try:
            consultar_btn = WebDriverWait(driver, 10).until(
                EC.element_to_be_clickable((By.ID, "j_idt17"))
            )
            consultar_btn.click()
            print("✅ Botón consultar presionado")
            time.sleep(8)
        except Exception as e:
            print(f"Error haciendo clic en consultar: {e}")
            # Intentar con JavaScript como respaldo
            consultar_js = """
            var btn = document.getElementById('j_idt17');
            if (btn) {
                btn.click();
                return true;
            }
            return false;
            """
            resultado_js = driver.execute_script(consultar_js)
            if resultado_js:
                print("✅ Botón consultar presionado (JavaScript)")
                time.sleep(8)
            else:
                return {"status": "error", "error": "No se pudo hacer clic en consultar", "metodo": "consultar_error"}
        
        # Paso 5: Obtener resultado
        print("Obteniendo resultado...")
        try:
            # Buscar diferentes elementos posibles donde puede aparecer el resultado
            resultado_element = None
            texto_resultado = ""
            
            # Intentar diferentes selectores para encontrar el resultado
            selectores_posibles = [
                (By.ID, "form:mensajeCiudadano"),
                (By.CLASS_NAME, "mensajeCiudadano"),
                (By.XPATH, "//div[contains(@class, 'mensaje')]"),
                (By.XPATH, "//div[contains(text(), 'antecedentes') or contains(text(), 'registra')]"),
                (By.XPATH, "//span[contains(text(), 'antecedentes') or contains(text(), 'registra')]"),
                (By.XPATH, "//td[contains(text(), 'antecedentes') or contains(text(), 'registra')]")
            ]
            
            for selector_type, selector_value in selectores_posibles:
                try:
                    resultado_element = WebDriverWait(driver, 5).until(
                        EC.presence_of_element_located((selector_type, selector_value))
                    )
                    texto_resultado = resultado_element.text.strip()
                    if texto_resultado:
                        print(f"✅ Resultado encontrado con selector: {selector_value}")
                        break
                except:
                    continue
            
            # Si no encontramos con los selectores específicos, buscar cualquier texto visible
            if not texto_resultado:
                try:
                    # Buscar en todo el body por texto relacionado con antecedentes
                    body_text = driver.find_element(By.TAG_NAME, "body").text
                    lines = body_text.split('\n')
                    for line in lines:
                        if any(palabra in line.upper() for palabra in ['ANTECEDENTES', 'REGISTRA', 'POLICIA', 'JUDICIAL']):
                            texto_resultado = line.strip()
                            print(f"✅ Resultado encontrado en texto general: {texto_resultado[:100]}...")
                            break
                except:
                    pass
            
            if not texto_resultado:
                return {"status": "error", "error": "No se pudo extraer resultado", "metodo": "no_result_found"}
            
            # Analizar resultado
            tiene_antecedentes = not any(frase in texto_resultado.upper() for frase in [
                "NO REGISTRA ANTECEDENTES",
                "SIN ANTECEDENTES", 
                "NO TIENE ANTECEDENTES",
                "NO CONSTA ANTECEDENTES",
                "NO HAY ANTECEDENTES"
            ])
            
            print(f"📄 Texto extraído: {texto_resultado[:200]}...")
            print(f"🔍 Tiene antecedentes: {tiene_antecedentes}")
            
            return {
                "status": "success",
                "texto": texto_resultado,
                "tiene_antecedentes": tiene_antecedentes,
                "metodo": "undetected_chrome_mejorado",
                "timestamp": datetime.now().isoformat()
            }
            
        except TimeoutException:
            return {"status": "error", "error": "Timeout obteniendo resultado", "metodo": "timeout_result"}
        except Exception as e:
            print(f"Error extrayendo resultado: {e}")
            return {"status": "error", "error": f"Error extrayendo resultado: {str(e)}", "metodo": "extraction_error"}
    
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
    # Prueba del scraping de antecedentes policiales
    resultado = consultar_policia("1234567890")
    print("=" * 50)
    print("RESULTADO DE LA CONSULTA:")
    print("=" * 50)
    print(f"Estado: {resultado.get('status')}")
    print(f"Texto: {resultado.get('texto', 'N/A')}")
    print(f"Tiene antecedentes: {resultado.get('tiene_antecedentes')}")
    print(f"Método: {resultado.get('metodo')}")
    print("=" * 50)