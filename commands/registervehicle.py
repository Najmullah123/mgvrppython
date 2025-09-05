import os
import json
import discord
from discord.ext import commands
from discord import app_commands
from datetime import datetime
from pathlib import Path
import logging

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Configuration
GUILD_ID = int(os.getenv("GUILD_ID", "1277047315047120978"))
VEHICLE_REGISTRY_CHANNEL = int(os.getenv("VEHICLE_REGISTRY_CHANNEL", "1339746547826556938"))
ECONOMY_CHANNEL = int(os.getenv("ECONOMY_CHANNEL", "1403779808135090186"))
DATA_DIR = Path(os.path.dirname(os.path.abspath(__file__))) / ".." / "data"
VEHICLES_FILE = DATA_DIR / "vehicles.json"
STICKY_FILE = DATA_DIR / "sticky.json"

# Valid US state codes
VALID_STATES = {
    "AL", "AK", "AZ", "AR", "CA", "CO", "CT", "DE", "FL", "GA", "HI", "ID", "IL",
    "IN", "IA", "KS", "KY", "LA", "ME", "MD", "MA", "MI", "MN", "MS", "MO", "MT",
    "NE", "NV", "NH", "NJ", "NM", "NY", "NC", "ND", "OH", "OK", "OR", "PA", "RI",
    "SC", "SD", "TN", "TX", "UT", "VT", "VA", "WA", "WV", "WI", "WY"
}

