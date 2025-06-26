import discord
from discord.ext import commands

class FacturaAModal(discord.ui.Modal, title='Registrar Solicitud Factura A'):
    def __init__(self):
        super().__init__(custom_id='facturaAModal')
        self.pedido = discord.ui.TextInput(
            label="Número de Pedido",
            placeholder="Ingresa el número de pedido...",
            custom_id="pedidoInput",
            style=discord.TextStyle.short,
            required=True,
            max_length=100
        )
        self.caso = discord.ui.TextInput(
            label="Número de Caso",
            placeholder="Ingresa el número de caso...",
            custom_id="casoInput",
            style=discord.TextStyle.short,
            required=True,
            max_length=100
        )
        self.email = discord.ui.TextInput(
            label="Email del Cliente",
            placeholder="ejemplo@email.com",
            custom_id="emailInput",
            style=discord.TextStyle.short,
            required=True,
            max_length=100
        )
        self.descripcion = discord.ui.TextInput(
            label="Detalle de la Solicitud",
            placeholder="Describe los detalles de la solicitud...",
            custom_id="descripcionInput",
            style=discord.TextStyle.paragraph,
            required=False,
            max_length=1000
        )
        
        # Agregar los componentes al modal
        self.add_item(self.pedido)
        self.add_item(self.caso)
        self.add_item(self.email)
        self.add_item(self.descripcion)

    async def on_submit(self, interaction: discord.Interaction):
        import config
        import utils.state_manager as state_manager
        from utils.state_manager import generar_solicitud_id, cleanup_expired_states
        cleanup_expired_states()
        try:
            user_id = str(interaction.user.id)
            solicitud_id = generar_solicitud_id(user_id)
            pedido = self.pedido.value.strip()
            caso = self.caso.value.strip()
            email = self.email.value.strip()
            descripcion = self.descripcion.value.strip()
            if not pedido or not caso or not email:
                await interaction.response.send_message('❌ Error: Los campos Pedido, Caso y Email son requeridos.', ephemeral=True)
                return
            if not config.GOOGLE_CREDENTIALS_JSON:
                await interaction.response.send_message('❌ Error: Las credenciales de Google no están configuradas.', ephemeral=True)
                return
            if not config.SPREADSHEET_ID_FAC_A:
                await interaction.response.send_message('❌ Error: El ID de la hoja de Factura A no está configurado.', ephemeral=True)
                return
            from utils.google_sheets import initialize_google_sheets, check_if_pedido_exists
            from datetime import datetime
            import pytz
            client = initialize_google_sheets(config.GOOGLE_CREDENTIALS_JSON)
            spreadsheet = client.open_by_key(config.SPREADSHEET_ID_FAC_A)
            sheet_range = getattr(config, 'SHEET_RANGE_FAC_A', 'A:E')
            hoja_nombre = None
            if '!' in sheet_range:
                partes = sheet_range.split('!')
                if len(partes) == 2:
                    hoja_nombre = partes[0].strip("'")
                    sheet_range_puro = partes[1]
                else:
                    hoja_nombre = None
                    sheet_range_puro = sheet_range
            else:
                sheet_range_puro = sheet_range
            if hoja_nombre:
                sheet = spreadsheet.worksheet(hoja_nombre)
            else:
                sheet = spreadsheet.sheet1
            rows = sheet.get(sheet_range_puro)
            is_duplicate = check_if_pedido_exists(sheet, sheet_range_puro, pedido)
            if is_duplicate:
                await interaction.response.send_message(f'❌ El número de pedido **{pedido}** ya se encuentra registrado en la hoja de Factura A.', ephemeral=True)
                return
            tz = pytz.timezone('America/Argentina/Buenos_Aires')
            now = datetime.now(tz)
            fecha_hora = now.strftime('%d-%m-%Y %H:%M:%S')
            row_data = [pedido, fecha_hora, f'#{caso}', email, descripcion]
            sheet.append_row(row_data)
            parent_folder_id = getattr(config, 'PARENT_DRIVE_FOLDER_ID', None)
            if parent_folder_id:
                state_manager.set_user_state(user_id, {"type": "facturaA", "pedido": pedido, "solicitud_id": solicitud_id, "timestamp": now.timestamp()})
            confirmation_message = '✅ **Solicitud de Factura A cargada correctamente en Google Sheets.**'
            if parent_folder_id:
                confirmation_message += '\n\n📎 **Próximo paso:** Envía los archivos adjuntos para esta solicitud en un **mensaje separado** aquí mismo en este canal.'
            else:
                confirmation_message += '\n\n⚠️ La carga de archivos adjuntos a Google Drive no está configurada en el bot para Factura A.'
            await interaction.response.send_message(confirmation_message, ephemeral=True)
        except Exception as error:
            await interaction.response.send_message(f'❌ Hubo un error al procesar tu solicitud de Factura A. Detalles: {error}', ephemeral=True)

