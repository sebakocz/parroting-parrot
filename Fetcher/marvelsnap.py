import json

import discord
import requests
from Fetcher import dict_fetcher

class MarvelSnapFetcher(dict_fetcher.DictFetcher):
    """
    This fetches every Marvelsnap card
    """

    def __init__(self):
        cards = {}
        request_url = 'https://marvelsnap.pro/snap/do.php?cmd=getcards'
        for card_info in requests.get(request_url).json():
            cards[card_info] = self.getImg(card_info)
        super().__init__(cards)

    def getImg(self, card_name):
        return f"https://marvelsnapzone.com/wp-content/themes/blocksy-child/assets/media/cards/{card_name}.webp?v=20"