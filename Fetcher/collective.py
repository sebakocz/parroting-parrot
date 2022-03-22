import json

import discord
import requests
from Fetcher import dict_fetcher


class CollectiveFetcher(dict_fetcher.DictFetcher):
    """
    This fetches every collective card that is not undraftable (requested by toukkan)
    """

    def __init__(self):
        cards = {}
        # every card ingame is stored here
        request_url = 'https://server.collective.gg/api/public-cards/'
        for card_info in requests.get(request_url).json()['cards']:
            # some old cards don't have an image link
            if card_info['imgurl'] is not None and card_info['rarity'] != "Undraftable":
                cards[card_info['name'].lower()] = card_info['imgurl']
        super().__init__(cards)


class CollectiveTokenFetcher(dict_fetcher.DictFetcher):
    """
    This fetches every collective card that is undraftable (aka a token).
    (requested by toukkan)
    """

    def __init__(self):
        cards = {}
        # every card ingame is stored here
        request_url = 'https://server.collective.gg/api/public-cards/'
        for card_info in requests.get(request_url).json()['cards']:
            # some old cards don't have an image link
            if card_info['imgurl'] is not None and card_info['rarity'] == "Undraftable":
                cards[card_info['name'].lower()] = card_info['imgurl']
        super().__init__(cards)


class CollectiveAnyFetcher(dict_fetcher.DictFetcher):
    """
    This fetches any collective card that exists inside the game
    """

    def __init__(self):
        cards = {}
        # every card ingame is stored here
        request_url = 'https://server.collective.gg/api/public-cards/'
        for card_info in requests.get(request_url).json()['cards']:
            # some old cards don't have an image link
            if card_info['imgurl'] is not None:
                cards[card_info['name'].lower()] = card_info['imgurl']
        super().__init__(cards)

class CollectiveHeroFetcher(dict_fetcher.DictFetcher):
    """
    this fetches hero info displayed in an embed
    """

    def __init__(self):
        heros = {}
        with open('Data/heros.json') as heros_file:
            heros_json = json.load(heros_file)["heros"]
            for hero in heros_json:
                embed = discord.Embed(title=hero["name"],
                                      description=f"Passive: {hero['passive']}",
                                      color=self.getColor(hero["affinity"]))
                embed.set_thumbnail(url=f"https://www.collective.gg/emotes/{hero['name'].lower().replace(' ', '')}_thumb.png")

                counter = 1
                for key, lvl in hero["rewards"].items():
                    counter += 1
                    embed.add_field(name=f"Level {counter} - {lvl['exp']} EXP",
                                    value=lvl["text"], inline=False)

                heros[hero["name"].lower()] = embed

            super().__init__(heros)

    def getColor(self, affinity):
        colors = {
            "Neutral": discord.Color.light_grey(),
            "Strength": discord.Color.dark_red(),
            "Mind": discord.Color.dark_blue(),
            "Spirit": discord.Color.dark_green()
        }
        return colors[affinity]