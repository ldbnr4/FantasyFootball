import urllib2

import re
from bs4 import BeautifulSoup

WEEK_URL = 'https://www.numberfire.com/nfl/fantasy/fantasy-football-projections'

ROS_URL = 'https://www.numberfire.com/nfl/fantasy/remaining-projections'


def execute(soup, players):
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
                projections[current_index] = players[name]
            else:
                # print "Number found and unknown player %s" % name
                continue
        else:
            if current_index in projections:
                value = float(row.find("td", class_="nf_fp").string)
                projections[current_index].set_number(value)
            else:
                # Unknown player
                continue
    return players


def crawl_number(week):
    # print "Crawling NumberFire's week and rest of the season pages..."
    week_doc = urllib2.urlopen(WEEK_URL).read()
    ros_doc = urllib2.urlopen(ROS_URL).read()

    wk_soup = BeautifulSoup(week_doc, 'html.parser')
    current_week = wk_soup.find("div", class_="projection-rankings__hed").find("h2").string.strip().split(" ")[1]
    wk_players = week[current_week]
    if wk_players is None:
        wk_players = {}
    week[current_week] = execute(wk_soup, wk_players)

    ros_players = week['ros']
    if ros_players is None:
        ros_players = {}
    ros_soup = BeautifulSoup(ros_doc, 'html.parser')
    week['ros'] = execute(ros_soup, ros_players)
    # print "Done with NumberFire"
