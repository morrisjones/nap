#!/usr/bin/python

from club import Club
from section import Section

class EventDetails(object):
  """The useful fields in the EventDetails are club name and number, and
  game date. The array of sections is valuable, and where most useful player
  data is held.
  """

  def __init__(self,details_dict):
    self.details_dict = details_dict
    self.club = Club(details_dict['club'],details_dict['club_num'])
    self.date = details_dict['date']
    self.sections = []
    for k in details_dict['section'].keys():
      self.sections.append(Section(k,details_dict['section'][k]))
