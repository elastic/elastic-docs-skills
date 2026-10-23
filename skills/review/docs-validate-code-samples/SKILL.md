---
name: docs-validate-code-samples
version: 1.1.0
description: Validate code samples in Elastic documentation markdown files. Checks language identifiers, substitution attributes, callout usage, JSON validity, ES|QL syntax, and Painless scripts. Use when reviewing docs PRs, auditing content, or writing new examples.
disable-model-invocation: true
argument-hint: <file|dir|glob> [--output <path>]
allowed-tools: Read, Glob, Grep, Write, Bash, ToolSearch, mcp__elastic-docs__search_docs, mcp__elastic-docs__get_document_by_url
sources:
  - https://docs-v3-preview.elastic.dev/elastic/docs-builder/tree/main/syntax/code
  - https://docs-v3-preview.elastic.dev/elastic/docs-builder/tree/main/syntax/substitutions
  - https://www.elastic.co/docs/reference/query-languages/esql
---
<!-- Copyright Elasticsearch B.V. and/or licensed to Elasticsearch B.V. under one
or more contributor license agreements. See the NOTICE file distributed with
this work for additional information regarding copyright
ownership. Elasticsearch B.V. licenses this file to you under
the Apache License, Version 2.0 (the "License"); you may
not use this file except in compliance with the License.
You may obtain a copy of the License at

	http://www.apache.org/licenses/LICENSE-2.0

Unless required by applicable law or agreed to in writing,
software distributed under the License is distributed on an
"AS IS" BASIS, WITHOUT WARRANTIES OR CONDITIONS OF ANY
KIND, either express or implied.  See the License for the
specific language governing permissions and limitations
under the License. -->

You are a code sample validator for Elastic documentation. Check every code block in one or more markdown files against the docs-builder style rules and report all violations.

**Never modify documentation source files. Only analyze and report.**

---

## Step 1: Resolve files

Parse `$ARGUMENTS` for an optional `--output <path>` flag (strip it before continuing). Resolve the target:

- **Single `.md` file** — analyze that file only.
- **Directory** — find all `.md` files recursively with `find <dir> -name "*.md" -type f | sort`.
- **Glob** — expand with `bash -O globstar -c 'printf "%s\n" <glob>'`.
- **No argument** — ask: "Please provide a file path, directory, or glob pattern."

---

## Step 2: Extract code blocks

Find blocks with one awk pass instead of grepping for fence lines. Grep cannot tell an opening fence from a closing one, and it mispairs nested fences. Run this with Bash over every resolved file (pass the file list as arguments):

```bash
awk '
function flush_unclosed() {
  if (open && !skip) print prev ":" start ":UNCLOSED:" info
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
        if (!skip) print FILENAME ":" start ":" FNR ":" info
        open = 0
      }
    } else if (n >= 3 && index(rest, "`") == 0) {
      open = n; start = FNR; info = rest
      skip = (substr(rest, 1, 1) == "{") || in_comment
    }
  }
  if (!open && in_comment && line ~ /-->/) in_comment = 0
}
END { flush_unclosed() }
' <files>
```

Each output line is `file:open:close:info`, where `open` and `close` are the line numbers of the opening and closing fences and `info` is everything after the opening backticks (it may be empty). When the file list comes from `find`, use `find <dir> -type f -name '*.md' -print0 | xargs -0 awk '...'` so file names with spaces survive. Split each output line on the first three colons only (file, open, close); everything after the third colon is the info string, which can itself contain colons. Use `open` as the line number in the report. Read lines `open+1` through `close-1` for the body.

The script applies these conventions, so do not re-implement them:

- A fence is a line that starts with three or more backticks, optionally indented. Mid-line backticks and `~~~` are not fences.
- A block closes on a line with at least as many backticks as the opener and nothing after them. This keeps a 4-backtick block that contains ```` ``` ```` lines as one block.
- Carriage returns are stripped, so CRLF files pair correctly.
- Blocks whose info string starts with `{` (for example `{applies_to}`, `{include}`, `{note}`) are MyST directives, not code, and are skipped.
- Blocks inside a multi-line HTML comment are skipped.
- An unclosed fence is emitted as `file:open:UNCLOSED:info` (the same four fields, with `UNCLOSED` in place of `close`). Report it as Check S (structure), Medium severity, with the suggestion to add a closing fence, and do not analyze its body.

