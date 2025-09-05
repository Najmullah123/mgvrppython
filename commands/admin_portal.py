import discord
from discord.ext import commands
from discord import app_commands
import json
import os
from datetime import datetime, timedelta
import asyncio
from typing import Optional, List
import logging

logger = logging.getLogger(__name__)

# Admin role IDs - configure these in your .env or here
ADMIN_ROLES = [
    1400212028353810572,  # Existing admin role
    # Add more admin role IDs as needed
]

GUILD_ID = int(os.getenv('GUILD_ID', '1277047315047120978'))

class AdminPortalView(discord.ui.View):
    def __init__(self):
        super().__init__(timeout=300)
    
    @discord.ui.button(label="Server Management", style=discord.ButtonStyle.primary, emoji="🛠️")
    async def server_management(self, interaction: discord.Interaction, button: discord.ui.Button):
        embed = discord.Embed(
            title="🛠️ Server Management",
            description="Choose a server management action:",
            color=0x89CFF0
        )
        view = ServerManagementView()
        await interaction.response.send_message(embed=embed, view=view, ephemeral=True)
    
    @discord.ui.button(label="User Management", style=discord.ButtonStyle.secondary, emoji="👥")
    async def user_management(self, interaction: discord.Interaction, button: discord.ui.Button):
        embed = discord.Embed(
            title="👥 User Management",
            description="Choose a user management action:",
            color=0x89CFF0
        )
        view = UserManagementView()
        await interaction.response.send_message(embed=embed, view=view, ephemeral=True)
    
    @discord.ui.button(label="Data Management", style=discord.ButtonStyle.success, emoji="📊")
    async def data_management(self, interaction: discord.Interaction, button: discord.ui.Button):
        embed = discord.Embed(
            title="📊 Data Management",
            description="Choose a data management action:",
            color=0x89CFF0
        )
        view = DataManagementView()
        await interaction.response.send_message(embed=embed, view=view, ephemeral=True)
    
    @discord.ui.button(label="Bot Settings", style=discord.ButtonStyle.danger, emoji="⚙️")
    async def bot_settings(self, interaction: discord.Interaction, button: discord.ui.Button):
        embed = discord.Embed(
            title="⚙️ Bot Settings",
            description="Choose a bot settings action:",
            color=0x89CFF0
        )
        view = BotSettingsView()
        await interaction.response.send_message(embed=embed, view=view, ephemeral=True)

class ServerManagementView(discord.ui.View):
    def __init__(self):
        super().__init__(timeout=300)
    
    @discord.ui.button(label="Channel Cleanup", style=discord.ButtonStyle.secondary, emoji="🧹")
    async def channel_cleanup(self, interaction: discord.Interaction, button: discord.ui.Button):
        modal = ChannelCleanupModal()
        await interaction.response.send_modal(modal)
    
    @discord.ui.button(label="Mass Role Assignment", style=discord.ButtonStyle.secondary, emoji="🏷️")
    async def mass_role_assignment(self, interaction: discord.Interaction, button: discord.ui.Button):
        modal = MassRoleModal()
        await interaction.response.send_modal(modal)
    
    @discord.ui.button(label="Server Stats", style=discord.ButtonStyle.primary, emoji="📈")
    async def server_stats(self, interaction: discord.Interaction, button: discord.ui.Button):
        guild = interaction.guild
        
        # Calculate various stats
        total_members = guild.member_count
        online_members = sum(1 for member in guild.members if member.status != discord.Status.offline)
        bot_count = sum(1 for member in guild.members if member.bot)
        text_channels = len(guild.text_channels)
        voice_channels = len(guild.voice_channels)
        roles = len(guild.roles)
        
        embed = discord.Embed(
            title=f"📈 Server Statistics - {guild.name}",
            color=0x89CFF0,
            timestamp=datetime.utcnow()
        )
        embed.set_thumbnail(url=guild.icon.url if guild.icon else None)
        
        embed.add_field(name="👥 Members", value=f"Total: {total_members}\nOnline: {online_members}\nBots: {bot_count}", inline=True)
        embed.add_field(name="📝 Channels", value=f"Text: {text_channels}\nVoice: {voice_channels}", inline=True)
        embed.add_field(name="🏷️ Roles", value=roles, inline=True)
        embed.add_field(name="📅 Created", value=discord.utils.format_dt(guild.created_at, 'F'), inline=False)
        
        if guild.premium_subscription_count:
            embed.add_field(name="💎 Boosts", value=f"Level {guild.premium_tier} ({guild.premium_subscription_count} boosts)", inline=True)
        
        await interaction.response.send_message(embed=embed, ephemeral=True)

