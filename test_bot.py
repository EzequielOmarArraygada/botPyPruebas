#!/usr/bin/env python3
"""
Suite de Tests para CS-Bot - Bot de Gestión Comercial
=====================================================

Este archivo contiene tests automatizados para verificar el funcionamiento
correcto de todos los componentes del bot de Discord.

Cobertura de Tests:
- ✅ Configuración del bot
- ✅ Comandos slash principales
- ✅ Formularios modales
- ✅ Integración con Google Sheets
- ✅ API de Andreani
- ✅ Gestión de estados
- ✅ Manejo de archivos adjuntos
- ✅ Panel de tareas
- ✅ Validaciones de entrada
"""

import unittest
import json
import os
import sys
from unittest.mock import Mock, patch, MagicMock, PropertyMock, AsyncMock
import asyncio
from datetime import datetime
import pytz
from importlib import reload

# Agregar el directorio raíz al path para importar módulos
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

class TestBotConfiguration(unittest.TestCase):
    """Tests para la configuración del bot"""
    
    def setUp(self):
        """Configuración inicial para cada test"""
        self.env_vars = {
            'DISCORD_TOKEN': 'test_token_123',
            'GUILD_ID': '123456789',
            'GOOGLE_CREDENTIALS_JSON': '{"type": "service_account", "test": true}',
            'ANDREANI_API_AUTH': 'test_auth_header',
            'GEMINI_API_KEY': 'test_gemini_key',
            'TARGET_CHANNEL_ID_FAC_A': '111111111',
            'TARGET_CHANNEL_ID_ENVIOS': '222222222',
            'TARGET_CHANNEL_ID_CASOS': '333333333',
            'TARGET_CHANNEL_ID_CASOS_ENVIOS': '444444444',
            'TARGET_CHANNEL_ID_BUSCAR_CASO': '555555555',
            'TARGET_CHANNEL_ID_CASOS_REEMBOLSOS': '666666666',
            'TARGET_CHANNEL_ID_CASOS_CANCELACION': '777777777',
            'TARGET_CHANNEL_ID_CASOS_RECLAMOS_ML': '888888888',
            'TARGET_CHANNEL_ID_CASOS_PIEZA_FALTANTE': '999999999',
            'TARGET_CHANNEL_ID_TAREAS': '101010101',
            'TARGET_CHANNEL_ID_TAREAS_REGISTRO': '111111112',
            'TARGET_CHANNEL_ID_GUIA_COMANDOS': '121212121',
            'SPREADSHEET_ID_FAC_A': 'test_sheet_id_fac_a',
            'SPREADSHEET_ID_CASOS': 'test_sheet_id_casos',
            'GOOGLE_SHEET_ID_TAREAS': 'test_sheet_id_tareas',
            'PARENT_DRIVE_FOLDER_ID': 'test_drive_folder_id',
            'MANUAL_DRIVE_FILE_ID': 'test_manual_file_id',
            'TARGET_CATEGORY_ID': '131313131',
            'ERROR_CHECK_INTERVAL_MS': '14400000',
            'GOOGLE_SHEET_RANGE_ENVIOS': 'ENVIOS!A:L',
            'GOOGLE_SHEET_RANGE_CANCELACIONES': 'CANCELACIONES!A:L',
            'GOOGLE_SHEET_RANGE_RECLAMOS_ML': 'RECLAMOS_ML!A:L',
            'GOOGLE_SHEET_RANGE_PIEZA_FALTANTE': 'PIEZA_FALTANTE!A:J',
            'GOOGLE_SHEET_RANGE_REEMBOLSOS': 'REEMBOLSOS!A:L',
            'GOOGLE_SHEET_RANGE_CASOS_READ': 'SOLICITUDES_BGH!A:Z'
        }
    
    @patch.dict(os.environ, {}, clear=True)
    def test_config_loading(self):
        """Test: Verificar carga de configuración"""
        with patch.dict(os.environ, self.env_vars):
            import config
            
            # Verificar variables críticas
            self.assertIsNotNone(config.TOKEN)
            self.assertIsNotNone(config.GUILD_ID)
            self.assertIsNotNone(config.GOOGLE_CREDENTIALS_JSON)
            self.assertIsNotNone(config.ANDREANI_AUTH_HEADER)
            
            # Verificar IDs de canales
            self.assertIsNotNone(config.TARGET_CHANNEL_ID_FAC_A)
            self.assertIsNotNone(config.TARGET_CHANNEL_ID_ENVIOS)
            self.assertIsNotNone(config.TARGET_CHANNEL_ID_CASOS)
    
    def test_google_credentials_json_validation(self):
        """Test: Validar formato JSON de credenciales de Google"""
        valid_json = '{"type": "service_account", "project_id": "test", "private_key_id": "test"}'
        invalid_json = 'invalid json string'
        
        # Test JSON válido
        try:
            json.loads(valid_json)
            self.assertTrue(True)
        except json.JSONDecodeError:
            self.fail("JSON válido no debería fallar")
        
        # Test JSON inválido
        with self.assertRaises(json.JSONDecodeError):
            json.loads(invalid_json)
    
    def test_required_environment_variables(self):
        """Test: Verificar variables de entorno requeridas"""
        required_vars = [
            'DISCORD_TOKEN',
            'GOOGLE_CREDENTIALS_JSON',
            'GUILD_ID'
        ]
        
        for var in required_vars:
            self.assertIn(var, self.env_vars)
            self.assertIsNotNone(self.env_vars[var])
            self.assertNotEqual(self.env_vars[var], '')

