#!/usr/bin/python


class Club(object):
  """Should probably just be a tuple, club name and number.
  """

  def __init__(self,name,number):
    self.name = name
    self.number = number

  def __key(self):
    return (self.name,self.number)

  def __hash__(self):
    return hash(self.__key())

  def __eq__(self, other):
    return self.__key() == other.__key()

  def __str__(self):
    return self.name
