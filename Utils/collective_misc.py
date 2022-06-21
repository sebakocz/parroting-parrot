import json
import Utils.collectiveApi


async def setChallengeCards():
    cards = await Utils.collectiveApi.fetchRandomCards()
    with open('Data/challenge_cards.json', 'w') as outfile:
        json.dump(cards, outfile)