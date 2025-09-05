import discord
from discord.ext import commands
from discord import app_commands
import json
import os
from datetime import datetime, timedelta
from pathlib import Path
import logging
import random
from typing import Optional, Dict, Any
import asyncio

logger = logging.getLogger(__name__)

GUILD_ID = int(os.getenv("GUILD_ID", "1277047315047120978"))
DATA_DIR = Path(os.path.dirname(os.path.abspath(__file__))) / ".." / "data"
ECONOMY_FILE = DATA_DIR / "economy.json"

# Economy settings
DAILY_REWARD = 1000
WEEKLY_REWARD = 5000
WORK_COOLDOWN = 3600  # 1 hour in seconds
WORK_REWARDS = {
    "min": 100,
    "max": 500
}

JOBS = [
    "delivered packages for UPS",
    "worked as a taxi driver",
    "completed a construction job",
    "worked at the local diner",
    "did some freelance coding",
    "worked as a security guard",
    "completed a delivery route",
    "worked at the gas station",
    "did some landscaping work",
    "worked as a mechanic"
]

class EconomySystem(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        DATA_DIR.mkdir(exist_ok=True)
        self.ensure_economy_file()
    
    def ensure_economy_file(self):
        """Ensure economy data file exists"""
        if not ECONOMY_FILE.exists():
            with ECONOMY_FILE.open("w", encoding="utf-8") as f:
                json.dump({"users": {}}, f, indent=2)
    
    def get_user_data(self, user_id: str) -> Dict[str, Any]:
        """Get user's economy data"""
        try:
            with ECONOMY_FILE.open("r", encoding="utf-8") as f:
                data = json.load(f)
            
            if user_id not in data["users"]:
                data["users"][user_id] = {
                    "balance": 0,
                    "bank": 0,
                    "last_daily": None,
                    "last_weekly": None,
                    "last_work": None,
                    "total_earned": 0,
                    "total_spent": 0
                }
                
                with ECONOMY_FILE.open("w", encoding="utf-8") as f:
                    json.dump(data, f, indent=2)
            
            return data["users"][user_id]
            
        except Exception as e:
            logger.error(f"Error getting user data: {e}")
            return {
                "balance": 0,
                "bank": 0,
                "last_daily": None,
                "last_weekly": None,
                "last_work": None,
                "total_earned": 0,
                "total_spent": 0
            }
    
    def update_user_data(self, user_id: str, user_data: Dict[str, Any]):
        """Update user's economy data"""
        try:
            with ECONOMY_FILE.open("r", encoding="utf-8") as f:
                data = json.load(f)
            
            data["users"][user_id] = user_data
            
            with ECONOMY_FILE.open("w", encoding="utf-8") as f:
                json.dump(data, f, indent=2)
                
        except Exception as e:
            logger.error(f"Error updating user data: {e}")
    
    def add_money(self, user_id: str, amount: int, to_bank: bool = False):
        """Add money to user's balance or bank"""
        user_data = self.get_user_data(user_id)
        
        if to_bank:
            user_data["bank"] += amount
        else:
            user_data["balance"] += amount
        
        user_data["total_earned"] += amount
        self.update_user_data(user_id, user_data)
    
    def remove_money(self, user_id: str, amount: int, from_bank: bool = False) -> bool:
        """Remove money from user's balance or bank. Returns True if successful."""
        user_data = self.get_user_data(user_id)
        
        if from_bank:
            if user_data["bank"] < amount:
                return False
            user_data["bank"] -= amount
        else:
            if user_data["balance"] < amount:
                return False
            user_data["balance"] -= amount
        
        user_data["total_spent"] += amount
        self.update_user_data(user_id, user_data)
        return True
    
    @app_commands.command(name="balance", description="Check your balance or someone else's")
    @app_commands.describe(user="User to check balance for (optional)")
    @app_commands.guilds(discord.Object(id=GUILD_ID))
    async def balance(self, interaction: discord.Interaction, user: Optional[discord.Member] = None):
        target_user = user or interaction.user
        user_data = self.get_user_data(str(target_user.id))
        
        total_money = user_data["balance"] + user_data["bank"]
        
        embed = discord.Embed(
            title=f"💰 {target_user.display_name}'s Balance",
            color=0x00ff00,
            timestamp=datetime.utcnow()
        )
        
        embed.add_field(name="💵 Wallet", value=f"${user_data['balance']:,}", inline=True)
        embed.add_field(name="🏦 Bank", value=f"${user_data['bank']:,}", inline=True)
        embed.add_field(name="💎 Total", value=f"${total_money:,}", inline=True)
        
        if target_user == interaction.user:
            embed.add_field(name="📈 Total Earned", value=f"${user_data['total_earned']:,}", inline=True)
            embed.add_field(name="📉 Total Spent", value=f"${user_data['total_spent']:,}", inline=True)
        
        embed.set_thumbnail(url=target_user.avatar.url if target_user.avatar else target_user.default_avatar.url)
        embed.set_footer(text="MGVRP Economy System")
        
        await interaction.response.send_message(embed=embed, ephemeral=True)
    
    @app_commands.command(name="daily", description="Claim your daily reward")
    @app_commands.guilds(discord.Object(id=GUILD_ID))
    async def daily(self, interaction: discord.Interaction):
        user_data = self.get_user_data(str(interaction.user.id))
        
        now = datetime.utcnow()
        
        if user_data["last_daily"]:
            last_daily = datetime.fromisoformat(user_data["last_daily"])
            if now - last_daily < timedelta(days=1):
                next_daily = last_daily + timedelta(days=1)
                await interaction.response.send_message(
                    f"❌ You've already claimed your daily reward! Next daily available {discord.utils.format_dt(next_daily, 'R')}",
                    ephemeral=True
                )
                return
        
        # Calculate streak bonus
        streak_bonus = 0
        if user_data["last_daily"]:
            last_daily = datetime.fromisoformat(user_data["last_daily"])
            if now - last_daily <= timedelta(days=2):  # Allow 1 day grace period
                streak_bonus = min(500, 50 * (user_data.get("daily_streak", 0)))
        
        total_reward = DAILY_REWARD + streak_bonus
        
        user_data["balance"] += total_reward
        user_data["total_earned"] += total_reward
        user_data["last_daily"] = now.isoformat()
        user_data["daily_streak"] = user_data.get("daily_streak", 0) + 1
        
        self.update_user_data(str(interaction.user.id), user_data)
        
        embed = discord.Embed(
            title="🎁 Daily Reward Claimed!",
            description=f"You received **${total_reward:,}**!",
            color=0x00ff00
        )
        
        embed.add_field(name="Base Reward", value=f"${DAILY_REWARD:,}", inline=True)
        if streak_bonus > 0:
            embed.add_field(name="Streak Bonus", value=f"${streak_bonus:,}", inline=True)
            embed.add_field(name="Current Streak", value=f"{user_data['daily_streak']} days", inline=True)
        
        embed.add_field(name="New Balance", value=f"${user_data['balance']:,}", inline=False)
        embed.set_footer(text="Come back tomorrow for another reward!")
        
        await interaction.response.send_message(embed=embed, ephemeral=True)
    
    @app_commands.command(name="weekly", description="Claim your weekly reward")
    @app_commands.guilds(discord.Object(id=GUILD_ID))
    async def weekly(self, interaction: discord.Interaction):
        user_data = self.get_user_data(str(interaction.user.id))
        
        now = datetime.utcnow()
        
        if user_data["last_weekly"]:
            last_weekly = datetime.fromisoformat(user_data["last_weekly"])
            if now - last_weekly < timedelta(days=7):
                next_weekly = last_weekly + timedelta(days=7)
                await interaction.response.send_message(
                    f"❌ You've already claimed your weekly reward! Next weekly available {discord.utils.format_dt(next_weekly, 'R')}",
                    ephemeral=True
                )
                return
        
        user_data["balance"] += WEEKLY_REWARD
        user_data["total_earned"] += WEEKLY_REWARD
        user_data["last_weekly"] = now.isoformat()
        
        self.update_user_data(str(interaction.user.id), user_data)
        
        embed = discord.Embed(
            title="🎊 Weekly Reward Claimed!",
            description=f"You received **${WEEKLY_REWARD:,}**!",
            color=0x00ff00
        )
        
        embed.add_field(name="New Balance", value=f"${user_data['balance']:,}", inline=True)
        embed.set_footer(text="Come back next week for another reward!")
        
        await interaction.response.send_message(embed=embed, ephemeral=True)
    
    @app_commands.command(name="work", description="Work to earn money")
    @app_commands.guilds(discord.Object(id=GUILD_ID))
    async def work(self, interaction: discord.Interaction):
        user_data = self.get_user_data(str(interaction.user.id))
        
        now = datetime.utcnow()
        
        if user_data["last_work"]:
            last_work = datetime.fromisoformat(user_data["last_work"])
            if now - last_work < timedelta(seconds=WORK_COOLDOWN):
                next_work = last_work + timedelta(seconds=WORK_COOLDOWN)
                await interaction.response.send_message(
                    f"❌ You're tired from your last job! You can work again {discord.utils.format_dt(next_work, 'R')}",
                    ephemeral=True
                )
                return
        
        # Calculate earnings
        base_earnings = random.randint(WORK_REWARDS["min"], WORK_REWARDS["max"])
        
        # Bonus for vehicle owners (check if user has registered vehicles)
        vehicle_bonus = 0
        try:
            vehicles_file = DATA_DIR / "vehicles.json"
            if vehicles_file.exists():
                with vehicles_file.open("r", encoding="utf-8") as f:
                    vehicle_data = json.load(f)
                
                user_vehicles = [v for v in vehicle_data.get("vehicles", []) if v.get("userId") == str(interaction.user.id)]
                if user_vehicles:
                    vehicle_bonus = min(100, len(user_vehicles) * 25)  # $25 per vehicle, max $100
        except:
            pass
        
        total_earnings = base_earnings + vehicle_bonus
        job = random.choice(JOBS)
        
        user_data["balance"] += total_earnings
        user_data["total_earned"] += total_earnings
        user_data["last_work"] = now.isoformat()
        
        self.update_user_data(str(interaction.user.id), user_data)
        
        embed = discord.Embed(
            title="💼 Work Complete!",
            description=f"You {job} and earned **${total_earnings:,}**!",
            color=0x00ff00
        )
        
        embed.add_field(name="Base Pay", value=f"${base_earnings:,}", inline=True)
        if vehicle_bonus > 0:
            embed.add_field(name="Vehicle Bonus", value=f"${vehicle_bonus:,}", inline=True)
        embed.add_field(name="New Balance", value=f"${user_data['balance']:,}", inline=True)
        
        embed.set_footer(text=f"You can work again in {WORK_COOLDOWN//60} minutes!")
        
        await interaction.response.send_message(embed=embed, ephemeral=True)
    
    @app_commands.command(name="deposit", description="Deposit money to your bank")
    @app_commands.describe(amount="Amount to deposit (or 'all' for everything)")
    @app_commands.guilds(discord.Object(id=GUILD_ID))
    async def deposit(self, interaction: discord.Interaction, amount: str):
        user_data = self.get_user_data(str(interaction.user.id))
        
        if amount.lower() == "all":
            deposit_amount = user_data["balance"]
        else:
            try:
                deposit_amount = int(amount.replace(",", ""))
            except ValueError:
                await interaction.response.send_message("❌ Invalid amount. Use a number or 'all'.", ephemeral=True)
                return
        
        if deposit_amount <= 0:
            await interaction.response.send_message("❌ Amount must be positive.", ephemeral=True)
            return
        
        if user_data["balance"] < deposit_amount:
            await interaction.response.send_message("❌ You don't have enough money in your wallet.", ephemeral=True)
            return
        
        user_data["balance"] -= deposit_amount
        user_data["bank"] += deposit_amount
        
        self.update_user_data(str(interaction.user.id), user_data)
        
        embed = discord.Embed(
            title="🏦 Deposit Successful",
            description=f"Deposited **${deposit_amount:,}** to your bank account.",
            color=0x00ff00
        )
        
        embed.add_field(name="💵 Wallet", value=f"${user_data['balance']:,}", inline=True)
        embed.add_field(name="🏦 Bank", value=f"${user_data['bank']:,}", inline=True)
        
        await interaction.response.send_message(embed=embed, ephemeral=True)
    
    @app_commands.command(name="withdraw", description="Withdraw money from your bank")
    @app_commands.describe(amount="Amount to withdraw (or 'all' for everything)")
    @app_commands.guilds(discord.Object(id=GUILD_ID))
    async def withdraw(self, interaction: discord.Interaction, amount: str):
        user_data = self.get_user_data(str(interaction.user.id))
        
        if amount.lower() == "all":
            withdraw_amount = user_data["bank"]
        else:
            try:
                withdraw_amount = int(amount.replace(",", ""))
            except ValueError:
                await interaction.response.send_message("❌ Invalid amount. Use a number or 'all'.", ephemeral=True)
                return
        
        if withdraw_amount <= 0:
            await interaction.response.send_message("❌ Amount must be positive.", ephemeral=True)
            return
        
        if user_data["bank"] < withdraw_amount:
            await interaction.response.send_message("❌ You don't have enough money in your bank.", ephemeral=True)
            return
        
        user_data["bank"] -= withdraw_amount
        user_data["balance"] += withdraw_amount
        
        self.update_user_data(str(interaction.user.id), user_data)
        
        embed = discord.Embed(
            title="🏦 Withdrawal Successful",
            description=f"Withdrew **${withdraw_amount:,}** from your bank account.",
            color=0x00ff00
        )
        
        embed.add_field(name="💵 Wallet", value=f"${user_data['balance']:,}", inline=True)
        embed.add_field(name="🏦 Bank", value=f"${user_data['bank']:,}", inline=True)
        
        await interaction.response.send_message(embed=embed, ephemeral=True)
    
    @app_commands.command(name="pay", description="Pay money to another user")
    @app_commands.describe(user="User to pay", amount="Amount to pay")
    @app_commands.guilds(discord.Object(id=GUILD_ID))
    async def pay(self, interaction: discord.Interaction, user: discord.Member, amount: int):
        if user == interaction.user:
            await interaction.response.send_message("❌ You can't pay yourself!", ephemeral=True)
            return
        
        if user.bot:
            await interaction.response.send_message("❌ You can't pay bots!", ephemeral=True)
            return
        
        if amount <= 0:
            await interaction.response.send_message("❌ Amount must be positive.", ephemeral=True)
            return
        
        sender_data = self.get_user_data(str(interaction.user.id))
        
        if sender_data["balance"] < amount:
            await interaction.response.send_message("❌ You don't have enough money in your wallet.", ephemeral=True)
            return
        
        # Transfer money
        sender_data["balance"] -= amount
        sender_data["total_spent"] += amount
        self.update_user_data(str(interaction.user.id), sender_data)
        
        self.add_money(str(user.id), amount)
        
        embed = discord.Embed(
            title="💸 Payment Sent",
            description=f"You paid **${amount:,}** to {user.mention}",
            color=0x00ff00
        )
        
        embed.add_field(name="Your New Balance", value=f"${sender_data['balance']:,}", inline=True)
        
        await interaction.response.send_message(embed=embed, ephemeral=True)
        
        # Notify recipient
        try:
            recipient_embed = discord.Embed(
                title="💰 Payment Received",
                description=f"You received **${amount:,}** from {interaction.user.mention}",
                color=0x00ff00
            )
            await user.send(embed=recipient_embed)
        except:
            pass  # User has DMs disabled
    
    @app_commands.command(name="leaderboard", description="View the economy leaderboard")
    @app_commands.guilds(discord.Object(id=GUILD_ID))
    async def leaderboard(self, interaction: discord.Interaction):
        await interaction.response.defer(ephemeral=True)
        
        try:
            with ECONOMY_FILE.open("r", encoding="utf-8") as f:
                data = json.load(f)
            
            # Calculate total wealth for each user
            user_wealth = []
            for user_id, user_data in data["users"].items():
                total_wealth = user_data["balance"] + user_data["bank"]
                if total_wealth > 0:  # Only include users with money
                    try:
                        user = interaction.guild.get_member(int(user_id))
                        if user:  # Only include current guild members
                            user_wealth.append((user, total_wealth))
                    except:
                        continue
            
            # Sort by wealth
            user_wealth.sort(key=lambda x: x[1], reverse=True)
            
            if not user_wealth:
                await interaction.followup.send("❌ No users found on the leaderboard.", ephemeral=True)
                return
            
            embed = discord.Embed(
                title="🏆 Economy Leaderboard",
                description="Top 10 richest members",
                color=0xffd700,
                timestamp=datetime.utcnow()
            )
            
            # Show top 10
            for i, (user, wealth) in enumerate(user_wealth[:10], 1):
                medal = "🥇" if i == 1 else "🥈" if i == 2 else "🥉" if i == 3 else f"{i}."
                embed.add_field(
                    name=f"{medal} {user.display_name}",
                    value=f"${wealth:,}",
                    inline=True
                )
            
            # Show user's position if not in top 10
            user_position = None
            for i, (user, wealth) in enumerate(user_wealth, 1):
                if user.id == interaction.user.id:
                    user_position = i
                    break
            
            if user_position and user_position > 10:
                user_data = self.get_user_data(str(interaction.user.id))
                user_wealth_total = user_data["balance"] + user_data["bank"]
                embed.add_field(
                    name=f"Your Position: #{user_position}",
                    value=f"${user_wealth_total:,}",
                    inline=False
                )
            
            embed.set_footer(text="MGVRP Economy System")
            
            await interaction.followup.send(embed=embed, ephemeral=True)
            
        except Exception as e:
            logger.error(f"Error generating leaderboard: {e}")
            await interaction.followup.send("❌ Error generating leaderboard.", ephemeral=True)

async def setup(bot):
    await bot.add_cog(EconomySystem(bot))