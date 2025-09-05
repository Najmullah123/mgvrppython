import discord
from discord.ext import commands
from discord import app_commands

class DMEmbed(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @app_commands.guilds(1277047315047120978)
    @app_commands.command(name="dmembed", description="Send a custom embed to a user via DM")
    @app_commands.describe(user="The user to DM", title="The title of the embed", description="The description of the embed", color="The color of the embed", thumbnail="The thumbnail URL (optional)", image="The image URL (optional)", footer="The footer text (optional)")
    @app_commands.choices(color=[
        app_commands.Choice(name="Red", value="#ff0000"),
        app_commands.Choice(name="Green", value="#00ff00"),
        app_commands.Choice(name="MGVRP Blue", value="#89CFF0"),
        app_commands.Choice(name="Yellow", value="#ffff00")
    ])
    async def dmembed(self, interaction: discord.Interaction, user: discord.User, title: str, description: str, color: app_commands.Choice[str], thumbnail: str = None, image: str = None, footer: str = None):
        await interaction.response.defer(ephemeral=True)
        description = description.replace("\\n", "\n")
        title = title.replace("\\n", "\n")
        if footer:
            footer = footer.replace("\\n", "\n")
        embed = discord.Embed(
            title=title,
            description=description,
            color=int(color.value.replace('#', ''), 16)
        )
        if thumbnail:
            embed.set_thumbnail(url=thumbnail)
        if image:
            embed.set_image(url=image)
        if footer:
            embed.set_footer(text=footer)
        try:
            await user.send(embed=embed)
            await interaction.followup.send(f"Embed sent to {user.mention} successfully!", ephemeral=True)
        except Exception:
            await interaction.followup.send(f"Failed to send embed to {user.mention}. They may have DMs disabled.", ephemeral=True)

async def setup(bot):
    await bot.add_cog(DMEmbed(bot))
