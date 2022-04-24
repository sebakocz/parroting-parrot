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
from dotenv import load_dotenv

from discord.ext import commands

load_dotenv()

bot = commands.Bot(
    command_prefix="!",
    help_command=None
)


@bot.event
async def on_ready():
    print(f'{bot.user} has connected to Discord!')

@bot.check_once
def exclude_dms(ctx):
    return ctx.guild is not None

@bot.check_once
def exclude_banned_users(ctx):
    with open("Data/banlist.txt", "r") as f:
        for line in f.readlines():
            if line.strip("\n") == str(ctx.author.id):
                return False
        return True


for filename in os.listdir('Cogs'):
    if filename.endswith('.py'):
        bot.load_extension(f'Cogs.{filename[:-3]}')
    else:
        if filename == '__pycache__':
            continue

        print(f'Unable to load {filename}')

bot.run(os.getenv("DISCORD_TOKEN"))