From the info string, take the first word as the language identifier and the remaining tokens as attributes (`subs=true`, `callouts=false`). An empty info string means no language identifier.

---

## Step 3: Run checks A through H

Check S (unclosed fence) is reported from Step 2 and needs no separate pass.

### Check A — Missing or unknown language identifier

Two separate findings, with different severity.

**A-1 (Low): empty info string.** Flag any block whose info string is empty. Infer the identifier from the content when it is unambiguous: an HTTP method line (`GET`, `PUT`, `POST`, `DELETE`, `HEAD`) means `console`; a body that starts with `{` or `[` means `json`; `key: value` lines mean `yaml`; `curl`, `apt-get`, or `$ ` prompts mean `bash`; `import`, `def`, or `print(` means `python`; `public class` means `java`; `const`, `let`, or `=>` means `javascript`. Otherwise suggest `text`. Many empty-info blocks are plain output, frontmatter samples, or paths, so do not guess a language for them.

**A-2 (Medium): identifier that is clearly wrong for the content.** Flag a block only when the identifier contradicts the content (for example, `console` on a response with no HTTP method line, or `json` on a body that is not valid JSON-like text), or when it appears in the likely-mistakes table below. Do not flag an identifier merely because it is absent from the accepted list.

Accepted identifiers (in use in `elastic/docs-content`; do not flag any of these):

- Elasticsearch and Kibana: `console`, `console-result`, `esql`, `eql`, `painless`, `kql`, `kuery`
- Shell: `bash`, `sh`, `shell`, `powershell`, `cmd`, `terminal`
- Data and config: `json`, `jsonc`, `yaml`, `yml`, `xml`, `toml`, `ini`, `properties`, `dockerfile`, `nginx`, `gradle`, `diff`
- Languages: `python`, `py`, `javascript`, `js`, `typescript`, `ts`, `java`, `go`, `ruby`, `php`, `csharp`, `swift`, `kotlin`, `groovy`, `sql`, `html`, `handlebars`
- Text and docs: `text`, `txt`, `plaintext`, `markdown`, `md`, `asciidoc`, `mermaid`, `http`

Flag these as likely mistakes, with the fix:

| Found | Suggest | Why |
|-------|---------|-----|
| `JSON` (any non-lowercase identifier) | `json` | Identifiers are lowercase. |
| `console-response` | `console-result` | `console-result` is the documented response identifier. Verify against the docs-builder code syntax page before flagging if unsure. |
| `language` | the real identifier | A placeholder left in from a template. |

### Check B — Variable substitution and `subs=true`

This check looks only inside code block bodies. `{{var}}` in prose, headings, or link targets is outside its scope. Only variables that docs-builder substitutes count. Many blocks contain `{{...}}` that is literal template syntax (Mustache, Go templates, workflow expressions, Painless or ingest templates). Flagging those is wrong.

