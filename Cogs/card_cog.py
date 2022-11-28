import discord
from discord.ext import commands
from discord import app_commands
import Utils.Collective.api


class CardCog(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.hybrid_group(name="card", description="card related utilities")
    async def card(self, ctx):
        pass

    @card.command(name="show_art", description="show the art of a card")
    @app_commands.describe(
        card_link="example: https://files.collective.gg/p/cards/388074b0-ee36-11ec-82cc-cfdbb9e62095-s.png"
    )
    async def show_art(self, ctx, card_link):
        async def art(self, ctx, card_link):
            try:
                art = Utils.Collective.api.get_art(card_link)
                await ctx.send(art)
            except Exception as e:
                print(e)
                await ctx.send("Something went wrong.")

    @card.command(name="from_art", description="Creates an empty card")
    @app_commands.describe(image="Attach an image to the same message")
    async def from_art(self, ctx, image: discord.Attachment):
        try:
            await ctx.defer()
            await ctx.send(Utils.Collective.api.art_to_card(image.proxy_url))
        except Exception as e:
            print("Error in art_to_card: ", e)
            await ctx.send("Something went wrong...")

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
