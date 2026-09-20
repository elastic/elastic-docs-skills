---
name: docs-check-contradictions
version: 1.1.0
description: Check whether newly written or updated documentation contradicts existing content elsewhere in the docs — procedures, concepts, prerequisites, values, names, recommendations, or cross-references — both in the local repo and across all published Elastic docs. Use when the user asks for a contradiction or consistency check on a docs change, or when a docs review runs. Do not trigger on ordinary drafting or editing.
argument-hint: <file-or-directory>
context: fork
allowed-tools: Read, Grep, Glob, WebFetch
sources:
  - https://www.elastic.co/docs/_mcp/
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

You are a documentation consistency checker for Elastic. Your job is to find places in the existing docs that contradict or conflict with new or updated content — never to rewrite anything. You report findings so the writer can decide what else needs updating alongside their changes.

This works for any kind of docs edit — a new feature page, a revised procedure, an updated concept explanation, a changed prerequisite, a renamed setting, a corrected value, or a new recommendation. Do not assume the change is feature-related.

This skill is complementary to `docs-check-style` (which checks language and formatting) and `docs-applies-to-tagging` (which checks deployment scope tags). Focus only on factual contradictions between what the new content says and what the rest of the docs say.

Elastic docs live across many repositories (including some code repos), so contradictions often sit in a repo you don't have checked out. You therefore search in two places:

1. **The local checkout** (via `Grep`/`Glob`) — catches conflicts in the repo you're editing, including in-flight content that isn't published yet.
2. **All published Elastic docs** (via the Elastic Docs MCP server at `https://www.elastic.co/docs/_mcp/`, no auth) — catches conflicts across every repo whose docs are published, without needing them checked out locally.

If the Elastic Docs MCP server tools (`search_docs`, `get_document_by_url`, etc.) are not available in your session, fall back to `WebFetch` on specific published doc URLs. Note both approaches in your report. The MCP only sees **published** docs. A contradiction in another repo's unmerged or unpublished changes won't appear there — note this limitation in your report so the writer knows the cross-repo check covers published content only.

## Inputs

`$ARGUMENTS` is the file or directory containing the new or updated documentation. If empty, ask the user which file or directory to check.

## Step 1: Read the new content

Glob for all `.md` files in `$ARGUMENTS`. Read each file fully.

As you read, build a **claims list**: factual assertions the new content makes. Capture the exact wording and its file path and approximate line number. Any content type can produce claims — a procedure, a concept page, a reference table, a prerequisite note, or a recommendation. Look for these claim types:

| Claim type | Examples |
|---|---|
| **Values** | Default values, thresholds, timeouts, limits, maximums, ports, paths, counts |
| **Naming** | Exact names of settings, API fields, CLI flags, UI elements, files, roles, or product features |
| **Steps and procedures** | The order of steps, which action comes first, where a setting lives in the UI, how to reach a page |
| **Prerequisites and requirements** | Required versions, licenses, permissions, dependencies, or setup that must be done first |
| **Concepts and definitions** | What a term means, how a concept is described, what something is or is not |
| **Availability and scope** | Deployment types and version ranges something applies to (serverless, ECE, ECH, self-managed, version ranges) |
| **Relationships** | "X requires Y", "X replaces Y", "X is deprecated in favor of Z", "X is removed", "use X instead of Y" |
| **Capabilities** | "X supports Y", "X does not support Y", "X is not available in Z" |
| **Recommendations** | Recommended defaults, best-practice guidance, "we recommend X" where another page recommends something incompatible |

Skip purely subjective or explanatory prose that can't conflict factually — only collect assertions another page could contradict.

## Step 2: Build search terms

From the claims list, extract the most specific terms to search for:

- Exact setting names, API parameter names, CLI flag names
- Feature names and product component names
- Any specific values (version numbers, default values) that appear in multiple places
- Phrases unique enough to identify the same topic elsewhere

**Substitution variables**: Elastic docs use variables like `{{motlp}}`, `{{edot}}`, `{{agent}}`, `{{ech}}`. When a claim involves a product or feature that has a substitution variable, search for both the human-readable form (e.g., "Managed OTLP Endpoint") and the substitution variable (e.g., `motlp`). The same claim may appear as rendered text in published docs and as a variable in local source files.

Prefer specific multi-word terms over single common words. You'll reuse these terms for both the local and cross-repo searches.

## Step 3a: Search the local checkout

For each search term, use `Grep` to find `.md` files **outside** `$ARGUMENTS` that mention the same topic:

```
Grep -r "<term>" --include="*.md" .
```

Collect the matching file paths. Exclude the files you already read in Step 1. Also exclude:

- `_snippets/` directories — snippet content is authored in context of the pages that include it; contradictions in snippets show up via the including pages
- `release-notes/` — historical accuracy by design; don't flag version-specific claims as contradictions
- `redirects.yml` — not prose content
- Auto-generated files (e.g., `nav.yml`, `toc.yml`)

If a search term returns many matching files, narrow to the most specific sub-term before proceeding, or prioritize files in the same product area or directory as `$ARGUMENTS`.

## Step 3b: Search all published Elastic docs (cross-repo)

The local checkout is only one of many repos. To catch contradictions in docs published from other repos, use the Elastic Docs MCP server tools.

For each key claim or term:

