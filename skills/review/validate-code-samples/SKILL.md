---
name: validate-code-samples
version: 1.0.0
description: Validate code samples in Elastic documentation markdown files. Checks for missing language identifiers, missing subs=true when using {{variables}}, inline comments that should be callouts, and invalid JSON in console blocks. Use when reviewing documentation PRs, auditing a section of docs, or writing new content with code examples. Trigger with /validate-code-samples.
disable-model-invocation: true
argument-hint: <file|dir|glob> [--output <path>]
allowed-tools: Read, Glob, Grep, Write, Bash(find *), Bash(python3 *), CallMcpTool
sources:
  - https://docs-v3-preview.elastic.dev/elastic/docs-builder/tree/main/syntax/code
  - https://docs-v3-preview.elastic.dev/elastic/docs-builder/tree/main/syntax/substitutions
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

You are a code sample validator for Elastic documentation. Your job is to check every code block in one or more markdown files against the docs-builder style rules and report all violations.

**Never modify documentation source files. Only analyze and report.**

---

## Step 1: Resolve files

Parse `$ARGUMENTS` to get the target and optional `--output` flag:

- `--output <path>`: if present, write the report to this path instead of printing to console. Strip this flag and its value from the target before continuing.

Resolve the target:

- **Single `.md` file** — analyze that file only.
- **Directory** — find all `.md` files recursively:
  ```bash
  find <dir> -name "*.md" -type f | sort
  ```
- **Glob** — expand the glob using:
  ```bash
  python3 -c "import glob, sys; print('\n'.join(sorted(glob.glob(sys.argv[1], recursive=True))))" "<glob>"
  ```
- **No argument** — ask the user: "Please provide a file path, directory, or glob pattern."

---

## Step 2: Extract code blocks from each file

For each file, read its full content and extract every fenced code block. A fenced code block starts and ends with three or more backticks (`` ``` ``).

**Skip code blocks inside HTML comments.** Before extracting blocks, strip all HTML comments (`<!-- ... -->`, including multi-line) from the file content. Code blocks inside comments are not rendered and should not be validated.

For each block, capture:
- **Line number** of the opening fence
- **Fence info string** — everything after the opening backticks on the first line (e.g., `bash subs=true`, `console`, or empty)
- **Language identifier** — the first word of the fence info string, if present
- **Attributes** — remaining words/tokens after the language identifier (e.g., `subs=true`, `callouts=false`)
- **Body** — the lines between the opening and closing fences

---

## Step 3: Run checks

Run all checks (A through F) against every extracted code block.

### Check A: Missing language identifier

Every code block must have a language identifier.

**Flag** any block where the fence info string is empty (opening fence is just ` ``` ` with nothing after it).

Common valid identifiers include: `bash`, `sh`, `shell`, `console`, `console-result`, `json`, `yaml`, `python`, `javascript`, `js`, `typescript`, `ts`, `java`, `go`, `ruby`, `php`, `csharp`, `c`, `cpp`, `xml`, `sql`, `http`, `txt`, `text`, `eql`, `esql`, `painless`, `kibana`, `logstash`, `markdown`, `diff`, `toml`, `ini`.

Note: `console` is for API request blocks (copyable by customers). `console-result` is for API response blocks (display only).

**Suggested fix:** Infer a specific language identifier from the block content using these heuristics (in order):

| Signal | Suggested identifier |
|--------|---------------------|
| First non-blank line matches `GET\|POST\|PUT\|DELETE\|PATCH\|HEAD <path>` | `console` |
| Content is valid JSON (starts with `{` or `[`) | `json` |
| Contains `apiVersion:` or `kind:` or predominant `key: value` lines | `yaml` |
| Contains `#!/bin/bash`, `#!/usr/bin/env`, or `curl `, `apt-get`, `brew ` | `bash` |
| Contains `import `, `def `, `print(`, `if __name__` | `python` |
| Contains `public class`, `void main`, `System.out` | `java` |
| Contains `const `, `let `, `function `, `=>`, `require(` | `javascript` |
| Contains `SELECT`, `FROM`, `WHERE`, `INSERT INTO` (SQL keywords) | `sql` |
| Contains `<` tags and `>` (XML/HTML structure) | `xml` |
| Plain prose or output with no code structure | `txt` |

Always state the recommended identifier explicitly in the suggestion: e.g., `**Suggestion:** Add ` ```json ` to this block.`

---

### Check B: Variable substitution missing `subs=true`

If a code block body contains `{{...}}` patterns that match **defined substitution variables**, the fence info must include `subs=true`.

Before running this check, look for a `docset.yml` file in the repo root (walk up from the target file's directory until found). Parse the `subs:` section to get the list of valid variable names:

```yaml
subs:
  es: "Elasticsearch"
  kib: "Kibana"
  version: "9.0"
