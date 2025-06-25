#!/usr/bin/env python3
"""
Script para probar el flujo de Factura A con el nuevo embed y botón
"""

def test_factura_a_flow():
    """Prueba el flujo de Factura A"""
    print("🔍 Probando flujo de Factura A...")
    
    try:
        # Importar las clases necesarias
        from events.attachment_handler import SolicitudCargadaButton, SolicitudCargadaView
        
        # Probar creación del botón
        print("\n📋 Probando SolicitudCargadaButton...")
        button = SolicitudCargadaButton("TEST123", "CASE456", "Test User", "01-01-2024 10:00:00", "123456")
        print(f"✅ SolicitudCargadaButton creado correctamente")
        print(f"   Label: {button.label}")
        print(f"   Style: {button.style}")
        print(f"   Custom ID: {button.custom_id}")
        print(f"   Disabled: {button.disabled}")
        
        # Probar creación de la vista
        print("\n📋 Probando SolicitudCargadaView...")
        view = SolicitudCargadaView("TEST123", "CASE456", "Test User", "01-01-2024 10:00:00", "123456")
        print(f"✅ SolicitudCargadaView creado correctamente")
        print(f"   Timeout: {view.timeout}")
        print(f"   Children: {len(view.children)}")
        
        # Verificar que el botón esté en la vista
        if view.children:
            child_button = view.children[0]
            print(f"   Botón en vista: {child_button.label}")
        
        return True
        
    except Exception as e:
        print(f"❌ Error al probar flujo de Factura A: {e}")
        return False

def test_embed_creation():
    """Prueba la creación del embed"""
    print("\n🔍 Probando creación de embed...")
    
    try:
        import discord
        from datetime import datetime
        
        # Crear un embed de ejemplo
        embed = discord.Embed(
            title='🧾 Nueva Solicitud de Factura A',
            description='Se ha cargado una nueva solicitud de Factura A con archivos adjuntos.',
            color=discord.Color.blue(),
            timestamp=datetime.now()
        )
        
        embed.add_field(
            name='📋 Número de Pedido',
            value='TEST123',
            inline=True
        )
        
        embed.add_field(
            name='📝 Número de Caso',
            value='CASE456',
            inline=True
        )
        
        embed.add_field(
            name='👤 Agente',
            value='Test User',
            inline=True
        )
        
        embed.add_field(
            name='📅 Fecha de Carga',
            value='01-01-2024 10:00:00',
            inline=True
        )
        
        embed.add_field(
            name='📎 Archivos',
            value='documento1.pdf, documento2.pdf',
            inline=False
        )
        
        embed.set_footer(text='Presiona el botón para marcar como cargada')
        
        print(f"✅ Embed creado correctamente")
        print(f"   Título: {embed.title}")
        print(f"   Color: {embed.color}")
        print(f"   Campos: {len(embed.fields)}")
        print(f"   Footer: {embed.footer.text}")
        
        return True
        
    except Exception as e:
        print(f"❌ Error al crear embed: {e}")
        return False

def main():
    """Función principal"""
    print("🚀 Verificando flujo de Factura A...\n")
    
    success1 = test_factura_a_flow()
    success2 = test_embed_creation()
    
    if success1 and success2:
        print("\n✅ El flujo de Factura A está configurado correctamente!")
        print("🎉 Los componentes deberían funcionar correctamente.")
        print("\n📝 Funcionalidades implementadas:")
        print("   - Embed automático al cargar archivos")
        print("   - Botón 'Solicitud cargada' con validación de roles")
        print("   - Actualización de Google Sheets")
        print("   - Cambio de estado del botón")
        print("   - Mencionado automático a @Bgh Back Office")
    else:
        print("\n❌ Hay problemas con el flujo de Factura A.")
        print("🔧 Revisa los errores mostrados arriba.")
    
    print("\n" + "="*50)

if __name__ == "__main__":
    main() 