#!/usr/bin/python

import sys
from gamefile import Gamefile

# Array of all read game files
games = []
# Array of all players
players = []
# Array of all clubs
clubs = []

def collect_players(flight):
  players = set()
  for game in games:
    qp = game.qualified_players(flight)
    for p in qp:
      players.add(p)
  for p in sorted(qp):
    print p

if __name__ == "__main__":
  import argparse

  parser = argparse.ArgumentParser(description='Create NAP qualifer list')
  parser.add_argument('input', type=str, 
      help="gamefile json file name, else stdin", nargs='*')
  parser.add_argument('-c', '--clubs', action="store_true", 
      help="Show info for clubs and games")
  parser.add_argument('-f', '--flight', action="append", default=[], 
      choices=("a","b","c"),
      help="Select A B or C to report qualifying players")
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
      print "%s\t%s\t%s\t%s" % (club.number, club.name, game.get_game_date(), game.table_count())

  if len(args.flight) > 0:
    for flight in args.flight:
      collect_players(flight)

  sys.exit(0)

