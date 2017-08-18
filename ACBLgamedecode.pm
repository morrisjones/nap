#!/usr/bin/perl
#
# ACBLgamedecode.pm
#
# Matthew J. Kidd (San Diego, CA)
#
# This software is released under the GNU General Public License GPLv3
# See: http://www.gnu.org/licenses/gpl.html for full license.
#
# Partially decodes an ACBLscore game file, outputting result as JSON.
# Useful reference: http://lajollabridge.com/Articles/ACBLscoreGameFilesDecoded.htm
#
# 05-Dec-2015 - Current release
# 05-Nov-2014 - Initial release

package ACBLgamedecode;

use strict;

# Error codes
my $SUCCESS              =    0;
my $ERR_FILE_ERR         =   -2;
my $ERR_NEED_32_BIT_PERL =   -4;
my $ERR_NOT_GAME_FILE    = -257;

# Version of decoded data
my $DECODE_FORMAT_VERSION = 4;

# ACBLscore constants
my $MAX_EVENTS   =  50;
my $MAX_SECTIONS = 100;

# ACBLscore events types and scoring methods.
my @EVENT_TYPE = ('Pairs', 'Teams', 'Individual', 'Home Style Pairs', 'BAM', 'Series Winner');
my @EVENT_SCORING = ('Matchpoints', 'IMPs with computed datum', 'Average IMPs', 'Total IMPs',
  'Instant Matchpoints', 'BAM Teams', 'Win/Loss', 'Victory Points', 'Knockout', undef,
  'Series Winner', undef, undef, undef, undef, undef, 'BAM Matchpoints', undef, 'Compact KO');
my @EVENT_RATING = ('No Masterpoints', 'Club Masterpoint', 'Club Championship', 
  'Charity Club Championship', 'Unit Championship', 'Sectional', 'Regional',
  'Club International Fund', 'Club Membership', undef, undef, undef, 'Upgraded Club Championship',
  undef, 'STAC', 'National', 'Bridge Plus', 'Progressive Sectional', 'Unit Charity Game',
  'Unit Extended Team Game', 'NAP Club Level', 'NAP Unit Level', 'GNT Club Level', 'GNT Unit Level',
  'ACBL Wide Charity', 'ACBL Wide International Fund', undef, 'Canada Wide Olympiad',
  'World Wide Instant Matchpoints', 'ACBL Wide Instant Matchpoints', 'Junior Fund', undef,
  'ACBL Wide Senior', 'COPC Club Level', 'CNTC Master/Non Master', 'CNTC Club Level',
  'CNTC Unit Level', 'CWTC', 'Canada Rookie/Master', 'Inter-Club Championship',
  'Unit Wide Championship', undef, undef, 'Club Appreciation', undef, undef, undef, undef, undef,
  'Club Appreciation Team', 'NABC Fund Raiser', 'GNT Fund Raiser', 'CNTC Fund Raiser', undef, undef,
  'Club Education Foundation', 'Unit International Fund', 'Club Membership', 'Unit Education Fund',
  undef, undef, undef, undef, 'Grass Roots Fund'
);
my @MOVEMENT_TYPE = ('Mitchell', 'Howell', 'Web', 'External', 'External BAM', 'Barometer',
  'Manual Mitchell', 'Manual Howell');

my @CLUB_GAME_TYPE = ('Open', 'Invitational', 'Novice', 'BridgePlus', 'Pupil', 'Introductory');
my %ACBL_PLAYER_RANKS = (' ' => 'Rookie', 'A' => 'Junior Master', 'B' => 'Club Master', 
  'C' => 'Sectional Master', 'D' => 'Regional Master', 'E' => 'NABC Master',
  'F' => 'Advanced NABC Master', 'G' => 'Life Master', 'H' => 'Bronze Life Master', 
  'I' => 'Silver Life Master', 'J' => 'Gold Life Master', 'K' => 'Diamond Life Master',
  'L' => 'Emerald Life Master', 'M' => 'Platinum Life Master', 'N' => 'Grand Life Master'
);
my @AWARD_SETS = ('previous', 'current', 'total');
my $PIGMENTATION_TYPES = ' BSRGP';
my @RIBBON_COLORS = ('', 'Blue', 'Red', 'Silver', undef, undef, undef, undef, undef, 'Blue/Red');
my @HANDICAP_TYPES = ('Not Handicapped', 'Percentage', 'Matchpoints', 'Boards');

my %SPECIAL_SCORES = ('900' => 'Late Play', '950' => 'Not Played',
  '2040' => 'Ave-', '2050' => 'Ave', '2060' => 'Ave+');
  
my $BYE_TEAM_NUMBER = 888;
my $FOUL_GROUP_OFFSET = 2000;

# Structure parameters
my $STRAT_STRUCTURE_SIZE = 95;
my $SECTION_SUMMARY_BASE = 0x13e;
my $SECTION_SUMMARY_SIZE = 22;
my $PLAYER_STRUCTURE_SIZE = 120;
my $TEAM_MATCH_ENTRY_SIZE = 32;

