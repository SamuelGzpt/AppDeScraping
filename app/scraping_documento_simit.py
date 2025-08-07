from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

def scrape_simit_por_documento(numero_doc, headless=True):
    """
    Consulta comparendos/multas en el SIMIT usando Selenium.
    numero_doc: str (puede ser cédula, placa, comparendo o resolución)
    headless: bool (True para no mostrar el navegador)
    """
    options = Options()
    if headless:
        options.add_argument("--headless")
    options.add_argument("--disable-gpu")
    options.add_argument("--window-size=1920,1080")
    service = Service("C:/chromedriver/chromedriver-win64/chromedriver.exe")
    driver = webdriver.Chrome(options=options, service=service)
    resultado = {}
    
    try:
        driver.get("https://www.fcm.org.co/simit/#/home-public")
        wait = WebDriverWait(driver, 15)

        # Espera el campo de texto único
        campo = wait.until(EC.visibility_of_element_located(
            (By.XPATH, "//input[@placeholder='Ingrese su número de documento, placa, comparendo o resolución']")
        ))
        campo.clear()
        campo.send_keys(numero_doc)

        # Haz clic en el botón "Consultar"
        boton = wait.until(EC.element_to_be_clickable(
            (By.XPATH, "//button[contains(., 'Consultar')]")
        ))
        boton.click()

        # Espera a que aparezcan los resultados
        wait.until(
            EC.any_of(
                EC.visibility_of_element_located((By.XPATH, "//table//tbody")),
                EC.visibility_of_element_located((By.XPATH, "//*[contains(text(), 'No tienes comparendos')]")),
                EC.visibility_of_element_located((By.XPATH, "//*[contains(text(), 'no posee a la fecha')]")),
                EC.visibility_of_element_located((By.XPATH, "//h3[contains(@class, 'text-secondary')]"))
            )
        )

        # Buscar mensaje de "sin multas" primero
        try:
            # Buscar el mensaje principal
            mensaje_elemento = driver.find_element(By.XPATH, "//h3[contains(@class, 'text-secondary') and contains(text(), 'No tienes comparendos')]")
            mensaje_principal = mensaje_elemento.text.strip()
            
            # Buscar el párrafo con detalles
            try:
                parrafo_detalle = driver.find_element(By.XPATH, "//p[contains(text(), 'no posee a la fecha')]")
                detalle_texto = parrafo_detalle.text.strip()
            except:
                detalle_texto = f"El ciudadano identificado con el número de documento {numero_doc}, no posee a la fecha pendientes de pago."
            
            # Buscar mensaje adicional
            try:
                parrafo_adicional = driver.find_element(By.XPATH, "//p[contains(text(), 'Revisa con tu número')]")
                mensaje_adicional = parrafo_adicional.text.strip()
            except:
                mensaje_adicional = "Revisa con tu número de identificación en las Secretarías de Tránsito."
            
            resultado = {
                "numero_documento": numero_doc,
                "multas_encontradas": False,
                "mensaje_completo": mensaje_principal,
                "detalle_consulta": detalle_texto,
                "recomendacion": mensaje_adicional,
                "comparendos": [],
                "estado_consulta": "SIN_MULTAS"
            }
            
        except:
            # Si no encuentra mensaje de sin multas, buscar tabla de resultados
            try:
                rows = driver.find_elements(By.XPATH, "//table//tbody/tr")
                comparendos = []
                
                for row in rows:
                    celdas = row.find_elements(By.TAG_NAME, "td")
                    if len(celdas) >= 5:
                        comparendo = {
                            "fecha": celdas[0].text.strip(),
                            "numero": celdas[1].text.strip(),
                            "secretaria": celdas[2].text.strip(),
                            "valor": celdas[3].text.strip(),
                            "estado": celdas[4].text.strip()
                        }
                        comparendos.append(comparendo)
                
                if comparendos:
                    resultado = {
                        "numero_documento": numero_doc,
                        "multas_encontradas": True,
                        "comparendos": comparendos,
                        "total_multas": len(comparendos),
                        "estado_consulta": "CON_MULTAS"
                    }
                else:
                    # No hay tabla pero tampoco mensaje de sin multas
                    resultado = {
                        "numero_documento": numero_doc,
                        "multas_encontradas": False,
                        "mensaje_completo": "Consulta realizada sin resultados específicos",
                        "comparendos": [],
                        "estado_consulta": "SIN_RESULTADOS"
                    }
                    
            except Exception as e:
                resultado = {
                    "numero_documento": numero_doc,
                    "multas_encontradas": False,
                    "error": f"Error al procesar resultados: {str(e)}",
                    "estado_consulta": "ERROR"
                }

    except Exception as e:
        resultado = {"error": f"Error en la consulta SIMIT: {str(e)}"}
    finally:
        driver.quit()
    
    return resultado