class UserManagementView(discord.ui.View):
    def __init__(self):
        super().__init__(timeout=300)
    
    @discord.ui.button(label="Bulk Ban", style=discord.ButtonStyle.danger, emoji="🔨")
    async def bulk_ban(self, interaction: discord.Interaction, button: discord.ui.Button):
        modal = BulkBanModal()
        await interaction.response.send_modal(modal)
    
    @discord.ui.button(label="User Lookup", style=discord.ButtonStyle.primary, emoji="🔍")
    async def user_lookup(self, interaction: discord.Interaction, button: discord.ui.Button):
        modal = UserLookupModal()
        await interaction.response.send_modal(modal)
    
    @discord.ui.button(label="Inactive Members", style=discord.ButtonStyle.secondary, emoji="😴")
    async def inactive_members(self, interaction: discord.Interaction, button: discord.ui.Button):
        await interaction.response.defer(ephemeral=True)
        
        # Find members who haven't been active in 30 days
        cutoff_date = datetime.utcnow() - timedelta(days=30)
        inactive_members = []
        
        for member in interaction.guild.members:
            if member.bot:
                continue
            
            # Check if member has any recent activity (this is a simplified check)
            if member.joined_at and member.joined_at < cutoff_date:
                # In a real implementation, you'd check message history, voice activity, etc.
                inactive_members.append(member)
        
        if not inactive_members:
            await interaction.followup.send("✅ No inactive members found!", ephemeral=True)
            return
        
        # Limit to first 20 for display
        display_members = inactive_members[:20]
        member_list = "\n".join([f"• {member.mention} ({member.display_name})" for member in display_members])
        
        embed = discord.Embed(
            title="😴 Inactive Members",
            description=f"Found {len(inactive_members)} inactive members (showing first 20):\n\n{member_list}",
            color=0xffa500
        )
        
        await interaction.followup.send(embed=embed, ephemeral=True)

class DataManagementView(discord.ui.View):
    def __init__(self):
        super().__init__(timeout=300)
    
    @discord.ui.button(label="Vehicle Database", style=discord.ButtonStyle.primary, emoji="🚗")
    async def vehicle_database(self, interaction: discord.Interaction, button: discord.ui.Button):
        try:
            from pathlib import Path
            vehicles_file = Path("data/vehicles.json")
            
            if not vehicles_file.exists():
                await interaction.response.send_message("❌ Vehicle database not found!", ephemeral=True)
                return
            
            with open(vehicles_file, 'r') as f:
                data = json.load(f)
            
            total_vehicles = len(data.get('vehicles', []))
            
            # Count by state
            state_counts = {}
            for vehicle in data.get('vehicles', []):
                state = vehicle.get('state', 'Unknown')
                state_counts[state] = state_counts.get(state, 0) + 1
            
            top_states = sorted(state_counts.items(), key=lambda x: x[1], reverse=True)[:5]
            
            embed = discord.Embed(
                title="🚗 Vehicle Database Statistics",
                color=0x89CFF0,
                timestamp=datetime.utcnow()
            )
            
            embed.add_field(name="Total Vehicles", value=total_vehicles, inline=True)
            embed.add_field(name="Unique States", value=len(state_counts), inline=True)
            embed.add_field(name="Top States", value="\n".join([f"{state}: {count}" for state, count in top_states]), inline=False)
            
            view = VehicleManagementView()
            await interaction.response.send_message(embed=embed, view=view, ephemeral=True)
            
        except Exception as e:
            logger.error(f"Error accessing vehicle database: {e}")
            await interaction.response.send_message("❌ Error accessing vehicle database!", ephemeral=True)
    
    @discord.ui.button(label="Backup Data", style=discord.ButtonStyle.success, emoji="💾")
    async def backup_data(self, interaction: discord.Interaction, button: discord.ui.Button):
        await interaction.response.defer(ephemeral=True)
        
        try:
            from pathlib import Path
            import shutil
            
            data_dir = Path("data")
            backup_dir = Path("backups")
            backup_dir.mkdir(exist_ok=True)
            
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            backup_path = backup_dir / f"backup_{timestamp}"
            
            if data_dir.exists():
                shutil.copytree(data_dir, backup_path)
                await interaction.followup.send(f"✅ Data backed up to `{backup_path}`", ephemeral=True)
            else:
                await interaction.followup.send("❌ No data directory found to backup!", ephemeral=True)
                
        except Exception as e:
            logger.error(f"Backup error: {e}")
            await interaction.followup.send("❌ Error creating backup!", ephemeral=True)

