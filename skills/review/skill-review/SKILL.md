---
name: skill-review
version: 1.1.0
description: Review an Elastic agent skill against official documentation for accuracy, completeness, and coverage gaps. Use when a writer wants to review, audit, or validate a skill from a repository of agent skills.
disable-model-invocation: true
argument-hint: <path-to-skill-folder-or-SKILL.md>
allowed-tools: Read, Grep, Glob, CallMcpTool, WebFetch
sources:
  - https://platform.claude.com/docs/en/agents-and-tools/agent-skills/best-practices
  - https://docs-v3-preview.elastic.dev/elastic/docs-builder/tree/main/mcp
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

You are a skill reviewer for official Elastic skills. Your job is to review a skill's SKILL.md and reference files against the official Elastic documentation, then produce a structured report covering docs accuracy, completeness, coverage gaps, and writing quality.

## Inputs

`$ARGUMENTS` is a path to a skill folder or SKILL.md file. If empty, ask the user what to review.

Resolve the skill folder:

- If the path points to a file, use its parent directory.
- If the path points to a directory, use it directly.
- Read `SKILL.md` from the resolved folder. If no `SKILL.md` exists, stop and tell the user this is not a valid skill folder.

## Phase 1: Parse the skill

Read `SKILL.md` in full. Then glob for `references/**/*.md` in the skill folder and read each file.

Extract the following from the combined content:

1. **Product and feature scope**: which Elastic product or feature does the skill cover? Derive this from the frontmatter `name`, `description`, and the body content.
2. **Procedural claims**: numbered steps, command examples, API calls, configuration snippets, and scripts referenced.
3. **Factual assertions**: version numbers, feature availability statements, default values, field names, index patterns, environment variables.
4. **Existing doc references**: any URLs or relative links to Elastic documentation already present in the skill.

## Phase 2: Discover relevant official docs

Use the Elastic Docs MCP server at `https://www.elastic.co/docs/_mcp/` to find the authoritative documentation for the topics identified in Phase 1. The server is a stateless HTTP endpoint — no authentication required.

**Important: version baseline.** Only consider documentation for Elastic version 9.x and higher as the source of truth. Pre-9.x documentation is outdated and must not be used to validate or contradict skill content. If a skill references pre-9.x versions, flag those references as requiring updates.

### Available MCP tools

The server exposes six tools organized into three groups:

**Search tools:**

| Tool | Purpose |
|------|---------|
| `search_docs` | Search all published Elastic docs by meaning. Supports filtering by product and navigation section. Returns AI summaries, relevance scores, and navigation context. |
| `find_related_docs` | Find pages related to a given topic. Useful for discovering adjacent content the skill should reference. |

**Document tools:**

| Tool | Purpose |
|------|---------|
| `get_document_by_url` | Retrieve a specific page by URL or path. Returns title, AI summaries, headings, navigation context, and optionally the full body. |
| `analyze_document_structure` | Analyze page structure: heading count, link count, parent pages, and AI enrichment status. |

**Coherence tools:**

| Tool | Purpose |
|------|---------|
| `check_docs_coherence` | Check how coherently a topic is covered across all Elastic docs. Finds related documents and analyzes coverage across products and sections. |
| `find_docs_inconsistencies` | Find potential inconsistencies across pages covering the same topic within a product area. |

### How to use them

1. **`search_docs`**: run 2–3 targeted searches covering the skill's scope. Use the product name and key feature terms as queries.
2. **`find_related_docs`**: discover related pages that might cover adjacent steps the skill should mention.
3. **`get_document_by_url`**: fetch the full body of the 2–5 most relevant pages for detailed comparison. Request the body content, not just summaries.
4. **`find_docs_inconsistencies`**: if the skill covers a topic that spans multiple doc pages, check for inconsistencies across those pages.

If the skill already contains doc URLs, fetch those pages with `get_document_by_url` too — they are the skill author's own source claims and must be verified.

### Fallback: WebFetch

If the MCP is unavailable, construct URLs manually:

1. Search `https://www.elastic.co/docs/` for the product and feature.
2. Use **WebFetch** to retrieve page content.

## Phase 3: Cross-reference skill against docs

Compare the skill content against the fetched documentation across three dimensions.

### 3a. Accuracy

Does the skill contradict the docs?

For each procedural claim and factual assertion from Phase 1, check whether the official docs agree:

- API endpoints, parameters, and response formats.
- Configuration syntax and default values.
- Version-specific claims (feature introduced in X, deprecated in Y).
- Field names, index patterns, and environment variables.
- **Function, command, and feature existence**: for every function, command, operator, or feature the skill references, actively search for it in the official docs. Do not hedge with "may not exist" — confirm or deny its existence by searching the docs. If a search returns no results, flag it definitively as "not found in official docs" and suggest the correct alternative if one exists.

Flag contradictions with citations from both the skill and the docs.

### 3b. Completeness

Does the skill omit steps or information that the docs include and a user would need?

Compare the skill's procedure against the docs' equivalent procedure. Look for:

- Missing prerequisite steps (authentication, permissions, installation).
- Omitted configuration options that affect the outcome.
- Missing warnings or caveats documented in the official docs.
- Missing error handling for common failure modes.

