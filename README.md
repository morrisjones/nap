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

TODO list:

* Generate a duplicates report
* Develop a means to manually add qualifiers from luddite directors
* Support limited games where the rank array doesn't start with flight A

HELP output, ./qual.py -h

    usage: qual.py [-h] [-t TREE] [-c] [-f {a,b,c}] [-v] [-s] [-V]
                   [gamefiles [gamefiles ...]]

    Create NAP qualifer list

    positional arguments:
      gamefiles             gamefile file name(s)

    optional arguments:
      -h, --help            show this help message and exit
      -t TREE, --tree TREE  top directory of a tree of ACBLScore game files
                            (default=./gamefiles)
      -c, --clubs           Show info for clubs and games
      -f {a,b,c}, --flight {a,b,c}
                            Select A B or C to report qualifying players
      -v, --verbose         Include more verbose information in reports
      -s, --summary         Generate the qualifier summary report
      -V, --version         show program's version number and exit
