# fetching, submitting and anything else you can do with reddit
import os

from discord import app_commands, Embed, Interaction
from discord.ext import commands
import Utils.reddit
import constants
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
        weeks_ago="optional number of weeks ago to show submissions from - default is 0",
    )
    async def showsub(
        self,
        interaction: Interaction,
        submission_type: Utils.reddit.PostType = Utils.reddit.PostType.CARD,
        weeks_ago: int = 0,
    ):
        # validate input
        if weeks_ago < 0:
            await interaction.response.send_message(
                "weeks_ago must be a positive number or zero", ephemeral=True
            )
            return

        top10card = None
        await interaction.response.defer()

        target_posts = await Utils.reddit.fetch_posts(submission_type, -weeks_ago)

        # # fetch normal cards since we use the top 10th card as point of reference
        # normal_card_posts = await Utils.reddit.fetch_posts(Utils.reddit.PostType.CARD)
        #
        # # prevent calling reddit twice
        # if submission_type != Utils.reddit.PostType.CARD:
        #     target_posts = await Utils.reddit.fetch_posts(submission_type, -weeks_ago)
        # else:
        #     target_posts = normal_card_posts

        # no cards?
        if weeks_ago == 0 and len(target_posts) <= 0:
            await interaction.followup.send(
                f"No {submission_type.value} cards found for this week. Go post some!"
            )
            return

        # build output
        post_embeds = []
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
        await interaction.followup.send(embed=view.initial, view=view)

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

    @commands.hybrid_command(name="updates")
    async def updates(self, ctx):
        await ctx.send("Deprecated. Use /showsub instead.")

    @commands.hybrid_command(name="legacyupdates")
    async def legacyupdates(self, ctx):
        await ctx.send("Deprecated. Use /showsub instead.")

    @commands.hybrid_command(name="top10")
    async def top10(self, ctx):
        await ctx.send("Deprecated. Use /showsub instead.")


async def setup(bot):  # an extension must have a setup function
    await bot.add_cog(RedditCog(bot))  # adding a cog
