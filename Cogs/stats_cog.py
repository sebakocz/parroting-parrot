# a place requests involving game stats like !updates or !winrate

import discord
from discord.ext import commands, tasks
import Utils.collective_winrates as analyse
from discord import app_commands


class StatsCog(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.fetch_winrate_data.start()

    def cog_unload(self):
        self.fetch_winrate_data.stop()

    @tasks.loop(seconds=86400)
    async def fetch_winrate_data(self):
        await analyse.collect_winrate_data()

    @commands.hybrid_group(name="stats")
    async def stats(self, ctx):
        await ctx.send(
            """
`!stats winrate <length>`
`!stats playrate <length>`
`!stats help`
        """
        )

    @stats.command(
        name="winrate",
        description="top 10 cards with highest win percentage. Card's with a p-value of >= 0.01 are excluded",
    )
    @app_commands.describe(length="choose to size of the dataset, default is 10")
    async def winrate(self, ctx, length=10):
        winrate = analyse.display_current_data_winrate(length)

        if length != 10:
            with open("Data/stats_result.txt", "w") as file:
                file.write(winrate.to_string())
            await ctx.send(file=discord.File("Data/stats_result.txt"))
            return

        await ctx.send(f"```{winrate}```")

    @stats.command(name="playrate", description="top 10 most used cards")
    @app_commands.describe(length="choose to size of the dataset, default is 10")
    async def playrate(self, ctx, length=10):
        playrate = analyse.display_current_data_playrate(length)

        if length != 10:
            with open("Data/stats_result.txt", "w") as file:
                file.write(playrate.to_string())
            await ctx.send(file=discord.File("Data/stats_result.txt"))
            return

        await ctx.send(f"```{playrate}```")

    @stats.command(description="full explanation on stats")
    async def help(self, ctx):
        await ctx.send(
            """
**•━•━•━•━•━•━•━•━•━•━•━•━•━•━•━•━•━•━•━•━•━•━•━•━•━•━•**
**Collective Stat Analysis**

The following data uses game records from the multiplayer queue that happened in the last 3 months. This data is updated daily. Mirrors are excluded.

**Playrate:**
Top 10 most used cards.

**Winrate:**
Top 10 cards with highest win percentage. Card's with a p-value of >= 0.01 are excluded.

**What's a p-value?**
The p-values shown are indicators of how confident we are that the winrate is skewed above 50%. **Low** p values indicate **high** confidence, and **high** p-values indicate **low** confidence.        """
        )


async def setup(bot):  # an extension must have a setup function
    await bot.add_cog(StatsCog(bot))  # adding a cog
