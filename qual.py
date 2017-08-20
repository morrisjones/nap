#!/usr/bin/python

import sys
from gamefile import Gamefile

# Array of all read game files
games = []
# Array of all players
players = set()
# Qualifying dates
qualdates = {}

def collect_players(flight):
  for game in sorted[games]:
    qd = game.get_qualdate()
    qp = game.qualified_players(flight)
    for p in qp:
      players.add(p)
      if p not in qualdates:
        qualdates[p] = set([qd])
      else:
        qualdates[p].add(qd)

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
  parser.add_argument('-v', '--verbose', action="store_true",
      help="Include more verbose information in reports")
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
    if args.verbose:
      print "{:8} {:30} {:17}    {:5}".format("Club No.","Club Name","Game Date","Tables")
    for game in sorted(games):
      club = game.get_club()
      print "{:8} {:30} {:17}    {:5}".format(club.number,club.name,game.get_game_date(), game.table_count())

  for flight in args.flight:
    players.clear()
    qualdates.clear()
    if args.verbose:
      print "\nQualifiers in Flight %s\n" % flight.upper()
    collect_players(flight)
    for p in sorted(players):
      print p
      if args.verbose:
        for qd in sorted(qualdates[p]):
          print "            %s" % qd

  sys.exit(0)

