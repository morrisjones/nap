#!/usr/bin/python

import json
from event import Event

class Gamefile(object):
  """Represents a gamefile imported using ACBLgamedump.pm from JSON

  Only has the attributes we're interested in for the NAP qualifier games
  """

  def __init__(self,json):
    self.gamefiledict = self.parse(json)
    self.events = []
    for e in self.gamefiledict:
      event = Event(e)
      self.events.append(event)

  def parse(self,jsonstring):
    gamefiledict = json.loads(jsonstring)
    return gamefiledict

  def pretty(self):
    print json.dumps(self.gamefiledict, sort_keys=True, indent=2, separators=(',', ': '))

  def get_club(self):
    return self.events[0].details[0].club

  def get_game_date(self):
    return self.events[0].details[0].date

  def table_count(self):
    entries = 0.0
    for section in self.events[0].details[0].sections:
      entries  += section.table_count()
    return entries
