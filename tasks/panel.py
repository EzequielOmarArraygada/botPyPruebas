# Este módulo requiere 'discord.py' instalado en el entorno.
import discord
from discord.ext import commands
import os

# Obtener el ID del canal desde la variable de entorno
TARGET_CHANNEL_ID_TAREAS = int(os.getenv('TARGET_CHANNEL_ID_TAREAS', '0'))

class TaskPanel(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.command(name='setup_panel_tareas')
    @commands.has_permissions(administrator=True)
    async def setup_panel_tareas(self, ctx):
        """Comando para admins: publica el panel de tareas en el canal configurado."""
        if TARGET_CHANNEL_ID_TAREAS == 0:
            await ctx.send('La variable de entorno TARGET_CHANNEL_ID_TAREAS no está configurada.')
            return
        canal = self.bot.get_channel(TARGET_CHANNEL_ID_TAREAS)
        if not canal:
            await ctx.send('No se encontró el canal configurado.')
            return
        embed = discord.Embed(
            title='Panel de Registro de Tareas',
            description='Presiona el botón para registrar una nueva tarea.',
            color=discord.Color.blue()
        )
        view = TaskPanelView()
        await canal.send(embed=embed, view=view)
        await ctx.send('Panel publicado correctamente.')

class TaskPanelView(discord.ui.View):
    def __init__(self):
        super().__init__(timeout=None)
        self.add_item(TaskRegisterButton())

class TaskRegisterButton(discord.ui.Button):
    def __init__(self):
        super().__init__(label='Registrar nueva tarea', style=discord.ButtonStyle.primary)

    async def callback(self, interaction: discord.Interaction):
        await interaction.response.send_message('Aquí irá el flujo de registro de tarea.', ephemeral=True)


def setup(bot):
    bot.add_cog(TaskPanel(bot)) 