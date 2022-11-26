from dataclasses import dataclass


@dataclass(frozen=True)
class FetcherObject:
    mod: str
    description: str
    __slots__ = ("mod", "description")


class FetcherList:
    col = FetcherObject("", "a non-token card from Collective")
    tk = FetcherObject("tk", "a token card from Collective")
    sub = FetcherObject("sub", "a card from Collective's subreddit")
    hero = FetcherObject("hero", "a hero from Collective")
    meme = FetcherObject("meme", "Collective Memes")

    ygo = FetcherObject("ygo", "Yugioh")
    mtg = FetcherObject("mtg", "Magic the Gathering")
    et = FetcherObject("et", "Eternal")
    hs = FetcherObject("hs", "Hearthstone")
    lor = FetcherObject("lor", "Legends of Runeterra")
    kf = FetcherObject("kf", "Keyforge")
    ms = FetcherObject("ms", "Marvel Snap")

    all = [col, tk, sub, hero, meme, ygo, mtg, et, hs, lor, kf, ms]
