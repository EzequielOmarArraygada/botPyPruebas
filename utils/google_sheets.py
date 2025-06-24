import gspread
from google.oauth2.service_account import Credentials
from datetime import datetime
import pytz
import discord
import json

def initialize_google_sheets(credentials_json: str):
    try:
        scopes = [
            'https://www.googleapis.com/auth/spreadsheets',
            'https://www.googleapis.com/auth/drive'
        ]
        
        # Validar que credentials_json sea un JSON válido
        try:
            if isinstance(credentials_json, str):
                creds_dict = json.loads(credentials_json)
            else:
                creds_dict = credentials_json
        except json.JSONDecodeError as e:
            raise ValueError(f"Error al parsear credenciales JSON: {e}")
        
        credentials = Credentials.from_service_account_info(creds_dict, scopes=scopes)
        client = gspread.authorize(credentials)
        print("Instancia de Google Sheets inicializada.")
        return client
    except Exception as error:
        print("Error al inicializar Google Sheets:", error)
        raise

def check_if_pedido_exists(sheet, sheet_range: str, pedido_number: str) -> bool:
    """
    Verifica si un número de pedido ya existe en la columna "Número de pedido" de una hoja específica.
    :param sheet: Instancia de gspread.Worksheet
    :param sheet_range: Rango de la hoja a leer (ej: 'A:Z')
    :param pedido_number: El número de pedido a buscar.
    :return: True si el pedido existe, False si no.
    """
    try:
        rows = sheet.get(sheet_range)
        if not rows or len(rows) <= 1:
            print(f"check_if_pedido_exists: No hay datos en {sheet_range}. Pedido {pedido_number} no encontrado.")
            return False
        header_row = rows[0]
        pedido_column_index = next((i for i, header in enumerate(header_row)
                                    if header and str(header).strip().lower() == 'número de pedido'), -1)
        if pedido_column_index == -1:
            print(f'check_if_pedido_exists: No se encontró la columna "Número de pedido" en el rango {sheet_range}.' )
            return False
        for i, row in enumerate(rows[1:], start=2):
            if len(row) <= pedido_column_index:
                continue
            row_pedido_value = str(row[pedido_column_index]).strip() if row[pedido_column_index] else ''
            if row_pedido_value.lower() == pedido_number.strip().lower():
                print(f"check_if_pedido_exists: Pedido {pedido_number} encontrado como duplicado en la fila {i} de {sheet_range}.")
                return True
        print(f"check_if_pedido_exists: Pedido {pedido_number} no encontrado en {sheet_range}.")
        return False
    except Exception as error:
        print(f"check_if_pedido_exists: Error al leer Google Sheet, rango {sheet_range}:", error)
        raise

