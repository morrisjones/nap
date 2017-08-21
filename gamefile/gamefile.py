#!/usr/bin/python

import json
from event import Event
from qualdate import QualDate

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

  def __str__(self):
    fmt = 'Game:\n  Name:   {0}\n  Number: {1}\n  Date:   {2}\n'
    return fmt.format(self.get_club().name, self.get_club().number, self.get_game_date())

  def __cmp__(self,other):
    me = self.get_qualdate().ptime
    him = other.get_qualdate().ptime
    if me > him:
      return 1
    if me < him:
      return -1
    else:
      return 0

  def parse(self,jsonstring):
    gamefiledict = json.loads(jsonstring)
    return gamefiledict

  def pretty(self):
    print json.dumps(self.gamefiledict, sort_keys=True, indent=2, separators=(',', ': '))

  def get_club(self):
    return self.events[0].details[0].club

  def get_strats(self):
    return self.events[0].details[0].strats

  def get_game_date(self):
    return self.events[0].details[0].date

  def get_qualdate(self):
    return QualDate(self.get_club(),self.get_game_date())

  def table_count(self):
    entries = 0.0
    for section in self.events[0].details[0].sections:
      entries  += section.table_count()
    return entries

  def get_sections(self):
    sections = []
    for event in self.events:
      for detail in event.details:
        for section in detail.sections:
          sections.append(section)
    return sections

  def qualified_players(self,flight):
    qp = []
    for section in self.get_sections():
      for player in section.players:
        if player.is_qual(flight):
          qp.append(player)
    return qp

