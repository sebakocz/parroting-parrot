import json
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
