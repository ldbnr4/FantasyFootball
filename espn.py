import re
from urllib import request

from bs4 import BeautifulSoup

from classes import Player
from utils import CURRENT_YEAR

WEEK_URL = 'http://games.espn.com/ffl/tools/projections?startIndex=%d'
LEAGUE_ID = 2055431
WEEK_URL_LEAGUE = '%s&leagueId=%d' % (WEEK_URL, LEAGUE_ID)
ROS_URL_LEAGUE = '%s&seasonTotals=true&seasonId=%d' % (WEEK_URL_LEAGUE, CURRENT_YEAR)

def execute(soup, players, verbose=False):
    for row in soup("tr", id=re.compile("plyr\d+")):
        name_team_pos = row.find("td", class_='playertablePlayerName')
        team_pos = name_team_pos.text.strip().split("\xa0")
        pos = team_pos[1]
        team_pos_buffer = team_pos[0]
        if pos == "D/ST":
            name = team_pos_buffer
            team = "n/a"
        else:
            team = team_pos_buffer.split(", ")[1]
            name = name_team_pos.find('a').string
            _buffer = name.split(" ")
            name = _buffer[0] + " " + _buffer[1]
        owner = name_team_pos.nextSibling.string
        points = row.find("td", class_='appliedPoints').string
        try:
            flexpop_buffer = row.find_all("a", class_='flexpop')
            if pos == "D/ST":
                opponent = flexpop_buffer[1].string
            else:
                opponent = flexpop_buffer[2].string
        except Exception:
            opponent = "n/a"
        if name in players:
            player = players[name]
        else:
            if verbose:
                print("Espn found an unknown player %s" % name)
            player = Player(name, pos, team, opponent, owner)
            players[name] = player
        player.set_espn(points)
    return players


def crawl_espn(week_map, verbose=False):
    if verbose:
        print('Crawling ESPN...')
    for i in range(0, 11):
        if verbose:
            print("on ESPN week page %d" % i)
        week_doc = request.urlopen(WEEK_URL_LEAGUE % (i * 40)).read()
        wk_soup = BeautifulSoup(week_doc, 'html.parser')
        # print wk_soup
        current_week = wk_soup.find("select", id="scoringPeriods").find("option", {"selected": "selected"}).string.strip().split(" ")[1]
        wk_players = week_map.get(current_week)
        if wk_players is None:

            wk_players = {}
        execute(wk_soup, wk_players, verbose)
        week_map[current_week] = wk_players

        if verbose:
            print("on ESPN ros page %d" % i)
        ros_doc = request.urlopen(ROS_URL_LEAGUE % (i * 40)).read()
        ros_soup = BeautifulSoup(ros_doc, 'html.parser')
        ros_players = week_map.get('ros')
        ex_verbose = verbose
        if ros_players is None:
            ex_verbose = False
            ros_players = {}
        execute(ros_soup, ros_players, ex_verbose)
        week_map['ros'] = ros_players
    if verbose:
        print('Done with ESPN!')
