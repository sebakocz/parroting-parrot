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

        new_embed = self._initial
        new_embed.set_footer(
            text="This view has timed out. Just call the command again to re-enable it!"
        )

        await self.response.edit(view=self, embed=new_embed)

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
