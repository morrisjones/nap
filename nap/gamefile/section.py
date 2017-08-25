#!/usr/bin/python

from player import Player

class Section(object):
  """Represents one section of play at an ACBL bridge club.

  Attributes:
    section_dict: The raw JSON dictionary from ACBLgamedump
    letter: Each section is reprented by a capital letter, sometimes
        a repeated letter if there could be more than 26 sections at
        an event.
    players: Array of all individual players in the section
    entries: An "entry" in a section is a pair of players. A pair qualifies
        together in the game, but the qualification applies to the
        individual members of the partnership.

  During the construction of this object, the Players are separated
  out from the Entries, and tested to have a qual_flag value greater
  than zero.

  The value of qual_flag is 0 if not qualified, or an integer that is
  the rank of the qualifier, i.e., a qual_flag value of '1' is the top
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
    """Returns the count of tables in the section, as entries / 2"""
    return len(self.entries.keys()) / 2.0
