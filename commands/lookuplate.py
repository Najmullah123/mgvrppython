import os
import json
import discord
from discord.ext import commands
from discord import app_commands
import logging
from pathlib import Path
from datetime import datetime

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Configuration
DATA_DIR = Path(os.getcwd()) / 'data'
VEHICLES_FILE = DATA_DIR / 'vehicles.json'
GUILD_ID = int(os.getenv('GUILD_ID', '1277047315047120978'))
LAW_ENFORCEMENT_ROLE = os.getenv('LAW_ENFORCEMENT_ROLE', 'Law Enforcement')  # Configurable role name

# Valid US state codes and Canadian province/territory codes
VALID_STATES = {
    # US States
    'AL', 'AK', 'AZ', 'AR', 'CA', 'CO', 'CT', 'DE', 'FL', 'GA', 'HI', 'ID', 'IL',
    'IN', 'IA', 'KS', 'KY', 'LA', 'ME', 'MD', 'MA', 'MI', 'MN', 'MS', 'MO', 'MT',
    'NE', 'NV', 'NH', 'NJ', 'NM', 'NY', 'NC', 'ND', 'OH', 'OK', 'OR', 'PA', 'RI',
    'SC', 'SD', 'TN', 'TX', 'UT', 'VT', 'VA', 'WA', 'WV', 'WI', 'WY',
    # Canadian Provinces/Territories
    'AB', 'BC', 'MB', 'NB', 'NL', 'NS', 'NT', 'NU', 'ON', 'PE', 'QC', 'SK', 'YT'
}

class PaginationView(discord.ui.View):
    def __init__(self, vehicles, per_page=1):
        super().__init__(timeout=60)
        self.vehicles = vehicles
        self.per_page = per_page
        self.page = 0
        self.max_page = (len(vehicles) - 1) // per_page
        self._update_button_states()

    def _update_button_states(self):
        """Enable/disable buttons based on current page."""
        self.previous.disabled = self.page == 0
        self.next.disabled = self.page == self.max_page

    def get_embed(self):
        """Create an embed for the current page."""
        embed = discord.Embed(
            title=f"🚓 Vehicle Lookup Results ({len(self.vehicles)} found)",
            description=f"Page {self.page + 1} of {self.max_page + 1}",
            color=0x3498db,  # GVRP-themed blue
            timestamp=discord.utils.utcnow()
        )
        start = self.page * self.per_page
        end = start + self.per_page
        for vehicle in self.vehicles[start:end]:
            is_test = vehicle['make'].lower() == 'test' or vehicle['model'].lower() == 'test' or vehicle['color'].lower() == 'test'
            embed.add_field(name="Plate", value=vehicle['plate'], inline=True)
            embed.add_field(name="State", value=vehicle['state'], inline=True)
            embed.add_field(
                name="Owner",
                value=f"<@{vehicle['userId']}>" if vehicle.get('userId') else "Unknown",
                inline=True
            )
            embed.add_field(name="Make", value=vehicle.get('make', 'N/A').title(), inline=True)
            embed.add_field(name="Model", value=vehicle.get('model', 'N/A').title(), inline=True)
            embed.add_field(name="Color", value=vehicle.get('color', 'N/A').title(), inline=True)
            embed.add_field(
                name="Registered",
                value=discord.utils.format_dt(datetime.fromisoformat(vehicle['registeredAt'].replace('Z', '+00:00')), 'F'),
                inline=True
            )
            if is_test:
                embed.add_field(
                    name="⚠️ Warning",
                    value="This vehicle has test data and may be invalid for roleplay.",
                    inline=False
                )
        embed.set_footer(text="MGVRP • Vehicle Registry • Use buttons to navigate")
        return embed

    @discord.ui.button(label="Previous", style=discord.ButtonStyle.secondary)
    async def previous(self, interaction: discord.Interaction, button: discord.ui.Button):
        if self.page > 0:
            self.page -= 1
            self._update_button_states()
            await interaction.response.edit_message(embed=self.get_embed(), view=self)

    @discord.ui.button(label="Next", style=discord.ButtonStyle.primary)
    async def next(self, interaction: discord.Interaction, button: discord.ui.Button):
        if self.page < self.max_page:
            self.page += 1
            self._update_button_states()
            await interaction.response.edit_message(embed=self.get_embed(), view=self)

    async def on_timeout(self):
        """Disable buttons after timeout."""
        for item in self.children:
            item.disabled = True
        try:
            await self.message.edit(view=self)
        except discord.HTTPException:
            pass

