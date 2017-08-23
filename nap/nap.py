# Generate reports for the NAP district playoffs.
#
# Morris "Mojo" Jones (Monrovia, CA)
#
# Grateful acknowledgement to Matthew J. Kidd of lajollabridge.com for his
# perl gamefile parsing tools, which are included here..
#
# This software is released under the GNU General Public License GPLv3
# See: http://www.gnu.org/licenses/gpl.html for full license.

import sys
from gamefile import Gamefile
from subprocess import check_call
from tempfile import mkstemp
import os
from os.path import join
from __init__ import __version__
from StringIO import StringIO

#
# This file's directory, necessary for finding ACBLdump utils
#
__cwd__ = os.path.dirname(os.path.realpath(__file__))

#
# Globals and methods to help webapp calls
#
class Nap(object):

  #
  # The set of persistent Game objects
  #
  games = {}

  #
  # Persistent set of Player objects
  #
  players = set()

  #
  # Qualdates tie players to games
  #
  qualdates = {}

  # INIT
  def __init__(self):
    self.games.clear()
    self.players.clear()
    self.qualdates.clear()

  #
  # Parse one game
  #
  def parse_game(self,gamefile):
    dump = join(__cwd__,"ACBLgamedump.pl")

    (handle,fname) = mkstemp()
    check_call("%s %s >%s 2>&1" % (dump, gamefile, fname),shell=True)

    with open(fname,"r") as f:
      json = f.read()
    os.remove(fname)

    game = Gamefile(json)
    return game

  #
  # Save one game on the games array
  #
  def load_game(self,gamefile):
    game = self.parse_game(gamefile)
    self.games[game.get_key()] = game
    return game

  #
  # Reload the games array
  #
  def reload_games(self,gamefile_tree):
    self.games.clear()

    # Walk the gamefile tree and pass everything that looks like a 
    # gamefile to extract_json
    for root, dirs, files in os.walk(gamefile_tree):
      for f in files:
        self.load_game(join(root,f))
    return self.get_game_list()

  #
  # Produce a sorted list of games
  #
  def get_game_list(self):
    gamelist = []
    for g in self.games.keys():
      gamelist.append(self.games[g])
    return sorted(gamelist)

  #
  # Load the players set with all qualified players
  #
  def reload_players(self):
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

  #
  # Single flight of qualified players
  # Assumes the player array is loaded!
  #
  def single_flight(self,flight):
    flight_players = []
    for p in self.players:
      if p.is_qual(flight):
        flight_players.append(p)
    return sorted(flight_players)

#
# MAIN routine
#
# Uses argparse, the help flag -h will print usage. Drives the report 
# generation.
#
# Individual gamefiles can be specified on the command line, else the
# program will walk a directory tree and process each gamefile found in
# the tree. By default it will walk a tree at ./gamefiles from the 
# directory where this script is found.
#
def main(scriptdir,arglist):
  #
  # Set up command line arguments
  #
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
  args = parser.parse_args(arglist)

  #
  # our object
  #
  nap = Nap()

  #
  # if gamefiles are specified on the command line, process those
  # otherwise look for gamefiles on the gamefile tree
  #
  if args.gamefiles:
    for filename in args.gamefiles:
      nap.load_game(filename)
  else:
    if args.tree:
      gamefile_tree = args.tree

    if gamefile_tree[0] != '/':
      gamefile_tree = join(scriptdir,gamefile_tree)

    nap.reload_games(gamefile_tree)

  report = ""

  # Test report, totals in strats
  for k in nap.games.keys():
    game = nap.games[k]
    details = game.get_event_details()
    totals = details.compute_total_pairs()

  #
  # Club report
  # List all clubs and game dates in the data set
  #
  if args.clubs:
    report += "{:8} {:30} {:17}    {:5}".format("Club No.","Club Name","Game Date","Tables")
    report += os.linesep
    for game in nap.get_game_list():
      club = game.get_club()
      report += "{:8} {:30} {:17}    {:5}"\
        .format(club.number,club.name,game.get_game_date(), game.table_count())
      report += os.linesep

  #
  # Flight report
  # This is the report for individual flight qualifiers. If multiple flights are
  # specified on the command line, each report will be generated
  #
  nap.reload_players()
  for flight in args.flight:
    if args.verbose:
      report += "\nQualifiers in Flight %s\n" % flight.upper()
      report += os.linesep
    for p in nap.single_flight(flight):
      report += "%s" % p
      report += os.linesep
      if args.verbose:
        for qd in sorted(nap.qualdates[p]):
          report += "            %s" % qd
          report += os.linesep

  #
  # Summary report
  # This report is a summary of all players and qualifying flights, emulating the
  # report from ACBLscore
  #
  if args.summary:
    report += os.linesep + "Summary of NAP Qualifiers" + os.linesep
    report += os.linesep
    fmt = "{:8} {:30} {:^4} {:^4} {:^4}"
    report += fmt.format("Player#","Name","FltA","FltB","FltC")
    report += os.linesep
    for p in sorted(nap.players):
      flta = 'Q' if p.is_qual('a') else ' '
      fltb = 'Q' if p.is_qual('b') else ' '
      fltc = 'Q' if p.is_qual('c') else ' '
      report += fmt.format(p.pnum,p.terse(),flta,fltb,fltc)
      report += os.linesep

  # TODO fix this
  #
  # Dupe report
  # This report lists players who appear in multiple game files under slightly
  # different names or player numbers
  #
  if args.dupe:
    report  += "TODO make dupe report"
#     report += os.linesep + "Interesting player duplications" + os.linesep
# 
#     # Initialize the canonical player list
#     players.clear()
#     for flight in ['a','b','c']:
#       collect_players(flight)
#     all_players = set(players)
#     keys = {}
#     for p in all_players:
#       keys[p.get_key()] = p
# 
#     # Look for players in games who don't exactly match
#     for game in games:
#       gp = []
#       for section in game.get_sections():
#         gp.extend(section.players)
#       for player in gp:
#         if player.get_key() in keys:
#           q = keys[player.get_key()]
#           if player.fname != q.fname or \
#               player.lname != q.lname or \
#               player.pnum != q.pnum:
#             report += "%s%s" % (player, q)
#             report += os.linesep

  # End of nap.main()
  return report

