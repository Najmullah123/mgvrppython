import os
import discord
from discord.ext import commands
from discord import app_commands

CONCLUSION_CHANNEL = int(os.getenv('CONCLUSION_CHANNEL', 'CONCLUSION_CHANNEL_ID'))

class ConcludeSession(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @app_commands.guilds(1277047315047120978)
    @app_commands.command(name="conclude_session", description="Send a session conclusion message")
    @app_commands.describe(
        host="Session host",
        start_time="Session start time",
        end_time="Session end time",
        rating="Session rating (e.g. 8/10)",
        notes="Additional notes (optional)"
    )
    async def conclude_session(self, interaction: discord.Interaction, host: discord.Member, start_time: str, end_time: str, rating: str, notes: str = 'None'):
        await interaction.response.defer(ephemeral=True)
        embed = discord.Embed(
            color=0x89CFF0,
            title='<:Megaphone_Blue:1386443190260989982> Mellow\'s Greenville Roleplay Concluded <:Megaphone_Blue:1386443190260989982>',
            description=(
                f"{host.mention} has officially ended their session! Thank you for attending! We hope you had fun here at Mellow's Greenville Roleplay.\n\n"
                f"<:bluedash:1386424783058763906>   Session Host: {host.mention}\n"
                f"<:bluedash:1386424783058763906>   Start Time: {start_time}\n"
                f"<:bluedash:1386424783058763906>   End Time: {end_time}\n"
                f"<:bluedash:1386424783058763906>  Session Rating: {rating}/10\n"
                f"<:bluedash:1386424783058763906>  Notes: {notes}"
            )
        )
        embed.set_thumbnail(url='https://cdn.discordapp.com/attachments/1393957236891713556/1395111568164913313/5b39ef01ba7ebe82c4789d0436064ac9-removebg-preview.png?ex=68794265&is=6877f0e5&hm=c48e7259262a3285802c57065a9ae875b901f6c08b816487a0f6f4506d6b3793&')
        embed.set_footer(text="Mellow's Greenville Roleplay™ - Developed by Baryonyx (Antivenom)")
        embed.timestamp = discord.utils.utcnow()
        channel = interaction.guild.get_channel(CONCLUSION_CHANNEL)
        if not channel:
            await interaction.followup.send('❌ Conclusion channel not found.', ephemeral=True)
            return
        await channel.send(embed=embed)
        await interaction.followup.send('✅ Session conclusion message sent!', ephemeral=True)

async def setup(bot):
    await bot.add_cog(ConcludeSession(bot))