class LookupPlate(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.vehicle_index = {}
        DATA_DIR.mkdir(exist_ok=True)
        self._build_index()

    def _build_index(self):
        """Build an in-memory index for faster lookups."""
        try:
            if not VEHICLES_FILE.exists():
                logger.warning(f"Vehicle data file not found: {VEHICLES_FILE}. Creating empty file.")
                with VEHICLES_FILE.open('w', encoding='utf-8') as f:
                    json.dump({"vehicles": []}, f, indent=2)
                return
            with VEHICLES_FILE.open('r', encoding='utf-8') as f:
                vehicle_data = json.load(f)
            if not isinstance(vehicle_data, dict) or 'vehicles' not in vehicle_data:
                logger.error("Invalid vehicle data format. Resetting to empty.")
                vehicle_data = {"vehicles": []}
                with VEHICLES_FILE.open('w', encoding='utf-8') as f:
                    json.dump(vehicle_data, f, indent=2)
            for vehicle in vehicle_data.get('vehicles', []):
                key = (vehicle['plate'].upper(), vehicle['state'].upper())
                self.vehicle_index[key] = vehicle
            logger.info(f"Built vehicle index with {len(self.vehicle_index)} entries")
        except json.JSONDecodeError as e:
            logger.error(f"Failed to parse vehicles.json: {e}")
        except Exception as e:
            logger.error(f"Unexpected error building index: {e}")

    def cog_unload(self):
        """Clear index on cog unload."""
        self.vehicle_index.clear()

    @app_commands.command(name="lookuplate", description="Look up vehicles by license plate")
    @app_commands.describe(plate="License plate (2-8 alphanumeric characters or hyphens)", state="State code (e.g., TX, CA), optional")
    @app_commands.guilds(discord.Object(id=GUILD_ID))
    async def lookuplate(self, interaction: discord.Interaction, plate: str, state: str = None):
        await interaction.response.defer(ephemeral=True)

        # Always reload vehicles.json for up-to-date results
        vehicle_index = {}
        try:
            with VEHICLES_FILE.open('r', encoding='utf-8') as f:
                vehicle_data = json.load(f)
            for vehicle in vehicle_data.get('vehicles', []):
                key = (vehicle['plate'].upper(), vehicle['state'].upper())
                vehicle_index[key] = vehicle
        except Exception as e:
            logger.error(f"Error loading vehicles.json: {e}")
            await interaction.followup.send("❌ Could not load vehicle data.", ephemeral=True)
            return

        # Validate inputs
        plate = plate.strip().upper()
        if not (2 <= len(plate) <= 8 and all(c.isalnum() or c == '-' for c in plate)):
            await interaction.followup.send(
                "❌ Invalid plate format. Use 2-8 alphanumeric characters or hyphens.",
                ephemeral=True
            )
            return

        state = state.strip().upper() if state else None
        if state and state not in VALID_STATES:
            await interaction.followup.send(
                f"❌ Invalid state code. Valid codes: {', '.join(sorted(VALID_STATES))}.",
                ephemeral=True
            )
            return

        # Check index
        if state:
            vehicle = vehicle_index.get((plate, state))
            if not vehicle:
                await interaction.followup.send(
                    f"❌ No vehicle found with plate **{plate}** in **{state}**.",
                    ephemeral=True
                )
                return
            vehicles = [vehicle]
        else:
            vehicles = [v for k, v in vehicle_index.items() if k[0] == plate]

        if not vehicles:
            await interaction.followup.send(
                f"❌ No vehicle found with plate **{plate}** in any state.",
                ephemeral=True
            )
            return

        # Always use pagination for results
        view = PaginationView(vehicles, per_page=1)
        message = await interaction.followup.send(embed=view.get_embed(), view=view, ephemeral=True)
        view.message = message

    async def on_error(self, interaction: discord.Interaction, error: app_commands.AppCommandError):
        if isinstance(error, app_commands.CheckFailure):
            await interaction.response.send_message(
                f"❌ You need the **{LAW_ENFORCEMENT_ROLE}** role to use this command.",
                ephemeral=True
            )
        else:
            logger.error(f"Error in lookuplate: {error}")
            await interaction.response.send_message(
                "❌ An unexpected error occurred. Contact the administrator.",
                ephemeral=True
            )

async def setup(bot):
    await bot.add_cog(LookupPlate(bot))