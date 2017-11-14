import requests
import urllib2
from bs4 import BeautifulSoup

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
#     for taken_player in soup.find_all(class_='playerName'):
#         taken_players.append(taken_player.string)

# print "Building available players..."
# available_players = []
# for i in range(0, 28):
#     offset = i*25+1
#     html_doc = urllib2.urlopen(NFL_PLAYERS_URL+str(offset)).read()
#     soup = BeautifulSoup(html_doc, 'html.parser')
#     for player in soup.find_all(class_='playerName'):
#         available_players.append(player.string)
# print "Done!"

html_doc = requests.get('https://www.fantasypros.com/nfl/projections/rb.php', stream=True).text
soup = BeautifulSoup(html_doc, 'html.parser')
for player in soup.find_all(class_='player-name'):
    print player.string
