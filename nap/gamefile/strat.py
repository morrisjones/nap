class Strat(object):
  """Represents a strat from a game event

  Attributes:
    max_mp: Max masterpoints for this strat, 0 = unlimited
    letter: Letter mapping to standard NAP strats, {'A','B','C'}
  """

  def __init__(self,dict):
    self.strat_dict = dict
    self.max_mp = self.strat_dict['max_mp']
    self.letter = self.strat_dict['letter']

