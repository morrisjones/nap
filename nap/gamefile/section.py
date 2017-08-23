#!/usr/bin/python

from player import Player

class Section(object):
  """Here is the most useful data of players and qualifying flags.
  The value of qual_flag is 0 if not qualified, or an integer that is
  the rank of the qualifier. I.e., a qual_flag value of '1' is the top
  qualifier in the section, '2' is the second, etc.

  The rank array has a number of elements that match the flight of the
  player's game results. rank[0] is results for flight A, rank[1] for
  flight B, etc.
  """

  def __init__(self,letter,section_dict,rank_idx_to_strat):
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
        player.set_qual(rank_idx_to_strat[0],ranks[0]['qual_flag'] > 0)
        if 1 < strat_num:
          player.set_qual(rank_idx_to_strat[1],ranks[1]['qual_flag'] > 0)
        if 2 < strat_num:
          player.set_qual(rank_idx_to_strat[2],ranks[2]['qual_flag'] > 0)
        self.players.append(player)

  def table_count(self):
    return len(self.entries.keys()) / 2.0
