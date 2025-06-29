import unittest
from unittest.mock import Mock, AsyncMock, patch
from tasks.panel import PausarReanudarButton

class TestTaskFlows(unittest.IsolatedAsyncioTestCase):
    @patch('utils.google_sheets.initialize_google_sheets')
    async def test_pausar_reanudar(self, mock_init):
        # Mock datos de tarea
        datos_tarea = {
            'estado': 'en proceso',
            'tarea': 'Test Tarea',
            'observaciones': 'Obs',
            'inicio': '01/01/2024 10:00:00',
            'tiempo_pausado': '00:00:00'
        }
        # Mock Google Sheets
        mock_sheet = Mock()
        mock_sheet.get_all_values.return_value = [
            ['Tarea ID', 'Usuario', 'Tarea', 'Estado (En proceso, Pausada)', 'Observaciones', 'Fecha/hora de inicio', 'Tiempo pausada acumulado'],
            ['TAREA123', 'TestUser', 'Test Tarea', 'En proceso', 'Obs', '01/01/2024 10:00:00', '00:00:00']
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
        interaction.response.edit_message = AsyncMock()
        interaction.followup.send = AsyncMock()

        # Probar pausar
        button = PausarReanudarButton('123', 'TAREA123', 'en proceso')
        await button.callback(interaction)
        interaction.response.edit_message.assert_called()
        interaction.followup.send.assert_called() 