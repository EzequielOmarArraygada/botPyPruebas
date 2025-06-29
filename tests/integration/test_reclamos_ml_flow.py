import unittest
from unittest.mock import Mock, AsyncMock, patch, PropertyMock
from interactions.modals import ReclamosMLModal

class TestReclamosMLFlow(unittest.IsolatedAsyncioTestCase):
    @patch('utils.google_sheets.initialize_google_sheets')
    @patch('utils.google_sheets.check_if_pedido_exists', return_value=False)
    async def test_registro_reclamo_ml(self, mock_check, mock_init):
        modal = ReclamosMLModal()
        # Simular valores del modal usando PropertyMock sobre la instancia
        setattr(type(modal.pedido), 'value', PropertyMock(return_value="PEDML1"))
        setattr(type(modal.direccion_datos), 'value', PropertyMock(return_value="Dirección ML"))
        setattr(type(modal.observaciones), 'value', PropertyMock(return_value="Observaciones ML"))
        # Mock de interacción
        interaction = AsyncMock()
        interaction.user.display_name = "TestUser"
        interaction.user.id = 101
        interaction.response.send_message = AsyncMock()
        # Mock de Google Sheets
        mock_sheet = Mock()
        mock_sheet.get.return_value = [
            ['Número de pedido', 'Dirección/Datos', 'Observaciones'],
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