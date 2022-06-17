# Dear programmer:
# When I wrote this code, only god and I knew how it worked
# Now, only god knows it!
#
# Therefore, if you are trying to optimize this
# and it fails (most surely)
# please increase this counter as a warning for the next person:
#
# total_hours_wasted_here = 254
import os

from discord import app_commands
from dotenv import load_dotenv

import discord
from discord.ext import commands

import asyncio
import platform
# prevent event loop is closed error
# https://stackoverflow.com/questions/45600579/asyncio-event-loop-is-closed-when-getting-loop
if platform.system()=='Windows':
    asyncio.set_event_loop_policy(asyncio.WindowsSelectorEventLoopPolicy())

load_dotenv()

class MyBot(commands.Bot):
    async def setup_hook(self):

        for filename in os.listdir('Cogs'):
            if filename.endswith('.py'):
                print(f"Loading Cog: {filename}")
                await bot.load_extension(f'Cogs.{filename[:-3]}')
            else:
                if filename == '__pycache__':
                    continue

                print(f'Unable to load {filename}')

        # await bot.load_extension('Cogs.dev_cog')
        # await bot.load_extension('Cogs.misc_cog')
        # await bot.load_extension('Cogs.stats_cog')
        # await bot.load_extension('Cogs.admin_cog')

        # self.tree.copy_global_to(guild=discord.Object(id=guild_id))
        # await self.tree.sync(guild=discord.Object(id=guild_id))


intents = discord.Intents.all()

bot = MyBot(
    command_prefix="!",
    help_command=None,
    intents=intents,
)


@bot.event
async def on_ready():
    print(f'{bot.user} has connected to Discord!')

@bot.check_once
def exclude_dms(ctx):
    return ctx.guild is not None

@bot.check_once
def exclude_banned_users(ctx):
    # previously would prevent cmds from running if banlist.txt doesn't exist
    # 'x+' mode raises FileExistsError if the file already exists
    try:
        f = open('Data/banlist.txt', 'x+')
    except FileExistsError:
        with open("Data/banlist.txt", "r") as f:
            for line in f.readlines():
                if line.strip("\n") == str(ctx.author.id):
                    return False
    return True

bot.run(os.getenv("DISCORD_TOKEN"))