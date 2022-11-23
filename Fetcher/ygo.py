import requests

from Fetcher import dict_fetcher


class YugiohFetcher(dict_fetcher.DictFetcher):
    def __init__(self):
        cards = {}
        request_url = "https://db.ygoprodeck.com/api/v7/cardinfo.php"
        for card_info in requests.get(request_url).json()["data"]:
            cards[card_info["name"].lower()] = card_info["card_images"][0]["image_url"]
        super().__init__(cards)