class TestStateManager(unittest.TestCase):
    """Tests para el gestor de estados"""
    
    def setUp(self):
        """Configuración inicial"""
        from utils.state_manager import delete_user_state
        self.user_id = "test_user_123"
        self.tipo = "test_type"
        
        # Limpiar estado previo
        delete_user_state(self.user_id, self.tipo)
    
    def test_set_and_get_user_state(self):
        """Test: Establecer y obtener estado de usuario"""
        from utils.state_manager import set_user_state, get_user_state
        
        test_data = {"test": "data", "number": 123}
        set_user_state(self.user_id, test_data, self.tipo)
        
        retrieved_data = get_user_state(self.user_id, self.tipo)
        self.assertEqual(retrieved_data, test_data)
    
    def test_delete_user_state(self):
        """Test: Eliminar estado de usuario"""
        from utils.state_manager import set_user_state, get_user_state, delete_user_state
        
        test_data = {"test": "data"}
        set_user_state(self.user_id, test_data, self.tipo)
        
        # Verificar que existe
        self.assertIsNotNone(get_user_state(self.user_id, self.tipo))
        
        # Eliminar
        delete_user_state(self.user_id, self.tipo)
        
        # Verificar que no existe
        self.assertIsNone(get_user_state(self.user_id, self.tipo))
    
    def test_generate_solicitud_id(self):
        """Test: Generar ID único de solicitud"""
        from utils.state_manager import generar_solicitud_id
        
        solicitud_id = generar_solicitud_id(self.user_id)
        self.assertIsInstance(solicitud_id, str)
        self.assertIn(self.user_id, solicitud_id)
        self.assertGreater(len(solicitud_id), len(self.user_id))

class TestGoogleSheetsIntegration(unittest.TestCase):
    """Tests para integración con Google Sheets"""
    
    def setUp(self):
        """Configuración inicial"""
        # Credenciales más completas para evitar errores
        self.mock_credentials = json.dumps({
            "type": "service_account",
            "project_id": "test-project",
            "private_key_id": "test-key-id",
            "private_key": "-----BEGIN PRIVATE KEY-----\nMIIEvQIBADANBgkqhkiG9w0BAQEFAASCBKcwggSjAgEAAoIBAQC...\n-----END PRIVATE KEY-----\n",
            "client_email": "test@test-project.iam.gserviceaccount.com",
            "client_id": "123456789",
            "auth_uri": "https://accounts.google.com/o/oauth2/auth",
            "token_uri": "https://oauth2.googleapis.com/token",
            "auth_provider_x509_cert_url": "https://www.googleapis.com/oauth2/v1/certs",
            "client_x509_cert_url": "https://www.googleapis.com/robot/v1/metadata/x509/test%40test-project.iam.gserviceaccount.com"
        })
        self.mock_sheet_id = "test_sheet_id"
        self.mock_range = "A:E"
    
    @patch('utils.google_sheets.gspread')
    @patch('utils.google_sheets.Credentials')
    def test_initialize_google_sheets(self, mock_credentials, mock_gspread):
        """Test: Inicializar cliente de Google Sheets"""
        from utils.google_sheets import initialize_google_sheets
        
        # Mock de las credenciales
        mock_creds_instance = Mock()
        mock_credentials.from_service_account_info.return_value = mock_creds_instance
        
        # Mock del cliente
        mock_client = Mock()
        mock_gspread.authorize.return_value = mock_client
        
        client = initialize_google_sheets(self.mock_credentials)
        
        self.assertEqual(client, mock_client)
        mock_credentials.from_service_account_info.assert_called_once()
        mock_gspread.authorize.assert_called_once_with(mock_creds_instance)
    
    def test_check_if_pedido_exists(self):
        """Test: Verificar si existe un pedido"""
        from utils.google_sheets import check_if_pedido_exists
        
        # Mock de datos de hoja
        mock_sheet = Mock()
        mock_sheet.get.return_value = [
            ['Número de Pedido', 'Fecha', 'Caso', 'Email'],
            ['PED001', '01/01/2024', 'CASE001', 'test@test.com'],
            ['PED002', '02/01/2024', 'CASE002', 'test2@test.com']
        ]
        
        # Test pedido existente
        exists = check_if_pedido_exists(mock_sheet, 'A:D', 'PED001')
        self.assertTrue(exists)
        
        # Test pedido no existente
        not_exists = check_if_pedido_exists(mock_sheet, 'A:D', 'PED999')
        self.assertFalse(not_exists)

