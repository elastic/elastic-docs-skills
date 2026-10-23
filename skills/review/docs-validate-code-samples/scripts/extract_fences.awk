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
# Emit one tab-separated "file open close info" line per code block (opening and closing fence line numbers).
# Skips directive fences (info starts with "{") and blocks inside HTML comments.
# An unclosed fence is emitted as "file open UNCLOSED info" (tab-separated).
function flush_unclosed() {
  if (open && !skip) print prev "\t" start "\tUNCLOSED\t" info
  open = 0
}
FNR == 1 { flush_unclosed(); prev = FILENAME; in_comment = 0 }
{
  line = $0; sub(/\r$/, "", line)
  if (!open && line ~ /<!--/ && substr(line, index(line, "<!--") + 4) !~ /-->/) in_comment = 1
  if (match(line, /^[ \t]*`+/)) {
    s = substr(line, RSTART, RLENGTH); gsub(/[ \t]/, "", s); n = length(s)
    rest = substr(line, RLENGTH + 1)
    sub(/^[ \t]+/, "", rest); sub(/[ \t]+$/, "", rest)
    if (open) {
      if (n >= open && rest == "") {
        if (!skip) print FILENAME "\t" start "\t" FNR "\t" info
        open = 0
      }
    } else if (n >= 3 && index(rest, "`") == 0 && !in_comment) {
      open = n; start = FNR; info = rest
      skip = (substr(rest, 1, 1) == "{")
    }
  }
  if (!open && in_comment && line ~ /-->/) in_comment = 0
}
END { flush_unclosed() }
