# Archivo de ejemplo de configuración
# Copia este archivo como .env y llena los valores reales

# Discord Configuration
DISCORD_TOKEN=your_discord_bot_token_here
DISCORD_CLIENT_ID=your_discord_client_id_here
GUILD_ID=your_guild_id_here
HELP_CHANNEL_ID=your_help_channel_id_here

# Discord Channel IDs
TARGET_CHANNEL_ID_FAC_A=your_factura_a_channel_id_here
TARGET_CHANNEL_ID_ENVIOS=your_envios_channel_id_here
TARGET_CHANNEL_ID_CASOS=your_casos_channel_id_here
TARGET_CHANNEL_ID_BUSCAR_CASO=your_buscar_caso_channel_id_here
TARGET_CHANNEL_ID_TAREAS_REGISTRO=your_tareas_registro_channel_id_here

# Andreani API
ANDREANI_API_AUTH=your_andreani_auth_header_here

# Google Services
GOOGLE_CREDENTIALS_JSON={"type":"service_account","project_id":"your_project_id","private_key_id":"your_private_key_id","private_key":"-----BEGIN PRIVATE KEY-----\nyour_private_key_here\n-----END PRIVATE KEY-----\n","client_email":"your_service_account_email@your_project.iam.gserviceaccount.com","client_id":"your_client_id","auth_uri":"https://accounts.google.com/o/oauth2/auth","token_uri":"https://oauth2.googleapis.com/token","auth_provider_x509_cert_url":"https://www.googleapis.com/oauth2/v1/certs","client_x509_cert_url":"https://www.googleapis.com/robot/v1/metadata/x509/your_service_account_email%40your_project.iam.gserviceaccount.com"}

# Google Sheets IDs
GOOGLE_SHEET_ID_FAC_A=your_factura_a_sheet_id_here
GOOGLE_SHEET_RANGE_FAC_A=A:E
GOOGLE_SHEET_ID_CASOS=your_casos_sheet_id_here
GOOGLE_SHEET_RANGE_CASOS=A:J
GOOGLE_SHEET_RANGE_CASOS_READ=A:K
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