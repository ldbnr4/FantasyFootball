import requests

import re
from bs4 import BeautifulSoup

from pros import POSITIONS

WEEK_URL = 'https://www.cbssports.com/fantasy/football/stats/sortable/points/%s/standard/projections/2017/tp?&print_rows=9999'
ROS_URL = 'https://www.cbssports.com/fantasy/football/stats/sortable/points/%s/standard/projections/2017/restofseason?&print_rows=9999'


def execute(soup, players):
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
                continue
    return players


def crawl_cbs(week):
    for pos in POSITIONS:
        week_doc = requests.get(WEEK_URL % pos, stream=True).text
        wk_soup = BeautifulSoup(week_doc, 'html.parser')
        current_week = wk_soup.find("select", id="timeframe").find("option", {"selected": "selected"}).string.strip().split(" ")[1]
        wk_players = week[current_week]
        if wk_players is None:
            wk_players = {}
        week[current_week] = execute(wk_soup, wk_players)

        ros_doc = requests.get(ROS_URL % pos, stream=True).text
        ros_soup = BeautifulSoup(ros_doc, 'html.parser')
        ros_players = week['ros']
        if ros_players is None:
            ros_players = {}
        week['ros'] = execute(ros_soup, ros_players)
