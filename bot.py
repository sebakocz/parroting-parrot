# Dear programmer:
# When I wrote this code, only god, and I knew how it worked
# Now, only god knows it!
#
# Therefore, if you are trying to optimize this,
# and it fails (most surely)
# please increase this counter as a warning for the next person:
#
# total_hours_wasted_here = 254
import os
import logging as log

from dotenv import load_dotenv

import discord
from discord.ext import commands

import asyncio
import platform

from Fetcher.fetcher_list import FetcherList
from help import CustomHelpCmd

# prevent event loop is closed error
# https://stackoverflow.com/questions/45600579/asyncio-event-loop-is-closed-when-getting-loop
if platform.system() == "Windows":
    asyncio.set_event_loop_policy(asyncio.WindowsSelectorEventLoopPolicy())

discord.utils.setup_logging()

discord.VoiceClient.warn_nacl = False

load_dotenv()

isDev = os.getenv("DEV") == "True"
log.info(f"Running in {'DEV' if isDev else 'PROD'} mode")


class MyBot(commands.Bot):
    async def setup_hook(self):

        for filename in os.listdir("Cogs"):
            if filename.endswith(".py"):
                log.info(f"Loading Cog: {filename}")
                await bot.load_extension(f"Cogs.{filename[:-3]}")
            else:
                if filename == "__pycache__":
                    continue

                log.error(f"Unable to load {filename}")

        # await bot.load_extension('Cogs.dev_cog')
        # await bot.load_extension('Cogs.reaction_cog')
        # await bot.load_extension('Cogs.mod_cog')
        # await bot.load_extension('Cogs.misc_cog')
        # await bot.load_extension('Cogs.stats_cog')
        # await bot.load_extension('Cogs.admin_cog')

        # self.tree.copy_global_to(guild=discord.Object(id=guild_id))
        # await self.tree.sync(guild=discord.Object(id=guild_id))

        if isDev:
            log.info("DEV: Updating README.md")
            with open("README.md", "w") as f:
                f.write(
                    "# ParrotingParrot - A friendly feather of Collective, The Community Created Card Game"
                )
                f.write("\n\n## Commands")
                f.write("\nList of usable commands. Case-sensitive.\n")

                for command in sorted(
                    [command for command in bot.commands if command.description],
                    key=lambda x: x.name,
                ):
                    f.write(f"\n### !{command.name} {command.signature}")
                    f.write(f"\n{command.description}")

                f.write("\n\n## Fetcher")
                f.write(
                    "\nYou can fetch heroes and cards from Collective as well as other card games. Names don't have to be accurate and the fetcher will try to find something relating.\n"
                )

                for fetcher in FetcherList.all:
                    f.write(f"\n### [[{fetcher.mod + ':' if fetcher.mod else ''}name]]")
                    f.write(f"\n{fetcher.description}")


intents = discord.Intents.all()

bot = MyBot(
    command_prefix="!",
    help_command=CustomHelpCmd(),
    intents=intents,
)


@bot.event
async def on_ready():
    log.info(f"{bot.user} has connected to Discord!")


@bot.check_once
def exclude_dms(ctx):
    return ctx.guild is not None


@bot.check_once
def exclude_banned_users(ctx):
    # previously would prevent cmds from running if banlist.txt doesn't exist
    # 'x+' mode raises FileExistsError if the file already exists
    try:
        open("Data/banlist.txt", "x+")
    except FileExistsError:
        with open("Data/banlist.txt", "r") as f:
            for line in f.readlines():
                if line.strip("\n") == str(ctx.author.id):
                    return False
    return True


bot.run(os.getenv("DISCORD_TOKEN"), log_handler=None)
