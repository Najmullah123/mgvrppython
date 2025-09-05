import os
import discord
from discord.ext import commands
from discord import app_commands
import psutil
import time

class BotStats(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.start_time = time.time()

    @app_commands.guilds(1277047315047120978)
    @app_commands.command(name="botstats", description="Display bot statistics")
    async def botstats(self, interaction: discord.Interaction):
        # Count lines of code in mgvrppython folder
        def count_lines_of_code(directory):
            lines = 0
            for root, _, files in os.walk(directory):
                for file in files:
                    if file.endswith('.py') or file.endswith('.json'):
                        with open(os.path.join(root, file), encoding='utf-8') as f:
                            lines += sum(1 for line in f if line.strip())
            return lines

        root_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
        total_lines = count_lines_of_code(root_dir)

        # Memory usage
        process = psutil.Process(os.getpid())
        memory_used_mb = round(process.memory_info().rss / 1024 / 1024, 2)

        # Uptime
        uptime_hours = round((time.time() - self.start_time) / 3600, 2)

        embed = discord.Embed(
            title="Bot Statistics",
            color=0x2f3136
        )
        embed.set_thumbnail(url="https://cdn.discordapp.com/attachments/1188598843152609480/1189025859910737930/5BFA9C31-E931-457A-8854-B86508B5A60D.jpg")
        embed.add_field(name="Lines of Code", value=f"`{total_lines}` lines", inline=True)
        embed.add_field(name="Memory Usage", value=f"`{memory_used_mb}` MB", inline=True)
        embed.add_field(name="Uptime", value=f"`{uptime_hours}` hours", inline=True)
        embed.set_footer(text="Mellow's Greenville Roleplay™ - Developed by Baryonyx (Antivenom)")
        embed.timestamp = discord.utils.utcnow()
        await interaction.response.send_message(embed=embed)

async def setup(bot):
    await bot.add_cog(BotStats(bot))
