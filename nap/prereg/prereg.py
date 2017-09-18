import json
from seat import Seat
from pairentry import PairEntry
from ..gamefile import Player


class PreReg(object):
  """Represents an array of entries for preregistration representing a section

  Collect a specific array of PreRegEntry objects, each representing a pair playing
  in the North American Pairs semi-finals.
  """

  MAX_TABLES = 25

  def __init__(self,event=None,flight=None):
    self.event = event
    self.flight = flight
    self.section = {}
    for table_number in range(1,PreReg.MAX_TABLES+1):
      self.section[table_number] = {}
      for direction in (Seat.NS,Seat.EW):
        seat = Seat(table_number,direction)
        # Mark tables 2, 4, and 6 for permanent NS
        if not bool(table_number & 1) and direction == Seat.NS and \
            table_number < 7:
          seat.perm_ns = True
        self.section[table_number][direction] = seat
    return

  def find_empty_seat(self,req_ns=False):
    for table_num in self.section:
      for direction in (Seat.NS, Seat.EW):
        seat = self.section[table_num][direction]
        # The following could be an XOR but this might be more readable
        if req_ns and not seat.perm_ns:
          continue
        elif not req_ns and seat.perm_ns:
          continue
        if seat.pair_entry is None:
          return seat
    # We could arrive here because of a lack of permanent N-S seats
    # If that happens, assign the first available N-S seat and mark it perm_ns
    if req_ns:
      for table_num in self.section:
        seat = self.section[table_num][Seat.NS]
        if seat.pair_entry is None:
          seat.perm_ns = True
          return seat
    raise Exception("Ran out of seats available!")

  def is_already_registered(self,pnum):
    """Look through all of the registrations for an existing player number"""
    for table_number in self.section:
      for direction in (Seat.NS, Seat.EW):
        seat = self.section[table_number][direction]
        if seat.pair_entry:
          if seat.pair_entry.player_a.pnum == pnum:
            return True
          if seat.pair_entry.player_b.pnum == pnum:
            return True
    return False

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
            'email': seat.pair_entry.email,
          }
          section[table_number][direction]['seat'] = pe
    return section

  def as_json(self):
    flight = {
      'flight': self.flight,
      'event': self.event,
      'section': self.get_section(),
    }
    return json.dumps(flight,sort_keys=True,indent=4,separators=(',',': '))

  def add_entry(self,player_a,player_b,req_ns=False):
    seat = self.find_empty_seat(req_ns)
    seat.pair_entry = PairEntry(player_a, player_b, req_ns)
    return seat

  def init_from_dict(self,prereg_dict):
    self.flight = prereg_dict['flight']
    self.event = prereg_dict['event']
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
          email = seat['email']
          pe = PairEntry(player_a,player_b,req_ns=req_ns,email=email)
          self.section[int(table_num)][direction].pair_entry = pe
    return

  def init_from_json(self,json_string):
    dict = json.loads(json_string)
    self.init_from_dict(dict)
    return

  def find_max_table(self):
    max_table = 1
    for table_number in range(1,PreReg.MAX_TABLES+1):
      table = self.section[table_number]
      for direction in (Seat.NS, Seat.EW):
        seat = table[direction]
        if seat.pair_entry:
          max_table = table_number
          continue
    return max_table

  def get_all_players(self):
    """Returns a set() of Player objects from the entire section"""
    players = set()
    for table_number in self.section:
      table = self.section[table_number]
      for direction in (Seat.NS, Seat.EW):
        seat = table[direction]
        if seat.pair_entry:
          players.update(seat.pair_entry.player_a,seat.pair_entry.player_b)
    return players
