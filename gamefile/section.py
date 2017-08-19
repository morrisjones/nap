#!/usr/bin/python

from player import Player

class Section(object):

  def __init__(self,letter,section_dict):
    self.letter = letter
    self.section_dict = section_dict
    self.players = []
    self.entries = self.section_dict['entry']
    for seat in self.entries.keys():
      entry = self.entries[seat]
      strat_num = entry['strat_num']
      players = entry['player']
      ranks = entry['rank']
      for p in players:
        player = Player(p['lname'],p['fname'],p['pnum'])
        player.set_qual('a',ranks[0]['qual_flag'] > 0)
        if 1 < strat_num:
          player.set_qual('b',ranks[1]['qual_flag'] > 0)
        if 2 < strat_num:
          player.set_qual('c',ranks[2]['qual_flag'] > 0)
        self.players.append(player)

  def table_count(self):
    return len(self.entries.keys()) / 2.0