sub decode {
  # Loads and parses a game file
  if (scalar(@_) < 1 || scalar(@_) > 3) { die "function requires 1-3 arguments."; }
  my ($fname, $opt, $bws) = @_;
  if (ref($fname) ne '') { die '1st argument must be a scalar.'; }
  if (!defined $opt) { $opt = {}; }
  elsif (ref($opt) ne 'HASH') { die '2nd argument must be a hashref or undef.'; }
  if (defined $bws && ref($bws) ne 'HASH') { die "3rd argument must be a hashref or undef."}
  
  my $data;
  # Safely isolate $/ change.
  {
    local $/; my $fh;
    return($ERR_FILE_ERR) if !open($fh, '<', $fname);
    binmode($fh);
    $data = <$fh>;
    close($fh);
  }
  
  # Check for the 'AC3' magic bytes that appear at the start of all ACBLscore
  # game files.
  return($ERR_NOT_GAME_FILE) if (substr($data,0,6) ne "\x12\x0a\x03AC3");
  
  my ($p, $event_type_id, $event_scoring_id, $rankstr, $pMemoNote);

  my $gm = {'filename' => $fname, 'decode_format_version' => $DECODE_FORMAT_VERSION };
  $gm->{'ACBLscore_version'} = sprintf('%.2f', unpack('v', substr($data, 0x9db, 2)) / 100);
  $gm->{'ACBLscore_min_compatible_version'} = sprintf('%.2f', unpack('v', substr($data, 0x9e1, 2)) / 100);
  $gm->{'creation_timestamp'} = datetime($data, 0x9dd);
  $pMemoNote = unpack('V', substr($data, 0x9d6, 4));
  $gm->{'memo'} = memonote($data, $pMemoNote, 'memo') if $pMemoNote;
  $pMemoNote = unpack('V', substr($data, 0x9e3, 4));
  $gm->{'note'} = memonote($data, $pMemoNote, 'note') if $pMemoNote;
  
  my $ix = 0;
  for (my $i=0; $i<$MAX_EVENTS; $i++) {
    $p = unpack('V', substr($data, 0x12 + 4*$i, 4));
    next if !$p;
    $event_type_id    = unpack('C', substr($data, 0xda  + $i));
    $event_scoring_id = unpack('C', substr($data, 0x10c + $i));
    my $ev = {'event_id' => $i+1,  
      'event_type_id' => $event_type_id, 'event_type', $EVENT_TYPE[$event_type_id], 
      'event_scoring_id' => $event_scoring_id, 'event_scoring', $EVENT_SCORING[$event_scoring_id] };
      
    $rankstr = eventDetails($ev, $data, $p);
    addSectionCombining($ev, $data);
    addSections($ev, $data, $opt, $rankstr, $bws);
    $gm->{'event'}[$ix] = $ev;
    $ix++;
  }
  
  return ($SUCCESS, $gm);
}

sub zstring {
  # zstring(str, offset)
  #
  # Parse a string where first byte gives the length of the string. 

  return substr($_[0], $_[1]+1, unpack('C', substr($_[0], $_[1],1)));
}

sub zstrings {
  # Decode multiple zstring fields and add fields to a hashref.
  # Example: zstrings($hr, $data, $p, 'fdname1', offset1, ...)
  die "At least two arguments are required" if (scalar(@_) < 3);
  die "Last string field has no offset" if (scalar(@_) % 2 == 0);
  my $hr = shift; my $data = shift; my $p = shift; my $fdname;
  while (defined ($fdname = shift)) { $hr->{$fdname} = zstring($data, $p + shift); }
}

sub datetime {
  # Decode ACBLscore (Pascal?) 32-bit encoded date and time.
  my ($data, $p) = @_;
  my ($tm, $dt) = unpack('vv', substr($data, $p, 4));
  my $year  = ($dt >> 9) + 1980;
  my $month = ($dt >> 5) & 0x0F;
  my $day   = $dt & 0x1F;
  my $hour  = $tm >> 11;
  my $min   = ($tm >> 5) & 0x3F;
  my $sec   = ($tm << 1) & 0x3F;
  
  return sprintf('%d-%02d-%02dT%02d:%02d:%02d', $year, $month, $day, $hour, $min, $sec);
}

sub real48 {
  # Decode 48-bit Pascal real number. See:
  # http://www.gamedev.net/topic/326742-conversion-of-pascal-real48-48-bit-float-to-c-double/
  my ($data, $p) = @_;
  
  # A kludge for fields that might not have been set. Some financial fields appear to be
  # real48 but might not ever be set if the situation is not relevant (i.e. not a charity game).
  return 0 if substr($data, $p, 6) eq "\x00\x00\x00\x00\x00\x00";
  
  my $exp = unpack('C', substr($data, $p, 1)) - 129;
  my $mantissa = unpack('n', substr($data, $p+1, 4)) / 4294967296;
  my $byte6 = unpack('C', substr($data, $p+5, 1));
  $mantissa += $byte6 & 0x7F;
  $mantissa *= 0.0078125;
  $mantissa += 1;
  $mantissa = -$mantissa if $byte6 & 0x80;
  
  return $mantissa * 2 ** $exp;
}

sub memonote {
  # Decodes an ACBLscore Memo or Note structure.
  # See http://lajollabridge.com/Articles/ACBLscoreGameFilesDecoded.htm#s-memo
  my ($data, $p, $type) = @_;
  my $linelen = $type eq 'memo' ? 64 : $type eq 'note' ? 76 : 0;
  die '3rd argument must be "memo" or "note"' if ! $linelen;
  my $linecount = unpack('v', substr($data, $p + 4, 2));
  my $text = '';
  for (my $i=0; $i < $linecount; $i++) {
    $text .= zstring($data, $p + 6 + $i * $linelen) . "\n";
  }
  
  return $text;
}

