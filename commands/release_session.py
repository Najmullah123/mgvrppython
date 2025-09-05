import discord
from discord.ext import commands
from discord import app_commands

class ReleaseSession(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @app_commands.guilds(1277047315047120978)
    @app_commands.command(name="session_release", description="Announce public release of the session")
    @app_commands.describe(host="Session host", priority="Priority status", frp="FRP speed limit", house="House claiming allowed?", link="Roblox session link", cohost="Session co-host (optional)")
    async def session_release(self, interaction: discord.Interaction, host: discord.Member, priority: str, frp: int, house: bool, link: str, cohost: discord.Member = None):
        await interaction.response.defer(ephemeral=True)
        house_text = 'Yes' if house else 'No'
        cohost_text = cohost.mention if cohost else '*None*'
        release_description = (
            f"{host.mention} has now released their roleplay session to the public! Before joining, ensure that you have read rules and the restricted-vehicles below in order to avoid any moderation.\n\n"
            f"<:bluedash:1386424783058763906> Session Host: {host.mention}\n"
            f"<:bluedash:1386424783058763906> Session Co-Host: {cohost_text}\n"
            f"<:bluedash:1386424783058763906> Priority Status: {priority}\n"
            f"<:bluedash:1386424783058763906> FRP Speed limit: {frp} MPH\n"
            f"<:bluedash:1386424783058763906> House Claiming: {house_text}"
        )
        embed = discord.Embed(
            title='<:Megaphone_Blue:1386443190260989982>  Mellow\'s Greenville Roleplay Public Release <:Megaphone_Blue:1386443190260989982>',
            description=release_description,
            color=0x89CFF0
        )
        embed.set_image(url='https://message.style/cdn/images/fa1f3c122408747e74868cfeca93d275e778181080643fe5fcefb0e9a7e132c1.webp')
        view = discord.ui.View()
        view.add_item(discord.ui.Button(label='Session Link', style=discord.ButtonStyle.link, url=link, emoji='🔗'))
        view.add_item(discord.ui.Button(label='Support', style=discord.ButtonStyle.link, url='https://discord.com/channels/1277047315047120978/1387097565933207644', emoji='📣'))
        await interaction.channel.send(embed=embed, view=view)
        await interaction.followup.send('✅ Session release announcement sent!', ephemeral=True)

async def setup(bot):
    await bot.add_cog(ReleaseSession(bot))
