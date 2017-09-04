from seat import Seat
from pairentry import PairEntry
from ..gamefile import Player


class PreReg(object):
  """Represents an array of entries for preregistration representing a section

  Collect a specific array of PreRegEntry objects, each representing a pair playing
  in the North American Pairs semi-finals.
  """

  MAX_TABLES = 25

  def __init__(self,flight):
    self.flight = flight
    self.section = {}
    for table_number in range(1,PreReg.MAX_TABLES+1):
      self.section[table_number] = {}
      for direction in (Seat.NS,Seat.EW):
        seat = Seat(table_number,direction)
        # Mark the odd tables for permanent NS
        if bool(table_number & 1) and direction == Seat.NS:
          seat.perm_ns = True
        self.section[table_number][direction] = seat
    return

  def find_empty_seat(self,req_ns=False):
    for table_num in self.section:
      for direction in (Seat.NS, Seat.EW):
        seat = self.section[table_num][direction]
        if req_ns and not seat.perm_ns:
          continue
        if seat.pair_entry == None:
          return seat
    raise Exception("Ran out of seats available!")

  def get_section(self):
    section = {}
    for table_number in range(1,PreReg.MAX_TABLES+1):
      section[table_number] = {
        Seat.NS: { 'seat': None },
        Seat.EW: { 'seat': None },
      }
    for table_number in self.section:
      table = self.section[table_number]
      for direction in (Seat.NS,Seat.EW):
        seat = table[direction]
        if seat.pair_entry:
          pe = {
            'player_a': {
              'lname': seat.pair_entry.player_a.lname,
              'fname': seat.pair_entry.player_a.fname,
              'pnum': seat.pair_entry.player_a.pnum,
            },
            'player_b': {
              'lname': seat.pair_entry.player_b.lname,
              'fname': seat.pair_entry.player_b.fname,
              'pnum': seat.pair_entry.player_b.pnum,
            },
            'req_ns': seat.pair_entry.req_ns,
          }
          section[table_number][direction]['seat'] = pe
    return section

  def add_entry(self,player_a,player_b,req_ns=False):
    seat = self.find_empty_seat(req_ns)
    seat.pair_entry = PairEntry(player_a, player_b, req_ns)
    return seat

  def init_from_dict(self,prereg_dict):
    for table_num in prereg_dict['section']:
      for direction in (Seat.NS, Seat.EW):
        seat = prereg_dict['section'][table_num][direction]['seat']
        if seat:
          player_a = Player(seat['player_a']['lname'],
                            seat['player_a']['fname'],
                            seat['player_a']['pnum'])
          player_b = Player(seat['player_b']['lname'],
                            seat['player_b']['fname'],
                            seat['player_b']['pnum'])
          req_ns = seat['req_ns']
          pe = PairEntry(player_a,player_b,req_ns)
          self.section[int(table_num)][direction].pair_entry = pe
    return