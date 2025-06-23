#!/usr/bin/env python3
"""
Script para verificar la configuración de las hojas de Google Sheets
"""

import os
import json
from dotenv import load_dotenv

# Cargar variables de entorno
load_dotenv()

def check_sheets_config():
    """Verifica la configuración de las hojas de Google Sheets"""
    print("🔍 Verificando configuración de Google Sheets...")
    
    credentials_json = os.getenv('GOOGLE_CREDENTIALS_JSON')
    spreadsheet_id_fac_a = os.getenv('GOOGLE_SHEET_ID_FAC_A')
    spreadsheet_id_casos = os.getenv('GOOGLE_SHEET_ID_CASOS')
    sheet_range_casos_read = os.getenv('GOOGLE_SHEET_RANGE_CASOS_READ')
    
    if not credentials_json:
        print("❌ GOOGLE_CREDENTIALS_JSON no está configurado")
        return False
    
    try:
        # Verificar formato JSON de credenciales
        creds_dict = json.loads(credentials_json)
        
        # Importar módulos necesarios
        from google.oauth2.service_account import Credentials
        import gspread
        
        # Inicializar Google Sheets
        scopes = [
            'https://www.googleapis.com/auth/spreadsheets',
            'https://www.googleapis.com/auth/drive'
        ]
        credentials = Credentials.from_service_account_info(creds_dict, scopes=scopes)
        client = gspread.authorize(credentials)
        
        print("✅ Cliente de Google Sheets inicializado correctamente")
        
        # Verificar hoja de Factura A
        if spreadsheet_id_fac_a:
            try:
                spreadsheet = client.open_by_key(spreadsheet_id_fac_a)
                print(f"✅ Hoja de Factura A encontrada: {spreadsheet.title}")
                
                # Listar pestañas
                worksheets = spreadsheet.worksheets()
                print(f"   Pestañas disponibles: {[ws.title for ws in worksheets]}")
                
            except Exception as e:
                print(f"❌ Error al acceder a la hoja de Factura A: {e}")
        else:
            print("⚠️ GOOGLE_SHEET_ID_FAC_A no está configurado")
        
        # Verificar hoja de Casos
        if spreadsheet_id_casos:
            try:
                spreadsheet = client.open_by_key(spreadsheet_id_casos)
                print(f"✅ Hoja de Casos encontrada: {spreadsheet.title}")
                
                # Listar pestañas
                worksheets = spreadsheet.worksheets()
                print(f"   Pestañas disponibles: {[ws.title for ws in worksheets]}")
                
                # Verificar rango de lectura
                if sheet_range_casos_read:
                    print(f"   Rango configurado: {sheet_range_casos_read}")
                    
                    # Limpiar rango si tiene formato incorrecto
                    clean_range = sheet_range_casos_read
                    if '!' in sheet_range_casos_read:
                        parts = sheet_range_casos_read.split('!')
                        if len(parts) >= 2:
                            clean_range = parts[-1]
                            print(f"   Rango limpio sugerido: {clean_range}")
                    
                    # Probar acceso a la primera hoja
                    try:
                        sheet = spreadsheet.sheet1
                        test_range = clean_range if ':' in clean_range else 'A1'
                        test_data = sheet.get(test_range)
                        print(f"   ✅ Acceso a datos exitoso (prueba con {test_range})")
                    except Exception as e:
                        print(f"   ❌ Error al acceder a datos: {e}")
                else:
                    print("   ⚠️ GOOGLE_SHEET_RANGE_CASOS_READ no está configurado")
                
            except Exception as e:
                print(f"❌ Error al acceder a la hoja de Casos: {e}")
        else:
            print("⚠️ GOOGLE_SHEET_ID_CASOS no está configurado")
        
        return True
        
    except json.JSONDecodeError as e:
        print(f"❌ Error en las credenciales JSON: {e}")
        return False
    except Exception as e:
        print(f"❌ Error inesperado: {e}")
        return False

def main():
    """Función principal"""
    print("🚀 Verificando configuración de Google Sheets...\n")
    
    success = check_sheets_config()
    
    if success:
        print("\n✅ La configuración de Google Sheets está correcta!")
        print("🎉 El bot debería poder acceder a las hojas sin problemas.")
    else:
        print("\n❌ Hay problemas con la configuración de Google Sheets.")
        print("🔧 Verifica que:")
        print("   - Las credenciales sean correctas")
        print("   - Los IDs de las hojas sean válidos")
        print("   - Los rangos tengan formato correcto (ej: A:K)")
    
    print("\n" + "="*50)

if __name__ == "__main__":
    main() 