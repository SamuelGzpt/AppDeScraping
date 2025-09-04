#!/usr/bin/env python3
"""
Script de prueba para la descarga y validación de audio CAPTCHA
"""

import os
import sys
from scraping_policia import descargar_audio_captcha, validar_archivo_audio, convertir_audio_captcha

def test_audio_download():
    """Prueba la descarga de audio con URLs de ejemplo"""
    
    print("🧪 Iniciando pruebas de descarga de audio...")
    print("=" * 60)
    
    # URLs de prueba (ejemplos de audio público)
    test_urls = [
        "https://www.soundjay.com/misc/sounds/bell-ringing-05.wav",
        "https://www.soundjay.com/misc/sounds/bell-ringing-01.wav"
    ]
    
    for url in test_urls:
        print(f"\n🎵 Probando descarga desde: {url}")
        print("-" * 40)
        
        try:
            resultado = descargar_audio_captcha(url, max_intentos=2)
            if resultado:
                print("✅ Descarga exitosa")
                
                # Probar validación
                if validar_archivo_audio("temp_audio.mp3"):
                    print("✅ Archivo validado correctamente")
                    
                    # Probar conversión
                    if convertir_audio_captcha("temp_audio.mp3", "test_output.wav", max_intentos=2):
                        print("✅ Conversión exitosa")
                        
                        # Limpiar archivos de prueba
                        if os.path.exists("test_output.wav"):
                            os.remove("test_output.wav")
                    else:
                        print("❌ Error en conversión")
                else:
                    print("❌ Archivo no válido")
            else:
                print("❌ Descarga falló")
                
        except Exception as e:
            print(f"❌ Error durante la prueba: {e}")
    
    # Limpiar archivos temporales
    archivos_temp = ["temp_audio.mp3", "temp_audio.wav"]
    for archivo in archivos_temp:
        if os.path.exists(archivo):
            try:
                os.remove(archivo)
                print(f"🗑️ Archivo temporal eliminado: {archivo}")
            except:
                pass
    
    print("\n" + "=" * 60)
    print("🧪 Pruebas de descarga completadas")

if __name__ == "__main__":
    print("🚀 Iniciando pruebas del sistema de descarga de audio")
    print("=" * 80)
    
    test_audio_download()
    
    print("\n✅ Todas las pruebas completadas")
