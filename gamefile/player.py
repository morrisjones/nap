#!/usr/bin/python

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

  def __hash__(self):
    return (self.lname + self.fname + self.pnum).hash()

  def __eq__(self,other):
    return self.__hash__() == other.__hash__()

  def __cmp__(self,other):
    if self.lname != other.lname:
      return self.lname > other.lname
    if self.fname != other.fname:
      return self.fname > other.fname
    return 0

  def set_qual(self,flight,qual):
    if flight == 0:
      self.a_flight = qual
    elif flight == 1:
      self.b_flight = qual
    elif flight == 2:
      self.b_flight = qual

  def is_qual(self,flight):
    if flight == 'A':
      return self.a_flight
    elif flight == 'B':
      return self.b_flight
    elif flight == 'C':
      return self.c_flight
    else:
      return False

