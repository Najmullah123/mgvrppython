import os
import discord
from discord.ext import commands
from discord import app_commands

INSURANCE_CHANNEL = os.getenv('INSURANCE_CHANNEL', '1348992734366662707')

# Sticky message embed
sticky_embed = discord.Embed(
    title="📋 How to Submit an Insurance Claim", 
    description="Use the `/insuranceclaim` command to open an interactive claim form.",
    color=0xff6b6b
)
sticky_embed.add_field(name="Required Information", value="• Involved parties\n• Speed at time of accident\n• Location of incident\n• Description of what happened", inline=False)
sticky_embed.add_field(name="Optional", value="• Third party involved\n• Image evidence", inline=False)
sticky_embed.add_field(name="Note", value="⚠️ You cannot be forced to write a claim", inline=False)
sticky_embed.set_footer(text="This message will always stay at the bottom")

last_sticky_id = None

class InsuranceClaimModal(discord.ui.Modal, title="Submit Insurance Claim"):
    user1 = discord.ui.TextInput(
        label="First Person Involved",
        placeholder="Discord username or ID",
        required=True
    )
    
    user2 = discord.ui.TextInput(
        label="Second Person Involved", 
        placeholder="Discord username or ID",
        required=True
    )
    
    speed = discord.ui.TextInput(
        label="Speed at Time of Accident (MPH)",
        placeholder="e.g., 45",
        required=True
    )
    
    location = discord.ui.TextInput(
        label="Location of Accident",
        placeholder="e.g., Main Street intersection",
        required=True
    )
    
    reason = discord.ui.TextInput(
        label="Description of Incident",
        placeholder="Brief description of what happened",
        style=discord.TextStyle.paragraph,
        required=True,
        max_length=1000
    )
    
    async def on_submit(self, interaction: discord.Interaction):
        await interaction.response.defer(ephemeral=True)
        
        try:
            speed_value = float(self.speed.value)
        except ValueError:
            await interaction.followup.send("❌ Speed must be a valid number.", ephemeral=True)
            return
        
        # Process the claim
        cog = interaction.client.get_cog('InsuranceClaim')
        if cog:
            await cog.process_claim(
                interaction, 
                self.user1.value, 
                self.user2.value, 
                speed_value, 
                self.location.value, 
                self.reason.value
            )
        else:
            await interaction.followup.send("❌ Insurance claim system unavailable.", ephemeral=True)
class InsuranceClaim(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.last_sticky_id = None

    @app_commands.command(name="insuranceclaim", description="Submit an insurance claim using an interactive form")
    @app_commands.guilds(discord.Object(id=1277047315047120978))
    async def insuranceclaim(self, interaction: discord.Interaction):
        """Open insurance claim modal"""
        modal = InsuranceClaimModal()
        await interaction.response.send_modal(modal)
    
    async def process_claim(self, interaction: discord.Interaction, user1_input: str, user2_input: str, speed: float, location: str, reason: str):
        """Process the insurance claim after modal submission"""
        try:
            # Try to resolve users from input
            def resolve_user(user_input: str):
                # Try to get user by ID first
                if user_input.isdigit():
                    try:
                        return interaction.guild.get_member(int(user_input))
                    except:
                        pass
                
                # Try to find by username/display name
                for member in interaction.guild.members:
                    if (member.name.lower() == user_input.lower() or 
                        member.display_name.lower() == user_input.lower() or
                        str(member) == user_input):
                        return member
                
                return None
            
            user1 = resolve_user(user1_input)
            user2 = resolve_user(user2_input)
            
            if not user1:
                await interaction.followup.send(f"❌ Could not find user: {user1_input}", ephemeral=True)
                return
            
            if not user2:
                await interaction.followup.send(f"❌ Could not find user: {user2_input}", ephemeral=True)
                return
        
        claimant = interaction.user.id
        involved_users = f"<@{user1.id}>, <@{user2.id}>"
        
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
        
        except Exception as e:
            print(f"Error processing insurance claim: {e}")
            await interaction.followup.send("❌ An error occurred while processing your claim.", ephemeral=True)

async def setup(bot):
    await bot.add_cog(InsuranceClaim(bot))