class CasoModal(discord.ui.Modal, title='Detalles del Caso'):
    def __init__(self):
        super().__init__(custom_id='casoModal')
        self.pedido = discord.ui.TextInput(
            label="Número de Pedido",
            placeholder="Ingresa el número de pedido...",
            custom_id="casoPedidoInput",
            style=discord.TextStyle.short,
            required=True,
            max_length=100
        )
        self.numero_caso = discord.ui.TextInput(
            label="Número de Caso",
            placeholder="Ingresa el número de caso...",
            custom_id="casoNumeroCasoInput",
            style=discord.TextStyle.short,
            required=True,
            max_length=100
        )
        self.datos_contacto = discord.ui.TextInput(
            label="Dirección / Teléfono / Otros Datos",
            placeholder="Ingresa los datos de contacto...",
            custom_id="casoDatosContactoInput",
            style=discord.TextStyle.paragraph,
            required=True,
            max_length=1000
        )
        
        # Agregar los componentes al modal
        self.add_item(self.pedido)
        self.add_item(self.numero_caso)
        self.add_item(self.datos_contacto)

    async def on_submit(self, interaction: discord.Interaction):
        import config
        import utils.state_manager as state_manager
        from utils.state_manager import generar_solicitud_id, cleanup_expired_states
        cleanup_expired_states()
        try:
            user_id = str(interaction.user.id)
            pending_data = state_manager.get_user_state(user_id)
            if not pending_data or pending_data.get('type') != 'caso':
                await interaction.response.send_message('❌ Error: No hay un proceso de caso activo. Usa /agregar-caso para empezar.', ephemeral=True)
                state_manager.delete_user_state(user_id)
                return
            # Recuperar datos del modal
            pedido = self.pedido.value.strip()
            numero_caso = self.numero_caso.value.strip()
            datos_contacto = self.datos_contacto.value.strip()
            tipo_solicitud = pending_data.get('tipoSolicitud', 'OTROS')
            solicitud_id = pending_data.get('solicitud_id') or generar_solicitud_id(user_id)
            # Validar datos requeridos
            if not pedido or not numero_caso or not datos_contacto:
                await interaction.response.send_message('❌ Error: Todos los campos son requeridos.', ephemeral=True)
                state_manager.delete_user_state(user_id)
                return
            # Verificar duplicado y guardar en Google Sheets
            from utils.google_sheets import initialize_google_sheets, check_if_pedido_exists
            from datetime import datetime
            import pytz
            if not config.GOOGLE_CREDENTIALS_JSON:
                await interaction.response.send_message('❌ Error: Las credenciales de Google no están configuradas.', ephemeral=True)
                state_manager.delete_user_state(user_id)
                return
            if not config.SPREADSHEET_ID_CASOS:
                await interaction.response.send_message('❌ Error: El ID de la hoja de Casos no está configurado.', ephemeral=True)
                state_manager.delete_user_state(user_id)
                return
            client = initialize_google_sheets(config.GOOGLE_CREDENTIALS_JSON)
            spreadsheet = client.open_by_key(config.SPREADSHEET_ID_CASOS)
            sheet_range = getattr(config, 'SHEET_RANGE_CASOS_READ', 'A:K')
            hoja_nombre = None
            if '!' in sheet_range:
                partes = sheet_range.split('!')
                if len(partes) == 2:
                    hoja_nombre = partes[0].strip("'")
                    sheet_range_puro = partes[1]
                else:
                    hoja_nombre = None
                    sheet_range_puro = sheet_range
            else:
                sheet_range_puro = sheet_range
            if hoja_nombre:
                sheet = spreadsheet.worksheet(hoja_nombre)
            else:
                sheet = spreadsheet.sheet1
            rows = sheet.get(sheet_range_puro)
            is_duplicate = check_if_pedido_exists(sheet, sheet_range_puro, pedido)
            if is_duplicate:
                await interaction.response.send_message(f'❌ El número de pedido **{pedido}** ya se encuentra registrado en la hoja de Casos.', ephemeral=True)
                state_manager.delete_user_state(user_id)
                return
            tz = pytz.timezone('America/Argentina/Buenos_Aires')
            now = datetime.now(tz)
            fecha_hora = now.strftime('%d-%m-%Y %H:%M:%S')
            agente_name = interaction.user.display_name
            # Buscar la primera fila vacía (donde la columna 'Número de pedido' esté vacía o solo espacios)
            header = rows[0] if rows else []
            def normaliza_columna(nombre):
                return str(nombre).strip().replace(' ', '').replace('/', '').replace('-', '').lower()
            col_map = {}
            for idx, col_name in enumerate(header):
                norm = normaliza_columna(col_name)
                if norm == normaliza_columna('Número de pedido'):
                    col_map['pedido'] = idx
                if norm == normaliza_columna('Fecha'):
                    col_map['fecha'] = idx
                if norm == normaliza_columna('Agente carga'):
                    col_map['agente'] = idx
                if norm == normaliza_columna('CASO ID'):
                    col_map['caso'] = idx
                if norm == normaliza_columna('Solicitud'):
                    col_map['solicitud'] = idx
                if norm == normaliza_columna('Dirección/Teléfono/Datos (Gestión Front)'):
                    col_map['datos'] = idx
            first_empty_row = None
            for i, row in enumerate(rows[1:], start=2):
                pedido_idx = col_map.get('pedido')
                if pedido_idx is not None and (len(row) <= pedido_idx or not str(row[pedido_idx]).strip()):
                    first_empty_row = i
                    break
            if first_empty_row is None:
                await interaction.response.send_message('❌ No hay filas vacías disponibles para registrar el caso. Agrega más filas plantilla en la hoja.', ephemeral=True)
                state_manager.delete_user_state(user_id)
                return
            # Escribir los datos solo en las columnas correspondientes
            if 'pedido' in col_map:
                sheet.update_cell(first_empty_row, col_map['pedido'] + 1, pedido)
            if 'fecha' in col_map:
                sheet.update_cell(first_empty_row, col_map['fecha'] + 1, fecha_hora)
            if 'agente' in col_map:
                sheet.update_cell(first_empty_row, col_map['agente'] + 1, agente_name)
            if 'caso' in col_map:
                sheet.update_cell(first_empty_row, col_map['caso'] + 1, numero_caso)
            if 'solicitud' in col_map:
                sheet.update_cell(first_empty_row, col_map['solicitud'] + 1, tipo_solicitud)
            if 'datos' in col_map:
                sheet.update_cell(first_empty_row, col_map['datos'] + 1, datos_contacto)
            confirmation_message = f"""✅ **Caso registrado exitosamente**\n\n📋 **Detalles del caso:**\n• **N° de Pedido:** {pedido}\n• **N° de Caso:** {numero_caso}\n• **Tipo de Solicitud:** {tipo_solicitud}\n• **Agente:** {agente_name}\n• **Fecha:** {fecha_hora}\n\nEl caso ha sido guardado en Google Sheets y será monitoreado automáticamente."""
            await interaction.response.send_message(confirmation_message, ephemeral=True)
            # --- AGREGAR DESPLEGABLES ---
            try:
                from utils.google_sheets import set_dropdown_validation
                # Obtener sheetId
                sheet_id = sheet._properties['sheetId']
                # Buscar índice de columnas
                col_agente_back = None
                col_resuelto = None
                for idx, col_name in enumerate(header):
                    norm = normaliza_columna(col_name)
                    if norm == normaliza_columna('Agente Back'):
                        col_agente_back = idx + 1  # 1-based
                    if norm == normaliza_columna('Resuelto'):
                        col_resuelto = idx + 1
                # Solo si existen ambas columnas
                if col_agente_back:
                    set_dropdown_validation(
                        config.GOOGLE_CREDENTIALS_JSON,
                        config.SPREADSHEET_ID_CASOS,
                        sheet_id,
                        first_empty_row,
                        col_agente_back,
                        ["Aldo", "Ariel", "Nico", "Kevin"],
                        color={"red": 0.9, "green": 0.9, "blue": 1.0}
                    )
                if col_resuelto:
                    set_dropdown_validation(
                        config.GOOGLE_CREDENTIALS_JSON,
                        config.SPREADSHEET_ID_CASOS,
                        sheet_id,
                        first_empty_row,
                        col_resuelto,
                        ["Si", "No"],
                        color={"red": 0.8, "green": 1.0, "blue": 0.8}
                    )
            except Exception as e:
                print(f"[Desplegables] Error al agregar validación de datos: {e}")
            # --- FIN AGREGAR DESPLEGABLES ---
            state_manager.delete_user_state(user_id)
        except Exception as error:
            print('Error general durante el procesamiento del modal de caso (on_submit):', error)
            await interaction.response.send_message(f'❌ Hubo un error al procesar tu caso. Detalles: {error}', ephemeral=True)
            state_manager.delete_user_state(str(interaction.user.id))

