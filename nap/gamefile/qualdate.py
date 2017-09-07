from datetime import datetime
from gfutils import GFUtils

class QualDate(object):
  """Descriptor for a player's qualifying event.

  Attributes:
    club: A Club object, which includes name and number
    date: A date string, in long form, en_us formatted
    sdate: Short date in local format
    ptime: A python datetime object, more useful for sorting
  """

  def __init__(self,club,date,session=22):
    self.club = club
    self.date = date
    self.ptime = datetime.strptime(date,"%B %d, %Y")
    self.sdate = self.ptime.strftime("%x")
    self.session = GFUtils.SESSION_STRING[session]

  def __key(self):
    return (self.club,self.date)

  def __hash__(self):
    return hash(self.__key())

  def _eq__(self,other):
    return self.__key() == other.__key()

  def __cmp__(self,other):
    if self.ptime > other.ptime:
      return 1
    elif self.ptime < other.ptime:
      return -1
    else:
      return 0

  def __str__(self):
    return "{0} {1} {2}".format(self.sdate,self.session,self.club)
