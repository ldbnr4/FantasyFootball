import re
from urllib import request

from bs4 import BeautifulSoup

from classes import Player

# ALL = 0
# QB = 1
# RB = 2
# WR = 3
# TE = 4
# K = 7
# DEF = 8
BASE_URL = "http://fantasy.nfl.com"
BASE_RESEARCH = "%s/research/projections?position=O&sort=projectedPts&statCategory=projectedStats&statSeason=2018" % BASE_URL
WEEK_URL = "%s&statType=weekProjectedStats" % BASE_RESEARCH
SEASON_URL = "%s/research/projections?position=O&sort=projectedPts&statCategory=projectedStats&statSeason=2018&statType" \
             "=seasonProjectedStats" % BASE_URL
WEEK_HOME_URL = "%s/league/6009432/players?playerStatus=all&position=O&statCategory=projectedStats" % BASE_URL
ROS_URL = "%s&statType=restOfSeasonProjectedStats" % WEEK_URL
NUM_PAGES = 27

# BASE_FILE_PATH = "projections/nfl/"
BASE_FILE_PATH = "."

offset = 1


# "scraped_%s.json" % datetime.datetime.now().strftime("%m_%d_%Y")

def parse_position_team(position_team):
    buffer_ = position_team.split(' - ')
    _position = buffer_[0]
    if len(buffer_) == 2:
        _team = buffer_[1]
    else:
        _team = "N/A"
    return _position, _team


def execute(soup, players):
    for player_row in soup("tr", class_=re.compile("player-\d+")):
        name = player_row.find("a", class_="playerName").string
        # For standardization
        _buffer = name.split(" ")
        name = _buffer[0] + " " + _buffer[1]
        if name not in players:
            # Build and insert into players dictionary
            position, team = parse_position_team(player_row.find("em").string)
            opponent = player_row.find("td", class_="playerOpponent").string
            # owner = player_row.find("td", class_="playerOwner").string
            players[name] = Player(name, position, team, opponent, "N/A")
        player = players[name]
        # Set nfl's predicted points
        try:
            projected_points = float(player_row.find("span", class_="playerWeekProjectedPts").string)
        except AttributeError:
            # Not playing this week?
            projected_points = float(player_row.find("td", class_="projected").string)
        except ValueError:
            # Not playing this week
            continue
        if projected_points == 0:
            #TODO: log the offset
            break
        # Add predictions
        player.set_nfl(projected_points)
    return players


def crawl_nfl_season(player_hash, single_shot=False, verbose=False):
    global offset
    if verbose:
        print('Crawling NFL season...')
    if player_hash is None:
        player_hash = {}

    if single_shot:
        pass
    else:
        for page in range(0, NUM_PAGES):
            if verbose:
                print("crawling page=%d" % page)
            season_web_page = request.urlopen("%s&offset=%d" % (SEASON_URL, offset)).read()
            season_soup = BeautifulSoup(season_web_page, 'html.parser')
            execute(season_soup, player_hash)
            offset = (25 * page) + 26
    pass
    if verbose:
        print('Done!')


def crawl_nfl(players_map, verbose=False):
    global offset
    if verbose:
        print('Crawling NFL...')
    week_url = "%s&statWeek=1" % WEEK_URL
    for i in range(0, NUM_PAGES):
        if verbose:
            print("On NFL week page=%d" % i)
        # NFL week page
        wk_web_page = request.urlopen("%s&offset=%d" % (week_url, offset)).read()
        week_soup = BeautifulSoup(wk_web_page, 'html.parser')
        current_week = week_soup.find("ul", class_="weekNav").find("li", class_="selected").find("span").string
        week_players = players_map.get(current_week)
        if week_players is None:
            week_players = {}
        players_map[current_week] = execute(week_soup, week_players)

        if verbose:
            print("On NFL ros page=%d" % i)
        ros_web_page = request.urlopen(ROS_URL + "&offset=%d" % offset).read()
        ros_soup = BeautifulSoup(ros_web_page, 'html.parser')
        ros_players = players_map.get('ros')
        if ros_players is None:
            ros_players = {}
        players_map['ros'] = execute(ros_soup, ros_players)
        offset = (25 * i) + 26