sub eventDetails {
  # Parse event details.
  # See http://lajollabridge.com/Articles/ACBLscoreGameFilesDecoded.htm#s-event-details
  if (scalar(@_) != 3) { die "function requires 3 arguments."; }
  my ($ev, $data, $p) = @_;

  my $isTeams = $ev->{'event_type_id'} == 1;
  
  $ev->{'mp_rating'} = {
    'p-factor' => unpack('v', substr($data, $p + 0x7d)) / 1000,
    't-factor' => unpack('v', substr($data, $p + 0x83)) / 1000,
    's-factor' => unpack('v', substr($data, $p + 0x24f)) / 100
  };
 
  my $club_session_num = unpack('C', substr($data, $p + 0x95));
  # It is not clear the best way to figure out if results are from a tournament.
  # One way is to check whether there is a club number. Another way is to look
  # at the club session number which is what is done below.
  my $isTourney = $club_session_num == 0 ? 1 : 0;
 
  $ev->{'tournament_flag'} = $isTourney;
  if (! $isTourney) {
    $ev->{'club_num'} = zstring($data, $p + 0xb0);
    $ev->{'club_session_num'} = $club_session_num;
    $ev->{'club_game_type'} = $CLUB_GAME_TYPE[unpack('C', substr($data, $p + 0xa1, 1))];
  }
  $ev->{'rating_id'} = unpack('C', substr($data, $p + 0x88));
  $ev->{'rating'} = $EVENT_RATING[ $ev->{'rating_id'} ];
  $ev->{'session_num'} = unpack('C', substr($data, $p + 0x8c, 1));
  $ev->{'handicap_type_id'} = unpack('c', substr($data, $p + 0x8d, 1));
  if ( $ev->{'handicap_type_id'} ) {
    $ev->{'handicap_type'} = $HANDICAP_TYPES[ abs($ev->{'handicap_type_id'}) ];
    $ev->{'handicap_scoring'} = $ev->{'handicap_type_id'} < 0 ? 'single-ranking' : 'double-ranking';
  }
  $ev->{'nstrats'} = unpack('C', substr($data, $p + 0x9e, 1));
  $ev->{'nsessions'} = unpack('C', substr($data, $p + 0x9f, 1));
  $ev->{'consolation_flag'} = unpack('C', substr($data, $p + 0xa0, 1));
  $ev->{'modification_timestamp'} = datetime($data, $p + 0xb7);  
  $ev->{'nbrackets'} = unpack('C', substr($data, $p + 0xc2, 1)) if $isTeams;
  $ev->{'bracket_num'} = unpack('C', substr($data, $p + 0xc3, 1)) if $isTeams;
  $ev->{'continuous_pairs_flag'} = unpack('C', substr($data, $p + 0xce, 1)) if ! $isTeams;
  $ev->{'senior_event_flag'} = unpack('C', substr($data, $p + 0x251, 1));
  $ev->{'mp_award_revision_num'} = unpack('C', substr($data, $p + 0x254, 1));
  $ev->{'stratify_by_avg_flag'} = unpack('C', substr($data, $p + 0x2c8, 1));
  $ev->{'non_ACBL_flag'} = unpack('C', substr($data, $p + 0x2ca, 1));
  # The +0 forces Perl's internal representation to be numeric instead of a string.
  # It doesn't matter for Perl but it does alter the JSON output, e.g. 0 instead of "0"
  $ev->{'final_session_flag'} = ($ev->{'session_num'} == $ev->{'nsessions'}) + 0;
  $ev->{'game_sanction_fee'} = real48($data, $p + 0x275);
  $ev->{'table_sanction_fee'} = real48($data, $p + 0x27b);
  $ev->{'charity_table_sanction_fee'} = real48($data, $p + 0x281);
  
  my $club_or_tournament = $isTourney ? 'tournament' : 'club';
  my $director_or_city   = $isTourney ? 'city' : 'director';
  zstrings($ev, $data, $p, 'event_name', 0x4, 'session_name', 0x1e, 
    $director_or_city, 0x2c, 'sanction', 0x3d, 'date', 0x48, $club_or_tournament, 0x5c,
    'event_code', 0x76, 'qual_event_code', 0xc5, 'hand_set', 0x244, 'local_charity', 0x295);

  my $pMemo = unpack('V', substr($data, $p + 0xbd, 4));
  $ev->{'memo'} = memonote($data, $pMemo, 'memo') if $pMemo;

  my ($rankstr, $LMelig);
  for (my $i=0; $i<$ev->{'nstrats'}; $i++) {
    $ev->{'strat'}[$i] = strat($data, $p + 0xd4 + $i * $STRAT_STRUCTURE_SIZE);
    $LMelig = unpack('C', substr($data, $p + 0x1f7 + $i, 1));
    $ev->{'strat'}[$i]{'LM_eligibility'} =
      $LMelig == -1 ? 'LM Only' : $LMelig == 1 ? 'NLM Only' : 'No Restriction';
    $rankstr .=  $ev->{'strat'}[$i]{'letter'};
  }
  
  return $rankstr;
}

sub strat {
  # Parse strat structure.
  # See http://lajollabridge.com/Articles/ACBLscoreGameFilesDecoded.htm#s-strat
  if (scalar(@_) != 2) { die "function requires 2 arguments."; }
  my ($data, $p) = @_;
  
  my $st = {
    'first_overall_award' => unpack('v', substr($data, $p + 0x10, 2)) / 100,
    'ribbon_color' => $RIBBON_COLORS[unpack('C', substr($data, $p + 0x12, 1))],
    'ribbon_depth' => unpack('C', substr($data, $p + 0x13, 1)),
    'mpt_factor' => unpack('V', substr($data, $p + 0x14, 4)) / 10000,
    'overall_award_depth' => unpack('v', substr($data, $p + 0x18, 2)),
    'table_basis' => unpack('C', substr($data, $p + 0x1a, 2)),
    'min_mp' => unpack('v', substr($data, $p + 0x1e, 2)),
    'max_mp' => unpack('v', substr($data, $p + 0x20, 2)),
    'letter' => substr($data, $p + 0x22, 1),
    'club_pct_open_rating' => unpack('C', substr($data, $p + 0x23, 1)),
    'event_m_factor' => real48($data, $p + 0x24),
    'session_m_factor' => real48($data, $p + 0x2a),    
    'pigmentation_breakdown' => {
      'overall' => pigmentation($data, $p + 0x32),
      'session' => pigmentation($data, $p + 0x41),
      'section' => pigmentation($data, $p + 0x50)
    }
  };

}

sub pigmentation {
  # Parse masterpoint pigmentation structure.
  # See http://lajollabridge.com/Articles/ACBLscoreGameFilesDecoded.htm#s-pigmentation
  if (scalar(@_) != 2) { die "function requires 2 arguments."; }
  my ($data, $p) = @_;
  
  my (@pgset, $i, $j, $mp, $tp);
  my @pct = unpack('v3', substr($data, $p, 6));
  my @mp  = unpack('v3', substr($data, $p+6, 6));
  my @tp  = unpack('C3', substr($data, $p+12, 12));
  
  for ($i=0; $i<3; $i++) {
    last if ! $pct[$i];
    push @pgset, {'pct' => $pct[$i] / 100, 'mp' => $mp[$i] / 100,
      'type' => substr($PIGMENTATION_TYPES, $tp[$i], 1) }; 
  }
  return \@pgset;
}

