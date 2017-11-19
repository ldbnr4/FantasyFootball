import requests

import re
from bs4 import BeautifulSoup

POSITIONS = ['qb', 'rb', 'wr', 'te', 'k']

WEEK_URL = 'https://www.fantasypros.com/nfl/projections/%s.php'
WEEK_FILE = 'projections/pros/week/%s.html'

ROS_URL = 'https://www.fantasypros.com/nfl/rankings/ros-%s.php'
ROS_FILE = 'projections/pros/ros/%s.html'


def execute(soup, current_week, players):
    for row in soup("tr", class_=re.compile("mpb-player-\d+")):
        name = row.find("a").string
        if name in players:
            if type(current_week) is int:
                points = float(row.find("td", {"data-sort-value": re.compile("\w+")}).string)
            else:
                points = int(row.find("td").string)
            players[name].get_projections(current_week).set_pros(points)
        else:
            # print "Pros found an unknown player %s" % name
            continue


def crawl_pros(players):
    week_docs = {}
    ros_docs = {}
    try:
        for pos in POSITIONS:
            with open(WEEK_FILE % pos) as week_file:
                week_docs[pos] = week_file.read()
                week_file.close()

            with open(ROS_FILE % pos) as ros_file:
                ros_docs[pos] = ros_file.read()
                ros_file.close()
    except IOError:
        # print "Downloading FantasyPros' web pages..."
        for pos in POSITIONS:
            week_doc = requests.get(WEEK_URL % pos, stream=True).text
            week_docs[pos] = week_doc
            with open(WEEK_FILE % pos, 'w') as week_file:
                week_file.write(week_doc)
                week_file.close()

            ros_doc = requests.get(ROS_URL % pos, stream=True).text
            ros_docs[pos] = ros_doc
            with open(ROS_FILE % pos, 'w') as ros_file:
                ros_file.write(ros_doc)
                ros_file.close()

    # print "Crawling FantasyPros's week and rest of the season pages..."
    for pos in POSITIONS:
        wk_soup = BeautifulSoup(week_docs[pos], 'html.parser')
        current_week = int(wk_soup.find("div", class_="primary-heading-subheading").find("h1").string.strip().split(" ")[-1])
        execute(wk_soup, current_week, players)

        ros_soup = BeautifulSoup(ros_docs[pos], 'html.parser')
        execute(ros_soup, 'ros', players)
    # print "Done with FantasyPros"
