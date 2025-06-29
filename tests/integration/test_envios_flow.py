import unittest
from unittest.mock import Mock, AsyncMock, patch
from interactions.modals import SolicitudEnviosModal

class TestEnviosFlow(unittest.IsolatedAsyncioTestCase):
    @patch('utils.google_sheets.initialize_google_sheets')
    @patch('utils.google_sheets.check_if_pedido_exists', return_value=False)
    async def test_registro_envio(self, mock_check, mock_init):
        modal = SolicitudEnviosModal()
        # Simular valores del modal
        type(modal.pedido).value = property(lambda self: "PED456")
        type(modal.numero_caso).value = property(lambda self: "CASO456")
        type(modal.direccion_telefono).value = property(lambda self: "Dirección de prueba")
        type(modal.observaciones).value = property(lambda self: "Observaciones de prueba")
        # Mock de interacción
        interaction = AsyncMock()
        interaction.user.display_name = "TestUser"
        interaction.user.id = 456
        interaction.response.send_message = AsyncMock()
        # Mock de Google Sheets
        mock_sheet = Mock()
        mock_sheet.get.return_value = [
            ['Número de pedido', 'CASO ID WISE', 'Dirección/Teléfono/Datos (Gestión Front)'],
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