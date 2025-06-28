# CS-Bot (Python) - Bot de Gestión Comercial

Este es un bot de Discord desarrollado en Python para automatizar y gestionar procesos comerciales. Utiliza `discord.py` y múltiples APIs para proporcionar una solución integral de gestión empresarial.

## 🚀 Funcionalidades Principales

### 📋 Gestión de Documentos
- **Comando `/factura-a`**: Registro de Factura A con formulario modal y carga de archivos adjuntos
- **Comando `/manual <pregunta>`**: Consulta inteligente al manual de procedimientos usando IA (Gemini)

### 📦 Gestión de Envíos
- **Comando `/tracking <numero>`**: Consulta de estado de envíos de Andreani con historial completo
- **Comando `/solicitudes-envios`**: Registro de solicitudes sobre envíos (cambio de dirección, reenvío, actualizar tracking)

### 🎯 Gestión de Casos
- **Comando `/cambios-devoluciones`**: Registro de casos con flujo de selección completo
- **Comando `/cancelaciones`**: Registro de cancelaciones con selección de tipo y formulario
- **Comando `/buscar-caso <pedido>`**: Búsqueda de casos por número de pedido en múltiples hojas
- **Comando `/reembolsos`**: Inicia el flujo de registro de reembolsos

### ⏱️ Control de Tareas
- **Panel de Tareas**: Sistema de registro y control de tiempo de actividades
- **Comandos de Administración**: `/setup_panel_tareas` y `/setup_panel_comandos`

### 🔄 Automatizaciones
- **Verificación automática de errores**: Monitoreo periódico de hojas de Google Sheets
- **Gestión de archivos**: Manejo automático de archivos adjuntos y carga a Google Drive
- **Sistema de estados**: Gestión de flujos complejos con persistencia

## 🏗️ Estructura del Proyecto

```
CS-Bot/
├── main.py                 # Archivo principal del bot
├── config.py              # Configuración y variables de entorno
├── requirements.txt       # Dependencias de Python
├── redeploy.py           # Script para redeploy de comandos
├── test_bot.py           # Suite de tests automatizados
├── events/               # Módulos de eventos de Discord
│   ├── interaction_commands.py  # Comandos slash principales
│   ├── interaction_selects.py   # Manejo de menús de selección
│   ├── attachment_handler.py    # Gestión de archivos adjuntos
│   └── guild_member_add.py      # Eventos de miembros
├── interactions/         # Módulos de interacciones
│   ├── modals.py         # Formularios modales
│   └── select_menus.py   # Menús de selección
├── tasks/               # Módulos de tareas
│   └── panel.py         # Panel de control de tareas
└── utils/               # Utilidades y servicios
    ├── google_sheets.py     # Integración con Google Sheets
    ├── google_drive.py      # Integración con Google Drive
    ├── andreani.py          # API de tracking de Andreani
    ├── qa_service.py        # Servicio de IA para consultas
    ├── manual_processor.py  # Procesamiento del manual
    └── state_manager.py     # Gestión de estados de usuario
```

## 📋 Comandos Disponibles

### Comandos de Usuario
| Comando | Descripción | Canal Restringido |
|---------|-------------|-------------------|
| `/factura-a` | Registro de Factura A con formulario | Canal específico |
| `/tracking <numero>` | Consulta estado de envío Andreani | Canal de envíos |
| `/cambios-devoluciones` | Registro de casos comerciales | Canal de casos |
| `/buscar-caso <pedido>` | Búsqueda de casos por pedido | Canal de búsqueda |
| `/solicitudes-envios` | Solicitudes sobre envíos | Canal de casos |
| `/reembolsos` | Registro de reembolsos | Canal de reembolsos |
| `/cancelaciones` | Registro de cancelaciones (CANCELAR/SEGUIMIENTO) | Canal de cancelaciones |
| `/manual <pregunta>` | Consulta al manual con IA | Cualquier canal |

### Comandos de Administración
| Comando | Descripción | Permisos |
|---------|-------------|----------|
| `/setup_panel_tareas` | Publica panel de tareas | Administrador |
| `/setup_panel_comandos` | Publica panel de comandos | Administrador |
| `/testping` | Verifica estado del bot | DM |

## 🛠️ Instalación

### Prerrequisitos
- Python 3.8 o superior
- Cuenta de Discord Developer
- Proyecto en Google Cloud Platform
- Token de API de Andreani
- API Key de Gemini AI

### 1. Clonar el Repositorio
```bash
git clone <repository-url>
cd CS-Bot
```

### 2. Crear Entorno Virtual
```bash
python -m venv myenv
# En Windows:
myenv\Scripts\activate
# En Linux/Mac:
source myenv/bin/activate
```

### 3. Instalar Dependencias
```bash
pip install -r requirements.txt
```

### 4. Configurar Variables de Entorno
Crea un archivo `.env` en la raíz del proyecto:

