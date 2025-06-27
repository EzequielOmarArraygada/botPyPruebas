# CS-Bot (Python)

Este es un port en Python del bot original de Discord escrito en JavaScript. Utiliza `discord.py` y otras librerías para replicar la funcionalidad original.

## Funcionalidades

- **Comando `/factura-a`**: Registro de Factura A con formulario modal
- **Comando `/tracking`**: Consulta de estado de envíos de Andreani
- **Comando `/agregar-caso`**: Registro de casos con flujo de selección
- **Comando `/buscar-caso`**: Búsqueda de casos por número de pedido
- **Comando `/manual`**: Consulta al manual de procedimientos usando IA (Gemini)
- **Verificación automática de errores**: Monitoreo periódico de hojas de Google Sheets
- **Gestión de archivos**: Manejo de archivos adjuntos y carga a Google Drive
- **Reembolsos**: Inicia el flujo de registro de reembolsos y guarda la información en Google Sheets

## Estructura del Proyecto

```
CS-Bot/
├── main.py                 # Archivo principal del bot
├── config.py              # Configuración y variables de entorno
├── requirements.txt       # Dependencias de Python
├── events/               # Módulos de eventos de Discord
│   ├── interaction_commands.py
│   ├── interaction_selects.py
│   ├── attachment_handler.py
│   └── guild_member_add.py
├── interactions/         # Módulos de interacciones
│   ├── modals.py
│   └── select_menus.py
└── utils/               # Utilidades y servicios
    ├── google_sheets.py
    ├── google_drive.py
    ├── andreani.py
    ├── qa_service.py
    ├── manual_processor.py
    └── state_manager.py
```

## Instalación

1. **Clona el repositorio**:
   ```bash
   git clone <repository-url>
   cd CS-Bot
   ```

2. **Crea un entorno virtual** (recomendado):
   ```bash
   python -m venv myenv
   # En Windows:
   myenv\Scripts\activate
   # En Linux/Mac:
   source myenv/bin/activate
   ```

3. **Instala las dependencias**:
   ```bash
   pip install -r requirements.txt
   ```

4. **Configura las variables de entorno**:
   Crea un archivo `.env` en la raíz del proyecto con las siguientes variables:

   ```env
   # Discord Configuration
   DISCORD_TOKEN=your_discord_bot_token_here
   GUILD_ID=your_guild_id_here
   HELP_CHANNEL_ID=your_help_channel_id_here

   # Discord Channel IDs
   TARGET_CHANNEL_ID_FAC_A=your_factura_a_channel_id_here
   TARGET_CHANNEL_ID_ENVIOS=your_envios_channel_id_here
   TARGET_CHANNEL_ID_CASOS=your_casos_channel_id_here
   TARGET_CHANNEL_ID_BUSCAR_CASO=your_buscar_caso_channel_id_here
   TARGET_CHANNEL_ID_CASOS_REEMBOLSOS=your_reembolsos_channel_id_here

   # Andreani API
   ANDREANI_API_AUTH=your_andreani_auth_header_here

   # Google Services
   GOOGLE_CREDENTIALS_JSON={"type":"service_account",...}

   # Google Sheets IDs
   GOOGLE_SHEET_ID_FAC_A=your_factura_a_sheet_id_here
   GOOGLE_SHEET_RANGE_FAC_A=your_factura_a_sheet_range_here
   GOOGLE_SHEET_ID_CASOS=your_casos_sheet_id_here
   GOOGLE_SHEET_RANGE_CASOS=your_casos_sheet_range_here
   GOOGLE_SHEET_RANGE_CASOS_READ=your_casos_read_range_here
   GOOGLE_SHEET_ID_REEMBOLSOS=your_reembolsos_sheet_id_here
   GOOGLE_SHEET_RANGE_REEMBOLSOS=your_reembolsos_sheet_range_here
   GOOGLE_SHEET_SEARCH_SHEET_ID=your_search_sheet_id_here
   GOOGLE_SHEET_SEARCH_SHEETS=Sheet1,Sheet2,Sheet3

   # Google Drive
   PARENT_DRIVE_FOLDER_ID=your_drive_folder_id_here
   MANUAL_DRIVE_FILE_ID=your_manual_file_id_here

   # Gemini AI
   GEMINI_API_KEY=your_gemini_api_key_here

   # Discord Category
   TARGET_CATEGORY_ID=your_target_category_id_here

   # Error Check Interval (in milliseconds, default: 4 hours)
   ERROR_CHECK_INTERVAL_MS=14400000
   ```

