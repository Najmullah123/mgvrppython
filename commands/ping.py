import discord
from discord.ext import commands
from discord import app_commands

class Ping(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @app_commands.guilds(1277047315047120978)
    @app_commands.command(name="ping", description="Shows bot and API latency")
    async def ping(self, interaction: discord.Interaction):
        await interaction.response.defer()
        latency = round(self.bot.latency * 1000)
        embed = discord.Embed(
            title="🏓 Pong!",
            color=0x89CFF0
        )
        embed.add_field(name="Bot Latency", value=f"{latency}ms", inline=True)
        embed.add_field(name="API Latency", value=f"{latency}ms", inline=True)
        embed.set_thumbnail(url="https://cdn.discordapp.com/attachments/1350837749426683969/1387479314861391964/main_server_logo.webp")
        embed.set_footer(text="Mellow's Greenville Roleplay™ - Developed by Baryonyx (Antivenom)")
        await interaction.followup.send(embed=embed, ephemeral=True)

async def setup(bot):
    await bot.add_cog(Ping(bot))
