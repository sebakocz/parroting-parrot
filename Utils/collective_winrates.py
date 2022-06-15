# -*- coding: utf-8 -*-
#Winrate code courtesy of StrangerSide
import aiohttp
import requests as req
import json
import pandas as pd
import numpy as np
from collections import Counter, defaultdict
import pickle as pck
from scipy.stats import binom_test

games_url = 'https://server.collective.gg/api/public/games'
decks_url = 'https://server.collective.gg/api/public/decklists'


async def collect_winrate_data():
    # Get games
    with req.get(games_url) as src:
        games = json.loads(src.text)

    with req.get(decks_url) as src:
        decks = json.loads(src.text)

    card_list = set()

    decklists = defaultdict(Counter)
    for item in decks['decklists']:  # Tabulate all decklists
        dl = item['decklist']
        card = item['card']
        decklists[dl][card] += 1
        card_list.add(card)

    ccnt = len(card_list)
    played_arry = np.zeros(shape=ccnt, dtype=int)
    win_arry = np.zeros(shape=ccnt, dtype=int)

    sorted_card_list = sorted(list(card_list))
    card_idx = dict([(item, i) for i, item in enumerate(sorted_card_list)])
    idx_card = dict([(i, item) for i, item in enumerate(sorted_card_list)])

    for game in games['games']:
        pl1 = game['player1']
        pl2 = game['player2']
        dl1 = game['decklist1']
        dl2 = game['decklist2']
        if game['winner'] == pl2:  # Player 1 is always winner
            pl1, pl2 = pl2, pl1
            dl1, dl2 = dl2, dl1
        dl1 = set(decklists[dl1].keys())
        dl2 = set(decklists[dl2].keys())
        inter = dl1.intersection(dl2)  # Found in both
        won = dl1 - inter  # Found in the winning deck, but not both
        lost = dl2 - inter  # Found in the losing deck, but not both
        for c in won:
            i = card_idx[c]
            win_arry[i] += 2
            played_arry[i] += 1
        for c in lost:
            i = card_idx[c]
            played_arry[i] += 1
        # for c in inter:
        #     i=card_idx[c]
        #     win_arry[i] += 1
        #     played_arry[i] += 1

    raw_wins = {}  # For ease of binomial
    winrates = {}
    for i, plays in enumerate(played_arry):
        wins = win_arry[i] // 2
        raw_wins[card] = wins
        card = idx_card[i]
        winrates[card] = wins / plays

    # Fetch card names:
    card_name_file = 'Data/card_names.pck'
    try:
        with open(card_name_file, 'rb') as src:
            card_names = pck.load(src)
    except FileNotFoundError:
        print('Could not locate names file.')
        card_names = {}

    print('Getting card data...')
    for card in winrates.keys():
        if card in card_names:
            continue  # Skip
        clink = f'https://server.collective.gg/api/card/{card}'
        print(f'Loading {clink}')
        async with aiohttp.ClientSession() as session:
            async with session.get(clink) as response:
                cobj = json.loads(await response.text())
        # with req.get(clink) as src:
        #     cobj = json.loads(src.text)
        name = cobj['card']['name']
        card_names[card] = name
        print(f'Found {name}')

    print('Saving card file...')
    with open(card_name_file, 'wb') as src:
        pck.dump(card_names, src)

    print('Building frame')
    frm = pd.DataFrame(winrates.items(), columns=['card', 'win_pct'])
    frm['name'] = frm['card'].apply(card_names.get)

    frm.sort_values('win_pct', inplace=True, ascending=False)
    frm['win_rate'] = frm['card'].apply(card_idx.get).apply(lambda v: win_arry[v] // 2)
    frm['played_rate'] = frm['card'].apply(card_idx.get).apply(lambda v: played_arry[v])

    pvals = {}
    print('Getting p-vals')
    for idx, row in frm.iterrows():
        c = row['name']
        w = row['win_rate']
        g = row['played_rate']
        p = binom_test(w, g, alternative='greater')
        pvals[c] = p
    frm['p_val'] = frm['name'].apply(pvals.get)

    frm.to_csv('Data/collective_winrates_no_mirrors.csv')

def display_current_data_playrate(length):

    # read csv
    data = pd.read_csv("Data/collective_winrates_no_mirrors.csv", index_col=False)

    # only show relevant columns
    data = data[['name', 'played_rate', 'win_pct', 'p_val']]

    # show top 10 played cards with descending order
    data = data.sort_values('played_rate', ascending=False).head(length)

    # show winrate as percentage
    data['win_pct'] = data['win_pct'].astype(float).map("{:.2%}".format)

    # format p_val to readable number
    data['p_val'] = data['p_val'].astype(float).map("{:.4f}".format)

    # make table name pretty
    data = data.rename(columns={'name': 'Name', 'played_rate': 'Usage', 'win_pct': "Win%", 'p_val': 'p-value'})
    data = data.reset_index(drop=True)
    data.index = data.index + 1

    return data

def display_current_data_winrate(length):
    # read csv
    data = pd.read_csv("Data/collective_winrates_no_mirrors.csv", index_col=False)

    # only show relevant columns
    data = data[['name', 'played_rate', 'win_pct', 'p_val']]

    # filter only low p-values
    data = data[data['p_val'] <= 0.01]

    # sort and show top 10 winning cards
    data = data.sort_values('win_pct', ascending=False).head(length)

    # show winrate as percentage
    data['win_pct'] = data['win_pct'].astype(float).map("{:.2%}".format)

    # format p_val to readable number
    data['p_val'] = data['p_val'].astype(float).map("{:.4f}".format)

    data = data.rename(
        columns={'name': 'Name', 'played_rate': 'Usage', 'win_pct': "Win%", 'p_val': 'p-value'})
    data = data.reset_index(drop=True)
    data.index = data.index + 1

    return data