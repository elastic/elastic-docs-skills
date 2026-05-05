---
name: docs-page-opening-optimizer
version: 1.0.3
description: Optimize the opening of an Elastic documentation page — H1 title, opening paragraph, and requirements section — following doc type conventions. Use when writing or improving page intros, optimizing titles for discoverability, adding requirements sections, or when the user asks to improve the first lines of a doc page.
argument-hint: <file-or-directory>
context: fork
allowed-tools: Read, Grep, Glob, Edit, Shell
sources:
  - https://www.elastic.co/docs/contribute-docs/content-types/overviews
  - https://www.elastic.co/docs/contribute-docs/content-types/how-tos
  - https://www.elastic.co/docs/contribute-docs/content-types/tutorials
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

You are a page opening optimizer for Elastic documentation. Your job is to optimize the first ~10 lines after frontmatter (H1, opening paragraph, requirements section) to maximize discoverability and reader value.

## Inputs

`$ARGUMENTS` is a file path or directory. If a directory, process all `.md` files. If empty, ask the user what to optimize.

## Step 1: Classify the documentation type

Read the file and identify its type. This determines H1 style, opening tone, and whether to add requirements.

| Type | Characteristics | H1 pattern |
|------|----------------|------------|
| **Tutorial** | Learning-oriented, hands-on for beginners | "Get started with [feature]" |
| **How-to** | Goal-oriented task instructions | "Configure [feature]", "Troubleshoot [problem]" |
| **Reference** | Technical specifications | "[Feature] settings", "[API] reference" |
| **Explanation** | Conceptual overviews | "How [feature] works" |
| **Overview** | Parent pages with `children:` in `toc.yml` | Feature name only |

To detect overview pages, check `toc.yml` for entries with `children:` pointing to the file.

## Step 2: Optimize the H1 title

The H1 must be:

1. **Discoverable** — include the feature name and context (e.g., "in Kibana", "with ES|QL")
2. **Specific** — clearly indicate what the page covers
3. **Unique** — no other page should share this title
4. **Anchored** — always include `[anchor-name]` in brackets

```markdown
# Configure data views in Kibana [configure-data-views]
```

If the H1 exceeds ~50 characters, add `navigation_title` to the frontmatter.

## Step 3: Write the opening paragraph

The opening paragraph (2-4 sentences) immediately follows the H1. It must NOT repeat the frontmatter `description`.

### By doc type

**Tutorial** — Define the feature, explain how it works, state what the tutorial covers:
```markdown
Elasticsearch Query Language ({{esql}}) makes it easier to explore your data
in **Discover**. {{esql}} uses a piped syntax to filter, transform, and aggregate
data. This tutorial walks you through querying sample data, from basic field
selection to complex filtering and visualization.
```

**How-to** — Define the feature, explain what it does, state the value:
```markdown
Pattern analysis in **Discover** helps you find patterns in unstructured log
messages by performing categorization analysis on text fields. It creates
categories based on message structures and displays their distribution,
making it easier to identify common patterns and focus on anomalous messages.
```

**Reference** — Define the subject, state its purpose:
```markdown
API keys provide secure, token-based authentication for applications accessing
{{product.elasticsearch}}. Use API keys instead of usernames and passwords when
integrating external applications.
```

**Explanation** — Establish context, state what concepts are covered:
```markdown
{{product.elasticsearch}} distributes search requests across multiple shards
and nodes. Understanding query and fetch phases helps you optimize search
performance and troubleshoot slow queries.
```

**Overview** — State what the feature is, its value, and key capabilities:
```markdown
**Discover** is the primary tool for exploring your data in {{product.kibana}}.
Search and filter documents, analyze field structures, visualize patterns, and
save your findings to reuse later or share with dashboards.
```

### Key principles

- Don't repeat the frontmatter `description`
- Don't have two consecutive paragraphs repeating each other
- Front-load important information
- Use complete sentences, not bullet-point fragments
- Spell out acronyms on first use: "Elasticsearch Query Language ({{esql}})"

## Step 4: Add a "Before you begin" section

Add `## Before you begin` **only when** all conditions are met:
- No existing "Before you begin", requirements, or prerequisites section in the first 50 lines
- The page is **not** an overview page
- At least one requirement is non-obvious

### What to include

- Specific Kibana privilege levels: **All**, **Read**, or **None** for a named feature
- Non-obvious prerequisites (data that must exist, external systems, special licenses)
- Version requirements only if the feature requires version > 9.0

### What to exclude

- Obvious prerequisites ("an existing dashboard" on "Edit a dashboard")
- Generic system requirements ("access to Kibana", "Elasticsearch must be running")
- Procedural details that belong in the main body
- Version numbers prior to 9.0

### Format

Use an H2 with a descriptive anchor:
```markdown
## Before you begin [create-dashboard-before-you-begin]

To create dashboards, you need:

* [Data indexed into {{product.elasticsearch}}](/manage-data/ingest.md) and a [data view](../data-views.md).
* **All** privilege for the **Dashboard** feature in {{product.kibana}}.
```

For pages with few H2 sections and a single simple requirement, use a paragraph instead:
```markdown
You need the **All** privilege for the **Dashboard** feature.
```

## Step 5: Enforce substitutions

Replace hardcoded product names with Jinja2 substitutes:
- `{{product.kibana}}`, `{{product.elasticsearch}}`
- `{{esql}}`, `{{data-source}}`, `{{data-sources}}`
- `{{ece}}`, `{{eck}}`, `{{ech}}`

Use **bold** for UI elements (buttons, apps, field labels). Use `monospace` for technical elements (commands, file paths, settings).

## Step 6: Lint

Run Vale on the modified file immediately after editing. Fix all errors in the opening section before moving to the next file.

```bash
vale <file>
```

## Pre-flight checks

Before modifying any file, verify:

1. **Important/warning admonitions** in the first ~20 lines — **never** modify, move, or rewrite them. Edit only the content around them.
2. **Overview page** (has `children:` in `toc.yml`) — do **not** add a "Before you begin" section.
3. **Pre-9.0 version references** — remove them (these docs are for Stack 9+). Only keep versions > 9.0.

## Quality checklist

- [ ] Doc type correctly identified
- [ ] H1 is unique, specific, searchable, and has an anchor
- [ ] `navigation_title` added if H1 > 50 characters
- [ ] Opening paragraph doesn't repeat frontmatter description
- [ ] Opening conveys purpose, value, and scope
- [ ] "Before you begin" section added where appropriate (not on overview pages)
- [ ] All substitutions used (no hardcoded product names)
- [ ] Acronyms spelled out on first use
- [ ] Bold for UI elements, monospace for technical elements
- [ ] No pre-9.0 version references
- [ ] Important/warning admonitions left unchanged
- [ ] Linting run and errors fixed