5. **Ejecuta el bot**:
   ```bash
   python main.py
   ```

## Redeploy de Comandos

Si necesitas actualizar los comandos del bot o después de hacer cambios en el código, usa el script de redeploy:

```bash
python redeploy.py
```

**⚠️ Importante**: 
- Este script sincroniza los comandos slash y registra las views persistentes
- Los botones del panel de tareas funcionarán correctamente después del redeploy
- No uses el archivo `deploy_commands.py` (ya no existe), usa solo `redeploy.py`

## Configuración Requerida

### Discord Bot
- Token del bot de Discord
- IDs de los canales específicos para cada comando
- ID del servidor (Guild)
- Permisos necesarios: Send Messages, Use Slash Commands, Attach Files

### Google Services
- Cuenta de servicio de Google Cloud Platform
- APIs habilitadas: Google Sheets API, Google Drive API
- Credenciales JSON de la cuenta de servicio
- IDs de las hojas de Google Sheets

### Andreani API
- Token de autorización para la API de tracking de Andreani

### Gemini AI
- API Key de Google Gemini para el comando del manual

## Comandos Disponibles

- `/factura-a` - Inicia el formulario de registro de Factura A
- `/tracking <numero>` - Consulta el estado de un envío de Andreani
- `/agregar-caso` - Inicia el registro de un nuevo caso
- `/buscar-caso <pedido>` - Busca un caso por número de pedido
- `/manual <pregunta>` - Consulta al manual de procedimientos
- `/reembolsos` - Inicia el flujo de registro de reembolsos

## Notas Importantes

- Algunas funciones requieren credenciales específicas de Google API
- El bot verifica automáticamente errores en las hojas de Google Sheets cada 4 horas por defecto
- Los comandos están restringidos a canales específicos para mantener la organización
- El manual se carga automáticamente desde Google Drive al iniciar el bot
- Asegúrate de tener los permisos necesarios en Discord y Google

## Solución de Problemas

1. **Error de credenciales de Google**: Verifica que el JSON de credenciales sea válido y tenga los permisos correctos
2. **Bot no responde**: Verifica que el token de Discord sea correcto y el bot tenga los permisos necesarios
3. **Comandos no aparecen**: Asegúrate de que el bot tenga permisos de aplicación en el servidor
4. **Error en tracking**: Verifica que el token de Andreani sea válido y esté actualizado

## Dependencias

- discord.py - Cliente de Discord
- python-dotenv - Manejo de variables de entorno
- gspread - API de Google Sheets
- google-api-python-client - Cliente de Google APIs
- requests - Cliente HTTP
- pytz - Manejo de zonas horarias
- google-generativeai - API de Gemini AI

## Configuración de Variables de Entorno

### Variables Requeridas
```env
# Discord
DISCORD_TOKEN=tu_token_de_discord
GUILD_ID=id_del_servidor

# Google Services
GOOGLE_CREDENTIALS_JSON={"tu":"json_de_credenciales"}

# IDs de Canales (Obligatorios para el panel de comandos)
TARGET_CHANNEL_ID_FAC_A=id_canal_factura_a
TARGET_CHANNEL_ID_ENVIOS=id_canal_envios
TARGET_CHANNEL_ID_CASOS=id_canal_casos
TARGET_CHANNEL_ID_CASOS_ENVIOS=id_canal_solicitudes_envios
TARGET_CHANNEL_ID_BUSCAR_CASO=id_canal_buscar_caso
TARGET_CHANNEL_ID_TAREAS=id_canal_tareas
TARGET_CHANNEL_ID_TAREAS_REGISTRO=id_canal_registro_tareas
TARGET_CHANNEL_ID_GUIA_COMANDOS=id_canal_guia_comandos
TARGET_CHANNEL_ID_CASOS_REEMBOLSOS=id_canal_reembolsos

# Google Sheets IDs
GOOGLE_SHEET_ID_FAC_A=id_hoja_factura_a
GOOGLE_SHEET_ID_CASOS=id_hoja_casos
GOOGLE_SHEET_ID_TAREAS=id_hoja_tareas
GOOGLE_SHEET_SEARCH_SHEET_ID=id_hoja_busqueda
GOOGLE_SHEET_RANGE_REEMBOLSOS=REEMBOLSOS!A:L

# API de Andreani
ANDREANI_API_AUTH=tu_header_de_autenticacion

# Gemini AI (Opcional)
GEMINI_API_KEY=tu_api_key_gemini
MANUAL_DRIVE_FILE_ID=id_archivo_manual
```

