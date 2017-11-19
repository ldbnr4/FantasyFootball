import urllib2

import re
from bs4 import BeautifulSoup

WEEK_URL = 'https://www.numberfire.com/nfl/fantasy/fantasy-football-projections'
WEEK_FILE = 'projections/number/week.html'

ROS_URL = 'https://www.numberfire.com/nfl/fantasy/remaining-projections'
ROS_FILE = 'projections/number/ros.html'


def execute(soup, current_week, players):
    projections = {}
    for row in soup("tr", {"data-row-index": re.compile("\d+")}):
        current_index = int(row["data-row-index"])
        name_buffer = row.find("span", class_='full')
        if name_buffer is not None:
            name = name_buffer.string
            # For standardization
            _buffer = name.split(" ")
            name = _buffer[0] + " " + _buffer[1]
            if name in players:
                projections[current_index] = players[name].get_projections(current_week)
            else:
                # print "Number found and unknown player %s" % name
                continue
        else:
            if current_index in projections:
                projection = projections[current_index]
                value = float(row.find("td", class_="nf_fp").string)
                projection.set_number(value)
            else:
                # Unknown player
                continue


def crawl_number(players):
    try:
        with open(WEEK_FILE) as week_file:
            week_doc = week_file.read()
            week_file.close()

        with open(ROS_FILE) as ros_file:
            ros_doc = ros_file.read()
            ros_file.close()
    except IOError:
        # print "Downloading NumberFire's web pages..."
        week_doc = urllib2.urlopen(WEEK_URL).read()
        with open(WEEK_FILE, 'w') as week_file:
            week_file.write(week_doc)
            week_file.close()

        ros_doc = urllib2.urlopen(ROS_URL).read()
        with open(ROS_FILE, 'w') as ros_file:
            ros_file.write(ros_doc)
            ros_file.close()

    # print "Crawling NumberFire's week and rest of the season pages..."
    wk_soup = BeautifulSoup(week_doc, 'html.parser')
    current_week = int(wk_soup.find("div", class_="projection-rankings__hed").find("h2").string.strip().split(" ")[1])
    execute(wk_soup, current_week, players)
    ros_soup = BeautifulSoup(ros_doc, 'html.parser')
    execute(ros_soup, 'ros', players)
    # print "Done with NumberFire"