sub addSectionCombining {
  # Work out how sections are combined and ranked together. Only 
  # combined sections may optionally be ranked together.
  if (scalar(@_) != 2) { die "function requires 2 arguments."; }
  my ($ev, $data) = @_;
  
  my ($prevScore, $prevRank, $nextScore, $nextRank);
  my @combining_and_ranking;

  # Search Master Table for all sections belonging to the event.
  my ($p, $pc, $pr);
  for (my $i=0; $i<$MAX_SECTIONS; $i++) {
    $p = $SECTION_SUMMARY_BASE + $SECTION_SUMMARY_SIZE * $i;
    next if unpack('C', substr($data, $p, 1)) != $ev->{'event_id'};
    
    $prevScore = unpack('C', substr($data, $p + 0xf, 1));
    next if $prevScore != 0;
    # Found first section in a group of combined sections.
    my @combined;
    $pc = $p;
    while (1) {
      $prevRank = unpack('C', substr($data, $pc + 0x11, 1));
      if ($prevRank == 0) {
        # Found first section in a group of sections ranked together (applies to
        # section awards, i.e. N-S and E-W can be ranked across multiple sections).
        my @rankedTogether;
        $pr = $pc;
        while (1) {
          push @rankedTogether, zstring($data, $pr + 0x1);
          $nextRank = unpack('C', substr($data, $pr + 0x12));
          if ($nextRank == 0) { push @combined, \@rankedTogether; last; }
          $pr = $SECTION_SUMMARY_BASE + $SECTION_SUMMARY_SIZE * ($nextRank-1);
        }
      }
      $nextScore = unpack('C', substr($data, $pc + 0x10, 1));
      last if $nextScore == 0;
      $pc = $SECTION_SUMMARY_BASE + $SECTION_SUMMARY_SIZE * ($nextScore-1);      
    }
    push @combining_and_ranking, \@combined;
  }
  
  $ev->{'combining_and_ranking'} = \@combining_and_ranking;
}

sub addSections {
  if (scalar(@_) != 5) { die "function requires 5 arguments."; }
  my ($ev, $data, $opt, $rankstr, $bws) = @_;
  
  # Search Master Table for all sections belonging to the event.
  # See http://lajollabridge.com/Articles/ACBLscoreGameFilesDecoded.htm#t-master
  my $p = $SECTION_SUMMARY_BASE;
  for (my $i=0; $i<$MAX_SECTIONS; $i++) {
    $p = $SECTION_SUMMARY_BASE + $i * $SECTION_SUMMARY_SIZE;
    next if unpack('C', substr($data, $p, 1)) != $ev->{'event_id'};
    my $sc = section($data, $p, $opt, $ev->{'event_type_id'}, $rankstr, $bws);
    $ev->{'section'}{$sc->{'letter'}} = $sc; 
  }
}

