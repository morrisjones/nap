class GamefileException(Exception):
  """Encapsulates an error in processing any file as an ACBLscore game file
  """
  def __init__(self,value):
    self.value = value
  def __str__(self):
    return repr(self.value)

