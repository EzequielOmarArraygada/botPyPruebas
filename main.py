import discord
from discord.ext import commands, tasks
import asyncio
import config
import logging
from utils.google_client_manager import initialize_google_clients, get_sheets_client, get_drive_client
from utils.andreani import get_andreani_tracking
from utils.discord_logger import setup_discord_logging, log_exception

# Configuración del bot con intents
intents = discord.Intents.all()
bot = commands.Bot(command_prefix=config.PREFIX, intents=intents)

# Variables globales para instancias de Google
sheets_instance = None
drive_instance = None

@bot.event
async def on_ready():
    print(f'Bot conectado como {bot.user}!')
    
    # Configurar sistema de logging para Discord
    try:
        global console_redirector
        console_redirector = setup_discord_logging(bot)
        print("Sistema de logging para Discord configurado correctamente.")
    except Exception as error:
        print(f"Error al configurar sistema de logging: {error}")
    
    # Inicializar APIs de Google
    global sheets_instance, drive_instance
    try:
        # Usar el gestor centralizado de clientes de Google
        initialize_google_clients()
        sheets_instance = get_sheets_client()
        drive_instance = get_drive_client()
        
        # Agregar las instancias como atributos del bot para acceso global
        bot.sheets_instance = sheets_instance
        bot.drive_instance = drive_instance
        
        if sheets_instance and drive_instance:
            print("✅ APIs de Google inicializadas correctamente.")
        else:
            print("⚠️ APIs de Google no disponibles, pero el bot continuará funcionando.")
    except Exception as error:
        print(f"⚠️ Error al inicializar APIs de Google: {error}")
        print("El bot continuará funcionando sin las APIs de Google.")
        sheets_instance = None
        drive_instance = None
        bot.sheets_instance = None
        bot.drive_instance = None

    # Cargar el manual en memoria
    if config.MANUAL_DRIVE_FILE_ID and drive_instance:
        try:
            from utils.manual_processor import load_and_cache_manual
            await load_and_cache_manual(drive_instance, config.MANUAL_DRIVE_FILE_ID)
            print("Manual cargado en memoria.")
        except Exception as error:
            print(f"Error al cargar el manual: {error}")
    else:
        print("No se cargará el manual porque falta MANUAL_DRIVE_FILE_ID o la instancia de Drive no está disponible.")

    print("Conectado a Discord.")
    
    # Iniciar la verificación periódica de errores en la hoja
    if (config.SPREADSHEET_ID_BUSCAR_CASO and config.SHEET_RANGE_CASOS_READ and 
        config.TARGET_CHANNEL_ID_CASOS and config.GUILD_ID):
        # Verificar si la tarea ya está ejecutándose antes de iniciarla
        if not check_errors.is_running():
            print(f"Iniciando verificación periódica de errores cada {config.ERROR_CHECK_INTERVAL_MIN} minutos en la hoja de búsqueda.")
            check_errors.start()
        else:
            print("La verificación periódica de errores ya está ejecutándose.")
    else:
        print("La verificación periódica de errores en la hoja de búsqueda no se iniciará debido a la falta de configuración.")

    # --- Sincronizar comandos de aplicación (slash) SOLO en el servidor configurado ---
    try:
        if not config.GUILD_ID:
            print("Error: GUILD_ID no está configurado, no se pueden sincronizar comandos")
        else:
            guild = discord.Object(id=int(config.GUILD_ID))
            synced = await bot.tree.sync(guild=guild)
            print(f"Comandos sincronizados en guild: {config.GUILD_ID} ({len(synced)})")
            print("Comandos disponibles en guild:")
            for cmd in synced:
                print(f"  - /{cmd.name}: {cmd.description}")
    except Exception as e:
        print(f"Error al sincronizar comandos: {e}")

@tasks.loop(minutes=config.ERROR_CHECK_INTERVAL_MIN)
async def check_errors():
    """Tarea periódica para verificar errores en múltiples rangos de Google Sheets"""
    if not sheets_instance:
        print("⚠️ Verificación de errores omitida: instancia de Sheets no disponible")
        return
    
    if not bot.is_ready():
        print("⚠️ Verificación de errores omitida: bot no está listo")
        return
    
    try:
        if not config.SPREADSHEET_ID_CASOS:
            print("Error: SPREADSHEET_ID_CASOS no está configurado")
            return
        if not config.GUILD_ID:
            print("Error: GUILD_ID no está configurado")
            return
        
        print(f"🔍 Iniciando verificación de errores en {len(config.MAPA_RANGOS_ERRORES)} rangos...")
        spreadsheet = sheets_instance.open_by_key(config.SPREADSHEET_ID_CASOS)
        
        errores_encontrados = 0
        hojas_verificadas = 0
        
        for sheet_range, channel_id in config.MAPA_RANGOS_ERRORES.items():
            if not sheet_range or not channel_id:
                continue
                
            hoja_nombre = None
            sheet_range_puro = sheet_range
            if '!' in sheet_range:
                partes = sheet_range.split('!')
                if len(partes) == 2:
                    hoja_nombre = partes[0].strip("'")
                    sheet_range_puro = partes[1]
            
            try:
                if hoja_nombre:
                    sheet = spreadsheet.worksheet(hoja_nombre)
                else:
                    sheet = spreadsheet.sheet1
                    
                hojas_verificadas += 1
                print(f"📊 Verificando hoja: {hoja_nombre or '[default]'} (Rango: {sheet_range})")
                
                from utils.google_sheets import check_sheet_for_errors
                await check_sheet_for_errors(
                    bot,
                    sheet,
                    sheet_range,
                    int(channel_id),
                    int(config.GUILD_ID)
                )
                
            except Exception as sheet_error:
                print(f"❌ Error al verificar hoja {hoja_nombre or '[default]'}: {sheet_error}")
                errores_encontrados += 1
                continue
        
        print(f"✅ Verificación completada: {hojas_verificadas} hojas verificadas, {errores_encontrados} errores")
        
    except Exception as error:
        print(f"❌ Error crítico en la verificación periódica: {error}")
        # No enviar este error a Discord para evitar spam

