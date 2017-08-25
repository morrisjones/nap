class Club(object):
  """Contains a bridge club description

  Attributes:
    name: String-based club name from the game file
    number: ACBL-assigned club number, unique within ACBL

  As such, the club number is considered to be a key, and club
  objects with the same number are the same club.
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
