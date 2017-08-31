import json
import string
import os
import re
from event import Event
from qualdate import QualDate
from gamefile_exception import GamefileException

class Gamefile(object):
  """Top of an object tree that represents and ACBLscore game file

  Attributes:
    gamefiledict: The raw JSON dictionary provided by ACBLgamedump
    events: Array of Event objects. In practice our game files only include
        a single Event, so it has to be referenced as events[0].

  """

  def __init__(self,filename,is_csv=False):
    if is_csv:
      try:
        self.parse_csv(filename)
      except GamefileException:
        raise
      # except Exception, e:
      #   raise GamefileException(e)
      return
    else:
      try:
        self.gamefiledict = self.parse(filename)
      except Exception, e:
        raise GamefileException(e)
      self.events = []
      for e in self.gamefiledict:
        event = Event(e)
        self.events.append(event)

  def parse_csv(self,pathname):
    """Parse a CSV file found in the gamefile_tree

    These tend to have a very specific filename format that we can use to deduce the
    club number and club name. Missing things include the game date, table count, and
    many other things. We'll have to make do.

    :param pathname: Full path name to the CSV file
    :return: None
    """
    print "CSV file found"
    print "pathname: %s" % pathname
    filename = string.split(pathname, os.sep)[-1]
    print "filename: %s" % filename
    clubname = string.split(pathname, os.sep)[-2]
    print "clubname: %s" % clubname
    pattern = re.compile("NAOP (\d+)-(\d+)")
    match = pattern.match(filename)
    club_num = match.group(1)
    print "club_num: %s" % club_num
    game_year = match.group(2)
    print "game_year: %s" % game_year

    club_name_split = re.split('-',clubname)
    new_club_name = []
    for w in club_name_split:
      new_club_name.append(w[0].upper() + w[1:])
    club_name = " ".join(new_club_name)
    print club_name

    game_dict = []
    event_dict = {
      'decode_format_version': 'not_relevant',
      'filename': pathname,
      'creation_timestamp': os.path.getmtime(pathname),
      'event': []
    }
    game_dict.append(event_dict)
    event_details_dict = {
      'club': club_name,
      'club_num': club_num,
      'date': game_year,
      'club_session_num': 22,
      'rating': 'NAP Club level',
      'strat': [{
        'max_mp': '0',
        'letter': 'A',
      },{
        'max_mp': '2500',
        'letter': 'B',
      },{
        'max_mp': 'NLM',
        'letter': 'C',
      }],
      'section': {
        'A': {
          '1N': {

          }
        }
      },
    }
    event_dict['event'].append(event_details_dict)
    self.events = []
    self.events.append(Event(event_dict))

    # TODO populate the section array with players from the CSV file

    return

  def __key(self):
    """Key to a unique game file.
    
    A unique game is identified by the club number, game date, and club 
    session number.
    """
    return (self.get_club().number, self.get_game_date(), 
        self.get_club_session_num())
    
  def get_key(self):
    """Public access to the game file key"""
    return self.__key()

  def __str__(self):
    fmt = "{:8} {:30} {:17} {:<8} {:>5}"
    return fmt.format(self.get_club().number, self.get_club().name, self.get_game_date(),
        self.session_string[self.get_club_session_num()], self.table_count())

  def __cmp__(self,other):
    """Natural ordering for game files
    
    Sort by game date first, then by club session number. The session number will
    distinguish between games played on the same date.
    """
    me = self.get_qualdate().ptime
    him = other.get_qualdate().ptime
    if me > him:
      return 1
    if me < him:
      return -1
    else:
      if self.get_club_session_num() > other.get_club_session_num():
        return 1
      if self.get_club_session_num() < other.get_club_session_num():
        return -1
      else:
        return 0

  def parse(self,jsonstring):
    gamefiledict = json.loads(jsonstring)
    return gamefiledict

  def pretty(self):
    """A debugging tool, pretty-prints the defining game file dict as JSON"""
    print json.dumps(self.gamefiledict, sort_keys=True, indent=2, separators=(',', ': '))

  def get_club(self):
    """Return a Club object connected to this Gamefile"""
    return self.events[0].details[0].club

  def get_strats(self):
    """Return the array of Strat objects for this game's event"""
    return self.events[0].details[0].strats

  def get_game_date(self):
    """Helper to return the game date from EventDetails"""
    return self.events[0].details[0].date

  def get_club_session_num(self):
    """Club session number refers to day of week and time of day"""
    return self.events[0].details[0].club_session_num

  def get_event_details(self):
    """Returns the EventDetails object related to this game"""
    return self.events[0].details[0]

  def get_club_num(self):
    """The unique club number for this bridge club."""
    return self.get_club().number

  def get_qualdate(self):
    """The club and date of this game, for reporting player qualifiers."""
    return QualDate(self.get_club(),self.get_game_date())

  def get_rating(self):
    """The game rating string from EventDetails"""
    return self.events[0].details[0].rating

  def table_count(self):
    """Returns the table count for all sections of this game"""
    entries = 0.0
    for section in self.events[0].details[0].sections:
      entries  += section.table_count()
    return entries

  def get_sections(self):
    """Get the Sections array for this game"""
    sections = []
    for event in self.events:
      for detail in event.details:
        for section in detail.sections:
          sections.append(section)
    return sections

  def qualified_players(self,flight):
    """List of qualified players for a given flight

    Args:
      flight: One character from {'a', 'b', 'c'} that indicates the flight
    """
    qp = []
    for section in self.get_sections():
      for player in section.players:
        if player.is_qual(flight):
          qp.append(player)
    return qp

  def all_players(self):
    """Get all individual Player objects, qualifiers and not"""
    plrs = []
    for section in self.get_sections():
      for player in section.players:
        plrs.append(player)
    return plrs

  # Mapping between club session numbers and day/time
  session_string = {
    1: 'Mon AM',
    2: 'Mon Aft',
    3: 'Mon Eve',
    4: 'Tue AM',
    5: 'Tue Aft',
    6: 'Tue Eve',
    7: 'Wed AM',
    8: 'Wed Aft',
    9: 'Wed Eve',
    10: 'Thu AM',
    11: 'Thu Aft',
    12: 'Thu Eve',
    13: 'Fri AM',
    14: 'Fri Aft',
    15: 'Fri Eve',
    16: 'Sat AM',
    17: 'Sat Aft',
    18: 'Sat Eve',
    19: 'Sun AM',
    20: 'Sun Aft',
    21: 'Sun Eve',
    22: '(Other)',
  }

