#!/usr/bin/env python3
"""
Script de prueba completo para el sistema de reconocimiento de audio CAPTCHA
"""

import os
import sys
import time
from scraping_policia import (
    reconocer_audio_captcha, 
    limpiar_texto_captcha,
    crear_audio_prueba_captcha,
    diagnosticar_audio_captcha,
    validar_archivo_audio
)

def test_crear_audio_prueba():
    """Prueba la creación de audio de prueba"""
    print("🎵 Probando creación de audio de prueba...")
    print("-" * 40)
    
    textos_prueba = ["123456", "789012", "345678", "901234"]
    
    for texto in textos_prueba:
        archivo = f"test_audio_{texto}.wav"
        if crear_audio_prueba_captcha(texto, archivo):
            print(f"✅ Audio creado para '{texto}': {archivo}")
            
            # Diagnosticar el audio creado
            diagnosticar_audio_captcha(archivo)
            
            # Probar reconocimiento
            resultado = reconocer_audio_captcha(archivo, max_intentos=2)
            if resultado:
                print(f"✅ Reconocimiento exitoso: '{resultado}' (esperado: '{texto}')")
                if resultado == texto:
                    print("🎯 ¡Reconocimiento perfecto!")
                else:
                    print("⚠️ Reconocimiento parcial")
            else:
                print("❌ Reconocimiento falló")
            
            # Limpiar archivo de prueba
            if os.path.exists(archivo):
                os.remove(archivo)
                print(f"🗑️ Archivo eliminado: {archivo}")
        else:
            print(f"❌ Error creando audio para '{texto}'")
        
        print()

def test_limpieza_texto():
    """Prueba la función de limpieza de texto"""
    print("🧹 Probando limpieza de texto...")
    print("-" * 40)
    
    casos_prueba = [
        ("123456", "123456"),
        ("abc123", "abc123"),
        ("A B C 1 2 3", "abc123"),
        ("a-b-c-1-2-3", "abc123"),
        ("ABC123DEF", "abc123def"),
        ("  spaced  text  ", "spacedtext"),
        ("special!@#chars123", "specialchars123"),
        ("123abc456def", "123abc456def"),
        ("", None),
        ("   ", None),
        ("only-special-chars!@#", None),
        ("123", "123"),
        ("abc", "abc")
    ]
    
    for entrada, esperado in casos_prueba:
        resultado = limpiar_texto_captcha(entrada)
        if resultado == esperado:
            print(f"✅ '{entrada}' -> '{resultado}' ✓")
        else:
            print(f"❌ '{entrada}' -> '{resultado}' (esperado: '{esperado}')")

def test_reconocimiento_avanzado():
    """Prueba el reconocimiento con diferentes configuraciones"""
    print("\n🎤 Probando reconocimiento avanzado...")
    print("-" * 40)
    
    # Crear audio de prueba
    texto_esperado = "123456"
    archivo_prueba = "test_avanzado.wav"
    
    if crear_audio_prueba_captcha(texto_esperado, archivo_prueba):
        print(f"✅ Audio de prueba creado: {archivo_prueba}")
        
        # Diagnosticar antes del reconocimiento
        diagnosticar_audio_captcha(archivo_prueba)
        
        # Probar reconocimiento con diferentes configuraciones
        configuraciones = [1, 2, 3, 5]  # Diferentes números de intentos
        
        for intentos in configuraciones:
            print(f"\n🔄 Probando con {intentos} intentos...")
            resultado = reconocer_audio_captcha(archivo_prueba, max_intentos=intentos)
            
            if resultado:
                print(f"✅ Reconocimiento exitoso: '{resultado}'")
                if resultado == texto_esperado:
                    print("🎯 ¡Reconocimiento perfecto!")
                    break
                else:
                    print(f"⚠️ Reconocimiento parcial (esperado: '{texto_esperado}')")
            else:
                print("❌ Reconocimiento falló")
        
        # Limpiar archivo
        if os.path.exists(archivo_prueba):
            os.remove(archivo_prueba)
            print(f"🗑️ Archivo eliminado: {archivo_prueba}")
    else:
        print("❌ No se pudo crear audio de prueba")

def test_validacion_archivos():
    """Prueba la validación de archivos de audio"""
    print("\n🔍 Probando validación de archivos...")
    print("-" * 40)
    
    # Crear archivo válido
    archivo_valido = "test_valido.wav"
    if crear_audio_prueba_captcha("123456", archivo_valido):
        print(f"✅ Archivo válido creado: {archivo_valido}")
        
        # Probar validación
        if validar_archivo_audio(archivo_valido):
            print("✅ Validación exitosa")
        else:
            print("❌ Validación falló")
        
        # Limpiar
        if os.path.exists(archivo_valido):
            os.remove(archivo_valido)
    
    # Probar archivo inexistente
    print("\n🔍 Probando archivo inexistente...")
    if validar_archivo_audio("archivo_inexistente.wav"):
        print("❌ Validación incorrecta (debería fallar)")
    else:
        print("✅ Validación correcta (falló como esperado)")
    
    # Probar archivo vacío
    print("\n🔍 Probando archivo vacío...")
    archivo_vacio = "test_vacio.wav"
    with open(archivo_vacio, "w") as f:
        f.write("")
    
    if validar_archivo_audio(archivo_vacio):
        print("❌ Validación incorrecta (debería fallar)")
    else:
        print("✅ Validación correcta (falló como esperado)")
    
    # Limpiar archivo vacío
    if os.path.exists(archivo_vacio):
        os.remove(archivo_vacio)

def main():
    """Función principal de pruebas"""
    print("🚀 Iniciando pruebas completas del sistema de reconocimiento de audio CAPTCHA")
    print("=" * 80)
    
    try:
        # Prueba 1: Creación de audio de prueba
        test_crear_audio_prueba()
        
        # Prueba 2: Limpieza de texto
        test_limpieza_texto()
        
        # Prueba 3: Reconocimiento avanzado
        test_reconocimiento_avanzado()
        
        # Prueba 4: Validación de archivos
        test_validacion_archivos()
        
        print("\n" + "=" * 80)
        print("✅ Todas las pruebas completadas")
        
    except Exception as e:
        print(f"\n❌ Error durante las pruebas: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    main()
