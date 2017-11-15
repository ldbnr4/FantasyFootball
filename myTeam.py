import requests
import urllib
import urllib2
from bs4 import BeautifulSoup, Tag

NFL_BASE_URL = 'http://fantasy.nfl.com/league/6009432/'
NFL_TEAM_URL = NFL_BASE_URL+'team/'
NFL_PLAYERS_URL = NFL_BASE_URL+'players?playerStatus=available&statCategory=projectedStats&offset='
NFL_PROVIDER = 'nfl'

NUMBER_FIRE_PROVIDER = 'number fire'
FANTASY_PROS_PROVIDER = 'fantasy pros'

class Projections:
    # def __init__(self, nfl, number_fire, pros):
    #     self.nfl = nfl
    #     self.number_fire = number_fire
    #     self.pros = pros

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

    projections = {}

    def __init__(self, pl_name, pl_position, pl_team):
        self.name = pl_name
        self.position = pl_position
        self.team = pl_team

    def add_projections(self, week, provider, projection):
        if provider == NFL_PROVIDER:
            self.projections[week].set_nfl(projection)
        elif provider == NUMBER_FIRE_PROVIDER:
            self.projections[week].set_number_fire(projection)
        else:
            self.projections[week].set_pros(projection)


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
    for row in soup('tr'):
        print row
        # name = player.next_element.next_element.next_element.next_element
        # if type(name) == Tag:
        #     continue
        # p_t_buffer = name.next_element.next_element.next_element
        # position_team = p_t_buffer.split(' - ')
        # position = position_team[0]
        # if len(position_team) == 2:
        #     team = position_team[1]
        # else:
        #     team = "N/A"
        # available_players.append(Player(name, position, team))
print "Done!"

# html_doc = requests.get('https://www.fantasypros.com/nfl/projections/rb.php', stream=True).text
# soup = BeautifulSoup(html_doc, 'html.parser')
# for player in soup(class_='player-name'):
#     print player.string

# html_doc = urllib2.urlopen('https://www.numberfire.com/nfl/fantasy/fantasy-football-projections').read()
# soup = BeautifulSoup(html_doc, 'html.parser')
# for player in soup(class_='full'):
#     print player.string
