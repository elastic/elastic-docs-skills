---
name: docs-frontmatter-audit
version: 1.1.0
description: Audit Elastic documentation files for frontmatter completeness and correctness. Checks applies_to, products, description, and navigation_title fields across a directory. Use when auditing docs metadata, checking frontmatter quality before publishing, or validating a batch of files.
argument-hint: <file-or-directory>
context: fork
allowed-tools: Read, Grep, Glob, CallMcpTool, WebFetch
sources:
  - https://elastic.github.io/docs-builder/syntax/frontmatter/
  - https://www.elastic.co/docs/contribute-docs/how-to/cumulative-docs/reference
  - https://developers.google.com/search/docs/appearance/snippet
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

You are a frontmatter auditor for Elastic documentation. Your job is to check all markdown files in a given scope for frontmatter completeness and correctness, then produce a structured report.

## Inputs

`$ARGUMENTS` is a file path or directory to audit. If empty, ask the user what to audit.

Use these configuration defaults unless the user provides overrides. Ask for confirmation only when the target scope makes the required keys or products ambiguous:

| Setting | Default | Description |
|---------|---------|-------------|
| **Required `applies_to` keys** | `stack`, `serverless` | Which keys must be present |
| **Required `products`** | *(none)* | Which product IDs must appear (e.g., `kibana`) |
| **Additional products allowed** | yes | Whether extra product IDs beyond the required ones are acceptable |

## Required frontmatter elements

Check each file for the following elements:

### 1. `applies_to` (mandatory)

Every page must have `applies_to` in its frontmatter. Verify:
- Presence of all configured required keys
- Valid lifecycle values: `preview`, `beta`, `ga`, `deprecated`, `removed`, `unavailable`
- Valid version syntax if present (for example, `ga 9.1+`, `preview =9.0`, `beta 9.1-9.2`, `preview =9.0, ga 9.2+`)
- No mixed dimensions (stack/serverless keys should not be combined with deployment keys)

```yaml
applies_to:
  stack: ga
  serverless: ga
```

Flag files missing this element or missing required keys. Preserve existing version-specific values — don't normalize `ga 9.1` to just `ga`.

### 2. `products` (mandatory)

Must include the configured required product IDs. May include additional products. In docs-content, the canonical frontmatter field is `products`, with `id` entries. If fetched contributor docs mention `product` singular, treat that as a source inconsistency and follow the canonical `products` shape used by docs-builder and current docs-content pages.

```yaml
products:
  - id: kibana
```

Flag files missing this element or missing required products. Don't remove existing additional products.
Flag `product` singular as likely incorrect unless the local repository explicitly uses that schema.

### 3. `description` (mandatory)

Validate against these rules:
- Present and non-empty
- Maximum 200 characters
- Complete sentence (not a fragment or label)
- No Jinja2 substitution variables (`{{kib}}`, `{{es}}`, `{{esql}}` — these aren't parsed in frontmatter)
- No label prefixes ("Reference -", "Tutorial -", "Guide -")
- Clear, user-facing summary of the page content
- Quoted if it contains punctuation or characters that could be misread by YAML, including colons

### 4. `navigation_title` (recommended)

Check if the H1 title exceeds ~50 characters. If so, flag that a `navigation_title` should be added.

```yaml
navigation_title: "Configure ML alerts"
```

### 5. `mapped_pages` (preserve)

If present, don't flag or suggest changes. If absent, don't suggest adding it.

## Execution

1. **Glob** for all `.md` files in the specified scope
2. **Read** the frontmatter of each file
3. **Validate** each element against the rules above
4. **Read** the H1 title to check length for `navigation_title`
5. **Compile** the report

## Report format

```
## Frontmatter audit: <scope>

**Configuration:**
- Required applies_to keys: stack, serverless
- Required products: kibana
- Files scanned: N

### Issues found

#### Missing `applies_to`
| File | Issue |
|------|-------|
| path/to/file.md | Missing entirely |
| path/to/other.md | Missing `serverless` key |

#### Missing `products`
| File | Issue |
|------|-------|
| path/to/file.md | Missing `kibana` product |

#### Invalid or missing `description`
| File | Issue |
|------|-------|
| path/to/file.md | Missing description |
| path/to/other.md | Contains Jinja2 variables |
| path/to/third.md | Exceeds 200 characters (247 chars) |

#### Missing `navigation_title`
| File | H1 length |
|------|-----------|
| path/to/file.md | 63 chars |

### Summary

- ✅ N files passed all checks
- ❌ N files have issues
  - N missing applies_to
  - N missing products
  - N invalid/missing description
  - N missing navigation_title (recommended)
```

Group issues by type, not by file, so users can batch-fix related problems. Only include sections that have issues.
