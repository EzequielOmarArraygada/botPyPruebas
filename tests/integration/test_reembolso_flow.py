import unittest
from unittest.mock import Mock, AsyncMock, patch
from interactions.modals import ReembolsoModal

class TestReembolsoFlow(unittest.IsolatedAsyncioTestCase):
    @patch('utils.google_sheets.initialize_google_sheets')
    @patch('utils.google_sheets.check_if_pedido_exists', return_value=False)
    async def test_registro_reembolso(self, mock_check, mock_init):
        modal = ReembolsoModal()
        # Simular valores del modal
        type(modal.pedido).value = property(lambda self: "PED789")
        type(modal.zre).value = property(lambda self: "ZRE2")
        type(modal.tarjeta).value = property(lambda self: "1234")
        type(modal.correo).value = property(lambda self: "correo@prueba.com")
        type(modal.observacion).value = property(lambda self: "Observación de prueba")
        # Mock de interacción
        interaction = AsyncMock()
        interaction.user.display_name = "TestUser"
        interaction.user.id = 789
        interaction.response.send_message = AsyncMock()
        # Mock de Google Sheets
        mock_sheet = Mock()
        mock_sheet.get.return_value = [
            ['Número de pedido', 'ZRE2 / ZRE4', 'Tarjeta', 'Correo del cliente'],
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