#!/usr/bin/env python3
"""
Script para verificar el formato del archivo del manual en Google Drive
"""

import os
import json
from dotenv import load_dotenv

# Cargar variables de entorno
load_dotenv()

def check_manual_file():
    """Verifica el archivo del manual en Google Drive"""
    print("🔍 Verificando archivo del manual...")
    
    manual_file_id = os.getenv('MANUAL_DRIVE_FILE_ID')
    credentials_json = os.getenv('GOOGLE_CREDENTIALS_JSON')
    
    if not manual_file_id:
        print("❌ MANUAL_DRIVE_FILE_ID no está configurado")
        return False
    
    if not credentials_json:
        print("❌ GOOGLE_CREDENTIALS_JSON no está configurado")
        return False
    
    try:
        # Verificar formato JSON de credenciales
        creds_dict = json.loads(credentials_json)
        
        # Importar módulos necesarios
        from google.oauth2.service_account import Credentials
        from googleapiclient.discovery import build
        from googleapiclient.http import MediaIoBaseDownload
        import io
        
        # Inicializar Google Drive
        scopes = ['https://www.googleapis.com/auth/drive']
        credentials = Credentials.from_service_account_info(creds_dict, scopes=scopes)
        drive_service = build('drive', 'v3', credentials=credentials)
        
        # Obtener información del archivo
        file_metadata = drive_service.files().get(fileId=manual_file_id, fields='name,size,mimeType').execute()
        
        print(f"✅ Archivo encontrado: {file_metadata['name']}")
        print(f"   Tamaño: {file_metadata['size']} bytes")
        print(f"   Tipo MIME: {file_metadata['mimeType']}")
        
        # Intentar descargar y verificar codificación
        try:
            request = drive_service.files().get_media(fileId=manual_file_id)
            fh = io.BytesIO()
            
            downloader = MediaIoBaseDownload(fh, request)
            done = False
            while not done:
                status, done = downloader.next_chunk()
                if status:
                    print(f"   Descargado {int(status.progress() * 100)}%")
            
            fh.seek(0)
            file_content = fh.read()
            
            # Probar diferentes codificaciones
            encodings = ['utf-8', 'latin-1', 'cp1252', 'iso-8859-1']
            successful_encoding = None
            
            for encoding in encodings:
                try:
                    decoded_content = file_content.decode(encoding)
                    successful_encoding = encoding
                    print(f"✅ Archivo decodificado exitosamente con {encoding}")
                    print(f"   Primeros 200 caracteres: {decoded_content[:200]}...")
                    break
                except UnicodeDecodeError:
                    continue
            
            if successful_encoding is None:
                # Intentar con 'ignore'
                decoded_content = file_content.decode('utf-8', errors='ignore')
                print("⚠️ Archivo decodificado con 'ignore' (algunos caracteres pueden haberse perdido)")
                print(f"   Primeros 200 caracteres: {decoded_content[:200]}...")
            
            return True
            
        except Exception as download_error:
            print(f"❌ Error al descargar el archivo: {download_error}")
            return False
        
    except json.JSONDecodeError as e:
        print(f"❌ Error en las credenciales JSON: {e}")
        return False
    except Exception as e:
        print(f"❌ Error inesperado: {e}")
        return False

def main():
    """Función principal"""
    print("🚀 Verificando archivo del manual...\n")
    
    success = check_manual_file()
    
    if success:
        print("\n✅ El archivo del manual está correcto!")
        print("🎉 El comando /manual debería funcionar correctamente.")
    else:
        print("\n❌ Hay problemas con el archivo del manual.")
        print("🔧 Verifica que:")
        print("   - MANUAL_DRIVE_FILE_ID sea correcto")
        print("   - El archivo sea accesible")
        print("   - El archivo esté en formato de texto")
    
    print("\n" + "="*50)

if __name__ == "__main__":
    main() 