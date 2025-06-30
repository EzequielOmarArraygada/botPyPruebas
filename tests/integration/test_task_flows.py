import unittest
from unittest.mock import Mock, AsyncMock, patch
from tasks.panel import PausarReanudarButton, PausarReanudarButtonPersistent, FinalizarButtonPersistent

class TestTaskFlows(unittest.IsolatedAsyncioTestCase):
    @patch('utils.google_sheets.initialize_google_sheets')
    async def test_pausar_reanudar_button(self, mock_init):
        """Test del botón original PausarReanudarButton"""
        # Mock datos de tarea
        datos_tarea = {
            'estado': 'en proceso',
            'tarea': 'Test Tarea',
            'observaciones': 'Obs',
            'inicio': '01/01/2024 10:00:00',
            'tiempo_pausado': '00:00:00',
            'user_id': '123'
        }
        
        # Mock Google Sheets
        mock_sheet = Mock()
        mock_sheet.get_all_values.return_value = [
            ['Usuario ID', 'Tarea ID', 'Usuario', 'Tarea', 'Estado (En proceso, Pausada)', 'Observaciones', 'Fecha/hora de inicio', 'Tiempo pausada acumulado'],
            ['123', 'TAREA123', 'TestUser', 'Test Tarea', 'En proceso', 'Obs', '01/01/2024 10:00:00', '00:00:00']
        ]
        mock_sheet.update_cell = Mock()
        
        mock_historial = Mock()
        mock_historial.get_all_values.return_value = [
            ['Usuario ID', 'Tarea ID', 'Usuario', 'Tarea', 'Observaciones', 'Estado', 'Fecha/hora de inicio', 'Tipo de evento (Inicio, Pausa, Reanudación, Finalización)', 'Tiempo pausada acumulado'],
            ['123', 'TAREA123', 'TestUser', 'Test Tarea', 'Obs', 'En proceso', '01/01/2024 10:00:00', 'Inicio', '00:00:00']
        ]
        mock_historial.append_row = Mock()
        
        mock_spreadsheet = Mock()
        mock_spreadsheet.worksheet.side_effect = lambda name: mock_sheet if name == 'Tareas Activas' else mock_historial
        mock_client = Mock()
        mock_client.open_by_key.return_value = mock_spreadsheet
        mock_init.return_value = mock_client

        # Mock interacción
        interaction = AsyncMock()
        interaction.user.id = '123'
        interaction.user.display_name = 'TestUser'
        interaction.response.defer = AsyncMock()
        interaction.message.edit = AsyncMock()
        interaction.followup.send = AsyncMock()

        # Probar pausar
        button = PausarReanudarButton('123', 'TAREA123', 'en proceso')
        await button.callback(interaction)
        
        # Verificar que se llamaron los métodos esperados
        interaction.response.defer.assert_called_once()
        interaction.followup.send.assert_called()

    @patch('utils.google_sheets.initialize_google_sheets')
    async def test_pausar_reanudar_button_persistent(self, mock_init):
        """Test del botón persistente PausarReanudarButtonPersistent"""
        # Mock datos de tarea activa
        datos_tarea_activa = {
            'user_id': '123',
            'tarea_id': 'TAREA123',
            'usuario': 'TestUser',
            'tarea': 'Test Tarea',
            'observaciones': 'Obs',
            'estado': 'en proceso',
            'inicio': '01/01/2024 10:00:00',
            'tiempo_pausado': '00:00:00'
        }
        
        datos_tarea = {
            'estado': 'en proceso',
            'tarea': 'Test Tarea',
            'observaciones': 'Obs',
            'inicio': '01/01/2024 10:00:00',
            'tiempo_pausado': '00:00:00',
            'user_id': '123'
        }
        
        # Mock Google Sheets
        mock_sheet = Mock()
        mock_sheet.get_all_values.return_value = [
            ['Usuario ID', 'Tarea ID', 'Usuario', 'Tarea', 'Estado (En proceso, Pausada)', 'Observaciones', 'Fecha/hora de inicio', 'Tiempo pausada acumulado'],
            ['123', 'TAREA123', 'TestUser', 'Test Tarea', 'En proceso', 'Obs', '01/01/2024 10:00:00', '00:00:00']
        ]
        mock_sheet.update_cell = Mock()
        
        mock_historial = Mock()
        mock_historial.get_all_values.return_value = [
            ['Usuario ID', 'Tarea ID', 'Usuario', 'Tarea', 'Observaciones', 'Estado', 'Fecha/hora de inicio', 'Tipo de evento (Inicio, Pausa, Reanudación, Finalización)', 'Tiempo pausada acumulado'],
            ['123', 'TAREA123', 'TestUser', 'Test Tarea', 'Obs', 'En proceso', '01/01/2024 10:00:00', 'Inicio', '00:00:00']
        ]
        mock_historial.append_row = Mock()
        
        mock_spreadsheet = Mock()
        mock_spreadsheet.worksheet.side_effect = lambda name: mock_sheet if name == 'Tareas Activas' else mock_historial
        mock_client = Mock()
        mock_client.open_by_key.return_value = mock_spreadsheet
        mock_init.return_value = mock_client

        # Mock interacción
        interaction = AsyncMock()
        interaction.user.id = '123'
        interaction.user.display_name = 'TestUser'
        interaction.response.defer = AsyncMock()
        interaction.message.edit = AsyncMock()
        interaction.followup.send = AsyncMock()
        interaction.message.content = ""
        interaction.message.embeds = []

        # Mock las funciones de Google Sheets
        with patch('utils.google_sheets.obtener_tarea_activa_por_usuario', return_value=datos_tarea_activa), \
             patch('utils.google_sheets.obtener_tarea_por_id', return_value=datos_tarea), \
             patch('utils.google_sheets.pausar_tarea_por_id'), \
             patch('tasks.panel.crear_embed_tarea') as mock_crear_embed:
            
            # Mock el embed
            mock_embed = Mock()
            mock_embed.color = None
            mock_crear_embed.return_value = mock_embed
            
            # Probar botón persistente
            button = PausarReanudarButtonPersistent()
            await button.callback(interaction)
            
            # Verificar que se llamaron los métodos esperados
            interaction.response.defer.assert_called_once()
            interaction.followup.send.assert_called()

    @patch('utils.google_sheets.initialize_google_sheets')
    async def test_finalizar_button_persistent(self, mock_init):
        """Test del botón persistente FinalizarButtonPersistent"""
        # Mock datos de tarea activa
        datos_tarea_activa = {
            'user_id': '123',
            'tarea_id': 'TAREA123',
            'usuario': 'TestUser',
            'tarea': 'Test Tarea',
            'observaciones': 'Obs',
            'estado': 'en proceso',
            'inicio': '01/01/2024 10:00:00',
            'tiempo_pausado': '00:00:00'
        }
        
        # Mock Google Sheets
        mock_sheet = Mock()
        mock_sheet.get_all_values.return_value = [
            ['Usuario ID', 'Tarea ID', 'Usuario', 'Tarea', 'Estado (En proceso, Pausada)', 'Observaciones', 'Fecha/hora de inicio', 'Tiempo pausada acumulado'],
            ['123', 'TAREA123', 'TestUser', 'Test Tarea', 'En proceso', 'Obs', '01/01/2024 10:00:00', '00:00:00']
        ]
        
        mock_spreadsheet = Mock()
        mock_spreadsheet.worksheet.return_value = mock_sheet
        mock_client = Mock()
        mock_client.open_by_key.return_value = mock_spreadsheet
        mock_init.return_value = mock_client

        # Mock interacción
        interaction = AsyncMock()
        interaction.user.id = '123'
        interaction.user.display_name = 'TestUser'
        interaction.response.send_modal = AsyncMock()

        # Mock las funciones de Google Sheets
        with patch('utils.google_sheets.obtener_tarea_activa_por_usuario', return_value=datos_tarea_activa):
            
            # Probar botón persistente
            from tasks.panel import FinalizarButtonPersistent
            button = FinalizarButtonPersistent()
            await button.callback(interaction)
            
            # Verificar que se abrió el modal
            interaction.response.send_modal.assert_called_once()

    async def test_tarea_control_view_persistent_creation(self):
        """Test de creación de la view persistente"""
        from tasks.panel import TareaControlViewPersistent
        
        # Crear la view persistente
        view = TareaControlViewPersistent()
        
        # Verificar que tiene los botones correctos
        self.assertEqual(len(view.children), 2)
        self.assertIsInstance(view.children[0], PausarReanudarButtonPersistent)
        self.assertIsInstance(view.children[1], FinalizarButtonPersistent) 