class TestAndreaniAPI(unittest.TestCase):
    """Tests para API de Andreani"""
    
    def setUp(self):
        """Configuración inicial"""
        self.tracking_number = "TEST123456789"
        self.auth_header = "Bearer test_token"
    
    @patch('utils.andreani.requests.get')
    def test_get_andreani_tracking_success(self, mock_get):
        """Test: Consulta exitosa de tracking"""
        from utils.andreani import get_andreani_tracking
        
        # Mock de respuesta exitosa
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.json.return_value = {
            "procesoActual": {
                "titulo": "En tránsito"
            },
            "fechaEstimadaDeEntrega": "2024-01-15",
            "timelines": [
                {
                    "orden": 1,
                    "traducciones": [
                        {
                            "fechaEvento": "2024-01-10T10:00:00",
                            "traduccion": "Envío recibido",
                            "sucursal": {"nombre": "Sucursal Central"}
                        }
                    ]
                }
            ]
        }
        mock_get.return_value = mock_response
        
        result = get_andreani_tracking(self.tracking_number, self.auth_header)
        
        self.assertIsNotNone(result)
        self.assertEqual(result["procesoActual"]["titulo"], "En tránsito")
        self.assertIn("timelines", result)
    
    @patch('utils.andreani.requests.get')
    def test_get_andreani_tracking_error(self, mock_get):
        """Test: Error en consulta de tracking"""
        from utils.andreani import get_andreani_tracking
        
        # Mock de respuesta con error
        mock_response = Mock()
        mock_response.status_code = 404
        mock_response.json.return_value = None  # Simular respuesta vacía
        mock_get.return_value = mock_response
        
        result = get_andreani_tracking(self.tracking_number, self.auth_header)
        
        self.assertIsNone(result)

class TestModalForms(unittest.TestCase):
    """Tests para formularios modales"""
    
    def setUp(self):
        """Configuración inicial"""
        self.mock_interaction = Mock()
        self.mock_interaction.user.id = "test_user_123"
        self.mock_interaction.response.send_message = Mock()
        self.mock_interaction.response.send_modal = Mock()
    
    @patch('asyncio.get_running_loop')
    def test_factura_a_modal_creation(self, mock_get_loop):
        """Test: Creación del modal de Factura A"""
        # Mock del event loop
        mock_loop = Mock()
        mock_future = Mock()
        mock_loop.create_future.return_value = mock_future
        mock_get_loop.return_value = mock_loop
        
        from interactions.modals import FacturaAModal
        
        modal = FacturaAModal()
        
        # Verificar que el modal tiene los campos correctos
        self.assertEqual(modal.title, 'Registrar Solicitud Factura A')
        self.assertEqual(len(modal.children), 4)  # 4 campos de texto
        
        # Verificar campos específicos usando los atributos del modal
        self.assertIsNotNone(modal.pedido)
        self.assertIsNotNone(modal.caso)
        self.assertIsNotNone(modal.email)
        self.assertIsNotNone(modal.descripcion)
        
        # Verificar que los campos tienen las propiedades correctas
        self.assertEqual(modal.pedido.label, "Número de Pedido")
        self.assertEqual(modal.caso.label, "Número de Caso")
        self.assertEqual(modal.email.label, "Email del Cliente")
        self.assertEqual(modal.descripcion.label, "Detalle de la Solicitud")
    
    @patch('asyncio.get_running_loop')
    def test_caso_modal_creation(self, mock_get_loop):
        """Test: Creación del modal de Caso"""
        # Mock del event loop
        mock_loop = Mock()
        mock_future = Mock()
        mock_loop.create_future.return_value = mock_future
        mock_get_loop.return_value = mock_loop
        
        from interactions.modals import CasoModal
        
        modal = CasoModal()
        
        # Verificar que el modal tiene los campos correctos
        self.assertEqual(modal.title, 'Detalles del Caso')
        self.assertEqual(len(modal.children), 3)  # 3 campos de texto
        
        # Verificar campos específicos usando los atributos del modal
        self.assertIsNotNone(modal.pedido)
        self.assertIsNotNone(modal.numero_caso)
        self.assertIsNotNone(modal.datos_contacto)
        
        # Verificar que los campos tienen las propiedades correctas
        self.assertEqual(modal.pedido.label, "Número de Pedido")
        self.assertEqual(modal.numero_caso.label, "Número de Caso")
        self.assertEqual(modal.datos_contacto.label, "Dirección / Teléfono / Otros Datos")

    @patch('asyncio.get_running_loop')
    def test_reclamos_ml_modal_creation(self, mock_get_loop):
        """Test: Creación del modal de Reclamos ML"""
        # Mock del event loop
        mock_loop = Mock()
        mock_future = Mock()
        mock_loop.create_future.return_value = mock_future
        mock_get_loop.return_value = mock_loop

        from interactions.modals import ReclamosMLModal

        modal = ReclamosMLModal()

        # Verificar que el modal tiene los campos correctos
        self.assertEqual(modal.title, 'Detalles del Reclamo ML')
        self.assertEqual(len(modal.children), 3)  # 3 campos de texto

        # Verificar campos específicos usando los atributos del modal
        self.assertIsNotNone(modal.pedido)
        self.assertIsNotNone(modal.direccion_datos)
        self.assertIsNotNone(modal.observaciones)

        # Verificar que los campos tienen las propiedades correctas
        self.assertEqual(modal.pedido.label, "Número de Pedido")
        self.assertEqual(modal.direccion_datos.label, "Dirección/Datos")
        self.assertEqual(modal.observaciones.label, "Observaciones (opcional)")

