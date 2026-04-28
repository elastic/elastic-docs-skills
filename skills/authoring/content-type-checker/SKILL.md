---
name: docs-content-type-checker
version: 2.1.0
description: Check a docs-content page against Elastic content type guidelines (overview, how-to, tutorial, troubleshooting, changelog). Use when the user asks to check content type compliance, validate page structure, or review a doc against content type standards.
argument-hint: <file-or-directory>
context: fork
allowed-tools: Read, Grep, Glob, CallMcpTool, WebFetch
sources:
  - https://www.elastic.co/docs/contribute-docs/content-types/overviews
  - https://www.elastic.co/docs/contribute-docs/content-types/how-tos
  - https://www.elastic.co/docs/contribute-docs/content-types/tutorials
  - https://www.elastic.co/docs/contribute-docs/content-types/troubleshooting
  - https://www.elastic.co/docs/contribute-docs/content-types/changelogs
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

You are a content type compliance checker for Elastic documentation. Your job is to evaluate documentation pages against the Elastic content type guidelines and report issues.

## Inputs

`$ARGUMENTS` is a file path or directory. If empty, ask the user what to check.

## Step 1: Detect the content type

Read the target file and check the frontmatter for a `type` field:

```yaml
---
type: overview
---
```

Valid content types: `overview`, `how-to`, `tutorial`, `troubleshooting`, `changelog`.

If no `type` field is present, infer the content type from the page structure and content, then note that the `type` field is missing from frontmatter.

## Step 2: Fetch the guidelines

### Preferred: elastic-docs MCP

Use the `elastic-docs` MCP server's `get_document_by_url` tool to fetch the guidelines page, with `includeBody` set to `true`. Pass the guidelines URL from the table below.
Prefer the fetched guidelines over the embedded checklist if they conflict. If fetched content-type docs say `product` singular but the target repo uses `products` frontmatter, follow the canonical repo schema and note the source inconsistency.

### Fallback: WebFetch

If the MCP is unavailable, fetch the guidelines and templates directly. Use the `.md` suffix on guidelines URLs to get the LLM-friendly version.

| Content type    | Guidelines URL                                                                       | Template URL                                                                                                                          |
|-----------------|--------------------------------------------------------------------------------------|---------------------------------------------------------------------------------------------------------------------------------------|
| overview        | https://www.elastic.co/docs/contribute-docs/content-types/overviews.md               | https://raw.githubusercontent.com/elastic/docs-content/main/contribute-docs/content-types/_snippets/templates/overview-template.md              |
| how-to          | https://www.elastic.co/docs/contribute-docs/content-types/how-tos.md                 | https://raw.githubusercontent.com/elastic/docs-content/main/contribute-docs/content-types/_snippets/templates/how-to-template.md                |
| tutorial        | https://www.elastic.co/docs/contribute-docs/content-types/tutorials.md               | https://raw.githubusercontent.com/elastic/docs-content/main/contribute-docs/content-types/_snippets/templates/tutorial-template.md              |
| troubleshooting | https://www.elastic.co/docs/contribute-docs/content-types/troubleshooting.md         | https://raw.githubusercontent.com/elastic/docs-content/main/contribute-docs/content-types/_snippets/templates/troubleshooting-template.md       |
| changelog       | https://www.elastic.co/docs/contribute-docs/content-types/changelogs.md              | *(schema is inline in the guidelines page)*                                                                                           |

Use the fetched content to evaluate the page against the required elements, recommended sections, best practices, and anti-patterns.

## Step 3: Evaluate against guidelines

Check the page against the fetched content type guidelines. For each required element, check whether it's present and correct. For best practices, note any violations.

Use these current checklists as the minimum review criteria:

### Shared frontmatter and metadata

- **Filename**: Matches the content type pattern when one exists.
- **Frontmatter**: Includes `applies_to`, `description`, and the repo's canonical product metadata field. In docs-content, use `products`, not `product`.
- **Title**: Matches the content type intent, uses sentence case, and is specific enough for search and navigation.
- **Introduction**: Helps readers confirm that the page matches their goal.

### Overview

- **Purpose**: Explains a single concept, feature, product, or capability.
- **Required content**: Answers what it is, how it works, and why it matters.
- **Recommended content**: Includes use cases or examples, how-it-works content, next steps, and related pages when useful.
- **Anti-patterns**: Does not include long procedures, reference tables that belong elsewhere, or duplicated how-to content.

### How-to guide

- **Purpose**: Helps users complete one self-contained task.
- **Required content**: Includes an action-verb title, a short outcome-focused introduction, a **Before you begin** or requirements section, numbered steps, and success checkpoints.
- **Recommended content**: Includes next steps and related pages when useful.
- **Anti-patterns**: Does not teach broad concepts, chain many tasks together, exceed roughly 10 overall steps without reason, or omit verification for important actions.

### Tutorial

- **Purpose**: Provides a hands-on learning experience that chains related tasks toward a meaningful outcome.
- **Required content**: Includes learning objectives, audience or skill expectations when useful, prerequisites and setup, instructional steps, checkpoints or results, code annotations when code is central, next steps, and related pages.
- **Recommended content**: Uses progressive disclosure, realistic examples, and verification steps throughout.
- **Anti-patterns**: Does not behave like a single narrow recipe, a reference page, or a long conceptual overview without practice.

### Troubleshooting

- **Purpose**: Helps users resolve one specific, repeatable problem.
- **Required content**: Includes a problem-focused title, a **Symptoms** section, and a **Resolution** section.
- **Symptoms**: Describes user-visible behavior only, includes exact error messages when available, and avoids causes.
- **Resolution**: Provides ordered, prescriptive steps from most common to least common fix, with minimal configuration examples when useful.
- **Optional content**: Includes **Diagnosis** only when the same symptom can have multiple causes, **Best practices** only for prevention directly tied to the problem, and **Resources** only for supplementary reading.
- **Anti-patterns**: Does not use a generic "Troubleshooting X" title for a dedicated issue page, mix unrelated problems, or put long explanations before the fix.

### Changelog

- **Purpose**: Describes one user-facing product change for release notes generation.
- **Required content**: Includes `title`, `type`, and `products`.
- **Title**: Uses present tense, starts with an action verb, focuses on user impact, and stays under 80 characters.
- **Description**: Adds context only when needed, focuses on user value, and stays under 600 characters.
- **Impact and action**: Required for breaking changes and recommended for deprecations and known issues.
- **Anti-patterns**: Does not focus on implementation details, internal references, vague summaries, or duplicated title text.

When the inferred type differs from the declared `type`, report the mismatch first, then evaluate against the type that best matches the page's actual purpose.

## Step 4: Generate report

```
## Content type check: <file>

### Detected type: <type>

### Required elements
- ✅ Frontmatter `applies_to`: Present
- ❌ Frontmatter `description`: Missing
- ✅ Title: Present, uses correct pattern
- ...

### Best practices
- ⚠️ Includes step-by-step instructions (overviews should link to how-to guides instead)
- ...

### Summary
X of Y required elements present. Z best practice issues found.
```