```

**Flag** any block that contains `{{var}}` where `var` is a key in the `subs:` section, and the fence info does not include `subs=true`.

**Do NOT flag** `{{...}}` patterns where the content inside is not a defined variable name — these are literal curly braces in the content (e.g., log output, regex patterns, template syntax from other systems) and are not docs-builder substitutions.

If no `docset.yml` is found, fall back to flagging any `{{word}}` pattern (single identifier, no spaces) as a potential substitution variable.

```
# Bad
```bash
wget https://artifacts.elastic.co/downloads/elasticsearch-{{version}}.tar.gz
```

# Good
```bash subs=true
wget https://artifacts.elastic.co/downloads/elasticsearch-{{version}}.tar.gz
```
```

**Suggested fix:** Add `subs=true` to the opening fence: ` ```bash subs=true `.

Also flag the inverse: a block with `subs=true` but no `{{...}}` patterns in its body — the attribute is unnecessary.

---

### Check C: Inline comments that should be callouts

For code blocks with language identifiers in `[bash, sh, shell, console, yaml, python, javascript, js, typescript, ts, java, go, ruby]`:

Flag lines where a comment character (`#` or `//`) appears **after code on the same line** and the comment text reads as an explanation or annotation rather than functional code.

**Exemptions — do NOT flag:**
- Shebang lines: `#!/bin/bash`, `#!/usr/bin/env python3`
- Standalone comment lines (the entire line is a comment, not mixed with code): `# Install dependencies`
- `#` inside strings or regex
- Lines using explicit callout markers: `command  <1>` (already using callouts)

**Examples:**

```
# Bad — inline annotation that should be a callout
apt-get install -y elasticsearch  # installs the package
curl -X GET "localhost:9200"  # check cluster health

# Good — use explicit callout markers instead
apt-get install -y elasticsearch  <1>
curl -X GET "localhost:9200"  <2>

1. Installs the package.
2. Checks cluster health.
```

**Suggested fix:** Replace the inline comment with an explicit callout marker (`<N>`) and add a numbered callout list after the code block.

Use judgment here — brief functional comments (`# TODO`, `# noqa`) are acceptable. Flag comments that are clearly intended as reader-facing explanations.

---

### Check D: JSON validation in `console` and `console-result` blocks

#### `console` vs `console-result`

- **`console`** — API request blocks. Customers copy-paste these. Must be complete and valid.
- **`console-result`** — API response blocks. Display only; may be intentionally truncated.

`console` blocks contain Elasticsearch API calls in this structure:

```
METHOD /path
{
  "json": "body"
}

METHOD /another-path
{ ... }
```

The first non-blank line of each API call is the HTTP method + path (not JSON). Everything after it until the next method line is the JSON body. Note:
- Paths may or may not include a leading slash (e.g., both `GET /index/_search` and `GET index/_search` are valid).
- Standalone `#` or `//` comment lines between calls are not JSON — skip them when building the JSON body.

#### Flag: `...` in `console` request blocks

`...` is used to indicate omitted JSON content for brevity. This is **never acceptable in `console` blocks** because customers should be able to copy-paste the example directly.

**Flag** any `console` block body containing a bare `...` (as a standalone line, inline `{...}`, or `[...]`).

**Suggested fix:** Replace `...` with a realistic, complete example value.

`...` in `console-result` blocks is acceptable — do not flag it, but still validate the JSON after stripping it (see pre-processing below).

#### Pre-processing before JSON parsing

Apply to **both** `console` and `console-result` block bodies:

1. **Strip callout markers**: remove trailing `<N>` markers from line ends, including any `//` or `#` comment character that precedes them (used in docs-builder to attach callouts to JSON lines).
   Pattern: `\s*(?://|#)?\s*<\d+>\s*$` → remove from each line.

2. **Replace template variables**: handle both double-brace `{{var}}` and triple-brace `{{{var}}}` (Mustache) syntax.
   - First replace `"{{var}}"` and `"{{{var}}}"` (already inside a JSON string) → `"__PLACEHOLDER__"` to avoid double-quoting.
   - Then replace any remaining bare `{{var}}` or `{{{var}}}` → `"__PLACEHOLDER__"`.

