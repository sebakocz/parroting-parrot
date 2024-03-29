# fetching, submitting and anything else you can do with reddit
import os

from discord import app_commands, Embed, Interaction
from discord.ext import commands
import Utils.reddit
from Utils import constants
from Utils.Views.embed_paginator import EmbedPaginatorView
from Utils.reddit import submit

isDev = os.getenv("DEV") == "True"


class RedditCog(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

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
        if ctx.channel.id != 430071237104893964 and not isDev:
            await ctx.send("Please use the submission channel for submissions.")
            return
        link = await submit(card_link, optional_text, submission_type.value)
        await ctx.send(link)

    @app_commands.command(
        name="showsub", description="Shows a list of reddit submissions of given type"
    )
    @app_commands.describe(
        submission_type="optional type like [Card], [DC], [Legacy Update] or [Standard Update] - default is [Card]",
    )
    async def showsub(
        self,
        interaction: Interaction,
        submission_type: Utils.reddit.PostType = Utils.reddit.PostType.CARD,
    ):

        top10card = None
        await interaction.response.defer()

        target_posts = await Utils.reddit.fetch_posts(submission_type)

        # # fetch normal cards since we use the top 10th card as point of reference
        # normal_card_posts = await Utils.reddit.fetch_posts(Utils.reddit.PostType.CARD)
        #
        # # prevent calling reddit twice
        # if submission_type != Utils.reddit.PostType.CARD:
        #     target_posts = await Utils.reddit.fetch_posts(submission_type, -weeks_ago)
        # else:
        #     target_posts = normal_card_posts

        # no cards?
        if len(target_posts) <= 0:
            await interaction.followup.send(
                f"No {submission_type.value} cards found for this week. Go post some!"
            )
            return

        # build output
        post_embeds = []

        # front page with top 10 cards
        top_10_posts = target_posts[:10]
        front_page_embed = Embed(
            title=f"Top 10 {submission_type.value}s of the week",
            description="Click on the arrows to see the cards!",
            color=constants.EMBED_COLOR,
        )
        for post in top_10_posts:
            front_page_embed.add_field(
                name=f"({post.score} points)",
                value=f"[{post.title[len(submission_type.value)+1:]}]({post.url} '{post.url}')",
                inline=False,
            )
        post_embeds.append(front_page_embed)

        for index, post in enumerate(target_posts):
            embed = Embed(
                title=post.title,
                description=f"{index + 1}/{len(target_posts)} | Score: {post.score}",
                url=f"{constants.REDDIT_BASE_URL}{post.permalink}",
                color=constants.EMBED_COLOR,
            )
            embed.set_image(url=post.url)
            embed.set_footer(text=f"by {post.author}")
            post_embeds.append(embed)

        view = EmbedPaginatorView(post_embeds)
        out = await interaction.followup.send(embed=view.initial, view=view)
        view.response = out

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

    @commands.command(name="updates")
    async def updates(self, ctx):
        await ctx.send("Deprecated. Use /showsub instead.")

    @commands.command(name="legacyupdates")
    async def legacyupdates(self, ctx):
        await ctx.send("Deprecated. Use /showsub instead.")

    @commands.command(name="top10")
    async def top10(self, ctx):
        await ctx.send("Deprecated. Use /showsub instead.")


async def setup(bot):  # an extension must have a setup function
    await bot.add_cog(RedditCog(bot))  # adding a cog