1. Walk up from the target file to find `docset.yml` and parse its `subs:` keys. Count the file's own directory as level 1. Stop at the git root (presence of `.git/`) or after 6 directory levels, whichever comes first.
2. Extract variable names from each block with `\{\{\{?\s*([^{}|]+?)\s*(\|[^{}]*)?\}?\}\}`. This drops mutation filters such as `{{version.stack|M.M}}` and handles `{{{var}}}`.
3. **B-1 (Medium):** flag a block without `subs=true` only when at least one extracted name is a key in `subs:`. Report the matching variable names.
4. **B-2 (Low):** flag `subs=true` on a block with no `{{` at all.
5. Do not flag a block whose `{{...}}` names are all outside `subs:`, for example `{{steps.create_case.output.case.id}}`, `{{event.alerts}}`, `{{foreach.item}}`, `{{#toJson}}`, `{{ctx.payload.hits.total}}`, or `{{.Config.Image}}`.
6. If no `docset.yml` is found, the valid variable names are unknown, so B-1 becomes an unverified advisory (Low). Flag a block without `subs=true` only when a name extracted in step 2 is a single identifier (letters, digits, `_` or `-`, starting with a letter, for example `{{version}}`). Do not flag names with dots, `#`, `/`, `[`, spaces, or other characters, which are template syntax. Label each finding "possible substitution, unverified because no `docset.yml` was found". B-2 runs as normal.

### Check C — Inline comments that should be callouts

For blocks with language `bash`, `sh`, `shell`, `console`, `yaml`, `python`, `javascript`, `js`, `typescript`, `java`, `go`, or `ruby`: flag lines where `#` or `//` appears **after code on the same line** and the comment reads as a reader-facing explanation.

Exemptions: shebang lines, standalone comment lines (no code on the same line), `#` inside strings, lines that end with a callout marker (`<1>`, `// <1>`, or `# <1>`).

Suggestion: replace with explicit callout markers (`<N>`) and a numbered list after the block.

### Check D — JSON validation in `console` and `console-result` blocks

`console` blocks are API requests (customers copy-paste them); `console-result` blocks are responses (display only). Each `console` block contains one or more API calls: an HTTP method+path line (it can be indented inside a list item), followed by an optional JSON body, repeated for multiple calls.

Run the script below once per `console` or `console-result` block, using the `file`, `open`, `close` values from Step 2 and the first word of the info string as `KIND`. Save it to a temp directory outside the repository (`d=$(mktemp -d)`) as `$d/check_console.pl`, then run `TMPDIR=$d perl $d/check_console.pl FILE OPEN CLOSE KIND` (set `TMPDIR` on the same command, because shell state does not persist between Bash calls). It needs `perl` and `jq`. Each output line is `file:line:High:D:message` with a real file line number, and no output means the block is clean. Report its output as the Check D findings; do not re-implement its rules by hand.

```perl
#!/usr/bin/env perl
# Check D for one console or console-result block.
# usage: perl check_console.pl FILE OPEN CLOSE KIND     (KIND = console | console-result)
# prints: FILE:LINE:SEVERITY:CHECK:message   (nothing when the block is clean)
use strict; use warnings;
my ($file, $open, $close, $kind) = @ARGV;
open(my $fh, '<', $file) or die "cannot read $file: $!";
my @l = <$fh>; close $fh; chomp @l; s/\r$// for @l;
my @body = @l[$open .. $close - 2];      # file lines OPEN+1 .. CLOSE-1
my $first = $open + 1;
my $tmp = $ENV{TMPDIR} || '/tmp';

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
    $ln =~ s/\{\{\{?[^{}]*\}?\}\}/PLACEHOLDER/g;
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
    $t =~ s/:\s*\.\.\.[ \t]*\n(?=\s*")/: null,\n/g; $t =~ s/:\s*\.\.\.(?=\s*[,}\]]|\s*$)/: null/gm;
    $t =~ s/^\s*\.\.\.\s*,?\s*$//gm;
    $t =~ s/,(\s*\n\s*[}\]])/$1/g if $elided;          # comma left behind by a removed ellipsis line
    $r->{elided} = $elided;
    $s = strip_strings($t);
  }
  if ($s =~ /,\s*[}\]]/) { my $pre = substr($s, 0, $-[0]); my $nl = ($pre =~ tr/\n//); printf "%s:%d:High:D:trailing comma before a closing bracket (%s)\n", $file, $r->{start} + 1 + $nl, $ctx; next; }
  # NDJSON for _bulk (one JSON document per line), otherwise one JSON document
  my @docs;
  if ($r->{name} =~ m{(?:^|[ /])(?:_bulk|_msearch)(?:[?/]|$)}) { my $n = 0; for my $ln (split /\n/, $t, -1) { $n++; push @docs, [$n, $ln] if $ln =~ /\S/ } }
  else { @docs = ([1, $t]) }
  for my $d (@docs) {
    open(my $jq, '|-', "jq -e . >/dev/null 2>$tmp/jq.err") or die;
    print $jq $d->[1]; close $jq;
    if ($? != 0) {
      last if $r->{elided};                              # elided response: cannot be validated
      open(my $e, '<', "$tmp/jq.err"); my $msg = join(' ', map { chomp; $_ } <$e>); close $e;
      my ($jl) = $msg =~ /line (\d+)/; $jl ||= 1;
      printf "%s:%d:High:D:invalid JSON (%s): %s\n", $file, $r->{start} + $d->[0] + $jl - 1, $ctx, $msg;
      last;
    }
  }
}
```