class TrackingModal(discord.ui.Modal, title='Consulta de Tracking'):
    def __init__(self):
        super().__init__(custom_id='trackingModal')
        self.numero = discord.ui.TextInput(
            label="Número de Seguimiento",
            placeholder="Ingresa el número de seguimiento de Andreani...",
            custom_id="trackingNumeroInput",
            style=discord.TextStyle.short,
            required=True,
            max_length=100
        )
        
        # Agregar los componentes al modal
        self.add_item(self.numero)

    async def on_submit(self, interaction: discord.Interaction):
        import config
        from utils.andreani import get_andreani_tracking
        from datetime import datetime
        
        try:
            tracking_number = self.numero.value.strip()
            if not tracking_number:
                await interaction.response.send_message('❌ Debes proporcionar un número de seguimiento válido.', ephemeral=True)
                return
            
            # Verificar configuración
            if not config.ANDREANI_AUTH_HEADER:
                await interaction.response.send_message('❌ Error: La configuración de Andreani no está disponible.', ephemeral=True)
                return
            
            # Deferir la respuesta porque la consulta puede tomar tiempo
            await interaction.response.defer(thinking=True)
            
            # Consultar tracking (función síncrona)
            tracking_data = get_andreani_tracking(tracking_number, config.ANDREANI_AUTH_HEADER)
            
            # Procesar respuesta igual que el comando original
            if tracking_data:
                info = tracking_data
                # Estado actual y fecha
                estado = info.get('procesoActual', {}).get('titulo', 'Sin datos')
                fecha_entrega = clean_html(info.get('fechaEstimadaDeEntrega', ''))
                tracking_info = f"📦 Estado del tracking {tracking_number}:\n{estado} - {fecha_entrega}\n\n"
                # Historial
                timelines = info.get('timelines', [])
                if timelines:
                    tracking_info += "Historial:\n"
                    # Ordenar por fecha descendente
                    eventos = []
                    for tl in sorted(timelines, key=lambda x: x.get('orden', 0), reverse=True):
                        for traduccion in tl.get('traducciones', []):
                            fecha_iso = traduccion.get('fechaEvento', '')
                            # Formatear fecha a dd/mm/yyyy HH:MM
                            try:
                                dt = datetime.fromisoformat(fecha_iso)
                                fecha_fmt = dt.strftime('%d/%m/%Y, %H:%M')
                            except Exception:
                                fecha_fmt = fecha_iso
                            desc = clean_html(traduccion.get('traduccion', ''))
                            suc = traduccion.get('sucursal', {}).get('nombre', '')
                            eventos.append(f"{fecha_fmt}: {desc} ({suc})")
                    tracking_info += '\n'.join(eventos)
                else:
                    tracking_info += "Historial: No disponible\n"
            else:
                tracking_info = f"😕 No se pudo encontrar la información de tracking para **{tracking_number}**."
            
            # Enviar resultado
            await interaction.followup.send(tracking_info, ephemeral=False)
            
        except Exception as error:
            await interaction.followup.send(f'❌ Hubo un error al consultar el tracking. Detalles: {error}', ephemeral=True)

