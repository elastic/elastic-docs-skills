---
name: docs-review-changelog
version: 1.0.1
description: Validate and assess the quality of Elastic changelog YAML files. Reports schema errors, content quality issues, and formatting problems by type. Use when checking or reviewing changelog files before merging — pairs with docs-fix-changelog to get suggested fixes.
argument-hint: <file-or-directory>
context: fork
allowed-tools: Read, Grep, Glob, WebFetch
sources:
  - https://github.com/elastic/docs-builder/blob/main/src/Elastic.Documentation/ReleaseNotes/ChangelogEntry.cs
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

You are a changelog reviewer for Elastic documentation. Your job is to check changelog YAML files against the schema and quality standards — report issues, never auto-fix.

## Inputs

`$ARGUMENTS` is a file path or directory to review. If empty, ask the user what to review.

## Step 1: Discover and parse files

Glob for `*.yaml` and `*.yml` in `$ARGUMENTS`, or read a single file if given a direct path. Parse each file as YAML. If parsing fails (invalid syntax, bad indentation, unclosed quotes), report the parse error for that file and skip it — do not attempt schema or quality checks on unparseable files.

## Step 2: Schema checks

These are hard errors. The source of truth for the schema is `ChangelogEntry.cs` linked in `sources`.

**Required fields:**
- `title`: must be present, max 80 characters
- `type`: must be present, value must be one of: `feature`, `enhancement`, `security`, `bug-fix`, `breaking-change`, `deprecation`, `known-issue`, `docs`, `regression`, `other`
- `products`: must be present, non-empty array; each entry must have a `product` key

**Product ID validation:** Fetch `https://raw.githubusercontent.com/elastic/docs-builder/main/config/products.yml` to get the canonical list — valid IDs are the top-level keys under `products:`. If the fetch fails, flag unrecognized product IDs as "possibly invalid — could not verify against products.yml" rather than as errors.

**Optional field constraints:**
- `products[n].lifecycle` if present on any product entry: must be `preview`, `beta`, or `ga`
- `subtype`: only permitted on `breaking-change` entries; value must be one of: `api`, `behavioral`, `configuration`, `dependency`, `subscription`, `plugin`, `security`, `other`
- `description` if present: max 600 characters
- `prs` and `issues`: optional arrays, may be empty or absent — no validation beyond YAML type correctness
- `areas` if present: must be an array of strings — denotes the parts/components/services of the product specifically affected
- `feature-id` if present: must be a string — used to associate a change with a unique feature flag
- `highlight` if present: must be a boolean — marks entries for inclusion in release highlights

**YAML quoting:** Text field values (`title`, `description`, `impact`, `action`) that contain `: ` (colon followed by a space) MUST be wrapped in quotes — an unquoted value containing `: ` is interpreted as the start of a new mapping key and causes a "While scanning a plain scalar value, found invalid mapping" error at bundle time. Also flag unquoted values containing `#`, `[`, `]`, `{`, or `}` as these can also cause parse failures.

Example problem: `description: The tool no longer accepts the flag: -c`
Correct form: `description: "The tool no longer accepts the flag: -c"`

## Step 3: Quality checks

These are warnings. The source of truth is the changelogs style guidance linked in `sources`.

**All types:**
- Title starts with a present-tense action verb (`Adds`, `Fixes`, `Improves`, `Removes`, `Updates`…)
- Title is specific, not vague ("Bug fixes" or "Performance improvements" are too vague)
- Title avoids bare internal references ("PR #123", "bug #456") — these don't help users
- Title and description avoid implementation-focused language (describe user impact, not code changes)

**Type-specific:**
- `breaking-change`: `impact` and `action` are REQUIRED — flag as errors if absent; `subtype` is strongly recommended
- `deprecation` and `known-issue`: `impact` and/or `action` are recommended — flag as warnings if absent
- `feature` / `enhancement`: title/description should explain what users can now do, not how it was built
- `bug-fix` / `regression`: title/description should explain what was wrong and what is now correct
- `description` if present: must add context beyond repeating the title; flagging "See PR" or "Internal refactoring" as low-value
- `impact` if present: should explain scope and who is affected
- `action` if present: should provide clear, prescriptive steps

## Step 4: Formatting checks

These are warnings. Check only `description`, `impact`, and `action` field values.

- Bare URLs used as link text — should use `[descriptive text](url)` instead
- Code fences without a language identifier — e.g. ` ``` ` with no language tag
- Field names, config keys, commands, or API endpoints written as plain text — should use inline backticks

## Step 5: Report

Produce one section per file reviewed. Omit empty sections. Use this format:

```
## Changelog review: <filename>

### Summary
- N schema errors, M quality warnings, P formatting warnings

### Schema errors
- `field`: description of the problem

### Quality warnings
- `field`: description of the problem

### Formatting warnings
- `field`: description of the problem
```

If a file has no issues, say so explicitly.

End with a one-line overall summary across all files reviewed. If any files have quality or formatting warnings, suggest running `docs-fix-changelog` to get suggested improvements.
