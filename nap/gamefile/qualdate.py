#!/usr/bin/python

from datetime import datetime

class QualDate(object):
  """This probably could have been a tuple, but it's a useful abstraction
  of a qualifying game, including the club and date. The club field is 
  expected to be of type Club, which includes the club number and name.
  """

  def __init__(self,club,date):
    self.club = club
    self.date = date
    self.ptime = datetime.strptime(date,"%B %d, %Y")

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
    return "{0} {1}".format(self.ptime.strftime("%x"),self.club)
