#!/usr/bin/env perl
# Copyright Elasticsearch B.V. and/or licensed to Elasticsearch B.V. under one
# or more contributor license agreements. See the NOTICE file distributed with
# this work for additional information regarding copyright
# ownership. Elasticsearch B.V. licenses this file to you under
# the Apache License, Version 2.0 (the "License"); you may
# not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#	http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing,
# software distributed under the License is distributed on an
# "AS IS" BASIS, WITHOUT WARRANTIES OR CONDITIONS OF ANY
# KIND, either express or implied.  See the License for the
# specific language governing permissions and limitations
# under the License.
# Check D for one console or console-result block.
# usage: perl check_console.pl FILE OPEN CLOSE KIND     (KIND = console | console-result)
# prints: FILE:LINE:SEVERITY:CHECK:message   (nothing when the block is clean)
use strict; use warnings;
use File::Temp qw(tempfile);
my ($file, $open, $close, $kind) = @ARGV;
open(my $fh, '<', $file) or die "cannot read $file: $!";
my @l = <$fh>; close $fh; chomp @l; s/\r$// for @l;
my @body = @l[$open .. $close - 2];      # file lines OPEN+1 .. CLOSE-1
my $first = $open + 1;
my (undef, $errfile) = tempfile('jqerr-XXXXXX', TMPDIR => 1, UNLINK => 1);   # scratch file in the system temp dir, deleted on exit

# Split into requests. console-result has no method line: treat the whole body as one request.
my @req;
if ($kind eq 'console') {
  for my $i (0 .. $#body) {
    if ($body[$i] =~ /^\s*(GET|PUT|POST|DELETE|HEAD|PATCH)\s+(\S+)/) { push @req, { start => $first + $i, name => "$1 $2", lines => [] }; next; }
    push @{ $req[-1]{lines} }, $body[$i] if @req;
  }
} else {
  push @req, { start => $first - 1, name => 'response', lines => [@body] };
}

sub strip_strings { my $t = shift; $t =~ s/"(?:[^"\\\n]|\\.)*"/""/g; return $t }
sub line_of { my ($t, $re) = @_; my $n = 0; for my $ln (split /\n/, $t, -1) { $n++; return $n if $ln =~ $re } return 1 }

for my $r (@req) {
  my $t = join("\n", @{ $r->{lines} }) . "\n";
  next if $t =~ /^\s*$/;
  # Painless triple-quoted strings -> placeholder, keeping the line count
  $t =~ s/"""(.*?)"""/'"PAINLESS"' . ("\n" x ($1 =~ tr|\n||))/gse;
  # standalone comments, trailing callout markers (one or more), template variables
  my @out;
  for my $ln (split /\n/, $t, -1) {
    $ln = '' if $ln =~ m{^\s*(?:#|//)};
    $ln =~ s{\s*(?:(?://|#)\s*)?(?:<\d+>\s*)+$}{};
    $ln =~ s/\{\{\{[^{}]*\}\}\}/null/g; $ln =~ s/\{\{[^{}]*\}\}/null/g;
    # trailing explanatory comment after code (Kibana Console accepts these; Check C reports them)
    (my $m = $ln) =~ s/"(?:[^"\\]|\\.)*"/'"' . ('x' x (length($&) - 2)) . '"'/ge;
    $ln = substr($ln, 0, $-[0]) if $m =~ m{(?://|#)};
    push @out, $ln;
  }
  $t = join("\n", @out);
  next if $t =~ /^\s*$/;
  my $s = strip_strings($t);
  my $ctx = $r->{name};
  if ($kind eq 'console') {
    if ($s =~ /\.\.\./) { printf "%s:%d:High:D:`...` in console block (%s); replace with realistic values\n", $file, $r->{start} + line_of($s, qr/\.\.\./), $ctx; next; }
  } else {
    next unless $t =~ /^\s*[\[{]/;                      # text tables and partial fragments are not validated
    my $elided = ($s =~ /\.\.\./) ? 1 : 0;
    $t =~ s/\[\s*\.\.\.[^\]\n]*\]/[]/g; $t =~ s/\{\s*\.\.\.[^}\n]*\}/{}/g;
    $t =~ s/,([ \t]*\n)(?:[ \t]*\n)*[ \t]*\.\.\.[ \t]*,?[ \t]*(?=\n\s*[}\]])/$1/g;   # comma dangling because a standalone `...` line is removed
    $t =~ s/:\s*\.\.\.[ \t]*,(?=[ \t]*\n\s*[}\]])/: null/g;                       # `"key": ...,` as the last property
    $t =~ s/:\s*\.\.\.[ \t]*\n(?=\s*")/: null,\n/g; $t =~ s/:\s*\.\.\.(?=\s*[,}\]]|\s*$)/: null/gm;
    $t =~ s/^\s*\.\.\.\s*,?\s*$//gm;
    $r->{elided} = $elided;
    $s = strip_strings($t);
  }
  if ($s =~ /,\s*[}\]]/) { my $pre = substr($s, 0, $-[0]); my $nl = ($pre =~ tr/\n//); printf "%s:%d:High:D:trailing comma before a closing bracket (%s)\n", $file, $r->{start} + 1 + $nl, $ctx; next; }
  # NDJSON for _bulk (one JSON document per line), otherwise one JSON document
  my @docs;
  if ($r->{name} =~ m{(?:^|[ /])(?:_bulk|_msearch)(?:[?/]|$)}) { my $n = 0; for my $ln (split /\n/, $t, -1) { $n++; push @docs, [$n, $ln] if $ln =~ /\S/ } }
  else { @docs = ([1, $t]) }
  for my $d (@docs) {
    open(my $jq, '|-', "jq -e . >/dev/null 2>'$errfile'") or die;
    print $jq $d->[1]; close $jq;
    if ($? != 0) {
      last if $r->{elided};                              # elided response: cannot be validated
      open(my $e, '<', $errfile); my $msg = join(' ', map { chomp; $_ } <$e>); close $e;
      my ($jl) = $msg =~ /line (\d+)/; $jl ||= 1;
      printf "%s:%d:High:D:invalid JSON (%s): %s\n", $file, $r->{start} + $d->[0] + $jl - 1, $ctx, $msg;
      last;
    }
  }
}
