#!/usr/bin/env python3
"""
Script de prueba para el reconocimiento de audio CAPTCHA mejorado
"""

import os
import sys
import time
from scraping_policia import reconocer_audio_captcha, limpiar_texto_captcha

def test_audio_recognition():
    """Prueba el reconocimiento de audio con diferentes archivos"""
    
    print("🧪 Iniciando pruebas de reconocimiento de audio...")
    print("=" * 60)
    
    # Lista de archivos de audio de prueba (si existen)
    audio_files = [
        "temp_audio.wav",
        "test_audio.wav",
        "captcha_audio.wav"
    ]
    
    # Buscar archivos de audio existentes
    existing_files = []
    for audio_file in audio_files:
        if os.path.exists(audio_file):
            existing_files.append(audio_file)
            print(f"✅ Archivo encontrado: {audio_file}")
    
    if not existing_files:
        print("⚠️ No se encontraron archivos de audio para probar")
        print("💡 Para probar, coloca un archivo de audio llamado 'temp_audio.wav' en el directorio")
        return
    
    # Probar reconocimiento con cada archivo
    for audio_file in existing_files:
        print(f"\n🎵 Probando reconocimiento con: {audio_file}")
        print("-" * 40)
        
        try:
            # Medir tiempo de reconocimiento
            start_time = time.time()
            resultado = reconocer_audio_captcha(audio_file, max_intentos=2)
            end_time = time.time()
            
            if resultado:
                print(f"✅ Reconocimiento exitoso: '{resultado}'")
                print(f"⏱️ Tiempo: {end_time - start_time:.2f} segundos")
            else:
                print("❌ Reconocimiento falló")
                
        except Exception as e:
            print(f"❌ Error durante la prueba: {e}")
    
    print("\n" + "=" * 60)
    print("🧪 Pruebas completadas")

def test_text_cleaning():
    """Prueba la función de limpieza de texto"""
    
    print("\n🧹 Probando limpieza de texto...")
    print("-" * 40)
    
    test_cases = [
        "123456",
        "abc123",
        "A B C 1 2 3",
        "a-b-c-1-2-3",
        "ABC123DEF",
        "  spaced  text  ",
        "special!@#chars123",
        "123abc456def",
        "",
        "   ",
        "only-special-chars!@#"
    ]
    
    for test_text in test_cases:
        resultado = limpiar_texto_captcha(test_text)
        print(f"Entrada: '{test_text}' -> Salida: '{resultado}'")

if __name__ == "__main__":
    print("🚀 Iniciando pruebas del sistema de reconocimiento de audio CAPTCHA")
    print("=" * 80)
    
    # Probar limpieza de texto
    test_text_cleaning()
    
    # Probar reconocimiento de audio
    test_audio_recognition()
    
    print("\n✅ Todas las pruebas completadas")
