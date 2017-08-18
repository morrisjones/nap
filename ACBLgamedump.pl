#!/usr/bin/perl
#
# ACBLgamedump.pl
#
# Matthew J. Kidd (San Diego, CA)
#
# This software is released under the GNU General Public License GPLv3
# See: http://www.gnu.org/licenses/gpl.html for full license.
#
# Partially decodes an ACBLscore game file, outputting result as JSON.
#
# Can also integrate contracts and leads from Bridgemate / BridgePad /
# BridgeScorer electronic scoring files.
#
# 05-Dec-2015 - Current release
# 05-Nov-2014 - Initial release

use strict;
use FindBin;
use lib $FindBin::Bin;

use Config;
use JSON::PP;
use ACBLgamedecode;

my $VERSTR = '1.0.6';

# Exit codes
my $EXIT_SUCCESS          =   0;
my $EXIT_ARG_PARSING      =  -1;
my $EXIT_FILE_ERR         =  -2;
my $EXIT_BWS_ERR          =  -3;
my $EXIT_NEED_32_BIT_PERL =  -4;

(my $bname = $0) =~ s/.*[\\\/]//;

if ( scalar(@ARGV) == 0 ) {
  
  print "\n  Missing parameter(s)\n";
  
  print << "DONE";

  Usage: $bname fname [fname...] [-b bfname [...]] [-o ofname]

  fname  : ACBLscore game filename
  bfname : BWS filename (electronic scoring file)
  ofname : Output filename (default is STDOUT)
    
  Options
    -sc : Dump to section level only
    -nb : Don't dump board
    -ne : Don't dump entries (individual, pairs, teams)
    
    -bv : Include binary values (db_key parameter)
    -pp : Pretty print JSON output
    -vr : Display version number
    
  Partially decodes one or more ACBLscore game files, outputting
  result as JSON. Can also integrate contracts, results, and opening
  leads from Bridgemate / BridgePad / BridgeScorer systems.
  
  Online documentation is located at:
  http://lajollabridge.com/Software/ACBLgamedump/ACBLgamedump-About.htm
  
  See http://lajollabridge.com/Articles/ACBLscoreGameFilesDecoded.htm
  for details of ACBLscore game file format.

DONE

  exit($EXIT_SUCCESS);
}

my (@fnames, @BWSfnames, %opt);

while ( my $arg = shift(@ARGV) ) {
  if ( substr($arg,0,1) ne '-' ) { push @fnames, $arg; next; };
  my $sw = substr($arg,1);
  if ($sw eq 'o') {
    $arg = shift(@ARGV);
    if (!defined $arg) {
      print STDERR "\n-$sw switch is missing argument.\n"; exit($EXIT_ARG_PARSING);
    }
    $opt{'ofname'} = $arg;
  }
  elsif ($sw eq 'b') {
    $arg = shift(@ARGV);
    if (!defined $arg) {
      print STDERR "\n-$sw switch is missing argument.\n"; exit($EXIT_ARG_PARSING);
    }
    push @BWSfnames, $arg;
  }
  elsif ($sw eq 'nb') { $opt{'noboards'} = 1; }
  elsif ($sw eq 'ne') { $opt{'noentries'} = 1; }
  elsif ($sw eq 'sc') { $opt{'sectionsonly'} = 1; }
  elsif ($sw eq 'bv') { $opt{'binaryfields'} = 1; }
  elsif ($sw eq 'pp') { $opt{'prettyprint'} = 1; }
  elsif ($sw eq 'vr') { $opt{'showver'} = 1; }
  else {
    print STDERR "Unrecognized switch: $arg\n";
  }
}

print STDERR "$bname $VERSTR\n" if $opt{'showver'};

if (scalar(@fnames) == 0) {
  print STDERR "No input file(s) to process.\n"; exit($EXIT_ARG_PARSING);
}

my ($data, $bws, $err);
my $ix = 0;

if ($#BWSfnames != -1) {
  if ($^O eq 'MSWin32' && $Config{'ptrsize'} == 8 ) {
    print STDERR <<'DONE';
  
You are using a 64-bit version of Perl. But on Windows, the -b option requires
the 32-bit Perl interpreter in order to access the 32-bit only Microsoft
libraries that can read Bridgemate, BridgePad, and BridgeScorer files.
DONE
    exit($EXIT_NEED_32_BIT_PERL);
  }
  
  ($err, $bws) = ACBLgamedecode::readBWSfiles(\@BWSfnames);
  if ($err) {
    print STDERR "Failed to parse BWS file(s).\n$err\n";
    exit($EXIT_BWS_ERR);
  }
}

foreach my $fname (@fnames) {
  ($err, my $gm) = ACBLgamedecode::decode($fname, \%opt, $bws);
  if ($err == -257) {
    print STDERR "Not an ACBLscore game file: $fname (skipped)\n";
  }
  elsif (!$err) { $data->[$ix] = $gm; }

  $ix++;
}

exit($EXIT_SUCCESS) if !defined $data;

my $fh;
if ( defined $opt{'ofname'} ) {
  if (! open($fh, '>', $opt{'ofname'})) {
    print STDERR "Unable to open/write: $opt{'ofname'}\n"; exit($EXIT_FILE_ERR);
  }  
}
else {
  open($fh, '>-');
}

my $js = new JSON::PP;
$js->pretty(1) if $opt{'prettyprint'};
print $fh $js->encode($data);
close($fh);  

exit($EXIT_SUCCESS);
