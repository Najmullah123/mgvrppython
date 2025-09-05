import os
import discord
from discord.ext import commands
from dotenv import load_dotenv

load_dotenv()
TOKEN = os.getenv('TOKEN')
GUILD_ID = int(os.getenv('GUILD_ID', '1277047315047120978'))

# Configure intents
intents = discord.Intents.default()
intents.message_content = True  # Enable message content intent for prefix commands
bot = commands.Bot(command_prefix='!', intents=intents)

# Load all command extensions from the commands folder
async def load_commands():
    for filename in os.listdir('./commands'):
        if filename.endswith('.py'):
            try:
                await bot.load_extension(f'commands.{filename[:-3]}')
                print(f"Loaded extension: commands.{filename[:-3]}")
            except Exception as e:
                print(f"Failed to load extension commands.{filename[:-3]}: {e}")


@bot.event
async def on_ready():
    print(f'Logged in as {bot.user}')
    try:
        await load_commands()
        # Set all commands to the target guild for instant deployment
        guild_obj = discord.Object(id=GUILD_ID)
        for cmd in bot.tree.get_commands():
            cmd.guilds = [guild_obj]
        # Print all registered app commands before syncing
        print('Registered app commands before sync:')
        for cmd in bot.tree.get_commands():
            print(f'- {cmd.name} (type: {type(cmd)})')
        synced = await bot.tree.sync(guild=guild_obj)
        print(f'✅ Successfully synced {len(synced)} commands to guild {GUILD_ID}.')
        if len(synced) == 0:
            print('⚠️ No commands were synced. This usually means no @app_commands.command are registered or cogs are not set up properly.')
    except Exception as e:
        print(f'❌ Error deploying commands: {e}')

# Run the bot
bot.run(TOKEN)