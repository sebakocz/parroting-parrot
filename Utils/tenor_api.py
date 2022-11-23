import json
import os
import random

import requests


def get_random_parrot_gif():
    # set the apikey and limit
    apikey = os.getenv("TENOR_API_KEY")
    lmt = 50
    ckey = "parroting_parrot"  # set the client_key for the integration and use the same value for all API calls

    # our test search
    search_term = "parrot"

    # get the top 50 GIFs for the search term and randomize the selection
    r = requests.get(
        "https://tenor.googleapis.com/v2/search?q=%s&key=%s&client_key=%s&limit=%s&random=true" % (search_term, apikey, ckey, lmt))

    if r.status_code == 200:
        # load the GIFs using the urls for the smaller GIF sizes
        top_gif_json = json.loads(r.content)
        top_gif = random.choice(top_gif_json["results"])
        url = top_gif["url"]

        return url