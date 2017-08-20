#!/usr/bin/python

pnum_map = {
  'J': '1',
  'j': '1',
  'K': '2',
  'k': '2',
  'L': '3',
  'l': '3',
  'M': '4',
  'm': '4',
  'N': '5',
  'n': '5',
  'O': '6',
  'o': '6',
  'P': '7',
  'p': '7',
  'Q': '8',
  'q': '8',
  'R': '9',
  'r': '9',
}

def canonical_pnum(p):
  if len(p) < 7:
    return p
  c = p[0]
  if c.isalpha():
    c = pnum_map[c]
  return c + p[1:]

class Player(object):
  """Object representing an ACBL member

  Attributes:
    fname
    lname
    pnum

  The attribute canon_pnum is derived from pnum by replacing a leading
  alphabetic character with the corresponding numeric value. This allows
  de-duping players who have achieved Life Master status, and list it
  within their player number.
  """

  def __init__(self, lname, fname, pnum=''):
    self.lname = lname
    self.fname = fname
    self.pnum = pnum
    self.canon_pnum = canonical_pnum(pnum)
    self.a_flight = False
    self.b_flight = False
    self.c_flight = False

  #
  # Players are considered identical when they have the same
  # canonical player number (canon_pnum). If the player has
  # no player number, the key is a tuple of lname,fname.
  #
  def __key(self):
    if len(self.canon_pnum) < 7:
      return (self.lname,self.fname)
    else:
      return self.canon_pnum

  def __hash__(self):
    return hash(self.__key())

  def __eq__(self,other):
    return self.__key() == other.__key()

  #
  # Players are sorted by last name, first name
  #
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

  #
  # Display the player class as lname, fname and player number
  #
  def __str__(self):
    name = self.terse()
    fmt = '{name:24} {pnum:8}'
    out = fmt.format(name=name, pnum=self.pnum)
    return out
    
  #
  # terse() prints name only, last name first
  #
  def terse(self):
    name = self.lname + ", " + self.fname
    return name

  #
  # set and check qualifying flags for each flight. qual is a boolean
  #
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

