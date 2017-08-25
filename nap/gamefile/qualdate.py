from datetime import datetime

class QualDate(object):
  """Descriptor for a player's qualifying event.

  Attributes:
    club: A Club object, which includes name and number
    date: A date string, in long form, en_us formatted
    sdate: Short date in local format
    ptime: A python datetime object, more useful for sorting
  """

  def __init__(self,club,date):
    self.club = club
    self.date = date
    self.ptime = datetime.strptime(date,"%B %d, %Y")
    self.sdate = self.ptime.strftime("%x")

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
    fmt = "{date} {club}"
    return "{0} {1}".format(self.sdate,self.club)
