import os
import discord
from discord.ext import commands
from dotenv import load_dotenv
import logging
import asyncio
from datetime import datetime

load_dotenv()
TOKEN = os.getenv('TOKEN')

# Set up logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('bot.log'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

intents = discord.Intents.default()
intents.guilds = True
intents.messages = True
intents.message_content = True
intents.dm_messages = True
intents.reactions = True
intents.members = True  # For member management features

bot = commands.Bot(command_prefix='!', intents=intents)
bot.start_time = datetime.utcnow()

# Start web server in a separate thread
def start_web_server():
    try:
        from web_server import start_web_server
        start_web_server(bot, host='0.0.0.0', port=5000)
    except ImportError:
        logger.warning("Web server module not found. Web interface will not be available.")
    except Exception as e:
        logger.error(f"Failed to start web server: {e}")
# Async load_commands to properly await load_extension
async def load_commands():
    loaded_count = 0
    failed_count = 0
    for filename in os.listdir('./commands'):
        if filename.endswith('.py'):
            ext = f'commands.{filename[:-3]}'
            try:
                await bot.load_extension(ext)
                logger.info(f'✅ Loaded extension: {ext}')
                loaded_count += 1
            except Exception as e:
                logger.error(f'❌ Failed to load {ext}: {e}')
                failed_count += 1
    
    logger.info(f'Extension loading complete: {loaded_count} loaded, {failed_count} failed')
    return loaded_count, failed_count


@bot.event
async def on_ready():
    logger.info(f'✅ Logged in as {bot.user} (ID: {bot.user.id})')
    logger.info(f'Connected to {len(bot.guilds)} guilds')
    
    await bot.change_presence(activity=discord.Activity(type=discord.ActivityType.watching, name="Mellow's Greenville Roleplay"))
    
    # Only load commands once, after bot is ready
    if not hasattr(bot, "_commands_loaded"):
        loaded, failed = await load_commands()
        bot._commands_loaded = True
        logger.info(f'Bot ready with {len(bot.tree.get_commands())} slash commands')
        
        # Start web server
        import threading
        web_thread = threading.Thread(target=start_web_server, daemon=True)
        web_thread.start()
        logger.info("Web server started on http://localhost:5000")

@bot.event
async def on_command_error(ctx, error):
    """Global error handler for prefix commands"""
    if isinstance(error, commands.CommandNotFound):
        return  # Ignore command not found errors
    
    logger.error(f'Command error in {ctx.command}: {error}')
    
    if isinstance(error, commands.MissingPermissions):
        await ctx.send("❌ You don't have permission to use this command.")
    elif isinstance(error, commands.BotMissingPermissions):
        await ctx.send("❌ I don't have the required permissions to execute this command.")
    else:
        await ctx.send("❌ An error occurred while processing the command.")

@bot.event
async def on_application_command_error(interaction, error):
    """Global error handler for slash commands"""
    logger.error(f'Slash command error in {interaction.command}: {error}')
    
    if interaction.response.is_done():
        await interaction.followup.send("❌ An error occurred while processing the command.", ephemeral=True)
    else:
        await interaction.response.send_message("❌ An error occurred while processing the command.", ephemeral=True)

# Graceful shutdown
async def shutdown():
    logger.info('Shutting down bot...')
    await bot.close()

# Health check command
@bot.command(name='health')
@commands.has_permissions(administrator=True)
async def health_check(ctx):
    """Check bot health status"""
    uptime = datetime.utcnow() - bot.start_time
    embed = discord.Embed(
        title="🏥 Bot Health Check",
        color=0x00ff00,
        timestamp=datetime.utcnow()
    )
    embed.add_field(name="Status", value="✅ Online", inline=True)
    embed.add_field(name="Uptime", value=f"{uptime.days}d {uptime.seconds//3600}h {(uptime.seconds//60)%60}m", inline=True)
    embed.add_field(name="Latency", value=f"{round(bot.latency * 1000)}ms", inline=True)
    embed.add_field(name="Guilds", value=len(bot.guilds), inline=True)
    embed.add_field(name="Commands", value=len(bot.tree.get_commands()), inline=True)
    embed.add_field(name="Web Interface", value="http://localhost:5000", inline=True)
    await ctx.send(embed=embed)

bot.run(TOKEN)
