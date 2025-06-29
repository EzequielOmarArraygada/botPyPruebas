import unittest
from unittest.mock import Mock, AsyncMock, patch

class TestErrorChecking(unittest.IsolatedAsyncioTestCase):
    @patch('utils.google_sheets.check_sheet_for_errors')
    @patch('utils.google_sheets.initialize_google_sheets')
    async def test_verificar_errores_command(self, mock_init, mock_check_errors):
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
        commands = InteractionCommands(Mock())
        # Ejecutar comando
        await commands.verificar_errores.callback(commands, mock_interaction)
        self.assertTrue(mock_check_errors.called) 