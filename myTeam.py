import requests
import urllib2
from bs4 import BeautifulSoup, Tag


class Player:
    def __init__(self, pl_name, pl_position, pl_team):
        self.name = pl_name
        self.position = pl_position
        self.team = pl_team


NFL_BASE_URL = 'http://fantasy.nfl.com/league/6009432/'
NFL_TEAM_URL = NFL_BASE_URL+'team/'
NFL_PLAYERS_URL = NFL_BASE_URL+'players?offset='

# print "Building my team..."
# html_doc = urllib2.urlopen(NFL_TEAM_URL + '1').read()
# soup = BeautifulSoup(html_doc, 'html.parser')
# my_team = []
# for my_player in soup.find_all(class_='playerName'):
#     my_team.append(my_player.string)
# print "Done!"

# print "Building taken players..."
# taken_players = []
# for i in range(2, 11):
#     html_doc = urllib2.urlopen(NFL_TEAM_URL + str(i)).read()
#     soup = BeautifulSoup(html_doc, 'html.parser')
#     for taken_player in soup(class_='playerName'):
#         taken_players.append(taken_player.string)

# TODO:Get stat projections from all sites
print "Building available players..."
available_players = []
for i in range(0, 28):
    offset = i*25+1
    html_doc = urllib2.urlopen(NFL_PLAYERS_URL+str(offset)).read()
    soup = BeautifulSoup(html_doc, 'html.parser')
    for player in soup(class_='playerNameAndInfo'):
        name = player.next_element.next_element.next_element.next_element
        if type(name) == Tag:
            continue
        p_t_buffer = name.next_element.next_element.next_element
        position_team = p_t_buffer.split(' - ')
        position = position_team[0]
        if len(position_team) == 2:
            team = position_team[1]
        else:
            team = "N/A"
        available_players.append(Player(name, position, team))
print "Done!"

# html_doc = requests.get('https://www.fantasypros.com/nfl/projections/rb.php', stream=True).text
# soup = BeautifulSoup(html_doc, 'html.parser')
# for player in soup(class_='player-name'):
#     print player.string

# html_doc = urllib2.urlopen('https://www.numberfire.com/nfl/fantasy/fantasy-football-projections').read()
# soup = BeautifulSoup(html_doc, 'html.parser')
# for player in soup(class_='full'):
#     print player.string
