import random

import discord
from discord.ext import commands

import Utils.reddit
import Utils.googleSheet
import Utils.collectiveApi

from Utils.reddit import submit


class MiscCog(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.command()
    async def artToCard(self, ctx):
        try:
            await ctx.send(Utils.collectiveApi.artToCard(ctx.message.attachments[0].url))
        except:
            await ctx.send("Something went wrong...")

    @commands.command()
    async def art(self, ctx, card_link):
        try:
            art = Utils.collectiveApi.getArt(card_link)
            await ctx.send(art)
        except Exception as e:
            print(e)
            await ctx.send("Something went wrong.")

    @commands.command()
    async def card(self, ctx, *name):
        link = Utils.googleSheet.findCardLink(name)
        await ctx.send(link)

    @commands.command()
    async def submit(self, ctx, card_link, optional_text="", optional_type=""):
        submit(card_link, optional_text, optional_type)
        await ctx.send("Submitted!")

    @commands.command()
    async def updates(self,ctx):
        cards = Utils.reddit.fetchCards()
        cards.sort(key=lambda x: x.score, reverse=True)

        updates = Utils.reddit.fetchUpdates()
        updates.sort(key=lambda x: x.score, reverse=True)

        text = f"Total Updates: {len(updates)}\n\n"

        # prevent index out of range errors
        try:
            top10card = cards[9]
        except IndexError:
            top10card = cards[-1]

        text += f"PS: Top 10 voted [Card] currently is at {top10card.score} votes! ({top10card.title})\n\n"
        for post in updates:
            # slice "[Update]" away
            text += f"{post.title[9:]}\nScore: {post.score}\n\n"

        text = "```"+text+"```"

        await ctx.send(text)

    @commands.command()
    async def top10(self,ctx):
        cards = Utils.reddit.fetchCards()
        cards.sort(key=lambda x: x.score, reverse=True)

        text = ""
        for post in cards[:9]:
            # slice "[Card]" away
            text += f"{post.title[7:]}\nScore: {post.score}\n\n"
        text = "```"+text+"```"

        await ctx.send(text)


    @commands.command()
    async def coinflip(self, ctx):
        await ctx.send("Tails!" if (0.5 < random.random()) else "Head!")


def setup(bot):  # an extension must have a setup function
    bot.add_cog(MiscCog(bot))  # adding a cog
