#!/usr/bin/python

from event_details import EventDetails

class Event(object):
  """The event object is a parent for EventDetails, and only has
    meta information from ACBLscore.
  """

  def __init__(self,event_dict):
    self.event_dict = event_dict
    self.decode_format_version = event_dict['decode_format_version']
    self.filename = event_dict['filename']
    self.created = event_dict['creation_timestamp']
    self.details = []
    for e in event_dict['event']:
      self.details.append(EventDetails(e))
