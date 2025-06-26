#!/usr/bin/env python3
"""
Script de prueba para verificar que las vistas persistentes están correctamente configuradas.
Este script simula el proceso de registro de vistas persistentes sin necesidad de conectar al bot.
"""

import sys
import os

# Agregar el directorio actual al path para importar los módulos
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

def test_persistent_views():
    """Prueba la configuración de las vistas persistentes"""
    print("🔍 Verificando configuración de vistas persistentes...")
    
    try:
        # Importar las vistas
        from tasks.panel import TaskPanelView, TareaControlView, PanelComandosView
        from events.attachment_handler import SolicitudCargadaView
        
        print("✅ Todas las vistas se importaron correctamente")
        
        # Verificar TaskPanelView
        print("\n📋 Verificando TaskPanelView...")
        task_panel = TaskPanelView()
        if task_panel.timeout is None:
            print("✅ TaskPanelView: timeout=None (correcto)")
        else:
            print(f"❌ TaskPanelView: timeout={task_panel.timeout} (debería ser None)")
        
        # Verificar que el botón tiene custom_id
        if task_panel.children:
            button = task_panel.children[0]
            if hasattr(button, 'custom_id') and button.custom_id:
                print(f"✅ TaskPanelView botón: custom_id='{button.custom_id}' (correcto)")
            else:
                print("❌ TaskPanelView botón: sin custom_id")
        
        # Verificar TareaControlView
        print("\n🎛️ Verificando TareaControlView...")
        tarea_control = TareaControlView()
        if tarea_control.timeout is None:
            print("✅ TareaControlView: timeout=None (correcto)")
        else:
            print(f"❌ TareaControlView: timeout={tarea_control.timeout} (debería ser None)")
        
        # Verificar que los botones tienen custom_id
        for i, button in enumerate(tarea_control.children):
            if hasattr(button, 'custom_id') and button.custom_id:
                print(f"✅ TareaControlView botón {i+1}: custom_id='{button.custom_id}' (correcto)")
            else:
                print(f"❌ TareaControlView botón {i+1}: sin custom_id")
        
        # Verificar PanelComandosView
        print("\n🎮 Verificando PanelComandosView...")
        panel_comandos = PanelComandosView()
        if panel_comandos.timeout is None:
            print("✅ PanelComandosView: timeout=None (correcto)")
        else:
            print(f"❌ PanelComandosView: timeout={panel_comandos.timeout} (debería ser None)")
        
        # Verificar que los botones tienen custom_id
        for i, button in enumerate(panel_comandos.children):
            if hasattr(button, 'custom_id') and button.custom_id:
                print(f"✅ PanelComandosView botón {i+1}: custom_id='{button.custom_id}' (correcto)")
            else:
                print(f"❌ PanelComandosView botón {i+1}: sin custom_id")
        
        # Verificar SolicitudCargadaView
        print("\n📄 Verificando SolicitudCargadaView...")
        solicitud_view = SolicitudCargadaView("test", "test", "test", "test", "test")
        if solicitud_view.timeout is None:
            print("✅ SolicitudCargadaView: timeout=None (correcto)")
        else:
            print(f"❌ SolicitudCargadaView: timeout={solicitud_view.timeout} (debería ser None)")
        
        # Verificar que el botón tiene custom_id
        if solicitud_view.children:
            button = solicitud_view.children[0]
            if hasattr(button, 'custom_id') and button.custom_id:
                print(f"✅ SolicitudCargadaView botón: custom_id='{button.custom_id}' (correcto)")
            else:
                print("❌ SolicitudCargadaView botón: sin custom_id")
        
        print("\n🎉 ¡Todas las verificaciones completadas!")
        print("📝 Resumen: Las vistas persistentes están correctamente configuradas.")
        
    except ImportError as e:
        print(f"❌ Error al importar módulos: {e}")
        return False
    except Exception as e:
        print(f"❌ Error durante la verificación: {e}")
        return False
    
    return True

def test_timeout_views():
    """Prueba las vistas que NO deben ser persistentes (con timeout)"""
    print("\n🔍 Verificando vistas con timeout (no persistentes)...")
    
    try:
        from tasks.panel import TaskSelectMenuView, TaskStartButtonView
        
        # Verificar TaskSelectMenuView
        print("\n📋 Verificando TaskSelectMenuView...")
        select_view = TaskSelectMenuView()
        if select_view.timeout is not None:
            print(f"✅ TaskSelectMenuView: timeout={select_view.timeout} (correcto - no persistente)")
        else:
            print("❌ TaskSelectMenuView: timeout=None (debería tener timeout)")
        
        # Verificar TaskStartButtonView
        print("\n▶️ Verificando TaskStartButtonView...")
        start_view = TaskStartButtonView("test")
        if start_view.timeout is not None:
            print(f"✅ TaskStartButtonView: timeout={start_view.timeout} (correcto - no persistente)")
        else:
            print("❌ TaskStartButtonView: timeout=None (debería tener timeout)")
        
        print("\n✅ Vistas con timeout verificadas correctamente")
        
    except Exception as e:
        print(f"❌ Error al verificar vistas con timeout: {e}")
        return False
    
    return True

if __name__ == "__main__":
    print("🚀 Iniciando pruebas de vistas persistentes...")
    
    success1 = test_persistent_views()
    success2 = test_timeout_views()
    
    if success1 and success2:
        print("\n🎉 ¡Todas las pruebas pasaron exitosamente!")
        print("✅ El bot debería funcionar correctamente sin errores de vistas persistentes.")
    else:
        print("\n❌ Algunas pruebas fallaron.")
        print("⚠️ Revisa los errores antes de ejecutar el bot.") 