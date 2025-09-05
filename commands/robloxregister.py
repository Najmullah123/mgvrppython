import discord
from discord.ext import commands
from discord import app_commands
import sqlite3
import os

DATABASE_PATH = os.path.join(os.getcwd(), 'database', 'index.db')

class RobloxRegister(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @app_commands.guilds(1277047315047120978)
    @app_commands.command(name="robloxregister", description="Register your Roblox account")
    @app_commands.describe(robloxusername="Your Roblox username", profilelink="Link to your Roblox profile")
    async def robloxregister(self, interaction: discord.Interaction, robloxusername: str, profilelink: str):
        if str(interaction.channel_id) != '1339747016317865994':
            await interaction.response.send_message('Roblox registration can only be done in the designated registration channel!', ephemeral=True)
            return
        if not profilelink.startswith('https://www.roblox.com/users/'):
            await interaction.response.send_message('Please provide a valid Roblox profile link!', ephemeral=True)
            return
        discord_id = str(interaction.user.id)
        discord_username = interaction.user.name
        try:
            conn = sqlite3.connect(DATABASE_PATH)
            cursor = conn.cursor()
            cursor.execute('''INSERT OR REPLACE INTO roblox_registry (discord_id, discord_username, roblox_username, profile_link) VALUES (?, ?, ?, ?)''', (discord_id, discord_username, robloxusername, profilelink))
            conn.commit()
            conn.close()
            embed = discord.Embed(
                color=0x2f3136,
                title='New Roblox Registration',
                description='**Instructions for Roblox Registration:**\n1. Go to your Roblox profile\n2. Copy your profile URL (Example: https://www.roblox.com/users/1234567/profile)\n3. Use the command: `/robloxregister`\n4. Enter your Roblox username and profile link when prompted'
            )
            embed.set_thumbnail(url='https://cdn.discordapp.com/attachments/1188598843152609480/1189025859910737930/5BFA9C31-E931-457A-8854-B86508B5A60D.jpg')
            embed.add_field(name='Discord User', value=f'<@{discord_id}> ({discord_username})', inline=True)
            embed.add_field(name='Roblox Username', value=robloxusername, inline=True)
            embed.add_field(name='Profile Link', value=profilelink)
            await interaction.response.send_message('Successfully registered your Roblox account!', embed=embed, ephemeral=True)
        except Exception as e:
            await interaction.response.send_message('There was an error registering your Roblox account!', ephemeral=True)

async def setup(bot):
    await bot.add_cog(RobloxRegister(bot))
