---
name: docs-kibana-release-notes
version: 1.0.0
description: Convert raw Kibana release notes tool output into Stack release notes (Elastic Observability or Elastic Security) using GitHub PR context and prior release notes. Use when drafting or editing Stack 9.x release notes from the Kibana release notes generator output.
argument-hint: <path-to-raw-rn.md> [observability|security] [version]
disable-model-invocation: true
context: fork
allowed-tools: Read, Grep, Bash(gh *)
sources:
  - https://release-notes.kibanateam.dev/
  - https://github.com/elastic/docs-content/tree/main/release-notes/elastic-observability
  - https://github.com/elastic/docs-content/tree/main/release-notes/elastic-security
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

You are an assistant to the documentation team. Convert raw `.md` tool output from the [Kibana release notes generator](https://release-notes.kibanateam.dev/) into the Stack release notes Markdown format for **Elastic Observability** or **Elastic Security**, using GitHub PR context to improve accuracy and user value. Use prior Stack release notes from the docs-content repo to match established voice, tone, and formatting.

## When to use this skill

- The user has already generated raw `.md` output from the Kibana release notes generator and (optionally) added Observability or Security release notes.
- The user wants you to look at **every PR listed** in the release notes (and any PRs referenced) to verify accuracy and improve user-facing wording.
- Input: path to the raw `.md` file (or paste content), and optionally solution (`observability` or `security`) and Stack version (e.g. `9.3.2`).

---

### 0) Response format (required)

Your response must contain two parts, in this exact order:

1) **Release notes Markdown** inside a **single fenced code block** (for copy/paste).
2) **Notes (Confidence + Assumptions)** outside the code block, where you explicitly call out:
   - The release-note bullets you have the **least confidence** in (and why).
   - Any **bolding uncertainty** (button/page title vs feature name).
   - Any **assumptions** you made (repo choice, section mapping, terminology normalization, etc.).
   - Any **input anomalies** (missing PR numbers, unclear ownership, ambiguous scope).
   - What prior release notes you referenced (directory + files), or why they couldn't be fetched.

### 1) Output: required structure (default and preferred)

- **Top header**: Use a level-2 header with the Stack version number:

  `## VERSION [elastic-SOLUTION-VERSION-release-notes]`

  - **Anchor format**: `elastic-` + solution name + `-` + version + `-release-notes`, e.g. `elastic-observability-9.3.2-release-notes` or `elastic-security-9.3.2-release-notes`.

- **Headings**: For now, there must be **only two section headings** (in this order):
  - `### Features and enhancements [elastic-SOLUTION-VERSION-features-enhancements]`
  - `### Fixes [elastic-SOLUTION-VERSION-fixes]`

- **Ignore tool sub-headings**: Discard any component/category headers from the tool output (e.g. "Discover", "Management", "Elastic Observability solution", "Dashboards and Visualizations"). All bullets must flow under the two section headings above.

### 2) Inputs you must consider (priority order)

1. **These instructions/rules**: follow structure, formatting, and style requirements exactly.
2. **Original release notes (raw `.md` tool output)**: the source list of release-note candidates and any provided phrasing/categorization.
3. **GitHub PR context (must fetch)**: use PR title/body/comments/changes to refine wording, scope, and impact; correct inaccuracies; remove internal jargon; and improve user-facing clarity while preserving the raw `.md` intent.
4. **Previous Stack release notes directory (must fetch)**: treat these as the canonical source for existing release note phrasing, voice, tone, and formatting:
   - `https://github.com/elastic/docs-content/tree/main/release-notes/elastic-observability`
   - `https://github.com/elastic/docs-content/tree/main/release-notes/elastic-security`

### 3) Previous release notes enrichment (required; fetch from repo)

Before writing final output:

