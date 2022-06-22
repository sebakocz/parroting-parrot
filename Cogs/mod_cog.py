import discord
from discord.ext import commands
import Utils.reddit as reddit
from discord import app_commands

class ModCog(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    async def cog_check(self, ctx):
        return await ctx.bot.is_owner(ctx.author) or (discord.utils.get(ctx.author.roles, id=876985473061503046) != None)

    @commands.hybrid_command(name="set_flair", description="changes current flair on the subreddit")
    @app_commands.default_permissions(manage_messages=True)
    async def set_flair(self, ctx, season: int, week: int):
        await reddit.change_flair(season, week)
        await ctx.send(f"Changed to 'Season {season} - Week {week}'")


async def setup(bot):  # an extension must have a setup function
    await bot.add_cog(ModCog(bot))  # adding a cog
