# Este módulo requiere 'discord.py' instalado en el entorno.
import discord
from discord.ext import commands
from discord import app_commands
import os
import config
import json
from pathlib import Path
from datetime import datetime
import utils.google_sheets as google_sheets

# Obtener el ID del canal desde la variable de entorno
target_channel_id = int(os.getenv('TARGET_CHANNEL_ID_TAREAS', '0'))
guild_id = int(getattr(config, 'GUILD_ID', 0))
print(f'[DEBUG] GUILD_ID usado para comandos slash: {guild_id}')

TAREAS_JSON_PATH = Path('data/tareas_activas.json')
print(f'[DEBUG] Ruta absoluta del JSON de tareas activas: {TAREAS_JSON_PATH.resolve()}')
TAREAS_JSON_PATH.parent.mkdir(parents=True, exist_ok=True)

def cargar_tareas_activas():
    if not TAREAS_JSON_PATH.exists():
        print('[DEBUG] El archivo JSON no existe, creando vacío.')
        try:
            with open(TAREAS_JSON_PATH, 'w', encoding='utf-8') as f:
                json.dump({}, f)
        except Exception as e:
            print(f'[ERROR] No se pudo crear el JSON: {e}')
        return {}
    with open(TAREAS_JSON_PATH, 'r', encoding='utf-8') as f:
        try:
            return json.load(f)
        except Exception as e:
            print(f'[ERROR] No se pudo leer el JSON: {e}')
            return {}

def guardar_tarea_activa(user_id, data):
    tareas = cargar_tareas_activas()
    tareas[user_id] = data
    try:
        with open(TAREAS_JSON_PATH, 'w', encoding='utf-8') as f:
            json.dump(tareas, f, ensure_ascii=False, indent=2)
        print(f'[DEBUG] Tarea guardada para usuario {user_id}')
    except Exception as e:
        print(f'[ERROR] No se pudo guardar el JSON: {e}')

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
        user_id = str(interaction.user.id)
        # --- Google Sheets ---
        client = google_sheets.initialize_google_sheets(config.GOOGLE_CREDENTIALS_JSON)
        spreadsheet = client.open_by_key(config.GOOGLE_SHEET_ID_TAREAS)
        sheet_activas = spreadsheet.worksheet('Tareas Activas')
        # Validar si ya tiene tarea activa
        if google_sheets.usuario_tiene_tarea_activa(sheet_activas, user_id):
            await interaction.response.send_message(
                '⚠️ Ya tienes una tarea activa. Finalízala antes de iniciar una nueva.',
                ephemeral=True
            )
            return
        await interaction.response.send_message(
            'Selecciona la tarea que vas a realizar:',
            view=TaskSelectMenuView(),
            ephemeral=True
        )

class TaskSelectMenu(discord.ui.Select):
    def __init__(self):
        options = [
            discord.SelectOption(label='Facturas B', value='Facturas B'),
            discord.SelectOption(label='Facturas A', value='Facturas A'),
            discord.SelectOption(label='Reclamos ML', value='Reclamos ML'),
            discord.SelectOption(label='Cambios / Devoluciones', value='Cambios / Devoluciones'),
            discord.SelectOption(label='Cancelaciones', value='Cancelaciones'),
            discord.SelectOption(label='Reembolsos', value='Reembolsos'),
            discord.SelectOption(label='Otra', value='Otra'),
        ]
        super().__init__(placeholder='Selecciona una tarea...', min_values=1, max_values=1, options=options)

    async def callback(self, interaction: discord.Interaction):
        seleccion = self.values[0]
        if seleccion == 'Otra':
            await interaction.response.send_modal(TaskObservacionesModal())
        else:
            await interaction.response.send_message(
                f'Tarea seleccionada: **{seleccion}**\nPresiona "Comenzar" para iniciar.',
                view=TaskStartButtonView(seleccion),
                ephemeral=True
            )

class TaskSelectMenuView(discord.ui.View):
    def __init__(self):
        super().__init__(timeout=120)
        self.add_item(TaskSelectMenu())

class TaskStartButtonView(discord.ui.View):
    def __init__(self, tarea):
        super().__init__(timeout=60)
        self.add_item(TaskStartButton(tarea))

class TaskStartButton(discord.ui.Button):
    def __init__(self, tarea):
        super().__init__(label='Comenzar', style=discord.ButtonStyle.success)
        self.tarea = tarea

    async def callback(self, interaction: discord.Interaction):
        user_id = str(interaction.user.id)
        # --- Google Sheets ---
        client = google_sheets.initialize_google_sheets(config.GOOGLE_CREDENTIALS_JSON)
        spreadsheet = client.open_by_key(config.GOOGLE_SHEET_ID_TAREAS)
        sheet_activas = spreadsheet.worksheet('Tareas Activas')
        sheet_historial = spreadsheet.worksheet('Historial')
        usuario = str(interaction.user)
        tarea = self.tarea
        observaciones = ''
        inicio = datetime.now().strftime('%d/%m/%Y %H:%M:%S')
        # Registrar tarea activa
        google_sheets.registrar_tarea_activa(sheet_activas, user_id, usuario, tarea, observaciones, inicio)
        # Agregar evento al historial
        google_sheets.agregar_evento_historial(sheet_historial, user_id, usuario, tarea, observaciones, inicio, fin='', estado='Iniciada')
        await interaction.response.send_message(f'¡Tarea "{tarea}" iniciada y registrada!', ephemeral=True)

class TaskObservacionesModal(discord.ui.Modal, title='Registrar Observaciones'):
    observaciones = discord.ui.TextInput(label='Observaciones (opcional)', required=False, style=discord.TextStyle.paragraph)

    async def on_submit(self, interaction: discord.Interaction):
        user_id = str(interaction.user.id)
        # --- Google Sheets ---
        client = google_sheets.initialize_google_sheets(config.GOOGLE_CREDENTIALS_JSON)
        spreadsheet = client.open_by_key(config.GOOGLE_SHEET_ID_TAREAS)
        sheet_activas = spreadsheet.worksheet('Tareas Activas')
        sheet_historial = spreadsheet.worksheet('Historial')
        usuario = str(interaction.user)
        tarea = 'Otra'
        obs = self.observaciones.value.strip()
        inicio = datetime.now().strftime('%d/%m/%Y %H:%M:%S')
        google_sheets.registrar_tarea_activa(sheet_activas, user_id, usuario, tarea, obs, inicio)
        google_sheets.agregar_evento_historial(sheet_historial, user_id, usuario, tarea, obs, inicio, fin='', estado='Iniciada')
        await interaction.response.send_message(f'¡Tarea "Otra" iniciada y registrada! Observaciones: {obs}', ephemeral=True)

async def setup(bot):
    print('[DEBUG] Ejecutando setup() de TaskPanel')
    await bot.add_cog(TaskPanel(bot))
    print('[DEBUG] TaskPanel Cog agregado al bot') 