class BotSettingsView(discord.ui.View):
    def __init__(self):
        super().__init__(timeout=300)
    
    @discord.ui.button(label="Reload Commands", style=discord.ButtonStyle.primary, emoji="🔄")
    async def reload_commands(self, interaction: discord.Interaction, button: discord.ui.Button):
        await interaction.response.defer(ephemeral=True)
        
        try:
            # Reload all extensions
            for extension in list(interaction.client.extensions.keys()):
                await interaction.client.reload_extension(extension)
            
            await interaction.followup.send("✅ All commands reloaded successfully!", ephemeral=True)
        except Exception as e:
            logger.error(f"Error reloading commands: {e}")
            await interaction.followup.send(f"❌ Error reloading commands: {e}", ephemeral=True)
    
    @discord.ui.button(label="System Info", style=discord.ButtonStyle.secondary, emoji="💻")
    async def system_info(self, interaction: discord.Interaction, button: discord.ui.Button):
        import psutil
        import platform
        
        # System information
        cpu_percent = psutil.cpu_percent(interval=1)
        memory = psutil.virtual_memory()
        disk = psutil.disk_usage('/')
        
        embed = discord.Embed(
            title="💻 System Information",
            color=0x89CFF0,
            timestamp=datetime.utcnow()
        )
        
        embed.add_field(name="Platform", value=platform.system(), inline=True)
        embed.add_field(name="Python Version", value=platform.python_version(), inline=True)
        embed.add_field(name="CPU Usage", value=f"{cpu_percent}%", inline=True)
        embed.add_field(name="Memory Usage", value=f"{memory.percent}% ({memory.used // 1024 // 1024} MB)", inline=True)
        embed.add_field(name="Disk Usage", value=f"{disk.percent}% ({disk.used // 1024 // 1024 // 1024} GB)", inline=True)
        
        await interaction.response.send_message(embed=embed, ephemeral=True)

class VehicleManagementView(discord.ui.View):
    def __init__(self):
        super().__init__(timeout=300)
    
    @discord.ui.button(label="Clear Test Vehicles", style=discord.ButtonStyle.danger, emoji="🧹")
    async def clear_test_vehicles(self, interaction: discord.Interaction, button: discord.ui.Button):
        await interaction.response.defer(ephemeral=True)
        
        try:
            from pathlib import Path
            vehicles_file = Path("data/vehicles.json")
            
            with open(vehicles_file, 'r') as f:
                data = json.load(f)
            
            original_count = len(data.get('vehicles', []))
            
            # Remove test vehicles
            data['vehicles'] = [
                vehicle for vehicle in data.get('vehicles', [])
                if not (vehicle.get('make', '').lower() == 'test' or 
                       vehicle.get('model', '').lower() == 'test' or
                       vehicle.get('plate', '').upper() == 'TEST')
            ]
            
            removed_count = original_count - len(data['vehicles'])
            
            with open(vehicles_file, 'w') as f:
                json.dump(data, f, indent=2)
            
            await interaction.followup.send(f"✅ Removed {removed_count} test vehicles from database!", ephemeral=True)
            
        except Exception as e:
            logger.error(f"Error clearing test vehicles: {e}")
            await interaction.followup.send("❌ Error clearing test vehicles!", ephemeral=True)

