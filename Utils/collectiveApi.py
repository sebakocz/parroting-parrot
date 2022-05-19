import json
import os
import random
import re
import requests

def jsonFromLink(card_link):
    card_id = re.search('(?<=/p/cards/)(.*?)(?=...png)', card_link)
    api_request = requests.get(f'https://server.collective.gg/api/card/{card_id.group()}')
    card_json = json.loads(api_request.text)["card"]
    return card_json


def findProperty(properties, target):
    for property in properties:
        if(property["Symbol"]["Name"] == target):
            return property["Expression"]["Value"]
    raise ValueError(f"Property not found: {target}")

def getArt(card_link):
    card = jsonFromLink(card_link)
    art = findProperty(card["Text"]["Properties"], "PortraitUrl")
    return art

def artToCard(art_link):
    # session is required for authentication
    session = requests.Session()

    login_url = 'https://server.collective.gg/api/auth/login'
    submit_url = 'https://server.collective.gg/api/submit-card'

    login_data = {
        "email": os.getenv("COLLECTIVE_EMAIL"),
        "password": os.getenv("COLLECTIVE_PASSWORD"),
        "username": ""
    }

    # login
    login_post = session.post(login_url, data=login_data)

    card_json = '{"Text":{"Name":"Card Name","Rarity":"Common","ObjectType":"Action","PlayAbility":{"Properties":[{"Symbol":{"Name":"AbilityText","Type":{"RootType":"String","Multiple":false},"Readonly":false},"Expression":{"$type":"StringLiteral","Value":""}}],"Statements":[],"$type":"Ability","Type":"Active","Parent":{"$type":"Predefines.PlaySpell"}},"Properties":[{"Symbol":{"Name":"IGOCost","Type":{"RootType":"Number","Multiple":false},"Readonly":false},"Expression":{"$type":"NumberLiteral","Value":1}},{"Symbol":{"Name":"TribalType","Type":{"RootType":"String","Multiple":false},"Readonly":false},"Expression":{"$type":"StringLiteral","Value":"Tribal Type"}},{"Symbol":{"Name":"CreatorName","Type":{"RootType":"String","Multiple":false},"Readonly":false},"Expression":{"$type":"StringLiteral","Value":"(Card Designer Name)"}},{"Symbol":{"Name":"ArtistName","Type":{"RootType":"String","Multiple":false},"Readonly":false},"Expression":{"$type":"StringLiteral","Value":"iamyoyoman"}},{"Symbol":{"Name":"PortraitUrl","Type":{"RootType":"String","Multiple":false},"Readonly":false},"Expression":{"$type":"StringLiteral","Value":"'+art_link+'"}}],"CustomSymbols":[],"Abilities":[],"Affinity":"None","AffinityExclusive":false,"ExternalCardReferences":[]},"collaborators":[]}'

    card_data = {"card": card_json}

    #print(card_data)

    submit_post = session.post(submit_url, data=card_data)
    # print(json.loads(submit_post.text)["redditLink"])

    return json.loads(submit_post.text)["redditLink"]

def fetchRandomCardNames():
    # names fetching for bot activity
    # get a pool of 100 random card names from public cards api

    request_url = 'https://server.collective.gg/api/public-cards/'

    cards = []
    for card_info in requests.get(request_url).json()['cards']:
        cards.append(card_info["name"])

    cards = random.sample(cards, 100)

    return cards
