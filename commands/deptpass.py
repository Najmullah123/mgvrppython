import discord
from discord.ext import commands
from discord import app_commands
import os

departments = {
    "Outagamie County Sheriff's Office": 'https://cdn.discordapp.com/attachments/1350837749426683969/1386075499754950868/dNlvRACGdUAAAAAElFTkSuQmCC.png',
    'Wisconsin State Patrol': 'https://cdn.discordapp.com/attachments/1350837749426683969/1386077443840016535/hNQjWXuFkjciQAAAABJRU5ErkJggg.png',
    'Wisconsin Department of Transportation': 'https://cdn.discordapp.com/attachments/1350837749426683969/1386079016233992323/weA8SX5bFQNjgAAAABJRU5ErkJggg.png',
    'National Park Service': 'https://upload.wikimedia.org/wikipedia/commons/1/1d/US-NationalParkService-Logo.svg',
    'Greenville Fire Rescue': 'https://cdn.discordapp.com/attachments/1350837749426683969/1386080475885342721/OJtZEa6wGaAAAAABJRU5ErkJggg.png',
    'Fox Valley Metro Police Department': 'https://cdn.discordapp.com/attachments/1394042842850263251/1400210479221047357/Aw40x2jcktH1AAAAAElFTkSuQmCC.png',
    'MGVRP Staff Team Application': 'https://cdn.discordapp.com/attachments/1393957236891713556/1395111568164913313/5b39ef01ba7ebe82c4789d0436064ac9-removebg-preview.png?ex=68a37265&is=68a220e5&hm=b27078d6f94b0ba723b8b0dd86391aaaa261eafcd6eb08dc31381282755654b6&'
}

ANNOUNCE_CHANNEL_ID = int(os.getenv('ANNOUNCE_CHANNEL_ID', '1339745222220972032'))


class DeptPass(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @app_commands.guilds(1277047315047120978)
    @app_commands.command(name="deptpass", description="Announce a department application pass")
    @app_commands.describe(
        user="The user who passed",
        department="The department they passed for"
    )
    @app_commands.choices(
        department=[app_commands.Choice(name=dept, value=dept) for dept in departments.keys()]
    )
    async def deptpass(self, interaction: discord.Interaction, user: discord.User, department: app_commands.Choice[str]):
        await interaction.response.defer(ephemeral=True)
    # Anyone can use this command
        channel = interaction.guild.get_channel(ANNOUNCE_CHANNEL_ID)
        if not channel:
            await interaction.followup.send('Could not find the announcement channel.', ephemeral=True)
            return
        try:
            embed = discord.Embed(
                color=0x89CFF0,
                title=f"{department.value} | Application Result",
                description=f"Congratulations {user.mention} You have successfully passed the {department.value} application"
            )
            embed.set_thumbnail(url=departments[department.value])
            embed.set_footer(text="Mellow's Greenville Roleplay™")
            embed.timestamp = discord.utils.utcnow()
            await channel.send(embed=embed)
            await interaction.followup.send('Pass announcement sent!', ephemeral=True)
        except Exception as error:
            print('Error in deptpass command:', error)
            await interaction.followup.send('An error occurred while sending the announcement.', ephemeral=True)

async def setup(bot):
    await bot.add_cog(DeptPass(bot))
