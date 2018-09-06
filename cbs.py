import re

import requests
from bs4 import BeautifulSoup

from classes import Player
from utils import POSITIONS

DRAFT_URL = 'https://www.cbssports.com/fantasy/football/stats/sortable/points/%s/standard/projections/2018/ytd?&print_rows'


def execute(soup, players_map, pos, verbose=False):
    for row in soup("tr", class_=re.compile("row\d+")):
        name_anchor = row.find("a")
        if name_anchor is None:
            continue
        name = name_anchor.string
        if name is not None and name not in players_map:
            if verbose:
                print "CBS found a new player %s" % name
            team = name_anchor.nextSibling.split(', ')[1]
            players_map[name] = Player(name, pos, team, "N/A", "N/A")
        points = list(row.children)[-1].string
        players_map[name].set_cbs(points)


def crawl_cbs_draft(players_map, verbose=False):
    if verbose:
        print "Crawling Fantasy Pros..."
    for pos in POSITIONS:
        print "crawling position: %s" % pos
        ros_doc = requests.get(DRAFT_URL % pos, stream=True).text
        ros_soup = BeautifulSoup(ros_doc, 'html.parser')
        execute(ros_soup, players_map, pos, verbose)
    if verbose:
        print "Done!"