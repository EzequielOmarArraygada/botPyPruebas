#!/usr/bin/env python3
"""
Script de verificación de configuración para el bot de Discord
Verifica que todas las variables de entorno necesarias estén configuradas correctamente
"""

import os
import json
from dotenv import load_dotenv

def check_config():
    """Verifica la configuración del bot"""
    print("🔍 Verificando configuración del bot...\n")
    
    # Cargar variables de entorno
    load_dotenv()
    
    # Variables críticas
    critical_vars = {
        'DISCORD_TOKEN': 'Token de Discord (requerido)',
        'GUILD_ID': 'ID del servidor (requerido)',
        'GOOGLE_CREDENTIALS_JSON': 'Credenciales de Google (requerido)'
    }
    
    # Variables de canales para el panel de comandos
    channel_vars = {
        'TARGET_CHANNEL_ID_FAC_A': 'Canal de Factura A',
        'TARGET_CHANNEL_ID_ENVIOS': 'Canal de Envíos',
        'TARGET_CHANNEL_ID_CASOS': 'Canal de Casos',
        'TARGET_CHANNEL_ID_CASOS_ENVIOS': 'Canal de Solicitudes de Envíos',
        'TARGET_CHANNEL_ID_BUSCAR_CASO': 'Canal de Búsqueda de Casos',
        'TARGET_CHANNEL_ID_TAREAS': 'Canal de Tareas',
        'TARGET_CHANNEL_ID_TAREAS_REGISTRO': 'Canal de Registro de Tareas',
        'TARGET_CHANNEL_ID_GUIA_COMANDOS': 'Canal de Guía de Comandos'
    }
    
    # Variables de Google Sheets
    sheets_vars = {
        'GOOGLE_SHEET_ID_FAC_A': 'ID de hoja de Factura A',
        'GOOGLE_SHEET_ID_CASOS': 'ID de hoja de Casos',
        'GOOGLE_SHEET_ID_TAREAS': 'ID de hoja de Tareas',
        'GOOGLE_SHEET_SEARCH_SHEET_ID': 'ID de hoja de Búsqueda'
    }
    
    # Variables opcionales
    optional_vars = {
        'ANDREANI_API_AUTH': 'API de Andreani (opcional)',
        'GEMINI_API_KEY': 'API de Gemini (opcional)',
        'MANUAL_DRIVE_FILE_ID': 'ID de archivo del manual (opcional)',
        'TARGET_CATEGORY_ID': 'ID de categoría objetivo (opcional)',
        'ERROR_CHECK_INTERVAL_MS': 'Intervalo de verificación de errores (opcional)'
    }
    
    print("📋 Variables Críticas:")
    critical_errors = []
    for var, description in critical_vars.items():
        value = os.getenv(var)
        if value:
            if var == 'GOOGLE_CREDENTIALS_JSON':
                try:
                    json.loads(value)
                    print(f"  ✅ {description}: Configurado correctamente")
                except json.JSONDecodeError:
                    print(f"  ❌ {description}: JSON inválido")
                    critical_errors.append(var)
            else:
                print(f"  ✅ {description}: Configurado")
        else:
            print(f"  ❌ {description}: NO CONFIGURADO")
            critical_errors.append(var)
    
    print("\n📺 Variables de Canales (Panel de Comandos):")
    channel_errors = []
    for var, description in channel_vars.items():
        value = os.getenv(var)
        if value:
            try:
                int(value)
                print(f"  ✅ {description}: {value}")
            except ValueError:
                print(f"  ❌ {description}: ID inválido ({value})")
                channel_errors.append(var)
        else:
            print(f"  ⚠️  {description}: NO CONFIGURADO")
            channel_errors.append(var)
    
    print("\n📊 Variables de Google Sheets:")
    sheets_errors = []
    for var, description in sheets_vars.items():
        value = os.getenv(var)
        if value:
            print(f"  ✅ {description}: Configurado")
        else:
            print(f"  ⚠️  {description}: NO CONFIGURADO")
            sheets_errors.append(var)
    
    print("\n🔧 Variables Opcionales:")
    for var, description in optional_vars.items():
        value = os.getenv(var)
        if value:
            print(f"  ✅ {description}: Configurado")
        else:
            print(f"  ⚪ {description}: No configurado (opcional)")
    
    # Resumen
    print("\n" + "="*50)
    print("📊 RESUMEN DE CONFIGURACIÓN")
    print("="*50)
    
    if critical_errors:
        print(f"❌ ERRORES CRÍTICOS ({len(critical_errors)}):")
        for error in critical_errors:
            print(f"  - {error}")
        print("\n⚠️  El bot NO funcionará correctamente sin estas variables.")
    else:
        print("✅ No hay errores críticos de configuración.")
    
    if channel_errors:
        print(f"\n⚠️  CANALES FALTANTES ({len(channel_errors)}):")
        for error in channel_errors:
            print(f"  - {error}")
        print("\n⚠️  El panel de comandos puede no funcionar correctamente.")
    
    if sheets_errors:
        print(f"\n⚠️  HOJAS DE GOOGLE FALTANTES ({len(sheets_errors)}):")
        for error in sheets_errors:
            print(f"  - {error}")
        print("\n⚠️  Algunas funcionalidades pueden no estar disponibles.")
    
    if not critical_errors and not channel_errors and not sheets_errors:
        print("🎉 ¡Toda la configuración está correcta!")
        print("El bot debería funcionar sin problemas.")
    
    print("\n" + "="*50)
    print("💡 CONSEJOS:")
    print("="*50)
    print("1. Asegúrate de que el archivo .env esté en la raíz del proyecto")
    print("2. Verifica que los IDs de canales sean correctos")
    print("3. Confirma que las credenciales de Google sean válidas")
    print("4. Para obtener IDs de canales: Activa el modo desarrollador en Discord")
    print("5. Haz clic derecho en el canal y selecciona 'Copiar ID'")

if __name__ == "__main__":
    check_config() 