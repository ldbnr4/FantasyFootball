
import re
from urllib import request
import requests

from bs4 import BeautifulSoup

from classes import Player

WEEK_URL = 'https://www.numberfire.com/nfl/fantasy/fantasy-football-projections'
ROS_URL = 'https://www.numberfire.com/nfl/fantasy/remaining-projections'


def execute(soup, players, verbose=False):
    projections = {}
    for row in soup("tr", {"data-row-index": re.compile("\d+")}):
        current_index = int(row["data-row-index"])
        name_buffer = row.find("span", class_='full')
        if name_buffer is not None:
            name = name_buffer.string
            # For standardization
            _buffer = name.split(" ")
            name = _buffer[0] + " " + _buffer[1]
            if name not in players:
                if verbose and name is not None:
                    print("Number found a player %s" % name)
                position_team = row.find("td", class_='player').find("a").nextSibling.split(",")
                position = position_team[0][2:]
                team = position_team[1][1:3]
                player = Player(name, position, team, "N/A", "N/A")
                players[name] = player
            projections[current_index] = players[name]
        else:
            if current_index in projections:
                value = float(row.find("td", class_="nf_fp").string)
                projections[current_index].set_number(value)
            else:
                # Unknown player
                continue
    return players


def crawl_number_ros(players_map, verbose=False):
    if verbose:
        print('Crawling NumberFire...')
    ros_doc = request.urlopen(ROS_URL).read()
    execute(BeautifulSoup(ros_doc, 'html.parser'), players_map, verbose)
    if verbose:
        print('Done!')


def crawl_number(week_map, verbose):
    if verbose:
        print("Crawling NumberFire...")
    week_doc = requests.get(WEEK_URL).text
    ros_doc = requests.get(ROS_URL).text

    if verbose:
        print("on NumberFire week")
    wk_soup = BeautifulSoup(week_doc, 'html.parser')
    current_week = wk_soup.find("div", class_="projection-rankings__hed").find("h2").string.strip().split(" ")[1]
    wk_players = week_map.get(current_week)
    if wk_players is None:
        wk_players = {}
    execute(wk_soup, wk_players)
    week_map[current_week] = wk_players

    if verbose:
        print("on NumberFire ros")
    ros_players = week_map.get('ros')
    if ros_players is None:
        ros_players = {}
    ros_soup = BeautifulSoup(ros_doc, 'html.parser')
    execute(ros_soup, ros_players)
    week_map['ros'] = ros_players
    if verbose:
        print("Done with NumberFire!")
