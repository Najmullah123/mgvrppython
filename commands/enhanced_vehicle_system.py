import discord
from discord.ext import commands
from discord import app_commands
import json
import os
from datetime import datetime
from pathlib import Path
import logging
from typing import Optional, List, Dict, Any
import asyncio

logger = logging.getLogger(__name__)

# Configuration
GUILD_ID = int(os.getenv("GUILD_ID", "1277047315047120978"))
VEHICLE_REGISTRY_CHANNEL = int(os.getenv("VEHICLE_REGISTRY_CHANNEL", "1339746547826556938"))
ECONOMY_CHANNEL = int(os.getenv("ECONOMY_CHANNEL", "1403779808135090186"))
DATA_DIR = Path(os.path.dirname(os.path.abspath(__file__))) / ".." / "data"
VEHICLES_FILE = DATA_DIR / "vehicles.json"

# Valid US state codes and Canadian provinces
VALID_STATES = {
    "AL", "AK", "AZ", "AR", "CA", "CO", "CT", "DE", "FL", "GA", "HI", "ID", "IL",
    "IN", "IA", "KS", "KY", "LA", "ME", "MD", "MA", "MI", "MN", "MS", "MO", "MT",
    "NE", "NV", "NH", "NJ", "NM", "NY", "NC", "ND", "OH", "OK", "OR", "PA", "RI",
    "SC", "SD", "TN", "TX", "UT", "VT", "VA", "WA", "WV", "WI", "WY",
    "AB", "BC", "MB", "NB", "NL", "NS", "NT", "NU", "ON", "PE", "QC", "SK", "YT"
}

# Vehicle categories for better organization
VEHICLE_CATEGORIES = {
    "sedan": ["sedan", "car", "civic", "accord", "camry", "corolla", "altima", "fusion"],
    "suv": ["suv", "crossover", "explorer", "tahoe", "suburban", "escalade", "x5", "q7"],
    "truck": ["truck", "pickup", "f150", "silverado", "ram", "tundra", "titan"],
    "sports": ["sports", "coupe", "convertible", "mustang", "camaro", "corvette", "911"],
    "luxury": ["luxury", "mercedes", "bmw", "audi", "lexus", "cadillac", "lincoln"],
    "motorcycle": ["motorcycle", "bike", "harley", "yamaha", "honda", "kawasaki"],
    "commercial": ["commercial", "van", "bus", "semi", "trailer", "delivery"]
}

class VehicleSearchView(discord.ui.View):
    def __init__(self, vehicles: List[Dict], query: str, page: int = 0):
        super().__init__(timeout=300)
        self.vehicles = vehicles
        self.query = query
        self.page = page
        self.per_page = 5
        self.max_page = (len(vehicles) - 1) // self.per_page
        
        self.update_buttons()
    
    def update_buttons(self):
        self.previous_page.disabled = self.page <= 0
        self.next_page.disabled = self.page >= self.max_page
    
    def get_embed(self) -> discord.Embed:
        start_idx = self.page * self.per_page
        end_idx = min(start_idx + self.per_page, len(self.vehicles))
        page_vehicles = self.vehicles[start_idx:end_idx]
        
        embed = discord.Embed(
            title=f"🔍 Vehicle Search Results",
            description=f"Query: **{self.query}**\nFound {len(self.vehicles)} vehicles (Page {self.page + 1}/{self.max_page + 1})",
            color=0x89CFF0,
            timestamp=datetime.utcnow()
        )
        
        for i, vehicle in enumerate(page_vehicles, start=start_idx + 1):
            owner = f"<@{vehicle['userId']}>" if vehicle.get('userId') else "Unknown"
            registered_date = datetime.fromisoformat(vehicle['registeredAt'].replace('Z', '+00:00'))
            
            embed.add_field(
                name=f"{i}. {vehicle['plate']} ({vehicle['state']})",
                value=f"**Owner:** {owner}\n"
                      f"**Vehicle:** {vehicle['make']} {vehicle['model']}\n"
                      f"**Color:** {vehicle['color']}\n"
                      f"**Registered:** {discord.utils.format_dt(registered_date, 'R')}",
                inline=False
            )
        
        embed.set_footer(text="MGVRP • Enhanced Vehicle System")
        return embed
    
    @discord.ui.button(label="◀️ Previous", style=discord.ButtonStyle.secondary)
    async def previous_page(self, interaction: discord.Interaction, button: discord.ui.Button):
        self.page -= 1
        self.update_buttons()
        await interaction.response.edit_message(embed=self.get_embed(), view=self)
    
    @discord.ui.button(label="Next ▶️", style=discord.ButtonStyle.secondary)
    async def next_page(self, interaction: discord.Interaction, button: discord.ui.Button):
        self.page += 1
        self.update_buttons()
        await interaction.response.edit_message(embed=self.get_embed(), view=self)
    
    @discord.ui.button(label="🔄 Refresh", style=discord.ButtonStyle.primary)
    async def refresh(self, interaction: discord.Interaction, button: discord.ui.Button):
        # Reload data and refresh results
        try:
            with VEHICLES_FILE.open("r", encoding="utf-8") as f:
                data = json.load(f)
            
            # Re-run search with current query
            self.vehicles = self.search_vehicles(data.get('vehicles', []), self.query)
            self.max_page = (len(self.vehicles) - 1) // self.per_page if self.vehicles else 0
            self.page = min(self.page, self.max_page)
            self.update_buttons()
            
            await interaction.response.edit_message(embed=self.get_embed(), view=self)
        except Exception as e:
            await interaction.response.send_message("❌ Error refreshing data.", ephemeral=True)
    
    def search_vehicles(self, vehicles: List[Dict], query: str) -> List[Dict]:
        """Enhanced search functionality"""
        query = query.lower()
        results = []
        
        for vehicle in vehicles:
            # Search in multiple fields
            searchable_text = f"{vehicle.get('make', '')} {vehicle.get('model', '')} {vehicle.get('color', '')} {vehicle.get('plate', '')} {vehicle.get('state', '')}".lower()
            
            if query in searchable_text:
                results.append(vehicle)
        
        return results

