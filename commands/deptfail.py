import discord
from discord.ext import commands
from discord import app_commands

DEPARTMENTS = {
    "Outagamie County Sheriff's Office": "https://cdn.discordapp.com/attachments/1350837749426683969/1386075499754950868/dNlvRACGdUAAAAAElFTkSuQmCC.png",
    "Wisconsin State Patrol": "https://cdn.discordapp.com/attachments/1350837749426683969/1386077443840016535/hNQjWXuFkjciQAAAABJRU5ErkJggg.png",
    "Wisconsin Department of Transportation": "https://cdn.discordapp.com/attachments/1350837749426683969/1386079016233992323/weA8SX5bFQNjgAAAABJRU5ErkJggg.png",
    "National Park Service": "https://upload.wikimedia.org/wikipedia/commons/1/1d/US-NationalParkService-Logo.svg",
    "Greenville Fire Rescue": "https://cdn.discordapp.com/attachments/1350837749426683969/1386080475885342721/OJtZEa6wGaAAAAABJRU5ErkJggg.png",
    "Fox Valley Metro Police Department": "https://cdn.discordapp.com/attachments/1394042842850263251/1400210479221047357/Aw40x2jcktH1AAAAAElFTkSuQmCC.png"
}

class DeptFail(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @app_commands.guilds(1277047315047120978)
    @app_commands.command(name="deptfail", description="Announce a department application fail")
    @app_commands.describe(user="The user who failed", department="The department they failed for")
    async def deptfail(self, interaction: discord.Interaction, user: discord.User, department: str):
        await interaction.response.defer(ephemeral=True)
        # Check if user has the required role
        if not any(role.id == 1400212028353810572 for role in interaction.user.roles):
            await interaction.followup.send('You do not have permission to use this command.', ephemeral=True)
            return
        channel = interaction.guild.get_channel(1339745222220972032)
        if not channel:
            await interaction.followup.send('Could not find the announcement channel.', ephemeral=True)
            return
        try:
            embed = discord.Embed(
                color=0xFF0000,
                title=f"{department} | Application Result",
                description=f"Unfortunately {user.mention} has failed the {department} application"
            )
            embed.set_thumbnail(url=DEPARTMENTS[department])
            embed.set_footer(text="Mellow's Greenville Roleplay™")
            embed.timestamp = discord.utils.utcnow()
            await channel.send(embed=embed)
            await interaction.followup.send('Fail announcement sent!', ephemeral=True)
        except Exception as error:
            await interaction.followup.send('An error occurred while sending the announcement.', ephemeral=True)

async def setup(bot):
    await bot.add_cog(DeptFail(bot))