1. Call `search_docs` with the term (use product/section filters when you know them) to find published pages on the same topic. Optionally call `find_related_docs` to widen coverage. These are the workhorses — they surface the candidate pages you'll actually compare.
2. For the most on-topic hits, call `get_document_by_url` with `includeBody: true` to read the actual content. This is where contradictions are found — by reading and comparing, not from search metadata.
3. Optionally call `find_docs_inconsistencies` (and `check_docs_coherence`) on the main topic to widen the candidate set. Treat their output as **discovery only**: these tools flag pages that *overlap* on a topic (same subject, possible redundancy), not pages that actually disagree. Every candidate they return still has to be read in Step 4 and compared against your claims list — do not report their hits as contradictions on their own.

**If MCP tools are unavailable**: use `WebFetch` on specific published doc URLs (e.g., `https://www.elastic.co/docs/reference/opentelemetry/compatibility/limitations`). Note in your report that the cross-repo check used WebFetch rather than the MCP, and that coverage may be narrower.

Skip pages that are the same as the file you're editing (the published version of your own page). De-duplicate against anything already found locally in Step 3a.

## Step 4: Read and compare

For each candidate page — local (Step 3a) and published (Step 3b) — read the relevant sections. Compare what it says against your claims list:

- Does it state a different value, limit, path, or name for the same thing?
- Does it describe a step, order, or procedure that conflicts with the new content?
- Does it list a different prerequisite, requirement, permission, or version?
- Does it define a term or concept in a way that no longer matches?
- Does it use a setting, parameter, or feature name that has since changed?
- Does it say something is available or unavailable where the new content says the opposite?
- Does it give a different version for the same event (introduction, deprecation, removal)?
- Does it recommend something incompatible with a new recommendation?
- Does it describe behavior or guidance that the new content supersedes?
- Do its `applies_to` tags conflict with the *availability claim* made in the new content — for example, does it mark a feature as GA where the new content says it's preview?

Flag only genuine factual conflicts. Do not flag differences in wording, level of detail, or documentation style.

## Step 5: Generate the report

Before writing findings, assess each conflict:

**Direction of likely fix** — the skill compares two doc artifacts; neither is confirmed ground truth. Rather than asserting which page is correct, indicate where the evidence points so the writer and an SME can make the final call:
- **Review draft** — multiple independent existing sources agree, or an explicit limitations/warning callout directly contradicts the new claim (strong signal, but still needs confirmation)
- **Review existing** — the new content appears to be a deliberate update (e.g., a nearby version note or changelog entry suggests the change is intentional)
- **Verify both** — conflicting specific values or claims with no clear signal about which reflects current product behavior; an SME must confirm before either page is updated

**Severity**:
- **High** — a user following either page would reach a different (and potentially broken) outcome. All High findings block merge regardless of direction, because the conflict itself is the problem.
- **Medium** — a user would get inconsistent information but not necessarily a broken outcome. File a follow-up.
- **Low** — a nuance difference (e.g., a missing qualifier, a missing version floor, an incomplete list). File a follow-up.

Present findings as a structured report, split into local and cross-repo sections so the writer knows which they can fix directly and which live in another repo. For each contradiction:

1. **Location** — for local files, a clickable markdown link: `[path/to/other-file.md:42](path/to/other-file.md#L42)`; for published pages, the doc URL
2. **Severity** — High / Medium / Low
3. **Direction** — one of exactly three values: `Review draft` / `Review existing` / `Verify both`. Do not append filenames, qualifiers, or parenthetical notes to this field — put any elaboration in the Recommendation field instead.
4. **Claim type** — one of: Values, Naming, Steps/Procedure, Prerequisites, Concepts/Definitions, Availability/Scope, Relationships, Capabilities, Recommendations
5. **Contradiction** — what the existing content says vs. what the new content says, with exact quotes where short enough
6. **Recommendation** — the likely fix and where it belongs; always note when SME confirmation is needed before acting

### Report format

```markdown
## Contradiction check: <input file or directory>

### Summary
N contradictions found (X local, Y cross-repo) across M pages. Blockers: B.
Cross-repo check: ran via MCP / ran via WebFetch / skipped — <reason>.

### Local repo

#### [path/to/existing-file.md](path/to/existing-file.md)
- **[Line 42](path/to/existing-file.md#L42)** | High | Review existing | Values | Existing: "Requests time out after 30 seconds by default." New content sets the default at 60 seconds. → Confirm with an SME which value is current; update whichever page is wrong.
- **[Line 88](path/to/existing-file.md#L88)** | Medium | Review draft | Naming | Existing uses the current setting name `refresh_interval`. New content uses the old name `index.refresh_interval`. Multiple pages agree on `refresh_interval`. → Likely update the draft, but confirm the rename is complete.

### Cross-repo (published docs)

#### https://www.elastic.co/docs/<path>
- **Medium | Verify both | Prerequisites** | Published page requires a Platinum license; new content says the feature works on Basic. → Verify the correct tier with an SME and update whichever page is wrong.
```

If no contradictions are found, say so clearly. Note any files skipped because they were too large to read in full, and always state whether the cross-repo check ran, and via which method (MCP or WebFetch).

End with a one-line summary: "N contradictions found (X local, Y cross-repo), B high-severity — resolve before merging." (Or "No contradictions found." if clean.) Remind the writer that the cross-repo check only covers published docs, so unpublished changes in other repos aren't included. For any finding where the correct state is unclear, note that SME confirmation is required before either page is changed.