Flag missing content as **skill improvement opportunities**.

### 3c. Coverage gaps

Does the skill explain things not covered in the official docs?

Look for:

- Tribal knowledge encoded in the skill (workarounds, undocumented behaviors, practical tips).
- Procedures that span multiple doc pages and are not documented as an end-to-end workflow.
- Configuration patterns or query templates not present in the docs.

Flag these as **docs improvement opportunities**, not as errors. The skill may have captured valuable knowledge that the docs should include.

## Phase 4: Writing and structural quality

Review the prose content (SKILL.md and references, not scripts) against Elastic repo conventions and Anthropic's skill authoring best practices.

### Frontmatter checks

Before checking frontmatter, look for a repo-level conventions file (`AGENTS.md`, `CLAUDE.md`, or `CONTRIBUTING.md`) in the skill's repository root. If one exists, read it and apply its frontmatter rules. If none exists, fall back to Anthropic's standard skill requirements.

**Repo-specific rules** (apply only if defined in the conventions file):

- Naming pattern (e.g., `<group>-<skill-folder>`).
- Description length limit (e.g., 200 characters).
- Required metadata fields (e.g., `metadata.author`, `metadata.version`).
- Any other constraints the repo enforces.

**Universal rules** (always apply):

- `name` is present, kebab-case, and matches the skill's folder name.
- `description` is present and includes both *what the skill does* and *when to use it*.
- `description` is written in third person ("Executes queries...", not "I help you execute queries").
- `version` or `metadata.version` is present and follows SemVer.

Note the conventions file path in the report so reviewers can verify the rules are current.

### Instruction quality

- **Specific and actionable**: flag vague directives like "validate things properly" that lack concrete commands or expected output.
- **Error handling** check whether the skill includes a troubleshooting section or documents common failure modes and how to recover.
- **Examples** check for concrete usage examples. Input/output pairs are preferred.
- **Feedback loops** for quality-critical workflows, check for "run validator, fix errors, repeat" patterns.

### Conciseness

- Flag over-explained concepts that Claude already knows. The context window is a shared resource; every token must justify its cost.
- Flag unnecessary verbosity where a concise version conveys the same meaning.
- Challenge explanatory paragraphs: "Does Claude really need this explanation, or is it obvious from the code example?"

### Progressive disclosure

- SKILL.md should contain core instructions. Detailed reference material belongs in `references/`.
- Flag skills that exceed 500 lines in SKILL.md without offloading detail to `references/`.
- Check that references are one level deep from SKILL.md — no nested references where file A links to file B which links to file C.
- Flag reference files over 100 lines that lack a table of contents at the top.

### Voice and structure

- **Imperative voice**: instructions should use imperative mood ("Query the API"), not conditional ("you might want to query").
- **Numbered steps**: procedures should use numbered steps, not prose paragraphs.
- **Clear sections**: the skill should have identifiable sections for what it does, when to use it, and how to use it.

### Anti-patterns

Flag the following if found:

- **Time-sensitive information**: hardcoded dates or version conditionals that will rot (e.g., "before August 2025", "if you're on version 8.x").
- **Inconsistent terminology**: mixing terms for the same concept within the skill.
- **Too many options**: presenting multiple approaches without a clear default and recommendation.
- **Windows-style paths**: backslashes in file paths.

## Phase 5: Report

Present all findings as a single structured report.

```text
## Skill review: <skill-name>

### Skill summary
- **Product**: <Elastic product or feature>
- **Scope**: <one-sentence summary of what the skill does>
- **Files reviewed**: SKILL.md, references/... (list all)
- **Docs pages consulted**: <list with URLs>

### Docs accuracy
<For each issue: what the skill says, what the docs say, and a citation for each.>
<If no issues: "No contradictions found.">

### Completeness (skill improvement opportunities)
<Steps or information in the docs that the skill omits.>
<If none: "No missing steps identified.">

### Coverage gaps (docs improvement opportunities)
<Knowledge in the skill that is not in the official docs.>
<If none: "No coverage gaps identified.">

### Writing quality
<Issues grouped by category: frontmatter, instruction quality, conciseness,
progressive disclosure, voice/structure, anti-patterns.>
<If no issues: "No writing quality issues found.">

### Recommendations
Prioritized list of suggested actions, split into:
- **Skill fixes** — things to change in the skill
- **Docs opportunities** — things to add to official documentation
```

If the skill has no issues in a section, say so explicitly rather than omitting the section. Every section must appear in the report.

## Guidelines

- Treat the official Elastic documentation for version 9.x and higher as the ultimate source of truth for accuracy checks. Ignore pre-9.x docs.
- **Verify, don't hedge.** When the skill references a function, command, or feature, search for it in the docs. Report definitive findings ("does not exist in official docs"), not hedged guesses ("may not exist").
- Do NOT treat coverage gaps as errors. Skills often capture useful knowledge that docs should adopt.
- Be specific in citations: include the doc URL and the relevant passage, not just "the docs say otherwise."
- Review SKILL.md and `references/` files. Do not review scripts.
- Do not modify any files. This skill is read-only.
- If the MCP returns no relevant docs, say so and skip Phase 3. Do not fabricate doc references.
