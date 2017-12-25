# import requests
import json
import re
import timeit
import urllib2

import datetime
from bs4 import BeautifulSoup

from cbs import crawl_cbs
from classes import Player

#TODO: add statSeason=2016 to the end of nlf url for historical data or https://partners.fantasypros.com/api/v1/nfl-stats.php?week=10&year=2017
#TODO: look into duplicates of players when building dict
from espn import crawl_espn
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


FILE_PATH = "projections/scraped_%s.json" % datetime.datetime.now().strftime("%m_%d_%Y")
NUM_PAGES = 26
# Week dictionary
Week = {}
# Players dictionary
# Players = {}


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
            owner = player_row.find("td", class_="playerOwner").string
            players[name] = Player(name, position, team, opponent, owner)
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
        # Add predictions
        player.set_nfl(projected_points)
    return players


def execute_main():
    start_time = timeit.default_timer()

    # print("Crawling NFL's pages...")
    week_url = 'http://fantasy.nfl.com/league/6009432/players?playerStatus=all&position=O&statCategory=projectedStats' \
               '&offset=%d'
    ros_url = "%s&statType=restOfSeasonProjectedStats" % week_url
    offset = 1
    for i in range(0, NUM_PAGES):
        # NFL week page
        url = week_url % offset
        wk_web_page = urllib2.urlopen(url).read()
        week_soup = BeautifulSoup(wk_web_page, 'html.parser')
        current_week = week_soup.find("ul", class_="weekNav").find("li", class_="selected").find("span", class_="text").string
        week_players = Week.get(current_week)
        if week_players is None:
            week_players = {}
        Week[current_week] = execute(week_soup, week_players)

        ros_web_page = urllib2.urlopen(ros_url % offset).read()
        ros_soup = BeautifulSoup(ros_web_page, 'html.parser')
        ros_players = Week.get('ros')
        if ros_players is None:
            ros_players = {}
        Week['ros'] = execute(ros_soup, ros_players)
        offset = (25 * i) + 26
    # elapsed = timeit.default_timer() - start_time
    # print "That took about %.2f sec" % elapsed
    #
    # print "Crawling NumberFire's week and rest of the season pages..."
    # start_time = timeit.default_timer()
    crawl_number(Week)

    # elapsed = timeit.default_timer() - start_time
    # print "That took about %.2f sec" % elapsed
    #
    # print "Crawling FantasyPros' web pages..."
    # start_time = timeit.default_timer()
    crawl_pros(Week)
    # elapsed = timeit.default_timer() - start_time
    # print "That took about %.2f sec" % elapsed
    #
    # print "Crawling ESPN's week pages..."
    # start_time = timeit.default_timer()
    crawl_espn(Week)
    # elapsed = timeit.default_timer() - start_time
    # print "That took about %.2f sec" % elapsed
    #
    # print "Crawling CBS' pages..."
    # start_time = timeit.default_timer()

    crawl_cbs(Week)
    # elapsed = timeit.default_timer() - start_time
    # print "That took about %.2f sec" % elapsed

    output_dict = {}
    for week in Week:
        output_dict[week] = []
        for player_name in Week[week]:
            output_dict[week].append(Week[week][player_name].toJSON())

    with open(FILE_PATH, 'w') as outfile:
        json.dump(output_dict, outfile)
        outfile.close()
    # print "Done with everything!"


try:
    scraped = open(FILE_PATH)
except IOError:
    execute_main()
    scraped = open(FILE_PATH)

print scraped.read()
scraped.close()


