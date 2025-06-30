#!/usr/bin/env python3
"""
Script de prueba para verificar el funcionamiento de los botones de pausar/reanudar tarea.
"""

import asyncio
import sys
import os

# Agregar el directorio raíz al path para importar módulos
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

def test_obtener_tarea_por_id():
    """Prueba la función obtener_tarea_por_id"""
    try:
        from utils.google_sheets import obtener_tarea_por_id, initialize_google_sheets
        import config
        
        print("🔍 Probando obtener_tarea_por_id...")
        
        # Verificar configuraciones
        if not config.GOOGLE_CREDENTIALS_JSON or not config.GOOGLE_SHEET_ID_TAREAS:
            print("❌ Configuraciones de Google Sheets no encontradas")
            return False
        
        # Inicializar Google Sheets
        client = initialize_google_sheets(config.GOOGLE_CREDENTIALS_JSON)
        spreadsheet = client.open_by_key(config.GOOGLE_SHEET_ID_TAREAS)
        sheet_activas = spreadsheet.worksheet('Tareas Activas')
        
        # Obtener todas las tareas para encontrar una válida
        rows = sheet_activas.get_all_values()
        if len(rows) < 2:
            print("❌ No hay tareas en la hoja para probar")
            return False
        
        # Buscar una tarea activa
        header = rows[0]
        estado_col = None
        tarea_id_col = None
        
        for i, col in enumerate(header):
            if 'estado' in col.lower():
                estado_col = i
            if 'tarea id' in col.lower():
                tarea_id_col = i
        
        if estado_col is None or tarea_id_col is None:
            print("❌ No se encontraron las columnas necesarias")
            return False
        
        # Buscar una tarea en proceso o pausada
        tarea_id_para_probar = None
        for row in rows[1:]:
            if len(row) > estado_col and len(row) > tarea_id_col:
                estado = row[estado_col].lower()
                if estado in ['en proceso', 'pausada']:
                    tarea_id_para_probar = row[tarea_id_col]
                    break
        
        if not tarea_id_para_probar:
            print("❌ No se encontró una tarea activa para probar")
            return False
        
        print(f"✅ Tarea encontrada para probar: {tarea_id_para_probar}")
        
        # Probar la función
        datos_tarea = obtener_tarea_por_id(sheet_activas, tarea_id_para_probar)
        
        if datos_tarea:
            print("✅ Función obtener_tarea_por_id funciona correctamente")
            print(f"   - Estado: {datos_tarea.get('estado', 'N/A')}")
            print(f"   - Tarea: {datos_tarea.get('tarea', 'N/A')}")
            print(f"   - Usuario: {datos_tarea.get('usuario', 'N/A')}")
            print(f"   - User ID: {datos_tarea.get('user_id', 'N/A')}")
            return True
        else:
            print("❌ La función no retornó datos")
            return False
            
    except Exception as e:
        print(f"❌ Error en test_obtener_tarea_por_id: {e}")
        return False

def test_pausar_reanudar_functions():
    """Prueba las funciones de pausar y reanudar"""
    try:
        from utils.google_sheets import (
            pausar_tarea_por_id, 
            reanudar_tarea_por_id, 
            obtener_tarea_por_id,
            initialize_google_sheets
        )
        import config
        from datetime import datetime
        import pytz
        
        print("🔍 Probando funciones de pausar/reanudar...")
        
        # Verificar configuraciones
        if not config.GOOGLE_CREDENTIALS_JSON or not config.GOOGLE_SHEET_ID_TAREAS:
            print("❌ Configuraciones de Google Sheets no encontradas")
            return False
        
        # Inicializar Google Sheets
        client = initialize_google_sheets(config.GOOGLE_CREDENTIALS_JSON)
        spreadsheet = client.open_by_key(config.GOOGLE_SHEET_ID_TAREAS)
        sheet_activas = spreadsheet.worksheet('Tareas Activas')
        sheet_historial = spreadsheet.worksheet('Historial')
        
        # Buscar una tarea en proceso para probar
        rows = sheet_activas.get_all_values()
        if len(rows) < 2:
            print("❌ No hay tareas en la hoja para probar")
            return False
        
        header = rows[0]
        estado_col = None
        tarea_id_col = None
        
        for i, col in enumerate(header):
            if 'estado' in col.lower():
                estado_col = i
            if 'tarea id' in col.lower():
                tarea_id_col = i
        
        if estado_col is None or tarea_id_col is None:
            print("❌ No se encontraron las columnas necesarias")
            return False
        
        # Buscar una tarea en proceso
        tarea_id_para_probar = None
        estado_original = None
        for row in rows[1:]:
            if len(row) > estado_col and len(row) > tarea_id_col:
                estado = row[estado_col].lower()
                if estado == 'en proceso':
                    tarea_id_para_probar = row[tarea_id_col]
                    estado_original = estado
                    break
        
        if not tarea_id_para_probar:
            print("❌ No se encontró una tarea en proceso para probar")
            return False
        
        print(f"✅ Tarea encontrada para probar: {tarea_id_para_probar}")
        print(f"   Estado original: {estado_original}")
        
        # Obtener fecha actual
        tz = pytz.timezone('America/Argentina/Buenos_Aires')
        now = datetime.now(tz)
        fecha_actual = now.strftime('%d/%m/%Y %H:%M:%S')
        
        # Probar pausar
        print("🔄 Probando pausar tarea...")
        try:
            pausar_tarea_por_id(sheet_activas, sheet_historial, tarea_id_para_probar, "Test User", fecha_actual)
            print("✅ Tarea pausada correctamente")
            
            # Verificar estado
            datos_actualizados = obtener_tarea_por_id(sheet_activas, tarea_id_para_probar)
            if datos_actualizados and datos_actualizados['estado'].lower() == 'pausada':
                print("✅ Estado actualizado correctamente a 'pausada'")
            else:
                print("❌ Estado no se actualizó correctamente")
                return False
            
            # Probar reanudar
            print("🔄 Probando reanudar tarea...")
            reanudar_tarea_por_id(sheet_activas, sheet_historial, tarea_id_para_probar, "Test User", fecha_actual)
            print("✅ Tarea reanudada correctamente")
            
            # Verificar estado final
            datos_finales = obtener_tarea_por_id(sheet_activas, tarea_id_para_probar)
            if datos_finales and datos_finales['estado'].lower() == 'en proceso':
                print("✅ Estado final correcto: 'en proceso'")
                return True
            else:
                print("❌ Estado final incorrecto")
                return False
                
        except Exception as e:
            print(f"❌ Error durante la prueba: {e}")
            return False
            
    except Exception as e:
        print(f"❌ Error en test_pausar_reanudar_functions: {e}")
        return False

def main():
    """Función principal de pruebas"""
    print("🧪 Iniciando pruebas de botones de tarea...")
    print("=" * 50)
    
    # Prueba 1: obtener_tarea_por_id
    test1_result = test_obtener_tarea_por_id()
    print()
    
    # Prueba 2: funciones de pausar/reanudar
    test2_result = test_pausar_reanudar_functions()
    print()
    
    # Resumen
    print("=" * 50)
    print("📊 RESUMEN DE PRUEBAS:")
    print(f"   Test obtener_tarea_por_id: {'✅ PASÓ' if test1_result else '❌ FALLÓ'}")
    print(f"   Test pausar/reanudar: {'✅ PASÓ' if test2_result else '❌ FALLÓ'}")
    
    if test1_result and test2_result:
        print("\n🎉 Todas las pruebas pasaron correctamente!")
        return True
    else:
        print("\n⚠️ Algunas pruebas fallaron. Revisa los errores arriba.")
        return False

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1) 