class VehicleTransferModal(discord.ui.Modal, title="Transfer Vehicle"):
    plate = discord.ui.TextInput(label="License Plate", placeholder="Enter the license plate")
    state = discord.ui.TextInput(label="State", placeholder="Enter the state code")
    new_owner = discord.ui.TextInput(label="New Owner ID", placeholder="Enter the new owner's Discord ID")
    
    async def on_submit(self, interaction: discord.Interaction):
        await interaction.response.defer(ephemeral=True)
        
        try:
            with VEHICLES_FILE.open("r", encoding="utf-8") as f:
                data = json.load(f)
            
            plate_upper = self.plate.value.upper()
            state_upper = self.state.value.upper()
            
            # Find the vehicle
            vehicle_found = False
            for vehicle in data.get('vehicles', []):
                if vehicle['plate'] == plate_upper and vehicle['state'] == state_upper:
                    old_owner = vehicle['userId']
                    vehicle['userId'] = self.new_owner.value
                    vehicle_found = True
                    break
            
            if not vehicle_found:
                await interaction.followup.send(f"❌ Vehicle with plate **{plate_upper}** in **{state_upper}** not found.", ephemeral=True)
                return
            
            # Save the updated data
            with VEHICLES_FILE.open("w", encoding="utf-8") as f:
                json.dump(data, f, indent=2)
            
            embed = discord.Embed(
                title="🔄 Vehicle Transferred",
                description=f"Vehicle **{plate_upper}** ({state_upper}) has been transferred.",
                color=0x00ff00
            )
            embed.add_field(name="From", value=f"<@{old_owner}>", inline=True)
            embed.add_field(name="To", value=f"<@{self.new_owner.value}>", inline=True)
            
            await interaction.followup.send(embed=embed, ephemeral=True)
            
        except Exception as e:
            logger.error(f"Error transferring vehicle: {e}")
            await interaction.followup.send("❌ Error transferring vehicle.", ephemeral=True)