sub section {
  # Parse section within an event. See:
  # http://lajollabridge.com/Articles/ACBLscoreGameFilesDecoded.htm#s-section-summary
  # http://lajollabridge.com/Articles/ACBLscoreGameFilesDecoded.htm#s-section-details
  if (scalar(@_) != 6) { die "function requires 6 arguments."; }
  my ($data, $p, $opt, $event_type_id, $rankstr, $bws) = @_;
  
  my ($has_overall_rankings, $has_quals) = (0, 0);
  my ($has_rank, $has_qual);
  
  my $sc = {'letter' => zstring($data, $p+1), 'rounds' => unpack('C', substr($data, $p + 0x14)) };
  $sc->{'is_scored'} = unpack('C', substr($data, $p + 0xe)) & 1;

  # Board Results pointer
  my $pBoardIdx = unpack('V', substr($data, $p + 8));
  
  # Move on to Section Details Structure.
  $p = unpack('V', substr($data, $p + 4));

  my @pIndex = unpack('V4', substr($data, $p + 4));
  my $isTeams = $event_type_id == 1;
  my $isIndy  = $event_type_id == 2;
  my $isHomeStylePairs = $event_type_id == 3;
  my $isBAM   = 0 + ($event_type_id == 4);
  
  my $highest_pairnum = unpack('v', substr($data, $p + 0x1b));
  
  $sc->{'movement_type'} = $MOVEMENT_TYPE[ unpack('C', substr($data, $p + 0x18)) ] if ! $isTeams;
  $sc->{'is_barometer'} = unpack('C', substr($data, $p + 0x47)) if ! $isTeams;
  $sc->{'is_web'} = unpack('C', substr($data, $p + 0x60)) if ! $isTeams;
  $sc->{'is_bam'} = $isBAM;
  
  $sc->{'nboards'} = unpack('v', substr($data, $p + 0x19)) if ! $isTeams;
  $sc->{$isBAM ? 'highest_teamnum' : 'highest_pairnum'} = $highest_pairnum if ! $isTeams;
  $sc->{'boards_per_round'} = unpack('C', substr($data, $p + 0x1d));
  $sc->{'max_results_per_board'} = unpack('C', substr($data, $p + 0x61)) if ! $isTeams;
  $sc->{'board_top'} = unpack('v', substr($data, $p + 0x1e)) if ! $isTeams;
  $sc->{'ntables'} = unpack('v', substr($data, $p + 0x48));
  
  $sc->{'match_award'} = unpack('v', substr($data, $p + 0xb5)) / 100 if $isTeams;
  $sc->{'maximum_score'} = unpack('v', substr($data, $p + 0x4e));
  $sc->{'modification_timestamp'} = datetime($data, $p + 0xbd);

  my $pMemo = unpack('V', substr($data, $p + 0xd1, 4));
  $sc->{'memo'} = memonote($data, $pMemo, 'memo') if $pMemo;

  return $sc if $opt->{'sectionsonly'};

  my $isHowell = unpack('C', substr($data, $p + 0x18)) == 1 ? 1 : 0;
  my $phantom = unpack('c', substr($data, $p + 0x43));
  
  my $bws2 = defined $bws ? $bws->{$sc->{'letter'}} : undef;
  
  my ($i, $j);
  if ($isHomeStylePairs) {
    # This is a rare format used when there are only two tables. It is a cross
    # between pairs and teams in that the four pairs get paired off in each of
    # the three possible ways to form three teams sessions with each pair being
    # scored by cummulative victory points.
    my $pEntry;
    if ( !$opt->{'noentries'} ) {
      # Don't know if pair reassignments are permitted for these events. Even
      # if they happen it seems like it would be infrequent since it is hard
      # to botch up only four pairs. Ignore this issue.
      for ($i=1; $i<=$highest_pairnum; $i++) {
        $pEntry = unpack('V', substr($data, $pIndex[0] + 0x10 + 8 * $i, 4));
        ($sc->{'entry'}{$i}, $has_rank, $has_qual) = entry($data, $pEntry, $opt, $rankstr);
        $has_overall_rankings = 1 if $has_rank;
        $has_quals = 1 if $has_qual;
      }
    }
      
    my $pTeamMatch = unpack('V', substr($data, $p + 0x23d));
    $sc->{'matches'} = teamMatches($data, $pTeamMatch, $pIndex[0]) if $pTeamMatch;      
  }
  elsif ($isHowell) {
    # Howell can be a pairs or an individual event.
    $sc->{'is_howell'} = $isHowell;
    if ( !$opt->{'noentries'} ) {    
      my $pPNM = $p + 0xdd;
      my ($pairnum, $table, $dir, $str, $pEntry);
      my @reassign = unpack('C80', substr($data, $p + 0xdd, 80));
      for ($i=1; $i<=$highest_pairnum; $i++) {
        $pairnum = $i;
        next if $pairnum == $phantom;

        $str = substr($data, $pPNM + 0x50 + 2*($pairnum-1), 2);
        ($table, $dir) = unpack('C2', $str);
        $pEntry = unpack('V', substr($data, $pIndex[$dir-1] + 0x10 + 8 * $table, 4));
  
        # Rare pair number reassignments with ACBLscore EDMOV command.
        $pairnum = $reassign[$i-1] if $reassign[$i-1];
  
        # IF clause is a quick hack to filter out phantom pairs.
        if ( unpack('v', substr($data, $pEntry + 0x1c, 2)) != 0 ) {
          ($sc->{'entry'}{$pairnum}, $has_rank, $has_qual) = entry($data, $pEntry, $opt, $rankstr);
          $has_overall_rankings = 1 if $has_rank;
          $has_quals = 1 if $has_qual;
        }
      }
    }

    # Need to check $pBoardIdx. It will be 0 (NULL) if the event is manually scored, i.e. manually
    # matchpointed with ACBLscore only used to assign masterpoints. This is very rare.
    $sc->{'board'} = boards($data, $pBoardIdx, $p, $isIndy, $bws2) if !$opt->{'noboards'} && $pBoardIdx;
  }
  elsif (!$isTeams && !$isBAM) {
    # Mitchell movement
    $sc->{'is_howell'} = $isHowell;
    if ( !$opt->{'noentries'} ) {
    my $pPNM = $p + 0xdd;
      my $ndir = $isIndy ? 4 : 2;
      my ($pairnum, $table, $pEntry);
      my @dirletter = ('N', 'E', 'S', 'W'); 
      my @reassign = unpack('C160', substr($data, $p + 0xdd, 160));
      my @maxEntry = ( unpack('C', substr($data, $pIndex[0] + 6, 1)), 
                       unpack('C', substr($data, $pIndex[1] + 6, 1)) );
      
      for ($i=1; $i<=$highest_pairnum; $i++) {
        for ($j=0; $j<$ndir; $j++) {
          $pairnum = $i;
          next if $pairnum == $phantom && $j == 0 || $pairnum == -$phantom && $j == 1;
          $table = unpack('C', substr($data, $pPNM + 0xa0 + 4*($pairnum-1) + $j, 1) );
          $pEntry = unpack('V', substr($data, $pIndex[$j] + 0x10 + 8 * $table, 4));
  
          # Rare pair number reassignments with ACBLscore EDMOV command.
          $pairnum = $reassign[4*($i-1)+$j] if $reassign[4*($i-1)+$j];
          
          # IF clause is a quick hack to filter out phantom pairs. First check is needed to
          # avoid generating a warning when a Michell movement has a bump pair.
          if ( $pairnum <= $maxEntry[$j] && unpack('v', substr($data, $pEntry + 0x1c, 2)) != 0 ) {
            ($sc->{'entry'}{$pairnum . $dirletter[$j]}, $has_rank, $has_qual) = 
              entry($data, $pEntry, $opt, $rankstr);
            $has_overall_rankings = 1 if $has_rank;
            $has_quals = 1 if $has_qual;
          }
        }
      }
    }

    $sc->{'board'} = boards($data, $pBoardIdx, $p, $isIndy, $bws2) if !$opt->{'noboards'} && $pBoardIdx;
  }
  elsif ($isTeams || $isBAM) {
    if ( !$opt->{'noentries'} ) {
      my ($teamnum, $nplayers, $pTeam, $pEntry);
      my $nteams = unpack('C', substr($data, $pIndex[0] + 6, 1));
      $sc->{'nteams'} = $nteams;
      
      $pTeam = $pIndex[0] + 0x14;
      for ($i=0; $i<$nteams; $i++) {
        $teamnum  = unpack('v', substr($data, $pTeam, 2));
        $nplayers = unpack('v', substr($data, $pTeam + 2, 2));
        $pEntry   = unpack('V', substr($data, $pTeam + 4, 4));
        ($sc->{'entry'}{$teamnum}, $has_rank, $has_qual) = entry($data, $pEntry, $opt, $rankstr, $nplayers);
        $has_overall_rankings = 1 if $has_rank;
        $has_quals = 1 if $has_qual;
        $pTeam += 8;
      }
    }
    
    if ($isTeams) {
      my $pTeamMatch = unpack('V', substr($data, $p + 0x23d));
      $sc->{'matches'} = teamMatches($data, $pTeamMatch, $pIndex[0]) if $pTeamMatch;
    }
    
    if ($isBAM) {
      $sc->{'board'} = boards($data, $pBoardIdx, $p, $isIndy, $bws2) if !$opt->{'noboards'} && $pBoardIdx;
    }
  }
  
  $sc->{'has_overall_rankings'} = $has_overall_rankings;
  $sc->{'has_quals'} = $has_quals;

  return $sc;
}

