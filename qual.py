#!/usr/bin/python

import sys
from player import Player
from gamefile import Gamefile

# Array of all players
players = []
# Array of all clubs

def process_game(game):
  if len(game.events) > 1:
    print "How unusual! More than one event in this game file."
  for e in game.events:
    print "File created: %s" % e.created
    for d in e.details:
      print "Club: %s" % d.club
      for s in d.sections:
        players.extend(s.players)
  return players

if __name__ == "__main__":
  import argparse

  parser = argparse.ArgumentParser(description='Create NAP qualifer list')
  parser.add_argument('input', type=str, help="gamefile json file name, else stdin", nargs='*')
  args = parser.parse_args()

  if not args.input:
    gjson = sys.stdin.read()
    game = Gamefile(gjson)
    process_game(game)
    sys.exit(0)

  for filename in args.input:
    with open(filename,'r') as f:
      gjson = f.read()
    game = Gamefile(gjson)

  players = process_game(game)
  for p in players:
    print "%s, %s" % (p.lname, p.fname)

  sys.exit(0)

