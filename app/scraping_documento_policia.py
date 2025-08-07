from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import Select

def antecedentes_judiciales(tipo_doc, numero_doc, primer_apellido, primer_nombre, headless=True):
    """
    Consulta antecedentes judiciales en la página de la Policía Nacional de Colombia.
    Requiere resolver el captcha manualmente si headless=False.
    """
    options = Options()
    if headless:
        options.add_argument("--headless")
    options.add_argument("--disable-gpu")
    options.add_argument("--window-size=1920,1080")
    options.add_argument("--disable-blink-features=AutomationControlled")
    options.add_experimental_option("excludeSwitches", ["enable-automation"])
    options.add_experimental_option('useAutomationExtension', False)
    
    service = Service("C:/chromedriver/chromedriver-win64/chromedriver.exe")
    driver = webdriver.Chrome(options=options, service=service)
    
    # Ocultar que es un webdriver automatizado
    driver.execute_script("Object.defineProperty(navigator, 'webdriver', {get: () => undefined})")
    
    resultado = {}
    
    try:
        driver.get('https://antecedentes.policia.gov.co:7005/WebJudicial/')
        wait = WebDriverWait(driver, 20)

        # Selecciona el tipo de documento
        sel_tipo_doc = wait.until(EC.presence_of_element_located((By.ID, "cbotipodocumento")))
        select = Select(sel_tipo_doc)
        
        # Buscar la opción que contenga el tipo de documento
        for option in select.options:
            if tipo_doc.lower() in option.text.lower() or "cédula" in option.text.lower():
                select.select_by_visible_text(option.text)
                break

        # Llena los campos
        campo_documento = wait.until(EC.presence_of_element_located((By.ID, "NoDocumento")))
        campo_documento.clear()
        campo_documento.send_keys(numero_doc)
        
        campo_nombre = wait.until(EC.presence_of_element_located((By.ID, "PrimerNombre")))
        campo_nombre.clear()
        campo_nombre.send_keys(primer_nombre)
        
        campo_apellido = wait.until(EC.presence_of_element_located((By.ID, "PrimerApellido")))
        campo_apellido.clear()
        campo_apellido.send_keys(primer_apellido)

        # Captcha manual si no es headless
        if not headless:
            input("Resuelve el captcha en el navegador y presiona Enter para continuar...")

        # Enviar el formulario
        btn = wait.until(EC.element_to_be_clickable((By.ID, "btnConsultar")))
        driver.execute_script("arguments[0].click();", btn)

        # Esperar por el resultado
        try:
            # Esperar a que aparezca el mensaje de resultado
            mensaje_elemento = WebDriverWait(driver, 15).until(
                EC.any_of(
                    EC.visibility_of_element_located((By.ID, "mensaje")),
                    EC.visibility_of_element_located((By.XPATH, "//*[contains(text(), 'no registra antecedentes')]")),
                    EC.visibility_of_element_located((By.XPATH, "//*[contains(text(), 'SI registra antecedentes')]")),
                    EC.visibility_of_element_located((By.XPATH, "//*[contains(text(), 'No se encontró')]")),
                    EC.visibility_of_element_located((By.CLASS_NAME, "alert"))
                )
            )
            
            # Intentar capturar el mensaje principal
            mensaje_texto = ""
            try:
                mensaje_elemento = driver.find_element(By.ID, "mensaje")
                mensaje_texto = mensaje_elemento.text.strip()
            except:
                # Buscar en otros posibles contenedores
                try:
                    mensaje_elemento = driver.find_element(By.XPATH, "//*[contains(text(), 'registra antecedentes') or contains(text(), 'No se encontró')]")
                    mensaje_texto = mensaje_elemento.text.strip()
                except:
                    mensaje_texto = "No se pudo extraer el mensaje de resultado"
            
            # Determinar el estado basado en el mensaje
            if "no registra antecedentes" in mensaje_texto.lower():
                estado = "SIN_ANTECEDENTES"
                tipo_resultado = "LIMPIO"
            elif "si registra antecedentes" in mensaje_texto.lower():
                estado = "CON_ANTECEDENTES" 
                tipo_resultado = "CON_REGISTROS"
            elif "no se encontró" in mensaje_texto.lower():
                estado = "NO_ENCONTRADO"
                tipo_resultado = "ERROR_BUSQUEDA"
            else:
                estado = "RESULTADO_INCIERTO"
                tipo_resultado = "VERIFICAR_MANUAL"
            
            # Buscar información adicional
            info_adicional = ""
            try:
                # Buscar elementos con información adicional
                elementos_info = driver.find_elements(By.XPATH, "//div[@class='alert']//p | //div[@id='mensaje']//p")
                info_adicional = " ".join([elem.text.strip() for elem in elementos_info if elem.text.strip()])
            except:
                pass
            
            resultado = {
                "numero_documento": numero_doc,
                "primer_nombre": primer_nombre,
                "primer_apellido": primer_apellido,
                "mensaje_principal": mensaje_texto,
                "informacion_adicional": info_adicional,
                "estado_antecedentes": estado,
                "tipo_resultado": tipo_resultado,
                "tiene_antecedentes": estado == "CON_ANTECEDENTES",
                "consulta_exitosa": True
            }
            
        except Exception as e:
            resultado = {
                "numero_documento": numero_doc,
                "primer_nombre": primer_nombre, 
                "primer_apellido": primer_apellido,
                "mensaje_principal": "No se pudo completar la consulta debido a limitaciones técnicas",
                "informacion_adicional": f"La consulta requiere resolución manual de captcha o verificación adicional. Error: {str(e)}",
                "estado_antecedentes": "ERROR_CONSULTA",
                "tipo_resultado": "REQUIERE_VERIFICACION_MANUAL",
                "consulta_exitosa": False,
                "error_tecnico": str(e)
            }
            
    except Exception as e:
        resultado = {
            "error": f"Error en la consulta de antecedentes: {str(e)}",
            "numero_documento": numero_doc,
            "estado_antecedentes": "ERROR_SISTEMA"
        }
    finally:
        try:
            driver.quit()
        except:
            pass
    
    return resultado