3. **Strip standalone comment lines from console bodies**: `#` or `//` lines that appear between API calls (not inside a JSON body) should be skipped when extracting JSON. A line that starts with `#` or `//` after stripping whitespace is not JSON — skip it when building the JSON body for each call.

4. **Replace triple-quoted Painless strings**: Painless scripts embedded in `"script"` fields use `"""..."""` triple-quote syntax which is not valid JSON. Replace any triple-quoted string with a plain JSON string placeholder before parsing.
   Pattern: `"""[\s\S]*?"""` → `"__PAINLESS__"`

5. **Normalize `...` ellipsis** (`console-result` only — for `console` blocks, `...` is flagged above but still normalized here so JSON parsing can continue):
   - `[...]` → `[]`
   - `{...}` → `{}`
   - Value-position ellipsis: `"key": ...` → `"key": null` (pattern: `re.sub(r':\s*\.\.\.', ': null', body)`) — handles truncated values like `"_shards": ...` common in Elasticsearch response examples.
   - Mixed arrays/objects with trailing ellipsis: `[val1, val2, ...]` → `[val1, val2]` (remove `, ...` before closing bracket)
   - A line consisting only of `...` → remove the line and any trailing comma on the preceding non-blank line.

6. **Detect trailing commas**: flag (do not silently fix) trailing commas before `}` or `]`.
   Pattern: `,\s*[}\]]`

#### NDJSON (`_bulk`) handling

`_bulk` endpoints use NDJSON (newline-delimited JSON) — each line is a separate JSON object, not a single document. Detect this by checking if the HTTP method line contains `_bulk`.

For `_bulk` bodies, validate **each non-empty line** as an individual JSON object rather than parsing the whole body at once. A line that fails `json.loads()` is a real error; multiple valid lines is not.

```bash
python3 << 'EOF'
import re, json, sys

method_line = sys.argv[1] if len(sys.argv) > 1 else ""
is_bulk = "_bulk" in method_line
is_result = sys.argv[2] == "result" if len(sys.argv) > 2 else False
body = sys.stdin.read()

# Strip callout markers (including preceding // or # comment chars used in JSON callouts)
body = re.sub(r'\s*(?://|#)?\s*<\d+>\s*$', '', body, flags=re.MULTILINE)

# Replace template variables — handle triple-brace {{{var}}} and double-brace {{var}},
# replacing quoted variants first to avoid producing invalid ""__PLACEHOLDER__""
body = re.sub(r'"\{\{\{[^}]+\}\}\}"', '"__PLACEHOLDER__"', body)
body = re.sub(r'"\{\{[^}]+\}\}"', '"__PLACEHOLDER__"', body)
body = re.sub(r'\{\{\{[^}]+\}\}\}', '"__PLACEHOLDER__"', body)
body = re.sub(r'\{\{[^}]+\}\}', '"__PLACEHOLDER__"', body)

# Replace triple-quoted Painless strings
body = re.sub(r'"""[\s\S]*?"""', '"__PAINLESS__"', body)

# Normalize ellipsis
body = re.sub(r'\[\.\.\.\]', '[]', body)
body = re.sub(r'\{\.\.\.\}', '{}', body)
body = re.sub(r':\s*\.\.\.', ': null', body)          # "key": ... → "key": null
body = re.sub(r',\s*\.\.\.\s*([}\]])', r'\1', body)   # [val1, val2, ...] → [val1, val2]
body = re.sub(r',(\s*\n(?:\s*\n)*)\s*\.\.\.\s*\n', r'\1', body)
body = re.sub(r'^\s*\.\.\.\s*,?\n?', '', body, flags=re.MULTILINE)

body = body.strip()
if not body:
    sys.exit(0)

# Check for trailing commas
if re.search(r',[ \t]*[}\]]', body):
    print("TRAILING_COMMA")

if is_bulk:
    # Validate each line independently
    for i, line in enumerate(body.splitlines(), 1):
        line = line.strip()
        if not line:
            continue
        try:
            json.loads(line)
        except json.JSONDecodeError as e:
            print(f"JSONDecodeError line {i}: {e}")
            sys.exit(1)
else:
    try:
        json.loads(body)
    except json.JSONDecodeError as e:
        lines = body.splitlines()
        start = max(0, e.lineno - 3)
        context = lines[start:e.lineno]
        pointer = ' ' * (e.colno - 1) + '^'
        print(f"JSONDecodeError: {e}")
        print('\n'.join(context))
        print(pointer)
        sys.exit(1)
EOF
```

**Suggested fix for trailing commas:** Remove the trailing comma before `}` or `]` on the flagged line.

#### Do NOT flag these as errors