sub entry {
  # Parse an entry, i.e. the fundamental competitive unit. This is an individual, pair, or
  # team depending on the event. See:
  # http://lajollabridge.com/Articles/ACBLscoreGameFilesDecoded.htm#s-individual
  # http://lajollabridge.com/Articles/ACBLscoreGameFilesDecoded.htm#s-pair
  # http://lajollabridge.com/Articles/ACBLscoreGameFilesDecoded.htm#s-team
  if (scalar(@_) != 4 && scalar(@_) != 5) { die "function requires 4-5 arguments."; }
  my ($data, $p, $opt, $rankstr, $nplayers) = @_;
  
  my $en;
  my @intfloats = unpack('l<6', substr($data, $p + 0x4, 24));
  
  $en->{'score_adjustment'} = $intfloats[0] / 100;
  $en->{'score_unscaled'}   = $intfloats[1] / 100;
  $en->{'score_session'}    = $intfloats[2] != -1 ? $intfloats[2] / 100 : undef;
  $en->{'score_carrover'}   = $intfloats[3] / 100;
  $en->{'score_final'}      = $intfloats[4] != -1 ? $intfloats[4] / 100 : undef;
  $en->{'score_handicap'}   = $intfloats[5] / 100;
  
  $en->{'pct'} =  unpack('v', substr($data, $p + 0x1c, 2)) / 100;
  $en->{'strat_num'} =  unpack('C', substr($data, $p + 0x1e, 1));
  $en->{'mp_average'} =  unpack('v', substr($data, $p + 0x20, 2));
  $en->{'nboards'} =  unpack('C', substr($data, $p + 0x2f, 1));
  $en->{'eligibility'} =  unpack('C', substr($data, $p + 0x33, 1));

  my $award = award($data, $p + 0x34, $rankstr);
  $en->{'award'} = $award if defined $award;
  ($en->{'rank'}, my $has_overall_rank, my $has_qual) = rank($data, $p + 0x5e);
  
  my $next_section = zstring($data, $p + 0x28);
  if ($next_section eq '98') { $en->{'next_section'} = 'Resigned'; }
  elsif ( $next_section ne '' ) {
    $en->{'next_section'} = $next_section;
    $en->{'next_dir'} = substr($data, $p + 0x2b, 1);
    $en->{'next_table'} = unpack('v', substr($data, $p + 0x2c, 2));
  }
  
  # There are three ways to determine the maximum number of players in an entry 
  # structure. The method here is based on the size of the player structure and will
  # return 1, 2, or 6. The second and probably more proper method is to use the number
  # from the entry index table. The third is to infer it from the event type.
  $nplayers = (unpack('v', substr($data, $p + 0, 2)) - 0xa2) / $PLAYER_STRUCTURE_SIZE
    if !defined $nplayers;
  
  if ($nplayers <= 2) {
    for (my $i=0; $i<$nplayers; $i++) {
      $en->{'player'}[$i] = player($data, $p + 0xa4 + $i * $PLAYER_STRUCTURE_SIZE, $opt, $rankstr);    
    }
  }
  else {
    # Typically only have four players on a team but up to six are possible.
    # Only return the player structures for actual players.
    my $j=0;
    for (my $i=0; $i<$nplayers; $i++) {
      my $pl = player($data, $p + 0xa4 + $i * $PLAYER_STRUCTURE_SIZE, $opt, $rankstr);
      next if $pl->{'lname'} eq '' && $pl->{'fname'} eq '' && $pl->{'pnum'} eq '';
      $en->{'player'}[$j] = $pl;
      $j++ 
    }
  }
  
  return ($en, $has_overall_rank, $has_qual);
}

sub player {
  # Parse player structure.
  # See http://lajollabridge.com/Articles/ACBLscoreGameFilesDecoded.htm#s-player
  if (scalar(@_) != 4) { die "function requires 3 arguments."; }
  my ($data, $p, $opt, $rankstr) = @_;
  
  my ($pl, $award);
  $pl->{'team_wins'} = unpack('v', substr($data, $p + 0x44, 2)) / 100;
  $pl->{'mp_total'}  = unpack('v', substr($data, $p + 0x71, 2));
  $pl->{'acbl_rank_letter'} = substr($data, $p + 0x73, 1);
  $pl->{'acbl_rank'} = $ACBL_PLAYER_RANKS{$pl->{'acbl_rank_letter'}};

  zstrings($pl, $data, $p, 'lname', 0, 'fname', 0x11, 'city', 0x22, 'state', 0x33,
    'pnum', 0x36, 'country', 0x75);
  $pl->{'db_key'} = zstring($data, $p + 0x3e) if $opt->{'binaryfields'};
    
  $award = award($data, $p + 0x48, $rankstr);
  $pl->{'award'} = $award if defined $award;

  return $pl;
}

sub award {
  # Parse masterpoint award structure.
  # See http://lajollabridge.com/Articles/ACBLscoreGameFilesDecoded.htm#s-masterpoints
  if (scalar(@_) != 3) { die "function requires 3 arguments."; }
  my ($data, $p, $rankstr) = @_;

  my ($awset, $i, $j, @v, $anyAward, $reason);
  # Loop over "previous", "current", and "total" awards.
  for ($i=0; $i<3; $i++) {
    @v = unpack('(vCC)3', substr($data, $p + $i * 12, 12) );
    my @aw;
    for ($j=0; $j<=6; $j+=3) {
      # Normally want to terminate when list of up to 3 masterpoint pigmentation types ends.
      # However, for handicapped games which are scored both with and without the handicap,
      # the first entry is the award with the handicap and the second entry is the award
      # without the handicap and therefore the second entry can have an award even though
      # the first does not.
      last if ! $v[$j] && ($j != 0 || ! $v[$j+3]);
      $anyAward = 1;
      $reason = $v[$j+2] ?
        ($v[$j+2] >= 10 ? 'O' : 'S') . substr($rankstr, $v[$j+2] % 10 - 1, 1) : '';
      push @aw, [$v[$j] / 100, substr($PIGMENTATION_TYPES, $v[$j+1], 1), $reason, $v[$j+2]];
    }
    $awset->{ $AWARD_SETS[$i] } = \@aw;
  }
  return $anyAward ? $awset : undef;
}

sub rank {
  # Parse ranking structure (for an entry)
  # See http://lajollabridge.com/Articles/ACBLscoreGameFilesDecoded.htm#s-ranking
  if (scalar(@_) != 2) { die "function requires 2 arguments."; }
  my ($data, $p) = @_;
  
  my (@rkset, $i, @v);
  my ($hasOverallRank, $hasQual);
  for ($i=0; $i<3; $i++) {
    # Currently not unpacking pointers to next lowest rank.
    @v = unpack('v6', substr($data, $p + $i * 20, 20));
    # Don't include zeros from strats that entry or player is not eligible to
    # be ranked in.
    last if !$v[5] && !$v[4];
    my $rk = {'section_rank_low' => $v[0], 'section_rank_high' => $v[1],
      'overall_rank_low' => $v[2], 'overall_rank_high' => $v[3],
      'qual_flag' => $v[4], 'rank' => $v[5] };
    push @rkset, $rk;
    $hasOverallRank = 1 if $v[2];
    $hasQual = 1 if $v[4];
  }
  return (\@rkset, $hasOverallRank, $hasQual);
}

