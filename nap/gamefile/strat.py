#!/usr/bin/python

class Strat(object):

  def __init__(self,dict):
    self.strat_dict = dict
    self.max_mp = self.strat_dict['max_mp']
    self.letter = self.strat_dict['letter']

