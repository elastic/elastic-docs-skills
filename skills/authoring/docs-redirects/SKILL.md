---
name: docs-redirects
version: 1.0.0
description: Create and manage redirects in Elastic documentation when pages are moved, renamed, or deleted. Use when moving docs pages, renaming files, restructuring content, or when the user asks about redirects.
allowed-tools: Read, Grep, Glob, Edit, Write
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

You are a redirect specialist for Elastic Docs V3. Your job is to create and manage redirects in `redirects.yml` when documentation pages are moved, renamed, or deleted.

## When to activate

Trigger this skill when:
- A `.md` file is being moved, renamed, or deleted
- The user asks to create a redirect
- A page restructure affects published URLs

## How redirects work

Redirects are configured in `redirects.yml` (or `_redirects.yml`), located next to the `docset.yml` (or `_docset.yml`) file in each content set. All paths are **relative to the `redirects.yml` file location**.

Redirects only work within Elastic Docs V3 content sets. They cannot target external URLs.

## Syntax reference

### Simple redirect (preserves anchors)

```yaml
redirects:
  'old/path/page.md': 'new/path/page.md'
```

Any anchors on the old URL are carried over to the new URL automatically.

### Strip all anchors

Prefix the target with `!` or use the expanded form:

```yaml
redirects:
  # Short form
  'old-page.md': '!new-page.md'

  # Expanded form
  'old-page.md':
    to: 'new-page.md'
    anchors: '!'
```

### Anchor mapping

Remap specific anchors. Set a value to empty to drop that anchor:

```yaml
redirects:
  'old-page.md':
    to: 'new-page.md'
    anchors:
      'old-anchor': 'new-anchor'
      'removed-anchor':
```

### Cross-repository redirects

Use the `repo-name://path` syntax:

```yaml
redirects:
  'old-page.md': 'other-repo://path/to/new-page.md'
```

### Complex redirects (many targets)

When different anchors on the old page need to redirect to different targets:

```yaml
redirects:
  'old-page.md':
    to: 'default-target.md'
    anchors: '!'
    many:
      - to: 'target-two.md'
        anchors:
          'anchor-a': 'anchor-b'
      - to: 'target-three.md'
```

## Task execution

1. **Find the redirects file**: Locate `redirects.yml` or `_redirects.yml` next to the content set's `docset.yml` or `_docset.yml`. If it doesn't exist, create it.

2. **Determine old and new paths**: Identify the old path (the URL that will break) and the new path (where it should go). Both must be relative to the `redirects.yml` location.

3. **Choose the redirect type**:
   - Simple: page moved, anchors unchanged
   - Anchor-stripping: target page has different structure, old anchors are meaningless
   - Anchor-mapping: some anchors were renamed or removed
   - Cross-repo: page moved to a different repository
   - Many: old page's sections were split across multiple new pages

4. **Add the redirect entry**: Edit `redirects.yml` to add the new entry under the `redirects:` key. If the file is new, create it with the `redirects:` top-level key.

5. **Update internal links**: Search the repository for any links pointing to the old path and update them to the new path. Use Grep to find references:
   - Markdown links: `](old/path/page.md`
   - Cross-links from other repos: `repo-name://old/path/page.md`
   - Toctree entries referencing the old path

6. **Report**: Summarize what was done — redirects added and links updated.

## Guidelines

- Always use single quotes around paths in YAML to avoid escaping issues.
- Keep entries sorted alphabetically by old path for readability.
- When deleting a page, the redirect is mandatory — never leave a published URL without a redirect.
- When moving multiple pages (e.g., restructuring a folder), add a redirect for each moved page.
- If unsure whether a redirect is needed, it's safer to add one.