sub boards {
  # Parse the boards results for a pair or individual event. See:
  # http://lajollabridge.com/Articles/ACBLscoreGameFilesDecoded.htm#t-board2-results
  # http://lajollabridge.com/Articles/ACBLscoreGameFilesDecoded.htm#t-board4-results
  if (scalar(@_) != 5) { die "function requires 5 arguments."; }
  my ($data, $pBoardIdx, $pSection, $isIndy, $bws2) = @_; 
  
  my (%bdset, $i, $j, $k, $bnum, $p, $nresults, $dr, $foulGroup);
  my $ncompetitors = $isIndy ? 4 : 2;
  my $fmt = 'CC(vs<V)' . $ncompetitors;
  my $resultSize = 2 + 8 * $ncompetitors;
  my $nboards = unpack('v', substr($data, $pBoardIdx + 4, 2));
  my $kupper = 3 * $ncompetitors + 2;

  # Deal with possible EDMOV pair reassignment, first checking if any reassignments
  # have occurred to minimize time spent in the loops below.
  my $isHowell = unpack('C', substr($data, $pSection + 0x18));
  my @reassign = $isHowell ? unpack('C80', substr($data, $pSection + 0xdd, 80)) :
    unpack('C160', substr($data, $pSection + 0xdd, 160));
  my $anyReassignedPairs = 0;
  my ($bws3, $contract, $contractresult, $declarer, $lead);
  # It's not clear if individual reassignments are possible in an individual event.
  # Don't bother for such. Individual events are rare and reassignments are rarer.
  if (!$isIndy) { foreach my $val (@reassign) { if ($val) {$anyReassignedPairs = 1; last; } } }

  for ($i=0; $i<$nboards; $i++) {
    my @bd;
    ($bnum, $nresults, $p) = unpack('CxvV', substr($data, $pBoardIdx + 0x26 + $i * 8, 8));
    $bws3 = $bws2->{$bnum};

    $p += 6;
    while ($nresults) {
      my @v = unpack($fmt, substr($data, $p, $resultSize));
      $p += $resultSize;
      # Skip if board is not in play on this round.
      next if $v[3] == 999;
      # Scheduled Late Play and Not Played results also do not count towards total number
      # of valid results in $NRESULTS.
      $nresults-- if $v[3] != 900 && $v[3] != 950;
      for ($k=2; $k<$kupper; $k+=3) {
        if ($anyReassignedPairs) {
          if ($isHowell) { $v[$k] = $reassign[$v[$k]-1] if $reassign[$v[$k]-1] }
          else {
            # 0 for N-S, 1 for E-W
            $dr = ($k == 5);
            $v[$k] = $reassign[4*($v[$k]-1)+$dr] if $reassign[4*($v[$k]-1)+$dr];
          }  
        }
        if ($v[$k+1] < 900) { $v[$k+1] *= 10; }
        elsif ($v[$k+1] < 3000) {
          $v[$k+1] = $SPECIAL_SCORES{$v[$k+1]};
          $v[$k+1] = 'Unknown' if !defined $v[$k+1];
        }
        else {
          # Have a fouled score. These occur when a board is not the same on each round
          # within a section or it differs between sections. This can happen when players
          # mix up the cards between hands when returning them to the board, when a board
          # is changed midway through a session because a player recognizes it from a 
          # previous section because it wasn't shuffled, or when players misduplicate
          # hands (more commmon up to the 1990s before dealing machines became widespread).
          # ACBLscore allows up to eight separate groups of results for scoring, the main
          # group, and seven "foul groups".
          $foulGroup = int( ($v[$k+1] - 1000) / $FOUL_GROUP_OFFSET );
          $v[$k+1] -= $FOUL_GROUP_OFFSET * ($foulGroup + 1);
          $v[$k+1] = ($v[$k+1] * 10) . 'F' . $foulGroup;
        }
        $v[$k+2] /= 100;
      }
    
      # BWS2 has electronic scoring results for the current section (if available).
      if (defined $bws3) {
        # $v[2] has the N-S pair number.
        $contract = $bws3->{$v[2]}{'Contract'};
        if (!$contract) {
          # Typically have an empty string for $CONTRACT when the board is not played
          # because the pair was too slow. Can also have an empty string if pairs are
          # assigned AVE, AVE+, or AVE-.
          push @v, '', '', '', '', undef;
        }
        elsif ($contract eq 'PASS') {
          push @v, 'PASS', '', '', '', undef;
        }
        else {
          substr($contract,2,3) = 'N' if substr($contract,2,2) eq 'NT';
          $contract =~ tr/x/*/; $contract =~ s/\s//g;
          push @v, 0 + substr($contract,0,1), substr($contract,1);
          
          $contractresult = $bws3->{$v[2]}{'Result'};
          $contractresult = 0 if $contractresult eq '=';
          $declarer = $bws3->{$v[2]}{'NS/EW'};
          push @v, $declarer, 0 + $contractresult, ;
          
          $lead = $bws3->{$v[2]}{'LeadCard'};
          push @v, (defined $lead ? $lead : '');
        }
      }
          
      push @bd, \@v;
    }
    $bdset{$bnum} = \@bd;
  }
  return \%bdset;
}

sub teamMatches {
  # Parse the team matchups
  # See http://lajollabridge.com/Articles/ACBLscoreGameFilesDecoded.htm#t-team-match
  if (scalar(@_) != 3) { die "function requires 3 arguments."; }
  my ($data, $p, $pIndex) = @_;
  
  my ($i, $j, $nmatches, $pTMT, $pTME);
  
  # Construct mapping from Team Entry ID to Team number.
  my ($nteams, $nrounds) = unpack('vv', substr($data, $p + 4, 4));
  my @tmap = unpack("(vx6)$nteams", substr($data, $pIndex + 0x14, 8 * $nteams));
  my @pTMT = unpack("V$nteams", substr($data, $p + 0x56, 4 * $nteams));
  
  my $tmset;
  for ($i=0; $i<$nteams; $i++) {
    my @tm;
    # Pointer to Team Match Table
    $pTMT = $pTMT[$i];
          
    # A team might not play all rounds of the event, e.g. when a team gets
    # knocked out of Knockout event (Knockout, ZIP Knockout, Compact Knockout).
    $nmatches = unpack('C', substr($data, $pTMT + 7, 1));
    $nmatches = unpack('C', substr($data, $pTMT + 4, 1)) if $nmatches == 0;
    
    for ($j=0; $j<$nmatches; $j++) {
      # Team Match Entry
      $pTME = $pTMT + 0x22 + $j * $TEAM_MATCH_ENTRY_SIZE;
      push @tm, {
        'round' => unpack('C', substr($data, $pTME + 1, 1)),
        'vs_team' => unpack('v', substr($data, $pTME + 2, 2)),
        'IMPs' => unpack('s<', substr($data, $pTME + 8, 2)),
        'VPs' => unpack('v', substr($data, $pTME + 0x0a, 2)) / 100,
        'nboards' => unpack('C', substr($data, $pTME + 0x0d, 1)),
        'wins' => unpack('v', substr($data, $pTME + 0x16, 2)) / 100
      } 
    }
    $tmset->{$tmap[$i]} = \@tm;
  }
  
  return $tmset;
}

sub readBWSfiles {
  # Read Bridgemate / BridgePad / BridgeScorer BWS file(s).
  #
  # Input is an arrayref of filenames or a single filename as a scalar.  
  if (scalar(@_) != 1) { die "function requires 1 argument."; }
  my ($fnames) = @_;
  if ( ref($fnames) eq '' ) { $fnames = [$fnames]; }
  elsif ( ref($fnames) ne 'ARRAY') { 
    error('First argument must be an arrayref or a scalar');
  }

  my ($bws, $errmsg);
  foreach my $fname (@$fnames) {
    if (!-f $fname) { return "File does not exist: $fname"; }
  
    my ($bsc, $brd);
    my $ctrcnt = 0; my $leadcnt = 0;
    
    if ($^O eq 'MSWin32') {
      require DBI;
      require DBD::ODBC;
      
      my $dsn = "driver=Microsoft Access Driver (*.mdb);dbq=$fname";
      my $dbh = DBI->connect("dbi:ODBC:$dsn", {ReadOnly => 1, PrintError => 0});
      
      if (!$dbh) { return "Database open for $fname failed. Was it a BWS file?\n" . DBI->errstr; }
      
      my $sql;
      $sql = "select * from Section";
      $bsc = $dbh->selectall_hashref($sql, ['ID']);
      return "Database query failed: $sql\n" . $dbh->errstr if $dbh->err;
           
      $sql = "select * from ReceivedData";
      $brd = $dbh->selectall_hashref($sql, ['Section', 'Board', 'PairNS']);
      return "Database query failed: $sql\n" . $dbh->errstr if $dbh->err;  
          
      $dbh->disconnect;
    }
    else {
      # Rely on mdb-export program from mdbtools package on non-Windows platforms.
      my ($data, $colnames, $rownum, $row);
      ($errmsg, $data, $colnames) = mdbReadTable($fname, 'Section');
      return $errmsg if $errmsg;
      
      while ( ($rownum, $row) = each %$data ) { $bsc->{$row->{'ID'}} = $row; }
      
      ($errmsg, $data, $colnames) = mdbReadTable($fname, 'ReceivedData');
      return $errmsg if $errmsg;
      
      while ( ($rownum, $row) = each %$data ) {
        $brd->{$row->{'Section'}}{$row->{'Board'}}{$row->{'PairNS'}} = $row;
        $ctrcnt++ if $row->{'Contract'} ne '';
        $leadcnt++ if $row->{'LeadCard'} ne '';
      }
    }
  
    foreach my $id (sort { $bsc->{$a}{'Letter'} cmp $bsc->{$b}{'Letter'} } keys %$bsc ) {
      my $secletter = $bsc->{$id}{'Letter'}; 
      
      # Strip whitespace from section letters. Problems usually seems to be one
      # or two trailing spaces but try to guard against other cases too.
      $secletter =~ s/\s+//g;
      
      # Transfer sections to $BWS, noting any replacements.
      if ( exists $bws->{$secletter} ) {
        print STDERR "Previous section $secletter data replaced by results in file: $fname\n";
      }
      
      $bws->{$secletter} = $brd->{$id};
    }
  }
  
      
  # BridgePad stores the opening lead as value-suit instead of suit-value as
  # Bridgemate does. Convert BridgePad format to Bridgemate format for standard
  # handling.
  my ($section, $bnum, $NSPair, $row, $lead);
  foreach $section (keys %$bws) {
    foreach $bnum (keys %{$bws->{$section}} ) {
      while ( ($NSPair, $row) = each %{$bws->{$section}{$bnum}} ) {
        $lead = $row->{'LeadCard'};
        if (defined $lead && substr($lead,-1) =~ /[CDHS]/) {
          $bws->{$section}{$bnum}{$NSPair}{'LeadCard'} = substr($lead,-1) . substr($lead,0,-1);
        }
      }
    }
  }

  return('', $bws);
}

sub mdbReadTable {
  # Read a table from a JET database using mdb-export program of mdbtools package.
  if (scalar(@_) != 2) { die "function requires 2 arguments."; }
  my ($fname, $tname) = @_;
  
  my $mdbname = 'mdb-export';
  
  my $cmd = "\"$mdbname\" -Q \"$fname\" \"$tname\"";
  my $str = `$cmd`;
  if (${^CHILD_ERROR_NATIVE} != 0) {
    print <<"END";

  Failed to read \"$tname\" table from file \"$fname\" using mdb-export.
  The exit code was ${^CHILD_ERROR_NATIVE}.

  Maybe the mdbtools package is not installed on your system. On Ubuntu
  (Debian) you can install it via:

    apt-get install mdbtools       (if logged in as root)
    sudo apt-get install mdbtools  (if you have permission to install packages)
    
  Prepackaged binaries and dynamic libraries are available for Mac OS X.
  See the online documentation for ACBLgamedump.pl
  
END

    return("Failed to read \"$tname\" table from file \"$fname\" using mdb-export.");
  }
  
  my $rownum = 0;
  my (%data, @fd);
  open(my $fh, '<', \$str);
  my $fline = <$fh>;
  chomp($fline);
  my @colnames = split /,/, $fline;
  while (defined ($fline = <$fh>)) {
    chomp($fline);
    @fd = split /,/, $fline;
    $rownum++;
    for (my $i=0; $i<$#colnames; $i++) { $data{$rownum}{$colnames[$i]} = $fd[$i]; }
  }
  close($fh);

  return ('', \%data, \@colnames);
}

# This is required to inform Perl that package has been loaded successfully.
1;
