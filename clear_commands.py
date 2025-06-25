from dotenv import load_dotenv
load_dotenv()

import os
import requests
import sys

# Variables de entorno necesarias
TOKEN = os.getenv('DISCORD_TOKEN')
CLIENT_ID = os.getenv('DISCORD_CLIENT_ID')
GUILD_ID = os.getenv('GUILD_ID')

if not TOKEN or not CLIENT_ID or not GUILD_ID:
    print('Faltan variables de entorno: DISCORD_TOKEN, DISCORD_CLIENT_ID o GUILD_ID')
    sys.exit(1)

headers = {
    'Authorization': f'Bot {TOKEN}',
    'Content-Type': 'application/json'
}

# Eliminar comandos de guild
guild_url = f'https://discord.com/api/v10/applications/{CLIENT_ID}/guilds/{GUILD_ID}/commands'
resp = requests.get(guild_url, headers=headers)
if resp.ok:
    commands = resp.json()
    print(f'Comandos de guild encontrados: {len(commands)}')
    for cmd in commands:
        del_url = f'{guild_url}/{cmd["id"]}'
        del_resp = requests.delete(del_url, headers=headers)
        if del_resp.ok:
            print(f'✅ Eliminado comando de guild: {cmd["name"]}')
        else:
            print(f'❌ Error al eliminar comando de guild: {cmd["name"]}')
else:
    print('No se pudieron obtener los comandos de guild')

# Eliminar comandos globales (por si acaso)
global_url = f'https://discord.com/api/v10/applications/{CLIENT_ID}/commands'
g_resp = requests.get(global_url, headers=headers)
if g_resp.ok:
    g_commands = g_resp.json()
    print(f'Comandos globales encontrados: {len(g_commands)}')
    for cmd in g_commands:
        del_url = f'{global_url}/{cmd["id"]}'
        del_resp = requests.delete(del_url, headers=headers)
        if del_resp.ok:
            print(f'✅ Eliminado comando global: {cmd["name"]}')
        else:
            print(f'❌ Error al eliminar comando global: {cmd["name"]}')
else:
    print('No se pudieron obtener los comandos globales')

print('Limpieza de comandos finalizada. Ahora ejecuta tu bot normalmente o el redeploy.') 