### Variables Opcionales
```env
# Categoría objetivo para comandos
TARGET_CATEGORY_ID=id_categoria

# Intervalo de verificación de errores (en milisegundos, por defecto 4 horas)
ERROR_CHECK_INTERVAL_MS=14400000

# Canales de ayuda
HELP_CHANNEL_ID=id_canal_ayuda
```

## Panel de Comandos

### Configuración Requerida
Para que el panel de comandos funcione correctamente, asegúrate de configurar todas las variables de canal:

1. **TARGET_CHANNEL_ID_CASOS_ENVIOS**: Canal para solicitudes de envíos (cambio de dirección, reenvío, etc.)
2. **TARGET_CHANNEL_ID_GUIA_COMANDOS**: Canal donde se publicará el panel de comandos

### Comandos del Panel
- **Factura A**: Inicia solicitud de facturación tipo A
- **Cambios/Devoluciones**: Registra casos de cambios o devoluciones
- **Solicitudes de Envíos**: Maneja solicitudes sobre envíos (cambio de dirección, reenvío, etc.)
- **Tracking**: Consulta el estado de envíos de Andreani
- **Buscar Caso**: Busca casos por número de pedido
- **Reembolsos**: Inicia el flujo de registro de reembolsos

### Solución de Problemas

#### Error: "No se configuró el canal de Solicitudes de Envíos"
- Asegúrate de que `TARGET_CHANNEL_ID_CASOS_ENVIOS` esté configurado en tu archivo `.env`
- Verifica que el ID del canal sea correcto

#### Error: "Error en la interacción"
- Los errores de interacción han sido mejorados con manejo de excepciones
- Verifica que todas las variables de configuración estén correctamente definidas
- Revisa los logs del bot para más detalles sobre errores específicos

## Instalación y Uso

1. Clona el repositorio
2. Instala las dependencias: `pip install -r requirements.txt`
3. Configura las variables de entorno en un archivo `.env`
4. Ejecuta el bot: `python main.py`

## Comandos Disponibles

### Comandos de Administración
- `/setup_panel_comandos`: Publica el panel de comandos (solo admins)
- `/setup_panel_tareas`: Publica el panel de tareas (solo admins)

### Comandos de Usuario
- `/factura-a`: Solicita registro de Factura A
- `/tracking <numero>`: Consulta estado de envío
- `/cambios-devoluciones`: Inicia registro de caso
- `/buscar-caso <pedido>`: Busca caso por número de pedido
- `/solicitudes-envios`: Inicia solicitud sobre envíos
- `/reembolsos`: Inicia el flujo de registro de reembolsos

## Notas de Desarrollo

### Mejoras Recientes
- ✅ Manejo mejorado de errores en botones del panel
- ✅ Validación de variables de configuración
- ✅ Mensajes de error más informativos
- ✅ Corrección del botón "Solicitudes de Envíos"

### Variables Faltantes Agregadas
- `TARGET_CHANNEL_ID_CASOS_ENVIOS`: Para el canal de solicitudes de envíos
- `TARGET_CHANNEL_ID_GUIA_COMANDOS`: Para el canal de guía de comandos
- `TARGET_CHANNEL_ID_CASOS_REEMBOLSOS`: Para el canal de reembolsos

### Manejo de Errores
Todos los botones del panel ahora incluyen:
- Try-catch blocks para capturar excepciones
- Mensajes de error informativos para el usuario
- Logs detallados para debugging
- Validación de permisos y configuración 