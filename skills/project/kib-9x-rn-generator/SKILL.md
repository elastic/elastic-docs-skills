---
name: docs-kib-9x-rn-generator
version: 1.0.0
description: Generate formatted Kibana 9.x release notes from raw tool output. Use when converting raw .md output from the Kibana release notes generator into publish-ready Markdown, or when asked to write Kibana release notes.
disable-model-invocation: true
argument-hint: <raw .md tool output or path to raw .md file>
allowed-tools: Read, Write, Grep, Glob, Bash(gh *), Bash(cat *), WebFetch
sources:
  - https://release-notes.kibanateam.dev/
  - https://github.com/elastic/kibana/blob/main/docs/release-notes/index.md
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

# Kibana 9.x Release Notes Generator

Convert raw `.md` tool output from the [Kibana release notes generator](https://release-notes.kibanateam.dev/) into publish-ready Markdown for `docs/release-notes/index.md` in the `elastic/kibana` repo. Use GitHub PR context to verify accuracy, improve wording, and assign correct component sub-headings.

## Prerequisites

The GH CLI (`gh`) must be installed and authenticated. The user must provide `$ARGUMENTS` containing either:
- The raw `.md` tool output pasted directly, OR
- A file path to the raw `.md` tool output

If `$ARGUMENTS` is empty, ask the user to provide the raw release notes tool output.

## Process

### Step 1: Read the raw input

If `$ARGUMENTS` looks like a file path, read the file. Otherwise treat `$ARGUMENTS` as the raw `.md` content.

Parse the raw input to extract:
- All PR numbers (normalize patterns like `#123456(opens in a new tab or window)` to `123456`)
- Section classifications (`release_note:feature`, `release_note:enhancement`, `release_note:fix`)
- Component labels from the tool output

### Step 2: Fetch prior Kibana release notes for style reference

Use the GH CLI to fetch `docs/release-notes/index.md` from the `elastic/kibana` repo:

```bash
gh api repos/elastic/kibana/contents/docs/release-notes/index.md --jq '.content' | base64 -d
```

Use this file to learn:
- Typical bullet phrasing, voice, and tense
- How UI labels are bolded vs feature names
- How technical terms and settings are formatted
- Component sub-heading naming conventions and ordering
- Any recurring Kibana terminology patterns

If the file cannot be fetched, proceed with the rules below and note reduced style confidence in the output.

### Step 3: Enrich every PR with GitHub context

For each PR number extracted from the raw input, fetch context via GH CLI:

```bash
gh pr view <PR_NUMBER> --repo elastic/kibana --json title,body,labels,files,comments
```

Use the PR context to:
- Correct or refine what the change actually does
- Remove internal tracking language ("Part 1", "Milestone", team-only jargon)
- Clarify user impact (what changed, where, why it matters)
- Determine the correct component sub-heading from labels, changed files, and description
- Prefer user-facing terminology from the PR when accurate

If a PR cannot be fetched, fall back to the raw tool output text and flag reduced confidence.

### Step 4: Generate the formatted release notes

Produce two parts in the response:

1. **Release notes Markdown** inside a single fenced code block
2. **Notes (Confidence + Assumptions)** outside the code block

## Output structure

### Top header

Use a level-2 header with version number and anchor:

```text
## VERSION [elastic-kibana-VERSION-release-notes]
```

Anchor format: `elastic-kibana-` + version + `-release-notes` (e.g., `elastic-kibana-9.3.2-release-notes`).

### Security advisory

If the release contains security vulnerability fixes, add a MyST admonition immediately after the `##` header:

```text
:::{important}
The VERSION release contains fixes for potential security vulnerabilities. Check our [security advisory](https://discuss.elastic.co/c/announcements/security-announcements/31) for more details.
:::
```

### Section headings

Exactly two possible section headings, in this order:
- `### Features and enhancements [elastic-kibana-VERSION-features-enhancements]`
- `### Fixes [elastic-kibana-VERSION-fixes]`

If a section has no items, omit it entirely.

### Component sub-headings

Use bold component sub-headings to organize items by area. Format: `**Component name**:` (bold text followed by a colon), with bullets listed beneath.

Canonical component names in preferred order:

| # | Component name | Covers |
|---|---|---|
| 1 | **Elastic Agent Builder** | |
| 2 | **Alerting** (or **Alerting and cases**) | Use "and cases" when Cases items are present |
| 3 | **Connectivity** | Connectors, Actions, MCP connectors |
| 4 | **Dashboards and Visualizations** | Lens, Maps, Canvas, dashboard panels |
| 5 | **Data ingestion and Fleet** | Fleet, integrations, ingest pipelines |
| 6 | **Discover** | |
| 7 | **{{esql}} editor** | |
| 8 | **Elastic Observability solution** | Always a cross-reference, never bullets |
| 9 | **Elastic Security solution** | Always a cross-reference, never bullets |
| 10 | **Kibana platform** | Core, Spaces, Saved Objects, platform services |
| 11 | **Kibana security** | Roles, API Keys, authentication |
| 12 | **Machine Learning** | Anomaly Detection, Data Frame Analytics |
| 13 | **Management** | Index Management, Dev Tools Console, Stack Management |
| 14 | **Search** | Elasticsearch UI, Playground, Search homepage |
| 15 | **Workflows** | |

If an item doesn't fit an established component, use a descriptive name consistent with Kibana's architecture and note the decision.

### Cross-references to Observability and Security

Under the appropriate component sub-heading, add:

```text
**Elastic Observability solution**:
For the Elastic Observability VERSION release information, refer to [Elastic Observability Solution Release Notes](docs-content://release-notes/elastic-observability/index.md).

**Elastic Security solution**:
For the Elastic Security VERSION release information, refer to [Elastic Security Solution Release Notes](docs-content://release-notes/elastic-security/index.md).
```

Include these in both Features and Fixes sections when each has entries from those solutions.

## Section mapping from tool output

| Tool output section | Maps to |
|---|---|
| `Features (release_note:feature)` | Features and enhancements |
| `Enhancements (release_note:enhancement)` | Features and enhancements |
| `Fixes (release_note:fix)` | Fixes |

## Component mapping from tool output

| Tool output label | Canonical component |
|---|---|
| "Discover", "Data Discovery" | **Discover** |
| "Management", "Stack Management", "Index Management" | **Management** |
| "Dashboards", "Visualizations", "Lens", "Maps", "Canvas" | **Dashboards and Visualizations** |
| "Alerting", "Cases", "Rules", "Reporting" | **Alerting** (or **Alerting and cases**) |
| "Fleet", "Integrations", "Ingest" | **Data ingestion and Fleet** |
| "ES\|QL", "ESQL" | **{{esql}} editor** |
| "ML", "Machine Learning", "Anomaly Detection" | **Machine Learning** |
| "Platform", "Core", "Spaces", "Saved Objects" | **Kibana platform** |
| "Security", "Roles", "API Keys", "Authentication" | **Kibana security** |
| "Connectors", "Actions", "MCP" | **Connectivity** |
| "Search", "Elasticsearch UI", "Playground" | **Search** |

## Unexpected sections

Items categorized as breaking changes, known issues, deprecations, or security notices do **not** get new headings. These belong in separate files:
- Breaking changes → `docs/release-notes/breaking-changes.md`
- Deprecations → `docs/release-notes/deprecations.md`
- Known issues → `docs/release-notes/known-issues.md`

Map each item into Features and enhancements or Fixes based on what it represents. Flag items that may belong in those separate files in the Notes section.

## PR link formatting

Every bullet referencing a PR must end with:

```text
[#123456]({{kib-pull}}123456)
```

Always use `{{kib-pull}}`. No bare URLs.

Multiple PRs use comma separation:

```text
[#111111]({{kib-pull}}111111), [#222222]({{kib-pull}}222222)
```

## Bullet writing rules

- **Audience**: Power users who can follow PR links for details.
- **One bullet per release-note-worthy change** (not per commit).
- **Verb-first, present tense**: Adds, Enables, Supports, Improves, Fixes, Ensures, Removes, Disables, Updates, Replaces, Refactors.
- **Be concrete**: Prefer "what the user can now do" over implementation detail. If primarily internal refactoring, say so plainly.

## Formatting rules

### UI elements vs feature names
- **Bold** button names, page titles, tabs, dropdown names, and other explicit UI labels (e.g., **Service Inventory**, **Manage index**, **Rule summary**, **Cases**, **Dev Tools Console**, **Data Views**).
- **Capitalize** (do not bold) feature names (e.g., AI Assistant, Machine Learning, Anomaly Detection, Elastic Agent Builder, Search Playground).
- When uncertain, choose the best formatting and note the uncertainty.

### Technical terms
- Use backticks for code-level syntax, operators, commands, settings, and parameters (e.g., `STATS`, `concat`, `xpack.fleet.experimentalFeatures`, `204 No Content`).

### ES|QL normalization
- Use `{{esql}}` (not "ES|QL" or variants).
- Put specific commands/functions in backticks (e.g., `STATS`, `WHERE`, `LOOKUP JOIN`, `FORK`, `KEEP`).

### Product variables

| Variable | Expands to |
|---|---|
| `{{esql}}` | ES\|QL |
| `{{kib}}` | Kibana |
| `{{es}}` | Elasticsearch |
| `{{ech}}` | Elastic Cloud Hosted |
| `{{ml}}` | machine learning |
| `{{serverless-full}}` | Elastic Cloud Serverless |
| `{{observability}}` | Observability |
| `{{fleet-server}}` | Fleet Server |
| `{{stack}}` | Elastic Stack |
| `{{fleet}}` | Fleet |
| `{{kib-pull}}` | Kibana PR link prefix |

### Docs-content link format
Cross-references to other doc pages use the `docs-content://` prefix:
```text
docs-content://release-notes/elastic-observability/index.md
docs-content://release-notes/elastic-security/index.md
```

## Editorial improvements

- **De-jargon**: Remove internal tracking notes ("Part 1", "Milestone") unless essential.
- **Clarify impact**: Replace vague phrasing with user-visible behavior.
- **Combine**: If multiple PRs represent one cohesive change, consolidate into one bullet with all PR links. Note the consolidation.
- **Group by component**: Organize bullets under the correct sub-heading based on PR context.
- **Order within components**: More impactful or user-facing changes first.

## Quality checklist

Before responding, verify:
- [ ] Markdown is in a single code block containing only Markdown
- [ ] Exactly one `##` header with `[elastic-kibana-VERSION-release-notes]` anchor
- [ ] Up to two `###` headers (Features and enhancements, Fixes) in order; omit empty sections
- [ ] Anchors use format `elastic-kibana-VERSION-*`
- [ ] Every PR bullet ends with `[#NNNNN]({{kib-pull}}NNNNN)`; multiple PRs use comma separation
- [ ] Component sub-headings use bold + colon format and follow canonical naming/ordering
- [ ] Cross-references to Observability and Security release notes included where applicable
- [ ] Security advisory uses `:::{important}` / `:::` MyST syntax when needed
- [ ] Verb-first bullets; consistent tense and tone aligned to prior release notes
- [ ] UI labels bolded; feature names capitalized (not bolded); technical terms in backticks
- [ ] `{{esql}}` used consistently (not "ES|QL")
- [ ] Notes section lists lowest-confidence bullets with reasons
- [ ] Notes section states which files from `docs/release-notes/` were referenced
- [ ] No items that belong in `breaking-changes.md`, `deprecations.md`, or `known-issues.md` were added as bullets (flagged separately if found)

## Notes (Confidence + Assumptions) section

After the Markdown code block, include a section that calls out:
- Bullets with the **least confidence** (and why)
- Any **bolding uncertainty** (button/page title vs feature name)
- Any **assumptions** made (component grouping, section mapping, terminology normalization)
- Any **input anomalies** (missing PR numbers, unclear ownership, ambiguous scope)
- Which prior release notes files were referenced (or why they couldn't be fetched)
