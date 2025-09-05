import discord
from discord.ext import commands
from discord import app_commands
import json
import os
from datetime import datetime, timedelta
from pathlib import Path
import logging
from typing import Optional, List
import asyncio

logger = logging.getLogger(__name__)

GUILD_ID = int(os.getenv("GUILD_ID", "1277047315047120978"))
MOD_LOG_CHANNEL = int(os.getenv("MOD_LOG_CHANNEL", "1339764330425487460"))
DATA_DIR = Path(os.path.dirname(os.path.abspath(__file__))) / ".." / "data"
WARNINGS_FILE = DATA_DIR / "warnings.json"
MUTES_FILE = DATA_DIR / "mutes.json"

# Moderation roles
MOD_ROLES = [
    1400212028353810572,  # Admin role
    # Add more moderator role IDs as needed
]

class ModerationSystem(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        DATA_DIR.mkdir(exist_ok=True)
        self.ensure_files_exist()
    
    def ensure_files_exist(self):
        """Ensure moderation data files exist"""
        for file_path in [WARNINGS_FILE, MUTES_FILE]:
            if not file_path.exists():
                with file_path.open("w", encoding="utf-8") as f:
                    json.dump({"data": []}, f, indent=2)
    
    def is_moderator(self, user: discord.Member) -> bool:
        """Check if user has moderation permissions"""
        if user.guild_permissions.moderate_members or user.guild_permissions.administrator:
            return True
        
        for role in user.roles:
            if role.id in MOD_ROLES:
                return True
        
        return False
    
    async def log_action(self, guild: discord.Guild, action: str, moderator: discord.Member, target: discord.Member, reason: str, duration: Optional[str] = None):
        """Log moderation actions"""
        try:
            log_channel = guild.get_channel(MOD_LOG_CHANNEL)
            if not log_channel:
                return
            
            embed = discord.Embed(
                title=f"🛡️ Moderation Action: {action}",
                color=0xff6b6b,
                timestamp=datetime.utcnow()
            )
            
            embed.add_field(name="Target", value=f"{target.mention} ({target.id})", inline=True)
            embed.add_field(name="Moderator", value=f"{moderator.mention} ({moderator.id})", inline=True)
            embed.add_field(name="Reason", value=reason or "No reason provided", inline=False)
            
            if duration:
                embed.add_field(name="Duration", value=duration, inline=True)
            
            embed.set_thumbnail(url=target.avatar.url if target.avatar else target.default_avatar.url)
            embed.set_footer(text="MGVRP Moderation System")
            
            await log_channel.send(embed=embed)
            
        except Exception as e:
            logger.error(f"Error logging moderation action: {e}")
    
    @app_commands.command(name="warn", description="Warn a user")
    @app_commands.describe(user="User to warn", reason="Reason for the warning")
    @app_commands.guilds(discord.Object(id=GUILD_ID))
    async def warn_user(self, interaction: discord.Interaction, user: discord.Member, reason: str):
        if not self.is_moderator(interaction.user):
            await interaction.response.send_message("❌ You don't have permission to warn users.", ephemeral=True)
            return
        
        await interaction.response.defer(ephemeral=True)
        
        try:
            # Load warnings data
            with WARNINGS_FILE.open("r", encoding="utf-8") as f:
                data = json.load(f)
            
            # Add new warning
            warning = {
                "id": len(data["data"]) + 1,
                "user_id": str(user.id),
                "moderator_id": str(interaction.user.id),
                "reason": reason,
                "timestamp": datetime.utcnow().isoformat(),
                "guild_id": str(interaction.guild.id)
            }
            
            data["data"].append(warning)
            
            # Save warnings data
            with WARNINGS_FILE.open("w", encoding="utf-8") as f:
                json.dump(data, f, indent=2)
            
            # Count user's warnings
            user_warnings = [w for w in data["data"] if w["user_id"] == str(user.id)]
            warning_count = len(user_warnings)
            
            # Send warning to user
            try:
                dm_embed = discord.Embed(
                    title="⚠️ Warning Received",
                    description=f"You have been warned in **{interaction.guild.name}**",
                    color=0xffa500
                )
                dm_embed.add_field(name="Reason", value=reason, inline=False)
                dm_embed.add_field(name="Moderator", value=interaction.user.display_name, inline=True)
                dm_embed.add_field(name="Total Warnings", value=warning_count, inline=True)
                dm_embed.set_footer(text="Please review the server rules to avoid further warnings.")
                
                await user.send(embed=dm_embed)
            except:
                pass  # User has DMs disabled
            
            # Log the action
            await self.log_action(interaction.guild, "Warning", interaction.user, user, reason)
            
            # Response embed
            embed = discord.Embed(
                title="⚠️ User Warned",
                color=0xffa500
            )
            embed.add_field(name="User", value=f"{user.mention} ({user.id})", inline=True)
            embed.add_field(name="Reason", value=reason, inline=True)
            embed.add_field(name="Total Warnings", value=warning_count, inline=True)
            
            await interaction.followup.send(embed=embed, ephemeral=True)
            
        except Exception as e:
            logger.error(f"Error warning user: {e}")
            await interaction.followup.send("❌ Error issuing warning.", ephemeral=True)
    
    @app_commands.command(name="warnings", description="View warnings for a user")
    @app_commands.describe(user="User to check warnings for")
    @app_commands.guilds(discord.Object(id=GUILD_ID))
    async def view_warnings(self, interaction: discord.Interaction, user: discord.Member):
        if not self.is_moderator(interaction.user):
            await interaction.response.send_message("❌ You don't have permission to view warnings.", ephemeral=True)
            return
        
        await interaction.response.defer(ephemeral=True)
        
        try:
            with WARNINGS_FILE.open("r", encoding="utf-8") as f:
                data = json.load(f)
            
            user_warnings = [w for w in data["data"] if w["user_id"] == str(user.id)]
            
            if not user_warnings:
                await interaction.followup.send(f"✅ {user.mention} has no warnings.", ephemeral=True)
                return
            
            embed = discord.Embed(
                title=f"⚠️ Warnings for {user.display_name}",
                description=f"Total warnings: {len(user_warnings)}",
                color=0xffa500,
                timestamp=datetime.utcnow()
            )
            
            embed.set_thumbnail(url=user.avatar.url if user.avatar else user.default_avatar.url)
            
            # Show last 5 warnings
            recent_warnings = sorted(user_warnings, key=lambda x: x["timestamp"], reverse=True)[:5]
            
            for i, warning in enumerate(recent_warnings, 1):
                timestamp = datetime.fromisoformat(warning["timestamp"])
                moderator = interaction.guild.get_member(int(warning["moderator_id"]))
                mod_name = moderator.display_name if moderator else "Unknown Moderator"
                
                embed.add_field(
                    name=f"Warning #{warning['id']}",
                    value=f"**Reason:** {warning['reason']}\n**Moderator:** {mod_name}\n**Date:** {discord.utils.format_dt(timestamp, 'R')}",
                    inline=False
                )
            
            if len(user_warnings) > 5:
                embed.add_field(
                    name="📝 Note",
                    value=f"Showing 5 most recent warnings. User has {len(user_warnings) - 5} more.",
                    inline=False
                )
            
            await interaction.followup.send(embed=embed, ephemeral=True)
            
        except Exception as e:
            logger.error(f"Error viewing warnings: {e}")
            await interaction.followup.send("❌ Error retrieving warnings.", ephemeral=True)
    
    @app_commands.command(name="timeout", description="Timeout a user")
    @app_commands.describe(
        user="User to timeout",
        duration="Duration (e.g., 10m, 1h, 1d)",
        reason="Reason for timeout"
    )
    @app_commands.guilds(discord.Object(id=GUILD_ID))
    async def timeout_user(self, interaction: discord.Interaction, user: discord.Member, duration: str, reason: str):
        if not self.is_moderator(interaction.user):
            await interaction.response.send_message("❌ You don't have permission to timeout users.", ephemeral=True)
            return
        
        await interaction.response.defer(ephemeral=True)
        
        try:
            # Parse duration
            duration_seconds = self.parse_duration(duration)
            if not duration_seconds:
                await interaction.followup.send("❌ Invalid duration format. Use formats like: 10m, 1h, 2d", ephemeral=True)
                return
            
            if duration_seconds > 2419200:  # 28 days max
                await interaction.followup.send("❌ Maximum timeout duration is 28 days.", ephemeral=True)
                return
            
            # Apply timeout
            timeout_until = datetime.utcnow() + timedelta(seconds=duration_seconds)
            await user.timeout(timeout_until, reason=reason)
            
            # Log the action
            await self.log_action(interaction.guild, "Timeout", interaction.user, user, reason, duration)
            
            # Send DM to user
            try:
                dm_embed = discord.Embed(
                    title="⏰ Timeout Applied",
                    description=f"You have been timed out in **{interaction.guild.name}**",
                    color=0xff6b6b
                )
                dm_embed.add_field(name="Duration", value=duration, inline=True)
                dm_embed.add_field(name="Reason", value=reason, inline=False)
                dm_embed.add_field(name="Expires", value=discord.utils.format_dt(timeout_until, 'F'), inline=False)
                
                await user.send(embed=dm_embed)
            except:
                pass
            
            # Response
            embed = discord.Embed(
                title="⏰ User Timed Out",
                color=0xff6b6b
            )
            embed.add_field(name="User", value=f"{user.mention} ({user.id})", inline=True)
            embed.add_field(name="Duration", value=duration, inline=True)
            embed.add_field(name="Expires", value=discord.utils.format_dt(timeout_until, 'R'), inline=True)
            embed.add_field(name="Reason", value=reason, inline=False)
            
            await interaction.followup.send(embed=embed, ephemeral=True)
            
        except Exception as e:
            logger.error(f"Error timing out user: {e}")
            await interaction.followup.send("❌ Error applying timeout.", ephemeral=True)
    
    @app_commands.command(name="untimeout", description="Remove timeout from a user")
    @app_commands.describe(user="User to remove timeout from", reason="Reason for removing timeout")
    @app_commands.guilds(discord.Object(id=GUILD_ID))
    async def untimeout_user(self, interaction: discord.Interaction, user: discord.Member, reason: Optional[str] = "No reason provided"):
        if not self.is_moderator(interaction.user):
            await interaction.response.send_message("❌ You don't have permission to remove timeouts.", ephemeral=True)
            return
        
        if not user.is_timed_out():
            await interaction.response.send_message("❌ User is not currently timed out.", ephemeral=True)
            return
        
        await interaction.response.defer(ephemeral=True)
        
        try:
            await user.timeout(None, reason=reason)
            
            # Log the action
            await self.log_action(interaction.guild, "Timeout Removed", interaction.user, user, reason)
            
            embed = discord.Embed(
                title="✅ Timeout Removed",
                description=f"Timeout removed from {user.mention}",
                color=0x00ff00
            )
            embed.add_field(name="Reason", value=reason, inline=False)
            
            await interaction.followup.send(embed=embed, ephemeral=True)
            
        except Exception as e:
            logger.error(f"Error removing timeout: {e}")
            await interaction.followup.send("❌ Error removing timeout.", ephemeral=True)
    
    @app_commands.command(name="kick", description="Kick a user from the server")
    @app_commands.describe(user="User to kick", reason="Reason for kick")
    @app_commands.guilds(discord.Object(id=GUILD_ID))
    async def kick_user(self, interaction: discord.Interaction, user: discord.Member, reason: str):
        if not self.is_moderator(interaction.user):
            await interaction.response.send_message("❌ You don't have permission to kick users.", ephemeral=True)
            return
        
        if user.top_role >= interaction.user.top_role and not interaction.user.guild_permissions.administrator:
            await interaction.response.send_message("❌ You cannot kick users with equal or higher roles.", ephemeral=True)
            return
        
        await interaction.response.defer(ephemeral=True)
        
        try:
            # Send DM before kicking
            try:
                dm_embed = discord.Embed(
                    title="👢 Kicked from Server",
                    description=f"You have been kicked from **{interaction.guild.name}**",
                    color=0xff6b6b
                )
                dm_embed.add_field(name="Reason", value=reason, inline=False)
                dm_embed.add_field(name="Moderator", value=interaction.user.display_name, inline=True)
                
                await user.send(embed=dm_embed)
            except:
                pass
            
            await user.kick(reason=reason)
            
            # Log the action
            await self.log_action(interaction.guild, "Kick", interaction.user, user, reason)
            
            embed = discord.Embed(
                title="👢 User Kicked",
                color=0xff6b6b
            )
            embed.add_field(name="User", value=f"{user.mention} ({user.id})", inline=True)
            embed.add_field(name="Reason", value=reason, inline=False)
            
            await interaction.followup.send(embed=embed, ephemeral=True)
            
        except Exception as e:
            logger.error(f"Error kicking user: {e}")
            await interaction.followup.send("❌ Error kicking user.", ephemeral=True)
    
    @app_commands.command(name="ban", description="Ban a user from the server")
    @app_commands.describe(
        user="User to ban",
        reason="Reason for ban",
        delete_messages="Delete messages from last X days (0-7)"
    )
    @app_commands.guilds(discord.Object(id=GUILD_ID))
    async def ban_user(self, interaction: discord.Interaction, user: discord.Member, reason: str, delete_messages: Optional[int] = 0):
        if not self.is_moderator(interaction.user):
            await interaction.response.send_message("❌ You don't have permission to ban users.", ephemeral=True)
            return
        
        if user.top_role >= interaction.user.top_role and not interaction.user.guild_permissions.administrator:
            await interaction.response.send_message("❌ You cannot ban users with equal or higher roles.", ephemeral=True)
            return
        
        if delete_messages < 0 or delete_messages > 7:
            await interaction.response.send_message("❌ Delete messages days must be between 0 and 7.", ephemeral=True)
            return
        
        await interaction.response.defer(ephemeral=True)
        
        try:
            # Send DM before banning
            try:
                dm_embed = discord.Embed(
                    title="🔨 Banned from Server",
                    description=f"You have been banned from **{interaction.guild.name}**",
                    color=0xff0000
                )
                dm_embed.add_field(name="Reason", value=reason, inline=False)
                dm_embed.add_field(name="Moderator", value=interaction.user.display_name, inline=True)
                
                await user.send(embed=dm_embed)
            except:
                pass
            
            await user.ban(reason=reason, delete_message_days=delete_messages)
            
            # Log the action
            await self.log_action(interaction.guild, "Ban", interaction.user, user, reason)
            
            embed = discord.Embed(
                title="🔨 User Banned",
                color=0xff0000
            )
            embed.add_field(name="User", value=f"{user.mention} ({user.id})", inline=True)
            embed.add_field(name="Reason", value=reason, inline=False)
            if delete_messages > 0:
                embed.add_field(name="Messages Deleted", value=f"Last {delete_messages} days", inline=True)
            
            await interaction.followup.send(embed=embed, ephemeral=True)
            
        except Exception as e:
            logger.error(f"Error banning user: {e}")
            await interaction.followup.send("❌ Error banning user.", ephemeral=True)
    
    def parse_duration(self, duration_str: str) -> Optional[int]:
        """Parse duration string to seconds"""
        try:
            duration_str = duration_str.lower().strip()
            
            if duration_str.endswith('s'):
                return int(duration_str[:-1])
            elif duration_str.endswith('m'):
                return int(duration_str[:-1]) * 60
            elif duration_str.endswith('h'):
                return int(duration_str[:-1]) * 3600
            elif duration_str.endswith('d'):
                return int(duration_str[:-1]) * 86400
            else:
                # Try to parse as just a number (assume minutes)
                return int(duration_str) * 60
                
        except ValueError:
            return None

async def setup(bot):
    await bot.add_cog(ModerationSystem(bot))