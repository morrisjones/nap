#!/usr/bin/python

import sys
from gamefile import Gamefile
from subprocess import call
import os

__version_info__ = ('2017', '08', '20')
__version__ = '-'.join(__version_info__)
__cwd__ = os.path.dirname(os.path.realpath(__file__))

# Array of all read game files
games = []
# Array of all players
players = set()
# Qualifying dates
qualdates = {}

def collect_players(flight):
  for game in sorted(games):
    qd = game.get_qualdate()
    qp = game.qualified_players(flight)
    for p in qp:
      players.add(p)
      if p not in qualdates:
        qualdates[p] = set([qd])
      else:
        qualdates[p].add(qd)

def extract_json(gamefile):
  print "Script dir: %s" % __cwd__
  return

if __name__ == "__main__":
  import argparse

  parser = argparse.ArgumentParser(description='Create NAP qualifer list')
  parser.add_argument('gamefiles', type=str, 
      help="gamefile json file name, else stdin", nargs='*')
  parser.add_argument('-t', '--tree', 
      help="top directory of a tree of ACBLScore game files")
  parser.add_argument('-c', '--clubs', action="store_true", 
      help="Show info for clubs and games")
  parser.add_argument('-f', '--flight', action="append", default=[], 
      choices=("a","b","c"),
      help="Select A B or C to report qualifying players")
  parser.add_argument('-v', '--verbose', action="store_true",
      help="Include more verbose information in reports")
  parser.add_argument('-V', '--version', action="version", 
      version="%(prog)s ("+__version__+")")
  args = parser.parse_args()

  gamefile_tree = "./gamefiles"
  if args.tree:
    gamefile_tree = args.tree

  if gamefile_tree[0] != '/':
    gamefile_tree = __cwd__ + "/" + gamefile_tree

  if args.verbose:
    print "Gamefile tree: %s" % gamefile_tree

  if args.gamefiles:
    for filename in args.gamefiles:
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