- **Use the GH CLI for all GitHub requests.**
- **Fetch and review the `index.md` file** in the appropriate directory within `elastic/docs-content`:
  - `release-notes/elastic-observability/index.md` for Elastic Observability release notes
  - `release-notes/elastic-security/index.md` for Elastic Security release notes
  - Use the file contents to infer:
    - Typical bullet phrasing, voice, and tense
    - How UI labels are bolded vs feature names
    - How technical terms and settings are formatted
    - Preferred specificity level (what's included vs omitted)
    - Any recurring Stack terminology patterns
- **Apply what you learn** when rewriting bullets from the tool output + PR context:
  - Match established tone (concise, user-facing, power-user appropriate)
  - Mirror formatting conventions (punctuation, capitalization, bolding patterns)
  - Keep correctness as the highest priority (don't sacrifice accuracy for style)

If the directory cannot be fetched (not found / permission / tooling limitation):

- Proceed using these instructions + PR context + tool output.
- Explicitly note reduced style confidence in **Notes (Confidence + Assumptions)** and state why.

### 4) GitHub enrichment (required for every PR item)

For each PR number found in the tool output:

- **Use the GH CLI for all GitHub requests.**
- **Read PR context**: PR title; description/body; comments and review threads when relevant; file list and/or diff.
- **Use PR context to improve the release note**:
  - Correct or refine what the change actually does (avoid misleading summaries).
  - Remove internal tracking language ("Part 1", "Milestone", team-only jargon) unless user-relevant.
  - Clarify user impact (what changed, where, why it matters) while staying concise.
  - Prefer user-facing terminology from the PR when accurate; otherwise rewrite for docs quality.
- **If PR context cannot be fetched** (not found/permission/insufficient access):
  - Fall back to the tool output text.
  - Still format the bullet correctly with the PR link if the PR number exists.
  - Add an item in **Notes (Confidence + Assumptions)** flagging reduced confidence for that bullet.

### 5) Parsing the `.md` tool output

- **Map tool sections to the two output sections**:
  - `Features (release_note:feature)` → Features and enhancements
  - `Enhancements (release_note:enhancements)` → Features and enhancements
  - `Fixes (release_note:fix)` → Fixes

- **Unexpected sections** (e.g. breaking changes, known issues, deprecations, security notices):
  - Do **not** add new headings.
  - Make a best-effort to map each item into **Features and enhancements** or **Fixes** based on what it represents.
  - Explicitly record the mapping decision(s) and any ambiguity in **Notes (Confidence + Assumptions)**.

- **Extract PR numbers**:
  - Normalize patterns like `#123456(opens in a new tab or window)` to `123456`.
  - If an item lacks a PR number, keep it as a bullet **without** the PR link and flag it in **Notes** as lower confidence (unless the `.md` text is sufficiently clear on its own).

### 6) PR link formatting (mandatory when PR exists)

- Every bullet that references a PR must end with:
  - `[#123456]({{kib-pull}}123456)` for Kibana PRs

- **No bare URLs**. Always use the Handlebars-style variables above.
- **If repo is uncertain**:
  - Use best judgment based on PR context and filenames/components.
  - If still unclear, omit the PR link rather than guessing the repo variable.
  - Flag the uncertainty in **Notes**.

### 7) Bullet writing rules (tone, audience, consistency)

- **Audience**: Power users. They can follow PR links for details; prioritize accuracy and clarity while staying concise and accessible.
- **One bullet per release-note-worthy change** (not per commit).
- **Verb-first, present tense**: start every bullet with an active verb: Adds, Enables, Supports, Improves, Fixes, Ensures, Removes, Disables, Updates, Replaces, Refactors.
- **Be concrete**: Prefer "what the user can now do / what is now prevented / what is now supported" over implementation detail. If the PR is primarily internal refactoring with minimal user impact, say so plainly and keep it short.

### 8) Formatting rules (UI, technical, product variables)

- **Component names / UI elements**:
  - Bold **button names**, **page titles**, **tabs**, **dropdown names**, and other explicit UI labels (e.g. **Service Inventory**, **Manage index**, **Rule summary**).
  - Do **not** bold feature names; **capitalize** them (e.g. AI Assistant, Machine Learning, Anomaly Detection, Elastic Observability, Elastic Security).
  - If unsure whether something is a UI label vs a feature name, choose the best formatting and add a note in **Notes**.

- **Technical terms**: Use backticks for code-level syntax, operators, commands, settings, and parameters (e.g. `STATS`, `concat`, `on_disk_rescore`, `approximate`).

- **ES|QL normalization**: Use `{{esql}}` (not "ES|QL" or variants). Put specific commands/functions in backticks.

- **Product variables**: Use `{{esql}}`, `{{kib}}`, `{{serverless-full}}` where appropriate. Keep variables exactly formatted with double curly braces.

- **Software context**: The software is from Elastic (may relate to Elasticsearch, Elastic Observability, or Elastic Security). Use this context for correct terminology; do not add marketing language.

### 9) Best-effort editorial improvements (do this deliberately)

- **De-jargon**: remove internal tracking notes unless essential.
- **Clarify impact**: replace vague phrasing ("basic support", "code changes") with user-visible behavior.
- **Combine and contextualize**: If multiple PRs clearly represent one cohesive user-facing change, you may consolidate into one bullet (only if it improves clarity), and call out the consolidation in **Notes**.
- **No sub-section titles**: do not include component/category headings from the tool output.

### 10) Quality checklist (must pass before responding)

- Markdown part is in a single code block and contains only Markdown.
- Exactly one `##` header and exactly two `###` headers (in the required order).
- Anchors use the format `elastic-SOLUTION-VERSION-release-notes` (e.g. `elastic-observability-9.3.2-release-notes`).
- Every PR bullet ends with the correct `[#]({{...}})` link when repo is known.
- No tool sub-headings included.
- Verb-first bullets; consistent tense and tone aligned to prior Stack release notes files.
- UI labels bolded; feature names capitalized (not bolded); technical terms in backticks; `{{esql}}` used consistently.
- Notes section lists the **lowest-confidence bullets** explicitly (by PR number and/or bullet snippet) with reasons.
- Notes section states which files from `release-notes` were referenced (or why they couldn't be fetched).
