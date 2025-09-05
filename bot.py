import os
import discord
from discord.ext import commands
from dotenv import load_dotenv

load_dotenv()
TOKEN = os.getenv('TOKEN')

intents = discord.Intents.default()
intents.guilds = True
intents.messages = True
intents.message_content = True
intents.dm_messages = True
intents.reactions = True

bot = commands.Bot(command_prefix='!', intents=intents)

# Async load_commands to properly await load_extension
async def load_commands():
    for filename in os.listdir('./commands'):
        if filename.endswith('.py'):
            ext = f'commands.{filename[:-3]}'
            try:
                await bot.load_extension(ext)
                print(f'Loaded extension: {ext}')
            except Exception as e:
                print(f'Failed to load {ext}: {e}')


@bot.event
async def on_ready():
    print(f'✅ Logged in as {bot.user}')
    await bot.change_presence(activity=discord.Activity(type=discord.ActivityType.watching, name="Mellow's Greenville Roleplay"))
    # Only load commands once, after bot is ready
    if not hasattr(bot, "_commands_loaded"):
        await load_commands()
        bot._commands_loaded = True

bot.run(TOKEN)