def clean_html(raw_html):
    """Limpia etiquetas HTML de un string"""
    import re
    clean = re.compile('<.*?>')
    return re.sub(clean, '', raw_html)

class BuscarCasoModal(discord.ui.Modal, title='Búsqueda de Caso'):
    def __init__(self):
        super().__init__(custom_id='buscarCasoModal')
        self.pedido = discord.ui.TextInput(
            label="Número de Pedido",
            placeholder="Ingresa el número de pedido a buscar...",
            custom_id="buscarCasoPedidoInput",
            style=discord.TextStyle.short,
            required=True,
            max_length=100
        )
        
        # Agregar los componentes al modal
        self.add_item(self.pedido)

    async def on_submit(self, interaction: discord.Interaction):
        import config
        
        try:
            pedido = self.pedido.value.strip()
            if not pedido or pedido.lower() == 'número de pedido':
                await interaction.response.send_message('❌ Debes proporcionar un número de pedido válido para buscar.', ephemeral=True)
                return
            
            # Verificar configuración
            if not hasattr(config, 'SPREADSHEET_ID_BUSCAR_CASO') or not hasattr(config, 'SHEETS_TO_SEARCH') or not config.SHEETS_TO_SEARCH:
                await interaction.response.send_message('❌ Error de configuración del bot: La búsqueda de casos no está configurada correctamente.', ephemeral=True)
                return
            
            # Deferir la respuesta porque la búsqueda puede tomar tiempo
            await interaction.response.defer(thinking=True)
            
            # Verificar credenciales
            if not config.GOOGLE_CREDENTIALS_JSON:
                await interaction.followup.send('❌ Error: Las credenciales de Google no están configuradas.', ephemeral=True)
                return
            if not config.SPREADSHEET_ID_BUSCAR_CASO:
                await interaction.followup.send('❌ Error: El ID de la hoja de búsqueda no está configurado.', ephemeral=True)
                return
            
            # Inicializar cliente de Google Sheets
            from utils.google_sheets import initialize_google_sheets
            client = initialize_google_sheets(config.GOOGLE_CREDENTIALS_JSON)
            spreadsheet = client.open_by_key(config.SPREADSHEET_ID_BUSCAR_CASO)
            found_rows = []
            search_summary = f"Resultados de la búsqueda para el pedido **{pedido}**:\n\n"
            
            for sheet_name in config.SHEETS_TO_SEARCH:
                try:
                    sheet = spreadsheet.worksheet(sheet_name)
                    rows = sheet.get_all_values()
                except Exception as sheet_error:
                    search_summary += f"⚠️ Error al leer la pestaña \"{sheet_name}\".\n"
                    continue
                if not rows or len(rows) <= 1:
                    continue
                header_row = rows[0]
                try:
                    pedido_column_index = next(i for i, h in enumerate(header_row) if h and str(h).strip().lower() == 'número de pedido')
                except StopIteration:
                    search_summary += f"⚠️ No se encontró la columna \"Número de pedido\" en la pestaña \"{sheet_name}\".\n"
                    continue
                for i, row in enumerate(rows[1:], start=2):
                    if len(row) <= pedido_column_index:
                        continue
                    row_pedido_value = str(row[pedido_column_index]).strip() if row[pedido_column_index] else ''
                    if row_pedido_value.lower() == pedido.lower():
                        found_rows.append({
                            'sheet': sheet_name,
                            'row_number': i,
                            'data': row
                        })
            
            if found_rows:
                search_summary += f"✅ Se encontraron **{len(found_rows)}** coincidencias:\n\n"
                detailed_results = ''
                for found in found_rows:
                    detailed_results += f"**Pestaña:** \"{found['sheet']}\", **Fila:** {found['row_number']}\n"
                    display_columns = ' | '.join(found['data'][:6])
                    detailed_results += f"`{display_columns}`\n\n"
                full_message = search_summary + detailed_results
                if len(full_message) > 2000:
                    await interaction.followup.send(search_summary + "Los resultados completos son demasiado largos para mostrar aquí. Por favor, revisa la hoja de Google Sheets directamente.", ephemeral=False)
                else:
                    await interaction.followup.send(full_message, ephemeral=False)
            else:
                search_summary += '😕 No se encontraron coincidencias en las pestañas configuradas.'
                await interaction.followup.send(search_summary, ephemeral=False)
            
        except Exception as error:
            print('Error general durante la búsqueda de casos en Google Sheets:', error)
            await interaction.followup.send('❌ Hubo un error al realizar la búsqueda de casos. Por favor, inténtalo de nuevo o contacta a un administrador.', ephemeral=False)

