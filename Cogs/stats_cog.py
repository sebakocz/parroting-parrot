# a place requests involving game stats like !updates or !winrate

import discord
from discord.ext import commands, tasks
import Utils.collective_winrates as analyse

class StatsCog(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.fetch_winrate_data.start()

    def cog_unload(self):
        self.fetch_winrate_data.stop()


    @tasks.loop(seconds=86400)
    async def fetch_winrate_data(self):
        await analyse.collect_winrate_data()


    @commands.group(invoke_without_command=True)
    async def stats(self, ctx):
        await ctx.send("""  
`!stats winrate`
`!stats playrate`
`!stats help`
        """)

    @stats.command()
    async def winrate(self, ctx):
        winrate = analyse.display_current_data_winrate()
        await ctx.send(f"```{winrate}```")


    @stats.command()
    async def playrate(self, ctx):
        playrate = analyse.display_current_data_playrate()
        await ctx.send(f"```{playrate}```")


    @stats.command()
    async def help(self, ctx):
        await ctx.send("""
**•━•━•━•━•━•━•━•━•━•━•━•━•━•━•━•━•━•━•━•━•━•━•━•━•━•━•**
**Collective Stat Analysis**

The following data uses game records from the multiplayer queue that happened in the last 3 months. This data is updated daily. Mirrors are excluded.

**Playrate:**
Top 10 most used cards.

**Winrate:**
Top 10 cards with heighest win percentage. Card's with a p-value of >= 0.01 are excluded.

**What's a p-value?**
The p-values shown are indicators of how confident we are that the winrate is skewed above 50%. **Low** p values indicate **high** confidence, and **high** p-values indicate **low** confidence.        """)


async def setup(bot):  # an extension must have a setup function
    await bot.add_cog(StatsCog(bot))  # adding a cog
