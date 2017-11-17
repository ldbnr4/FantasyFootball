# import requests
import re
import sys
import urllib2

from bs4 import BeautifulSoup

NFL_PROVIDER = 'nfl'
NFL_BASE_URL = 'http://fantasy.nfl.com/league/6009432/'
NFL_TEAM_URL = NFL_BASE_URL + 'team/%d?statCategory=projectedStats'
NFL_PLAYERS_URL = NFL_BASE_URL + 'players?playerStatus=available&statCategory=projectedStats&offset=%d'

NUMBER_FIRE_PROVIDER = 'number fire'
NUMBER_FIRE_BASE_URL = 'https://www.numberfire.com/nfl/fantasy/fantasy-football-projections'
NUMBER_FIRE_FILE = 'projections/number_fire.html'

FANTASY_PROS_PROVIDER = 'fantasy pros'
FANTASY_PROS_BASE_URL = 'https://www.fantasypros.com/nfl/projections/'

MY_TEAM_FILE = 'players/mine.html'
TAKE_PLAYERS_FILE = 'players/taken/taken_page_%d.html'
AVAILABLE_PLAYERS_FILE = 'players/available/available_page_%d.html'


class Projections:
    def __init__(self):
        self.nfl = 0
        self.number_fire = 0
        self.pros = 0

    def set_nfl(self, projection):
        self.nfl = float(projection)

    def set_number_fire(self, projection):
        self.number_fire = float(projection)

    def set_pros(self, projection):
        self.pros = float(projection)


class Player:
    def __init__(self, pl_name, pl_position, pl_team):
        self.name = pl_name
        self.position = pl_position
        self.team = pl_team
        self.projections = dict()

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
    buffer_ = position_team.split(' - ')
    position = buffer_[0]
    if len(buffer_) == 2:
        team = buffer_[1]
    else:
        team = "N/A"
    return position, team


def is_table_row(tag):
    return tag.has_attr('data-row-index')


def build_nfl_player_with_projections(_soup, _current_week, _map, individual=False, lower_bound=sys.float_info.min):
    _not_playing = []
    if re.match("\d", _current_week) is None:
        raise Exception("Bad week")
    _current_week = int(_current_week)
    match = re.compile("^player-\d+")
    if individual:
        match = re.compile("^player-\d+-\d+")
    rows = _soup('tr', class_=match)
    if len(rows) is not 15 and individual:
        raise Exception("Bad matching for rows")
    for _row in rows:
        player_name = _row.find("a", class_="playerName").string
        pattern = "\w+|\w\.\w\. \w+"
        if re.match(pattern, player_name) is None:
            raise Exception("Bad name: %s, wanted: %s" % (player_name, pattern))

        player_position, player_team = parse_position_team(_row.find("em").string)
        pattern = "\w\w|\w"
        if re.match(pattern, player_position) is None:
            raise Exception("Bad position: %s, wanted: %s" % (player_position, pattern))
        if re.match(pattern, player_team) is None:
            if "N/A" in player_team:
                _not_playing.append(player_name)
                # print "Free Agent: name-%s, position-%s" % (player_name, player_position)
                continue
            raise Exception("Bad team: %s, wanted: %s" % (player_team, pattern))

        try:
            projected_points = _row.find("span", class_="playerWeekProjectedPts").string
        except AttributeError:
            _not_playing.append(player_name)
            # print "IR player: name-%s, pos-%s, team-%s" % (player_name, player_position, player_team)
            continue
        pattern = "\d+.\d+"
        if re.match(pattern, projected_points) is None:
            if "-" in projected_points:
                _not_playing.append(player_name)
                # print "Out: name-%s, pos-%s, team-%s" % (player_name, player_position, player_team)
                continue
            raise Exception("Bad points: %s, wanted: %s" % (projected_points, pattern))
        if float(projected_points) <= 1.0 and not individual:
            break

        new_player = Player(player_name, player_position, player_team)
        new_player.add_projections(_current_week, NFL_PROVIDER, projected_points)
        _map[player_name] = new_player
        if sum(map(lambda _p: _p.projections[int(current_week)].nfl, _map.viewvalues())) / len(_map) < lower_bound:
            return _not_playing
    # print len(_map)
    return _not_playing


try:
    with open(MY_TEAM_FILE) as infile:
        html_doc = infile.read()
        infile.close()
except IOError:
    print "Downloading my team's web page..."
    html_doc = urllib2.urlopen(NFL_TEAM_URL % 1).read()
    with open(MY_TEAM_FILE, 'w') as outfile:
        outfile.write(html_doc)
        outfile.close()
# print "Building my team with nfl projections..."
soup = BeautifulSoup(html_doc, 'html.parser')
my_team = {}
current_week = soup.find("div", class_="stat-type-nav").find("li", class_="selected").find("span", class_="text").string
if re.match("\d+", current_week) is None:
    raise Exception("Bad week")
not_playing = build_nfl_player_with_projections(soup, current_week, my_team, True)
len_my_team = len(my_team)
if len_my_team is not 15:
    print "Houston, Fix your roster!"
