# test_estrategias_captcha.py
import time
from estrategia_captcha import (
    consultar_policia_estrategia_humana,
    consultar_policia_con_proxy_rotacion,
    consultar_policia_bypass_captcha,
    consultar_policia_session_previa,
    detectar_tipo_captcha
)

def test_todas_estrategias(cedula_prueba):
    """
    Prueba todas las estrategias para ver cuál funciona mejor
    """
    print("🧪 PROBANDO TODAS LAS ESTRATEGIAS ANTI-CAPTCHA")
    print("="*60)
    
    estrategias = [
        {
            "nombre": "🎭 Comportamiento Humano",
            "funcion": lambda: consultar_policia_estrategia_humana(cedula_prueba, max_intentos=1),
            "descripcion": "Simula movimientos y tiempos humanos"
        },
        {
            "nombre": "🔄 Rotación User-Agent", 
            "funcion": lambda: consultar_policia_con_proxy_rotacion(cedula_prueba),
            "descripcion": "Cambia User-Agent para parecer diferente navegador"
        },
        {
            "nombre": "🎯 Bypass Token",
            "funcion": lambda: consultar_policia_bypass_captcha(cedula_prueba),
            "descripcion": "Inyecta token válido directamente"
        },
        {
            "nombre": "💾 Sesión Previa",
            "funcion": lambda: consultar_policia_session_previa(cedula_prueba),
            "descripcion": "Usa historial de navegador para parecer confiable"
        }
    ]
    
    resultados = []
    
    for i, estrategia in enumerate(estrategias, 1):
        print(f"\n{i}. {estrategia['nombre']}")
        print(f"   📝 {estrategia['descripcion']}")
        print("   🚀 Ejecutando...")
        
        try:
            resultado = estrategia["funcion"]()
            
            if resultado and "error" not in resultado:
                print(f"   ✅ ¡ÉXITO! - {estrategia['nombre']}")
                print(f"   📊 Tiene antecedentes: {resultado.get('tiene_antecedentes', 'N/A')}")
                resultados.append({
                    "estrategia": estrategia["nombre"],
                    "exito": True,
                    "resultado": resultado
                })
            else:
                error_msg = resultado.get("error", "Error desconocido") if resultado else "Sin respuesta"
                print(f"   ❌ FALLÓ - {error_msg}")
                resultados.append({
                    "estrategia": estrategia["nombre"],
                    "exito": False,
                    "error": error_msg
                })
                
        except Exception as e:
            print(f"   💥 EXCEPCIÓN - {str(e)}")
            resultados.append({
                "estrategia": estrategia["nombre"],
                "exito": False,
                "error": str(e)
            })
        
        print("   ⏳ Esperando antes del siguiente intento...")
        time.sleep(10)  # Pausa entre estrategias
    
    # Resumen final
    print("\n" + "="*60)
    print("📊 RESUMEN DE RESULTADOS")
    print("="*60)
    
    exitosas = [r for r in resultados if r["exito"]]
    fallidas = [r for r in resultados if not r["exito"]]
    
    print(f"✅ Estrategias exitosas: {len(exitosas)}")
    print(f"❌ Estrategias fallidas: {len(fallidas)}")
    
    if exitosas:
        print("\n🎉 MEJORES ESTRATEGIAS:")
        for resultado in exitosas:
            print(f"   ✅ {resultado['estrategia']}")
    
    if fallidas:
        print("\n💔 ESTRATEGIAS QUE FALLARON:")
        for resultado in fallidas:
            print(f"   ❌ {resultado['estrategia']}: {resultado['error']}")
    
    return resultados


def quick_test_captcha_type(cedula_prueba):
    """
    Test rápido para ver qué tipo de CAPTCHA aparece
    """
    from selenium import webdriver
    from selenium.webdriver.chrome.service import Service
    from selenium.webdriver.chrome.options import Options
    from webdriver_manager.chrome import ChromeDriverManager
    
    options = Options()
    options.add_argument("--disable-blink-features=AutomationControlled")
    options.add_experimental_option("excludeSwitches", ["enable-automation"])
    options.add_experimental_option('useAutomationExtension', False)
    
    driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=options)
    driver.execute_script("Object.defineProperty(navigator, 'webdriver', {get: () => undefined})")
    
    try:
        print("🔍 ANALIZANDO TIPO DE CAPTCHA...")
        
        driver.get("https://antecedentes.policia.gov.co:7005/WebJudicial/index.xhtml")
        time.sleep(3)
        
        # Aceptar términos rápidamente
        from selenium.webdriver.support.ui import WebDriverWait
        from selenium.webdriver.support import expected_conditions as EC
        
        wait = WebDriverWait(driver, 20)
        
        aceptar_radio = wait.until(EC.element_to_be_clickable((By.ID, "aceptaOption:0")))  #type: ignore
        driver.execute_script("arguments[0].click();", aceptar_radio)
        
        continuar_btn = wait.until(EC.element_to_be_clickable((By.ID, "continuarBtn")))  #type: ignore
        driver.execute_script("arguments[0].click();", continuar_btn)

        # Ingresar cédula
        campo_cedula = wait.until(EC.element_to_be_clickable((By.ID, "cedulaInput")))  #type: ignore
        campo_cedula.send_keys(str(cedula_prueba))
        
        # Analizar CAPTCHA
        tipo_captcha = detectar_tipo_captcha(driver)
        
        print(f"📋 RESULTADO DEL ANÁLISIS:")
        print(f"   🎯 Tipo de CAPTCHA: {tipo_captcha}")
        
        if tipo_captcha == "simple":
            print("   ✅ ¡PERFECTO! Solo necesitas marcar el checkbox")
        elif tipo_captcha == "complejo":
            print("   ⚠️  CAPTCHA complejo - necesitas seleccionar imágenes")
            print("   💡 Recomendación: Usar estrategia de rotación o sesión previa")
        else:
            print("   ❓ No se pudo determinar el tipo")
        
        input("\nPresiona ENTER para cerrar el navegador...")
        
        return tipo_captcha
        
    except Exception as e:
        print(f"❌ Error en análisis: {e}")
        return "error"
    finally:
        driver.quit()


if __name__ == "__main__":
    # Para probar rápidamente
    cedula_test = input("Ingresa una cédula para probar: ")
    
    print("\n¿Qué quieres hacer?")
    print("1. 🔍 Solo analizar tipo de CAPTCHA")
    print("2. 🧪 Probar todas las estrategias")
    print("3. 🎯 Probar estrategia específica")
    
    opcion = input("\nSelecciona (1/2/3): ")
    
    if opcion == "1":
        tipo = quick_test_captcha_type(cedula_test)
        print(f"\nTipo de CAPTCHA detectado: {tipo}")
        
    elif opcion == "2":
        resultados = test_todas_estrategias(cedula_test)
        
    elif opcion == "3":
        print("\nEstrategias disponibles:")
        print("1. Comportamiento humano")
        print("2. Rotación User-Agent") 
        print("3. Bypass con token")
        print("4. Sesión previa")
        
        est = input("Selecciona estrategia (1/2/3/4): ")
        
        if est == "1":
            resultado = consultar_policia_estrategia_humana(cedula_test)
        elif est == "2":
            resultado = consultar_policia_con_proxy_rotacion(cedula_test)
        elif est == "3":
            resultado = consultar_policia_bypass_captcha(cedula_test)
        elif est == "4":
            resultado = consultar_policia_session_previa(cedula_test)
        
        print(f"\n📊 Resultado: {resultado}")
    
    else:
        print("Opción no válida")