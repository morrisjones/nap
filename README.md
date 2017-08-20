NAP qualifiers

Generate reports from collected ACBLScore gamefiles.

TODO list:

* Generate Q report that shows players and all qualified flights
* Generate a duplicates report
* Add system calls that will generate the JSON on the fly from a tree
  of game files using ACBLgamedump.pl

usage: qual.py [-h] [-c] [-f {a,b,c}] [-v] [input [input ...]]

Create NAP qualifer list

positional arguments:
  input                 gamefile json file name, else stdin

optional arguments:
  -h, --help            show this help message and exit
  -c, --clubs           Show info for clubs and games
  -f {a,b,c}, --flight {a,b,c}
                        Select A B or C to report qualifying players
  -v, --verbose         Include more verbose information in reports
