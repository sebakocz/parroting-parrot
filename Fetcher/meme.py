from Fetcher import dict_fetcher
from Utils.memeSheet import memeCompilation


class MemeFetcher(dict_fetcher.DictFetcher):
    """
    This fetches collective's memes
    """

    def __init__(self):
        cards = {}
        for index, row in memeCompilation().iterrows():
            cards[row['keyword']] = row['url']
        super().__init__(cards)