What the script does:

- **Requests:** splits a `console` block into requests on method lines and validates each body separately. A `console-result` block is one body, and it is validated only when it starts with `{` or `[`. Text tables (`_cat` output) and partial fragments are not JSON, so they are skipped.
- **Pre-processing:** strips callout markers (`// <1>`, `# <1>`, a bare `<1>`, and several markers on one line), standalone comment lines, and trailing explanatory comments after code (Kibana Console accepts these, and Check C reports them). It replaces `{{var}}` / `{{{var}}}` with a placeholder and Painless `"""..."""` strings with a placeholder, keeping line numbers intact.
- **`...`:** a `...` outside a string in a `console` block is High, because customers copy-paste requests (replace it with realistic values). In a `console-result` block `...` is allowed, since authors trim long response examples, so it is never a finding there. The script normalizes it before parsing (`[...]`, `{...}`, `"key": ...`, prose placeholders like `[...list of hits...]`, standalone `...` lines). A `console-result` block that uses `...` and then fails to parse is skipped, because the response is intentionally incomplete.
- **Trailing commas:** a comma before `}` or `]` is High. It is reported, not silently fixed.
- **NDJSON:** for `_bulk` and `_msearch` each non-empty body line is validated as its own JSON document.
- **Line numbers:** `jq` reports lines relative to the body, and the script maps them back to file lines. For `Expected separator between values`, jq points at the next token, but the comma is missing at the end of the previous line, so put the `^` there. Use the line the script reports in the heading, and put the `^` under the end of the previous line in the context snippet.

Do NOT flag: Painless scripts, EQL/ES|QL string values, callout markers, template variables, text-table responses, or `...` inside a quoted string.

### Check E — Non-reserved domain names

Flag URLs or hostnames in code blocks that use invented placeholder domains with real TLDs (e.g., `mycompany.com`, `mycluster.io`). Scope is URLs and hostnames only: do not flag email addresses (for example `john@smith.com` in sample data).

Safe — do not flag: `example.com/net/org`, any subdomain thereof, `.example`/`.test`/`.localhost`/`.invalid` TLDs, `localhost`, loopback (`127.x.x.x`), RFC 5737 doc IPs (`192.0.2.x`, `198.51.100.x`, `203.0.113.x`), private ranges, and known legitimate domains: `elastic.co`, `amazonaws.com`, `azure.com`, `googleapis.com`, `docker.com`, `github.com`, `pypi.org`, `npmjs.com`, and similar well-known registries and cloud providers.

Suggestion: replace with `example.com` or a subdomain like `my-cluster.example.com`.

### Check F — API validation for `console` blocks

Collect all unique `METHOD /path` values across all files first. For each unique endpoint (skip any already validated earlier in this run), call `mcp__elastic-docs__search_docs` (`productFilter`: `elasticsearch`, `sectionFilter`: `api`) with the query described below to find the matching API reference page (URL starting with `/docs/api/doc/elasticsearch/operation/`). Fetch it with `mcp__elastic-docs__get_document_by_url` (`includeBody`: true).

