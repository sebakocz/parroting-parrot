import discord
from discord.ext import commands
from discord import app_commands, Interaction
import Utils.Collective.api
from Utils import constants
from Utils.Views.embed_paginator import EmbedPaginatorView


class CardCog(commands.GroupCog, name="card"):
    def __init__(self, bot):
        self.bot = bot

    @app_commands.command(name="show_art", description="show the art of a card")
    @app_commands.describe(
        card_link="example: https://files.collective.gg/p/cards/388074b0-ee36-11ec-82cc-cfdbb9e62095-s.png"
    )
    async def show_art(self, interaction: Interaction, card_link: str):
        await interaction.response.defer()
        try:
            art = Utils.Collective.api.get_art(card_link)
            await interaction.followup.send(art)
        except Exception as e:
            print(e)
            await interaction.followup.send("Something went wrong.")

    @app_commands.command(name="from_art", description="Creates an empty card")
    @app_commands.describe(image="Attach an image to the same message")
    async def from_art(self, interaction: Interaction, image: discord.Attachment):
        try:
            await interaction.response.defer()
            await interaction.followup.send(
                Utils.Collective.api.art_to_card(image.proxy_url)
            )
        except Exception as e:
            print("Error in art_to_card: ", e)
            await interaction.followup.send("Something went wrong...")

    @app_commands.command(name="examine", description="View a card's external cards.")
    @app_commands.describe(
        card_link="example: https://files.collective.gg/p/cards/388074b0-ee36-11ec-82cc-cfdbb9e62095-s.png"
    )
    async def examine(self, interaction: Interaction, card_link: str):
        await interaction.response.defer()

        try:
            externals = Utils.Collective.api.get_externals(card_link)

            embeds = []
            for index, external in enumerate(externals):
                embed = discord.Embed(
                    title=external["name"],
                    url=external["imgurl"],
                    description=f"{index + 1}/{len(externals)}",
                    color=constants.EMBED_COLOR,
                )
                embed.set_image(url=external["imgurl"])
                embeds.append(embed)

            view = EmbedPaginatorView(embeds)

            out = await interaction.followup.send(embed=view.initial, view=view)
            view.response = out

        except Exception as e:
            await interaction.followup.send(
                "Something went wrong. Maybe the card has no externals?"
            )
            return

    @commands.command()
    async def art_to_card(self, ctx):
        """Deprecated"""
        await ctx.send("Deprecated. Use `/card from_art` instead.")

    @commands.command()
    async def art(self, ctx):
        """deprecated"""
        await ctx.send("Deprecated. Use card `/card show_art` instead.")


async def setup(bot):  # an extension must have a setup function
    await bot.add_cog(CardCog(bot))  # adding a cog
