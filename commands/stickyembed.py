import discord
from discord.ext import commands, tasks

STICKY_CHANNEL_ID = 1339749459998933022
STICKY_EMBED_THUMBNAIL = "https://cdn.discordapp.com/attachments/1393957236891713556/1395111568164913313/5b39ef01ba7ebe82c4789d0436064ac9-removebg-preview.png?ex=68b3ed25&is=68b29ba5&hm=1db29f9eb0fc5562a151e21a1febc5cdcc50637214caa4fb4bfc8722ce068f81&"
STICKY_EMBED_FOOTER = "Mellow's Greenville Roleplay"
STICKY_EMBED_DESCRIPTION = (
    "Have a complaint, request or just a general question? Contact our staff team in the https://discord.com/channels/1277047315047120978/1387097565933207644 channel. \n\n"
    "Please keep this chat as respectful as possible for everyone in MGVRP."
)

class StickyEmbed(commands.Cog):
    @commands.command(name="stickyrefresh", help="Check for or send the sticky embed in the sticky channel.")
    @commands.has_permissions(manage_messages=True)
    async def stickyrefresh(self, ctx):
        """Manually check for or send the sticky embed in the sticky channel."""
        await ctx.send("[StickyEmbed] Checking for existing sticky embed...")
        channel = self.bot.get_channel(STICKY_CHANNEL_ID)
        if not channel:
            await ctx.send(f"[StickyEmbed] Could not find channel with ID {STICKY_CHANNEL_ID}.")
            return
        found = False
        async for msg in channel.history(limit=50):
            if msg.author == self.bot.user and msg.embeds:
                embed = msg.embeds[0]
                if embed.description and STICKY_EMBED_DESCRIPTION in embed.description:
                    self.last_embed_message = msg
                    found = True
                    await ctx.send("[StickyEmbed] Found existing sticky embed.")
                    break
        if not found:
            embed = discord.Embed(description=STICKY_EMBED_DESCRIPTION, color=0x2f3136)
            embed.set_footer(text=STICKY_EMBED_FOOTER)
            embed.set_thumbnail(url=STICKY_EMBED_THUMBNAIL)
            self.last_embed_message = await channel.send(embed=embed)
            await ctx.send("[StickyEmbed] No sticky embed found, sent new sticky embed.")
    async def cog_load(self):
        print("[StickyEmbed] Cog loaded, checking for existing sticky embed on startup...")
        await self.ensure_sticky_on_startup()

    async def ensure_sticky_on_startup(self):
        await self.bot.wait_until_ready()
        channel = self.bot.get_channel(STICKY_CHANNEL_ID)
        if not channel:
            print(f"[StickyEmbed] Could not find channel with ID {STICKY_CHANNEL_ID} on startup.")
            return
        try:
            async for msg in channel.history(limit=50):
                if msg.author == self.bot.user and msg.embeds:
                    embed = msg.embeds[0]
                    if embed.description and STICKY_EMBED_DESCRIPTION in embed.description:
                        self.last_embed_message = msg
                        print("[StickyEmbed] Found existing sticky embed on startup.")
                        return
            # No sticky embed found, send one
            embed = discord.Embed(description=STICKY_EMBED_DESCRIPTION, color=0x2f3136)
            embed.set_footer(text=STICKY_EMBED_FOOTER)
            embed.set_thumbnail(url=STICKY_EMBED_THUMBNAIL)
            self.last_embed_message = await channel.send(embed=embed)
            print("[StickyEmbed] No sticky embed found, sent new sticky embed on startup.")
        except Exception as e:
            print(f"[StickyEmbed] Error checking/sending sticky embed on startup: {e}")
    def __init__(self, bot):
        self.bot = bot
        self.last_embed_message = None
        self.refresh_task = None

    @commands.Cog.listener()
    async def on_message(self, message):
        if message.channel.id != STICKY_CHANNEL_ID or message.author.bot:
            return
        print(f"[StickyEmbed] Detected message in sticky channel by {message.author} (ID: {message.author.id})")
        # Delete old sticky embed if exists
        if self.last_embed_message:
            try:
                await self.last_embed_message.delete()
                print("[StickyEmbed] Deleted previous sticky embed.")
            except Exception as e:
                print(f"[StickyEmbed] Failed to delete previous sticky embed: {e}")
        # Send new sticky embed
        embed = discord.Embed(description=STICKY_EMBED_DESCRIPTION, color=0x2f3136)
        embed.set_footer(text=STICKY_EMBED_FOOTER)
        embed.set_thumbnail(url=STICKY_EMBED_THUMBNAIL)
        self.last_embed_message = await message.channel.send(embed=embed)
        print("[StickyEmbed] Sent new sticky embed.")
        # Start/Restart refresh task
        if self.refresh_task and not self.refresh_task.done():
            self.refresh_task.cancel()
            print("[StickyEmbed] Cancelled previous refresh task.")
        self.refresh_task = self.bot.loop.create_task(self.refresh_sticky(message.channel))
        print("[StickyEmbed] Started refresh task.")

    async def refresh_sticky(self, channel):
        await discord.utils.sleep_until(discord.utils.utcnow() + discord.timedelta(seconds=5))
        print("[StickyEmbed] Refreshing sticky embed after 5 seconds.")
        if self.last_embed_message:
            try:
                await self.last_embed_message.delete()
                print("[StickyEmbed] Deleted sticky embed before refresh.")
            except Exception as e:
                print(f"[StickyEmbed] Failed to delete sticky embed before refresh: {e}")
        embed = discord.Embed(description=STICKY_EMBED_DESCRIPTION, color=0x2f3136)
        embed.set_footer(text=STICKY_EMBED_FOOTER)
        embed.set_thumbnail(url=STICKY_EMBED_THUMBNAIL)
        self.last_embed_message = await channel.send(embed=embed)
        print("[StickyEmbed] Sent refreshed sticky embed.")

async def setup(bot):
    cog = StickyEmbed(bot)
    await bot.add_cog(cog)
    bot.add_command(cog.stickyrefresh)