- **Painless scripts**: triple-quoted `"""..."""` replaced before parsing. **EQL / ES|QL**: appear as string values — valid JSON. **`_bulk` bodies**: validated line-by-line. **Callout markers** and **template variables** already stripped in pre-processing.

---

### Check E: Non-reserved domain names in examples

Per Elastic's documentation policy (based on RFC 2606 and RFC 6761), all placeholder domain names in examples MUST use IETF-reserved domains. Using real-looking but unregistered domains risks pointing readers to live third-party sites.

#### Reserved/safe domains — do NOT flag

**RFC 2606 / RFC 6761 reserved (always safe):**
- `example.com`, `example.net`, `example.org`, `example.edu`
- Any subdomain of the above: `api.example.com`, `db.example.com`
- Any name under `.example`, `.invalid`, `.localhost`, `.test` TLDs
- `localhost` and loopback addresses (`127.0.0.1`, `127.x.x.x`)
- RFC 5737 documentation IP ranges: `192.0.2.x`, `198.51.100.x`, `203.0.113.x`
- Private IP ranges: `10.x.x.x`, `172.16–31.x.x`, `192.168.x.x`
- IPv6 documentation range: `2001:db8::/32`

**Real, legitimate domains — do NOT flag:**

These are known real domains used for genuine references (downloads, registries, services):

| Category | Domains |
|----------|---------|
| Elastic | `elastic.co` |
| Cloud providers | `amazonaws.com`, `aws.amazon.com`, `azure.com`, `microsoft.com`, `googlecloud.com`, `googleapis.com` |
| Container/registry | `docker.com`, `hub.docker.com`, `ghcr.io`, `quay.io`, `registry.k8s.io` |
| Package managers | `pypi.org`, `npmjs.com`, `maven.apache.org`, `repo1.maven.org`, `mvnrepository.com`, `nuget.org`, `rubygems.org`, `pkg.go.dev` |
| Source control | `github.com` |
| OS/package repos | `debian.org`, `ubuntu.com`, `centos.org`, `fedoraproject.org`, `rpm.releases.hashicorp.com`, `apt.releases.hashicorp.com` |
| Other known software | `openjdk.org`, `brew.sh`, `chocolatey.org` |

**Also acceptable:**
- Placeholder strings that are clearly not domains: `<your-domain>`, `YOUR_DOMAIN`, `my-cluster-name` (no TLD)
- Elasticsearch node addresses with no TLD: `node1`, `es-node-1`

#### Flag — potentially unregistered domain names

Flag URLs or hostnames in code blocks where the domain:
- Has a real TLD (`.com`, `.net`, `.org`, `.io`, `.co`, `.dev`, `.app`, etc.)
- Is NOT in the reserved or known-legitimate lists above
- Looks like a placeholder someone invented (e.g., `mycompany.com`, `mycluster.io`, `test-server.net`, `myapp.example` is fine but `myapp.com` is not)

Common patterns to scan for:
- Full URLs: `https?://[^\s"']+`
- Hostnames in strings: `"[a-z0-9.-]+\.[a-z]{2,}"`
- Config values: `host: some.domain.com`, `DB_HOST=some.domain.com`

**Suggested fix:** Replace the domain with `example.com` or an appropriate subdomain (e.g., `my-cluster.example.com`, `api.example.com`).

**Do NOT flag** strings that contain a TLD as part of a file path, variable name, or non-URL context (e.g., `myfile.json`, `config.yaml`, `.env`).

### Check F: API Validation

For each `console` block, use the `elastic-docs` MCP server to:
1. Verify the API endpoint exists in current Elastic documentation
2. Flag any request body fields that the API docs explicitly mark as **deprecated**

> **Note:** The Elastic Docs MCP returns prose documentation, not structured schemas. Do not attempt to validate every field name against the API docs — only flag fields explicitly described as deprecated. The primary value of this check is confirming the endpoint is current and surfacing known-deprecated usage.

##### Step F-1: Extract API calls

From each `console` block, collect every `METHOD /path` line. Deduplicate the same method+path across a file — look it up once.

##### Step F-2: Look up the API reference page

Use **`SemanticSearch`** with a targeted query: `"request body fields <endpoint> elasticsearch API"` (e.g., `"request body fields reindex elasticsearch API"`), with `product: "elasticsearch"`.

Pick the top result whose URL starts with `/docs/api/doc/elasticsearch/operation/`. Then call **`GetDocumentByUrl`** with `includeBody: true` on the matched URL to get the full parameter list, including any deprecation notices.