class CantidadCasosModal(discord.ui.Modal, title='Finalizar Tarea'):
    def __init__(self, tarea_id, user_id):
        super().__init__(custom_id='cantidadCasosModal')
        self.tarea_id = tarea_id
        self.user_id = user_id
        
        self.cantidad_casos = discord.ui.TextInput(
            label="Cantidad de casos gestionados",
            placeholder="Ingresa el número de casos gestionados...",
            custom_id="cantidadCasosInput",
            style=discord.TextStyle.short,
            required=True,
            max_length=10
        )
        
        # Agregar los componentes al modal
        self.add_item(self.cantidad_casos)

    async def on_submit(self, interaction: discord.Interaction):
        import config
        import utils.google_sheets as google_sheets
        from datetime import datetime
        import pytz
        
        try:
            # Validar que el usuario sea el correcto
            if str(interaction.user.id) != self.user_id:
                await interaction.response.send_message('❌ Solo puedes finalizar tus propias tareas.', ephemeral=True)
                return
            
            # Validar y convertir la cantidad de casos
            cantidad_str = self.cantidad_casos.value.strip()
            try:
                cantidad = int(cantidad_str)
                if cantidad <= 0:
                    await interaction.response.send_message('❌ La cantidad de casos debe ser un número entero positivo mayor a cero.', ephemeral=True)
                    return
            except ValueError:
                await interaction.response.send_message('❌ La cantidad de casos debe ser un número entero válido.', ephemeral=True)
                return
            
            # Verificar credenciales
            if not config.GOOGLE_CREDENTIALS_JSON:
                await interaction.response.send_message('❌ Error: Las credenciales de Google no están configuradas.', ephemeral=True)
                return
            if not config.GOOGLE_SHEET_ID_TAREAS:
                await interaction.response.send_message('❌ Error: El ID de la hoja de tareas no está configurado.', ephemeral=True)
                return
            
            # Inicializar Google Sheets
            client = google_sheets.initialize_google_sheets(config.GOOGLE_CREDENTIALS_JSON)
            spreadsheet = client.open_by_key(config.GOOGLE_SHEET_ID_TAREAS)
            sheet_activas = spreadsheet.worksheet('Tareas Activas')
            sheet_historial = spreadsheet.worksheet('Historial')
            
            # Obtener datos actuales de la tarea
            datos_tarea = google_sheets.obtener_tarea_por_id(sheet_activas, self.tarea_id)
            if not datos_tarea:
                await interaction.response.send_message('❌ No se encontró la tarea especificada.', ephemeral=True)
                return
            
            # Obtener fecha actual
            tz = pytz.timezone('America/Argentina/Buenos_Aires')
            now = datetime.now(tz)
            fecha_actual = now.strftime('%d/%m/%Y %H:%M:%S')
            
            # Finalizar la tarea con la cantidad de casos
            google_sheets.finalizar_tarea_por_id_con_cantidad(
                sheet_activas, 
                sheet_historial, 
                self.tarea_id, 
                str(interaction.user), 
                fecha_actual, 
                cantidad
            )
            
            # Actualizar el embed con estado finalizado y cantidad de casos
            from tasks.panel import crear_embed_tarea
            embed = crear_embed_tarea(
                interaction.user, 
                datos_tarea['tarea'], 
                datos_tarea['observaciones'], 
                datos_tarea['inicio'], 
                'Finalizada', 
                datos_tarea['tiempo_pausado'],
                cantidad_casos=cantidad
            )
            embed.color = discord.Color.red()
            
            # Crear una nueva vista sin botones para tareas finalizadas
            view = discord.ui.View(timeout=None)
            
            await interaction.response.edit_message(embed=embed, view=view)
            
        except Exception as e:
            print(f'Error al finalizar tarea con cantidad de casos: {e}')
            await interaction.response.send_message(f'❌ Error al finalizar la tarea: {str(e)}', ephemeral=True)

class Modals(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    # Aquí puedes agregar comandos que muestren los modales
    @commands.command()
    async def factura_a(self, ctx):
        """Muestra el modal de Factura A"""
        modal = FacturaAModal()
        await ctx.send_modal(modal)

    @commands.command()
    async def caso(self, ctx):
        """Muestra el modal de Caso"""
        modal = CasoModal()
        await ctx.send_modal(modal)

async def setup(bot):
    await bot.add_cog(Modals(bot)) 