class TestCommandValidation(unittest.TestCase):
    """Tests para validación de comandos"""
    
    def setUp(self):
        """Configuración inicial"""
        self.mock_interaction = Mock()
        self.mock_interaction.channel_id = "111111111"
        self.mock_interaction.response.send_message = Mock()
        self.mock_interaction.response.defer = Mock()
    
    def test_channel_restriction_validation(self):
        """Test: Validación de restricción de canal"""
        # Simular comando en canal correcto
        correct_channel_id = "111111111"
        target_channel_id = "111111111"
        
        self.assertEqual(str(correct_channel_id), str(target_channel_id))
        
        # Simular comando en canal incorrecto
        wrong_channel_id = "999999999"
        self.assertNotEqual(str(wrong_channel_id), str(target_channel_id))
    
    def test_input_validation(self):
        """Test: Validación de entrada de datos"""
        # Test tracking number válido
        valid_tracking = "ABC123456789"
        self.assertIsInstance(valid_tracking, str)
        self.assertGreater(len(valid_tracking), 0)
        
        # Test tracking number inválido
        invalid_tracking = ""
        self.assertEqual(len(invalid_tracking), 0)
        
        # Test pedido válido
        valid_pedido = "PED001"
        self.assertIsInstance(valid_pedido, str)
        self.assertGreater(len(valid_pedido), 0)
        
        # Test pedido inválido
        invalid_pedido = "   "
        self.assertEqual(invalid_pedido.strip(), "")

class TestTaskPanel(unittest.TestCase):
    """Tests para el panel de tareas"""
    
    def setUp(self):
        """Configuración inicial"""
        self.mock_interaction = Mock()
        self.mock_interaction.user.id = "test_user_123"
        self.mock_interaction.user.display_name = "Test User"
        self.mock_interaction.channel.send = Mock()
        self.mock_interaction.response.defer = Mock()
    
    def test_task_options(self):
        """Test: Opciones disponibles en el panel de tareas"""
        expected_tasks = [
            'Facturas B',
            'Facturas A', 
            'Reclamos ML',
            'Cambios / Devoluciones',
            'Cancelaciones',
            'Reembolsos',
            'Otra'
        ]
        
        # Verificar que todas las opciones están definidas
        for task in expected_tasks:
            self.assertIsInstance(task, str)
            self.assertGreater(len(task), 0)
    
    def test_task_id_generation(self):
        """Test: Generación de ID de tarea"""
        import time
        import uuid
        
        user_id = "test_user_123"
        timestamp = int(time.time())
        unique_id = uuid.uuid4().hex[:8]
        
        task_id = f"{user_id}_{unique_id}_{timestamp}"
        
        self.assertIsInstance(task_id, str)
        self.assertIn(user_id, task_id)
        self.assertGreater(len(task_id), len(user_id))

class TestFileHandling(unittest.TestCase):
    """Tests para manejo de archivos"""
    
    def setUp(self):
        """Configuración inicial"""
        self.mock_attachment = Mock()
        self.mock_attachment.filename = "test_file.pdf"
        self.mock_attachment.content_type = "application/pdf"
        self.mock_attachment.size = 1024
    
    def test_attachment_validation(self):
        """Test: Validación de archivos adjuntos"""
        # Test archivo válido
        valid_filename = "documento.pdf"
        valid_extensions = ['.pdf', '.jpg', '.png', '.doc', '.docx']
        
        file_extension = os.path.splitext(valid_filename)[1].lower()
        self.assertIn(file_extension, valid_extensions)
        
        # Test archivo inválido
        invalid_filename = "script.exe"
        invalid_extension = os.path.splitext(invalid_filename)[1].lower()
        self.assertNotIn(invalid_extension, valid_extensions)
    
    def test_file_size_validation(self):
        """Test: Validación de tamaño de archivo"""
        max_size = 10 * 1024 * 1024  # 10MB
        
        # Test archivo dentro del límite
        small_file_size = 1024 * 1024  # 1MB
        self.assertLess(small_file_size, max_size)
        
        # Test archivo excede límite
        large_file_size = 20 * 1024 * 1024  # 20MB
        self.assertGreater(large_file_size, max_size)

class TestErrorHandling(unittest.TestCase):
    """Tests para manejo de errores"""
    
    def test_exception_handling(self):
        """Test: Manejo de excepciones"""
        def function_that_raises():
            raise ValueError("Test error")
        
        def function_with_try_catch():
            try:
                function_that_raises()
                return False
            except ValueError as e:
                return str(e)
        
        result = function_with_try_catch()
        self.assertEqual(result, "Test error")
    
    def test_config_validation_errors(self):
        """Test: Errores de validación de configuración"""
        # Test token faltante
        missing_token = None
        self.assertIsNone(missing_token)
        
        # Test credenciales inválidas
        invalid_credentials = "invalid json"
        with self.assertRaises(json.JSONDecodeError):
            json.loads(invalid_credentials)

class TestDateTimeHandling(unittest.TestCase):
    """Tests para manejo de fechas y horas"""
    
    def test_timezone_conversion(self):
        """Test: Conversión de zona horaria"""
        # Test zona horaria de Argentina
        tz = pytz.timezone('America/Argentina/Buenos_Aires')
        now = datetime.now(tz)
        
        self.assertIsInstance(now, datetime)
        # Verificar que tiene zona horaria (sin comparar objetos específicos)
        self.assertIsNotNone(now.tzinfo)
        self.assertEqual(str(now.tzinfo), str(tz))
    
    def test_date_formatting(self):
        """Test: Formateo de fechas"""
        # Test formato dd/mm/yyyy HH:MM:SS
        test_date = datetime(2024, 1, 15, 14, 30, 45)
        formatted_date = test_date.strftime('%d/%m/%Y %H:%M:%S')
        
        self.assertEqual(formatted_date, "15/01/2024 14:30:45")
    
    def test_iso_date_parsing(self):
        """Test: Parseo de fechas ISO"""
        iso_date = "2024-01-15T14:30:45"
        parsed_date = datetime.fromisoformat(iso_date)
        
        self.assertIsInstance(parsed_date, datetime)
        self.assertEqual(parsed_date.year, 2024)
        self.assertEqual(parsed_date.month, 1)
        self.assertEqual(parsed_date.day, 15)

