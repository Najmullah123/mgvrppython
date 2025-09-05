import discord
from discord.ext import commands
from discord import app_commands
import json
import os
from datetime import datetime, timedelta
from pathlib import Path
import logging
from typing import Optional, List, Dict
import asyncio

logger = logging.getLogger(__name__)

GUILD_ID = int(os.getenv("GUILD_ID", "1277047315047120978"))
DATA_DIR = Path(os.path.dirname(os.path.abspath(__file__))) / ".." / "data"
SESSIONS_FILE = DATA_DIR / "sessions.json"

class SessionManagementView(discord.ui.View):
    def __init__(self, session_data: Dict):
        super().__init__(timeout=None)
        self.session_data = session_data
    
    @discord.ui.button(label="Join Session", style=discord.ButtonStyle.success, emoji="🎮")
    async def join_session(self, interaction: discord.Interaction, button: discord.ui.Button):
        # Add user to session participants
        user_id = str(interaction.user.id)
        
        if user_id not in self.session_data.get("participants", []):
            self.session_data.setdefault("participants", []).append(user_id)
            
            # Update session data
            try:
                with SESSIONS_FILE.open("r", encoding="utf-8") as f:
                    data = json.load(f)
                
                # Find and update the session
                for session in data.get("sessions", []):
                    if session["id"] == self.session_data["id"]:
                        session["participants"] = self.session_data["participants"]
                        break
                
                with SESSIONS_FILE.open("w", encoding="utf-8") as f:
                    json.dump(data, f, indent=2)
                
                await interaction.response.send_message("✅ You've joined the session!", ephemeral=True)
            except Exception as e:
                logger.error(f"Error updating session participants: {e}")
                await interaction.response.send_message("❌ Error joining session.", ephemeral=True)
        else:
            await interaction.response.send_message("❌ You're already in this session!", ephemeral=True)
    
    @discord.ui.button(label="Leave Session", style=discord.ButtonStyle.danger, emoji="🚪")
    async def leave_session(self, interaction: discord.Interaction, button: discord.ui.Button):
        user_id = str(interaction.user.id)
        
        if user_id in self.session_data.get("participants", []):
            self.session_data["participants"].remove(user_id)
            
            # Update session data
            try:
                with SESSIONS_FILE.open("r", encoding="utf-8") as f:
                    data = json.load(f)
                
                # Find and update the session
                for session in data.get("sessions", []):
                    if session["id"] == self.session_data["id"]:
                        session["participants"] = self.session_data["participants"]
                        break
                
                with SESSIONS_FILE.open("w", encoding="utf-8") as f:
                    json.dump(data, f, indent=2)
                
                await interaction.response.send_message("✅ You've left the session.", ephemeral=True)
            except Exception as e:
                logger.error(f"Error updating session participants: {e}")
                await interaction.response.send_message("❌ Error leaving session.", ephemeral=True)
        else:
            await interaction.response.send_message("❌ You're not in this session!", ephemeral=True)
    
    @discord.ui.button(label="Session Info", style=discord.ButtonStyle.primary, emoji="ℹ️")
    async def session_info(self, interaction: discord.Interaction, button: discord.ui.Button):
        embed = discord.Embed(
            title=f"📋 Session Information",
            color=0x89CFF0,
            timestamp=datetime.utcnow()
        )
        
        host = interaction.guild.get_member(int(self.session_data["host_id"]))
        embed.add_field(name="Host", value=host.mention if host else "Unknown", inline=True)
        
        if self.session_data.get("cohost_id"):
            cohost = interaction.guild.get_member(int(self.session_data["cohost_id"]))
            embed.add_field(name="Co-Host", value=cohost.mention if cohost else "Unknown", inline=True)
        
        embed.add_field(name="Status", value=self.session_data.get("status", "Unknown"), inline=True)
        embed.add_field(name="Priority", value=self.session_data.get("priority", "Unknown"), inline=True)
        embed.add_field(name="FRP Speed", value=f"{self.session_data.get('frp_speed', 'Unknown')} MPH", inline=True)
        embed.add_field(name="House Claiming", value=self.session_data.get("house_claiming", "Unknown"), inline=True)
        
        participants_count = len(self.session_data.get("participants", []))
        embed.add_field(name="Participants", value=f"{participants_count} players", inline=True)
        
        if self.session_data.get("session_link"):
            embed.add_field(name="Session Link", value=f"[Join Game]({self.session_data['session_link']})", inline=False)
        
        created_at = datetime.fromisoformat(self.session_data["created_at"])
        embed.add_field(name="Created", value=discord.utils.format_dt(created_at, 'R'), inline=True)
        
        embed.set_footer(text="MGVRP Session Management")
        
        await interaction.response.send_message(embed=embed, ephemeral=True)