# Verificar errores y notificar en Discord
async def check_sheet_for_errors(bot, sheet, sheet_range: str, target_channel_id: int, guild_id: int):
    """
    Verifica errores en la hoja de Google Sheets y notifica en Discord.
    :param bot: Instancia de discord.ext.commands.Bot
    :param sheet: Instancia de gspread.Worksheet
    :param sheet_range: Rango de lectura (ej: 'A:K')
    :param target_channel_id: ID del canal de Discord para notificaciones
    :param guild_id: ID del servidor de Discord
    """
    print('Iniciando verificación de errores en Google Sheets...')
    try:
        # Limpiar el rango si tiene formato incorrecto
        if '!' in sheet_range:
            # Si el rango tiene formato 'SheetName!Range', extraer solo el rango
            parts = sheet_range.split('!')
            if len(parts) >= 2:
                sheet_range = parts[-1]  # Tomar la última parte como rango
                print(f"Rango limpiado de '{sheet_range}' a '{sheet_range}'")
        
        # Validar formato del rango
        if not sheet_range or ':' not in sheet_range:
            print(f"Error: Rango inválido '{sheet_range}'. Debe tener formato 'A:K'")
            return
        
        rows = sheet.get(sheet_range)
        if not rows or len(rows) <= 1:
            print('No hay datos de casos en la hoja para verificar.')
            return
        cases_channel = bot.get_channel(target_channel_id)
        if not cases_channel:
            print(f"Error: No se pudo encontrar el canal de Discord con ID {target_channel_id}.")
            return
        guild = bot.get_guild(guild_id)
        if not guild:
            print(f"Error: No se pudo encontrar el servidor de Discord con ID {guild_id}.")
            return
        # Obtener todos los miembros del guild
        try:
            members = [member async for member in guild.fetch_members()]
        except Exception:
            members = guild.members  # fallback si ya están en caché
        
        header_row = rows[0]
        print(f"Encabezados encontrados en la hoja: {header_row}")
        
        # Buscar los índices de las columnas por título (más robusto)
        def normaliza_encabezado(h):
            if not h:
                return ''
            # Eliminar caracteres invisibles y normalizar
            return str(h).strip().replace('\u200b', '').replace('\ufeff', '').lower()
        
        error_column_index = None
        notified_column_index = None
        
        for i, header in enumerate(header_row):
            normalized_header = normaliza_encabezado(header)
            print(f"Columna {i}: '{header}' -> normalizado: '{normalized_header}'")
            
            if normalized_header == 'error':
                error_column_index = i
                print(f"Columna ERROR encontrada en índice {i}")
            elif normalized_header == 'errorenviocheck':
                notified_column_index = i
                print(f"Columna ErrorEnvioCheck encontrada en índice {i}")
        
        if error_column_index is None or notified_column_index is None:
            print('No se encontraron las columnas "ERROR" o "ErrorEnvioCheck" en la hoja.')
            print(f'Columna ERROR encontrada: {error_column_index is not None}')
            print(f'Columna ErrorEnvioCheck encontrada: {notified_column_index is not None}')
            return
        
        for i, row in enumerate(rows[1:], start=2):
            error_value = str(row[error_column_index]).strip() if len(row) > error_column_index and row[error_column_index] else ''
            notified_value = str(row[notified_column_index]).strip() if len(row) > notified_column_index and row[notified_column_index] else ''
            if error_value and not notified_value:
                pedido = row[0] if len(row) > 0 else 'N/A'
                fecha = row[1] if len(row) > 1 else 'N/A'
                agente_name = row[2] if len(row) > 2 else 'N/A'
                numero_caso = row[3] if len(row) > 3 else 'N/A'
                tipo_solicitud = row[4] if len(row) > 4 else 'N/A'
                datos_contacto = row[5] if len(row) > 5 else 'N/A'
                mention = agente_name
                found_member = next((m for m in members if m.display_name == agente_name or m.name == agente_name), None)
                if found_member:
                    mention = f'<@{found_member.id}>'
                notification_message = (
                    f"\n🚨 **Error detectado en la hoja de Casos** 🚨\n\n"
                    f"{mention}, hay un error marcado en un caso que cargaste:\n\n"
                    f"**Fila en Sheet:** {i}\n"
                    f"**N° de Pedido:** {pedido}\n"
                    f"**N° de Caso:** {numero_caso}\n"
                    f"**Tipo de Solicitud:** {tipo_solicitud}\n"
                    f"**Datos de Contacto:** {datos_contacto}\n"
                    f"**Error:** {error_value}\n\n"
                    f"Por favor, revisa la hoja para más detalles."
                )
                try:
                    await cases_channel.send(notification_message)
                    # Marcar como notificado
                    tz = pytz.timezone('America/Argentina/Buenos_Aires')
                    now = datetime.now(tz)
                    notification_timestamp = now.strftime('%d-%m-%Y %H:%M:%S')
                    # Buscar la letra de la columna para update_cell
                    def colnum_string(n):
                        string = ''
                        while n >= 0:
                            string = chr(n % 26 + ord('A')) + string
                            n = n // 26 - 1
                        return string
                    notified_col_letter = colnum_string(notified_column_index)
                    update_cell = f'{notified_col_letter}{i}'
                    sheet.update(update_cell, f'Notificado {notification_timestamp}')
                    print(f'Fila {i} marcada como notificada en Google Sheets.')
                except Exception as send_or_update_error:
                    print(f'Error al enviar el mensaje de notificación o marcar la fila {i}:', send_or_update_error)
        print('Verificación de errores en Google Sheets completada.')
    except Exception as error:
        print('Error al leer la hoja de Google Sheets para verificar errores:', error)
        print(f'Rango utilizado: {sheet_range}')
        print('Sugerencia: Verifica que el rango tenga formato correcto (ej: A:K)')

def funcion_google_sheets():
    pass 