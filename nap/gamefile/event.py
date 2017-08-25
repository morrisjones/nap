from event_details import EventDetails

class Event(object):
  """An event from ACBLscore

  Includes some meta-information from ACBLscore, and contains EventDetails.

  An Event can have an array of EventDetails, though in practice the game files
  we work with have exactly one Event and exactly one EventDetails object.

  See the Gamefile object code for the pain of dealing with that.

  Attributes:
    event_dict: raw data from the JSON file
    decode_format_version: No idea what this is
    filename: Generally has the full path of the raw ACBLscore game file
    created: Game file creation date in ACBLscore
    details: Array of EventDetails objects
  """

  def __init__(self,event_dict):
    self.event_dict = event_dict
    self.decode_format_version = event_dict['decode_format_version']
    self.filename = event_dict['filename']
    self.created = event_dict['creation_timestamp']
    self.details = []
    for e in event_dict['event']:
      self.details.append(EventDetails(e))
