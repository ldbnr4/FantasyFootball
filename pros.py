import re

import requests
from bs4 import BeautifulSoup

from classes import Player
from utils import POSITIONS

DRAFT_URL = 'https://www.fantasypros.com/nfl/projections/%s.php?week=draft'

WEEK_URL = 'https://www.fantasypros.com/nfl/projections/%s.php'
ROS_URL = 'https://www.fantasypros.com/nfl/rankings/ros-%s.php'


def execute(soup, players, position, week=True, verbose=False):
    for row in soup("tr", class_=re.compile("mpb-player-\d+")):
        name = row.find("a", class_="player-name").string
        if name not in players:
            if name is not None:
                if verbose:
                    print("Pros found a new player %s" % name)
                team = row.find("a", class_="player-name").nextSibling
                players[name] = Player(name, position, team, "N/A", "N/A")
        if week:
            points = float(row.find("td", {"data-sort-value": re.compile("\w+")}).string)
        else:
            points = int(row.find("td").string)
        players[name].set_pros(points)
    return players


def crawl_pros_draft(players_map, verbose=False):
    if verbose:
        print('Crawling Fantasy Pros...')
    for pos in POSITIONS:
        if verbose:
            print("on Fantasy Pros position %s" % pos)
        ros_doc = requests.get(DRAFT_URL % pos, stream=True).text
        ros_soup = BeautifulSoup(ros_doc, 'html.parser')
        execute(ros_soup, players_map, pos, True, verbose)
    if verbose:
        print('Done with Fantasy Pros!')


def crawl_pros(week_map, verbose=False):
    if verbose:
        print('Crawling Fantasy Pros...')
    for pos in POSITIONS:
        if verbose:
            print('on Fantasy Pros week position %s' % pos)
        week_doc = requests.get(WEEK_URL % pos, stream=True).text
        wk_soup = BeautifulSoup(week_doc, 'html.parser')
        current_week = wk_soup.find("div", class_="primary-heading-subheading").find("h1").string.strip().split(" ")[-1]
        wk_players = week_map.get(current_week)
        if wk_players is None:
            wk_players = {}
        execute(wk_soup, wk_players, pos)
        week_map[current_week] = wk_players

        # if verbose:
        #     print('on Fantasy Pros ros position %s' % pos)
        # ros_doc = requests.get(ROS_URL % pos, stream=True).text
        # ros_soup = BeautifulSoup(ros_doc, 'html.parser')
        # ros_players = week_map.get('ros')
        # if ros_players is None:
        #     ros_players = {}
        # execute(ros_soup, ros_players, pos, False)
        # week_map['ros'] = ros_players
