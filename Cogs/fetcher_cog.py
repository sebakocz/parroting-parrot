from discord.ext import commands
import Fetcher.collective, Fetcher.reddit, Fetcher.mtg, Fetcher.eternal, Fetcher.ygo, Fetcher.hs, Fetcher.lor, Fetcher.keyforge, Fetcher.marvelsnap, Fetcher.meme
from Fetcher.fetcher_list import FetcherList


class FetcherCog(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.card_fetchers = {
            FetcherList.col.mod: Fetcher.collective.CollectiveFetcher(),
            FetcherList.tk.mod: Fetcher.collective.CollectiveTokenFetcher(),
            FetcherList.sub.mod: Fetcher.reddit.CollectiveSub(),
            FetcherList.mtg.mod: Fetcher.mtg.MtgFetcher(),
            FetcherList.et.mod: Fetcher.eternal.EternalFetcher(),
            FetcherList.ygo.mod: Fetcher.ygo.YugiohFetcher(),
            FetcherList.hs.mod: Fetcher.hs.HsFetcher(),
            FetcherList.lor.mod: Fetcher.lor.LorFetcher(),
            FetcherList.kf.mod: Fetcher.keyforge.KeyforgeFetcher(),
            FetcherList.hero.mod: Fetcher.collective.CollectiveHeroFetcher(),
            FetcherList.ms.mod: Fetcher.marvelsnap.MarvelSnapFetcher(),
            FetcherList.meme.mod: Fetcher.meme.MemeFetcher(),
        }

    def get_card_name(self, text):
        """
        takes a string and extracts card names from it.
        card names are encapsulated in [[xxxx]] where xxxx is the card name.
        """

        cards = []  # list of names of cards
        start = text.find("[[")
        while start != -1:  # until there are no more brackets
            end = text.find("]]")
            # if there is an opener but no closer, then we skip it
            if end != -1:
                query = text[start + 2 : end]
                if query.find(":") > 0:
                    mod = query[: query.find(":")].lower()
                    card = query[query.find(":") + 1 :].lstrip(" ")
                    if mod not in self.card_fetchers:
                        card = query
                        mod = "none"
                    cards.append((mod, card))
                else:
                    cards.append(("", query))  # gets the name of the card
            text = text[end + 2 :]  # cuts out the part with the card
            start = text.find("[[")  # and the circle begins anew
        return cards

    @commands.Cog.listener()
    async def on_message(self, message):
        cards = self.get_card_name(
            message.content
        )  # this gets all card names in the message
        links = []  # here are the card links stored
        for card in cards:
            mod, card = card
            if mod == "hero":
                await message.channel.send(embed=self.card_fetchers[mod][card])
                continue
            if mod in self.card_fetchers:
                try:
                    links.append(self.card_fetchers[mod][card])
                except KeyError:
                    links.append("could not find {}".format(card))
            else:
                links.append("{} is not a supported search modifier".format(mod))
        if links:  # if there are any links
            # this loops runs one time plus once for every five links
            # since discord can only display five pictures per message
            for x in range((len(links) // 5) + 1):
                await message.channel.send("\n".join(links[5 * x : 5 * (x + 1)]))
        # await bot.process_commands(message)


async def setup(bot):  # an extension must have a setup function
    await bot.add_cog(FetcherCog(bot))  # adding a cog
