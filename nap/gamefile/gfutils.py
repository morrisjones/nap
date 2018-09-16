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
    '26N', '26E', '27N', '27E', '28N', '28E', '29N', '29E', '30N', '30E',
    '31N', '31E', '32N', '32E', '33N', '33E', '34N', '34E', '35N', '35E',
    '36N', '36E', '37N', '37E', '38N', '38E', '39N', '39E', '40N', '40E',
    '41N', '41E', '42N', '42E', '43N', '43E', '44N', '44E', '45N', '45E',
    '46N', '46E', '47N', '47E', '48N', '48E', '49N', '49E', '50N', '50E',
    '51N', '51E', '52N', '52E', '53N', '53E', '54N', '54E', '55N', '55E',
    '56N', '56E', '57N', '57E', '58N', '58E', '59N', '59E', '60N', '60E',
    '41N', '41E', '42N', '42E', '43N', '43E', '44N', '44E', '45N', '45E',
    '46N', '46E', '47N', '47E', '48N', '48E', '49N', '49E', '70N', '70E',
    '41N', '41E', '42N', '42E', '43N', '43E', '44N', '44E', '45N', '45E',
    '46N', '46E', '47N', '47E', '48N', '48E', '49N', '49E', '80N', '80E',
  ]