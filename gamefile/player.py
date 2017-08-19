#!/usr/bin/python

from qualdate import QualDate

class Player(object):
  """Object representing an ACBL member

  Attributes:
    fname
    lname
    pnum
    mp_total
    acbl_rank_letter
  """

  def __init__(self, lname, fname, pnum=''):
    self.lname = lname
    self.fname = fname
    self.pnum = pnum
    self.a_flight = False
    self.b_flight = False
    self.c_flight = False
    self.qualdates = []

  def __hash__(self):
    return hash(self.lname + self.fname + self.pnum)

  def __cmp__(self,other):
    if self.lname != other.lname:
      if self.lname > other.lname:
        return 1
      else:
        return -1
    if self.fname != other.fname:
      if self.fname > other.fname:
        return 1
      else:
        return -1
    return 0

  def __str__(self):
    name = self.lname + ", " + self.fname
    fmt = '{name:25} {pnum:8}'
    out = fmt.format(name=name, pnum=self.pnum)
    for qualdate in self.qualdates:
      out += '    {:18} {:25}'.format(qualdate.date,qualdate.club.name)
    return out
    
  def set_qual(self,flight,qual):
    if flight == 'a':
      self.a_flight = qual
    elif flight == 'b':
      self.b_flight = qual
    elif flight == 'c':
      self.c_flight = qual

  def is_qual(self,flight):
    if flight == 'a':
      return self.a_flight
    elif flight == 'b':
      return self.b_flight
    elif flight == 'c':
      return self.c_flight
    else:
      return False

  def add_qualdate(self,club,date):
    qd = QualDate(club,date)
    self.qualdates.append(qd)

