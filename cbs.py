import re

import requests
from bs4 import BeautifulSoup

from classes import Player
from utils import POSITIONS

DRAFT_URL = 'https://www.cbssports.com/fantasy/football/stats/sortable/points/%s/standard/projections/2018/ytd' \
            '?&print_rows '
WEEK_URL = 'https://www.cbssports.com/fantasy/football/stats/sortable/points/%s/standard/projections/2018/tp' \
           '?&print_rows=9999 '
ROS_URL = 'https://www.cbssports.com/fantasy/football/stats/sortable/points/%s/standard/projections/2018/restofseason' \
          '?&print_rows=9999 '


def execute_crawl(soup, players):
    for row in soup("tr", class_=re.compile("row[1,2]")):
        try:
            if row['id']:
                continue
        except KeyError:
            name = row.find("td").find("a").string
            if name in players:
                points = row.find_all("td")[-1].string
                players[name].set_cbs(points)
            else:
                # print "CBS found an unknown player %s" % name
                # TODO: create a player
                continue
    return players


def crawl_cbs(players_map, verbose):
    if verbose:
        print("Crawling Fantasy Pros...")
    for pos in POSITIONS:
        if verbose:
            print("On Fantasy Pros position: %s" % pos)
        url = WEEK_URL % pos
        week_doc = requests.get(url, stream=True).text
        wk_soup = BeautifulSoup(week_doc, 'html.parser')
        current_week = \
        wk_soup.find("select", id="timeframe").find("option", {"selected": "selected"}).string.strip().split(" ")[1]
        wk_players = players_map.get(current_week)
        if wk_players is None:
            wk_players = {}
        execute_crawl(wk_soup, wk_players)
        players_map[current_week] = wk_players

        ros_doc = requests.get(ROS_URL % pos, stream=True).text
        ros_soup = BeautifulSoup(ros_doc, 'html.parser')
        ros_players = players_map.get('ros')
        if ros_players is None:
            ros_players = {}
        players_map['ros'] = execute_crawl(ros_soup, ros_players)
        if verbose:
            print("Done!")


def execute(soup, players_map, pos, verbose=False):
    for row in soup("tr", class_=re.compile("row\d+")):
        name_anchor = row.find("a")
        if name_anchor is None:
            continue
        name = name_anchor.string
        if name is not None and name not in players_map:
            if verbose:
                print("CBS found a new player %s" % name)
            team = name_anchor.nextSibling.split(', ')[1]
            players_map[name] = Player(name, pos, team, "N/A", "N/A")
        points = list(row.children)[-1].string
        players_map[name].set_cbs(points)


def crawl_cbs_draft(players_map, verbose=False):
    if verbose:
        print("Crawling Fantasy Pros...")
    for pos in POSITIONS:
        print("crawling position: %s" % pos)
        ros_doc = requests.get(DRAFT_URL % pos, stream=True).text
        ros_soup = BeautifulSoup(ros_doc, 'html.parser')
        execute(ros_soup, players_map, pos, verbose)
    if verbose:
        print("Done!")
