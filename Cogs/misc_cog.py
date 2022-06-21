import json
import random
from itertools import cycle

import discord
from discord.ext import commands, tasks
from discord import app_commands

import Utils.reddit
import Utils.googleSheet
import Utils.collectiveApi

from Utils.reddit import submit
import Data.command_descriptions as cmds


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


    @commands.hybrid_command(name="week", description=cmds.list["week"])
    @app_commands.describe(week_number="X weeks away from ongoing week")
    async def week(self, ctx, week_number="1"):
        if week_number == "last".lower():
            week_number = 0
        if week_number == "next".lower():
            week_number = 2
        await ctx.send(f"<t:{Utils.reddit.getWeekUnixStamp(int(week_number))}>")


    @commands.hybrid_command(name="parrot", description=cmds.list["parrot"])
    @app_commands.describe(sentence="type something for parrot to repeat")
    async def parrot(self, ctx, *, sentence):
        await ctx.send(f"> {sentence}")


    @commands.hybrid_command(name="art_to_card", description=cmds.list["art_to_card"])
    async def art_to_card(self, ctx, image: discord.Attachment):

        try:
            await ctx.defer()
            await ctx.send(Utils.collectiveApi.artToCard(image.proxy_url))
            # await ctx.send(Utils.collectiveApi.artToCard(ctx.message.attachments[0].url))
        except:
            await ctx.send("Something went wrong...")


    @commands.hybrid_command(name="art", description=cmds.list["art"])
    @app_commands.describe(card_link="example: https://files.collective.gg/p/cards/388074b0-ee36-11ec-82cc-cfdbb9e62095-s.png")
    async def art(self, ctx, card_link):
        try:
            art = Utils.collectiveApi.getArt(card_link)
            await ctx.send(art)
        except Exception as e:
            print(e)
            await ctx.send("Something went wrong.")


    @commands.hybrid_command(name="submit", description=cmds.list["submit"])
    @app_commands.describe(
        card_link="example: https://files.collective.gg/p/cards/388074b0-ee36-11ec-82cc-cfdbb9e62095-s.png",
        text="optional text displayed in parentheses",
        type="optional type like [Card], [DC] or [Update] - default is [Card]"
    )
    async def submit(self, ctx, card_link, text="", type: Utils.reddit.PostType = Utils.reddit.PostType.CARD):
        submit(card_link, text, type.value)
        await ctx.send("Submitted!")


    @commands.hybrid_command(name="updates", description=cmds.list["updates"])
    async def updates(self, ctx):
        await ctx.defer()
        cards = Utils.reddit.fetchPosts(Utils.reddit.PostType.CARD)

        updates = Utils.reddit.fetchPosts(Utils.reddit.PostType.UPDATE)

        text = f"Total Updates: {len(updates)}\n\n"

        try:
            top10card = cards[9]
        except IndexError:
            if len(cards) > 0:
                top10card = cards[-1]

        if len(cards) > 0:
            text += f"PS: Top 10 voted [Card] currently is at {top10card.score} votes! ({top10card.title})\n\n"
        for post in updates:
            # slice "[Update]" away
            text += f"{post.title[9:]}\nScore: {post.score}\n\n"

        text = "```" + text + "```"

        await ctx.send(text)


    @commands.hybrid_command(name="top10", description=cmds.list["top10"])
    async def top10(self, ctx):
        await ctx.defer()
        cards = Utils.reddit.fetchPosts(Utils.reddit.PostType.CARD)

        if len(cards) <= 0:
            await ctx.send("No cards found for this week. Go post some!")
            return

        text = ""
        for post in cards[:9]:
            # slice "[Card]" away
            text += f"{post.title[7:]}\nScore: {post.score}\n\n"
        text = "```" + text + "```"

        await ctx.send(text)


    @commands.hybrid_command(name="coinflip", description=cmds.list["coinflip"])
    async def coinflip(self, ctx):
        await ctx.send("Tails!" if (0.5 < random.random()) else "Head!")

    @commands.hybrid_command(name="github", description=cmds.list["github"])
    async def github(self, ctx):
        await ctx.send("https://github.com/sebakocz/parroting-parrot")

    @commands.hybrid_command(name="support", description=cmds.list["support"])
    async def support(selfs, ctx):
        await ctx.send("https://www.buymeacoffee.com/sevas")

    @commands.hybrid_command(name="help", description=cmds.list["help"])
    async def help(self, ctx):
        embed = discord.Embed(title="Commands", description="List of usable commands. Case sensitive.", color=0x2eaed4)

        embed.add_field(name="!top10", value=cmds.list["top10"])
        embed.add_field(name="!updates", value=cmds.list["updates"])
        embed.add_field(name="!stats", value=cmds.list["stats"])
        embed.add_field(name="!week <last|next|number>", value=cmds.list["week"])
        embed.add_field(
            name='!submit card_link <"card text, default is empty"> <[submit type, default is [Card]]>',
            value=cmds.list["submit"])
        embed.add_field(name="!art card_link", value=cmds.list["art"])
        embed.add_field(name="!art_to_card", value=cmds.list["art_to_card"])
        embed.add_field(name="!parrot sentence", value=cmds.list["parrot"])
        embed.add_field(name="!coinflip", value=cmds.list["coinflip"])
        embed.add_field(name="!github", value=cmds.list["github"])
        embed.add_field(name="!support", value=cmds.list["support"])

        await ctx.send(embed=embed)

        embed = discord.Embed(title="Fetcher",
                              description="You can fetch heroes and cards from Collective as well as other card games. Names don't have to be accurate and the fetcher will try to find something relating.",
                              color=0x2eaed4)

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

    @commands.Cog.listener()
    async def on_message(self, msg):
        if msg.channel.id == 655541513740091393 and msg.author.id == 651119952748871694:
            embed_content_in_dict = msg.embeds[0].to_dict()
            winner = embed_content_in_dict['fields']['name']
            session = Utils.collectiveApi.login()
            winner_id = \
            json.loads(session.get(f'https://server.collective.gg/api/users/search?query={winner}').text)['results'][
                'id']
            print(winner_id)

async def setup(bot):  # an extension must have a setup function
    await bot.add_cog(MiscCog(bot))  # adding a cog
