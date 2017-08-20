NAP qualifiers

Generate reports from collected ACBLScore gamefiles.

TODO list:

* Generate Q report that shows players and all qualified flights
* Generate a duplicates report

HELP output, ./qual.py -h

    usage: qual.py [-h] [-t TREE] [-c] [-f {a,b,c}] [-v] [-V]
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
      -V, --version         show program's version number and exit
