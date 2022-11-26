from collections import deque
from typing import List

import discord
from discord import ui, Embed, Interaction

from Utils import constants


class EmbedPaginatorView(ui.View):
    def __init__(self, embeds: List[Embed]):
        self._embeds = embeds
        self._queue = deque(embeds)
        self._initial = embeds[0]
        self._len = len(embeds)
        self.response = None

        super().__init__(timeout=60 * 3)

    async def on_timeout(self):
        for child in self.children:
            child.disabled = True

        embed = discord.Embed(
            title="This view has timed out.",
            description="Just call the command again to get a new view!",
            color=constants.EMBED_COLOR,
        )

        await self.response.edit(view=self, embed=embed)

    @ui.button(emoji="\N{LEFTWARDS BLACK ARROW}")
    async def previous_embed(self, interaction: Interaction, _):
        self._queue.rotate(1)
        await interaction.response.edit_message(embed=self._queue[0])

    @ui.button(emoji="\N{BLACK RIGHTWARDS ARROW}")
    async def next_embed(self, interaction: Interaction, _):
        self._queue.rotate(-1)
        await interaction.response.edit_message(embed=self._queue[0])

    @property
    def initial(self) -> Embed:
        return self._initial
