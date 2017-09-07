class GFUtils(object):
  """Useful reference constants shared by gamefile objects
  """

  # Mapping between club session numbers and day/time
  SESSION_STRING = {
    1: 'Mon AM',
    2: 'Mon Aft',
    3: 'Mon Eve',
    4: 'Tue AM',
    5: 'Tue Aft',
    6: 'Tue Eve',
    7: 'Wed AM',
    8: 'Wed Aft',
    9: 'Wed Eve',
    10: 'Thu AM',
    11: 'Thu Aft',
    12: 'Thu Eve',
    13: 'Fri AM',
    14: 'Fri Aft',
    15: 'Fri Eve',
    16: 'Sat AM',
    17: 'Sat Aft',
    18: 'Sat Eve',
    19: 'Sun AM',
    20: 'Sun Aft',
    21: 'Sun Eve',
    22: '(Other)',
  }

  SEATS = [
    '1N', '1E', '2N', '2E', '3N', '3E', '4N', '4E', '5N', '5E',
    '6N', '6E', '7N', '7E', '8N', '8E', '9N', '9E', '10N','10E',
    '11N', '11E', '12N', '12E', '13N', '13E', '14N', '14E', '15N', '15E',
    '16N', '16E', '17N', '17E', '18N', '18E', '19N', '19E', '20N', '20E',
    '21N', '21E', '22N', '22E', '23N', '23E', '24N', '24E', '25N', '25E',
  ]