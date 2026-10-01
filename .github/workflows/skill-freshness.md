---
description: |
  Weekly check of all skills for staleness against their upstream source URLs.
  Compares each SKILL.md against the documentation it encodes and opens a PR
  if anything has drifted.

on:
  schedule: weekly
  workflow_dispatch:

permissions:
  contents: read
  pull-requests: read
  issues: read
  copilot-requests: write

network:
  allowed:
    - defaults
    - "www.elastic.co"
    - "docs-v3-preview.elastic.dev"
    - "platform.claude.com"
    - "developers.google.com"

tools:
  github:
    lockdown: false
  web-fetch:
  edit:

safe-outputs:
  create-pull-request:
    title-prefix: "[skill-freshness] "
    labels: [automated, skill-freshness]
    allowed-files:
      - skills/**/SKILL.md
      - skills/**/references/*.md
      - .claude-plugin/plugin.json
    protected-files:
      policy: request_review
      exclude:
        - .claude-plugin/
  add-comment:
  close-issue:
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

# Weekly Skill Freshness Check

Check all skills in `skills/**/SKILL.md` for staleness against their upstream source URLs, then check the area reference files in `skills/**/references/` for staleness against the repos they name.

## Process

1. Find every `SKILL.md` file under the `skills/` directory.
2. For each skill:
   - Read the SKILL.md file.
   - Parse the `sources:` list from its YAML frontmatter.
   - **If `sources:` exists**: fetch each source URL (append `.md` for the LLM-friendly variant, e.g. `https://www.elastic.co/docs/contribute-docs/style-guide.md`). **If a fetch fails or times out for any reason (network error, firewall block, HTTP error), skip that URL immediately — do not retry.**
   - **If no `sources:` field**: use the Elastic Docs MCP server (`https://www.elastic.co/docs/_mcp/`) to find relevant upstream content. Call `SemanticSearch` with the skill's name and description to discover related documentation pages. Then fetch the top results with `GetDocumentByUrl` (with `includeBody: true`) and compare them against the skill.
   - Compare the fetched content against the rules, syntax, and options encoded in the skill.
   - If the skill is stale (new rules added, syntax changed, options removed, links broken), update the SKILL.md to reflect the current upstream state. If the skill lacked `sources:` and you found relevant upstream pages, add them to the frontmatter.
   - After updating a skill, run its evals to catch regressions (see "Post-update eval check" below).
3. Check the area reference files (see "Area reference files" below).
4. If any files changed:
   - Read `.claude-plugin/plugin.json` and bump its `version` field (patch increment — e.g. `1.0.0` → `1.0.1`).
   - Request a pull request using the `create-pull-request` safe output exactly once, summarizing what drifted, why, and eval results.
5. If nothing changed, close this issue with a comment confirming all skills are current.

## Area reference files

Files under `skills/**/references/` that declare an `area:` key in their YAML frontmatter are area reference files. They encode facts about a documentation area — product source paths, navigation files, local conventions — that no upstream URL covers, so they need a different check from `sources:`.

For each one:

1. **Read the frontmatter.** Note `verified` (the date it was last checked), `verified_against` (the repos it was checked against), and `status` (an anchor in the same directory's `status.md`, present only when an in-flight transition affects the area).
2. **Check the product source paths.** The *Source of truth* section names paths in the repos listed in `verified_against`. Check each one still exists using the GitHub contents API on the default branch. A path that 404s is the highest-value finding in this workflow, because the skill verifies product facts there and a moved path silently finds nothing.

   **Some paths are cited precisely because they no longer exist.** Area files record moved paths as traps, so that a search against the old location does not look like a missing feature — `workflows.md` says the old `x-pack/platform/plugins/shared/workflows/` path is gone, and `elastic-security.md` says the same of `x-pack/plugins/security_solution/`. Read the sentence around a path before flagging it. When the file describes it as old, stale, moved, removed, or no longer existing, a 404 confirms the file is correct and is not a finding. Flag a 404 only for a path the file presents as current. If a path the file calls removed has *come back*, that is worth reporting, because the trap is now wrong.
3. **Resolve any `status:` entry.** Read the named entry in `status.md` and check its *Expires when* condition — normally whether a tracking issue has closed. When the condition has been met, the entry is stale and should be removed, and the area file section it covers needs refreshing. If a tracking issue is in a repo this workflow cannot read, say so rather than assuming either way.
4. **Report the age.** Anything with `verified` more than 90 days old gets flagged for a human to re-check, whether or not a path broke.

**Do not guess a replacement for a broken path.** Report it with the old path, the 404, and the area file it appears in, and let a human resolve it. An area file that confidently names the wrong path is worse than one that names a path someone knows is broken — a wrong path sends the skill to verify a claim against code that no longer governs it.

You may bump `verified` only when you have actually re-checked every path in the file and they all resolve. Never bump it to silence the age flag.

Report findings under a "### Area reference files" section in the PR body:

```markdown
### Area reference files

| File | Verified | Broken paths | Status entry |
|------|----------|--------------|--------------|
| references/workflows.md | 112 days ago ⚠️ | `src/platform/...` (404) | — |
| references/elastic-security.md | 40 days ago | None | #1541 still open |
```

When nothing is wrong across all area files, note "All area reference files current" instead of the table.

## Pull request creation rules

When files change, the `create-pull-request` safe output is the only mechanism for opening the pull request.

- Emit exactly one `create-pull-request` safe output.
- Do not run `gh pr create` or any other pull request creation command.
- Do not write additional pull request JSON files manually.
- Do not emit `report_incomplete` after emitting `create-pull-request`.
- After emitting the `create-pull-request` safe output, stop and provide only a brief summary.

## Post-update eval check

After updating a skill, check whether `evals/evals.json` exists in the skill directory. If it does:

1. **Before editing**, read the original SKILL.md content and save it mentally as the "old version."
2. **After editing**, for each eval in `evals/evals.json`:
   - Read the eval prompt and expectations.
   - Follow the **updated** skill's instructions to accomplish the eval prompt.
   - Grade your output against each expectation (PASS/FAIL with evidence).
3. **Compare**: Note any expectations that the updated skill fails. If the update causes regressions (expectations that would have passed with the old version now fail), flag these in the PR body.
4. **Include results** in the PR body under a "### Eval results" section for each updated skill:

```markdown
### Eval results

#### <skill-name>
| Eval | Pass Rate | Regressions |
|------|-----------|-------------|
| 1 — <prompt summary> | 3/4 (75%) | None |
| 2 — <prompt summary> | 2/3 (67%) | ❌ "expectation text" — was passing before update |
```

If all evals pass, note "All evals passing" instead of the table.

If no evals exist for a skill, note "No evals available" and skip.
