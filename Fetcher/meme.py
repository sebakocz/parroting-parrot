from Fetcher import dict_fetcher
from Utils.googleSheetApi import get_google_sheet


class MemeFetcher(dict_fetcher.DictFetcher):
    """
    This fetches collective's memes
    """

    def __init__(self):
        cards = {}
        for index, row in get_google_sheet("1Qa-bbX2JQSGDbqkAiZZOyOfMP4MBdwOpTW-RVHdcIZw", 0).iterrows():
            cards[row['keyword']] = row['url']
        super().__init__(cards)