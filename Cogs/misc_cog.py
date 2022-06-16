import random
from itertools import cycle

import discord
from discord.ext import commands, tasks

import Utils.reddit
import Utils.googleSheet
import Utils.collectiveApi

from Utils.reddit import submit


class MiscCog(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

        # update card names list
        self.card_list = cycle(Utils.collectiveApi.fetchRandomCardNames())

    @commands.Cog.listener()
    async def on_ready(self):
        self.change_activity.start()

    @tasks.loop(seconds=10)
    async def change_activity(self):
        await self.bot.change_presence(activity=discord.Game(next(self.card_list)))


    @commands.command()
    async def week(self, ctx):
        await ctx.send(f"<t:{Utils.reddit.getLastWeekUnixStamp()}>")


    @commands.command()
    async def parrot(self, ctx, *, sentence):
        await ctx.send(f"> {sentence}")

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
    async def submit(self, ctx, card_link, optional_text="", optional_type="[Card]"):
        submit(card_link, optional_text, optional_type)
        await ctx.send("Submitted!")

    @commands.command()
    async def updates(self,ctx):
        cards = Utils.reddit.fetchPosts(Utils.reddit.PostType.CARD)

        updates = Utils.reddit.fetchPosts(Utils.reddit.PostType.UPDATE)

        text = f"Total Updates: {len(updates)}\n\n"

        # prevent index out of range errors
        try:
            top10card = cards[9]
        except IndexError:
            try:
                top10card = cards[-1]
            except IndexError:
                await ctx.send("No updates found for this week. Go post some!")
                return

        text += f"PS: Top 10 voted [Card] currently is at {top10card.score} votes! ({top10card.title})\n\n"
        for post in updates:
            # slice "[Update]" away
            text += f"{post.title[9:]}\nScore: {post.score}\n\n"

        text = "```"+text+"```"

        await ctx.send(text)

    @commands.command()
    async def top10(self,ctx):
        cards = Utils.reddit.fetchPosts(Utils.reddit.PostType.CARD)

        text = ""
        for post in cards[:9]:
            # slice "[Card]" away
            text += f"{post.title[7:]}\nScore: {post.score}\n\n"
        text = "```"+text+"```"

        await ctx.send(text)


    @commands.command()
    async def coinflip(self, ctx):
        await ctx.send("Tails!" if (0.5 < random.random()) else "Head!")

    @commands.command()
    async def github(self, ctx):
        await ctx.send("https://github.com/sebakocz/parroting-parrot")

    @commands.command()
    async def support(selfs, ctx):
        await ctx.send("https://www.buymeacoffee.com/sevas")

    @commands.command()
    async def help(self, ctx):
        embed = discord.Embed(title="Commands", description="List of usable commands. Case sensitive.", color=0x2eaed4)

        embed.add_field(name="!top10", value="Shows a list of the top10 cards from current voting week.")
        embed.add_field(name="!updates", value="Shows a list of updates from current voting week.")
        embed.add_field(name="!stats", value="Shows playrates and winrates.")
        embed.add_field(
            name='!submit card_link "optional card text, default is empty" [submit type, default is [Card]]',
            value="Submits a card to the subreddit.")
        embed.add_field(name="!art card_link", value="Returns the full image used for the card art.")
        embed.add_field(name="!artToCard", value="Creates an empty card. (Attach an image to the same message.)")
        embed.add_field(name="!parrot sentence", value="Repeats the sentence.")
        embed.add_field(name="!coinflip", value="Flips a coin. Returns either 'Tails' or 'Head'.")
        embed.add_field(name="!github", value="Shows Parrot's code.")
        embed.add_field(name="!support", value="Sevas also accepts love, food and shelter.")

        await ctx.send(embed=embed)

        embed = discord.Embed(title="Fetcher", description="You can fetch heroes and cards from Collective as well as other card games. Names don't have to be accurate and the fetcher will try to find something relating.", color=0x2eaed4)

        embed.add_field(name="[[name]]", value="a non-token card from Collective")
        embed.add_field(name="[[tk:name]]", value="a token card from Collective")
        embed.add_field(name="[[hero:name]]", value="a hero from Collective")
        embed.add_field(name="[[sub:name]]", value="a card from Collective's subreddit")
        embed.add_field(name="[[mtg:name]]", value="Magic the Gathering")
        embed.add_field(name="[[et:name]]", value="Eternal")
        embed.add_field(name="[[ygo:name]]", value="Yugioh")
        embed.add_field(name="[[hs:name]]", value="Hearthstone")
        embed.add_field(name="[[kf:name]]", value="Keyforge")
        embed.add_field(name="[[lor:name]]", value="Legends of Runeterra")

        await ctx.send(embed=embed)


async def setup(bot):  # an extension must have a setup function
    await bot.add_cog(MiscCog(bot))  # adding a cog
