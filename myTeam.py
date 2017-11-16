import json
import requests
import urllib2

import re

import pickle
from bs4 import BeautifulSoup

NFL_PROVIDER = 'nfl'
NFL_BASE_URL = 'http://fantasy.nfl.com/league/6009432/'
NFL_TEAM_URL = NFL_BASE_URL+'team/'
NFL_PLAYERS_URL = NFL_BASE_URL+'players?playerStatus=available&statCategory=projectedStats&offset='

NUMBER_FIRE_PROVIDER = 'number fire'
NUMBER_FIRE_BASE_URL = 'https://www.numberfire.com/nfl/fantasy/fantasy-football-projections'

FANTASY_PROS_PROVIDER = 'fantasy pros'
FANTASY_PROS_BASE_URL = 'https://www.fantasypros.com/nfl/projections/'

MY_TEAM_FILE = 'my_team.json'
TAKE_PLAYERS_FILE = 'taken_players.json'
AVAILABLE_PLAYERS_FILE = 'available_players.pkl'
IR_PLAYERS_FILE = 'ir_players.json'


class Projections:
    def __init__(self):
        self.nfl = 0
        self.number_fire = 0
        self.pros = 0

    def set_nfl(self, projection):
        self.nfl = projection

    def set_number_fire(self, projection):
        self.number_fire = projection

    def set_pros(self, projection):
        self.pros = projection


class Player:

    projections = dict()

    def __init__(self, pl_name, pl_position, pl_team):
        self.name = pl_name
        self.position = pl_position
        self.team = pl_team

    def add_projections(self, week, provider, projection):
        try:
            self.projections[week]
        except KeyError:
            self.projections[week] = Projections()

        if provider == NFL_PROVIDER:
            self.projections[week].set_nfl(projection)
        elif provider == NUMBER_FIRE_PROVIDER:
            self.projections[week].set_number_fire(projection)
        else:
            self.projections[week].set_pros(projection)


def parse_position_team(position_team):
    buffer_= position_team.split(' - ')
    position = buffer_[0]
    if len(buffer_) == 2:
        team = buffer_[1]
    else:
        team = "N/A"
    return position, team


def is_table_row(tag):
    return tag.has_attr('data-row-index')


try:
    my_team = json.load(open(MY_TEAM_FILE))
except IOError:
    print "Building my team..."
    html_doc = urllib2.urlopen(NFL_TEAM_URL + '1').read()
    soup = BeautifulSoup(html_doc, 'html.parser')
    my_team = []
    for my_player in soup.find_all(class_='playerName'):
        my_team.append(my_player.string)
    with open(MY_TEAM_FILE, 'w') as outfile:
        json.dump(my_team, outfile)
len_ = len(my_team)
if len_ is not 15:
    print "ERROR: Fix your roster!"
print "My team has %d players!" % len_

try:
    taken_players = json.load(open(TAKE_PLAYERS_FILE))
except IOError:
    print "Building taken players..."
    taken_players = []
    for i in range(2, 11):
        html_doc = urllib2.urlopen(NFL_TEAM_URL + str(i)).read()
        soup = BeautifulSoup(html_doc, 'html.parser')
        for taken_player in soup(class_='playerName'):
            taken_players.append(taken_player.string)
    with open(TAKE_PLAYERS_FILE, 'w') as outfile:
        json.dump(taken_players, outfile)
print "There are %d taken players" % len(taken_players)


try:
    available_players = pickle.load(open(AVAILABLE_PLAYERS_FILE))
    ir_players = json.load(open(IR_PLAYERS_FILE))
except IOError:
    print "Building available players and nfl projections..."
    available_players = {}
    ir_players = []
    for i in range(0, 28):
        offset = i*25+1
        html_doc = urllib2.urlopen(NFL_PLAYERS_URL+str(offset)).read()
        soup = BeautifulSoup(html_doc, 'html.parser')
        current_week = soup.find("div", class_="stat-type-nav").find("li", class_="selected").find("span", class_="text").string
        if re.match("\d", current_week) is None:
            raise Exception("Bad week")
        for row in soup('tr', class_=re.compile("player-\d")):
            player_name = row.find("a", class_="playerName").string
            pattern = "\w+|\w\.\w\. \w+"
            if re.match(pattern, player_name) is None:
                raise Exception("Bad name: %s, wanted: %s" % (player_name, pattern))

            player_position, player_team = parse_position_team(row.find("em").string)
            pattern = "\w\w"
            if re.match(pattern, player_position) is None:
                raise Exception("Bad position: %s, wanted: %s" % (player_position, pattern))
            if re.match(pattern, player_team) is None:
                if "N/A" in player_team:
                    # print "Free Agent: name-%s, position-%s" % (player_name, player_position)
                    continue
                raise Exception("Bad team: %s, wanted: %s" % (player_team, pattern))

            try:
                projected_points = row.find("span", class_="playerWeekProjectedPts").string
            except AttributeError:
                ir_players.append(player_name)
                # print "IR player: name-%s, pos-%s, team-%s" % (player_name, player_position, player_team)
                continue
            pattern = "\d+.\d+"
            if re.match(pattern, projected_points) is None:
                if "-" in projected_points:
                    # print "Out: name-%s, pos-%s, team-%s" % (player_name, player_position, player_team)
                    continue
                raise Exception("Bad points: %s, wanted: %s" % (projected_points, pattern))
            if float(projected_points) <= 1.0:
                break

            new_player = Player(player_name, player_position, player_team)
            new_player.add_projections(current_week, NFL_PROVIDER, projected_points)
            available_players[player_name] = new_player
            new_player, player_name, player_team, player_position, projected_points = None, None, None, None, None
    with open(AVAILABLE_PLAYERS_FILE, 'w') as outfile:
        pickle.dump(available_players, outfile)
    with open(IR_PLAYERS_FILE, 'w') as output_file:
        json.dump(ir_players, output_file)
map_length = len(available_players)
print "There are %d available players! And %d injured soldiers." % (map_length, len(ir_players))

html_doc = urllib2.urlopen(NUMBER_FIRE_BASE_URL).read()
soup = BeautifulSoup(html_doc, 'html.parser')
for row in soup(is_table_row):
    print row
    nf_name = row.find("span", class_='full').string
    _buffer = nf_name.split(" ")
    nf_name = _buffer[0] + " " + _buffer[1]
    if int(row["data-row-index"]) > map_length:
        break
    try:
        player = available_players[nf_name]
        # print "Hit on %s!" % nf_name
        continue
    except KeyError:
        if nf_name in taken_players:
            continue
        if nf_name in my_team:
            continue
        if nf_name in ir_players:
            continue
        print "Unknown player %s. I should probably create him" % nf_name


# html_doc = requests.get(FANTASY_PROS_BASE_URL+'rb.php', stream=True).text
# soup = BeautifulSoup(html_doc, 'html.parser')
# for player in soup(class_='player-name'):
#     print player.string

