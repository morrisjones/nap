NAP qualifiers

Morris "Mojo" Jones  
Monrovia, CA  
mojo@whiteoaks.com  

Generate reports relevant to the North American Pairs district
playoffs from collected ACBLScore gamefiles.

Grateful acknowledgement to Matthew J. Kidd of lajollabridge.com for
his ACBLscore gamefile parsing software.

This software is released under the GNU General Public License GPLv3
See: http://www.gnu.org/licenses/gpl.html for full license.

HELP output, ./qual -h

    usage: qual [-h] [-t TREE] [-c] [-C CLUB] [-g GAME] [-p PLAYER] [-f {a,b,c}]
                [-v] [-s] [-V] [-d] [--totals] [--test]
                [gamefiles [gamefiles ...]]

    Create NAP qualifer list

    positional arguments:
      gamefiles             gamefile file name(s)

    optional arguments:
      -h, --help            show this help message and exit
      -t TREE, --tree TREE  top directory of a tree of ACBLScore game files
                            (default=./gamefiles)
      -c, --clubgames       Show info for clubs and games
      -C CLUB, --club CLUB  Report for an individual club, by ACBL club no.
      -g GAME, --game GAME  Report for an individual game
      -p PLAYER, --player PLAYER
                            Report for an individual player, by player number
      -f {a,b,c}, --flight {a,b,c}
                            Select A B or C to report qualifying players
      -v, --verbose         Include more verbose information in reports
      -s, --summary         Generate the qualifier summary report
      -V, --version         show program's version number and exit
      -d, --dupe            Generate an interesting report of player duplicates
      --totals              Diagnostic report of flight totals
      --test                For developmental test reports
