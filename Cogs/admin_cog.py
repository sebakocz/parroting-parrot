import discord
from discord.ext import commands


class AdminCog(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    async def cog_check(self, ctx):
        return await ctx.bot.is_owner(ctx.author)

    @commands.command()
    async def ban(self, ctx, user: discord.User):
        with open('Data/banlist.txt', 'a') as f:
            f.write(str(user.id)+"\n")

    @commands.command()
    async def unban(self, ctx, user:discord.User):
        with open("Data/banlist.txt", "r") as f:
            lines = f.readlines()
        with open("Data/banlist.txt", "w") as f:
            for line in lines:
                if line.strip("\n") != str(user.id):
                    f.write(line)

def setup(bot):  # an extension must have a setup function
    bot.add_cog(AdminCog(bot))  # adding a cog