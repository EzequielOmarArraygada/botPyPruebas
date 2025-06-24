# Este módulo requiere 'discord.py' instalado en el entorno.
import discord
from discord.ext import commands
from discord import app_commands
import os
import config

# Obtener el ID del canal desde la variable de entorno
target_channel_id = int(os.getenv('TARGET_CHANNEL_ID_TAREAS', '0'))
guild_id = int(getattr(config, 'GUILD_ID', 0))
print(f'[DEBUG] GUILD_ID usado para comandos slash: {guild_id}')

def guilds_decorator():
    if guild_id:
        return app_commands.guilds(discord.Object(id=guild_id))
    return lambda x: x

class TaskPanel(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        print('[DEBUG] TaskPanel Cog inicializado')

    @guilds_decorator()
    @app_commands.command(name='setup_panel_tareas', description='Publica el panel de tareas en el canal configurado (solo admins)')
    async def setup_panel_tareas(self, interaction: discord.Interaction):
        print('[DEBUG] Ejecutando /setup_panel_tareas')
        # Solo admins pueden ejecutar
        if not interaction.user.guild_permissions.administrator:
            await interaction.response.send_message('No tienes permisos para usar este comando.', ephemeral=True)
            return
        if target_channel_id == 0:
            await interaction.response.send_message('La variable de entorno TARGET_CHANNEL_ID_TAREAS no está configurada.', ephemeral=True)
            return
        canal = interaction.guild.get_channel(target_channel_id)
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

    @guilds_decorator()
    @app_commands.command(name='prueba', description='Comando de prueba')
    async def prueba(self, interaction: discord.Interaction):
        print('[DEBUG] Ejecutando /prueba')
        await interaction.response.send_message('¡Funciona el comando de prueba!', ephemeral=True)

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
    print('[DEBUG] Ejecutando setup() de TaskPanel')
    await bot.add_cog(TaskPanel(bot))
    print('[DEBUG] TaskPanel Cog agregado al bot') 