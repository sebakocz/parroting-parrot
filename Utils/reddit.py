import calendar
import datetime
import os
import re
from enum import Enum

import asyncpraw

import Utils.collectiveApi


class PostType(Enum):
    # PostType.value returns the strings
    CARD = "[Card]"
    STANDARD_UPDATE = "[Standard Update]"
    LEGACY_UPDATE = "[Legacy Update]"
    DC = "[DC]"


async def get_subreddit():
    reddit = asyncpraw.Reddit(
        client_id=os.getenv("REDDIT_CLIENT_ID"),
        client_secret=os.getenv("REDDIT_API_SECRET"),
        username=os.getenv("REDDIT_USERNAME"),
        password=os.getenv("REDDIT_PASSWORD"),
        user_agent="DraftingParrot - bot by Sevas",
        redirect_uri="https://www.collective.gg/",
        refresh_token="XXXXXXXXXXXXXXXX",
    )

    subreddit = await reddit.subreddit(os.getenv("REDDIT_SUBREDDIT"))

    return subreddit, reddit


def get_week_unix_stamp(week_number=1):
    # https://stackoverflow.com/questions/1622038/find-mondays-date-with-python
    # get last Wednesday Midnight PST stamp depending on which day is today
    # transfer to UTC in order to work on local machine as well as server in the same manner
    # UTC is 7 hours ahead of PST
    today = datetime.datetime.utcnow().replace(
        hour=7, minute=0, second=0, microsecond=0
    )
    stamp = today - datetime.timedelta(days=(today.weekday() + 4) % 7)

    # offset stamp by week number
    stamp += datetime.timedelta(days=7 * week_number)

    # convert to Unix
    unix_stamp = calendar.timegm(stamp.timetuple())
    # unix_stamp = calendar.timegm(stamp.timetuple()) + 7 * 3600

    # Debug
    # print("getLastWeekUnixStamp() DEBUG")
    # print(f"Today: {today}")
    # print(f"Delta: {datetime.timedelta(days=(today.weekday()+4)%7)}")
    # print(f"Stamp: {stamp}")
    # print((f"Unix: {unix_stamp}"))

    return unix_stamp


async def submit(card_link, optional_text="", submit_type="[Card]"):
    # 1. get the card's name from the json data
    # 2. combine card's name and the type (Update, DC, standard=Card) and optional text to create a post
    # ie.: title="[Card] Ila, Seeker of Futures (New cool card!)" url=https://files.collective.gg/p/cards/91c64410-2874-11ec-a560-3dfd4d1fd4c0-m.png

    card_json = Utils.collectiveApi.json_from_link(card_link)
    card_name = card_json["Text"]["Name"]

    subreddit, reddit = await get_subreddit()

    title = f"{submit_type} {card_name}"
    if optional_text != "":
        title += f" ({optional_text})"

    submission = await subreddit.submit(title, url=card_link)
    await submission.load()
    await reddit.close()

    return f"https://www.reddit.com{submission.permalink}"


async def fetch_posts(submit_type):

    # 0 = starting timestamp of current running week
    unix_stamp = get_week_unix_stamp(0)

    subreddit, reddit = await get_subreddit()
    posts = []
    async for post in subreddit.top(time_filter="week"):
        # Debug
        # print(post.title)
        # print(post.created)
        if submit_type.value in post.title and post.created > unix_stamp:
            posts.append(post)
    await reddit.close()

    posts.sort(key=lambda x: x.score, reverse=True)

    return posts


async def change_flair(season=1, week=1):
    subreddit, reddit = await get_subreddit()

    automod = await subreddit.wiki.get_page("config/automoderator")

    content = re.sub(
        r'(?<=title: \["\[Card]", "\[Update]", "\[Cosmetic Update]", "\[DC]","\[DCDC]",]\ndomain: "files.collective.gg"\nset_flair: ")(.*?)(?=")',
        f"Season {season} - Week {week}",
        automod.content_md,
    )

    await automod.edit(content=content)
    await reddit.close()
