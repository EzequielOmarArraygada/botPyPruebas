import discord
from discord.ext import commands
from discord.ui import Button, View
from interactions.modals import CasoModal
import utils.state_manager as state_manager
import config

# --- NUEVO: Definición de la View y el Button fuera de la función ---
class CompleteCasoButton(Button):
    def __init__(self):
        super().__init__(label="Completar detalles del caso", style=discord.ButtonStyle.primary, custom_id="completeCasoDetailsButton")
    async def callback(self, interaction):
        print('DEBUG: callback de CompleteCasoButton ejecutado')
        pass  # El flujo real lo maneja el listener

class CompleteCasoView(View):
    def __init__(self):
        super().__init__(timeout=None)
        self.add_item(CompleteCasoButton())

class InteractionSelects(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.Cog.listener()
    async def on_interaction(self, interaction: discord.Interaction):
        # --- Manejar Select Menu de Tipo de Solicitud ---
        if (interaction.type == discord.InteractionType.component and 
            interaction.data and 
            interaction.data.get('custom_id') == 'casoTipoSolicitudSelect'):
            
            print('DEBUG: Interacción recibida del select menu')
            try:
                user_id = str(interaction.user.id)
                pending_data = state_manager.get_user_state(user_id)
                print(f'DEBUG: Estado pendiente para usuario {user_id}: {pending_data}')
                if pending_data and pending_data.get('type') == 'caso' and pending_data.get('paso') == 1:
                    try:
                        select_data = interaction.data
                        print(f'DEBUG: Datos del select: {select_data}')
                        if 'values' in select_data and select_data['values']:
                            selected_tipo = select_data['values'][0]
                            print(f"DEBUG: Tipo seleccionado: {selected_tipo}")
                            state_manager.set_user_state(user_id, {
                                "type": "caso",
                                "paso": 2,
                                "tipoSolicitud": selected_tipo
                            })
                            print('DEBUG: Estado actualizado, creando CompleteCasoView...')
                            try:
                                print('DEBUG: Antes de crear CompleteCasoView')
                                view = CompleteCasoView()
                                print('DEBUG: Después de crear CompleteCasoView')
                                print('DEBUG: Antes de enviar mensaje con botón')
                                await interaction.response.send_message(
                                    content=f"Tipo de solicitud seleccionado: **{selected_tipo}**\n\nHaz clic en el botón para completar los detalles del caso.",
                                    view=view,
                                    ephemeral=True
                                )
                                print('DEBUG: Mensaje con botón enviado correctamente.')
                            except Exception as e:
                                print(f'ERROR al crear la View o enviar el mensaje con el botón: {e}')
                            return
                        else:
                            raise ValueError("No se encontraron valores en la selección")
                    except (KeyError, IndexError, ValueError) as e:
                        print(f"Error al procesar selección de tipo de solicitud: {e}")
                        await interaction.response.edit_message(
                            content='Error al procesar la selección. Por favor, intenta de nuevo.',
                            view=None
                        )
                        state_manager.delete_user_state(user_id)
                else:
                    await interaction.response.edit_message(
                        content='Esta selección no corresponde a un proceso activo. Por favor, usa el comando /agregar-caso para empezar.',
                        view=None
                    )
                    state_manager.delete_user_state(user_id)
            except Exception as e:
                print(f'ERROR GLOBAL en el bloque del select menu: {e}')

        # --- Manejar Botón para completar detalles del caso ---
        elif (interaction.type == discord.InteractionType.component and 
              interaction.data and 
              interaction.data.get('custom_id') == 'completeCasoDetailsButton'):
            
            user_id = str(interaction.user.id)
            pending_data = state_manager.get_user_state(user_id)
            if pending_data and pending_data.get('type') == 'caso' and pending_data.get('paso') == 2 and pending_data.get('tipoSolicitud'):
                modal = CasoModal()
                await interaction.response.send_modal(modal)
            else:
                await interaction.response.edit_message(
                    content='Este botón no corresponde a un proceso activo. Por favor, usa el comando /agregar-caso para empezar.',
                    view=None
                )
                state_manager.delete_user_state(user_id)

        # --- Manejar sumisión de modals (CasoModal) ---
        elif (interaction.type == discord.InteractionType.modal_submit and 
              interaction.data and 
              interaction.data.get('custom_id') == 'casoModal'):
            
            user_id = str(interaction.user.id)
            pending_data = state_manager.get_user_state(user_id)
            
            if not pending_data or pending_data.get('type') != 'caso':
                await interaction.response.send_message('❌ Error: No hay un proceso de caso activo. Usa /agregar-caso para empezar.', ephemeral=True)
                state_manager.delete_user_state(user_id)
                return
                
            try:
                # Verificar configuraciones necesarias
                if not config.GOOGLE_CREDENTIALS_JSON:
                    await interaction.response.send_message('❌ Error: Las credenciales de Google no están configuradas.', ephemeral=True)
                    state_manager.delete_user_state(user_id)
                    return
                    
                if not config.SPREADSHEET_ID_CASOS:
                    await interaction.response.send_message('❌ Error: El ID de la hoja de Casos no está configurado.', ephemeral=True)
                    state_manager.delete_user_state(user_id)
                    return
                    
                # Recuperar datos del modal
                pedido = interaction.text_values.get('casoPedidoInput', '').strip()
                numero_caso = interaction.text_values.get('casoNumeroCasoInput', '').strip()
                datos_contacto = interaction.text_values.get('casoDatosContactoInput', '').strip()
                tipo_solicitud = pending_data.get('tipoSolicitud', 'OTROS')
                
                # Validar datos requeridos
                if not pedido or not numero_caso or not datos_contacto:
                    await interaction.response.send_message('❌ Error: Todos los campos son requeridos.', ephemeral=True)
                    state_manager.delete_user_state(user_id)
                    return
                    
                # Verificar duplicado
                from utils.google_sheets import initialize_google_sheets, check_if_pedido_exists
                from datetime import datetime
                import pytz
                
                client = initialize_google_sheets(config.GOOGLE_CREDENTIALS_JSON)
                spreadsheet = client.open_by_key(config.SPREADSHEET_ID_CASOS)
                
                # Usar la primera hoja si no hay una específica configurada
                sheet_name = getattr(config, 'SHEET_NAME_CASOS', None)
                if sheet_name:
                    sheet = spreadsheet.worksheet(sheet_name)
                else:
                    sheet = spreadsheet.sheet1
                    
                is_duplicate = check_if_pedido_exists(sheet, 'A:Z', pedido)
                if is_duplicate:
                    await interaction.response.send_message(f'❌ El número de pedido **{pedido}** ya se encuentra registrado en la hoja de Casos.', ephemeral=True)
                    state_manager.delete_user_state(user_id)
                    return
                    
                # Escribir en Google Sheets
                tz = pytz.timezone('America/Argentina/Buenos_Aires')
                now = datetime.now(tz)
                fecha_hora = now.strftime('%d-%m-%Y %H:%M:%S')
                
                # Obtener el nombre del usuario
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
                print('Error general durante el procesamiento del modal de caso:', error)
                await interaction.response.send_message(f'❌ Hubo un error al procesar tu caso. Detalles: {error}', ephemeral=True)
            state_manager.delete_user_state(user_id)

        # --- Manejar sumisión de modals (FacturaAModal) ---
        elif (interaction.type == discord.InteractionType.modal_submit and 
              interaction.data and 
              interaction.data.get('custom_id') == 'facturaAModal'):
            
            user_id = str(interaction.user.id)
            
            # Verificar configuraciones necesarias
            if not config.GOOGLE_CREDENTIALS_JSON:
                await interaction.response.send_message('❌ Error: Las credenciales de Google no están configuradas.', ephemeral=True)
                return
                
            if not config.SPREADSHEET_ID_FAC_A:
                await interaction.response.send_message('❌ Error: El ID de la hoja de Factura A no está configurado.', ephemeral=True)
                return
                
            # Recuperar datos del modal
            pedido = interaction.text_values.get('pedidoInput', '').strip()
            caso = interaction.text_values.get('casoInput', '').strip()
            email = interaction.text_values.get('emailInput', '').strip()
            descripcion = interaction.text_values.get('descripcionInput', '').strip()
            
            # Validar datos requeridos
            if not pedido or not caso or not email:
                await interaction.response.send_message('❌ Error: Los campos Pedido, Caso y Email son requeridos.', ephemeral=True)
                return
                
            # Verificar duplicado
            sheet_success = False
            try:
                from utils.google_sheets import initialize_google_sheets, check_if_pedido_exists
                from datetime import datetime
                import pytz
                
                client = initialize_google_sheets(config.GOOGLE_CREDENTIALS_JSON)
                spreadsheet = client.open_by_key(config.SPREADSHEET_ID_FAC_A)
                
                # Usar la primera hoja si no hay una específica configurada
                sheet_name = getattr(config, 'SHEET_NAME_FAC_A', None)
                if sheet_name:
                    sheet = spreadsheet.worksheet(sheet_name)
                else:
                    sheet = spreadsheet.sheet1
                    
                is_duplicate = check_if_pedido_exists(sheet, 'A:Z', pedido)
                if is_duplicate:
                    await interaction.response.send_message(f'❌ El número de pedido **{pedido}** ya se encuentra registrado en la hoja de Factura A.', ephemeral=True)
                    return
                    
                # Escribir en Google Sheets
                tz = pytz.timezone('America/Argentina/Buenos_Aires')
                now = datetime.now(tz)
                fecha_hora = now.strftime('%d-%m-%Y %H:%M:%S')
                row_data = [pedido, fecha_hora, f'#{caso}', email, descripcion]
                sheet.append_row(row_data)
                sheet_success = True
                
                # Estado de espera de adjuntos (si aplica)
                parent_folder_id = getattr(config, 'PARENT_DRIVE_FOLDER_ID', None)
                if parent_folder_id:
                    state_manager.set_user_state(user_id, {"type": "facturaA", "pedido": pedido, "timestamp": now.isoformat()})
                    
                confirmation_message = '✅ **Solicitud de Factura A cargada correctamente en Google Sheets.**'
                if parent_folder_id:
                    confirmation_message += '\n\n📎 **Próximo paso:** Envía los archivos adjuntos para esta solicitud en un **mensaje separado** aquí mismo en este canal.'
                else:
                    confirmation_message += '\n\n⚠️ La carga de archivos adjuntos a Google Drive no está configurada en el bot para Factura A.'
                    
                await interaction.response.send_message(confirmation_message, ephemeral=True)
                
            except Exception as error:
                print('Error general durante el procesamiento de la sumisión del modal (Factura A Sheets):', error)
                await interaction.response.send_message(f'❌ Hubo un error al procesar tu solicitud de Factura A. Detalles: {error}', ephemeral=True)

async def setup(bot):
    await bot.add_cog(InteractionSelects(bot)) 