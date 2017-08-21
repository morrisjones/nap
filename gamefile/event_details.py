#!/usr/bin/python

from club import Club
from section import Section
from strat import Strat

class EventDetails(object):
  """The useful fields in the EventDetails are club name and number, and
  game date. The array of sections is valuable, and where most useful player
  data is held.
  """

  def __init__(self,details_dict):
    self.details_dict = details_dict
    self.club = Club(details_dict['club'],details_dict['club_num'])
    self.date = details_dict['date']

    # Load the strats array
    self.strats = []
    for s in details_dict['strat']:
      self.strats.append(Strat(s))

    # Create a map of strats to rank indexes for the players
    rank_idx_to_strat = {}
    for idx in range(0,len(self.strats)):
      rank_idx_to_strat[idx] = self.map_rank_index_to_strat(idx)

    # Load the sections array with the rank map
    self.sections = []
    for k in details_dict['section'].keys():
      self.sections.append(Section(k,details_dict['section'][k],rank_idx_to_strat))

  def map_rank_index_to_strat(self,rank_index):
    strat = self.strats[rank_index]
    return strat.letter.lower()

