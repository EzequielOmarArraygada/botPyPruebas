# Este módulo requiere 'discord.py' instalado en el entorno.
import discord
from discord.ext import commands
from discord import app_commands
import os

# Obtener el ID del canal desde la variable de entorno
TARGET_CHANNEL_ID_TAREAS = int(os.getenv('TARGET_CHANNEL_ID_TAREAS', '0'))

class TaskPanel(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @app_commands.command(name='setup_panel_tareas', description='Publica el panel de tareas en el canal configurado (solo admins)')
    async def setup_panel_tareas(self, interaction: discord.Interaction):
        # Solo admins pueden ejecutar
        if not interaction.user.guild_permissions.administrator:
            await interaction.response.send_message('No tienes permisos para usar este comando.', ephemeral=True)
            return
        if TARGET_CHANNEL_ID_TAREAS == 0:
            await interaction.response.send_message('La variable de entorno TARGET_CHANNEL_ID_TAREAS no está configurada.', ephemeral=True)
            return
        canal = interaction.guild.get_channel(TARGET_CHANNEL_ID_TAREAS)
        if not canal:
            await interaction.response.send_message('No se encontró el canal configurado.', ephemeral=True)
            return
        embed = discord.Embed(
            title='Panel de Registro de Tareas',
            description='Presiona el botón para registrar una nueva tarea.',
            color=discord.Color.blue()
        )
        view = TaskPanelView()
        await canal.send(embed=embed, view=view)
        await interaction.response.send_message('Panel publicado correctamente.', ephemeral=True)

    async def cog_load(self):
        # Registrar el comando en el árbol de comandos
        self.bot.tree.add_command(self.setup_panel_tareas)

class TaskPanelView(discord.ui.View):
    def __init__(self):
        super().__init__(timeout=None)
        self.add_item(TaskRegisterButton())

class TaskRegisterButton(discord.ui.Button):
    def __init__(self):
        super().__init__(label='Registrar nueva tarea', style=discord.ButtonStyle.primary)

    async def callback(self, interaction: discord.Interaction):
        await interaction.response.send_message('Aquí irá el flujo de registro de tarea.', ephemeral=True)


async def setup(bot):
    await bot.add_cog(TaskPanel(bot)) 