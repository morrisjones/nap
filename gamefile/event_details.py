#!/usr/bin/python

from club import Club
from section import Section

class EventDetails(object):

  def __init__(self,details_dict):
    self.details_dict = details_dict
    self.club = Club(details_dict['club'],details_dict['club_num'])
    self.date = details_dict['date']
    self.sections = []
    for k in details_dict['section'].keys():
      self.sections.append(Section(k,details_dict['section'][k]))
