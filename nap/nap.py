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
from gamefile.player import canonical_pnum
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

  def club_games(self,club_number=None,game_index=None):
    """ Return structured data for a sorted list of club games

    This will be suitable for the club_games_report and for the webapp

    Args:
      club_number: if specified will select games at a particular club
      game_index: if specified will select an individual game by its index
    """
    all_games = self.get_game_list()
    resultlist = []
    for idx, game in enumerate(all_games):
      result = {
        'game_index': idx,
        'club_number': game.get_club().number,
        'club_name': game.get_club().name,
        'game_date': game.get_game_date(),
        'session': game.get_club_session_num(),
        'session_name': Gamefile.session_string[game.get_club_session_num()],
        'tables': game.table_count(),
        'game': game,
      }
      if game_index is not None:
        if game_index == idx:
          resultlist.append(result)
      elif club_number:
        if club_number == result['club_number']:
          resultlist.append(result)
      else:
        resultlist.append(result)
    return resultlist

  def club_games_report(self,game_index=None,club_number=None):
    """Report club games in the data set.

    ASCII formatted for fixed-pitch (<pre>) print out.

    Args:
      game_index: Index number for one particular game
      club_number: Club number for all games related to a club

    Returns: report string
    """
    report = ""
    fmt = "{:>5} {:8} {:30} {:17} {:<8} {:>5}"
    report += fmt.format("Index","Club No.","Club Name","Game Date","Session","Tables")
    report += os.linesep
    club_game_list = self.club_games(game_index=game_index,club_number=club_number)
    table_count = 0.0
    for idx, game in enumerate(club_game_list):
      report += fmt.format(game['game_index'] + 1,
          game['club_number'], 
          game['club_name'], 
          game['game_date'],
          game['session_name'],
          game['tables'],
          )
      report += os.linesep
      table_count += game['tables']
    report += os.linesep
    report += "Total games: %s" % len(club_game_list)
    report += os.linesep
    report += "Total tables: %s" % table_count
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

  def summary_report(self,players_list=None):
    """Report all qualified players with markers for their flight.

    Args:
      players_list: If provided, use this list of players instead of the 
          whole list from the nap object
    Returns: report string
    """
    if not players_list:
      players_list = self.players
    report = ""
    report += os.linesep + "Summary of NAP Qualifiers" + os.linesep
    report += os.linesep
    fmt = "{:8} {:30} {:^4} {:^4} {:^4}"
    report += fmt.format("Player#","Name","FltA","FltB","FltC")
    report += os.linesep
    for p in sorted(players_list):
      flta = 'Q' if p.is_qual('a') else ' '
      fltb = 'Q' if p.is_qual('b') else ' '
      fltc = 'Q' if p.is_qual('c') else ' '
      report += fmt.format(p.pnum,p.terse(),flta,fltb,fltc)
      report += os.linesep
    return report

  def players_from_game(self,game):
    my_player_set = set()
    for flight in ['a','b','c']:
      my_player_set.update(game.qualified_players(flight))
    return my_player_set

  def club_report(self,club_num):
    """Select for a particular club, report games and players
    """
    report = "Club report for club %s" % club_num
    report += os.linesep

    report += self.club_games_report(club_number=club_num)
    report += os.linesep

    my_games = self.club_games(club_number=club_num)
    report += "Games from club: %s" % len(my_games)
    report += os.linesep

    my_player_set = set()
    for g in my_games:
      my_player_set.update(self.players_from_game(g['game']))

    report += self.player_summary_report(my_player_set)

    return report

  def flight_totals(self,players=None):
    if not players:
      players = self.players
    flight_totals = {
      'a': 0,
      'b': 0,
      'c': 0,
    }
    for qp in players:
      if qp.is_qual('a'):
        flight_totals['a'] += 1
      if qp.is_qual('b'):
        flight_totals['b'] += 1
      if qp.is_qual('c'):
        flight_totals['c'] += 1
    return flight_totals

  def player_summary_report(self,players=None):
    if not players:
      players = self.players
    report = self.summary_report(players_list=players)
    report += os.linesep

    flight_totals = self.flight_totals()

    report += "Qualified players" + os.linesep
    report += "Total: %s" % len(players)
    report += os.linesep
    report += "  Flight A: %s" % flight_totals['a']
    report += os.linesep
    report += "  Flight B: %s" % flight_totals['b']
    report += os.linesep
    report += "  Flight C: %s" % flight_totals['c']
    report += os.linesep
    return report

  def game_report(self,gameidx):
    """Produce a game report

    Args:
      gameidx: one-based index into games list
    """
    gamelist = self.get_game_list()
    game = gamelist[int(gameidx)-1]
    report = "Report for single game" + os.linesep
    report += "%s" % game
    report += os.linesep

    my_player_set = set()
    my_player_set.update(self.players_from_game(game))

    report += self.player_summary_report(my_player_set)

    return report

  def find_player(self,player_number):
    player_key = canonical_pnum(player_number)
    for p in self.players:
      if player_key == p.canon_pnum:
        return p
    return None

  def player_report(self,player_number):
    report = ""
    player = self.find_player(player_number)
    if not player:
      report += "Not found in qualified player list"
      return report
    report += "%s" % player
    report += os.linesep + "Qualification flights: "
    if player.is_qual('a'):
      report += "A "
    if player.is_qual('b'):
      report += "B "
    if player.is_qual('c'):
      report += "C"
    report += os.linesep
    report += "Played in qualifier games:" + os.linesep
    for qd in self.qualdates[player]:
      report += "   %s" % qd
      report += os.linesep
    return report

# End of Nap object


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
  parser.add_argument('-c', '--clubgames', action="store_true", default=[],
      help="Show info for clubs and games")
  parser.add_argument('-C', '--club', action="append", default=[],
      help="Report for an individual club, by ACBL club no.")
  parser.add_argument('-g', '--game', action="append", default=[],
      help="Report for an individual game")
  parser.add_argument('-p', '--player', action="append", default=[],
      help="Report for an individual player, by player number")
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

  nap.load_players()
  report = ""

  # Here I'm going to test various algorithms for data reduction
  if args.test:
    report = ""
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

  # Club games report
  # List all clubs and game dates in the data set
  # Print an index number useful for displaying an individual game result
  if args.clubgames:
    report += nap.club_games_report()

  # Club report
  for club in args.club:
    report += nap.club_report(club)

  # Game report
  for gameidx in args.game:
    report += nap.game_report(gameidx)

  # Player report
  for pnum in args.player:
    report += nap.player_report(pnum)
    report += os.linesep

  # Flight report
  # This is the report for individual flight qualifiers. If multiple flights are
  # specified on the command line, each report will be generated
  for flight in args.flight:
    report += nap.flight_report(flight,args.verbose)

  # Summary report
  # This report is a summary of all players and qualifying flights, emulating the
  # report from ACBLscore
  if args.summary:
    report += nap.player_summary_report()

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

