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
    'Fecha/hora de inicio', 'Fecha/hora de finalización', 'Tiempo pausada acumulado'
]
# Columnas para Historial
COLUMNAS_HISTORIAL = [
    'Usuario ID', 'Usuario', 'Tarea', 'Observaciones', 'Estado (En proceso, Pausada, Finalizada)',
    'Fecha/hora de inicio', 'Tipo de evento (Inicio, Pausa, Reanudación, Finalización)', 'Tiempo pausada acumulado'
]

def get_col_index(header, col_name):
    col_norm = normaliza_columna(col_name)
    for i, h in enumerate(header):
        if normaliza_columna(h) == col_norm:
            return i
    return None

def registrar_tarea_activa(sheet, user_id, usuario, tarea, observaciones, inicio, estado='En proceso'):
    """
    Registra una nueva tarea activa para un usuario en la hoja 'Tareas Activas'.
    Si el usuario ya tiene una tarea activa, lanza una excepción.
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
        
        # Verificar si ya tiene una tarea activa
        for idx, row in enumerate(rows[1:], start=2):
            if len(row) > user_col and row[user_col] == user_id:
                # Verificar el estado de la tarea existente
                estado_col = get_col_index(header, 'Estado (En proceso, Pausada)')
                if estado_col is not None and len(row) > estado_col:
                    estado_existente = row[estado_col].strip().lower()
                    if estado_existente in ['en proceso', 'pausada']:
                        raise Exception(f'El usuario ya tiene una tarea activa con estado "{estado_existente}". Debe finalizar la tarea actual antes de iniciar una nueva.')
        
        # Si no tiene tarea activa, agregar la nueva
        nueva_fila = [user_id, usuario, tarea, observaciones, estado, inicio, '', '00:00:00']
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
                # Solo si el estado es 'En proceso' o 'Pausada' (no 'Finalizada')
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

def obtener_datos_tarea_activa(sheet, user_id):
    """
    Obtiene los datos de la tarea activa de un usuario.
    """
    try:
        rows = sheet.get_all_values()
        if not rows or len(rows) < 2:
            return None
        
        header = rows[0]
        user_col = get_col_index(header, 'Usuario ID')
        
        if user_col is None:
            return None
        
        for row in rows[1:]:
            if len(row) > user_col and row[user_col] == user_id:
                return {
                    'usuario': row[get_col_index(header, 'Usuario')] if len(row) > get_col_index(header, 'Usuario') else '',
                    'tarea': row[get_col_index(header, 'Tarea')] if len(row) > get_col_index(header, 'Tarea') else '',
                    'observaciones': row[get_col_index(header, 'Observaciones')] if len(row) > get_col_index(header, 'Observaciones') else '',
                    'estado': row[get_col_index(header, 'Estado (En proceso, Pausada)')] if len(row) > get_col_index(header, 'Estado (En proceso, Pausada)') else '',
                    'inicio': row[get_col_index(header, 'Fecha/hora de inicio')] if len(row) > get_col_index(header, 'Fecha/hora de inicio') else '',
                    'tiempo_pausado': row[get_col_index(header, 'Tiempo pausada acumulado')] if len(row) > get_col_index(header, 'Tiempo pausada acumulado') else '00:00:00'
                }
        
        return None
    except Exception as e:
        print(f'[ERROR] obtener_datos_tarea_activa: {e}')
        return None

def sumar_tiempo_pausado(tiempo_actual, tiempo_agregar):
    """
    Suma dos tiempos en formato HH:MM:SS
    """
    try:
        def tiempo_a_segundos(tiempo_str):
            if not tiempo_str or tiempo_str == '':
                return 0
            partes = tiempo_str.split(':')
            if len(partes) == 3:
                return int(partes[0]) * 3600 + int(partes[1]) * 60 + int(partes[2])
            return 0
        
        def segundos_a_tiempo(segundos):
            horas = segundos // 3600
            minutos = (segundos % 3600) // 60
            segs = segundos % 60
            return f"{horas:02d}:{minutos:02d}:{segs:02d}"
        
        segundos_actual = tiempo_a_segundos(tiempo_actual)
        segundos_agregar = tiempo_a_segundos(tiempo_agregar)
        total_segundos = segundos_actual + segundos_agregar
        
        return segundos_a_tiempo(total_segundos)
    except Exception as e:
        print(f'[ERROR] sumar_tiempo_pausado: {e}')
        return '00:00:00'

def calcular_diferencia_tiempo(inicio, fin):
    """
    Calcula la diferencia entre dos fechas en formato HH:MM:SS
    """
    try:
        from datetime import datetime
        
        # Parsear las fechas
        inicio_dt = datetime.strptime(inicio, '%d/%m/%Y %H:%M:%S')
        fin_dt = datetime.strptime(fin, '%d/%m/%Y %H:%M:%S')
        
        # Calcular diferencia
        diferencia = fin_dt - inicio_dt
        segundos_totales = int(diferencia.total_seconds())
        
        # Convertir a formato HH:MM:SS
        horas = segundos_totales // 3600
        minutos = (segundos_totales % 3600) // 60
        segundos = segundos_totales % 60
        
        return f"{horas:02d}:{minutos:02d}:{segundos:02d}"
    except Exception as e:
        print(f'[ERROR] calcular_diferencia_tiempo: {e}')
        return '00:00:00'

def pausar_tarea_activa(sheet_activas, sheet_historial, user_id, usuario, fecha_pausa):
    """
    Pausa una tarea activa y registra el evento en el historial.
    """
    try:
        rows = sheet_activas.get_all_values()
        if not rows or len(rows) < 2:
            raise Exception('No se encontraron tareas activas.')
        
        header = rows[0]
        user_col = get_col_index(header, 'Usuario ID')
        estado_col = get_col_index(header, 'Estado (En proceso, Pausada)')
        
        if user_col is None or estado_col is None:
            raise Exception('No se encontraron las columnas necesarias en la hoja de Tareas Activas.')
        
        # Buscar la tarea del usuario
        for idx, row in enumerate(rows[1:], start=2):
            if len(row) > user_col and row[user_col] == user_id:
                estado_actual = row[estado_col].strip().lower() if len(row) > estado_col else ''
                
                if estado_actual == 'en proceso':
                    # Obtener datos de la tarea para el historial
                    tarea = row[get_col_index(header, 'Tarea')] if len(row) > get_col_index(header, 'Tarea') else ''
                    observaciones = row[get_col_index(header, 'Observaciones')] if len(row) > get_col_index(header, 'Observaciones') else ''
                    tiempo_pausado_actual = row[get_col_index(header, 'Tiempo pausada acumulado')] if len(row) > get_col_index(header, 'Tiempo pausada acumulado') else '00:00:00'
                    
                    # Actualizar estado a pausada
                    sheet_activas.update_cell(idx, estado_col + 1, 'Pausada')
                    
                    # Registrar evento en historial
                    agregar_evento_historial(
                        sheet_historial,
                        user_id,
                        usuario,
                        tarea,
                        observaciones,
                        fecha_pausa,  # Fecha del evento
                        'Pausada',
                        'Pausa',
                        tiempo_pausado_actual
                    )
                    return True
                elif estado_actual == 'pausada':
                    raise Exception('La tarea ya está pausada.')
                else:
                    raise Exception('La tarea no está en proceso.')
        
        raise Exception('No se encontró una tarea activa para este usuario.')
    except Exception as e:
        print(f'[ERROR] pausar_tarea_activa: {e}')
        raise

def reanudar_tarea_activa(sheet_activas, sheet_historial, user_id, usuario, fecha_reanudacion):
    """
    Reanuda una tarea pausada y registra el evento en el historial.
    """
    try:
        rows = sheet_activas.get_all_values()
        if not rows or len(rows) < 2:
            raise Exception('No se encontraron tareas activas.')
        
        header = rows[0]
        user_col = get_col_index(header, 'Usuario ID')
        estado_col = get_col_index(header, 'Estado (En proceso, Pausada)')
        
        if user_col is None or estado_col is None:
            raise Exception('No se encontraron las columnas necesarias en la hoja de Tareas Activas.')
        
        # Buscar la tarea del usuario
        for idx, row in enumerate(rows[1:], start=2):
            if len(row) > user_col and row[user_col] == user_id:
                estado_actual = row[estado_col].strip().lower() if len(row) > estado_col else ''
                
                if estado_actual == 'pausada':
                    # Obtener datos de la tarea para el historial
                    tarea = row[get_col_index(header, 'Tarea')] if len(row) > get_col_index(header, 'Tarea') else ''
                    observaciones = row[get_col_index(header, 'Observaciones')] if len(row) > get_col_index(header, 'Observaciones') else ''
                    tiempo_pausado_actual = row[get_col_index(header, 'Tiempo pausada acumulado')] if len(row) > get_col_index(header, 'Tiempo pausada acumulado') else '00:00:00'
                    
                    # Actualizar estado a en proceso
                    sheet_activas.update_cell(idx, estado_col + 1, 'En proceso')
                    
                    # Registrar evento en historial
                    agregar_evento_historial(
                        sheet_historial,
                        user_id,
                        usuario,
                        tarea,
                        observaciones,
                        fecha_reanudacion,  # Fecha del evento
                        'En proceso',
                        'Reanudación',
                        tiempo_pausado_actual
                    )
                    return True
                elif estado_actual == 'en proceso':
                    raise Exception('La tarea ya está en proceso.')
                else:
                    raise Exception('La tarea no está pausada.')
        
        raise Exception('No se encontró una tarea pausada para este usuario.')
    except Exception as e:
        print(f'[ERROR] reanudar_tarea_activa: {e}')
        raise

def finalizar_tarea_activa(sheet_activas, sheet_historial, user_id, usuario, fecha_finalizacion):
    """
    Finaliza una tarea activa y registra el evento en el historial.
    """
    try:
        rows = sheet_activas.get_all_values()
        if not rows or len(rows) < 2:
            raise Exception('No se encontraron tareas activas.')
        
        header = rows[0]
        user_col = get_col_index(header, 'Usuario ID')
        estado_col = get_col_index(header, 'Estado (En proceso, Pausada)')
        finalizacion_col = get_col_index(header, 'Fecha/hora de finalización')
        
        if user_col is None or estado_col is None or finalizacion_col is None:
            raise Exception('No se encontraron las columnas necesarias en la hoja de Tareas Activas.')
        
        # Buscar la tarea del usuario
        for idx, row in enumerate(rows[1:], start=2):
            if len(row) > user_col and row[user_col] == user_id:
                estado_actual = row[estado_col].strip().lower() if len(row) > estado_col else ''
                
                if estado_actual in ['en proceso', 'pausada']:
                    # Obtener datos de la tarea para el historial antes de actualizar
                    tarea = row[get_col_index(header, 'Tarea')] if len(row) > get_col_index(header, 'Tarea') else ''
                    observaciones = row[get_col_index(header, 'Observaciones')] if len(row) > get_col_index(header, 'Observaciones') else ''
                    tiempo_pausado_actual = row[get_col_index(header, 'Tiempo pausada acumulado')] if len(row) > get_col_index(header, 'Tiempo pausada acumulado') else '00:00:00'
                    
                    # Actualizar estado a finalizada y agregar fecha de finalización
                    sheet_activas.update_cell(idx, estado_col + 1, 'Finalizada')
                    sheet_activas.update_cell(idx, finalizacion_col + 1, fecha_finalizacion)
                    
                    # Registrar evento en historial
                    agregar_evento_historial(
                        sheet_historial,
                        user_id,
                        usuario,
                        tarea,
                        observaciones,
                        fecha_finalizacion,  # Fecha del evento
                        'Finalizada',
                        'Finalización',
                        tiempo_pausado_actual
                    )
                    return True
                else:
                    raise Exception('La tarea no está activa.')
        
        raise Exception('No se encontró una tarea activa para este usuario.')
    except Exception as e:
        print(f'[ERROR] finalizar_tarea_activa: {e}')
        raise 