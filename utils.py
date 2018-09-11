import json
import os
from stat import ST_MTIME, S_ISREG, ST_MODE

POSITIONS = ['qb', 'rb', 'wr', 'te', 'k']


def get_latest_file(file_path):
    # get all entries in the directory w/ stats
    entries = (os.path.join(file_path, fn) for fn in os.listdir(file_path))
    entries = ((os.stat(path), path) for path in entries)

    # leave only regular files, insert creation date
    entries = ((stat[ST_MTIME], path)
               for stat, path in entries if S_ISREG(stat[ST_MODE]))
    sorted_files = sorted(entries)
    return sorted_files[len(sorted_files) - 1][1]


def write_draft_map_to_file(player_map, file_path):
    output_dict = []
    # for week in player_map:
    #     output_dict[week] = []
    for player_name in player_map:
        player = player_map[player_name]
        player.set_ave()
        player.set_smart_ave()
        player.set_deviation()
        player.set_smart_deviation()
        output_dict.append(player.to_json())

    with open(file_path, 'w') as outfile:
        json.dump(output_dict, outfile)
        outfile.close()


def write_scrape_map_to_file(player_maps, file_path):
    output_dict = {}
    for week in player_maps:
        week_players = player_maps[week]
        week_players_arr = []
        for player_name in week_players:
            player = week_players[player_name]
            player.set_ave()
            player.set_smart_ave()
            player.set_deviation()
            player.set_smart_deviation()
            week_players_arr.append(player.to_json())
        output_dict[week] = week_players_arr

    with open(file_path, 'w') as outfile:
        json.dump(output_dict, outfile)
        outfile.close()
