import os


class Seat(object):
  """Represent a pair of seats in a bridge game"""

  NS, EW = ('North-South','East-West')

  def __init__(self,table,direction):
    self.table = table
    self.direction = direction
    self.pair_entry = None
    self.perm_ns = False
    return

  def __str__(self):
    output = ""
    output += "Table {} {}".format(self.table,self.direction)
    output += os.linesep
    if self.pair_entry:
      output += "  {}".format(self.pair_entry.player_a) + os.linesep
      output += "  {}".format(self.pair_entry.player_b)
    else:
      output += "  Not assigned"
    return output


  def __cmp__(self,other):
    if self.table > other.table:
      return 1
    if self.table < other.table:
      return -1
    if self.direction == Seat.NS and other.direction == Seat.EW:
      return 1
    if self.direction == Seat.EW and other.direction == Seat.NS:
      return -1
    return 0

  def __key__(self):
    return (self.table,self.direction)