# Modal classes for various admin functions
class ChannelCleanupModal(discord.ui.Modal, title="Channel Cleanup"):
    channel_id = discord.ui.TextInput(label="Channel ID", placeholder="Enter channel ID to clean up")
    message_count = discord.ui.TextInput(label="Message Count", placeholder="Number of messages to delete (max 100)", default="10")
    
    async def on_submit(self, interaction: discord.Interaction):
        await interaction.response.defer(ephemeral=True)
        
        try:
            channel = interaction.guild.get_channel(int(self.channel_id.value))
            if not channel:
                await interaction.followup.send("❌ Channel not found!", ephemeral=True)
                return
            
            count = min(int(self.message_count.value), 100)
            deleted = await channel.purge(limit=count)
            
            await interaction.followup.send(f"✅ Deleted {len(deleted)} messages from {channel.mention}!", ephemeral=True)
            
        except Exception as e:
            await interaction.followup.send(f"❌ Error: {e}", ephemeral=True)

class MassRoleModal(discord.ui.Modal, title="Mass Role Assignment"):
    role_id = discord.ui.TextInput(label="Role ID", placeholder="Enter role ID to assign/remove")
    user_ids = discord.ui.TextInput(label="User IDs", placeholder="Enter user IDs separated by commas", style=discord.TextStyle.paragraph)
    action = discord.ui.TextInput(label="Action", placeholder="'add' or 'remove'", default="add")
    
    async def on_submit(self, interaction: discord.Interaction):
        await interaction.response.defer(ephemeral=True)
        
        try:
            role = interaction.guild.get_role(int(self.role_id.value))
            if not role:
                await interaction.followup.send("❌ Role not found!", ephemeral=True)
                return
            
            user_id_list = [int(uid.strip()) for uid in self.user_ids.value.split(',')]
            action = self.action.value.lower()
            
            success_count = 0
            for user_id in user_id_list:
                try:
                    member = interaction.guild.get_member(user_id)
                    if member:
                        if action == 'add':
                            await member.add_roles(role)
                        elif action == 'remove':
                            await member.remove_roles(role)
                        success_count += 1
                except:
                    continue
            
            await interaction.followup.send(f"✅ Successfully {action}ed role {role.name} for {success_count} members!", ephemeral=True)
            
        except Exception as e:
            await interaction.followup.send(f"❌ Error: {e}", ephemeral=True)

class BulkBanModal(discord.ui.Modal, title="Bulk Ban Users"):
    user_ids = discord.ui.TextInput(label="User IDs", placeholder="Enter user IDs separated by commas", style=discord.TextStyle.paragraph)
    reason = discord.ui.TextInput(label="Reason", placeholder="Ban reason", default="Bulk ban via admin portal")
    
    async def on_submit(self, interaction: discord.Interaction):
        await interaction.response.defer(ephemeral=True)
        
        try:
            user_id_list = [int(uid.strip()) for uid in self.user_ids.value.split(',')]
            reason = self.reason.value
            
            success_count = 0
            for user_id in user_id_list:
                try:
                    user = await interaction.client.fetch_user(user_id)
                    await interaction.guild.ban(user, reason=reason)
                    success_count += 1
                except:
                    continue
            
            await interaction.followup.send(f"✅ Successfully banned {success_count} users!", ephemeral=True)
            
        except Exception as e:
            await interaction.followup.send(f"❌ Error: {e}", ephemeral=True)

