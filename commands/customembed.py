import discord
from discord.ext import commands
from discord import app_commands

class CustomEmbedModal(discord.ui.Modal, title="Create Custom Embed"):
    title_input = discord.ui.TextInput(
        label="Embed Title",
        placeholder="Enter the title for your embed",
        required=True,
        max_length=256
    )
    
    description_input = discord.ui.TextInput(
        label="Embed Description",
        placeholder="Enter the description (use \\n for new lines)",
        style=discord.TextStyle.paragraph,
        required=True,
        max_length=4000
    )
    
    color_input = discord.ui.TextInput(
        label="Embed Color (Hex)",
        placeholder="e.g., #89CFF0 or 89CFF0",
        required=False,
        default="89CFF0",
        max_length=7
    )
    
    image_input = discord.ui.TextInput(
        label="Image URL (Optional)",
        placeholder="https://example.com/image.png",
        required=False
    )
    
    footer_input = discord.ui.TextInput(
        label="Footer Text (Optional)",
        placeholder="Custom footer text",
        required=False,
        max_length=2048
    )
    
    async def on_submit(self, interaction: discord.Interaction):
        await interaction.response.defer(ephemeral=True)
        
        # Process inputs
        title = self.title_input.value.replace("\\n", "\n")
        description = self.description_input.value.replace("\\n", "\n")
        
        # Parse color
        color_str = self.color_input.value.strip()
        if color_str.startswith('#'):
            color_str = color_str[1:]
        
        try:
            color = int(color_str, 16) if color_str else 0x89CFF0
        except ValueError:
            color = 0x89CFF0
        
        # Create embed
        embed = discord.Embed(
            title=title,
            description=description,
            color=color
        )
        
        # Add thumbnail
        embed.set_thumbnail(url="https://cdn.discordapp.com/attachments/1393957236891713556/1395111568164913313/5b39ef01ba7ebe82c4789d0436064ac9-removebg-preview.png")
        
        # Add image if provided
        if self.image_input.value:
            try:
                embed.set_image(url=self.image_input.value)
            except Exception:
                await interaction.followup.send("⚠️ Invalid image URL provided, embed sent without image.", ephemeral=True)
        
        # Add footer
        footer_text = self.footer_input.value if self.footer_input.value else "Mellow's Greenville Roleplay™ - Developed by Baryonyx (Antivenom)"
        embed.set_footer(text=footer_text)
        
        try:
            await interaction.channel.send(embed=embed)
            await interaction.followup.send("✅ Custom embed sent successfully!", ephemeral=True)
        except Exception as e:
            await interaction.followup.send(f"❌ Error sending embed: {str(e)}", ephemeral=True)
class CustomEmbed(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @app_commands.command(name="customembed", description="Create a custom embed using an interactive form")
    @app_commands.guilds(discord.Object(id=1277047315047120978))
    async def customembed(self, interaction: discord.Interaction):
        """Open custom embed creation modal"""
        modal = CustomEmbedModal()
        await interaction.response.send_modal(modal)

async def setup(bot):
    await bot.add_cog(CustomEmbed(bot))