@check_errors.before_loop
async def before_check_errors():
    """Esperar hasta que el bot esté listo antes de iniciar la tarea"""
    await bot.wait_until_ready()

@bot.event
async def on_error(event, *args, **kwargs):
    """Manejador global de errores"""
    import traceback
    error_info = traceback.format_exc()
    print(f"Error en evento {event}: {error_info}")
    try:
        log_exception(bot, Exception(f"Error en evento {event}: {error_info}"), f"Evento: {event}")
    except:
        pass

@bot.event
async def on_command_error(ctx, error):
    """Manejador de errores de comandos"""
    print(f"Error en comando {ctx.command}: {error}")
    try:
        log_exception(bot, error, f"Comando: {ctx.command}")
    except:
        pass

@bot.event
async def on_disconnect():
    """Manejador cuando el bot se desconecta"""
    print("Bot desconectado. Deteniendo tareas...")
    try:
        if check_errors.is_running():
            check_errors.cancel()
            print("Tarea check_errors detenida.")
    except Exception as e:
        print(f"Error al detener tareas: {e}")

@bot.event
async def on_connect():
    """Manejador cuando el bot se conecta"""
    print("Bot conectado a Discord.")

@bot.event
async def on_resumed():
    """Manejador cuando el bot se reconecta después de una desconexión"""
    print("Bot reconectado. Reiniciando tareas...")
    try:
        # Reiniciar la tarea de verificación de errores si no está ejecutándose
        if not check_errors.is_running():
            if (config.SPREADSHEET_ID_CASOS and config.MAPA_RANGOS_ERRORES and 
                config.GUILD_ID and sheets_instance):
                print("Reiniciando verificación periódica de errores...")
                check_errors.start()
            else:
                print("No se puede reiniciar verificación de errores: configuración incompleta")
    except Exception as e:
        print(f"Error al reiniciar tareas: {e}")

@bot.event
async def on_error(event, *args, **kwargs):
    """Manejador global de errores con mejor logging"""
    import traceback
    error_info = traceback.format_exc()
    print(f"Error en evento {event}: {error_info}")
    
    # No enviar todos los errores a Discord para evitar spam
    if "rate limit" not in error_info.lower() and "429" not in error_info:
        try:
            log_exception(bot, Exception(f"Error en evento {event}: {error_info}"), f"Evento: {event}")
        except:
            pass

# Cargar eventos y comandos
async def load_extensions():
    """Cargar todas las extensiones (eventos y comandos)"""
    extensions = [
        'events.guild_member_add',
        'events.interaction_commands', 
        'events.interaction_selects',
        'events.attachment_handler',
        'events.admin_commands',
        'events.logging_commands',
        'interactions.modals',
        'interactions.select_menus',
        'tasks.panel'
    ]
    
    for extension in extensions:
        try:
            await bot.load_extension(extension)
            print(f"Extension cargada: {extension}")
        except Exception as e:
            print(f"Error al cargar extension {extension}: {e}")
            # Log detallado del error
            import traceback
            print(f"Traceback completo: {traceback.format_exc()}")

async def register_persistent_views():
    """Registrar views persistentes para botones que funcionen después de redeploy"""
    # try:
    from tasks.panel import TaskPanelView, TareaControlView, PanelComandosView
    from events.attachment_handler import SolicitudCargadaView, NotaCreditoCargadaView
    
    # Registrar views del panel de tareas (solo las que no tienen timeout)
    bot.add_view(TaskPanelView())
    bot.add_view(TareaControlView())
    bot.add_view(PanelComandosView())
    
    # Registrar view para solicitudes de Factura A
    bot.add_view(SolicitudCargadaView("placeholder", "placeholder", "placeholder", "placeholder", "placeholder"))
    
    # Registrar view para solicitudes de Nota de Crédito (sin placeholders)
    # Las views se registran dinámicamente cuando se crean
    
    print("Views persistentes registradas correctamente")
    # except Exception as e:
    #     print(f"Error al registrar views persistentes: {e}")

async def main():
    print("Paso 1: Iniciando bot...")
    print(f"Paso 2: Token de Discord cargado (primeros 5 chars): {config.TOKEN[:5] if config.TOKEN else 'TOKEN NO CARGADO'}...")
    
    if not config.TOKEN:
        print("Error CRÍTICO: TOKEN no está configurado. No se puede conectar al bot.")
        return
    
    # Cargar extensiones
    await load_extensions()
    
    # Registrar views persistentes
    await register_persistent_views()
    
    # Conectar el bot
    try:
        print("Paso 3: Conectando con Discord...")
        await bot.start(config.TOKEN)
    finally:
        print("Paso 4: Apagando bot de forma inmediata...")
        # Limpiar sistema de logging si existe
        try:
            if 'console_redirector' in globals():
                console_redirector.stop()
                print("Sistema de logging detenido.")
        except:
            pass
    # except Exception as e:
    #     print(f"Paso 3: Error al conectar con Discord: {e}")
    #     return

if __name__ == "__main__":
    asyncio.run(main())