class UserLookupModal(discord.ui.Modal, title="User Lookup"):
    user_input = discord.ui.TextInput(label="User ID or Username", placeholder="Enter user ID or username")
    
    async def on_submit(self, interaction: discord.Interaction):
        await interaction.response.defer(ephemeral=True)
        
        try:
            # Try to find user by ID first
            user = None
            if self.user_input.value.isdigit():
                try:
                    user = await interaction.client.fetch_user(int(self.user_input.value))
                except:
                    pass
            
            # If not found by ID, search by username
            if not user:
                for member in interaction.guild.members:
                    if (member.name.lower() == self.user_input.value.lower() or 
                        member.display_name.lower() == self.user_input.value.lower()):
                        user = member
                        break
            
            if not user:
                await interaction.followup.send("❌ User not found!", ephemeral=True)
                return
            
            # Get member info if they're in the guild
            member = interaction.guild.get_member(user.id) if hasattr(user, 'id') else None
            
            embed = discord.Embed(
                title=f"👤 User Information - {user.display_name}",
                color=0x89CFF0,
                timestamp=datetime.utcnow()
            )
            
            embed.set_thumbnail(url=user.avatar.url if user.avatar else user.default_avatar.url)
            embed.add_field(name="Username", value=f"{user.name}#{user.discriminator}", inline=True)
            embed.add_field(name="ID", value=user.id, inline=True)
            embed.add_field(name="Created", value=discord.utils.format_dt(user.created_at, 'F'), inline=False)
            
            if member:
                embed.add_field(name="Joined", value=discord.utils.format_dt(member.joined_at, 'F'), inline=True)
                embed.add_field(name="Roles", value=f"{len(member.roles)} roles", inline=True)
                embed.add_field(name="Status", value=str(member.status).title(), inline=True)
            
            await interaction.followup.send(embed=embed, ephemeral=True)
            
        except Exception as e:
            await interaction.followup.send(f"❌ Error: {e}", ephemeral=True)

class AdminPortal(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
    
    def is_admin(self, user: discord.Member) -> bool:
        """Check if user has admin permissions"""
        if user.guild_permissions.administrator:
            return True
        
        for role in user.roles:
            if role.id in ADMIN_ROLES:
                return True
        
        return False
    
    @app_commands.command(name="admin", description="Open the admin portal")
    @app_commands.guilds(discord.Object(id=GUILD_ID))
    async def admin_portal(self, interaction: discord.Interaction):
        if not self.is_admin(interaction.user):
            await interaction.response.send_message("❌ You don't have permission to access the admin portal.", ephemeral=True)
            return
        
        embed = discord.Embed(
            title="🛡️ Admin Portal",
            description="Welcome to the MGVRP Admin Portal. Choose a category below to get started.",
            color=0x89CFF0,
            timestamp=datetime.utcnow()
        )
        
        embed.add_field(
            name="🛠️ Server Management", 
            value="Channel cleanup, role management, server statistics", 
            inline=False
        )
        embed.add_field(
            name="👥 User Management", 
            value="User lookup, bulk actions, inactive member detection", 
            inline=False
        )
        embed.add_field(
            name="📊 Data Management", 
            value="Vehicle database, backups, data cleanup", 
            inline=False
        )
        embed.add_field(
            name="⚙️ Bot Settings", 
            value="Command reloading, system information, configuration", 
            inline=False
        )
        
        embed.set_footer(text="Mellow's Greenville Roleplay™ - Admin Portal")
        embed.set_thumbnail(url="https://cdn.discordapp.com/attachments/1350837749426683969/1387479314861391964/main_server_logo.webp")
        
        view = AdminPortalView()
        await interaction.response.send_message(embed=embed, view=view, ephemeral=True)
    
    @app_commands.command(name="emergency_shutdown", description="Emergency bot shutdown (Admin only)")
    @app_commands.guilds(discord.Object(id=GUILD_ID))
    async def emergency_shutdown(self, interaction: discord.Interaction):
        if not self.is_admin(interaction.user):
            await interaction.response.send_message("❌ You don't have permission to use this command.", ephemeral=True)
            return
        
        embed = discord.Embed(
            title="🚨 Emergency Shutdown",
            description="Bot is shutting down...",
            color=0xff0000
        )
        
        await interaction.response.send_message(embed=embed, ephemeral=True)
        logger.warning(f"Emergency shutdown initiated by {interaction.user}")
        
        await asyncio.sleep(2)
        await self.bot.close()

async def setup(bot):
    await bot.add_cog(AdminPortal(bot))