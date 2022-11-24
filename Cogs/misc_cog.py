import json
import random
import datetime
from itertools import cycle

import discord
from discord.ext import commands, tasks
from discord import app_commands

import Utils.reddit
import Utils.collectiveApi
import Utils.collective_db
import Utils.collective_misc
import Utils.tenor_api

from Utils.reddit import submit


class MiscCog(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

        # update card names list
        self.card_list = cycle(Utils.collectiveApi.fetch_random_card_names())

    @commands.Cog.listener()
    async def on_ready(self):
        self.task_change_activity.start()
        self.task_reset_challenge.start()

    @tasks.loop(seconds=10)
    async def task_change_activity(self):
        await self.bot.change_presence(activity=discord.Game(next(self.card_list)))

    @commands.hybrid_command(
        name="week", description="Shows when the submission week is over"
    )
    @app_commands.describe(week_number="X weeks away from ongoing week")
    async def week(self, ctx, week_number="1"):
        if week_number == "last".lower():
            week_number = 0
        if week_number == "next".lower():
            week_number = 2
        await ctx.send(f"<t:{Utils.reddit.get_week_unix_stamp(int(week_number))}>")

    @commands.hybrid_command(name="parrot", description="Repeats the sentence")
    @app_commands.describe(sentence="type something for parrot to repeat")
    async def parrot(self, ctx, *, sentence):
        await ctx.send(f"> {sentence}")

    @commands.hybrid_command(
        name="art_to_card",
        description="Creates an empty card (Attach an image to the same message)",
    )
    async def art_to_card(self, ctx, image: discord.Attachment):

        try:
            await ctx.defer()
            await ctx.send(Utils.collectiveApi.art_to_card(image.proxy_url))
        except Exception as e:
            print("Error in art_to_card: ", e)
            await ctx.send("Something went wrong...")

    @commands.hybrid_command(
        name="art", description="Returns the full image used for the card art"
    )
    @app_commands.describe(
        card_link="example: https://files.collective.gg/p/cards/388074b0-ee36-11ec-82cc-cfdbb9e62095-s.png"
    )
    async def art(self, ctx, card_link):
        try:
            art = Utils.collectiveApi.get_art(card_link)
            await ctx.send(art)
        except Exception as e:
            print(e)
            await ctx.send("Something went wrong.")

    @commands.hybrid_command(
        name="submit", description="Submits a card to the subreddit"
    )
    @app_commands.describe(
        card_link="example: https://files.collective.gg/p/cards/388074b0-ee36-11ec-82cc-cfdbb9e62095-s.png",
        optional_text="optional text displayed in parentheses",
        submission_type="optional type like [Card], [DC], [Legacy Update] or [Standard Update] - default is [Card]",
    )
    async def submit(
        self,
        ctx,
        card_link,
        optional_text="",
        submission_type: Utils.reddit.PostType = Utils.reddit.PostType.CARD,
    ):
        # Grief's request: limit submissions to the submission channel
        if ctx.channel.id != 430071237104893964:
            await ctx.send("Please use the submission channel for submissions.")
            return
        await submit(card_link, optional_text, submission_type.value)
        await ctx.send("Submitted!")

    @commands.hybrid_command(
        name="updates", description="Shows a list of updates from current voting week"
    )
    async def updates(self, ctx):
        top10card = None
        await ctx.defer()
        cards = await Utils.reddit.fetch_posts(Utils.reddit.PostType.CARD)

        updates = await Utils.reddit.fetch_posts(Utils.reddit.PostType.STANDARD_UPDATE)
        text = f"Total Standard Updates: {len(updates)}\n\n"

        try:
            top10card = cards[9]
        except IndexError:
            if len(cards) > 0:
                top10card = cards[-1]

        if len(cards) > 0:
            text += f"PS: Top 10 voted [Card] currently is at {top10card.score} votes! ({top10card.title})\n\n"
        for post in updates:
            # slice "[Update]" away
            text += f"{post.title[18:]}\nScore: {post.score}\n\n"

        if len(text) >= 2000:
            with open("Data/stats_result.txt", "w") as file:
                file.write(text)
            # await ctx.send(file=discord.File("Data/stats_result.txt"))
            await ctx.send("", file=discord.File("Data/stats_result.txt"))
        else:
            text = "```" + text + "```"
            await ctx.send(text)

    # TODO: refactor this, I just copy & pasted updates, this should be more modular but I'm tired now
    @commands.hybrid_command(name="legacyupdates", description="Legacy Updates")
    async def legacyupdates(self, ctx):
        top10card = None
        await ctx.defer()
        cards = await Utils.reddit.fetch_posts(Utils.reddit.PostType.CARD)

        updates = await Utils.reddit.fetch_posts(Utils.reddit.PostType.LEGACY_UPDATE)
        text = f"Total Legacy Updates: {len(updates)}\n\n"

        try:
            top10card = cards[9]
        except IndexError:
            if len(cards) > 0:
                top10card = cards[-1]

        if len(cards) > 0:
            text += f"PS: Top 10 voted [Card] currently is at {top10card.score} votes! ({top10card.title})\n\n"
        for post in updates:
            # slice "[Update]" away
            text += f"{post.title[16:]}\nScore: {post.score}\n\n"

        if len(text) >= 2000:
            with open("Data/stats_result.txt", "w") as file:
                file.write(text)
            await ctx.send("", file=discord.File("Data/stats_result.txt"))
        else:
            text = "```" + text + "```"
            await ctx.send(text)

    @commands.hybrid_command(
        name="top10",
        description="Shows a list of the top10 cards from current voting week",
    )
    async def top10(self, ctx):
        await ctx.defer()
        cards = await Utils.reddit.fetch_posts(Utils.reddit.PostType.CARD)

        if len(cards) <= 0:
            await ctx.send("No cards found for this week. Go post some!")
            return

        text = ""
        for post in cards[:9]:
            # slice "[Card]" away
            text += f"{post.title[7:]}\nScore: {post.score}\n\n"
        text = "```" + text + "```"

        await ctx.send(text)

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

    # credits to Gokun for the idea
    @commands.hybrid_command(
        name="daily_challenge", description="Shows today's brew challenge"
    )
    async def daily_challenge(self, ctx):
        text = "**Daily Brew Challenge**\n"

        with open("Data/challenge_players.txt") as file:
            lines = file.readlines()
            lines = [line.rstrip() for line in lines]
        if len(lines) > 0:
            text += "\nToday's Challengers:"
            for line in lines:
                text += f"\n{line}"
        else:
            text += "\nNobody finished this quest yet! Be the first one!"

        text += "\n\nWin a multiplayer game while having x3 copies of each of the following cards."

        with open("Data/challenge_cards.json") as json_file:
            cards = json.load(json_file)
        for card in cards:
            text += "\n" + card["imgurl"]
            # embed = discord.Embed(title=card['name'], color=0x2eaed4)
            # embed.set_image(url=)
            # await ctx.send(embed=embed)
        await ctx.send(text)

    @tasks.loop(time=datetime.time(hour=6, minute=30))
    async def task_reset_challenge(self):
        open("Data/challenge_players.txt", "w").close()
        await Utils.collective_misc.set_challenge_cards()

    @commands.Cog.listener()
    async def on_message(self, msg):
        if msg.channel.id == 655541513740091393 and msg.author.id == 651119952748871694:
            embed_content_in_dict = msg.embeds[0].to_dict()
            match_id = embed_content_in_dict["footer"]["text"]
            deck = Utils.collective_db.get_deck_from_match(match_id)

            with open("Data/challenge_cards.json") as json_file:
                challenge_cards = json.load(json_file)
            for card in challenge_cards:
                if 3 > deck.count(card["uid"]):
                    print("Non-Challenge Deck Winner: " + match_id)
                    return
            print("Challenge Deck Winner Found! " + match_id)

            player_name = embed_content_in_dict["fields"][0]["name"]
            with open("Data/challenge_players.txt", "r") as file:
                for line in file:
                    if player_name in line:
                        return
            with open("Data/challenge_players.txt", "a") as outfile:
                outfile.write("\n" + player_name)

            # tried to make it work via api but sadly the api doesn't get updated quickly enough
            # session = Utils.collectiveApi.login()
            # winner_id = \
            # session.get(f'https://server.collective.gg/api/users/search?query={winner}').json()['result']['id']
            # print(winner_id)

    @commands.hybrid_command(name="gif", description="Shows a random parrot")
    async def gif(self, ctx):
        await ctx.send(Utils.tenor_api.get_random_parrot_gif())


async def setup(bot):  # an extension must have a setup function
    await bot.add_cog(MiscCog(bot))  # adding a cog
