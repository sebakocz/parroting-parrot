import re

import requests
from slugify import slugify

from Fetcher import dict_fetcher


def get_img(card_name):
    return f"https://marvelsnapzone.com/wp-content/themes/blocksy-child/assets/media/cards/{card_name}.webp?v=20"


class MarvelSnapFetcher(dict_fetcher.DictFetcher):
    """
    This fetches every Marvelsnap card
    """

    def __init__(self):
        cards = {}
        request_url = "https://marvelsnap.pro/snap/do.php?cmd=getcards"
        for card_info in requests.get(request_url).json().values():
            # remove html markup from card description
            description = re.sub(r"<[^>]*>", "", card_info["description"])
            cards[
                card_info["name"]
            ] = f"_{description}_\n|{get_img(slugify(card_info['name']))}|"
        super().__init__(cards)
