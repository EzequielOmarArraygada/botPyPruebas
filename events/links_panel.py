import discord
from discord.ext import commands
from discord import app_commands
import config

class LinksPanel(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @app_commands.guilds(discord.Object(id=int(config.GUILD_ID)))
    @app_commands.command(name='setup_panel_links', description='📋 Publica el panel de links útiles (solo admins)')
    async def setup_panel_links(self, interaction: discord.Interaction):
        """Comando para publicar el panel de links útiles"""
        
        # Verificar permisos de administrador o usuario autorizado
        if not interaction.user.guild_permissions.administrator and str(interaction.user.id) not in config.SETUP_USER_IDS:
            await interaction.response.send_message(
                '❌ **Acceso denegado**\n\n'
                'Solo los administradores o usuarios autorizados pueden usar este comando.',
                ephemeral=True
            )
            return

        try:
            # Enviar el panel al canal configurado
            canal = self.bot.get_channel(config.TARGET_CHANNEL_ID_LINKS)
            if not canal:
                await interaction.response.send_message(
                    f'❌ No se encontró el canal de links (ID: {config.TARGET_CHANNEL_ID_LINKS})',
                    ephemeral=True
                )
                return

            # Crear y enviar 4 paneles separados
            
            # Panel 1: Plataformas de Gestión
            embed1 = discord.Embed(
                title="🔧 Plataformas de Gestión",
                description="Herramientas principales para la gestión de pedidos y casos",
                color=0x3498db,
                timestamp=discord.utils.utcnow()
            )
            embed1.set_footer(text="Panel de Links Útiles - BGH")
            view1 = PlataformasGestionView()
            await canal.send(embed=embed1, view=view1)

            # Panel 2: Plataformas de Envío
            embed2 = discord.Embed(
                title="🚚 Plataformas de Envío",
                description="Sistemas de tracking y gestión de envíos",
                color=0x95a5a6,
                timestamp=discord.utils.utcnow()
            )
            embed2.set_footer(text="Panel de Links Útiles - BGH")
            view2 = PlataformasEnvioView()
            await canal.send(embed=embed2, view=view2)

            # Panel 3: Información para la Gestión
            embed3 = discord.Embed(
                title="📚 Información para la Gestión",
                description="Documentación, manuales y recursos de consulta",
                color=0x2ecc71,
                timestamp=discord.utils.utcnow()
            )
            embed3.set_footer(text="Panel de Links Útiles - BGH")
            view3 = InformacionGestionView()
            await canal.send(embed=embed3, view=view3)

            # Panel 4: Real Time
            embed4 = discord.Embed(
                title="⚡ Real Time",
                description="Herramientas de tiempo real y reportes",
                color=0xe74c3c,
                timestamp=discord.utils.utcnow()
            )
            embed4.set_footer(text="Panel de Links Útiles - BGH")
            view4 = RealTimeView()
            await canal.send(embed=embed4, view=view4)
            
            await interaction.response.send_message(
                f'✅ **Panel de links útiles publicado correctamente** en <#{config.TARGET_CHANNEL_ID_LINKS}>',
                ephemeral=True
            )
            
            print(f'[LINKS] Panel de links publicado por {interaction.user} ({interaction.user.id})')
            
        except Exception as e:
            await interaction.response.send_message(
                f'❌ **Error al publicar el panel**\n\n```{str(e)}```',
                ephemeral=True
            )
            print(f'[LINKS] Error al publicar panel: {e}')

# Panel 1: Plataformas de Gestión
class PlataformasGestionView(discord.ui.View):
    def __init__(self):
        super().__init__(timeout=None)
        
        self.add_item(discord.ui.Button(
            label="Wise",
            url="https://login.wcx.cloud/",
            style=discord.ButtonStyle.primary,
            emoji="🔐"
        ))
        
        self.add_item(discord.ui.Button(
            label="VTEX BGH",
            url="https://arbghprod.myvtex.com/admin/orders",
            style=discord.ButtonStyle.primary,
            emoji="🛒"
        ))
        
        self.add_item(discord.ui.Button(
            label="Producteca BGH",
            url="https://app.producteca.com/salesorders",
            style=discord.ButtonStyle.primary,
            emoji="📊"
        ))
        
        self.add_item(discord.ui.Button(
            label="Casos BGH",
            url="https://docs.google.com/spreadsheets/d/15RGK3zOJCI6lJVMscp3teQZ_8NRmT7p6/edit?pli=1&gid=120633518#gid=120633518",
            style=discord.ButtonStyle.primary,
            emoji="📋"
        ))
        
        self.add_item(discord.ui.Button(
            label="Facturación BGH",
            url="https://docs.google.com/spreadsheets/d/1cpOFZmJoy26SX_BD5t31c3Ps_ZZEwdv6Sug1dLMmFn4/edit?gid=0#gid=0",
            style=discord.ButtonStyle.primary,
            emoji="🧾"
        ))

# Panel 2: Plataformas de Envío
class PlataformasEnvioView(discord.ui.View):
    def __init__(self):
        super().__init__(timeout=None)
        
        self.add_item(discord.ui.Button(
            label="Entregar Búsqueda",
            url="https://svr.entregar.net.ar/e_transport/app_Login/app_Login.php",
            style=discord.ButtonStyle.secondary,
            emoji="🔍"
        ))
        
        self.add_item(discord.ui.Button(
            label="Entregar Tracking",
            url="https://svr.entregar.net.ar/tracking_bgh/",
            style=discord.ButtonStyle.secondary,
            emoji="📦"
        ))
        
        self.add_item(discord.ui.Button(
            label="Andreani",
            url="https://www.andreani.com/",
            style=discord.ButtonStyle.secondary,
            emoji="🚛"
        ))
        
        self.add_item(discord.ui.Button(
            label="Urbano",
            url="https://www.urbano.com.ar/segui-tu-envio",
            style=discord.ButtonStyle.secondary,
            emoji="🏍️"
        ))

# Panel 3: Información para la Gestión
class InformacionGestionView(discord.ui.View):
    def __init__(self):
        super().__init__(timeout=None)
        
        self.add_item(discord.ui.Button(
            label="Manual BGH Front",
            url="https://docs.google.com/document/d/1fSEHllwd6CrBTg17TujlcT39eVHonvFkvYMn4QLeI_4/edit?tab=t.akuk112mktt#heading=h.7lf2mo1kh90l",
            style=discord.ButtonStyle.success,
            emoji="📖"
        ))
        
        self.add_item(discord.ui.Button(
            label="BOOK BGH",
            url="https://grupobgh.sharepoint.com/:f:/s/BOOK_EXTERNO/EouV2_fVsoFGr9wjpcfFk3ABDcNzqzn1VeauPPft7MSR0w?e=nHQTsV",
            style=discord.ButtonStyle.success,
            emoji="📚"
        ))
        
        self.add_item(discord.ui.Button(
            label="Consultas Técnicas 2",
            url="https://grupobgh-my.sharepoint.com/:x:/r/personal/ignacio_rivera_bgh_com_ar/_layouts/15/doc2.aspx?sourcedoc=%7B62CCC614-5BBD-4F75-BB86-7C120A02C545%7D&file=Consultas%20T%25u00e9cnicas%202.xlsx&fromShare=true&action=default&mobileredirect=true",
            style=discord.ButtonStyle.success,
            emoji="🔧"
        ))
        
        self.add_item(discord.ui.Button(
            label="Índice de Documentos BGH",
            url="https://docs.google.com/spreadsheets/d/1yvjZDIwL8_HQ-XyJkGWym9gBKHXOSooH_XVIO9SBPO0/edit?pli=1&gid=0#gid=0",
            style=discord.ButtonStyle.success,
            emoji="📑"
        ))

# Panel 4: Real Time
class RealTimeView(discord.ui.View):
    def __init__(self):
        super().__init__(timeout=None)
        
        self.add_item(discord.ui.Button(
            label="Reporting",
            url="https://sites.google.com/wearesolu.com/portal-workforce/inicio/reporting?authuser=0",
            style=discord.ButtonStyle.danger,
            emoji="📈"
        ))
        
        self.add_item(discord.ui.Button(
            label="Solicitud de Licencias",
            url="https://docs.google.com/forms/d/e/1FAIpQLSeOyX0QfNyHLYeB_a5Z7ldi5ue0-3MpCBYRn-B2Rp11SHZtcg/viewform",
            style=discord.ButtonStyle.danger,
            emoji="📝"
        ))
        
        self.add_item(discord.ui.Button(
            label="Solicitud a WFM",
            url="https://docs.google.com/forms/d/e/1FAIpQLSeXTrVQz-kD6RdvPnufyi13OLD0zpLd9U8kkoWWmYN1m2tpIg/viewform",
            style=discord.ButtonStyle.danger,
            emoji="⏰"
        ))
        
        self.add_item(discord.ui.Button(
            label="Estado de Solicitudes",
            url="https://sites.google.com/wearesolu.com/portal-workforce/inicio/workforce/estado-de-solicitudes-wfm?authuser=0",
            style=discord.ButtonStyle.danger,
            emoji="📊"
        ))
        
        self.add_item(discord.ui.Button(
            label="Formulario Salida de Línea",
            url="https://docs.google.com/forms/d/e/1FAIpQLSf_OsQgq5vP9yJNtRVVUqLVo-qf3JaR-YkADZSX1N1MYWU-Pw/viewform",
            style=discord.ButtonStyle.danger,
            emoji="🚪"
        ))
        
        self.add_item(discord.ui.Button(
            label="Solicitud Solu Swap",
            url="https://docs.google.com/forms/d/e/1FAIpQLSeHh9px-OqkMDbGX0MAH8jAsGQI6aHlk7xuqpXwTJ-VdQIcXg/viewform",
            style=discord.ButtonStyle.danger,
            emoji="🔄"
        ))
        
        self.add_item(discord.ui.Button(
            label="Estado Swap",
            url="https://sites.google.com/wearesolu.com/portal-workforce/inicio/real-time/looker-swap?authuser=0",
            style=discord.ButtonStyle.danger,
            emoji="📊"
        ))
        
        self.add_item(discord.ui.Button(
            label="Registro Salidas de Línea",
            url="https://sites.google.com/wearesolu.com/portal-workforce/inicio/real-time/looker-deslogueos?authuser=0",
            style=discord.ButtonStyle.danger,
            emoji="📋"
        ))

async def setup(bot):
    await bot.add_cog(LinksPanel(bot))
