# import requests
import json
import re
import timeit
import urllib2

import datetime
from bs4 import BeautifulSoup

from classes import Player

#TODO: add statSeason=2016 to the end of nlf url for historical data or https://partners.fantasypros.com/api/v1/nfl-stats.php?week=10&year=2017
#TODO: look into duplicates of players when building dict
from number import crawl_number
from pros import crawl_pros


def parse_position_team(position_team):
    buffer_ = position_team.split(' - ')
    _position = buffer_[0]
    if len(buffer_) == 2:
        _team = buffer_[1]
    else:
        _team = "N/A"
    return _position, _team


FILE_PATH = "projections/done/scraped_%s.json" % datetime.datetime.now().strftime("%m_%d_%Y")
NUM_PAGES = 27
# Players dictionary
Players = {}


def execute(soup, week):
    for player_row in soup("tr", class_=re.compile("player-\d+")):
        name = player_row.find("a", class_="playerName").string
        # For standardization
        _buffer = name.split(" ")
        name = _buffer[0] + " " + _buffer[1]
        if name not in Players:
            # Build and insert into players dictionary
            position, team = parse_position_team(player_row.find("em").string)
            opponent = player_row.find("td", class_="playerOpponent").string
            owner = player_row.find("td", class_="playerOwner").string
            Players[name] = Player(name, position, team, opponent, owner)
        player = Players[name]
        # Set nfl's predicted points
        try:
            projected_points = float(player_row.find("span", class_="playerWeekProjectedPts").string)
        except AttributeError:
            # Not playing this week?
            projected_points = float(player_row.find("td", class_="projected").string)
        except ValueError:
            # Not playing this week
            continue
        # Add predictions
        player.get_projections(week).set_nfl(projected_points)


def execute_main():
    nfl_file = 'projections/nfl/%s/page_%d.html'
    week_docs = {}
    ros_docs = {}
    start_time = timeit.default_timer()
    # code you want to evaluate
    try:
        for i in range(0, NUM_PAGES):
            # NFL week file
            with open(nfl_file % ("wk", i)) as week_file:
                week_docs[i] = week_file.read()
                week_file.close()
            # NFL rest of the season file
            with open(nfl_file % ("ros", i)) as ros_file:
                ros_docs[i] = ros_file.read()
                ros_file.close()

    except IOError:
        print "Downloading nfl's pages..."
        week_url = 'http://fantasy.nfl.com/league/6009432/players?playerStatus=all&position=O&statCategory=projectedStats' \
                   '&offset=%d'
        ros_url = "%s&statType=restOfSeasonProjectedStats" % week_url
        offset = 1
        for i in range(0, NUM_PAGES):
            # NFL week page
            nfl_wk_web_page = urllib2.urlopen(week_url % offset).read()
            week_docs[i] = nfl_wk_web_page
            with open(nfl_file % ("wk", i), 'w') as week_file:
                week_file.write(nfl_wk_web_page)
                week_file.close()
            # NFL rest of the season page
            nfl_ros_web_page = urllib2.urlopen(ros_url % offset).read()
            ros_docs[i] = nfl_ros_web_page
            with open(nfl_file % ("ros", i), 'w') as ros_file:
                ros_file.write(nfl_ros_web_page)
                ros_file.close()
            offset = (25 * i) + 26

        elapsed = timeit.default_timer() - start_time
        print "That took about %.2f sec" % elapsed

    print "Crawling nfl's pages and building Players dictionary..."
    start_time = timeit.default_timer()
    for i in range(0, NUM_PAGES):
        # NFL week soup
        week_soup = BeautifulSoup(week_docs[i], 'html.parser')
        # Extract the week
        current_week = int(
            week_soup.find("ul", class_="weekNav").find("li", class_="selected").find("span", class_="text").string)
        execute(week_soup, current_week)

        ros_soup = BeautifulSoup(ros_docs[i], 'html.parser')
        execute(ros_soup, 'ros')
    print "Done with NFL!"
    elapsed = timeit.default_timer() - start_time
    print "That took about %.2f sec" % elapsed

    start_time = timeit.default_timer()
    crawl_number(Players)
    elapsed = timeit.default_timer() - start_time
    print "That took about %.2f sec" % elapsed

    start_time = timeit.default_timer()
    crawl_pros(Players)
    elapsed = timeit.default_timer() - start_time
    print "That took about %.2f sec" % elapsed

    players_json_array = []
    for player in Players:
        players_json_array.append(Players[player].toJSON())
    with open(FILE_PATH, 'w') as outfile:
        json.dump(players_json_array, outfile)
        outfile.close()
    print "Done with everything!"


try:
    with open(FILE_PATH) as file_:
        file_.close()
except IOError:
    execute_main()