class RegisterVehicle(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.last_sticky_id = None
        DATA_DIR.mkdir(exist_ok=True)
        self._load_sticky_id()

    def _load_sticky_id(self):
        """Load the last sticky message ID from file."""
        try:
            if STICKY_FILE.exists():
                with STICKY_FILE.open("r", encoding="utf-8") as f:
                    data = json.load(f)
                    self.last_sticky_id = data.get("last_sticky_id")
        except (json.JSONDecodeError, Exception) as e:
            logger.error(f"Failed to load sticky ID: {e}")

    def _save_sticky_id(self, sticky_id):
        """Save the sticky message ID to file."""
        try:
            with STICKY_FILE.open("w", encoding="utf-8") as f:
                json.dump({"last_sticky_id": sticky_id}, f, indent=2)
            self.last_sticky_id = sticky_id
        except Exception as e:
            logger.error(f"Failed to save sticky ID: {e}")

    @app_commands.command(name="registervehicle", description="Register your vehicle and send the info to a channel")
    @app_commands.describe(
        make="Vehicle make (e.g., Ford, max 20 chars)",
        model="Vehicle model (e.g., Explorer, max 20 chars)",
        color="Vehicle color (e.g., Blue, max 20 chars)",
        state="Vehicle registration state (e.g., TX)",
        plate="License plate (e.g., ABC123, max 8 chars)"
    )
    @app_commands.guilds(discord.Object(id=GUILD_ID))
    async def registervehicle(self, interaction: discord.Interaction, make: str, model: str, color: str, state: str, plate: str):
        await interaction.response.defer(ephemeral=True)

        # Validate inputs
        make = make.strip()[:20]
        model = model.strip()[:20]
        color = color.strip()[:20]
        state = state.upper().strip()
        plate = plate.upper().strip()

        if not make or not model or not color:
            await interaction.followup.send("❌ Make, model, and color cannot be empty.", ephemeral=True)
            return
        if state not in VALID_STATES:
            await interaction.followup.send(f"❌ Invalid state code. Use one of: {', '.join(sorted(VALID_STATES))}.", ephemeral=True)
            return
        if not (2 <= len(plate) <= 8 and all(c.isalnum() or c == "-" for c in plate)):
            await interaction.followup.send("❌ License plate must be 2–8 characters and contain only letters, numbers, or hyphens.", ephemeral=True)
            return

        # Load or create vehicle data
        try:
            vehicle_data = {"vehicles": []}
            if VEHICLES_FILE.exists():
                with VEHICLES_FILE.open("r", encoding="utf-8") as f:
                    vehicle_data = json.load(f)
                if not isinstance(vehicle_data, dict) or "vehicles" not in vehicle_data:
                    logger.error("Invalid vehicle data format")
                    await interaction.followup.send("❌ Invalid vehicle data format. Contact the administrator.", ephemeral=True)
                    return
        except json.JSONDecodeError as e:
            logger.error(f"Failed to parse vehicles.json: {e}")
            await interaction.followup.send("❌ Error reading vehicle data. Contact the administrator.", ephemeral=True)
            return
        except Exception as e:
            logger.error(f"Unexpected error reading vehicles.json: {e}")
            await interaction.followup.send("❌ An unexpected error occurred. Contact the administrator.", ephemeral=True)
            return

        # Check for duplicate plate in same state
        if any(v["plate"] == plate and v["state"] == state for v in vehicle_data["vehicles"]):
            await interaction.followup.send(f"❌ A vehicle with plate **{plate}** is already registered in **{state}**.", ephemeral=True)
            return

        # Add new vehicle
        vehicle_data["vehicles"].append({
            "userId": str(interaction.user.id),
            "make": make,
            "model": model,
            "color": color,
            "state": state,
            "plate": plate,
            "registeredAt": datetime.utcnow().isoformat()
        })

        # Save vehicle data
        try:
            with VEHICLES_FILE.open("w", encoding="utf-8") as f:
                json.dump(vehicle_data, f, indent=2)
        except Exception as e:
            logger.error(f"Failed to save vehicles.json: {e}")
            await interaction.followup.send("❌ Failed to save vehicle data. Contact the administrator.", ephemeral=True)
            return

        # Create vehicle registration embed
        embed = discord.Embed(
            title="🚗 New Vehicle Registration",
            description=f"**Registered by**: <@{interaction.user.id}>\n**Registered on**: {discord.utils.format_dt(datetime.utcnow(), 'F')}",
            color=0x2ecc71,
            timestamp=discord.utils.utcnow()
        )
        embed.add_field(name="Make", value=make, inline=True)
        embed.add_field(name="Model", value=model, inline=True)
        embed.add_field(name="Color", value=color, inline=True)
        embed.add_field(name="State", value=state, inline=True)
        embed.add_field(name="Plate", value=plate, inline=True)
        embed.set_footer(text="MGVRP • Vehicle Registry", icon_url="https://cdn.discordapp.com/attachments/1393957236891713556/1395111568164913313/5b39ef01ba7ebe82c4789d0436064ac9-removebg-preview.png")

        # Send to registry channel
        channel = interaction.guild.get_channel(VEHICLE_REGISTRY_CHANNEL)
        if not channel or not isinstance(channel, discord.TextChannel):
            logger.error(f"Invalid or inaccessible vehicle registry channel: {VEHICLE_REGISTRY_CHANNEL}")
            await interaction.followup.send("✅ Vehicle registered, but couldn't send to registry channel (invalid or inaccessible).", ephemeral=True)
            return

        # Delete previous sticky message
        if self.last_sticky_id:
            try:
                prev_sticky = await channel.fetch_message(self.last_sticky_id)
                await prev_sticky.delete()
            except discord.HTTPException as e:
                logger.warning(f"Failed to delete previous sticky message: {e}")

        # Send vehicle registration
        try:
            await channel.send(embed=embed)
        except discord.Forbidden:
            logger.error(f"Missing permissions to send to vehicle registry channel: {VEHICLE_REGISTRY_CHANNEL}")
            await interaction.followup.send("✅ Vehicle registered, but couldn't send to registry channel (missing permissions).", ephemeral=True)
            return

        # Send sticky embed
        sticky_embed = discord.Embed(
            title="How to Register Your Vehicle",
            description="Use the `/registervehicle` command with the following information:",
            color=0x808080
        )
        sticky_embed.add_field(name="Make", value="Vehicle manufacturer (e.g., Ford, max 20 chars)", inline=True)
        sticky_embed.add_field(name="Model", value="Vehicle model (e.g., Explorer, max 20 chars)", inline=True)
        sticky_embed.add_field(name="Color", value="Vehicle color (e.g., Blue, max 20 chars)", inline=True)
        sticky_embed.add_field(name="State", value="2-letter state code (e.g., TX, CA)", inline=True)
        sticky_embed.add_field(name="Plate", value="License plate (e.g., ABC123, 2–8 chars)", inline=True)
        sticky_embed.set_footer(text="MGVRP • Vehicle Registry", icon_url="https://cdn.discordapp.com/attachments/1393957236891713556/1395111568164913313/5b39ef01ba7ebe82c4789d0436064ac9-removebg-preview.png")
        try:
            sticky_msg = await channel.send(embed=sticky_embed)
            self._save_sticky_id(sticky_msg.id)
        except discord.Forbidden:
            logger.error(f"Missing permissions to send sticky message to channel: {VEHICLE_REGISTRY_CHANNEL}")
            await interaction.followup.send("✅ Vehicle registered, but couldn't send sticky message (missing permissions).", ephemeral=True)
            return

        # Economy handshake
        economy_channel = interaction.guild.get_channel(ECONOMY_CHANNEL)
        if economy_channel and isinstance(economy_channel, discord.TextChannel):
            try:
                await economy_channel.send(f"Vehicle registration: <@{interaction.user.id}> -500")
                await interaction.followup.send("✅ Your vehicle has been registered! A fee of 500 units has been deducted.", ephemeral=True)
            except discord.Forbidden:
                logger.error(f"Missing permissions to send to economy channel: {ECONOMY_CHANNEL}")
                await interaction.followup.send("✅ Your vehicle has been registered, but the economy update failed (missing permissions).", ephemeral=True)
            except discord.HTTPException as e:
                logger.error(f"Failed to send to economy channel: {e}")
                await interaction.followup.send("✅ Your vehicle has been registered, but the economy update failed.", ephemeral=True)
        else:
            logger.error(f"Invalid or inaccessible economy channel: {ECONOMY_CHANNEL}")
            await interaction.followup.send("✅ Your vehicle has been registered, but the economy channel is invalid.", ephemeral=True)

async def setup(bot):
    await bot.add_cog(RegisterVehicle(bot))