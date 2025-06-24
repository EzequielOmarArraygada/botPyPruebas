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
    :param sheet_range: Rango de lectura (ej: 'A:K' o 'SheetName!A:K')
    :param target_channel_id: ID del canal de Discord para notificaciones
    :param guild_id: ID del servidor de Discord
    """
    print('Iniciando verificación de errores en Google Sheets...')
    print(f'Hoja actual: {sheet.title}')
    print(f'Rango solicitado: {sheet_range}')
    
    try:
        # Verificar si el rango incluye un nombre de hoja específica
        hoja_nombre = None
        sheet_range_puro = sheet_range
        
        if '!' in sheet_range:
            # Si el rango tiene formato 'SheetName!Range', extraer nombre de hoja y rango
            parts = sheet_range.split('!')
            if len(parts) == 2:
                hoja_nombre = parts[0].strip("'")  # Remover comillas si las hay
                sheet_range_puro = parts[1]
                print(f"Nombre de hoja extraído: '{hoja_nombre}'")
                print(f"Rango puro: '{sheet_range_puro}'")
                
                # Obtener la hoja específica
                try:
                    spreadsheet = sheet.spreadsheet
                    sheet = spreadsheet.worksheet(hoja_nombre)
                    print(f"Cambiado a hoja: {sheet.title}")
                except Exception as e:
                    print(f"Error al cambiar a la hoja '{hoja_nombre}': {e}")
                    return
        
        # Validar formato del rango
        if not sheet_range_puro or ':' not in sheet_range_puro:
            print(f"Error: Rango inválido '{sheet_range_puro}'. Debe tener formato 'A:K'")
            return
        
        print(f'Intentando leer rango: {sheet_range_puro}')
        rows = sheet.get(sheet_range_puro)
        print(f'Filas leídas: {len(rows) if rows else 0}')
        
        if not rows:
            print('No se leyeron datos de la hoja. Verificando si la hoja tiene datos...')
            # Intentar leer un rango más amplio para ver si hay datos
            try:
                test_rows = sheet.get('A1:Z10')
                print(f'Datos de prueba (A1:Z10): {test_rows}')
            except Exception as e:
                print(f'Error al leer datos de prueba: {e}')
            return
        
        if len(rows) <= 1:
            print('Solo hay una fila o menos en la hoja. Datos encontrados:', rows)
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
        print(f"Número de columnas en encabezados: {len(header_row)}")
        
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
                    
                    # Convertir índice de columna a letra (corregido)
                    def colnum_string(n):
                        result = ""
                        while n >= 0:
                            n, remainder = divmod(n, 26)
                            result = chr(65 + remainder) + result
                            n -= 1
                        return result
                    
                    notified_col_letter = colnum_string(notified_column_index)
                    update_cell = f'{notified_col_letter}{i}'
                    print(f'Intentando marcar celda {update_cell} como notificada...')
                    
                    # Usar update_cell en lugar de update para una sola celda
                    sheet.update_cell(i, notified_column_index + 1, f'Notificado {notification_timestamp}')
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

def normaliza_columna(nombre):
    return str(nombre).strip().replace(' ', '').lower()

# Columnas para Tareas Activas
COLUMNAS_TAREAS_ACTIVAS = [
    'Usuario ID', 'Usuario', 'Tarea', 'Observaciones', 'Estado (En proceso, Pausada)',
    'Fecha/hora de inicio', 'Fecha/hora de pausa (opcional)', 'Tiempo pausada acumulado (opcional)'
]
# Columnas para Historial
COLUMNAS_HISTORIAL = [
    'Usuario ID', 'Usuario', 'Tarea', 'Observaciones', 'Estado (En proceso, Pausada, Finalizada)',
    'Fecha/hora del evento', 'Tipo de evento (Inicio, Pausa, Reanudación, Finalización)', 'Tiempo pausada acumulado (opcional, útil para auditoría)'
]

def get_col_index(header, col_name):
    col_norm = normaliza_columna(col_name)
    for i, h in enumerate(header):
        if normaliza_columna(h) == col_norm:
            return i
    return None

def registrar_tarea_activa(sheet, user_id, usuario, tarea, observaciones, inicio, estado='En proceso'):
    """
    Registra o actualiza una tarea activa para un usuario en la hoja 'Tareas Activas'.
    """
    try:
        rows = sheet.get_all_values()
        if not rows:
            sheet.append_row(COLUMNAS_TAREAS_ACTIVAS)
            rows = [COLUMNAS_TAREAS_ACTIVAS]
        header = rows[0]
        user_col = get_col_index(header, 'Usuario ID')
        if user_col is None:
            raise Exception('No se encontró la columna Usuario ID en la hoja de Tareas Activas.')
        # Buscar si ya existe
        for idx, row in enumerate(rows[1:], start=2):
            if len(row) > user_col and row[user_col] == user_id:
                # Actualizar fila existente
                nueva_fila = [user_id, usuario, tarea, observaciones, estado, inicio, '', '']
                sheet.update(f'A{idx}:H{idx}', [nueva_fila])
                return 'actualizado'
        # Si no existe, agregar
        nueva_fila = [user_id, usuario, tarea, observaciones, estado, inicio, '', '']
        sheet.append_row(nueva_fila)
        return 'nuevo'
    except Exception as e:
        print(f'[ERROR] registrar_tarea_activa: {e}')
        raise

def usuario_tiene_tarea_activa(sheet, user_id):
    try:
        rows = sheet.get_all_values()
        if not rows or len(rows) < 2:
            return False
        header = rows[0]
        user_col = get_col_index(header, 'Usuario ID')
        if user_col is None:
            return False
        for row in rows[1:]:
            if len(row) > user_col and row[user_col] == user_id:
                # Solo si el estado es 'En proceso' o 'Pausada'
                estado_col = get_col_index(header, 'Estado (En proceso, Pausada)')
                if estado_col is not None and len(row) > estado_col:
                    estado = row[estado_col].strip().lower()
                    if estado in ['en proceso', 'pausada']:
                        return True
        return False
    except Exception as e:
        print(f'[ERROR] usuario_tiene_tarea_activa: {e}')
        raise

def agregar_evento_historial(sheet, user_id, usuario, tarea, observaciones, fecha_evento, estado, tipo_evento, tiempo_pausada=''):
    try:
        rows = sheet.get_all_values()
        if not rows:
            sheet.append_row(COLUMNAS_HISTORIAL)
        nueva_fila = [user_id, usuario, tarea, observaciones, estado, fecha_evento, tipo_evento, tiempo_pausada]
        sheet.append_row(nueva_fila)
    except Exception as e:
        print(f'[ERROR] agregar_evento_historial: {e}')
        raise 