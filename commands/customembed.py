import discord
from discord.ext import commands
from discord import app_commands

class CustomEmbed(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @app_commands.guilds(1277047315047120978)
    @app_commands.command(name="customembed", description="Create a custom embed with specific elements")
    @app_commands.describe(title="The title of the embed", description="The description of the embed", image="URL of the image to include (optional)")
    async def customembed(self, interaction: discord.Interaction, title: str, description: str, image: str = None):
        await interaction.response.defer(ephemeral=True)
        description = description.replace("\\n", "\n")
        embed = discord.Embed(
            title=title,
            description=description,
            color=0x89CFF0
        )
        embed.set_thumbnail(url="https://cdn.discordapp.com/attachments/1393957236891713556/1395111568164913313/5b39ef01ba7ebe82c4789d0436064ac9-removebg-preview.png")
        embed.set_footer(text="Mellow's Greenville Roleplay™ - Developed by Baryonyx (Antivenom)")
        if image:
            try:
                embed.set_image(url=image)
            except Exception:
                await interaction.followup.send("Please provide a valid image URL.", ephemeral=True)
                return
        await interaction.channel.send(embed=embed)
        await interaction.followup.send("Embed sent successfully!", ephemeral=True)

async def setup(bot):
    await bot.add_cog(CustomEmbed(bot))
