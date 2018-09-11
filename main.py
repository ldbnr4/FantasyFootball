# import requests
import argparse
import datetime
import json

from cbs import crawl_cbs
from cbs import crawl_cbs_draft
# TODO: add statSeason=2016 to the end of nlf url for historical data or https://partners.fantasypros.com/api/v1/nfl-stats.php?week=10&year=2017
# TODO: look into duplicates of players when building dict
from espn import crawl_espn
from nfl import crawl_nfl_season
from number import crawl_number, crawl_number_ros
from pros import crawl_pros, crawl_pros_draft
from utils import write_draft_map_to_file, write_scrape_map_to_file

FILE_PATH = "projections/scraped_%s.json" % datetime.datetime.now().strftime("%m_%d_%Y")
# Week dictionary
Week = {}
# Players dictionary
# Players = {}


def execute_main():
    # start_time = timeit.default_timer()
    # print "Crawling nfl's pages..."
    crawl_nfl_season(Week)
    # print "Done with NFL!"

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
            output_dict[week].append(Week[week][player_name].to_json())

    with open(FILE_PATH, 'w') as outfile:
        json.dump(output_dict, outfile)
        outfile.close()
    # print "Done with everything!"


parser = argparse.ArgumentParser(description='Get fantasy projections.')
parser.add_argument('-s', '--season', action='store_true', default=False)
# parser.add_argument('-w', '--week', action='store', type=int, default=-1)
parser.add_argument('-v', '--verbose', action='store_true', default=False)
# parser.add_argument('integers', metavar='N', type=int, nargs='+',
#                     help='an integer for the accumulator')
# parser.add_argument('--sum', dest='accumulate', action='store_const',
#                     const=sum, default=max,
#                     help='sum the integers (default: find the max)')

args = parser.parse_args()
verbose = args.verbose
players_map = {}
# week = args.week
if args.season:
    crawl_nfl_season(players_map, verbose=verbose)
    crawl_cbs_draft(players_map, verbose=verbose)
    crawl_number_ros(players_map, verbose)
    crawl_pros_draft(players_map, verbose)
    write_draft_map_to_file(players_map, 'season.json')
else:
    # crawl_nfl(players_map, verbose)
    crawl_cbs(players_map, verbose)
    write_scrape_map_to_file(players_map, 'scrape.json')

# print args.season
# try:
#     scraped = open(FILE_PATH)
# except IOError:
#     execute_main()
#     scraped = open(FILE_PATH)
#
# print scraped.read()
# scraped.close()
#
#
