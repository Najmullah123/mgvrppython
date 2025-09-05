import discord
from discord.ext import commands
from discord import app_commands
from config import EARLY_ACCESS_CHANNEL, SETTING_UP_CHANNEL
from utils.embed import create_embed

class SettingUp(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @app_commands.command(
        name="settingup",
        description="Send startup embeds to channels"
    )
    @app_commands.describe(
        session_host="Session Host (mention or ID)",
        priority_status="Priority status",
        frp_speed_limit="FRP speed limit",
        house_claiming="House claiming allowed? (Yes/No)",
        session_link="Roblox session link",
        peacetime="Peacetime status (e.g. Active/Inactive)",
        session_cohost="Session Co-Host (mention or ID)"
    )
    async def settingup(
        self,
        interaction: discord.Interaction,
        session_host: str,
        priority_status: str,
        frp_speed_limit: str,
        house_claiming: str,
        session_link: str,
        peacetime: str,
        session_cohost: str = None
    ):
        await interaction.response.defer(ephemeral=True)

        host = session_host
        cohost = session_cohost if session_cohost else "None"
        priority = priority_status
        frp = frp_speed_limit
        house = house_claiming
        peacetime = peacetime
        link = session_link

        early_access_channel_id = EARLY_ACCESS_CHANNEL
        startup_channel_id = SETTING_UP_CHANNEL

        early_access_description = (
            f"{host} has now released their roleplay session for early access users! "
            f"Before joining, ensure that you have read ⁠rules and the ⁠restricted-vehicles below in order to avoid any moderation.\n\n"
            f"<:bluedash:1386424783058763906> Session Host: {host}\n"
            f"<:bluedash:1386424783058763906> Session Co-Host: {cohost if cohost != 'None' else '*None*'}\n"
            f"<:bluedash:1386424783058763906> Priority Status: {priority}\n"
            f"<:bluedash:1386424783058763906> FRP Speed limit: {frp}\n"
            f"<:bluedash:1386424783058763906> House Claiming: {house}\n"
            f"<:bluedash:1386424783058763906> Peacetime: {peacetime}"
        )

        early_access_embed = create_embed(
            title="<:Megaphone_Blue:1386443190260989982> Mellow's Greenville Roleplay Early Access Release <:Megaphone_Blue:1386443190260989982>",
            description=early_access_description,
            color=0x89CFF0
        )
        early_access_embed.set_footer(text="Mellow's Greenville Roleplay™")
        early_access_embed.set_thumbnail(url="https://message.style/cdn/images/62c6b688787b4e26c30146c63bd0e1b0fa96f0d6d431e3d3c46ef6497d939cf3.png")

        button_row = discord.ui.View()
        button_row.add_item(
            discord.ui.Button(
                label="Session Link",
                style=discord.ButtonStyle.link,
                emoji="🖇️",
                url=link
            )
        )
        button_row.add_item(
            discord.ui.Button(
                label="Support",
                style=discord.ButtonStyle.link,
                emoji="❓",
                url="https://discord.com/channels/1277047315047120978/1387097565933207644"
            )
        )

        startup_embed = create_embed(
            title="<:Megaphone_Blue:1386443190260989982> Mellow's Greenville Roleplay Starting Up <:Megaphone_Blue:1386443190260989982>",
            description="<:bluedash:1386424783058763906> Session setup in progress, at this time Early Access, Staff and Public Services may join through the Early Access link.",
            color=0x89CFF0
        )
        startup_embed.set_footer(text="Mellow's Greenville Roleplay™")
        startup_embed.set_thumbnail(url="https://message.style/cdn/images/62c6b688787b4e26c30146c63bd0e1b0fa96f0d6d431e3d3c46ef6497d939cf3.png")

        try:
            early_access_channel = await self.bot.fetch_channel(early_access_channel_id)
            startup_channel = await self.bot.fetch_channel(startup_channel_id)

            if not early_access_channel or not startup_channel:
                await interaction.follow_up(content="❌ One or both fixed channels could not be fetched.", ephemeral=True)
                return

            await early_access_channel.send(embed=early_access_embed, view=button_row)
            await startup_channel.send(embed=startup_embed)

            await interaction.follow_up(content="✅ Early Access and Startup embeds sent to default channels.", ephemeral=True)
        except Exception as error:
            print(f"Error sending embeds: {error}")
            await interaction.follow_up(content="❌ Failed to send embeds due to an error.", ephemeral=True)

async def setup(bot):
    await bot.add_cog(SettingUp(bot))