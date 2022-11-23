import requests
from Fetcher import dict_fetcher


class KeyforgeFetcher(dict_fetcher.DictFetcher):
    """
    This fetches every keyforge card (requested by ThriftyFishin)
    """

    def __init__(self):
        cards = {}
        request_url = "https://www.keyforgegame.com/api/decks/?links=cards"
        for card_info in requests.get(request_url).json()["_linked"]["cards"]:
            cards[card_info["card_title"].lower()] = card_info["front_image"]
        super().__init__(cards)
