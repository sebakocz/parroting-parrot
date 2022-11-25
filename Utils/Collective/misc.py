import json
import Utils.Collective.api


async def set_challenge_cards():
    cards = await Utils.Collective.api.fetch_random_cards()
    with open("Data/challenge_cards.json", "w") as outfile:
        json.dump(cards, outfile)
