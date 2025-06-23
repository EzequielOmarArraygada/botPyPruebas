#!/usr/bin/env python3
"""
Script para verificar el formato de las credenciales de Google
"""

import os
import json
from dotenv import load_dotenv

# Cargar variables de entorno
load_dotenv()

def check_google_credentials():
    """Verifica el formato de las credenciales de Google"""
    print("🔍 Verificando credenciales de Google...")
    
    credentials_json = os.getenv('GOOGLE_CREDENTIALS_JSON')
    
    if not credentials_json:
        print("❌ GOOGLE_CREDENTIALS_JSON no está configurado")
        return False
    
    try:
        # Intentar parsear el JSON
        creds_dict = json.loads(credentials_json)
        
        # Verificar campos requeridos
        required_fields = ['type', 'project_id', 'private_key_id', 'private_key', 'client_email']
        missing_fields = []
        
        for field in required_fields:
            if field not in creds_dict:
                missing_fields.append(field)
        
        if missing_fields:
            print(f"❌ Faltan campos requeridos: {', '.join(missing_fields)}")
            return False
        
        # Verificar que sea una cuenta de servicio
        if creds_dict['type'] != 'service_account':
            print("❌ El tipo debe ser 'service_account'")
            return False
        
        # Verificar que la private_key tenga el formato correcto
        private_key = creds_dict['private_key']
        if not private_key.startswith('-----BEGIN PRIVATE KEY-----'):
            print("❌ La private_key no tiene el formato correcto")
            return False
        
        if not private_key.endswith('-----END PRIVATE KEY-----\n'):
            print("❌ La private_key no termina correctamente")
            return False
        
        print("✅ Credenciales de Google tienen formato válido")
        print(f"   Proyecto: {creds_dict['project_id']}")
        print(f"   Email: {creds_dict['client_email']}")
        
        return True
        
    except json.JSONDecodeError as e:
        print(f"❌ Error al parsear JSON: {e}")
        print("\n💡 Posibles problemas:")
        print("   - Falta una llave de apertura o cierre { }")
        print("   - Falta una comilla de apertura o cierre \"")
        print("   - Hay una coma extra al final")
        print("   - El JSON está mal formateado")
        
        # Mostrar los primeros 100 caracteres para debug
        print(f"\n📝 Primeros 100 caracteres de GOOGLE_CREDENTIALS_JSON:")
        print(credentials_json[:100])
        
        return False
    except Exception as e:
        print(f"❌ Error inesperado: {e}")
        return False

def main():
    """Función principal"""
    print("🚀 Verificando credenciales de Google...\n")
    
    success = check_google_credentials()
    
    if success:
        print("\n✅ Las credenciales están correctas!")
        print("🎉 El bot debería poder conectarse a Google sin problemas.")
    else:
        print("\n❌ Hay problemas con las credenciales.")
        print("🔧 Revisa el formato del JSON en tu variable de entorno.")
    
    print("\n" + "="*50)

if __name__ == "__main__":
    main() 