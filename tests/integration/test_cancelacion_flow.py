import unittest
from unittest.mock import Mock, AsyncMock, patch, PropertyMock
from interactions.modals import CancelacionModal

class TestCancelacionFlow(unittest.IsolatedAsyncioTestCase):
    @patch('utils.google_sheets.initialize_google_sheets')
    async def test_registro_cancelacion(self, mock_init):
        modal = CancelacionModal()
        # Simular valores del modal usando PropertyMock
        setattr(type(modal.pedido), 'value', PropertyMock(return_value="PEDCAN1"))
        setattr(type(modal.observaciones), 'value', PropertyMock(return_value="Observación cancelación"))
        # Mock de interacción
        interaction = AsyncMock()
        interaction.user.display_name = "TestUser"
        interaction.user.id = 303
        interaction.response.send_message = AsyncMock()
        # Mock de Google Sheets
        mock_sheet = Mock()
        mock_sheet.get.return_value = [
            ['Número de pedido', 'Agente que carga', 'FECHA', 'SOLICITUD', 'OBSERVACIONES'],
        ]
        mock_spreadsheet = Mock()
        mock_spreadsheet.worksheet.return_value = mock_sheet
        mock_spreadsheet.sheet1 = mock_sheet
        mock_client = Mock()
        mock_client.open_by_key.return_value = mock_spreadsheet
        mock_init.return_value = mock_client
        # Ejecutar
        await modal.on_submit(interaction)
        interaction.response.send_message.assert_called() 