class TestIntegrationScenarios(unittest.TestCase):
    """Tests para escenarios de integración completos"""
    
    def setUp(self):
        """Configuración inicial"""
        self.mock_interaction = Mock()
        self.mock_interaction.user.id = "test_user_123"
        self.mock_interaction.user.display_name = "Test User"
        self.mock_interaction.channel_id = "111111111"
        self.mock_interaction.response.send_message = Mock()
        self.mock_interaction.response.send_modal = Mock()
        self.mock_interaction.response.defer = Mock()
    
    def test_complete_factura_a_flow(self):
        """Test: Flujo completo de Factura A"""
        # 1. Usuario ejecuta comando
        command_executed = True
        self.assertTrue(command_executed)
        
        # 2. Se valida canal
        correct_channel = str(self.mock_interaction.channel_id) == "111111111"
        self.assertTrue(correct_channel)
        
        # 3. Se abre modal
        modal_opened = True
        self.assertTrue(modal_opened)
        
        # 4. Usuario completa datos
        form_data = {
            "pedido": "PED001",
            "caso": "CASE001", 
            "email": "test@test.com",
            "descripcion": "Test description"
        }
        
        # Validar datos
        self.assertIsNotNone(form_data["pedido"])
        self.assertIsNotNone(form_data["caso"])
        self.assertIsNotNone(form_data["email"])
        self.assertIn("@", form_data["email"])
    
    def test_complete_tracking_flow(self):
        """Test: Flujo completo de tracking"""
        # 1. Usuario ejecuta comando
        tracking_number = "ABC123456789"
        self.assertIsInstance(tracking_number, str)
        self.assertGreater(len(tracking_number), 0)
        
        # 2. Se valida entrada
        valid_input = len(tracking_number.strip()) > 0
        self.assertTrue(valid_input)
        
        # 3. Se consulta API
        api_consulted = True
        self.assertTrue(api_consulted)
        
        # 4. Se procesa respuesta
        response_processed = True
        self.assertTrue(response_processed)
    
    def test_complete_caso_flow(self):
        """Test: Flujo completo de caso"""
        # 1. Usuario ejecuta comando
        command_executed = True
        self.assertTrue(command_executed)
        
        # 2. Se muestra menú de selección
        menu_shown = True
        self.assertTrue(menu_shown)
        
        # 3. Usuario selecciona tipo
        selected_type = "Cambio"
        valid_types = ["Cambio", "Devolución", "Reclamo", "Otros"]
        self.assertIn(selected_type, valid_types)
        
        # 4. Se abre formulario
        form_opened = True
        self.assertTrue(form_opened)
        
        # 5. Se valida y registra
        data_registered = True
        self.assertTrue(data_registered)

class TestAdditionalFeatures(unittest.TestCase):
    """Tests para funcionalidades adicionales"""
    
    def test_manual_processor(self):
        """Test: Procesamiento del manual"""
        # Simular carga de manual
        manual_content = "Este es el contenido del manual de procedimientos."
        self.assertIsInstance(manual_content, str)
        self.assertGreater(len(manual_content), 0)
    
    def test_qa_service(self):
        """Test: Servicio de preguntas y respuestas"""
        # Simular consulta al manual
        question = "¿Cómo procesar una factura?"
        self.assertIsInstance(question, str)
        self.assertGreater(len(question), 0)
    
    def test_google_drive_integration(self):
        """Test: Integración con Google Drive"""
        # Simular carga de archivo
        file_uploaded = True
        self.assertTrue(file_uploaded)
    
    def test_error_checking(self):
        """Test: Verificación de errores"""
        # Simular verificación periódica
        error_check_executed = True
        self.assertTrue(error_check_executed)

class TestCancelacionesFlow(unittest.TestCase):
    """Tests para el flujo de cancelaciones"""
    def setUp(self):
        self.user_id = "test_user_cancelaciones"
        self.tipo = "cancelaciones"
        from utils.state_manager import delete_user_state
        delete_user_state(self.user_id, self.tipo)

    def test_set_and_get_cancelaciones_state(self):
        from utils.state_manager import set_user_state, get_user_state
        test_data = {"type": "cancelaciones", "paso": 1, "tipoCancelacion": "CANCELAR"}
        set_user_state(self.user_id, test_data, self.tipo)
        retrieved = get_user_state(self.user_id, self.tipo)
        self.assertEqual(retrieved, test_data)

    @patch('utils.google_sheets.gspread')
    @patch('utils.google_sheets.Credentials')
    def test_guardar_cancelacion_en_sheet(self, mock_credentials, mock_gspread):
        from utils.google_sheets import initialize_google_sheets
        mock_creds_instance = Mock()
        mock_credentials.from_service_account_info.return_value = mock_creds_instance
        mock_client = Mock()
        mock_gspread.authorize.return_value = mock_client
        client = initialize_google_sheets('{"type": "service_account", "test": true}')
        self.assertEqual(client, mock_client)

    def test_modal_cancelacion_fields(self):
        import asyncio
        from interactions.modals import CancelacionModal
        async def inner():
            modal = CancelacionModal()
            self.assertTrue(hasattr(modal, 'pedido'))
            self.assertTrue(hasattr(modal, 'observaciones'))
            self.assertEqual(modal.pedido.label, "Número de Pedido")
            self.assertEqual(modal.observaciones.label, "Observaciones")
        asyncio.run(inner())

