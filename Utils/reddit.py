import calendar
import re
import requests
import os
import json
import praw
import datetime
import time
from enum import Enum

import Utils.collectiveApi

class PostType(Enum):
    # PostType.value returns the strings
    CARD = "[Card]"
    UPDATE = "[Update]"
    DC = "[DC]"

def getSubreddit():
    reddit = praw.Reddit(client_id=os.getenv("REDDIT_CLIENT_ID"),
                         client_secret=os.getenv("REDDIT_API_SECRET"),
                         username=os.getenv("REDDIT_USERNAME"),
                         password=os.getenv("REDDIT_PASSWORD"),
                         user_agent="DraftingParrot - bot by Sevas",
                         redirect_uri="https://www.collective.gg/",
                         refresh_token="XXXXXXXXXXXXXXXX")

    subreddit = reddit.subreddit(os.getenv("REDDIT_SUBREDDIT"))

    return subreddit

def getLastWeekUnixStamp():
    # https://stackoverflow.com/questions/1622038/find-mondays-date-with-python
    # get last Wednesday Midnight PST stamp depending on which day is today
    # transfer to UTC in order to work on local machine as well as server in the same manner
    today = datetime.datetime.utcnow().replace(hour=0, minute=0, second=0, microsecond=0)
    stamp = today - datetime.timedelta(days=(today.weekday() + 4) % 7)

    # convert to Unix
    # UTC is 7 hours ahead of PST
    unix_stamp = calendar.timegm(stamp.timetuple()) + 7 * 3600

    # Debug
    # print("getLastWeekUnixStamp() DEBUG")
    # print(f"Today: {today}")
    # print(f"Delta: {datetime.timedelta(days=(today.weekday()+4)%7)}")
    # print(f"Stamp: {stamp}")
    # print((f"Unix: {unix_stamp}"))

    return unix_stamp

def submit(card_link, optional_text="", type="[Card]"):
    # 1. get the card's name from the json data
    # 2. combine card's name and the type (Update, DC, standard=Card) and optional text to create a post
    # ie.: title="[Card] Ila, Seeker of Futures (New cool card!)" url=https://files.collective.gg/p/cards/91c64410-2874-11ec-a560-3dfd4d1fd4c0-m.png

    card_json = Utils.collectiveApi.jsonFromLink(card_link)
    card_name = card_json["Text"]["Name"]

    subreddit = getSubreddit()

    title = f'{type} {card_name}'
    if (optional_text != ""):
        title += f" ({optional_text})"

    subreddit.submit(title, url=card_link)

def fetchPosts(type):

    unix_stamp = getLastWeekUnixStamp()

    subreddit = getSubreddit()

    posts= []
    for post in subreddit.top(time_filter="week"):
        # Debug
        # print(post.title)
        # print(post.created)
        if(type.value in post.title and post.created > unix_stamp):
            posts.append(post)

    posts.sort(key=lambda x: x.score, reverse=True)

    return posts
