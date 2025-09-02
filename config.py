import os, sys, json
from dotenv import load_dotenv

# Cargar variables de entorno desde .env
load_dotenv()

# Configuración de Discord
TOKEN = os.getenv('DISCORD_TOKEN')
GUILD_ID = os.getenv('GUILD_ID')

# Configuración de permisos para comandos de setup
# IDs de usuarios que pueden usar comandos de setup (además de administradores)
SETUP_USER_IDS = ['1297896768523993120', '894659916525109288']
SETUP_BO_ROL= 1300888951619584101

# IDs de canales específicos
HELP_CHANNEL_ID = 1370019052755488808
TARGET_CHANNEL_ID_FAC_A = 1369820702026502244
TARGET_CHANNEL_ID_FAC_B = 1369820702026502244
TARGET_CHANNEL_ID_NC = 1369820702026502244
TARGET_CHANNEL_ID_ENVIOS = 1388162681164529846
TARGET_CHANNEL_ID_CASOS = 1370035840918487193
TARGET_CHANNEL_ID_BUSCAR_CASO = 1364993141685620869
TARGET_CATEGORY_ID = 1385037093742448651
TARGET_LINKS = 1412456421722816512


TARGET_CHANNEL_ID_TAREAS = 1387103181552488561
TARGET_CHANNEL_ID_TAREAS_REGISTRO = 1387103213366280376
TARGET_CHANNEL_ID_GUIA_COMANDOS = 1370019052755488808
TARGET_CHANNEL_ID_REEMBOLSOS = 1388241730746192013
TARGET_CHANNEL_ID_CASOS_ENVIOS = 1388162681164529846
TARGET_CHANNEL_ID_CASOS_CANCELACION = 1388638546306400286
TARGET_CHANNEL_ID_CASOS_RECLAMOS_ML = 1388921439578492958
TARGET_CHANNEL_ID_CASOS_PIEZA_FALTANTE = 1388941378045743284
TARGET_CHANNEL_ID_ICBC = 1364993141685620869
TARGET_CHANNEL_ID_LOGS = 1396872530655973416
TARGET_CHANNEL_ID_LINKS = 1412456421722816512

# API de Andreani
ANDREANI_AUTH_HEADER = os.getenv('ANDREANI_API_AUTH')

# Google Services
raw = os.getenv('GOOGLE_CREDENTIALS_PATH') or os.getenv('GOOGLE_CREDENTIALS_JSON')
if not raw:
    print("⚠️ Advertencia: no se ha proporcionado ni GOOGLE_CREDENTIALS_PATH ni GOOGLE_CREDENTIALS_JSON.")
    print("El bot funcionará sin las APIs de Google.")
    GOOGLE_CREDENTIALS = None
    GOOGLE_CREDENTIALS_JSON = None
    GOOGLE_CREDENTIALS_PATH = None

elif raw.lstrip().startswith('{'):
    # Llegó el JSON completo en ENV
    try:
        GOOGLE_CREDENTIALS = json.loads(raw)
        GOOGLE_CREDENTIALS_PATH = None
        # Alias para compatibilidad con código existente
        GOOGLE_CREDENTIALS_JSON = GOOGLE_CREDENTIALS
        print("✅ Credenciales cargadas desde JSON en ENV.")
    except json.JSONDecodeError as e:
        print("Error CRÍTICO parseando JSON de credenciales:", e)
        sys.exit(1)
else:
    # Llegó una ruta de fichero local (para desarrollo)
    try:
        with open(raw, encoding='utf-8') as f:
            GOOGLE_CREDENTIALS = json.load(f)
        GOOGLE_CREDENTIALS_PATH = raw
        # Alias para compatibilidad con código existente
        GOOGLE_CREDENTIALS_JSON = GOOGLE_CREDENTIALS
        print("✅ Credenciales cargadas desde fichero local.")
    except Exception as e:
        print("Error CRÍTICO leyendo fichero de credenciales:", e)
        sys.exit(1)