class EnhancedVehicleSystem(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        DATA_DIR.mkdir(exist_ok=True)
    
    @app_commands.command(name="vehicle_search", description="Advanced vehicle search with filters")
    @app_commands.describe(
        query="Search query (make, model, color, plate, or owner)",
        state="Filter by state (optional)",
        owner="Filter by owner (optional)"
    )
    @app_commands.guilds(discord.Object(id=GUILD_ID))
    async def vehicle_search(self, interaction: discord.Interaction, query: str, state: Optional[str] = None, owner: Optional[discord.User] = None):
        await interaction.response.defer(ephemeral=True)
        
        try:
            with VEHICLES_FILE.open("r", encoding="utf-8") as f:
                data = json.load(f)
        except Exception as e:
            await interaction.followup.send("❌ Error loading vehicle database.", ephemeral=True)
            return
        
        vehicles = data.get('vehicles', [])
        
        # Apply filters
        if state:
            vehicles = [v for v in vehicles if v.get('state', '').upper() == state.upper()]
        
        if owner:
            vehicles = [v for v in vehicles if v.get('userId') == str(owner.id)]
        
        # Apply search query
        if query:
            query_lower = query.lower()
            filtered_vehicles = []
            for vehicle in vehicles:
                searchable = f"{vehicle.get('make', '')} {vehicle.get('model', '')} {vehicle.get('color', '')} {vehicle.get('plate', '')}".lower()
                if query_lower in searchable:
                    filtered_vehicles.append(vehicle)
            vehicles = filtered_vehicles
        
        if not vehicles:
            await interaction.followup.send("❌ No vehicles found matching your criteria.", ephemeral=True)
            return
        
        view = VehicleSearchView(vehicles, query)
        await interaction.followup.send(embed=view.get_embed(), view=view, ephemeral=True)
    
    @app_commands.command(name="vehicle_stats", description="Get comprehensive vehicle statistics")
    @app_commands.guilds(discord.Object(id=GUILD_ID))
    async def vehicle_stats(self, interaction: discord.Interaction):
        await interaction.response.defer(ephemeral=True)
        
        try:
            with VEHICLES_FILE.open("r", encoding="utf-8") as f:
                data = json.load(f)
        except Exception as e:
            await interaction.followup.send("❌ Error loading vehicle database.", ephemeral=True)
            return
        
        vehicles = data.get('vehicles', [])
        
        if not vehicles:
            await interaction.followup.send("❌ No vehicles in database.", ephemeral=True)
            return
        
        # Calculate statistics
        total_vehicles = len(vehicles)
        
        # State distribution
        state_counts = {}
        for vehicle in vehicles:
            state = vehicle.get('state', 'Unknown')
            state_counts[state] = state_counts.get(state, 0) + 1
        
        top_states = sorted(state_counts.items(), key=lambda x: x[1], reverse=True)[:5]
        
        # Make distribution
        make_counts = {}
        for vehicle in vehicles:
            make = vehicle.get('make', 'Unknown').title()
            make_counts[make] = make_counts.get(make, 0) + 1
        
        top_makes = sorted(make_counts.items(), key=lambda x: x[1], reverse=True)[:5]
        
        # Color distribution
        color_counts = {}
        for vehicle in vehicles:
            color = vehicle.get('color', 'Unknown').title()
            color_counts[color] = color_counts.get(color, 0) + 1
        
        top_colors = sorted(color_counts.items(), key=lambda x: x[1], reverse=True)[:5]
        
        # Recent registrations (last 7 days)
        from datetime import timedelta
        week_ago = datetime.utcnow() - timedelta(days=7)
        recent_vehicles = 0
        
        for vehicle in vehicles:
            try:
                reg_date = datetime.fromisoformat(vehicle['registeredAt'].replace('Z', '+00:00'))
                if reg_date >= week_ago:
                    recent_vehicles += 1
            except:
                continue
        
        embed = discord.Embed(
            title="📊 Vehicle Database Statistics",
            color=0x89CFF0,
            timestamp=datetime.utcnow()
        )
        
        embed.add_field(name="📈 Overview", value=f"Total Vehicles: **{total_vehicles}**\nRecent (7 days): **{recent_vehicles}**", inline=False)
        
        embed.add_field(
            name="🗺️ Top States",
            value="\n".join([f"{state}: {count}" for state, count in top_states]),
            inline=True
        )
        
        embed.add_field(
            name="🚗 Top Makes",
            value="\n".join([f"{make}: {count}" for make, count in top_makes]),
            inline=True
        )
        
        embed.add_field(
            name="🎨 Top Colors",
            value="\n".join([f"{color}: {count}" for color, count in top_colors]),
            inline=True
        )
        
        embed.set_footer(text="MGVRP • Enhanced Vehicle System")
        
        await interaction.followup.send(embed=embed, ephemeral=True)
    
    @app_commands.command(name="transfer_vehicle", description="Transfer vehicle ownership (Admin only)")
    @app_commands.guilds(discord.Object(id=GUILD_ID))
    async def transfer_vehicle(self, interaction: discord.Interaction):
        # Check if user has admin permissions
        if not (interaction.user.guild_permissions.administrator or 
                any(role.id == 1400212028353810572 for role in interaction.user.roles)):
            await interaction.response.send_message("❌ You don't have permission to transfer vehicles.", ephemeral=True)
            return
        
        modal = VehicleTransferModal()
        await interaction.response.send_modal(modal)
    
    @app_commands.command(name="my_vehicles", description="View all your registered vehicles")
    @app_commands.guilds(discord.Object(id=GUILD_ID))
    async def my_vehicles(self, interaction: discord.Interaction):
        await interaction.response.defer(ephemeral=True)
        
        try:
            with VEHICLES_FILE.open("r", encoding="utf-8") as f:
                data = json.load(f)
        except Exception as e:
            await interaction.followup.send("❌ Error loading vehicle database.", ephemeral=True)
            return
        
        user_vehicles = [v for v in data.get('vehicles', []) if v.get('userId') == str(interaction.user.id)]
        
        if not user_vehicles:
            await interaction.followup.send("❌ You don't have any registered vehicles.", ephemeral=True)
            return
        
        embed = discord.Embed(
            title=f"🚗 Your Vehicles ({len(user_vehicles)})",
            color=0x89CFF0,
            timestamp=datetime.utcnow()
        )
        
        for i, vehicle in enumerate(user_vehicles[:10], 1):  # Limit to 10 for display
            reg_date = datetime.fromisoformat(vehicle['registeredAt'].replace('Z', '+00:00'))
            embed.add_field(
                name=f"{i}. {vehicle['plate']} ({vehicle['state']})",
                value=f"**{vehicle['make']} {vehicle['model']}**\nColor: {vehicle['color']}\nRegistered: {discord.utils.format_dt(reg_date, 'R')}",
                inline=True
            )
        
        if len(user_vehicles) > 10:
            embed.add_field(
                name="📝 Note",
                value=f"Showing first 10 vehicles. You have {len(user_vehicles) - 10} more.",
                inline=False
            )
        
        embed.set_footer(text="MGVRP • Enhanced Vehicle System")
        
        await interaction.followup.send(embed=embed, ephemeral=True)

async def setup(bot):
    await bot.add_cog(EnhancedVehicleSystem(bot))