class EnhancedSessionManagement(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        DATA_DIR.mkdir(exist_ok=True)
        self.ensure_sessions_file()
    
    def ensure_sessions_file(self):
        """Ensure sessions data file exists"""
        if not SESSIONS_FILE.exists():
            with SESSIONS_FILE.open("w", encoding="utf-8") as f:
                json.dump({"sessions": []}, f, indent=2)
    
    def is_staff(self, user: discord.Member) -> bool:
        """Check if user has staff permissions"""
        staff_roles = [1400212028353810572]  # Add more staff role IDs
        return (user.guild_permissions.administrator or 
                any(role.id in staff_roles for role in user.roles))
    
    @app_commands.command(name="create_session", description="Create a new roleplay session")
    @app_commands.describe(
        priority="Priority status",
        frp_speed="FRP speed limit in MPH",
        house_claiming="Allow house claiming?",
        session_link="Roblox session link",
        cohost="Session co-host (optional)"
    )
    @app_commands.guilds(discord.Object(id=GUILD_ID))
    async def create_session(
        self, 
        interaction: discord.Interaction, 
        priority: str, 
        frp_speed: int, 
        house_claiming: bool, 
        session_link: str,
        cohost: Optional[discord.Member] = None
    ):
        if not self.is_staff(interaction.user):
            await interaction.response.send_message("❌ You don't have permission to create sessions.", ephemeral=True)
            return
        
        await interaction.response.defer(ephemeral=True)
        
        try:
            # Load existing sessions
            with SESSIONS_FILE.open("r", encoding="utf-8") as f:
                data = json.load(f)
            
            # Create new session
            session_id = len(data["sessions"]) + 1
            session_data = {
                "id": session_id,
                "host_id": str(interaction.user.id),
                "cohost_id": str(cohost.id) if cohost else None,
                "priority": priority,
                "frp_speed": frp_speed,
                "house_claiming": "Yes" if house_claiming else "No",
                "session_link": session_link,
                "status": "Setting Up",
                "participants": [],
                "created_at": datetime.utcnow().isoformat(),
                "ended_at": None
            }
            
            data["sessions"].append(session_data)
            
            # Save sessions data
            with SESSIONS_FILE.open("w", encoding="utf-8") as f:
                json.dump(data, f, indent=2)
            
            # Create session embed
            embed = discord.Embed(
                title="🎮 New Session Created",
                description=f"Session #{session_id} has been created!",
                color=0x00ff00,
                timestamp=datetime.utcnow()
            )
            
            embed.add_field(name="Host", value=interaction.user.mention, inline=True)
            if cohost:
                embed.add_field(name="Co-Host", value=cohost.mention, inline=True)
            embed.add_field(name="Priority", value=priority, inline=True)
            embed.add_field(name="FRP Speed", value=f"{frp_speed} MPH", inline=True)
            embed.add_field(name="House Claiming", value="Yes" if house_claiming else "No", inline=True)
            embed.add_field(name="Status", value="Setting Up", inline=True)
            
            view = SessionManagementView(session_data)
            
            await interaction.followup.send(embed=embed, view=view, ephemeral=True)
            
            # Also send to public channel
            public_embed = discord.Embed(
                title="🎮 New Roleplay Session",
                description=f"{interaction.user.mention} is setting up a new session!",
                color=0x89CFF0
            )
            
            public_embed.add_field(name="Priority", value=priority, inline=True)
            public_embed.add_field(name="FRP Speed", value=f"{frp_speed} MPH", inline=True)
            public_embed.add_field(name="House Claiming", value="Yes" if house_claiming else "No", inline=True)
            
            public_view = SessionManagementView(session_data)
            await interaction.channel.send(embed=public_embed, view=public_view)
            
        except Exception as e:
            logger.error(f"Error creating session: {e}")
            await interaction.followup.send("❌ Error creating session.", ephemeral=True)
    
    @app_commands.command(name="update_session", description="Update session status")
    @app_commands.describe(
        session_id="Session ID to update",
        status="New session status"
    )
    @app_commands.choices(status=[
        app_commands.Choice(name="Setting Up", value="Setting Up"),
        app_commands.Choice(name="Early Access", value="Early Access"),
        app_commands.Choice(name="Public", value="Public"),
        app_commands.Choice(name="Ended", value="Ended")
    ])
    @app_commands.guilds(discord.Object(id=GUILD_ID))
    async def update_session(self, interaction: discord.Interaction, session_id: int, status: app_commands.Choice[str]):
        if not self.is_staff(interaction.user):
            await interaction.response.send_message("❌ You don't have permission to update sessions.", ephemeral=True)
            return
        
        await interaction.response.defer(ephemeral=True)
        
        try:
            with SESSIONS_FILE.open("r", encoding="utf-8") as f:
                data = json.load(f)
            
            # Find and update session
            session_found = False
            for session in data["sessions"]:
                if session["id"] == session_id:
                    # Check if user is host or has admin permissions
                    if (session["host_id"] != str(interaction.user.id) and 
                        not interaction.user.guild_permissions.administrator):
                        await interaction.followup.send("❌ You can only update your own sessions.", ephemeral=True)
                        return
                    
                    session["status"] = status.value
                    if status.value == "Ended":
                        session["ended_at"] = datetime.utcnow().isoformat()
                    
                    session_found = True
                    break
            
            if not session_found:
                await interaction.followup.send("❌ Session not found.", ephemeral=True)
                return
            
            # Save updated data
            with SESSIONS_FILE.open("w", encoding="utf-8") as f:
                json.dump(data, f, indent=2)
            
            embed = discord.Embed(
                title="✅ Session Updated",
                description=f"Session #{session_id} status updated to **{status.value}**",
                color=0x00ff00
            )
            
            await interaction.followup.send(embed=embed, ephemeral=True)
            
        except Exception as e:
            logger.error(f"Error updating session: {e}")
            await interaction.followup.send("❌ Error updating session.", ephemeral=True)
    
    @app_commands.command(name="active_sessions", description="View all active sessions")
    @app_commands.guilds(discord.Object(id=GUILD_ID))
    async def active_sessions(self, interaction: discord.Interaction):
        await interaction.response.defer(ephemeral=True)
        
        try:
            with SESSIONS_FILE.open("r", encoding="utf-8") as f:
                data = json.load(f)
            
            active_sessions = [s for s in data["sessions"] if s["status"] != "Ended"]
            
            if not active_sessions:
                await interaction.followup.send("❌ No active sessions found.", ephemeral=True)
                return
            
            embed = discord.Embed(
                title="🎮 Active Sessions",
                description=f"Found {len(active_sessions)} active session(s)",
                color=0x89CFF0,
                timestamp=datetime.utcnow()
            )
            
            for session in active_sessions[-5:]:  # Show last 5 sessions
                host = interaction.guild.get_member(int(session["host_id"]))
                host_name = host.display_name if host else "Unknown"
                
                participants_count = len(session.get("participants", []))
                created_at = datetime.fromisoformat(session["created_at"])
                
                embed.add_field(
                    name=f"Session #{session['id']} - {session['status']}",
                    value=f"**Host:** {host_name}\n"
                          f"**Priority:** {session['priority']}\n"
                          f"**Participants:** {participants_count}\n"
                          f"**Created:** {discord.utils.format_dt(created_at, 'R')}",
                    inline=True
                )
            
            embed.set_footer(text="MGVRP Session Management")
            
            await interaction.followup.send(embed=embed, ephemeral=True)
            
        except Exception as e:
            logger.error(f"Error getting active sessions: {e}")
            await interaction.followup.send("❌ Error retrieving sessions.", ephemeral=True)
    
    @app_commands.command(name="session_stats", description="View session statistics")
    @app_commands.guilds(discord.Object(id=GUILD_ID))
    async def session_stats(self, interaction: discord.Interaction):
        if not self.is_staff(interaction.user):
            await interaction.response.send_message("❌ You don't have permission to view session statistics.", ephemeral=True)
            return
        
        await interaction.response.defer(ephemeral=True)
        
        try:
            with SESSIONS_FILE.open("r", encoding="utf-8") as f:
                data = json.load(f)
            
            sessions = data.get("sessions", [])
            
            if not sessions:
                await interaction.followup.send("❌ No session data found.", ephemeral=True)
                return
            
            # Calculate statistics
            total_sessions = len(sessions)
            active_sessions = len([s for s in sessions if s["status"] != "Ended"])
            ended_sessions = len([s for s in sessions if s["status"] == "Ended"])
            
            # Host statistics
            host_counts = {}
            for session in sessions:
                host_id = session["host_id"]
                host_counts[host_id] = host_counts.get(host_id, 0) + 1
            
            top_hosts = sorted(host_counts.items(), key=lambda x: x[1], reverse=True)[:5]
            
            # Recent activity (last 7 days)
            week_ago = datetime.utcnow() - timedelta(days=7)
            recent_sessions = 0
            
            for session in sessions:
                created_at = datetime.fromisoformat(session["created_at"])
                if created_at >= week_ago:
                    recent_sessions += 1
            
            embed = discord.Embed(
                title="📊 Session Statistics",
                color=0x89CFF0,
                timestamp=datetime.utcnow()
            )
            
            embed.add_field(name="📈 Overview", 
                          value=f"Total Sessions: **{total_sessions}**\n"
                                f"Active: **{active_sessions}**\n"
                                f"Ended: **{ended_sessions}**\n"
                                f"Recent (7 days): **{recent_sessions}**", 
                          inline=True)
            
            # Top hosts
            if top_hosts:
                host_list = []
                for host_id, count in top_hosts:
                    host = interaction.guild.get_member(int(host_id))
                    host_name = host.display_name if host else "Unknown"
                    host_list.append(f"{host_name}: {count}")
                
                embed.add_field(name="🏆 Top Hosts", value="\n".join(host_list), inline=True)
            
            embed.set_footer(text="MGVRP Session Management")
            
            await interaction.followup.send(embed=embed, ephemeral=True)
            
        except Exception as e:
            logger.error(f"Error generating session stats: {e}")
            await interaction.followup.send("❌ Error generating statistics.", ephemeral=True)

async def setup(bot):
    await bot.add_cog(EnhancedSessionManagement(bot))