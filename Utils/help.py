# custom !help command
import discord
from discord.ext import commands

from Fetcher.fetcher_list import FetcherList
from Utils import constants


class CustomHelpCmd(commands.HelpCommand):
    async def send_bot_help(self, mapping):
        info_embed = discord.Embed(
            title="Looking for help?",
            color=constants.EMBED_COLOR,
        )
        info_embed.add_field(
            name="Use slash commands instead!",
            value="Discord is moving away from the old way of using commands. Gets used to it! Press ``/`` to see the list of commands and browse through them.",
            inline=False,
        )

        info_embed.add_field(
            name="If you really still want to see all the commands...",
            value="[Link to full list of cmds](https://github.com/sebakocz/parroting-parrot/blob/master/COMMAND_LIST.md)",
            inline=False,
        )

        await self.context.send(embed=info_embed)
