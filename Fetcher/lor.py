from Fetcher import dict_fetcher
import requests


class LorFetcher(dict_fetcher.DictFetcher):

    def __init__(self):
        # fetch a list of all available sets
        # pick the "sets" value from globals json
        globals_sets = requests.get("https://dd.b.pvp.net/latest/core/en_us/data/globals-en_us.json").json()["sets"]

        # this code been working with following json syntax: "nameRef": "Set3"
        # exclude unreachable sets like: "nameRef": "SetEvent"
        sets_range = []
        for set in globals_sets:
            if "Set" in set["nameRef"]:
                set_suffix = set["nameRef"][3:]
                if(set_suffix.isnumeric()):
                    sets_range.append(set_suffix)

        # go through each set, previously the range been set manually
        # this uses official riot api - https://developer.riotgames.com/docs/lor#data-dragon
        card_set = {}
        for set in sets_range:
            for card in requests.get(self.card_set_url(set)).json():
                if card["rarity"] != "None":
                    card_set[card['name']] = card['assets'][0]["gameAbsolutePath"]
        return super().__init__(card_set)

    def card_set_url(self, set):
        """
        returns a correct url based on which set is being used
        """

        return f"http://dd.b.pvp.net/latest/set{set}/en_us/data/set{set}-en_us.json"
