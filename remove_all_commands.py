import os
import discord
from discord.ext import commands
from dotenv import load_dotenv

load_dotenv()
TOKEN = os.getenv('TOKEN')
CLIENT_ID = os.getenv('CLIENT_ID')

intents = discord.Intents.default()
bot = commands.Bot(command_prefix='!', intents=intents)


@bot.event
async def on_ready():
    print(f'Logged in as {bot.user}')
    import os
    import discord
    from discord.ext import commands
    from dotenv import load_dotenv

    load_dotenv()
    TOKEN = os.getenv('TOKEN')
    CLIENT_ID = os.getenv('CLIENT_ID')
    GUILD_ID = os.getenv('GUILD_ID')

    intents = discord.Intents.default()
    bot = commands.Bot(command_prefix='!', intents=intents)

    async def wipe_all_commands():
        # Remove all global commands
        bot.tree.clear_commands(guild=None)
        await bot.tree.sync(guild=None)
        print('✅ All global commands have been removed.')
        # Remove all guild commands (if any)
        if GUILD_ID:
            try:
                guild_obj = discord.Object(id=int(GUILD_ID))
                bot.tree.clear_commands(guild=guild_obj)
                await bot.tree.sync(guild=guild_obj)
                print(f'✅ All commands removed for guild {GUILD_ID}.')
            except Exception as e:
                print(f'❌ Error removing guild commands: {e}')

    @bot.event
    async def on_ready():
        print(f'Logged in as {bot.user}')
        try:
            await wipe_all_commands()
        except Exception as e:
            print(f'❌ Error wiping commands: {e}')
        await bot.close()

    bot.run(TOKEN)
