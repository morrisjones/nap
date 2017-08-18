#!/usr/bin/python

import json
import argparse
import sys

def get_input():
  return json.load(sys.stdin)

if __name__ == '__main__':
  games = get_input()
  print "Number of games: %s" % (len(games))
  for game in games:
    event = game['event'][0]
    print "Sections in the event:"
    sections = event['section']
    for letter in sections.keys():
      print "Section %s:" % letter
      section = sections[letter]
      entry = section['entry']
      for seat in entry.keys():
        player = entry[seat]
        letter = ['','A','B','C'][player['strat_num']]
        print "\n\nSeat: %s strat: %s" % (seat, player['strat_num'])
        for idx, rank in enumerate(player['rank']):
          letter = ['A','B','C'][idx]
          print "  Strat %s qual %s" % (letter, rank['qual_flag'])

