import os
import discord
from discord.ext import commands
from discord import app_commands

INSURANCE_CHANNEL = os.getenv('INSURANCE_CHANNEL', '1348992734366662707')

# Sticky message embed
sticky_embed = discord.Embed(
    title="📋 How to Submit an Insurance Claim",
    description="Use `/insuranceclaim` with the following information:",
    color=0xff6b6b
)
sticky_embed.add_field(name="User 1", value="First person involved in the accident", inline=True)
sticky_embed.add_field(name="User 2", value="Second person involved in the accident", inline=True)
sticky_embed.add_field(name="User 3", value="Optional: Third person involved", inline=True)
sticky_embed.add_field(name="Speed", value="Speed at time of accident in MPH", inline=True)
sticky_embed.add_field(name="Location", value="Where the accident occurred", inline=True)
sticky_embed.add_field(name="Reason", value="Brief description of what happened", inline=False)
sticky_embed.add_field(name="Image", value="Optional: Attach an image of the accident", inline=False)
sticky_embed.add_field(name="Note", value="⚠️ You cannot be forced to write a claim", inline=False)
sticky_embed.set_footer(text="This message will always stay at the bottom")

last_sticky_id = None

class InsuranceClaim(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.last_sticky_id = None

    @app_commands.guilds(1277047315047120978)
    @app_commands.command(name="insuranceclaim", description="Submit an insurance claim for a vehicle incident")
    @app_commands.describe(
        user1="First person involved in the accident",
        user2="Second person involved in the accident",
        speed="Speed at time of accident (MPH)",
        location="Location of the accident",
        reason="Reason for the accident",
        user3="Third person involved in the accident (optional)",
        image="Image of the accident (optional)"
    )
    async def insuranceclaim(self, interaction: discord.Interaction, user1: discord.User, user2: discord.User, speed: float, location: str, reason: str, user3: discord.User = None, image: discord.Attachment = None):
        await interaction.response.defer(ephemeral=True)
        claimant = interaction.user.id
        involved_users = f"<@{user1.id}>, <@{user2.id}>"
        if user3:
            involved_users += f", <@{user3.id}>"
        embed = discord.Embed(
            title="🚨 Insurance Claim Report",
            description=f"Claim filed by: <@{claimant}>",
            color=0xff6b6b
        )
        embed.add_field(name='\u200B', value='**Incident Details**')
        embed.add_field(name='Involved Parties', value=involved_users, inline=False)
        embed.add_field(name='Speed', value=f"{speed} MPH", inline=True)
        embed.add_field(name='Location', value=location, inline=True)
        embed.add_field(name='\u200B', value='\u200B', inline=True)
        embed.add_field(name='Reason', value=reason, inline=False)
        embed.set_footer(text='Insurance Claim System')
        embed.timestamp = discord.utils.utcnow()
        if image:
            embed.set_image(url=image.url)
        channel = interaction.client.get_channel(int(INSURANCE_CHANNEL)) if INSURANCE_CHANNEL.isdigit() else None
        if not channel or not hasattr(channel, 'send'):
            await interaction.followup.send("❌ Cannot submit claim. Channel configuration error.", ephemeral=True)
            return
        # Delete previous sticky if it exists
        if self.last_sticky_id:
            try:
                old_sticky = await channel.fetch_message(self.last_sticky_id)
                await old_sticky.delete()
            except Exception as err:
                print('Could not delete old sticky:', err)
        # Send claim embed
        await channel.send(embed=embed)
        # Send new sticky message and store its ID
        sticky_message = await channel.send(embed=sticky_embed)
        self.last_sticky_id = sticky_message.id
        await interaction.followup.send("✅ Your insurance claim has been submitted!", ephemeral=True)

async def setup(bot):
    await bot.add_cog(InsuranceClaim(bot))