nlf_team_projections = map(lambda _p: _p.projections[int(current_week)].nfl, my_team.viewvalues())
team_ave = sum(nlf_team_projections)/len_my_team
team_lower_bound = min(nlf_team_projections)
print "My nfl team average is %.2f this week! With a lower bound of %.2f" % (team_ave, team_lower_bound)


# taken_players_files = []
# try:
#     for i in range(2, 11):
#         with open(TAKE_PLAYERS_FILE % i) as infile:
#             taken_players_files.append(infile.read())
#             infile.close()
# except IOError:
#     print "Downloading my opponent teams web pages..."
#     for i in range(2, 11):
#         html_doc = urllib2.urlopen(NFL_TEAM_URL % i).read()
#         taken_players_files.append(html_doc)
#         with open(TAKE_PLAYERS_FILE % i, 'w') as outfile:
#             outfile.write(html_doc)
#             outfile.close()
# taken_players = {}
# for i in range(0, 9):
#     soup = BeautifulSoup(taken_players_files[i], 'html.parser')
#     current_week = soup.find("div", class_="stat-type-nav").find("li", class_="selected").find("span",
#                                                                                                class_="text").string
#     result = build_nfl_player_with_projections(soup, current_week, taken_players, True)
#     for p in result:
#         not_playing.append(p)
# len_taken = len(taken_players)
# print "There are %d taken active players!" % len_taken
# if len_taken + len(not_playing) is not 135:
#     print "Houston, someone does not a have a full roster!"

available_players_files = []
try:
    for i in range(0, 6):
        with open(AVAILABLE_PLAYERS_FILE % i) as infile:
            available_players_files.append(infile.read())
            infile.close()
except IOError:
    print "Downloading available players pages..."
    for i in range(0, 6):
        offset = i * 25
        html_doc = urllib2.urlopen(NFL_PLAYERS_URL % offset).read()
        available_players_files.append(html_doc)
        with open(AVAILABLE_PLAYERS_FILE % i, 'w') as outfile:
            outfile.write(html_doc)
            outfile.close()
available_players = {}
for i in range(0, 6):
    soup = BeautifulSoup(available_players_files[i], 'html.parser')
    current_week = soup.find("div", class_="stat-type-nav").find("li", class_="selected").find("span",
                                                                                               class_="text").string
    result = build_nfl_player_with_projections(soup, current_week, available_players, False, team_lower_bound)
    for p in result:
        not_playing.append(p)
available_len = len(available_players)
available_ave = sum(map(lambda _p: _p.projections[int(current_week)].nfl, available_players.viewvalues()))/available_len
print "The available nfl average is %.2f this week!" % available_ave

try:
    with open(NUMBER_FIRE_FILE) as input_file:
        html_doc = input_file.read()
        input_file.close()
except IOError:
    print "Downloading NumberFire web page..."
    html_doc = urllib2.urlopen(NUMBER_FIRE_BASE_URL).read()
    with open(NUMBER_FIRE_FILE, 'w') as outfile:
        outfile.write(html_doc)
        outfile.close()
soup = BeautifulSoup(html_doc, 'html.parser')
current_week = int(soup.find("div", class_="projection-rankings__hed").find("h2").string.strip().split(" ")[1])
names = True
nf_my_names = {}
# nf_taken_names = {}
nf_available_names = {}
values = []
for row in soup(is_table_row):
    current_index = int(row["data-row-index"])
    if current_index > available_len + 135 + len_my_team:
        names = False
        continue
    if names:
        nf_name = row.find("span", class_='full').string
        _buffer = nf_name.split(" ")
        nf_name = _buffer[0] + " " + _buffer[1]
        if nf_name in my_team:
            nf_my_names[current_index] = nf_name
        elif nf_name in available_players:
            nf_available_names[current_index] = nf_name
        else:
            continue
            print "Unknown player %s. I might want to create him" % nf_name
    else:
        if current_index in nf_my_names:
            player = my_team[nf_my_names[current_index]]
        elif current_index in nf_available_names:
            player = available_players[nf_available_names[current_index]]
        else:
            continue
        value = float(row.find("td", class_="nf_fp").string)
        values.append(value)
        nf_team_projections = map(lambda _p: _p.projections[int(current_week)].number_fire, my_team.viewvalues())
        nf_team_projections.append(team_lower_bound)
        team_lower_bound = min(i for i in nf_team_projections if i > 0)
        # print min(values)
        values_ave = sum(values)/len(values)
        if values_ave < team_lower_bound:
            break
        player.add_projections(current_week, NUMBER_FIRE_PROVIDER, value)
nf_team_ave = sum(map(lambda _p: _p.projections[int(current_week)].number_fire, my_team.viewvalues()))/len_my_team
print "My numberFire team average is %.2f this week! With a lower bound of %.2f" % (nf_team_ave, team_lower_bound)
print "The available numberFire average is %.2f this week!" % values_ave

# html_doc = requests.get(FANTASY_PROS_BASE_URL+'rb.php', stream=True).text
# soup = BeautifulSoup(html_doc, 'html.parser')
# for player in soup(class_='player-name'):
#     print player.string
