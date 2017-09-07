class PairEntry(object):
  """Represent a single pair registered to play in a semi-final flight
  """

  def __init__(self,a,b,req_ns=False,email=None):
    self.player_a = a
    self.player_b = b
    self.req_ns = req_ns
    self.email = email
    return



