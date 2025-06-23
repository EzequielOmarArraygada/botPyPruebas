#!/usr/bin/env python3
"""
Script de diagnóstico para el bot de Discord
Verifica la configuración y conectividad de todos los servicios
"""

import os
import sys
from dotenv import load_dotenv

# Cargar variables de entorno
load_dotenv()

def check_discord_config():
    """Verifica la configuración de Discord"""
    print("🔍 Verificando configuración de Discord...")
    
    token = os.getenv('DISCORD_TOKEN')
    client_id = os.getenv('DISCORD_CLIENT_ID')
    guild_id = os.getenv('GUILD_ID')
    
    if not token:
        print("❌ DISCORD_TOKEN no está configurado")
        return False
    else:
        print(f"✅ DISCORD_TOKEN configurado (primeros 10 chars: {token[:10]}...)")
    
    if not client_id:
        print("❌ DISCORD_CLIENT_ID no está configurado")
        return False
    else:
        print(f"✅ DISCORD_CLIENT_ID configurado: {client_id}")
    
    if not guild_id:
        print("❌ GUILD_ID no está configurado")
        return False
    else:
        print(f"✅ GUILD_ID configurado: {guild_id}")
    
    return True

def check_channel_config():
    """Verifica la configuración de canales"""
    print("\n🔍 Verificando configuración de canales...")
    
    channels = [
        ('TARGET_CHANNEL_ID_FAC_A', 'Canal de Factura A'),
        ('TARGET_CHANNEL_ID_ENVIOS', 'Canal de Envíos'),
        ('TARGET_CHANNEL_ID_CASOS', 'Canal de Casos'),
        ('TARGET_CHANNEL_ID_BUSCAR_CASO', 'Canal de Búsqueda de Casos')
    ]
    
    all_configured = True
    for env_var, description in channels:
        channel_id = os.getenv(env_var)
        if channel_id:
            print(f"✅ {description}: {channel_id}")
        else:
            print(f"❌ {description}: No configurado")
            all_configured = False
    
    return all_configured

def check_google_config():
    """Verifica la configuración de Google"""
    print("\n🔍 Verificando configuración de Google...")
    
    credentials = os.getenv('GOOGLE_CREDENTIALS_JSON')
    if not credentials:
        print("❌ GOOGLE_CREDENTIALS_JSON no está configurado")
        return False
    
    try:
        import json
        creds_dict = json.loads(credentials)
        if 'type' in creds_dict and creds_dict['type'] == 'service_account':
            print("✅ GOOGLE_CREDENTIALS_JSON configurado correctamente")
        else:
            print("❌ GOOGLE_CREDENTIALS_JSON no tiene el formato correcto")
            return False
    except json.JSONDecodeError:
        print("❌ GOOGLE_CREDENTIALS_JSON no es un JSON válido")
        return False
    
    # Verificar IDs de hojas
    sheets_config = [
        ('GOOGLE_SHEET_ID_FAC_A', 'Hoja de Factura A'),
        ('GOOGLE_SHEET_ID_CASOS', 'Hoja de Casos'),
        ('GOOGLE_SHEET_SEARCH_SHEET_ID', 'Hoja de Búsqueda')
    ]
    
    all_configured = True
    for env_var, description in sheets_config:
        sheet_id = os.getenv(env_var)
        if sheet_id:
            print(f"✅ {description}: {sheet_id}")
        else:
            print(f"❌ {description}: No configurado")
            all_configured = False
    
    return all_configured

def check_andreani_config():
    """Verifica la configuración de Andreani"""
    print("\n🔍 Verificando configuración de Andreani...")
    
    auth_header = os.getenv('ANDREANI_API_AUTH')
    if auth_header:
        print("✅ ANDREANI_API_AUTH configurado")
        return True
    else:
        print("❌ ANDREANI_API_AUTH no está configurado")
        return False

def check_gemini_config():
    """Verifica la configuración de Gemini"""
    print("\n🔍 Verificando configuración de Gemini...")
    
    api_key = os.getenv('GEMINI_API_KEY')
    manual_file_id = os.getenv('MANUAL_DRIVE_FILE_ID')
    
    if api_key:
        print("✅ GEMINI_API_KEY configurado")
    else:
        print("❌ GEMINI_API_KEY no está configurado")
    
    if manual_file_id:
        print("✅ MANUAL_DRIVE_FILE_ID configurado")
    else:
        print("❌ MANUAL_DRIVE_FILE_ID no está configurado")
    
    return api_key and manual_file_id

def check_dependencies():
    """Verifica que todas las dependencias estén instaladas"""
    print("\n🔍 Verificando dependencias...")
    
    required_packages = [
        'discord',
        'gspread',
        'google',
        'requests',
        'pytz',
        'google.generativeai'
    ]
    
    all_installed = True
    for package in required_packages:
        try:
            __import__(package)
            print(f"✅ {package} instalado")
        except ImportError:
            print(f"❌ {package} no está instalado")
            all_installed = False
    
    return all_installed

def main():
    """Función principal del diagnóstico"""
    print("🚀 Iniciando diagnóstico del bot de Discord...\n")
    
    # Verificar dependencias
    deps_ok = check_dependencies()
    
    # Verificar configuraciones
    discord_ok = check_discord_config()
    channels_ok = check_channel_config()
    google_ok = check_google_config()
    andreani_ok = check_andreani_config()
    gemini_ok = check_gemini_config()
    
    # Resumen
    print("\n" + "="*50)
    print("📊 RESUMEN DEL DIAGNÓSTICO")
    print("="*50)
    
    issues = []
    if not deps_ok:
        issues.append("❌ Faltan dependencias - Ejecuta: pip install -r requirements.txt")
    if not discord_ok:
        issues.append("❌ Configuración de Discord incompleta")
    if not channels_ok:
        issues.append("❌ Configuración de canales incompleta")
    if not google_ok:
        issues.append("❌ Configuración de Google incompleta")
    if not andreani_ok:
        issues.append("❌ Configuración de Andreani incompleta")
    if not gemini_ok:
        issues.append("❌ Configuración de Gemini incompleta (comando /manual no funcionará)")
    
    if not issues:
        print("✅ Todo está configurado correctamente!")
        print("🎉 El bot debería funcionar sin problemas.")
    else:
        print("⚠️ Se encontraron los siguientes problemas:")
        for issue in issues:
            print(f"  {issue}")
        print("\n💡 Revisa el archivo config.example.py para ver qué variables necesitas configurar.")
    
    print("\n" + "="*50)

if __name__ == "__main__":
    main() 