If no matching result is found, note "API docs not found for `<METHOD> <path>`" and skip this call.

##### Step F-3: Verify the endpoint exists

If `SemanticSearch` returns no result matching the method+path, or the top result's description doesn't match the expected operation, flag:

```
> **Issue:** `DELETE /_search/scroll` — no matching API reference page found. This endpoint may have been removed or renamed.
> **Suggestion:** Check the current Elasticsearch API docs to confirm the correct endpoint.
```

##### Step F-4: Flag unrecognized or deprecated fields

For each top-level JSON key in the code block's request body, check the full page body text returned by `GetDocumentByUrl`:

**Unrecognized field** (advisory) — if the field name does not appear anywhere in the docs body (look for it in backtick or bold formatting, e.g., `` `field_name` `` or `**field_name**`), flag it as an advisory finding. API docs pages may not enumerate every valid field, so treat these as hints to verify rather than definitive errors:

```
> **Note:** `POST _reindex` — field `"foo"` was not found in the API reference. Verify it is a valid request body field.
> **API docs:** https://www.elastic.co/docs/api/doc/elasticsearch/operation/operation-reindex
> **Suggestion:** Confirm this field is valid, or replace with a documented field.
```

**Deprecated field** — if the field name appears alongside the word `deprecated` (e.g., `` `field_name` — deprecated ``, `Deprecated in X.Y`), flag it:

```
> **Issue:** `POST _reindex` — field `"size"` is deprecated. Use `"max_docs"` instead.
> **API docs:** https://www.elastic.co/docs/api/doc/elasticsearch/operation/operation-reindex
> **Suggestion:** Replace `"size"` with `"max_docs"`.
```

**Do NOT flag:**
- Fields prefixed with `_` (internal ES metadata: `_source`, `_index`, `_id`)
- Fields inside nested objects — only check top-level keys
- Standard Search DSL fields (`query`, `aggs`, `sort`, `size`, `from`, `highlight`, `suggest`, `knn`, `retriever`, `fields`, `script`) or short common words (`type`, `index`, `id`) — documented separately or risk false positives

##### Step F-5: Report findings

Include API Validation issues in the summary table under the **API Validation** column. Always include the API docs URL in the issue detail so authors can verify the finding.

---

## Step 4: Generate the report

### Format

Always output in two sections:

**Section 1 — Overview table** (only files with at least one issue; clean files are omitted):

**Section 2 — Issue details** (one subsection per file that has issues).

Full example:

```
## Code Sample Validation Report

**Target:** docs/reference/
**Files checked:** 4
**Issues found:** 3

### Summary

| File | Missing lang | subs=true | Callout | Ellipsis | JSON errors | Domain | API Validation | Total |
|------|-------------|-----------|---------|----------|-------------|--------|----------------|-------|
| `mapping-reference/bbq.md` | 0 | 0 | 0 | 0 | 1 | 0 | 0 | 1 |
| `mapping-reference/dense-vector.md` | 1 | 0 | 0 | 0 | 0 | 0 | 0 | 1 |

---

### Issues

#### `mapping-reference/bbq.md` — Line 254 — Check D — Invalid JSON

> **Issue:** `PUT bbq_disk-index/_mapping` — Expecting ',' delimiter: line 9 column 9 (char 168)
> **Suggestion:** Fix the JSON syntax error.

\```
  "index_options": {
    "type": "bbq_disk"
    "bits": 2
        ^
\```

---

#### `mapping-reference/dense-vector.md` — Line 622 — Check A — Missing Language Identifier

> **Issue:** Code block has no language identifier.
> **Suggestion:** Add an appropriate language identifier based on the content (e.g., `txt`).

\```
1000000100000000000000010010101001111111
^
0111111110000001000000000000000100101010
\```

---
```

If no files have any issues, replace Section 2 with:

```
### Issues

No issues found across all checked files.
```

### Output mode

- **No `--output` flag**: print the full report to the console.
- **`--output <path>`**: write the report as a markdown file to the specified path and tell the user where it was written.

---

## Guidelines

- Report the **line number** of the opening fence for every flagged block.
- Be precise about **which line** within a block has an issue (e.g., for inline comments, give the line number within the file).
- For JSON errors, include the specific `JSONDecodeError` message and show context around the error: up to 2 lines before the error line, the error line itself, and the `^` pointer caret line. This gives authors enough context to find the problem without showing the entire block.
- Do not flag false positives — when in doubt about an inline comment being functional vs. explanatory, skip it.
- Skip non-markdown files silently.
- If a file cannot be read, note it as unreadable and continue.
