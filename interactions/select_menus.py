import discord
from discord.ext import commands

# Opciones para el Select Menu de Tipo de Solicitud
tipo_solicitud_options = [
    {'label': 'CAMBIO DEFECTUOSO', 'value': 'CAMBIO DEFECTUOSO'},
    {'label': 'CAMBIO INCORRECTO', 'value': 'CAMBIO INCORRECTO'},
    {'label': 'RETIRO ARREPENTIMIENTO', 'value': 'RETIRO ARREPENTIMIENTO'},
    {'label': 'PRODUCTO INCOMPLETO', 'value': 'PRODUCTO INCOMPLETO'},
    {'label': 'OTROS', 'value': 'OTROS'},
]

def build_tipo_solicitud_select_menu():
    class TipoSolicitudSelect(discord.ui.Select):
        def __init__(self):
            options = [
                discord.SelectOption(label=opt['label'], value=opt['value'])
                for opt in tipo_solicitud_options
            ]
            super().__init__(
                placeholder='Selecciona el tipo de solicitud...',
                min_values=1,
                max_values=1,
                options=options,
                custom_id='casoTipoSolicitudSelect'
            )

    class TipoSolicitudView(discord.ui.View):
        def __init__(self):
            super().__init__()
            self.add_item(TipoSolicitudSelect())

    return TipoSolicitudView()

class TipoSolicitudEnviosSelect(discord.ui.Select):
    def __init__(self):
        options = [
            discord.SelectOption(label='Reenvío', value='Reenvío'),
            discord.SelectOption(label='Cambio de dirección', value='Cambio de dirección'),
            discord.SelectOption(label='Actualizar tracking', value='Actualizar tracking'),
        ]
        super().__init__(placeholder='Selecciona el tipo de solicitud de envío...', min_values=1, max_values=1, options=options, custom_id='solicitudEnviosTipoSelect')

    async def callback(self, interaction: discord.Interaction):
        from utils.state_manager import set_user_state
        user_id = str(interaction.user.id)
        selected_tipo = self.values[0]
        set_user_state(user_id, {"type": "solicitudes_envios", "paso": 2, "tipoSolicitud": selected_tipo})
        from interactions.modals import SolicitudEnviosModal
        await interaction.response.send_modal(SolicitudEnviosModal())

class TipoSolicitudEnviosView(discord.ui.View):
    def __init__(self):
        super().__init__(timeout=120)
        self.add_item(TipoSolicitudEnviosSelect())

def build_tipo_solicitud_envios_menu():
    return TipoSolicitudEnviosView()

class TipoReembolsoSelect(discord.ui.Select):
    def __init__(self):
        options = [
            discord.SelectOption(label='Reembolso total', value='Reembolso total'),
            discord.SelectOption(label='Reembolso parcial', value='Reembolso parcial'),
            discord.SelectOption(label='Rechazado', value='Rechazado'),
            discord.SelectOption(label='OTROS', value='OTROS'),
        ]
        super().__init__(placeholder='Selecciona el tipo de reembolso...', min_values=1, max_values=1, options=options, custom_id='reembolsoTipoSelect')

    async def callback(self, interaction: discord.Interaction):
        from utils.state_manager import set_user_state
        user_id = str(interaction.user.id)
        selected_tipo = self.values[0]
        set_user_state(user_id, {"type": "reembolsos", "paso": 2, "tipoReembolso": selected_tipo})
        from interactions.modals import ReembolsoModal
        await interaction.response.send_modal(ReembolsoModal())

class TipoReembolsoView(discord.ui.View):
    def __init__(self):
        super().__init__(timeout=120)
        self.add_item(TipoReembolsoSelect())

def build_tipo_reembolso_menu():
    return TipoReembolsoView()

class SelectMenus(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

async def setup(bot):
    await bot.add_cog(SelectMenus(bot)) 