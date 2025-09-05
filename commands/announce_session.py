import discord
from discord.ext import commands
from discord import app_commands

class AnnounceSession(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @app_commands.guilds(1277047315047120978)
    @app_commands.command(name="session_startup", description="Announce a roleplay session with host, time, and reactions")
    @app_commands.describe(host="User hosting", time="UNIX timestamp or friendly time", reactions="Reactions needed", cohost="User co-hosting (optional)")
    async def session_startup(self, interaction: discord.Interaction, host: discord.User, time: str, reactions: int, cohost: discord.User = None):
        await interaction.response.defer(ephemeral=True)
        host_text = f"{host.mention} and {cohost.mention}" if cohost else f"{host.mention}"
        log_channel_id = 1339764330425487460
        economy_channel_id = 1403779808135090186

        def generate_embed(interested_count, late_count):
            embed = discord.Embed(
                color=0x89CFF0,
                title="<:Megaphone_Blue:1386443190260989982> Session Startup <:Megaphone_Blue:1386443190260989982>",
                description=(
                    f"<:bluedash:1386424783058763906> Greetings, {host_text} {'are' if cohost else 'is'} currently planning on hosting a Roleplay session at {time}!\n"
                    f"<:bluedash:1386424783058763906> Before joining, ensure that you have read <#1278334460827406356> in order to avoid any moderation.\n"
                    f"<:bluedash:1386424783058763906> We need **{reactions}+ reactions** to begin\n"
                    f"<:bluedash:1386424783058763906> Register vehicles in <#1339746547826556938>\n"
                    f"<:bluedash:1386424783058763906> Use the buttons below to indicate interest or late arrival\n\n"
                    f"**Current Interest: {interested_count} player{'s' if interested_count != 1 else ''}\n"
                    f"Late Arrivals: {late_count} player{'s' if late_count != 1 else ''}**"
                )
            )
            embed.set_thumbnail(url="https://cdn.discordapp.com/attachments/1393957236891713556/1395111568164913313/5b39ef01ba7ebe82c4789d0436064ac9-removebg-preview.png?ex=68794265&is=6877f0e5&hm=c48e7259262a3285802c57065a9ae875b901f6c08b816487a0f6f4506d6b3793&")
            embed.set_image(url="https://cdn.discordapp.com/attachments/1350837749426683969/1387242786209792060/MGVRP_Mellow_Greenville_Things_banner_idk.png")
            embed.set_footer(text="Mellow's Greenville Roleplay™ - Developed by Baryonyx (Antivenom)")
            return embed

        class SessionView(discord.ui.View):
            def __init__(self):
                super().__init__(timeout=None)
                self.interested_users = set()
                self.late_users = set()

            @discord.ui.button(label="Interested", style=discord.ButtonStyle.success, custom_id="interested")
            async def interested(self, interaction_btn: discord.Interaction, button: discord.ui.Button):
                user = interaction_btn.user
                if user.id not in self.interested_users:
                    self.interested_users.add(user.id)
                    await interaction_btn.response.send_message("✅ You have shown interest in the session!", ephemeral=True)
                    log_channel = interaction.guild.get_channel(log_channel_id)
                    if log_channel:
                        await log_channel.send(f"{user.mention} has shown interest in the session hosted by {host_text}")
                    economy_channel = interaction.guild.get_channel(economy_channel_id)
                    if economy_channel:
                        await economy_channel.send(f"{user} {user.id} +1000")
                    await msg.edit(embed=generate_embed(len(self.interested_users), len(self.late_users)), view=self)
                else:
                    await interaction_btn.response.send_message("⚠️ You have already shown interest!", ephemeral=True)

            @discord.ui.button(label="Revoke Interest", style=discord.ButtonStyle.danger, custom_id="revoke_interest")
            async def revoke_interest(self, interaction_btn: discord.Interaction, button: discord.ui.Button):
                user = interaction_btn.user
                if user.id in self.interested_users:
                    self.interested_users.remove(user.id)
                    await interaction_btn.response.send_message("✅ You have revoked your interest in the session.", ephemeral=True)
                    log_channel = interaction.guild.get_channel(log_channel_id)
                    if log_channel:
                        await log_channel.send(f"{user.mention} has revoked their interest in the session hosted by {host_text}")
                    economy_channel = interaction.guild.get_channel(economy_channel_id)
                    if economy_channel:
                        await economy_channel.send(f"{user} {user.id} -1000")
                    await msg.edit(embed=generate_embed(len(self.interested_users), len(self.late_users)), view=self)
                else:
                    await interaction_btn.response.send_message("⚠️ You have not shown interest to revoke!", ephemeral=True)

            @discord.ui.button(label="Join Late (15 min)", style=discord.ButtonStyle.primary, custom_id="join_late")
            async def join_late(self, interaction_btn: discord.Interaction, button: discord.ui.Button):
                user = interaction_btn.user
                if user.id not in self.late_users:
                    self.late_users.add(user.id)
                    await interaction_btn.response.send_message("✅ You have indicated you will join up to 15 minutes late!", ephemeral=True)
                    log_channel = interaction.guild.get_channel(log_channel_id)
                    if log_channel:
                        await log_channel.send(f"{user.mention} has indicated they will join the session hosted by {host_text} up to 15 minutes late")
                    economy_channel = interaction.guild.get_channel(economy_channel_id)
                    if economy_channel:
                        await economy_channel.send(f"{user} {user.id} +1000")
                    await msg.edit(embed=generate_embed(len(self.interested_users), len(self.late_users)), view=self)
                else:
                    await interaction_btn.response.send_message("⚠️ You have already indicated you will join late!", ephemeral=True)

            @discord.ui.button(label="Revoke Late Interest", style=discord.ButtonStyle.secondary, custom_id="revoke_late")
            async def revoke_late(self, interaction_btn: discord.Interaction, button: discord.ui.Button):
                user = interaction_btn.user
                if user.id in self.late_users:
                    self.late_users.remove(user.id)
                    await interaction_btn.response.send_message("✅ You have revoked your late joining indication.", ephemeral=True)
                    log_channel = interaction.guild.get_channel(log_channel_id)
                    if log_channel:
                        await log_channel.send(f"{user.mention} has revoked their late joining indication for the session hosted by {host_text}")
                    economy_channel = interaction.guild.get_channel(economy_channel_id)
                    if economy_channel:
                        await economy_channel.send(f"{user} {user.id} -1000")
                    await msg.edit(embed=generate_embed(len(self.interested_users), len(self.late_users)), view=self)
                else:
                    await interaction_btn.response.send_message("⚠️ You have not indicated late joining to revoke!", ephemeral=True)

        view = SessionView()
        msg = await interaction.channel.send(embed=generate_embed(0, 0), view=view)
        await interaction.followup.send("✅ Session announcement sent!", ephemeral=True)

async def setup(bot):
    await bot.add_cog(AnnounceSession(bot))