A path with no leading slash (`POST _reindex`) is normalized the same way. Normalize each path before searching: keep the `_`-prefixed API segments and replace every other segment with a placeholder (`/my-index/_update/1` becomes `/{index}/_update/{id}`, `GET /my-index/_search` becomes `/{index}/_search`). Search on the API name rather than the full path, with the query `"<api-name> API request body"` (for example `"_update API request body"`). Accept the result whose URL starts with `/docs/api/doc/elasticsearch/operation/operation-` and whose path contains the same `_` API segment; the page may document a different HTTP method than the block uses (for example POST only for `_search`), which is not a finding. If the first search returns no such page, retry once with `"<api-name> API"` before concluding there is none. If every top-level key in the body is exempt (see below), still run the search so the endpoint is confirmed to exist, but skip fetching the page.

- **No matching page found (after the retry):** flag the endpoint as potentially removed or renamed.
- **Deprecated field:** if a top-level request body key appears alongside "deprecated" in the docs, flag it with the replacement.
- **Unrecognized field (advisory):** if a top-level key doesn't appear in the docs body at all, note it for verification.
- **No request-body listing:** if the fetched page body is prose only and lists no request fields, report "cannot verify request fields" once for that endpoint. Do not raise an unrecognized-field advisory for its keys.

Do NOT flag: `_`-prefixed metadata fields, nested object keys, standard Search DSL fields (`query`, `aggs`, `sort`, `size`, `from`, `highlight`, `knn`, `retriever`, `script`), and the standard create-index body fields `settings`, `mappings`, `aliases`.

Always include the API docs URL: in the issue detail when there is an issue, otherwise in the Notes section.

### Check G — ES|QL syntax validation

**G-1 — Source command:** the first non-blank, non-comment line must be `FROM`, `PROMQL`, `ROW`, `SHOW INFO`, or `TS`. Flag blocks that start with a processing command (missing source), or with `SELECT` (SQL syntax).

**G-2 — Pipe command names:** every line beginning with `|` must use a recognized command: `CHANGE_POINT`, `COMPLETION`, `DEDUP`, `DISSECT`, `DROP`, `ENRICH`, `EVAL`, `FORK`, `FUSE`, `GROK`, `HIGHLIGHT`, `INLINE STATS`, `IP_LOCATION`, `KEEP`, `LIMIT`, `LOOKUP JOIN`, `METRICS_INFO`, `MMR`, `MV_EXPAND`, `REGISTERED_DOMAIN`, `RENAME`, `RERANK`, `SAMPLE`, `SORT`, `STATS`, `TS_COLLAPSE`, `TS_INFO`, `URI_PARTS`, `USER_AGENT`, `WHERE`. Flag unrecognized names.

**G-2a — Incomplete pipe commands:** recognizing the command name is not enough — flag any pipe command that is present but has no arguments following it on the same line. Required arguments:

| Command | Requires |
|---------|---------|
| `KEEP`, `DROP` | at least one field name |
| `WHERE` | a condition expression |
| `SORT` | at least one field |
| `EVAL`, `STATS` | at least one expression |
| `RENAME` | at least one `old AS new` pair |
| `DISSECT`, `GROK` | an input field and a pattern |
| `ENRICH` | a policy name |
| `LOOKUP JOIN` | a lookup index name and `ON <field>` |

**G-3 — SQL-isms:** flag `SELECT` at line start, `GROUP BY`, raw `JOIN` (without `LOOKUP`), and `ORDER BY` — all SQL syntax invalid in ES|QL.

**G-4 — Do not flag:** `//` comment lines, `WHERE` after a pipe, `FROM` inside a string, blocks with only comments or blank lines.

### Check H — Painless script validation

