#!/usr/bin/python

import sys
from gamefile import Gamefile
from subprocess import check_output
import os
from os.path import join

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
  dump = join(__cwd__,"ACBLgamedump.pl")
  json = check_output([dump, gamefile])
  game = Gamefile(json)
  games.append(game)
  return

if __name__ == "__main__":
  import argparse

  parser = argparse.ArgumentParser(description='Create NAP qualifer list')
  parser.add_argument('gamefiles', type=str, 
      help="gamefile file name(s)", nargs='*')
  parser.add_argument('-t', '--tree', default="./gamefiles",
      help="top directory of a tree of ACBLScore game files (default=./gamefiles)")
  parser.add_argument('-c', '--clubs', action="store_true", 
      help="Show info for clubs and games")
  parser.add_argument('-f', '--flight', action="append", default=[], 
      choices=("a","b","c"),
      help="Select A B or C to report qualifying players")
  parser.add_argument('-v', '--verbose', action="store_true",
      help="Include more verbose information in reports")
  parser.add_argument('-s', '--summary', action="store_true",
      help="Generate the qualifier summary report")
  parser.add_argument('-V', '--version', action="version", 
      version="%(prog)s ("+__version__+")")
  args = parser.parse_args()

  # if gamefiles are specified on the command line, process those
  # otherwise look for gamefiles on the gamefile tree
  if args.gamefiles:
    for filename in args.gamefiles:
      extract_json(filename)
  else:
    if args.tree:
      gamefile_tree = args.tree

    if gamefile_tree[0] != '/':
      gamefile_tree = join(__cwd__,gamefile_tree)

    # Walk the gamefile tree and pass everything that looks like a 
    # gamefile to extract_json
    for root, dirs, files in os.walk(gamefile_tree):
      for f in files:
        extract_json(join(root,f))

  if args.clubs:
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

  if args.summary:
    print "\nSummary of NAP Qualifiers\n"
    fmt = "{:8} {:30} {:^4} {:^4} {:^4}"
    print fmt.format("Player#","Name","FltA","FltB","FltC")
    players.clear()
    for flight in ['a','b','c']:
      collect_players(flight)
    for p in sorted(players):
      flta = 'Q' if p.is_qual('a') else ' '
      fltb = 'Q' if p.is_qual('b') else ' '
      fltc = 'Q' if p.is_qual('c') else ' '
      print fmt.format(p.pnum,p.terse(),flta,fltb,fltc)

  sys.exit(0)

