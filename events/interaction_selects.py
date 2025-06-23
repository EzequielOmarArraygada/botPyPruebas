import discord
from discord.ext import commands
from interactions.modals import CasoModal
from utils.state_manager import get_user_state, set_user_state, delete_user_state
import config

class InteractionSelects(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.Cog.listener()
    async def on_interaction(self, interaction: discord.Interaction):
        # --- Manejar Select Menu de Tipo de Solicitud ---
        if (interaction.type == discord.InteractionType.component and 
            interaction.data and 
            interaction.data.get('custom_id') == 'casoTipoSolicitudSelect'):
            
            user_id = str(interaction.user.id)
            pending_data = get_user_state(user_id)
            if pending_data and pending_data.get('type') == 'caso' and pending_data.get('paso') == 1:
                try:
                    # Type assertion for select menu data
                    select_data = interaction.data
                    if 'values' in select_data and select_data['values']:
                        selected_tipo = select_data['values'][0]
                        print(f"Tipo seleccionado: {selected_tipo}")
                        set_user_state(user_id, {"type": "caso", "paso": 2, "tipoSolicitud": selected_tipo, "interactionId": interaction.id})
                        # Mostrar botón para completar detalles
                        button = discord.ui.Button(label="Completar Detalles del Caso", custom_id="completeCasoDetailsButton", style=discord.ButtonStyle.primary)
                        view = discord.ui.View()
                        view.add_item(button)
                        print(f"Botón creado y agregado a la vista")
                        await interaction.response.edit_message(
                            content=f"Tipo de Solicitud seleccionado: **{selected_tipo}**. Haz clic en el botón para completar los detalles.",
                            view=view
                        )
                        print(f"Mensaje editado con botón")
                    else:
                        raise ValueError("No se encontraron valores en la selección")
                except (KeyError, IndexError, ValueError) as e:
                    print(f"Error al procesar selección de tipo de solicitud: {e}")
                    await interaction.response.edit_message(
                        content='Error al procesar la selección. Por favor, intenta de nuevo.',
                        view=None
                    )
                    delete_user_state(user_id)
            else:
                await interaction.response.edit_message(
                    content='Esta selección no corresponde a un proceso activo. Por favor, usa el comando /agregar-caso para empezar.',
                    view=None
                )
                delete_user_state(user_id)

        # --- Manejar Botón para completar detalles del caso ---
        elif (interaction.type == discord.InteractionType.component and 
              interaction.data and 
              interaction.data.get('custom_id') == 'completeCasoDetailsButton'):
            
            user_id = str(interaction.user.id)
            pending_data = get_user_state(user_id)
            if pending_data and pending_data.get('type') == 'caso' and pending_data.get('paso') == 2 and pending_data.get('tipoSolicitud'):
                modal = CasoModal()
                await interaction.response.send_modal(modal)
            else:
                await interaction.response.edit_message(
                    content='Este botón no corresponde a un proceso activo. Por favor, usa el comando /agregar-caso para empezar.',
                    view=None
                )
                delete_user_state(user_id)

        # --- Manejar sumisión de modals (CasoModal) ---
        elif (interaction.type == discord.InteractionType.modal_submit and 
              interaction.data and 
              interaction.data.get('custom_id') == 'casoModal'):
            
            user_id = str(interaction.user.id)
            pending_data = get_user_state(user_id)
            
            if not pending_data or pending_data.get('type') != 'caso':
                await interaction.response.send_message('❌ Error: No hay un proceso de caso activo. Usa /agregar-caso para empezar.', ephemeral=True)
                delete_user_state(user_id)
                return
                
            try:
                # Verificar configuraciones necesarias
                if not config.GOOGLE_CREDENTIALS_JSON:
                    await interaction.response.send_message('❌ Error: Las credenciales de Google no están configuradas.', ephemeral=True)
                    delete_user_state(user_id)
                    return
                    
                if not config.SPREADSHEET_ID_CASOS:
                    await interaction.response.send_message('❌ Error: El ID de la hoja de Casos no está configurado.', ephemeral=True)
                    delete_user_state(user_id)
                    return
                    
                # Recuperar datos del modal
                pedido = interaction.text_values.get('casoPedidoInput', '').strip()
                numero_caso = interaction.text_values.get('casoNumeroCasoInput', '').strip()
                datos_contacto = interaction.text_values.get('casoDatosContactoInput', '').strip()
                tipo_solicitud = pending_data.get('tipoSolicitud', 'OTROS')
                
                # Validar datos requeridos
                if not pedido or not numero_caso or not datos_contacto:
                    await interaction.response.send_message('❌ Error: Todos los campos son requeridos.', ephemeral=True)
                    delete_user_state(user_id)
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
                    delete_user_state(user_id)
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
                
                confirmation_message = f"""✅ **Caso registrado exitosamente**

📋 **Detalles del caso:**
• **N° de Pedido:** {pedido}
• **N° de Caso:** {numero_caso}
• **Tipo de Solicitud:** {tipo_solicitud}
• **Agente:** {agente_name}
• **Fecha:** {fecha_hora}

El caso ha sido guardado en Google Sheets y será monitoreado automáticamente."""
                
                await interaction.response.send_message(confirmation_message, ephemeral=True)
                delete_user_state(user_id)
                
            except Exception as error:
                print('Error general durante el procesamiento del modal de caso:', error)
                await interaction.response.send_message(f'❌ Hubo un error al procesar tu caso. Detalles: {error}', ephemeral=True)
                delete_user_state(user_id)

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
                    from utils.state_manager import set_user_state
                    set_user_state(user_id, {"type": "facturaA", "pedido": pedido, "timestamp": now.isoformat()})
                    
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