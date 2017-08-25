"""Generate reports for the NAP district playoffs.

Package methods:
    main: Called from a command-line script, passed the working directory of
        the script and an array of arguments. Returns reports as strings.

Classes:
    Nap: Methods to generate reports, and contains games, players, and qualdates

Grateful acknowledgement to Matthew J. Kidd of lajollabridge.com for his
perl gamefile parsing tools, which are included here..

This software is released under the GNU General Public License GPLv3
See: http://www.gnu.org/licenses/gpl.html for full license.

Morris "Mojo" Jones, mojo@bridgemojo.com

"""

import sys
from gamefile import Gamefile, GamefileException
from subprocess import check_call
from tempfile import mkstemp
import os
from os.path import join
from __init__ import __version__
from StringIO import StringIO

# This file's directory, necessary for finding ACBLdump utils
__cwd__ = os.path.dirname(os.path.realpath(__file__))

class Nap(object):
  """Encapsulates games, players, and qualdates for use in reports
  """

  # Mapping between club session numbers and day/time
  session_string = {
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

  def __init__(self):
    self.games = {}
    self.players = set()
    self.qualdates = {}

  def parse_game(self,gamefile):
    """Convert a raw ACBLscore gamefile into Gamefile object.

    This function relies on a perl script and accompanying perl module
    that are included in the package as package_data.

    ACBLgamedump is described at this link:
      https://lajollabridge.com/Software/ACBLgamedump/ACBLgamedump-About.htm

    Args:
      gamefile: Path string to an ACBLscore game file on local storage

    Returns:
      Gamefile

    Exceptions:
      GamefileException if there is a parse error.
    """
    dump = join(__cwd__,"ACBLgamedump.pl")

    # Write JSON output to a temp file.
    # (subprocess stdio capture cannot be used here. When this module is 
    # embedded in a web framework, the stdio handles are frequently 
    # unavailable.)
    (handle,fname) = mkstemp()
    try:
      check_call("%s %s >%s 2>&1" % (dump, gamefile, fname),shell=True)
    except CalledProcessError, e:
      raise GamefileException(e)

    with open(fname,"r") as f:
      json = f.read()
    if json.startswith('Not an ACBLscore game file'):
      os.remove(fname)
      raise GamefileException(json)
    else:
      os.remove(fname)

    try:
      game = Gamefile(json)
    except GamefileException:
      raise
    except Exception, e:
      raise GamefileException(e)

    rating = game.get_rating()
    if not rating.startswith('NAP'):
      raise GamefileExcpetion("Not NAP game: " + rating)
    return game

  def load_game(self,gamefile):
    """Save one gamefile in the games dictionary by its natural key"""
    game = self.parse_game(gamefile)
    self.games[game.get_key()] = game
    return game

  def load_games(self,gamefile_tree):
    """Walk the gamefile tree and pass all files to load_game()

    Since game file names are not globally unique, the practice here is
    to keep game files in subdirectories with a relevant name for the
    bridge club.

    (If collisions between similarly named bridge clubs are anticipated, the
    ACBL-assigned club number could be used as a parent directory instead,
    following practices of TheCommonGame.com)

    This method does not throw the GamefileException. If a particular file
    throws that exception, it is skipped with a message written to stderr.

    Args:
      gamefile_tree: The root directory of a tree of game files.
    Returns:
      A list of Gamefile objects in their natural order, as returned by
      get_game_list(). (Not the games dictionary.)
    """
    for root, dirs, files in os.walk(gamefile_tree):
      for f in files:
        try:
          gamefile = join(root,f)
          self.load_game(gamefile)
        except GamefileException, e:
          print >>sys.stderr, "Skipped %s" % gamefile, e
    return self.get_game_list()

  def get_game_list(self):
    """Returns a list of games sorted by their occurence date/time"""
    gamelist = []
    for g in self.games.keys():
      gamelist.append(self.games[g])
    return sorted(gamelist)

  def load_players(self):
    """Populate the class players set with qualified players.

    This method walks the game set and finds all players who have a
    non-zero qual_flag value, meaning they have qualified to advance
    in one of the three available flights.

    Players who did not qualify in any flight are not added by this
    method, but the player set is not cleared at the start. This method
    will only add players, deleting none.
    """
    for flight in ['a','b','c']:
      for game in self.get_game_list():
        qd = game.get_qualdate()
        qp = game.qualified_players(flight)
        for p in qp:
          self.players.add(p)
          if p not in self.qualdates:
            self.qualdates[p] = set([qd])
          else:
            self.qualdates[p].add(qd)
    return sorted(self.players)

  def single_flight(self,flight):
    """Return players from the class players set for a single flight.

    Note that this method does not check or modify the class players
    set, which must be populated before calling. (See load_players().)
    """
    flight_players = []
    for p in self.players:
      if p.is_qual(flight):
        flight_players.append(p)
    return sorted(flight_players)

  def club_games(self):
    """Report club games in the data set.

    ASCII formatted for fixed-pitch (<pre>) print out.

    Args: none
    Returns: report string
    """
    report = ""
    fmt = "{:8} {:30} {:17} {:<8} {:>5}"
    report += fmt.format("Club No.","Club Name","Game Date","Session","Tables")
    report += os.linesep
    for game in self.get_game_list():
      club = game.get_club()
      report += fmt.format(club.number, 
                           club.name, 
                           game.get_game_date(),
                           Nap.session_string[game.get_club_session_num()], 
                           game.table_count()
                          )
      report += os.linesep
    return report

  def flight_report(self,flight,verbose=False):
    """Report players for a single flight

    This is an ASCII formatted report for fixed-pitch (<pre>) rendering.

    Args:
      flight: Must be values from {'a','b','c'} (not tested)
      verbose: If True, the report will include game dates and locations
    Returns: report string
    """
    report = ""
    if verbose:
      report += "\nQualifiers in Flight %s\n" % flight.upper()
      report += os.linesep
    for p in self.single_flight(flight):
      report += "%s" % p
      report += os.linesep
      if verbose:
        for qd in sorted(self.qualdates[p]):
          report += "            %s" % qd
          report += os.linesep
    return report

  def flight_players(self,flight):
    """Return a nice sorted array of Players with Qualdates

    This is intended to be rendered by the webapp with appropriate formatting,
    like a nice table, with odd/even highlighting or such.

    Assumes players have been loaded.
    """
    flight_players = []
    for p in self.single_flight(flight):
      record = {}
      record['player_name'] = p.terse()
      record['player_number'] = p.pnum
      record['qualdates'] = sorted(self.qualdates[p])
      flight_players.append(record)
    return flight_players

  def summary_report(self):
    """Report all qualified players with markers for their flight.

    Args: none
    Returns: report string
    """
    report = ""
    report += os.linesep + "Summary of NAP Qualifiers" + os.linesep
    report += os.linesep
    fmt = "{:8} {:30} {:^4} {:^4} {:^4}"
    report += fmt.format("Player#","Name","FltA","FltB","FltC")
    report += os.linesep
    for p in sorted(self.players):
      flta = 'Q' if p.is_qual('a') else ' '
      fltb = 'Q' if p.is_qual('b') else ' '
      fltc = 'Q' if p.is_qual('c') else ' '
      report += fmt.format(p.pnum,p.terse(),flta,fltb,fltc)
      report += os.linesep
    return report

def main(scriptdir,arglist):
  """Command line oriented report generator

  Args:
    scriptdir: 
        If the gamefile_tree is relative, or default, it's assumed to be 
        relative to the directory supplied in scriptdir. If gamefile_tree is 
        supplied and starts with /, this argument is unnecessary.
    arglist:
        A string list, expected to be sys.argv from the command line. Will be
        parsed by argparse.

  The argument list may include a number of individual game files or with
  the -t option, the top of a gamefile tree. Game files will be found by
  walking the tree from that root.
  """

  import argparse

  parser = argparse.ArgumentParser(description='Create NAP qualifer list')
  parser.add_argument('gamefiles', type=str, 
      help="gamefile file name(s)", nargs='*')
  parser.add_argument('-t', '--tree', default="./gamefiles",
      help="top directory of a tree of ACBLScore game files (default=./gamefiles)")
  parser.add_argument('-c', '--clubs', action="store_true", 
      help="Show info for clubs and games")
  parser.add_argument('-f', '--flight', action="append", default=[], 
      choices=("a","b","c"),
      help="Select A B or C to report qualifying players")
  parser.add_argument('-v', '--verbose', action="store_true",
      help="Include more verbose information in reports")
  parser.add_argument('-s', '--summary', action="store_true",
      help="Generate the qualifier summary report")
  parser.add_argument('-V', '--version', action="version", 
      version="%(prog)s ("+__version__+")")
  parser.add_argument('-d', '--dupe', action="store_true",
      help="Generate an interesting report of player duplicates")
  parser.add_argument('--totals', action="store_true",
      help="Diagnostic report of flight totals")
  parser.add_argument('--test', action="store_true",
      help="For developmental test reports")
  args = parser.parse_args(arglist)

  # Encapsulate the games, players, and qualdates
  nap = Nap()

  # if gamefiles are specified on the command line, process those
  # otherwise look for gamefiles on the gamefile tree
  if args.gamefiles:
    for filename in args.gamefiles:
      nap.load_game(filename)
  else:
    if args.tree:
      gamefile_tree = args.tree

    if gamefile_tree[0] != '/':
      gamefile_tree = join(scriptdir,gamefile_tree)

    nap.load_games(gamefile_tree)

  report = ""

  # Here I'm going to test various algorithms for data reduction
  if args.test:
    report = ""
    nap.load_players()
    flight_players = nap.flight_players('a')
    for fp in flight_players:
      report += ''.join('{}: {}'.format(key, val) for key, val in fp.items())
      report += os.linesep
    return report
    

  # (NEW in testing) Show number of pairs in each strat
  # (Note that higher strats should include the number of pairs from
  # lower strats as well, and do not at present.)
  if args.totals:
    for k in nap.games.keys():
      game = nap.games[k]
      details = game.get_event_details()
      totals = details.compute_total_pairs()
      print game
      print totals

  # Club report
  # List all clubs and game dates in the data set
  if args.clubs:
    report += nap.club_games()

  # Flight report
  # This is the report for individual flight qualifiers. If multiple flights are
  # specified on the command line, each report will be generated
  nap.load_players()
  for flight in args.flight:
    report += nap.flight_report(flight,args.verbose)

  # Summary report
  # This report is a summary of all players and qualifying flights, emulating the
  # report from ACBLscore
  if args.summary:
    report += nap.summary_report()

  # Dupe report
  # This report lists players who appear in multiple game files under slightly
  # different names or player numbers
  # (The dupe report isn't yet de-duped. :) )
  if args.dupe:
    report  += os.linesep + "Interesting player duplications" + os.linesep + os.linesep
    napdupe = Nap()
    if args.gamefiles:
      for filename in args.gamefiles:
        napdupe.load_game(filename)
    else:
      if args.tree:
        gamefile_tree = args.tree

      if gamefile_tree[0] != '/':
        gamefile_tree = join(scriptdir,gamefile_tree)

    napdupe.load_games(gamefile_tree)
    qual_players = napdupe.load_players()
    keys = {}
    for qp in qual_players:
      keys[qp.get_key()] = qp

    for k in napdupe.games.keys():
      game = napdupe.games[k]
      players = game.all_players()
      for p in players:
        if p.get_key() in keys:
          q = keys[p.get_key()]
          if p.fname != q.fname or \
              p.lname != q.lname or \
              p.pnum != q.pnum:
            report += "%s%s" % (p,q)
            report += os.linesep

  # End of nap.main()
  return report

