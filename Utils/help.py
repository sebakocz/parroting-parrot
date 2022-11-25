# custom !help command
import discord
from discord.ext import commands

import constants
from Fetcher.fetcher_list import FetcherList


class CustomHelpCmd(commands.HelpCommand):
    async def send_bot_help(self, mapping):
        filtered = await self.filter_commands(
            [command for command in self.context.bot.commands if command.description],
            sort=True,
        )

        embed = discord.Embed(
            title="Commands",
            description="List of usable commands. Case sensitive.",
            color=constants.EMBED_COLOR,
        )
        for command in filtered:
            embed.add_field(
                name=f"/{command.name} {command.signature}",
                value=command.description,
                inline=False,
            )

        await self.context.send(embed=embed)

        if self.context.bot.get_cog("FetcherCog"):
            embed = discord.Embed(
                title="Fetcher",
                description="You can fetch heroes and cards from Collective as well as other card games. Names don't have to be accurate and the fetcher will try to find something relating.",
                color=constants.EMBED_COLOR,
            )

            for fetcher in FetcherList.all:
                embed.add_field(
                    name=f"[[{fetcher.mod+':' if fetcher.mod else ''}name]]",
                    value=fetcher.description,
                    inline=False,
                )

            await self.context.send(embed=embed)
