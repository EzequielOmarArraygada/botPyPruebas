# Reparaciones y Mejoras del Bot de Discord

## ✅ Problemas Reparados

### 1. Comando `/manual` Habilitado
- **Problema**: El comando estaba comentado y no funcionaba
- **Solución**: Descomentado y arreglado el comando en `events/interaction_commands.py`
- **Funcionalidad**: Ahora permite hacer preguntas al manual de procedimientos usando IA (Gemini)

### 2. Carga del Manual Mejorada
- **Problema**: La función `load_and_cache_manual` usaba una API obsoleta de Google Drive
- **Solución**: Actualizada para usar la API moderna de Google Drive
- **Archivo**: `utils/manual_processor.py`

### 3. Flujo de Casos Reparado
- **Problema**: Los modales no estaban conectados correctamente con el sistema de interacciones
- **Solución**: 
  - Agregado `custom_id` a los modales
  - Mejorado el procesamiento en `events/interaction_selects.py`
  - Implementado guardado completo en Google Sheets
- **Funcionalidad**: Ahora el flujo `/agregar-caso` funciona completamente

### 4. Modal de Factura A Mejorado
- **Problema**: El modal no tenía el `custom_id` correcto
- **Solución**: Agregado `custom_id='facturaAModal'` y mejorado el procesamiento
- **Funcionalidad**: Ahora guarda correctamente en Google Sheets y maneja archivos adjuntos

### 5. Función de Descarga de Google Drive Reparada
- **Problema**: Error en la implementación de `download_file_from_drive`
- **Solución**: Corregida la lógica de descarga usando `MediaIoBaseDownload`
- **Archivo**: `utils/google_drive.py`

### 6. Carga Automática del Manual
- **Problema**: El manual no se cargaba automáticamente al iniciar el bot
- **Solución**: Descomentado y mejorado el código en `main.py`
- **Funcionalidad**: El manual se carga automáticamente al iniciar el bot

### 7. Errores de Async/Await Reparados ⚡ NUEVO
- **Problema**: Errores "coroutine 'BotBase.add_cog' was never awaited" en varios archivos
- **Solución**: Convertidas las funciones `setup()` a `async def setup()` en:
  - `events/guild_member_add.py`
  - `interactions/modals.py`
  - `interactions/select_menus.py`
- **Funcionalidad**: Las extensiones ahora se cargan correctamente sin errores

### 8. Validación de Credenciales de Google Mejorada ⚡ NUEVO
- **Problema**: Error "'{' was never closed" en las credenciales de Google
- **Solución**: 
  - Agregada validación JSON en `config.py`
  - Mejorado manejo de errores en `utils/google_sheets.py` y `utils/google_drive.py`
  - Creado script `check_google_creds.py` para verificar formato
- **Funcionalidad**: Mejor detección de errores en las credenciales de Google

## 🆕 Nuevas Funcionalidades Agregadas

### 1. Script de Diagnóstico
- **Archivo**: `diagnostic.py`
- **Funcionalidad**: Verifica toda la configuración del bot
- **Uso**: `python diagnostic.py`

### 2. Archivo de Configuración de Ejemplo
- **Archivo**: `config.example.py`
- **Funcionalidad**: Muestra todas las variables de entorno necesarias

### 3. Verificador de Credenciales de Google ⚡ NUEVO
- **Archivo**: `check_google_creds.py`
- **Funcionalidad**: Verifica el formato de las credenciales de Google
- **Uso**: `python check_google_creds.py`

## 🔧 Comandos Disponibles

### Comandos Funcionales:
1. `/factura-a` - Registro de Factura A con formulario modal
2. `/tracking <numero>` - Consulta de estado de envíos de Andreani
3. `/agregar-caso` - Registro de casos con flujo de selección
4. `/buscar-caso <pedido>` - Búsqueda de casos por número de pedido
5. `/manual <pregunta>` - Consulta al manual de procedimientos usando IA

### Funcionalidades Automáticas:
- Verificación periódica de errores en Google Sheets
- Manejo de archivos adjuntos para Factura A
- Notificaciones automáticas de errores en Discord

## 📋 Variables de Entorno Requeridas

### Discord:
- `DISCORD_TOKEN` - Token del bot
- `DISCORD_CLIENT_ID` - ID de la aplicación
- `GUILD_ID` - ID del servidor
- `TARGET_CHANNEL_ID_FAC_A` - Canal para Factura A
- `TARGET_CHANNEL_ID_ENVIOS` - Canal para envíos
- `TARGET_CHANNEL_ID_CASOS` - Canal para casos
- `TARGET_CHANNEL_ID_BUSCAR_CASO` - Canal para búsqueda

### Google:
- `GOOGLE_CREDENTIALS_JSON` - Credenciales de servicio
- `GOOGLE_SHEET_ID_FAC_A` - ID de hoja de Factura A
- `GOOGLE_SHEET_ID_CASOS` - ID de hoja de Casos
- `PARENT_DRIVE_FOLDER_ID` - ID de carpeta de Drive
- `MANUAL_DRIVE_FILE_ID` - ID del archivo del manual

### Otros:
- `ANDREANI_API_AUTH` - Token de Andreani
- `GEMINI_API_KEY` - API Key de Gemini

## 🚀 Instrucciones de Uso

### 1. Verificar Configuración
```bash
python diagnostic.py
```

### 2. Verificar Credenciales de Google ⚡ NUEVO
```bash
python check_google_creds.py
```

### 3. Desplegar Comandos
```bash
python deploy_commands.py
```

### 4. Ejecutar el Bot
```bash
python main.py
```

## ⚠️ Notas Importantes

1. **Permisos de Discord**: El bot necesita permisos para enviar mensajes, usar comandos slash y adjuntar archivos
2. **APIs de Google**: Necesitas habilitar Google Sheets API y Google Drive API
3. **Cuenta de Servicio**: Usa una cuenta de servicio de Google Cloud Platform
4. **Archivo del Manual**: El archivo debe estar en formato de texto plano en Google Drive
5. **Formato JSON**: Las credenciales de Google deben estar en formato JSON válido ⚡ NUEVO

## 🔍 Solución de Problemas

### Si el bot no responde:
1. Verifica que el token de Discord sea correcto
2. Asegúrate de que el bot esté en el servidor
3. Verifica los permisos del bot

### Si los comandos no aparecen:
1. Ejecuta `python deploy_commands.py`
2. Verifica que `DISCORD_CLIENT_ID` y `GUILD_ID` estén correctos
3. Asegúrate de que el bot tenga permisos de aplicación

### Si hay errores de Google:
1. Ejecuta `python check_google_creds.py` para verificar el formato ⚡ NUEVO
2. Verifica que las credenciales JSON sean válidas
3. Asegúrate de que las APIs estén habilitadas
4. Verifica que los IDs de las hojas sean correctos

### Si el comando /manual no funciona:
1. Verifica que `GEMINI_API_KEY` esté configurado
2. Verifica que `MANUAL_DRIVE_FILE_ID` esté configurado
3. Asegúrate de que el archivo del manual sea accesible

### Si hay errores de async/await: ⚡ NUEVO
1. Asegúrate de que todas las funciones `setup()` sean `async def setup()`
2. Verifica que se use `await bot.add_cog()` en lugar de `bot.add_cog()`

## 📞 Soporte

Si encuentras problemas adicionales:
1. Revisa los logs del bot
2. Ejecuta el script de diagnóstico
3. Ejecuta el verificador de credenciales de Google
4. Verifica la configuración de las variables de entorno 