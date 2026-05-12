---
name: docs-validate-code-samples
version: 1.0.0
description: Validate code samples in Elastic documentation markdown files. Checks language identifiers, substitution attributes, callout usage, JSON validity, ES|QL syntax, and Painless scripts. Use when reviewing docs PRs, auditing content, or writing new examples.
disable-model-invocation: true
argument-hint: <file|dir|glob> [--output <path>]
allowed-tools: Read, Glob, Grep, Write, Bash, mcp__elastic-docs__search_docs, mcp__elastic-docs__get_document_by_url
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

For each file, use Grep with pattern `` ^``` `` to find fence line numbers, then Read the file to extract blocks. Also search for indented fences (`` ^\s+``` ``) to catch blocks inside list items.

- **Skip blocks inside HTML comments** (`<!-- ... -->`).
- **Skip MyST directive blocks** where the info string starts and ends with `{}` (e.g., `` ```{note} ``).

For each block capture: opening line number, fence info string, language identifier (first word), attributes (remaining tokens), and body.

---

## Step 3: Run checks A through H

### Check A — Missing or wrong language identifier

Flag any block with an empty fence info string. Also flag blocks where the language identifier is clearly wrong for the content (e.g., `js` used for a JSON-only response, `console` used for response-only data with no HTTP method line).

Common valid identifiers: `bash`, `sh`, `console`, `console-result`, `json`, `yaml`, `python`, `javascript`, `js`, `typescript`, `java`, `go`, `ruby`, `sql`, `esql`, `eql`, `painless`, `kql`, `kuery`, `txt`, `text`, `xml`, `toml`, `ini`, `diff`.

Infer the correct identifier from content: HTTP method line → `console`; starts with `{`/`[` → `json`; `key: value` lines → `yaml`; `curl`/`apt-get` → `bash`; `import`/`def`/`print(` → `python`; `public class` → `java`; `const`/`let`/`=>` → `javascript`.

### Check B — Variable substitution missing `subs=true`

Walk up from the target file to find `docset.yml` and parse its `subs:` section for valid variable names. Stop at the git root (presence of `.git/`) or after 6 directory levels, whichever comes first. Flag any block containing `{{var}}` where `var` is a defined substitution key but the fence info lacks `subs=true`. Also flag the inverse: `subs=true` on a block with no `{{...}}` patterns.

If no `docset.yml` is found, flag any `{{word}}` pattern (single identifier) as a potential substitution variable.

### Check C — Inline comments that should be callouts

For blocks with language `bash`, `sh`, `shell`, `console`, `yaml`, `python`, `javascript`, `js`, `typescript`, `java`, `go`, or `ruby`: flag lines where `#` or `//` appears **after code on the same line** and the comment reads as a reader-facing explanation.

Exemptions: shebang lines, standalone comment lines (no code on the same line), `#` inside strings, lines already using callout markers (`<1>`).

Suggestion: replace with explicit callout markers (`<N>`) and a numbered list after the block.

### Check D — JSON validation in `console` and `console-result` blocks

`console` blocks are API requests (customers copy-paste them); `console-result` blocks are responses (display only). Each `console` block contains one or more API calls: an HTTP method+path line, followed by an optional JSON body, repeated for multiple calls.

**Flag `...` in `console` blocks** — never acceptable; replace with realistic values. `...` in `console-result` is fine.

**Pre-process both block types before JSON parsing:**
1. Strip callout markers (`<N>`) and their preceding `//`/`#` from line ends.
2. Replace `{{var}}` / `{{{var}}}` template variables with a placeholder string.
3. Skip standalone `#` or `//` comment lines when building the JSON body.
4. Replace triple-quoted Painless strings (`"""..."""`) with a placeholder using a multiline perl substitution.
5. For `console-result` only: normalize `...` ellipsis — replace `[...]` with `[]`, `{...}` with `{}`, `: ...` with `: null`, strip standalone `...` lines.
6. Detect and flag trailing commas before `}` or `]` (do not silently fix).

**NDJSON (`_bulk`):** if the method line contains `_bulk`, validate each non-empty line as a separate JSON object. Otherwise validate the full body with `jq`.

**Do NOT flag:** Painless scripts (replaced before parsing), EQL/ES|QL string values, callout markers and template variables (already stripped).

### Check E — Non-reserved domain names

Flag URLs or hostnames in code blocks that use invented placeholder domains with real TLDs (e.g., `mycompany.com`, `mycluster.io`).

Safe — do not flag: `example.com/net/org`, any subdomain thereof, `.example`/`.test`/`.localhost`/`.invalid` TLDs, `localhost`, loopback (`127.x.x.x`), RFC 5737 doc IPs (`192.0.2.x`, `198.51.100.x`, `203.0.113.x`), private ranges, and known legitimate domains: `elastic.co`, `amazonaws.com`, `azure.com`, `googleapis.com`, `docker.com`, `github.com`, `pypi.org`, `npmjs.com`, and similar well-known registries and cloud providers.

Suggestion: replace with `example.com` or a subdomain like `my-cluster.example.com`.

### Check F — API validation for `console` blocks

Collect all unique `METHOD /path` values across all files first. For each unique endpoint (skip any already validated earlier in this run), call `mcp__elastic-docs__search_docs` with query `"request body fields <endpoint> elasticsearch API"` (product: `elasticsearch`, section: `api`) to find the matching API reference page (URL starting with `/docs/api/doc/elasticsearch/operation/`). Fetch it with `mcp__elastic-docs__get_document_by_url` (include_body: true).

- **No matching page found:** flag the endpoint as potentially removed or renamed.
- **Deprecated field:** if a top-level request body key appears alongside "deprecated" in the docs, flag it with the replacement.
- **Unrecognized field (advisory):** if a top-level key doesn't appear in the docs body at all, note it for verification.

Do NOT flag: `_`-prefixed metadata fields, nested object keys, standard Search DSL fields (`query`, `aggs`, `sort`, `size`, `from`, `highlight`, `knn`, `retriever`, `script`).

Always include the API docs URL in the issue detail.

### Check G — ES|QL syntax validation

**G-1 — Source command:** the first non-blank, non-comment line must be `FROM`, `ROW`, `SHOW INFO`, or `METRICS`. Flag blocks that start with a processing command (missing source), or with `SELECT` (SQL syntax).

**G-2 — Pipe command names:** every line beginning with `|` must use a recognized command: `DISSECT`, `DROP`, `ENRICH`, `EVAL`, `GROK`, `KEEP`, `LIMIT`, `MV_EXPAND`, `RENAME`, `SORT`, `STATS`, `WHERE`, `LOOKUP`, `INLINESTATS`, `CHANGE_POINT`, `MATCH`, `QSTR`, `RERANK`. Flag unrecognized names.

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

## Step 4: Generate the report

Output two sections. Omit any table where no files have issues.

**Section 1 — Summary tables:**

```
## Code Sample Validation Report

**Target:** <path>
**Files checked:** N
**Issues found:** N

### Summary

#### All blocks (Checks A, B, C, E)
| File | Missing/wrong lang | subs=true | Callout | Domain | Total |
|------|--------------------|-----------|---------|--------|-------|

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
#### `path/to/file.md` — Line N — Check X — Short title

> **Issue:** description
> **Suggestion:** fix

```
  context lines around the error
      ^
```
````

For JSON errors include the `jq` error message and up to 2 lines of context around the offending line with a `^` pointer. For Painless inline scripts, note whether the issue is from a standalone block or an embedded triple-quoted string.

If no issues are found: print "No issues found across all checked files." in place of Section 2.

**Output mode:** print to console unless `--output <path>` was given, in which case write the report as a markdown file and confirm the path.

---

## Guidelines

- Report the line number of the opening fence for every flagged block.
- Do not flag false positives — skip ambiguous inline comments, and apply H-1 only when imbalance is unambiguous.
- Skip non-markdown files silently. Note unreadable files and continue.