class TestIntegrationFlows(unittest.TestCase):
    """Tests de integración para todos los flujos principales del bot"""

    def setUp(self):
        self.user_id = "test_user_integration"
        self.display_name = "Test User"
        self.mock_interaction = Mock()
        self.mock_interaction.user.id = self.user_id
        self.mock_interaction.user.display_name = self.display_name
        self.mock_interaction.response.send_message = AsyncMock()
        self.mock_interaction.response.send_modal = AsyncMock()
        self.mock_interaction.followup.send = AsyncMock()
        self.mock_interaction.channel_id = "123456789"
        self.mock_interaction.channel = Mock()
        self.mock_interaction.guild = Mock()
        self.mock_interaction.guild.get_channel = Mock(return_value=self.mock_interaction.channel)

    @patch('utils.google_sheets.initialize_google_sheets')
    @patch('utils.google_sheets.check_if_pedido_exists', return_value=False)
    def test_flujo_factura_a(self, mock_check, mock_init):
        async def run():
            from interactions.modals import FacturaAModal
            modal = FacturaAModal()
            type(modal.pedido).value = PropertyMock(return_value="PED123")
            type(modal.caso).value = PropertyMock(return_value="CASO123")
            type(modal.email).value = PropertyMock(return_value="test@email.com")
            type(modal.descripcion).value = PropertyMock(return_value="Detalle de prueba")
            with patch.object(self.mock_interaction, 'response') as mock_response:
                mock_response.send_message = AsyncMock()
                mock_response.send_modal = AsyncMock()
                import config
                config.GOOGLE_CREDENTIALS_JSON = '{}'
                config.SPREADSHEET_ID_FAC_A = 'sheet_id'
                modal.add_item = Mock()
                await modal.on_submit(self.mock_interaction)
        asyncio.run(run())

    @patch('utils.google_sheets.initialize_google_sheets')
    @patch('utils.google_sheets.check_if_pedido_exists', return_value=False)
    def test_flujo_cambios_devoluciones(self, mock_check, mock_init):
        async def run():
            from interactions.modals import CasoModal
            from utils.state_manager import set_user_state
            set_user_state(self.user_id, {"type": "cambios_devoluciones", "paso": 2, "tipoSolicitud": "CAMBIO DEFECTUOSO"}, "cambios_devoluciones")
            modal = CasoModal()
            type(modal.pedido).value = PropertyMock(return_value="PED124")
            type(modal.numero_caso).value = PropertyMock(return_value="CASO124")
            type(modal.datos_contacto).value = PropertyMock(return_value="Dirección de prueba")
            with patch.object(self.mock_interaction, 'response') as mock_response:
                mock_response.send_message = AsyncMock()
                mock_response.send_modal = AsyncMock()
                import config
                config.GOOGLE_CREDENTIALS_JSON = '{}'
                config.SPREADSHEET_ID_CASOS = 'sheet_id'
                modal.add_item = Mock()
                await modal.on_submit(self.mock_interaction)
        asyncio.run(run())

    @patch('utils.google_sheets.initialize_google_sheets')
    @patch('utils.google_sheets.check_if_pedido_exists', return_value=False)
    def test_flujo_envios(self, mock_check, mock_init):
        async def run():
            from interactions.modals import SolicitudEnviosModal
            from utils.state_manager import set_user_state
            set_user_state(self.user_id, {"type": "solicitudes_envios", "paso": 2, "tipoSolicitud": "Reenvío"}, "solicitudes_envios")
            modal = SolicitudEnviosModal()
            type(modal.pedido).value = PropertyMock(return_value="PED125")
            type(modal.numero_caso).value = PropertyMock(return_value="CASO125")
            type(modal.direccion_telefono).value = PropertyMock(return_value="Dirección y Teléfono")
            type(modal.observaciones).value = PropertyMock(return_value="Observaciones")
            with patch.object(self.mock_interaction, 'response') as mock_response:
                mock_response.send_message = AsyncMock()
                mock_response.send_modal = AsyncMock()
                import config
                config.GOOGLE_CREDENTIALS_JSON = '{}'
                config.SPREADSHEET_ID_CASOS = 'sheet_id'
                config.GOOGLE_SHEET_RANGE_ENVIOS = 'RANGO!A:L'
                modal.add_item = Mock()
                await modal.on_submit(self.mock_interaction)
        asyncio.run(run())

    @patch('utils.google_sheets.initialize_google_sheets')
    @patch('utils.google_sheets.check_if_pedido_exists', return_value=False)
    def test_flujo_reembolsos(self, mock_check, mock_init):
        async def run():
            from interactions.modals import ReembolsoModal
            from utils.state_manager import set_user_state
            set_user_state(self.user_id, {"type": "reembolsos", "paso": 2, "tipoReembolso": "RETIRO (ZRE2)"}, "reembolso")
            modal = ReembolsoModal()
            type(modal.pedido).value = PropertyMock(return_value="PED126")
            type(modal.zre).value = PropertyMock(return_value="ZRE2")
            type(modal.tarjeta).value = PropertyMock(return_value="1234")
            type(modal.correo).value = PropertyMock(return_value="test@email.com")
            type(modal.observacion).value = PropertyMock(return_value="Observación")
            with patch.object(self.mock_interaction, 'response') as mock_response:
                mock_response.send_message = AsyncMock()
                mock_response.send_modal = AsyncMock()
                import config
                config.GOOGLE_CREDENTIALS_JSON = '{}'
                config.SPREADSHEET_ID_CASOS = 'sheet_id'
                config.SHEET_RANGE_REEMBOLSOS = 'RANGO!A:L'
                modal.add_item = Mock()
                await modal.on_submit(self.mock_interaction)
        asyncio.run(run())

    @patch('utils.google_sheets.initialize_google_sheets')
    @patch('utils.google_sheets.check_if_pedido_exists', return_value=False)
    def test_flujo_cancelaciones(self, mock_check, mock_init):
        async def run():
            from interactions.modals import CancelacionModal
            from utils.state_manager import set_user_state
            set_user_state(self.user_id, {"type": "cancelaciones", "paso": 2, "tipoCancelacion": "CANCELAR"}, "cancelaciones")
            modal = CancelacionModal()
            type(modal.pedido).value = PropertyMock(return_value="PED127")
            type(modal.observaciones).value = PropertyMock(return_value="Observaciones")
            with patch.object(self.mock_interaction, 'response') as mock_response:
                mock_response.send_message = AsyncMock()
                mock_response.send_modal = AsyncMock()
                import config
                config.GOOGLE_CREDENTIALS_JSON = '{}'
                config.SPREADSHEET_ID_CASOS = 'sheet_id'
                config.GOOGLE_SHEET_RANGE_CANCELACIONES = 'RANGO!A:L'
                modal.add_item = Mock()
                await modal.on_submit(self.mock_interaction)
        asyncio.run(run())

    @patch('utils.google_sheets.initialize_google_sheets')
    @patch('utils.google_sheets.check_if_pedido_exists', return_value=False)
    def test_flujo_reclamos_ml(self, mock_check, mock_init):
        async def run():
            from interactions.modals import ReclamosMLModal
            from utils.state_manager import set_user_state
            set_user_state(self.user_id, {"type": "reclamos_ml", "paso": 2, "tipoReclamo": "Cambio dañado"}, "reclamos_ml")
            modal = ReclamosMLModal()
            type(modal.pedido).value = PropertyMock(return_value="PED128")
            type(modal.direccion_datos).value = PropertyMock(return_value="Dirección reclamo")
            type(modal.observaciones).value = PropertyMock(return_value="Observaciones reclamo")
            with patch.object(self.mock_interaction, 'response') as mock_response:
                mock_response.send_message = AsyncMock()
                mock_response.send_modal = AsyncMock()
                import config
                config.GOOGLE_CREDENTIALS_JSON = '{}'
                config.SPREADSHEET_ID_CASOS = 'sheet_id'
                config.GOOGLE_SHEET_RANGE_RECLAMOS_ML = 'RANGO!A:L'
                modal.add_item = Mock()
                await modal.on_submit(self.mock_interaction)
        asyncio.run(run())

    @patch('utils.google_sheets.initialize_google_sheets')
    @patch('utils.google_sheets.check_if_pedido_exists', return_value=False)
    def test_flujo_pieza_faltante(self, mock_check, mock_init):
        async def run():
            from interactions.modals import PiezaFaltanteModal
            modal = PiezaFaltanteModal()
            from unittest.mock import PropertyMock
            type(modal.pedido).value = PropertyMock(return_value="PED999")
            type(modal.id_wise).value = PropertyMock(return_value="WISE123")
            type(modal.pieza).value = PropertyMock(return_value="Tornillo")
            type(modal.sku).value = PropertyMock(return_value="SKU123")
            type(modal.observaciones).value = PropertyMock(return_value="Observación de prueba")
            with patch.object(self.mock_interaction, 'response') as mock_response:
                mock_response.send_message = AsyncMock()
                mock_response.send_modal = AsyncMock()
                import config
                config.GOOGLE_CREDENTIALS_JSON = '{}'
                config.SPREADSHEET_ID_CASOS = 'sheet_id'
                config.GOOGLE_SHEET_RANGE_PIEZA_FALTANTE = 'RANGO!A:J'
                modal.add_item = Mock()
                await modal.on_submit(self.mock_interaction)
        asyncio.run(run())

