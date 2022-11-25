from collections import deque
from typing import List

from discord import ui, Embed, Interaction


class EmbedPaginatorView(ui.View):
    def __init__(self, embeds: List[Embed]):
        self._embeds = embeds
        self._queue = deque(embeds)
        self._initial = embeds[0]
        self._len = len(embeds)

        super().__init__(timeout=90)

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
