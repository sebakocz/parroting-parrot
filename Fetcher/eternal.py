import requests
from Fetcher import dict_fetcher


def get_card_json():
    """
    This method downloads the json file from the eternal warcry website
    """
    return requests.get("https://eternalwarcry.com/content/cards/eternal-cards.json").json()


def filter_card_json(warcry_json):
    """
    this method takes the warcry json and formats it to fit our needs.
    """
    cards = {}
    for card_info in warcry_json:
        cards[card_info['Name']] = card_info['ImageUrl']
    return cards


class EternalFetcher(dict_fetcher.DictFetcher):

    def __init__(self):
        super().__init__(filter_card_json(get_card_json()))