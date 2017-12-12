import urllib2

import re
from bs4 import BeautifulSoup

WEEK_URL = 'http://games.espn.com/ffl/tools/projections'


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


def crawl_espn(week):
    # print "Crawling ESPN's week pages..."
    week_doc = urllib2.urlopen(WEEK_URL).read()
    wk_soup = BeautifulSoup(week_doc, 'html.parser')
    # print wk_soup
    current_week = wk_soup.find("select", id="scoringPeriods").find("option", {"selected": "selected"}).string.strip().split(" ")[1]
    print(current_week)
    wk_players = week[current_week]
    if wk_players is None:
        wk_players = {}
    # week[current_week] = execute(wk_soup, wk_players)
    # print "Done with ESPN"