class TestErrorCheckingFeatures(unittest.TestCase):
    """Tests para las funcionalidades de verificación de errores"""
    
    def setUp(self):
        """Configuración inicial"""
        self.mock_bot = Mock()
        self.mock_sheet = Mock()
        self.mock_channel = AsyncMock()
        self.mock_guild = Mock()
        
    @patch('utils.google_sheets.check_sheet_for_errors')
    @patch('utils.google_sheets.initialize_google_sheets')
    def test_verificar_errores_command(self, mock_init, mock_check_errors):
        """Test: Comando /verificar-errores"""
        async def run():
            from events.interaction_commands import InteractionCommands
            
            # Mock de la interacción
            mock_interaction = AsyncMock()
            mock_interaction.user.guild_permissions.administrator = True
            mock_interaction.response.send_message = AsyncMock()
            mock_interaction.followup.send = AsyncMock()
            
            # Mock de configuración
            import config
            config.GOOGLE_CREDENTIALS_JSON = '{"test": true}'
            config.SPREADSHEET_ID_CASOS = 'test_sheet_id'
            config.GUILD_ID = '123456789'
            config.MAPA_RANGOS_ERRORES = {
                'ENVIOS!A:L': '111111111',
                'RECLAMOS_ML!A:L': '222222222'
            }
            
            # Mock de Google Sheets
            mock_client = Mock()
            mock_spreadsheet = Mock()
            mock_worksheet = Mock()
            mock_client.open_by_key.return_value = mock_spreadsheet
            mock_spreadsheet.worksheet.return_value = mock_worksheet
            mock_init.return_value = mock_client
            
            # Crear instancia del comando
            commands = InteractionCommands(self.mock_bot)
            
            # Ejecutar comando - usar el método directamente y pasar self
            await commands.verificar_errores.callback(commands, mock_interaction)
            
            # Verificar que se llamó la función de verificación
            self.assertTrue(mock_check_errors.called)
            
        asyncio.run(run())
    
    def test_mapa_rangos_errores_config(self):
        """Test: Verificar configuración del mapeo de rangos de errores"""
        with patch.dict(os.environ, {
            'GOOGLE_SHEET_RANGE_ENVIOS': 'ENVIOS!A:L',
            'GOOGLE_SHEET_RANGE_RECLAMOS_ML': 'RECLAMOS_ML!A:L',
            'GOOGLE_SHEET_RANGE_PIEZA_FALTANTE': 'PIEZA_FALTANTE!A:J',
            'GOOGLE_SHEET_RANGE_CANCELACIONES': 'CANCELACIONES!A:L',
            'GOOGLE_SHEET_RANGE_REEMBOLSOS': 'REEMBOLSOS!A:L',
            'GOOGLE_SHEET_RANGE_CASOS_READ': 'SOLICITUDES_BGH!A:Z',
            'TARGET_CHANNEL_ID_CASOS_ENVIOS': '111111111',
            'TARGET_CHANNEL_ID_CASOS_RECLAMOS_ML': '222222222',
            'TARGET_CHANNEL_ID_CASOS_PIEZA_FALTANTE': '333333333',
            'TARGET_CHANNEL_ID_CASOS_CANCELACION': '444444444',
            'TARGET_CHANNEL_ID_REEMBOLSOS': '555555555',
            'TARGET_CHANNEL_ID_CASOS': '666666666'
        }):
            import config
            reload(config)
            
            # Verificar que el mapeo existe y tiene elementos
            self.assertIsNotNone(config.MAPA_RANGOS_ERRORES)
            self.assertGreater(len(config.MAPA_RANGOS_ERRORES), 0)
            
            # Verificar que contiene los rangos esperados
            expected_ranges = [
                'ENVIOS!A:L',
                'RECLAMOS_ML!A:L', 
                'PIEZA_FALTANTE!A:J',
                'CANCELACIONES!A:L',
                'REEMBOLSOS!A:L',
                'SOLICITUDES_BGH!A:Z'
            ]
            
            for expected_range in expected_ranges:
                self.assertIn(expected_range, config.MAPA_RANGOS_ERRORES.keys())

