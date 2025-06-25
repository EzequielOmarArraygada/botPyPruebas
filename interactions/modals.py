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
            row_data = [
                pedido,           # A - Número de Pedido
                fecha_hora,       # B - Fecha
                agente_name,      # C - Agente
                numero_caso,      # D - Número de Caso
                tipo_solicitud,   # E - Tipo de Solicitud
                datos_contacto,   # F - Datos de Contacto
                '',               # G - Estado
                '',               # H - Observaciones
                '',               # I - Error
                ''                # J - Notificado
            ]
            sheet.append_row(row_data)
            confirmation_message = f"""✅ **Caso registrado exitosamente**\n\n📋 **Detalles del caso:**\n• **N° de Pedido:** {pedido}\n• **N° de Caso:** {numero_caso}\n• **Tipo de Solicitud:** {tipo_solicitud}\n• **Agente:** {agente_name}\n• **Fecha:** {fecha_hora}\n\nEl caso ha sido guardado en Google Sheets y será monitoreado automáticamente."""
            await interaction.response.send_message(confirmation_message, ephemeral=True)
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