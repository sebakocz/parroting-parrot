import json
import os
import random
import datetime
from itertools import cycle

import discord
from discord.ext import commands, tasks
from discord import app_commands

import Utils.collectiveApi
import Utils.collective_db
import Utils.collective_misc
import Utils.tenor_api


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
