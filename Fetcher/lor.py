from Fetcher import dict_fetcher
import requests


class LorFetcher(dict_fetcher.DictFetcher):

    def __init__(self):
        card_set = {}
        for set in range(1,6):
            for card in requests.get(self.card_set_url(set)).json():
                if card["rarity"] != "None":
                    card_set[card['name']] = card['assets'][0]["gameAbsolutePath"]
        return super().__init__(card_set)

    def card_set_url(self, set):
        """
        returns a correct url based on which set is being used
        """

        return f"http://dd.b.pvp.net/latest/set{set}/en_us/data/set{set}-en_us.json"
