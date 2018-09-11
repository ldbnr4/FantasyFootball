import urllib2

import re
from bs4 import BeautifulSoup

WEEK_URL = 'http://games.espn.com/ffl/tools/projections?startIndex=%d'


def execute(soup, players):
    for row in soup("tr", id=re.compile("plyr\d+")):
        name = row.find("td", class_='playertablePlayerName').find('a').string
        _buffer = name.split(" ")
        name = _buffer[0] + " " + _buffer[1]
        points = row.find("td", class_='appliedPoints').string
        if name in players:
            players[name].set_espn(points)
        else:
            # print "Espn found an unknown player %s" % name
            continue
    return players


def crawl_espn(week):
    try:
        for i in range(0, 11):
            week_doc = urllib2.urlopen(WEEK_URL % (i * 40)).read()
            wk_soup = BeautifulSoup(week_doc, 'html.parser')
            # print wk_soup
            current_week = wk_soup.find("select", id="scoringPeriods").find("option", {"selected": "selected"}).string.strip().split(" ")[1]
            wk_players = week[current_week]
            if wk_players is None:
                wk_players = {}
            week[current_week] = execute(wk_soup, wk_players)
    except Exception:
        pass