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
  """Convert a player number to a canonical player number.

  Traditionally Life Masters have the first digit of their player number replaced
  with a letter, from J through R, as a badge of honor. If the number is presented
  with a leading letter value, this returns a mapping to the original digit.
  """
  if len(p) < 7:
    return p
  c = p[0]
  if c.isalpha():
    c = pnum_map[c]
  return c + p[1:]

class Player(object):
  """Object representing an ACBL member

  Attributes:
    fname: First name
    lname: Last name
    pnum: Player number as provided in the game file
    canon_pnum: Canonical player number for finding duplicates
    a_flight: Boolean value for an A flight qualification
    b_flight: Boolean value for a B flight qualification
    c_flight: Boolean value for a C flight qualification

  Methods:
    get_key(): Returns the private unique key for a pleyer. The key is the
        canonical player number for ACBL members, or (lname,fname) for 
        non-members.
  """

  def __init__(self, lname, fname, pnum=''):
    self.lname = lname
    self.fname = fname
    self.pnum = pnum
    self.canon_pnum = canonical_pnum(pnum)
    self.a_flight = False
    self.b_flight = False
    self.c_flight = False

  def __key(self):
    if len(self.canon_pnum) < 7:
      return (self.lname,self.fname)
    else:
      return self.canon_pnum

  def get_key(self):
    return self.__key()

  def __hash__(self):
    return hash(self.__key())

  def __eq__(self,other):
    return self.__key() == other.__key()

  def __cmp__(self,other):
    """Natural ordering of Player objects

    Order by last name, then first name, then player number
    """
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
    if self.pnum != other.pnum:
      if self.pnum > other.pnum:
        return 1
      else:
        return -1
    return 0

  def cmp(self,other):
    """Public method for the __cmp__ function, does not invoke __eq__ or __hash__"""
    return self.__cmp__(other)

  def __str__(self):
    """Display the player as lname, fname, and plalyer number"""
    name = self.terse()
    fmt = '{name:24} {pnum:8}'
    out = fmt.format(name=name, pnum=self.pnum)
    return out
    
  def terse(self):
    """Print name only (no player number), lname, fname"""
    name = self.lname + ", " + self.fname
    return name

  def set_qual(self,flight,qual):
    """Set a qualifier flag

    Args:
      flight: One character of {'a','b','c'}
      qual: Boolean value, True if qualfied
    """
    if flight == 'a':
      self.a_flight = qual
    elif flight == 'b':
      self.b_flight = qual
    elif flight == 'c':
      self.c_flight = qual

  def is_qual(self,flight):
    """Return boolean qualifier flag

    Args:
      flight: One of {'a','b','c'}
    """
    if flight == 'a':
      return self.a_flight
    elif flight == 'b':
      return self.b_flight
    elif flight == 'c':
      return self.c_flight
    else:
      return False

