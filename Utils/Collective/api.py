import json
import os
import random
import re
from datetime import datetime, timedelta

import aiohttp
import dateutil.parser
import requests

from Utils.constants import COLLECTIVE_API_BASE_URL


def get_uid_from_url(url):
    uid = re.search(
        r"[0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{12}", url
    ).group(0)
    return uid


def get_url_from_uid(uid):
    api_request = requests.get(f"{COLLECTIVE_API_BASE_URL}/card/{uid}")
    try:
        externals = json.loads(api_request.text)["externals"]
    except KeyError:
        externals = []

    # create card_link
    # suffix -m or -s is based on whether the card has externals
    if len(externals) > 0:
        externals_suffix = "-m"
    else:
        externals_suffix = "-s"

    return f"https://files.collective.gg/p/cards/{uid}{externals_suffix}.png"


def json_from_link(card_link, head="card"):
    # 1. extract ID from the card link
    # 2. use ID to get the card's json data via an API call
    card_id = re.search("(?<=/p/cards/)(.*?)(?=...png)", card_link)
    api_request = requests.get(f"{COLLECTIVE_API_BASE_URL}/card/{card_id.group()}")
    card_json = json.loads(api_request.text)[head]
    return card_json


def get_externals(card_link):
    cards = json_from_link(card_link, "externals")
    return cards


def find_property(properties, target):
    for json_property in properties:
        if json_property["Symbol"]["Name"] == target:
            return json_property["Expression"]["Value"]
    raise ValueError(f"Property not found: {target}")


def get_art(card_link):
    card = json_from_link(card_link)
    art = find_property(card["Text"]["Properties"], "PortraitUrl")
    return art


def login():
    # session is required for authentication
    session = requests.Session()

    login_url = f"{COLLECTIVE_API_BASE_URL}/auth/login"

    login_data = {
        "email": os.getenv("COLLECTIVE_EMAIL"),
        "password": os.getenv("COLLECTIVE_PASSWORD"),
        "username": "",
    }

    session.post(login_url, data=login_data)

    return session


def art_to_card(art_link):
    submit_url = f"{COLLECTIVE_API_BASE_URL}/submit-card"

    session = login()

    card_json = (
        '{"Text":{"Name":"Card Name","Rarity":"Common","ObjectType":"Action","PlayAbility":{"Properties":[{"Symbol":{"Name":"AbilityText","Type":{"RootType":"String","Multiple":false},"Readonly":false},"Expression":{"$type":"StringLiteral","Value":""}}],"Statements":[],"$type":"Ability","Type":"Active","Parent":{"$type":"Predefines.PlaySpell"}},"Properties":[{"Symbol":{"Name":"IGOCost","Type":{"RootType":"Number","Multiple":false},"Readonly":false},"Expression":{"$type":"NumberLiteral","Value":1}},{"Symbol":{"Name":"TribalType","Type":{"RootType":"String","Multiple":false},"Readonly":false},"Expression":{"$type":"StringLiteral","Value":"Tribal Type"}},{"Symbol":{"Name":"CreatorName","Type":{"RootType":"String","Multiple":false},"Readonly":false},"Expression":{"$type":"StringLiteral","Value":"(Card Designer Name)"}},{"Symbol":{"Name":"ArtistName","Type":{"RootType":"String","Multiple":false},"Readonly":false},"Expression":{"$type":"StringLiteral","Value":"(Card Artist Name)"}},{"Symbol":{"Name":"PortraitUrl","Type":{"RootType":"String","Multiple":false},"Readonly":false},"Expression":{"$type":"StringLiteral","Value":"'
        + art_link
        + '"}}],"CustomSymbols":[],"Abilities":[],"Affinity":"None","AffinityExclusive":false,"ExternalCardReferences":[]},"collaborators":[]}'
    )

    card_data = {"card": card_json}

    # print(card_data)

    submit_post = session.post(submit_url, data=card_data)
    # print(json.loads(submit_post.text)["redditLink"])

    return json.loads(submit_post.text)["redditLink"]


def fetch_random_card_names():
    # names fetching for bot activity
    # get a pool of 100 random card names from public cards api

    request_url = f"{COLLECTIVE_API_BASE_URL}/public-cards/"

    cards = []
    for card_info in requests.get(request_url).json()["cards"]:
        cards.append(card_info["name"])

    cards = random.sample(cards, 100)

    return cards


async def fetch_random_cards():
    async with aiohttp.ClientSession() as session:
        async with session.get(f"{COLLECTIVE_API_BASE_URL}/public-cards/") as response:
            return random.sample(
                [
                    card
                    for card in json.loads(await response.text())["cards"]
                    if card["approval_state"] == 0
                    and datetime.today().replace(day=1) - timedelta(days=10)
                    > dateutil.parser.isoparse(card["dtreleased"]).replace(tzinfo=None)
                    and card["rarity"] != "Undraftable"
                ],
                3,
            )