```env
# Discord Configuration
DISCORD_TOKEN=your_discord_bot_token_here
GUILD_ID=your_guild_id_here
HELP_CHANNEL_ID=your_help_channel_id_here

# Discord Channel IDs (Obligatorios)
TARGET_CHANNEL_ID_FAC_A=your_factura_a_channel_id_here
TARGET_CHANNEL_ID_ENVIOS=your_envios_channel_id_here
TARGET_CHANNEL_ID_CASOS=your_casos_channel_id_here
TARGET_CHANNEL_ID_BUSCAR_CASO=your_buscar_caso_channel_id_here
TARGET_CHANNEL_ID_CASOS_REEMBOLSOS=your_reembolsos_channel_id_here
TARGET_CHANNEL_ID_TAREAS=your_tareas_channel_id_here
TARGET_CHANNEL_ID_TAREAS_REGISTRO=your_registro_tareas_channel_id_here
TARGET_CHANNEL_ID_GUIA_COMANDOS=your_guia_comandos_channel_id_here

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
GOOGLE_SHEET_ID_TAREAS=your_tareas_sheet_id_here

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

### 5. Ejecutar el Bot
```bash
python main.py
```

## 🔄 Redeploy de Comandos

Para actualizar comandos después de cambios:

```bash
python redeploy.py
```

**⚠️ Importante**: 
- Este script sincroniza los comandos slash y registra las views persistentes
- Los botones del panel de tareas funcionarán correctamente después del redeploy
- No uses el archivo `deploy_commands.py` (ya no existe), usa solo `redeploy.py`

## 🧪 Testing

### Ejecutar Tests
```bash
python test_bot.py
```

### Cobertura de Tests
Los tests cubren:
- ✅ Configuración del bot
- ✅ Comandos slash principales
- ✅ Formularios modales
- ✅ Integración con Google Sheets
- ✅ API de Andreani
- ✅ Gestión de estados
- ✅ Manejo de archivos adjuntos
- ✅ Panel de tareas
- ✅ Validaciones de entrada

### Tests Disponibles
- **Test de Configuración**: Verifica variables de entorno
- **Test de Comandos**: Valida funcionamiento de comandos slash
- **Test de Modales**: Prueba formularios de entrada
- **Test de APIs**: Verifica integraciones externas
- **Test de Estados**: Valida gestión de flujos
- **Test de Archivos**: Prueba manejo de adjuntos

## 🔧 Configuración Requerida

### Discord Bot
- Token del bot de Discord
- IDs de los canales específicos para cada comando
- ID del servidor (Guild)
- Permisos necesarios: Send Messages, Use Slash Commands, Attach Files, Manage Messages

### Google Services
- Cuenta de servicio de Google Cloud Platform
- APIs habilitadas: Google Sheets API, Google Drive API
- Credenciales JSON de la cuenta de servicio
- IDs de las hojas de Google Sheets

### Andreani API
- Token de autorización para la API de tracking de Andreani

### Gemini AI
- API Key de Google Gemini para el comando del manual

## 📊 Flujos de Trabajo

### Flujo de Factura A
1. Usuario ejecuta `/factura-a`
2. Se abre formulario modal
3. Usuario completa datos
4. Se valida duplicado en Google Sheets
5. Se registra en hoja de cálculo
6. Se solicita carga de archivos adjuntos

### Flujo de Tracking
1. Usuario ejecuta `/tracking <numero>`
2. Se consulta API de Andreani
3. Se procesa respuesta
4. Se muestra estado actual e historial

### Flujo de Casos
1. Usuario ejecuta `/cambios-devoluciones`
2. Se muestra menú de selección
3. Usuario selecciona tipo de solicitud
4. Se abre formulario modal
5. Se valida y registra en Google Sheets

## 🚨 Solución de Problemas

### Errores Comunes

1. **Error de credenciales de Google**
   ```
   Error: GOOGLE_CREDENTIALS_JSON no es un JSON válido
   ```
   **Solución**: Verifica que el JSON de credenciales sea válido y tenga los permisos correctos

2. **Bot no responde**
   ```
   Error al conectar con Discord
   ```
   **Solución**: Verifica que el token de Discord sea correcto y el bot tenga los permisos necesarios

3. **Comandos no aparecen**
   ```
   Error al sincronizar comandos
   ```
   **Solución**: Asegúrate de que el bot tenga permisos de aplicación en el servidor

4. **Error en tracking**
   ```
   Error al consultar la API de tracking de Andreani
   ```
   **Solución**: Verifica que el token de Andreani sea válido y esté actualizado

### Logs y Debugging
- El bot genera logs detallados en la consola
- Usa `/testping` para verificar conectividad
- Revisa la configuración con `check_config.py`

## 📚 Dependencias

| Paquete | Versión | Propósito |
|---------|---------|-----------|
| discord.py | Latest | Cliente de Discord |
| python-dotenv | Latest | Manejo de variables de entorno |
| gspread | Latest | API de Google Sheets |
| google-api-python-client | Latest | Cliente de Google APIs |
| google-auth-httplib2 | Latest | Autenticación Google |
| google-auth-oauthlib | Latest | OAuth Google |
| requests | Latest | Cliente HTTP |
| pytz | Latest | Manejo de zonas horarias |
| google-generativeai | Latest | API de Gemini AI |

## 🤝 Contribución

1. Fork el proyecto
2. Crea una rama para tu feature (`git checkout -b feature/AmazingFeature`)
3. Commit tus cambios (`git commit -m 'Add some AmazingFeature'`)
4. Push a la rama (`git push origin feature/AmazingFeature`)
5. Abre un Pull Request

## 📄 Licencia

Este proyecto está bajo la Licencia MIT. Ver el archivo `LICENSE` para más detalles.

## 📞 Soporte

Para soporte técnico o preguntas:
- Revisa la documentación
- Ejecuta los tests para diagnosticar problemas
- Verifica la configuración con `check_config.py`

---

**Desarrollado para automatizar y optimizar procesos comerciales con Discord y Google Workspace.** 