#!/usr/bin/env python3
"""
Instalador automático de FFmpeg para Windows
Descarga e instala FFmpeg automáticamente
"""

import os
import sys
import zipfile
import requests
from pathlib import Path
import subprocess

def download_ffmpeg():
    """Descarga FFmpeg para Windows"""
    print("🔽 Descargando FFmpeg...")
    
    # URL de FFmpeg para Windows (versión estable)
    ffmpeg_url = "https://www.gyan.dev/ffmpeg/builds/ffmpeg-release-essentials.zip"
    
    # Crear directorio de descarga
    download_dir = Path.home() / "ffmpeg_download"
    download_dir.mkdir(exist_ok=True)
    
    zip_path = download_dir / "ffmpeg.zip"
    
    try:
        response = requests.get(ffmpeg_url, stream=True)
        response.raise_for_status()
        
        total_size = int(response.headers.get('content-length', 0))
        downloaded = 0
        
        with open(zip_path, 'wb') as f:
            for chunk in response.iter_content(chunk_size=8192):
                if chunk:
                    f.write(chunk)
                    downloaded += len(chunk)
                    if total_size > 0:
                        percent = (downloaded / total_size) * 100
                        print(f"\r📥 Descargando: {percent:.1f}%", end='')
        
        print(f"\n✅ FFmpeg descargado: {zip_path}")
        return zip_path
        
    except Exception as e:
        print(f"❌ Error descargando FFmpeg: {e}")
        return None

def extract_ffmpeg(zip_path):
    """Extrae FFmpeg al directorio del usuario"""
    print("\n📦 Extrayendo FFmpeg...")
    
    extract_dir = Path.home() / "ffmpeg"
    
    try:
        with zipfile.ZipFile(zip_path, 'r') as zip_ref:
            zip_ref.extractall(extract_dir)
        
        # Buscar la carpeta extraída (tiene nombre con versión)
        extracted_dirs = [d for d in extract_dir.iterdir() if d.is_dir()]
        if extracted_dirs:
            ffmpeg_dir = extracted_dirs[0]
            bin_dir = ffmpeg_dir / "bin"
            
            if bin_dir.exists():
                print(f"✅ FFmpeg extraído en: {bin_dir}")
                return bin_dir
        
        print("❌ No se encontró la carpeta bin de FFmpeg")
        return None
        
    except Exception as e:
        print(f"❌ Error extrayendo FFmpeg: {e}")
        return None

def add_to_path(ffmpeg_bin):
    """Agrega FFmpeg al PATH del sistema"""
    print("\n🛠️  Configurando PATH...")
    
    try:
        # Obtener PATH actual
        import winreg
        
        # Leer PATH del usuario
        key = winreg.OpenKey(winreg.HKEY_CURRENT_USER, "Environment", 0, winreg.KEY_READ)
        try:
            current_path, _ = winreg.QueryValueEx(key, "PATH")
        except FileNotFoundError:
            current_path = ""
        winreg.CloseKey(key)
        
        ffmpeg_path = str(ffmpeg_bin)
        
        # Verificar si ya está en PATH
        if ffmpeg_path.lower() in current_path.lower():
            print("✅ FFmpeg ya está en PATH")
            return True
        
        # Agregar al PATH
        new_path = current_path + ";" + ffmpeg_path if current_path else ffmpeg_path
        
        key = winreg.OpenKey(winreg.HKEY_CURRENT_USER, "Environment", 0, winreg.KEY_WRITE)
        winreg.SetValueEx(key, "PATH", 0, winreg.REG_EXPAND_SZ, new_path)
        winreg.CloseKey(key)
        
        print("✅ FFmpeg agregado al PATH")
        print("⚠️  Reinicia tu terminal/IDE para que tome efecto")
        
        return True
        
    except Exception as e:
        print(f"❌ Error configurando PATH: {e}")
        return False

def test_ffmpeg():
    """Prueba si FFmpeg funciona"""
    print("\n🧪 Probando FFmpeg...")
    
    try:
        result = subprocess.run(['ffmpeg', '-version'], 
                              capture_output=True, text=True, timeout=10)
        
        if result.returncode == 0:
            print("✅ FFmpeg funciona correctamente")
            # Mostrar primera línea de versión
            first_line = result.stdout.split('\n')[0]
            print(f"ℹ️  {first_line}")
            return True
        else:
            print("❌ FFmpeg no responde correctamente")
            return False
            
    except subprocess.TimeoutExpired:
        print("❌ FFmpeg no responde (timeout)")
        return False
    except FileNotFoundError:
        print("❌ FFmpeg no se encuentra en PATH")
        return False
    except Exception as e:
        print(f"❌ Error probando FFmpeg: {e}")
        return False

def main():
    """Función principal"""
    print("🚀 Instalador de FFmpeg para Windows")
    print("=" * 40)
    
    # Primero probar si ya está instalado
    if test_ffmpeg():
        print("🎉 FFmpeg ya está instalado y funcionando")
        return True
    
    print("\n📥 FFmpeg no detectado, procediendo con instalación...")
    
    # Descargar
    zip_path = download_ffmpeg()
    if not zip_path:
        return False
    
    # Extraer
    bin_path = extract_ffmpeg(zip_path)
    if not bin_path:
        return False
    
    # Configurar PATH
    if not add_to_path(bin_path):
        print(f"⚠️  No se pudo agregar automáticamente al PATH")
        print(f"📝 Agrega manualmente esta ruta al PATH: {bin_path}")
        return False
    
    # Limpiar archivo descargado
    try:
        zip_path.unlink()
        zip_path.parent.rmdir()
        print("🗑️  Archivos temporales eliminados")
    except:
        pass
    
    print("\n🎉 ¡FFmpeg instalado exitosamente!")
    print("\n📋 Próximos pasos:")
    print("1. Reinicia tu terminal/IDE")
    print("2. Ejecuta de nuevo tu aplicación")
    print("3. FFmpeg debería funcionar correctamente")
    
    return True

if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\n❌ Instalación cancelada por el usuario")
    except Exception as e:
        print(f"\n❌ Error inesperado: {e}")
        print("💡 Puedes instalar FFmpeg manualmente desde: https://ffmpeg.org/download.html")