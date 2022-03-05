import re
import requests
import os
import json
import praw
import datetime
import time

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

def submit(card_link, optional_text="", optional_type=""):
    card_id = re.search('(?<=/p/cards/)(.*?)(?=...png)', card_link)
    api_request = requests.get(f'https://server.collective.gg/api/card/{card_id.group()}')
    card_json = json.loads(api_request.text)

    card_name = card_json["card"]["Text"]["Name"]

    subreddit = getSubreddit()

    type = "[Card]" if optional_type == "" else optional_type
    title = f'{type} {card_name}'
    if (optional_text != ""):
        title += f" ({optional_text})"

    subreddit.submit(title, url=card_link)

def fetchUpdates():

    # https://stackoverflow.com/questions/1622038/find-mondays-date-with-python
    # added 3 to fetch from Fridays instead Mondays
    today = datetime.date.today()
    stamp = today - datetime.timedelta(days=(today.weekday()+4)%7)

    # convert to Unix
    unix_stamp = time.mktime(stamp.timetuple()) + 43200


    # # Debug
    print(f"Today: {today}")
    print(f"Delta: {datetime.timedelta(days=(today.weekday()+4)%7)}")
    print(f"Stamp: {stamp}")
    print((f"Unix: {unix_stamp}"))

    subreddit = getSubreddit()

    posts= []
    for post in subreddit.top(time_filter="week"):
        if("[Update]" in post.title and post.created > unix_stamp):
            posts.append(post)

    return posts

def fetchCards():

    # https://stackoverflow.com/questions/1622038/find-mondays-date-with-python
    # added 3 to fetch from Fridays instead Mondays
    today = datetime.date.today()
    stamp = today - datetime.timedelta(days=(today.weekday() + 4) % 7)

    # convert to Unix
    unix_stamp = time.mktime(stamp.timetuple())

    subreddit = getSubreddit()

    posts= []
    for post in subreddit.top(time_filter="week"):
        if("[Card]" in post.title and post.created > unix_stamp):
            posts.append(post)

    return posts
