#!/usr/bin/python

import sys
from gamefile import Gamefile

# Array of all read game files
games = []
# Array of all players
players = []
# Array of all clubs
clubs = []

if __name__ == "__main__":
  import argparse

  parser = argparse.ArgumentParser(description='Create NAP qualifer list')
  parser.add_argument('input', type=str, help="gamefile json file name, else stdin", nargs='*')
  parser.add_argument('-c', '--clubs', action="store_true", help="Show info for clubs and games")
  args = parser.parse_args()

  if not args.input:
    gjson = sys.stdin.read()
    game = Gamefile(gjson)
    games.append(game)
  else:
    for filename in args.input:
      with open(filename,'r') as f:
        gjson = f.read()
      game = Gamefile(gjson)
      games.append(game)

  if args.clubs:
    for game in games:
      club = game.get_club()
      print "%s\t%s\t%s" % (club.number, club.name, game.get_game_date())

  sys.exit(0)

