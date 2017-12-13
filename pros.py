import requests

import re
from bs4 import BeautifulSoup

POSITIONS = ['qb', 'rb', 'wr', 'te', 'k']

WEEK_URL = 'https://www.fantasypros.com/nfl/projections/%s.php'
ROS_URL = 'https://www.fantasypros.com/nfl/rankings/ros-%s.php'


def execute(soup, players, week=True):
    for row in soup("tr", class_=re.compile("mpb-player-\d+")):
        name = row.find("a").string
        if name in players:
            if week:
                points = float(row.find("td", {"data-sort-value": re.compile("\w+")}).string)
            else:
                points = int(row.find("td").string)
            players[name].set_pros(points)
        else:
            # print "Pros found an unknown player %s" % name
            continue
    return players


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
