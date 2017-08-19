#!/usr/bin/python

from player import Player
from club import Club
from event_details import EventDetails

class Event(object):

  def __init__(self,event_dict):
    self.event_dict = event_dict
    self.decode_format_version = event_dict['decode_format_version']
    self.filename = event_dict['filename']
    self.created = event_dict['creation_timestamp']
    self.details = []
    for e in event_dict['event']:
      self.details.append(EventDetails(e))
