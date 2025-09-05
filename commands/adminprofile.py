import discord
from discord.ext import commands
from discord import app_commands

STAFF_PROFILES = {
    '1130717731998683200': {
        'discord': '@DIRECTOR | MELLOW',
        'robloxUser': 'yoboyjuju09',
        'robloxId': '1795315647',
        'nicknames': 'Mellow',
        'roles': "Director and owner of Mellow's Greenville Roleplay",
        'command': ':addadmin 1795315647'
    },
    '549296839191691265': {
        'discord': '@CO-DIRECTOR | BΛRYOИYXX',
        'robloxUser': 'Blackwater_MERC',
        'robloxId': '573091829',
        'nicknames': 'Baryonyx, Bary, Blackwater',
        'roles': "Co-Director of Mellow's Greenville Roleplay",
        'command': ':addadmin 573091829'
    },
    '812410874811646012': {
        'discord': '@STAFF | GEORGE',
        'robloxUser': 'moneypugs1',
        'robloxId': '2635116405',
        'nicknames': 'George, Money',
        'roles': "Session Staff in Mellow's Greenville Roleplay",
        'command': ':addadmin 2635116405'
    },
    '908162965310689302': {
        'discord': '@STAFF | MIKE',
        'robloxUser': 'President_1999',
        'robloxId': '2434296994',
        'nicknames': 'Mike',
        'roles': "Session Staff and host in Mellow's Greenville Roleplay",
        'command': ':addadmin 2434296994'
    }
}

class AdminProfile(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @app_commands.guilds(1277047315047120978)
    @app_commands.command(name="adminclockin", description="Send a button for staff to reveal their profile info")
    async def adminclockin(self, interaction: discord.Interaction):
        await interaction.response.defer(ephemeral=True)
        embed = discord.Embed(
            color=0x89CFF0,
            title="📜 Reveal Staff Profile",
            description="If you are a staff member, press the button below to reveal your profile info to the server."
        )
        embed.set_thumbnail(url="https://cdn.discordapp.com/attachments/1350837749426683969/1387479314861391964/main_server_logo.webp")
        embed.set_footer(text="Mellow's Greenville Roleplay™ - Developed by Baryonyx (Antivenom)")
        view = self.ProfileButtonView()
        await interaction.channel.send(embed=embed, view=view)
        await interaction.followup.send("✅ Profile button created!", ephemeral=True)

    class ProfileButtonView(discord.ui.View):
        def __init__(self):
            super().__init__(timeout=None)

        @discord.ui.button(label="Reveal My Profile", style=discord.ButtonStyle.primary, custom_id="reveal_profile", emoji="📜")
        async def reveal_profile(self, interaction_btn: discord.Interaction, button: discord.ui.Button):
            user_id = str(interaction_btn.user.id)
            profile = STAFF_PROFILES.get(user_id)
            if not profile:
                await interaction_btn.response.send_message("❌ You are not authorized to reveal a profile.", ephemeral=True)
                return
            embed = discord.Embed(
                color=0x89CFF0,
                title=f"{profile['discord']} Profile",
                description=(
                    f"**Discord ID:** {user_id}\n"
                    f"**Discord Username:** {profile['discord']}\n"
                    f"**Roblox user:** {profile['robloxUser']}\n"
                    f"**Roblox ID:** {profile['robloxId']}\n"
                    f"**Nickname(s):** {profile['nicknames']}\n"
                    f"**Role(s):** {profile['roles']}\n\n"
                    f"**Command:** `{profile['command']}`\n"
                    f"**YOU ARE NOT GARUNTEED TO BE SESSION STAFF ALL THE TIME**"
                )
            )
            embed.set_thumbnail(url="https://cdn.discordapp.com/attachments/1350837749426683969/1387479314861391964/main_server_logo.webp")
            embed.set_footer(text="Mellow's Greenville Roleplay™ - Developed by Baryonyx (Antivenom)")
            await interaction_btn.response.send_message(f"{interaction_btn.user.mention} plans to join the upcoming session!", embed=embed, ephemeral=False)

async def setup(bot):
    await bot.add_cog(AdminProfile(bot))
