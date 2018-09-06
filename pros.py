import requests

import re
from bs4 import BeautifulSoup

from classes import Player
from utils import POSITIONS

DRAFT_URL = 'https://www.fantasypros.com/nfl/projections/%s.php?week=draft'

WEEK_URL = 'https://www.fantasypros.com/nfl/projections/%s.php'
WEEK_FILE = 'projections/pros/week/%s.html'

ROS_URL = 'https://www.fantasypros.com/nfl/rankings/ros-%s.php'
ROS_FILE = 'projections/pros/ros/%s.html'


def execute(soup, players, position, week=True, verbose=False):
    for row in soup("tr", class_=re.compile("mpb-player-\d+")):
        name = row.find("a", class_="player-name").string
        if name not in players:
            if name is not None:
                if verbose:
                    print "Pros found a new player %s" % name
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
        print "Crawling Fantasy Pros..."
    for pos in POSITIONS:
        print "crawling position: %s" % pos
        ros_doc = requests.get(DRAFT_URL % pos, stream=True).text
        ros_soup = BeautifulSoup(ros_doc, 'html.parser')
        execute(ros_soup, players_map, pos, True, verbose)
    if verbose:
        print "Done!"


def crawl_pros(week):
    # print "Crawling FantasyPros' web pages..."
    for pos in POSITIONS:
        week_doc = requests.get(WEEK_URL % pos, stream=True).text
        wk_soup = BeautifulSoup(week_doc, 'html.parser')
        current_week = wk_soup.find("div", class_="primary-heading-subheading").find("h1").string.strip().split(" ")[-1]
        wk_players = week[current_week]
        if wk_players is None:
            wk_players = {}
        week[current_week] = execute(wk_soup, wk_players)

        ros_doc = requests.get(ROS_URL % pos, stream=True).text
        ros_soup = BeautifulSoup(ros_doc, 'html.parser')
        ros_players = week['ros']
        if ros_players is None:
            ros_players = {}
        week['ros'] = execute(ros_soup, ros_players, False)
    # print "Done with FantasyPros"
