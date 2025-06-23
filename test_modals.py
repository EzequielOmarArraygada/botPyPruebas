#!/usr/bin/env python3
"""
Script para probar la creación de modales
"""

def test_modals():
    """Prueba la creación de modales"""
    print("🔍 Probando creación de modales...")
    
    try:
        # Importar los modales
        from interactions.modals import FacturaAModal, CasoModal
        
        # Probar FacturaAModal
        print("\n📋 Probando FacturaAModal...")
        factura_modal = FacturaAModal()
        print(f"✅ FacturaAModal creado correctamente")
        print(f"   Título: {factura_modal.title}")
        print(f"   Custom ID: {factura_modal.custom_id}")
        print(f"   Componentes: {len(factura_modal.children)}")
        
        # Probar CasoModal
        print("\n📋 Probando CasoModal...")
        caso_modal = CasoModal()
        print(f"✅ CasoModal creado correctamente")
        print(f"   Título: {caso_modal.title}")
        print(f"   Custom ID: {caso_modal.custom_id}")
        print(f"   Componentes: {len(caso_modal.children)}")
        
        # Verificar componentes
        print("\n🔍 Verificando componentes...")
        for i, child in enumerate(factura_modal.children):
            print(f"   FacturaAModal componente {i+1}: {child.label} ({child.custom_id})")
        
        for i, child in enumerate(caso_modal.children):
            print(f"   CasoModal componente {i+1}: {child.label} ({child.custom_id})")
        
        return True
        
    except Exception as e:
        print(f"❌ Error al crear modales: {e}")
        return False

def main():
    """Función principal"""
    print("🚀 Probando modales...\n")
    
    success = test_modals()
    
    if success:
        print("\n✅ Los modales se crean correctamente!")
        print("🎉 El comando /agregar-caso debería funcionar ahora.")
    else:
        print("\n❌ Hay problemas con los modales.")
        print("🔧 Revisa la configuración de los modales.")
    
    print("\n" + "="*50)

if __name__ == "__main__":
    main() 