SPREADSHEET_ID_FAC_A = "1E2NMgo2V2lB2JPafV5rcpIyj9Xb9Q-NJJlYLY-fzysE"
SHEET_RANGE_FAC_A = "FacA!A:F"  
SHEET_RANGE_FAC_B = "FacB!A:G"
SHEET_RANGE_NC = "NC!A:G"
SPREADSHEET_ID_CASOS = "1SYMd88ISCk75SEapzwuQiRvJD2VBgYdPqivat60uRhg"
SHEET_RANGE_CASOS = "SOLICITUDES BGH 2025!A:F"
SHEET_RANGE_CASOS_READ = "SOLICITUDES BGH 2025!A:K"
SPREADSHEET_ID_BUSCAR_CASO = "1SYMd88ISCk75SEapzwuQiRvJD2VBgYdPqivat60uRhg"
SPREADSHEET_ID_ICBC ="1nfhVym0dmM15oBB4Fmc6WTeoNPfaWwKH_cHZkxKO3I4"
SHEETS_TO_SEARCH = "SOLICITUDES BGH 2025,CAMBIO DE DIRECCIÓN 2025,Cancelaciones 2025,REEMBOLSOS,SOLICITUDES CON RECLAMO ABIERTO 2025 ML,Casos de Piezas Faltantes 2025".split(',') if "SOLICITUDES BGH 2025,CAMBIO DE DIRECCIÓN 2025,Cancelaciones 2025,REEMBOLSOS,SOLICITUDES CON RECLAMO ABIERTO 2025 ML,Casos de Piezas Faltantes 2025" else []
PARENT_DRIVE_FOLDER_ID = "11HEcU4oKciXFMIPaHyz5UjgnXNVnalzI"
GOOGLE_SHEET_ID_TAREAS = "1546Lue8br4yxMy4_V2EvyWjPbJiBUTNfucb7TDheCfU"
GOOGLE_SHEET_RANGE_ENVIOS = "CAMBIO DE DIRECCIÓN 2025!A:M"
SHEET_RANGE_REEMBOLSOS = "REEMBOLSOS!A:L"
GOOGLE_SHEET_RANGE_CANCELACIONES = "Cancelaciones 2025!A:M"
GOOGLE_SHEET_RANGE_RECLAMOS_ML = "SOLICITUDES CON RECLAMO ABIERTO 2025 ML!A:L"
GOOGLE_SHEET_RANGE_PIEZA_FALTANTE = "Casos de Piezas Faltantes 2025!A:J"
GOOGLE_SHEET_RANGE_ICBC = "ICBC!A:F"

# Gemini AI
GEMINI_API_KEY = os.getenv('GEMINI_API_KEY')
MANUAL_DRIVE_FILE_ID = os.getenv('MANUAL_DRIVE_FILE_ID')

# --- Intervalos ---
# Intervalo de chequeo en minutos (default: 240)
try:
    ERROR_CHECK_INTERVAL_MIN = int(os.getenv('ERROR_CHECK_INTERVAL_MIN', '240'))
except ValueError:
    print("ERROR_CHECK_INTERVAL_MIN no es un entero válido; usando 240 min por defecto.")
    ERROR_CHECK_INTERVAL_MIN = 240

# Validaciones básicas
if not TOKEN:
    print("⚠️ Advertencia: La variable de entorno DISCORD_TOKEN no está configurada.")
    print("El bot no podrá conectarse a Discord sin el token.")

if not GUILD_ID:
    print("Advertencia: GUILD_ID no configurado. Algunas funcionalidades podrían no funcionar correctamente.")

if not GEMINI_API_KEY:
    print("Advertencia: GEMINI_API_KEY no configurada. El comando del manual no funcionará.")

if not MANUAL_DRIVE_FILE_ID:
    print("Advertencia: MANUAL_DRIVE_FILE_ID no configurado. El comando del manual no funcionará.")

# --- Prefijo de comandos ---
PREFIX = os.getenv('PREFIX', '-')

# Mapeo de rangos de Google Sheets a canales de Discord para verificación de errores
MAPA_RANGOS_ERRORES = {
    GOOGLE_SHEET_RANGE_ENVIOS: TARGET_CHANNEL_ID_CASOS_ENVIOS,
    GOOGLE_SHEET_RANGE_RECLAMOS_ML: TARGET_CHANNEL_ID_CASOS_RECLAMOS_ML,
    GOOGLE_SHEET_RANGE_PIEZA_FALTANTE: TARGET_CHANNEL_ID_CASOS_PIEZA_FALTANTE,
    GOOGLE_SHEET_RANGE_CANCELACIONES: TARGET_CHANNEL_ID_CASOS_CANCELACION,
    SHEET_RANGE_REEMBOLSOS: TARGET_CHANNEL_ID_REEMBOLSOS,
    SHEET_RANGE_CASOS_READ: TARGET_CHANNEL_ID_CASOS,
}
