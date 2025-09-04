#!/usr/bin/env python3
"""
Script de debugging para el reconocimiento de audio CAPTCHA
"""

import os
import sys
from scraping_policia import (
    reconocer_audio_captcha, 
    diagnosticar_audio_captcha,
    crear_audio_prueba_captcha,
    limpiar_texto_captcha
)

def test_audio_recognition_debug():
    """Prueba detallada del reconocimiento de audio con debugging"""
    
    print("🔍 DEBUGGING: Reconocimiento de audio CAPTCHA")
    print("=" * 60)
    
    # Crear audio de prueba
    texto_esperado = "123456"
    archivo_prueba = "debug_audio.wav"
    
    print(f"🎵 Creando audio de prueba con texto: '{texto_esperado}'")
    if crear_audio_prueba_captcha(texto_esperado, archivo_prueba):
        print(f"✅ Audio de prueba creado: {archivo_prueba}")
        
        # Diagnosticar el audio
        print("\n🔍 DIAGNÓSTICO DEL AUDIO:")
        print("-" * 40)
        diagnosticar_audio_captcha(archivo_prueba)
        
        # Probar reconocimiento con diferentes configuraciones
        print("\n🎤 PRUEBAS DE RECONOCIMIENTO:")
        print("-" * 40)
        
        configuraciones = [1, 2, 3, 5]
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
        
        # Probar limpieza de texto
        print("\n🧹 PRUEBAS DE LIMPIEZA DE TEXTO:")
        print("-" * 40)
        
        casos_prueba = [
            "123456",
            "abc123",
            "A B C 1 2 3",
            "a-b-c-1-2-3",
            "special!@#chars123",
            "123abc456def"
        ]
        
        for caso in casos_prueba:
            resultado = limpiar_texto_captcha(caso)
            print(f"'{caso}' -> '{resultado}'")
        
        # Limpiar archivo de prueba
        if os.path.exists(archivo_prueba):
            os.remove(archivo_prueba)
            print(f"\n🗑️ Archivo de prueba eliminado: {archivo_prueba}")
    else:
        print("❌ No se pudo crear audio de prueba")

def test_with_real_audio():
    """Prueba con archivo de audio real si existe"""
    
    print("\n🔍 PRUEBA CON AUDIO REAL:")
    print("-" * 40)
    
    archivos_reales = ["temp_audio.wav", "test_audio.wav", "captcha_audio.wav"]
    
    for archivo in archivos_reales:
        if os.path.exists(archivo):
            print(f"\n🎵 Probando con archivo real: {archivo}")
            diagnosticar_audio_captcha(archivo)
            
            resultado = reconocer_audio_captcha(archivo, max_intentos=3)
            if resultado:
                print(f"✅ Reconocimiento exitoso: '{resultado}'")
            else:
                print("❌ Reconocimiento falló")
        else:
            print(f"⚠️ Archivo no encontrado: {archivo}")

def main():
    """Función principal de debugging"""
    
    print("🚀 INICIANDO DEBUGGING DEL RECONOCIMIENTO DE AUDIO CAPTCHA")
    print("=" * 80)
    
    try:
        # Prueba 1: Audio de prueba
        test_audio_recognition_debug()
        
        # Prueba 2: Audio real
        test_with_real_audio()
        
        print("\n" + "=" * 80)
        print("✅ DEBUGGING COMPLETADO")
        
        print("\n📋 RESUMEN DE PROBLEMAS COMUNES:")
        print("-" * 40)
        print("1. Archivo de audio corrupto o vacío")
        print("2. Audio muy silencioso o con mucho ruido")
        print("3. Problemas de conexión con Google Speech API")
        print("4. Configuración incorrecta del reconocedor")
        print("5. Audio muy corto o muy largo")
        
        print("\n🔧 SOLUCIONES SUGERIDAS:")
        print("-" * 40)
        print("1. Verificar que el archivo de audio sea válido")
        print("2. Ajustar la configuración del reconocedor")
        print("3. Procesar el audio antes del reconocimiento")
        print("4. Usar múltiples estrategias de reconocimiento")
        print("5. Implementar fallback con valor aleatorio")
        
    except Exception as e:
        print(f"\n❌ ERROR DURANTE EL DEBUGGING: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    main()
