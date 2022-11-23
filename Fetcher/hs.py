from Fetcher import dict_fetcher
import requests


def get_card_art_link(card_id):
    """
    fetches a card image from hearthstonejson.com based on the id of the card.
    """
    return "https://art.hearthstonejson.com/v1/render/latest/enUS/256x/{}.png".format(card_id)


class HsFetcher(dict_fetcher.DictFetcher):

    def __init__(self):
        card_set = {}
        card_set_url = "https://api.hearthstonejson.com/v1/latest/enUS/cards.collectible.json"
        for card in requests.get(card_set_url).json():
            if not card['id'].startswith('HERO'):
                card_set[card['name']] = get_card_art_link(card['id'])
        super().__init__(card_set)