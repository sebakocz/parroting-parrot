import json
import Utils.collectiveApi


async def set_challenge_cards():
    cards = await Utils.collectiveApi.fetch_random_cards()
    with open('Data/challenge_cards.json', 'w') as outfile:
        json.dump(cards, outfile)