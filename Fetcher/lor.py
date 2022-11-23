from Fetcher import dict_fetcher
import requests


def card_set_url(card_set):
    """
    returns a correct url based on which set is being used
    """

    return f"https://dd.b.pvp.net/latest/set{card_set}/en_us/data/set{card_set}-en_us.json"


class LorFetcher(dict_fetcher.DictFetcher):

    def __init__(self):
        # fetch a list of all available sets
        # pick the "sets" value from globals json
        globals_sets = requests.get("https://dd.b.pvp.net/latest/core/en_us/data/globals-en_us.json").json()["sets"]

        # this code been working with following json syntax: "nameRef": "Set3"
        # exclude unreachable sets like: "nameRef": "SetEvent"
        # this part might cause in error in the future if syntax changes
        sets_range = []
        for card_set in globals_sets:
            if "Set" in card_set["nameRef"]:
                set_suffix = card_set["nameRef"][3:]
                if set_suffix.isnumeric():
                    sets_range.append(set_suffix)

        # go through each set, previously the range been set manually
        # this uses official riot api - https://developer.riotgames.com/docs/lor#data-dragon
        cards = {}
        for card_set in sets_range:
            for card in requests.get(card_set_url(card_set)).json():
                if card["rarity"] != "None":
                    cards[card['name']] = card['assets'][0]["gameAbsolutePath"]
        super().__init__(cards)