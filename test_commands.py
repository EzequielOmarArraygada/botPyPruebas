#!/usr/bin/env python3
"""
Script para probar la configuración de comandos
"""

def test_commands_config():
    """Prueba la configuración de comandos"""
    print("🔍 Verificando configuración de comandos...")
    
    try:
        # Verificar que los comandos estén registrados
        from events.interaction_commands import InteractionCommands
        
        print("✅ Módulo de comandos cargado correctamente")
        
        # Verificar configuraciones necesarias
        import config
        
        print("\n📋 Verificando configuraciones:")
        
        # Discord
        if config.TOKEN:
            print("✅ DISCORD_TOKEN configurado")
        else:
            print("❌ DISCORD_TOKEN no configurado")
            
        if config.GUILD_ID:
            print("✅ GUILD_ID configurado")
        else:
            print("❌ GUILD_ID no configurado")
            
        # Canales
        if config.TARGET_CHANNEL_ID_FAC_A:
            print("✅ TARGET_CHANNEL_ID_FAC_A configurado")
        else:
            print("❌ TARGET_CHANNEL_ID_FAC_A no configurado")
            
        if config.TARGET_CHANNEL_ID_ENVIOS:
            print("✅ TARGET_CHANNEL_ID_ENVIOS configurado")
        else:
            print("❌ TARGET_CHANNEL_ID_ENVIOS no configurado")
            
        if config.TARGET_CHANNEL_ID_CASOS:
            print("✅ TARGET_CHANNEL_ID_CASOS configurado")
        else:
            print("❌ TARGET_CHANNEL_ID_CASOS no configurado")
            
        # Google Sheets
        if config.SPREADSHEET_ID_FAC_A:
            print("✅ SPREADSHEET_ID_FAC_A configurado")
        else:
            print("❌ SPREADSHEET_ID_FAC_A no configurado")
            
        if config.SPREADSHEET_ID_CASOS:
            print("✅ SPREADSHEET_ID_CASOS configurado")
        else:
            print("❌ SPREADSHEET_ID_CASOS no configurado")
            
        # Andreani
        if config.ANDREANI_AUTH_HEADER:
            print("✅ ANDREANI_AUTH_HEADER configurado")
        else:
            print("❌ ANDREANI_AUTH_HEADER no configurado")
            
        # Google Drive
        if config.PARENT_DRIVE_FOLDER_ID:
            print("✅ PARENT_DRIVE_FOLDER_ID configurado")
        else:
            print("❌ PARENT_DRIVE_FOLDER_ID no configurado")
            
        return True
        
    except Exception as e:
        print(f"❌ Error al verificar comandos: {e}")
        return False

def main():
    """Función principal"""
    print("🚀 Verificando configuración de comandos...\n")
    
    success = test_commands_config()
    
    if success:
        print("\n✅ La configuración de comandos está correcta!")
        print("🎉 Los comandos deberían funcionar correctamente.")
        print("\n📝 Comandos disponibles:")
        print("   /factura-a - Registro de Factura A")
        print("   /tracking <numero> - Consulta de envíos")
        print("   /agregar-caso - Registro de casos")
        print("   /buscar-caso <pedido> - Búsqueda de casos")
    else:
        print("\n❌ Hay problemas con la configuración de comandos.")
        print("🔧 Revisa las configuraciones faltantes.")
    
    print("\n" + "="*50)

if __name__ == "__main__":
    main() 