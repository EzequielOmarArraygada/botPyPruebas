import unittest
from unittest.mock import Mock
from utils import google_sheets

class TestGoogleSheetsUtils(unittest.TestCase):
    def test_check_if_pedido_exists_true(self):
        mock_sheet = Mock()
        mock_sheet.get.return_value = [
            ['Número de pedido', 'Fecha'],
            ['PED001', '01/01/2024']
        ]
        self.assertTrue(google_sheets.check_if_pedido_exists(mock_sheet, 'A:B', 'PED001'))

    def test_check_if_pedido_exists_false(self):
        mock_sheet = Mock()
        mock_sheet.get.return_value = [
            ['Número de pedido', 'Fecha'],
            ['PED001', '01/01/2024']
        ]
        self.assertFalse(google_sheets.check_if_pedido_exists(mock_sheet, 'A:B', 'PED999'))

    def test_get_col_index_found(self):
        header = ['Col1', 'Col2', 'Col3']
        idx = google_sheets.get_col_index(header, 'Col2')
        self.assertEqual(idx, 1)

    def test_get_col_index_not_found(self):
        header = ['Col1', 'Col2', 'Col3']
        idx = google_sheets.get_col_index(header, 'ColX')
        self.assertIsNone(idx)

    def test_normaliza_columna(self):
        self.assertEqual(google_sheets.normaliza_columna('  Col Á  '), 'colá') 