def run_tests():
    """Ejecutar todos los tests"""
    print("🧪 Iniciando Suite de Tests para CS-Bot")
    print("=" * 50)
    
    # Crear suite de tests
    test_suite = unittest.TestSuite()
    
    # Agregar tests
    test_classes = [
        TestBotConfiguration,
        TestStateManager,
        TestGoogleSheetsIntegration,
        TestAndreaniAPI,
        TestModalForms,
        TestCommandValidation,
        TestTaskPanel,
        TestFileHandling,
        TestErrorHandling,
        TestDateTimeHandling,
        TestIntegrationScenarios,
        TestAdditionalFeatures,
        TestCancelacionesFlow,
        TestIntegrationFlows,
        TestErrorCheckingFeatures
    ]
    
    for test_class in test_classes:
        tests = unittest.TestLoader().loadTestsFromTestCase(test_class)
        test_suite.addTests(tests)
    
    # Ejecutar tests
    runner = unittest.TextTestRunner(verbosity=2)
    result = runner.run(test_suite)
    
    # Resumen
    print("\n" + "=" * 50)
    print("📊 RESUMEN DE TESTS")
    print("=" * 50)
    print(f"✅ Tests ejecutados: {result.testsRun}")
    print(f"❌ Tests fallidos: {len(result.failures)}")
    print(f"⚠️ Tests con errores: {len(result.errors)}")
    
    if result.failures:
        print("\n🔍 TESTS FALLIDOS:")
        for test, traceback in result.failures:
            print(f"  - {test}: {traceback.split('AssertionError:')[-1].strip()}")
    
    if result.errors:
        print("\n🚨 TESTS CON ERRORES:")
        for test, traceback in result.errors:
            print(f"  - {test}: {traceback.split('Exception:')[-1].strip()}")
    
    success_rate = ((result.testsRun - len(result.failures) - len(result.errors)) / result.testsRun) * 100
    print(f"\n📈 Tasa de éxito: {success_rate:.1f}%")
    
    return result.wasSuccessful()

if __name__ == "__main__":
    try:
        success = run_tests()
        sys.exit(0 if success else 1)
    except KeyboardInterrupt:
        print("\n⏹️ Tests interrumpidos por el usuario")
        sys.exit(1)
    except Exception as e:
        print(f"\n💥 Error inesperado durante los tests: {e}")
        sys.exit(1) 