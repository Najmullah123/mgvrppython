import discord
from discord.ext import commands
from discord import app_commands
import sqlite3
import os

DATABASE_PATH = os.path.join(os.getcwd(), 'database', 'index.db')

class RobloxLookup(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @app_commands.guilds(1277047315047120978)
    @app_commands.command(name="robloxlookup", description="Look up a registered Roblox user")
    @app_commands.describe(robloxusername="The Roblox username to look up")
    async def robloxlookup(self, interaction: discord.Interaction, robloxusername: str):
        try:
            conn = sqlite3.connect(DATABASE_PATH)
            cursor = conn.cursor()
            cursor.execute("SELECT discord_id, discord_username, roblox_username, profile_link FROM roblox_registry WHERE roblox_username = ?", (robloxusername,))
            user = cursor.fetchone()
            conn.close()
            if not user:
                embed = discord.Embed(
                    color=0x2f3136,
                    title="User Not Found",
                    description="No registered user found with that Roblox username."
                )
                embed.set_thumbnail(url="https://cdn.discordapp.com/attachments/1188598843152609480/1189025859910737930/5BFA9C31-E931-457A-8854-B86508B5A60D.jpg")
                embed.add_field(name="How to Register", value="Use the `/robloxregister` command in <#1339747016317865994> with the following format:")
                embed.add_field(name="Command Usage", value="`/robloxregister robloxusername:[Your Roblox Username] profilelink:[Your Roblox Profile Link]`")
                embed.add_field(name="Profile Link Example", value="Your profile link should look like: `https://www.roblox.com/users/1234567/profile`")
                await interaction.response.send_message(embed=embed, ephemeral=True)
                return
            discord_id, discord_username, roblox_username, profile_link = user
            embed = discord.Embed(
                color=0x2f3136,
                title="Roblox User Information"
            )
            embed.set_thumbnail(url="https://cdn.discordapp.com/attachments/1188598843152609480/1189025859910737930/5BFA9C31-E931-457A-8854-B86508B5A60D.jpg")
            embed.add_field(name="Discord User", value=f"<@{discord_id}> ({discord_username})", inline=True)
            embed.add_field(name="Roblox Username", value=roblox_username, inline=True)
            embed.add_field(name="Profile Link", value=profile_link)
            await interaction.response.send_message(embed=embed)
        except Exception as e:
            await interaction.response.send_message("There was an error looking up the Roblox user!", ephemeral=True)

async def setup(bot):
    await bot.add_cog(RobloxLookup(bot))