Painless appears in two places: standalone `` ```painless `` blocks, and triple-quoted `"""..."""` strings inside `console` blocks. Extract inline Painless from `console` blocks using a multiline perl match (via Bash) before Check D replaces them with placeholders.

Run these checks on each Painless source:

**H-1 — Balanced delimiters:** count `{}`  `[]` `()` pairs. Flag any imbalance. Do not count delimiters inside string literals.

**H-2 — Deprecated `.getValue()` API:** `.getValue()` on `doc` fields is deprecated — flag any usage and suggest `.value` instead (e.g., `doc['field'].value`).

**H-3 — Unavailable APIs:** flag use of `System.out`, `System.err`, `System.exit`, `Thread.sleep`, `Runtime.getRuntime`, or `ProcessBuilder` — none are available in the Painless sandbox. Suggest using the Painless execute API (`POST /_scripts/painless/_execute`) for debugging instead.

**H-4 — Do not flag:** `//` comment lines, delimiters inside quoted strings, single-expression scripts with no delimiters, empty or comment-only blocks.

---

## Severity

Assign each finding one of these default severities, and include it in the issue details.

| Severity | Findings |
|----------|----------|
| High | D `...` in a `console` block; D invalid JSON or trailing comma; G-1 SQL syntax used for ES\|QL |
| Medium | S unclosed fence; A-2 wrong identifier (including the likely-mistakes table); B-1 missing `subs=true` (Low when it is an unverified advisory because no `docset.yml` was found); F removed or deprecated API or field; G-1 missing source command, G-2, G-2a, G-3; H-1, H-3 |
| Low | A-1 empty info string; B-2 unused `subs=true`; C inline comment; E domain; F unrecognized-field advisory; H-2 |

---

## Step 4: Generate the report

Output three sections (Summary tables, Issue details, Notes). Omit any table where no files have issues.

**Section 1 — Summary tables:**

```
## Code Sample Validation Report

**Target:** <path>
**Files checked:** N
**Issues found:** N

### Summary

#### All blocks (Checks A, B, C, E, S)
| File | Missing/wrong lang | subs=true | Callout | Domain | Unclosed fence | Total |
|------|--------------------|-----------|---------|--------|----------------|-------|

#### Console / console-result blocks (Checks D, F)
| File | Ellipsis | JSON errors | API Validation | Total |
|------|----------|-------------|----------------|-------|

#### ES|QL blocks (Check G)
| File | Source cmd | Pipe cmd | SQL-ism | Total |
|------|------------|----------|---------|-------|

#### Painless blocks (Check H)
| File | Unbalanced delimiters | Deprecated API | Unavailable API | Total |
|------|-----------------------|----------------|-----------------|-------|
```

**Section 2 — Issue details**, one subsection per file:

````
#### `path/to/file.md` — Line N — Check X — Severity — Short title

> **Issue:** description
> **Suggestion:** fix

```
  context lines around the error
      ^
```
````

For JSON errors include the `jq` error message and up to 2 lines of context around the offending line with a `^` pointer. For Painless inline scripts, note whether the issue is from a standalone block or an embedded triple-quoted string.

**Section 3 — Notes** (informational; not counted as issues). Always print it, including when there are no issues. List, one bullet each:

- Checks that were skipped or limited, printed once per run, for example "Check B-1 ran as an unverified advisory: no `docset.yml` found".
- Each endpoint Check F looked up, with its API docs URL, or "not field-checked (all keys exempt)" when the fetch was skipped.
- Each endpoint whose API page lists no request-body fields ("cannot verify request fields").

If no issues are found: print "No issues found across all checked files." in place of Section 2, then Section 3.

**Output mode:** print to console unless `--output <path>` was given, in which case write the report as a markdown file and confirm the path.

---

## Guidelines

- Report the line number of the opening fence for block-level findings. For Check D use the file line the script reports, which is the line to fix.
- Do not flag false positives — skip ambiguous inline comments, and apply H-1 only when imbalance is unambiguous.
- Skip non-markdown files silently. Note unreadable files and continue.
