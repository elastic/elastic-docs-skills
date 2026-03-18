---
name: llm-matrix-update
version: 1.1.0
description: Update the Elastic Security LLM performance matrix from screenshot or spreadsheet data. Use when the user provides new benchmark scores for the large language model support matrix, or asks to update LLM model scores in docs-content.
argument-hint: <screenshot or table data>
allowed-tools: Read, Grep, Glob, Edit, Write, Bash
sources:
  - https://www.elastic.co/docs/solutions/security/ai/large-language-model-performance-matrix
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

You are updating the Elastic Security LLM performance matrix. The user will provide new benchmark data as a screenshot, spreadsheet, or table. Your job is to update the markdown file to match, preserving the exact formatting conventions.

## Target file

`solutions/security/ai/large-language-model-performance-matrix.md` in the `docs-content` repo. If the file moves, use the alternative location.

## Workflow

1. **Read the current file** to understand its structure and formatting conventions.
2. **Extract data** from the user-provided screenshot or spreadsheet. Carefully read every model name, score, and "Not Recommended" entry.
3. **Compare** the new data against the current table. Identify:
   - New models to add
   - Removed models to delete
   - Changed scores to update
   - Reordering needed (tables are sorted by descending average score)
4. **Apply changes** following the formatting rules strictly.
5. **Push and open a PR** in the `docs-content` repo when the user requests it.

## Formatting rules

These rules are critical. The table uses specific conventions that must be preserved exactly.

### Number formatting

- Drop trailing zeros after the decimal point: `9.50` → `9.5`, `8.00` → `8`, `10.00` → `10`
- Keep meaningful decimal digits: `8.42` stays `8.42`, `9.81` stays `9.81`
- Examples: `7.30` → `7.3`, `9.00` → `9`, `6.96` stays `6.96`

### Cell formatting

- Model names are bold: `**Opus 4.6**`
- The average score column is bold: `**9**`, `**8.19**`
- All other score cells are plain numbers (not bold)
- Failed tests use the exact string `Not recommended` (capital N, lowercase r)

### Table structure

The file contains two tables with identical column headers:

| **Model** | **Alerts** | **Security Knowledge** | **{{esql}} Query Generation** | **Knowledge Base Retrieval** | **Attack Discovery** | **Automatic Migration** | **Average Score** |

Note: `{{esql}}` is a docs-builder substitution variable that renders as "ES|QL" in the published page. Preserve it exactly as `{{esql}}` in the source file.

- **Proprietary models**: Third-party provider models (section anchor: `_proprietary_models`)
- **Open-source models**: Self-deployable models (section anchor: `_open_source_models`)

### Row ordering

Rows in each table are sorted by **Average Score** (highest first aka descending order).

### Row format

Each row follows this exact pattern:

```
| **Model Name** | score | score | score | score | score | score | **avg** |
```

Alignment row uses `:--- |` (left-aligned) for all columns.

## Do not modify

- YAML frontmatter
- Page title, intro paragraph, or admonition
- Section headings or anchor IDs
- Section descriptions ("Models from third-party LLM providers." etc.)
- Column headers or alignment row

## Example transformation

Source data: `Sonnet 4.5 | 8.60 | 7.60 | 7.70 | 7.23 | 8.00 | 10.00 | 8.19`

Formatted row: `| **Sonnet 4.5** | 8.6 | 7.6 | 7.7 | 7.23 | 8 | 10 | **8.19** |`

Source data: `Sonnet 4.6 | 9.30 | 9.50 | 8.40 | 7.45 | Not Recommended | 10.00 | 7.44`

Formatted row: `| **Sonnet 4.6** | 9.3 | 9.5 | 8.4 | 7.45 | Not recommended | 10 | **7.44** |`
