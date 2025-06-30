import unittest
from unittest.mock import Mock, patch
from utils.google_sheets import obtener_tarea_por_id, obtener_tarea_activa_por_usuario, get_col_index

class TestGoogleSheetsHelpers(unittest.TestCase):
    
    def test_get_col_index(self):
        """Test de la función get_col_index"""
        header = ['Usuario ID', 'Tarea ID', 'Usuario', 'Tarea', 'Estado (En proceso, Pausada)']
        
        # Test casos exitosos
        self.assertEqual(get_col_index(header, 'Usuario ID'), 0)
        self.assertEqual(get_col_index(header, 'Tarea ID'), 1)
        self.assertEqual(get_col_index(header, 'Estado (En proceso, Pausada)'), 4)
        
        # Test caso no encontrado
        self.assertIsNone(get_col_index(header, 'Columna Inexistente'))
        
        # Test con normalización
        self.assertEqual(get_col_index(header, 'usuario id'), 0)
        self.assertEqual(get_col_index(header, 'TAREA ID'), 1)
    
    def test_obtener_tarea_por_id(self):
        """Test de la función obtener_tarea_por_id"""
        # Mock de la hoja
        mock_sheet = Mock()
        mock_sheet.get_all_values.return_value = [
            ['Usuario ID', 'Tarea ID', 'Usuario', 'Tarea', 'Estado (En proceso, Pausada)', 'Observaciones', 'Fecha/hora de inicio', 'Tiempo pausada acumulado'],
            ['123', 'TAREA123', 'TestUser', 'Test Tarea', 'En proceso', 'Obs', '01/01/2024 10:00:00', '00:00:00']
        ]
        
        # Test con tarea existente
        resultado = obtener_tarea_por_id(mock_sheet, 'TAREA123')
        
        self.assertIsNotNone(resultado)
        self.assertEqual(resultado['user_id'], '123')
        self.assertEqual(resultado['tarea'], 'Test Tarea')
        self.assertEqual(resultado['estado'], 'En proceso')
        self.assertEqual(resultado['usuario'], 'TestUser')
        self.assertEqual(resultado['observaciones'], 'Obs')
        self.assertEqual(resultado['inicio'], '01/01/2024 10:00:00')
        self.assertEqual(resultado['tiempo_pausado'], '00:00:00')
        self.assertEqual(resultado['fila_idx'], 2)
        
        # Test con tarea inexistente
        resultado = obtener_tarea_por_id(mock_sheet, 'TAREA_INEXISTENTE')
        self.assertIsNone(resultado)
    
    def test_obtener_tarea_activa_por_usuario(self):
        """Test de la función obtener_tarea_activa_por_usuario"""
        # Mock de la hoja
        mock_sheet = Mock()
        mock_sheet.get_all_values.return_value = [
            ['Usuario ID', 'Tarea ID', 'Usuario', 'Tarea', 'Estado (En proceso, Pausada)', 'Observaciones', 'Fecha/hora de inicio', 'Tiempo pausada acumulado'],
            ['123', 'TAREA123', 'TestUser', 'Test Tarea', 'En proceso', 'Obs', '01/01/2024 10:00:00', '00:00:00'],
            ['456', 'TAREA456', 'OtherUser', 'Otra Tarea', 'Finalizada', 'Obs2', '01/01/2024 11:00:00', '00:00:00']
        ]
        
        # Test con usuario que tiene tarea activa
        resultado = obtener_tarea_activa_por_usuario(mock_sheet, '123')
        
        self.assertIsNotNone(resultado)
        self.assertEqual(resultado['user_id'], '123')
        self.assertEqual(resultado['tarea_id'], 'TAREA123')
        self.assertEqual(resultado['tarea'], 'Test Tarea')
        self.assertEqual(resultado['estado'], 'En proceso')
        
        # Test con usuario que no tiene tarea activa
        resultado = obtener_tarea_activa_por_usuario(mock_sheet, '456')
        self.assertIsNone(resultado)
        
        # Test con usuario inexistente
        resultado = obtener_tarea_activa_por_usuario(mock_sheet, '999')
        self.assertIsNone(resultado)
    
    def test_obtener_tarea_por_id_con_columnas_faltantes(self):
        """Test de obtener_tarea_por_id con columnas faltantes"""
        # Mock de la hoja con columnas faltantes
        mock_sheet = Mock()
        mock_sheet.get_all_values.return_value = [
            ['Usuario ID', 'Tarea ID'],  # Solo algunas columnas
            ['123', 'TAREA123']
        ]
        
        resultado = obtener_tarea_por_id(mock_sheet, 'TAREA123')
        
        # La función retorna un diccionario con valores vacíos cuando faltan columnas
        self.assertIsNotNone(resultado)
        self.assertEqual(resultado['user_id'], '123')
        self.assertEqual(resultado['tarea'], '')
        self.assertEqual(resultado['estado'], '')
        self.assertEqual(resultado['usuario'], '')
    
    def test_obtener_tarea_activa_por_usuario_con_columnas_faltantes(self):
        """Test de obtener_tarea_activa_por_usuario con columnas faltantes"""
        # Mock de la hoja con columnas faltantes
        mock_sheet = Mock()
        mock_sheet.get_all_values.return_value = [
            ['Usuario ID'],  # Solo una columna
            ['123']
        ]
        
        resultado = obtener_tarea_activa_por_usuario(mock_sheet, '123')
        
        # Debe retornar None si faltan columnas esenciales
        self.assertIsNone(resultado) 