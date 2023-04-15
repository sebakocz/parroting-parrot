import json
import random
import datetime
from itertools import cycle

import discord
from discord.ext import commands, tasks
from discord import app_commands

import Utils.Collective.api
import Utils.Collective.db
import Utils.Collective.misc
import Utils.tenor_api


class MiscCog(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

        # update card names list
        self.card_list = cycle(Utils.Collective.api.fetch_random_card_names())

    @commands.Cog.listener()
    async def on_ready(self):
        self.task_change_activity.start()
        self.task_reset_challenge.start()

    @tasks.loop(seconds=10)
    async def task_change_activity(self):
        await self.bot.change_presence(activity=discord.Game(next(self.card_list)))

    @commands.hybrid_command(name="parrot", description="Repeats the sentence")
    @app_commands.describe(sentence="type something for parrot to repeat")
    async def parrot(self, ctx, *, sentence):
        await ctx.send(f"> {sentence}")

    @commands.hybrid_command(
        name="coinflip", description="Flips a coin. Returns either 'Tails' or 'Head'"
    )
    async def coinflip(self, ctx):
        await ctx.send("Tails!" if (0.5 < random.random()) else "Head!")

    @commands.hybrid_command(name="github", description="Shows Parrot's code")
    async def github(self, ctx):
        await ctx.send("https://github.com/sebakocz/parroting-parrot")

    @commands.hybrid_command(
        name="support", description="Sevas also accepts love, food and shelter"
    )
    async def support(self, ctx):
        await ctx.send("https://www.buymeacoffee.com/sevas")

    @tasks.loop(time=datetime.time(hour=6, minute=30))
    async def task_reset_challenge(self):
        open("Data/challenge_players.txt", "w").close()
        await Utils.Collective.misc.set_challenge_cards()

    @commands.hybrid_command(name="gif", description="Shows a random parrot")
    async def gif(self, ctx):
        await ctx.send(Utils.tenor_api.get_random_parrot_gif())


async def setup(bot):  # an extension must have a setup function
    await bot.add_cog(MiscCog(bot))  # adding a cog
