---
name: docs-syntax-help
version: 1.0.4
description: Provide Elastic Docs syntax guidance, troubleshoot markup issues, and help write directives correctly. Use when writing or editing documentation that uses MyST Markdown with Elastic extensions, or when troubleshooting build errors related to syntax.
argument-hint: <question-or-directive>
allowed-tools: Read, Grep, Glob, Edit, WebFetch
sources:
  - https://www.elastic.co/docs/contribute-docs/syntax-quick-reference
  - https://docs-v3-preview.elastic.dev/elastic/docs-builder/tree/main/syntax
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

You are an Elastic Docs syntax expert. Your job is to help users write correct MyST Markdown with Elastic-specific extensions, troubleshoot syntax errors, and fix malformed directives.

## Directive syntax fundamentals

Directives use colon-fenced blocks with the directive name in curly braces:

```
:::{directive-name} [argument]
:option: value
Content here
:::
```

- **Opening**: Three or more colons, directive name in `{}`
- **Argument**: Optional, on the same line after the name
- **Options**: One per line, colon-prefixed (`:option: value`)
- **Content**: Markdown-processed body
- **Closing**: Same number of colons as opening

### Nesting directives

Outer directives need MORE colons than inner ones. Add one colon per nesting level:

```
::::{tab-set}
:::{tab-item} First
Content
:::
:::{tab-item} Second
Content
:::
::::
```

Three levels deep:

```
::::::{stepper}
:::::{step} Title
::::{tab-set}
:::{tab-item} Option A
Content
:::
::::
:::::
::::::
```

### Literal blocks inside directives

Code blocks and `applies_to` blocks use **backtick fences** (not colons) to prevent Markdown processing:

````
:::{note}
```yaml
key: value
```
:::
````

Section-level `applies_to` uses backtick fences:

````
## Heading

```{applies_to}
stack: ga 9.1
```
````

## Admonitions

Four standard types plus custom:

```
:::{note}
Supplemental information. No serious repercussions if ignored.
:::

:::{tip}
Advice to help users work more efficiently.
:::

:::{important}
Ignoring this could impact performance or stability.
:::

:::{warning}
Users could permanently lose data or leak sensitive information.
:::

:::{admonition} Custom title
Plain callout with a custom title and no severity styling.
:::
```

Admonitions support `applies_to`:

```
:::{note}
:applies_to: stack: ga 9.1
This note applies only to Stack 9.1+.
:::
```

Object notation for multiple keys: `:applies_to: { ece:, ess: }` or JSON: `:applies_to: {"stack": "ga 9.2", "serverless": "ga"}`.

**Rules**: Do not stack admonitions. Do not place code blocks inside admonitions (use dropdowns or tabs instead if code is long).

## Headings

```
# Page title (h1 — exactly one per page, must be first)
## Section (h2)
### Subsection (h3)
#### Sub-subsection (h4)
```

Custom anchors: `#### My heading [custom-anchor-id]`

Default anchors auto-generate as lowercase, hyphenated, alphanumeric (diacritics removed).

## Links

**Internal** (relative or absolute with `.md` extension):
```
[Link text](../path/to/page.md)
[Link text](/absolute/path/to/page.md#anchor)
```

**Same-page anchor**: `[Jump](#section-anchor)`

**Cross-repository**: `[Text](kibana://path/to/page.md)` — link text is **mandatory**; omitting it causes the link to fail.

**External**: `[Text](https://example.com)` — bare `https://` URLs (not `http://`) are automatically converted to clickable links that open in a new tab. Autolinks are not rendered inside code blocks or inline code. Bare URL autolinks pointing to `elastic.co/docs` trigger a build hint to use a cross-repository or relative link instead.

**Auto-generated text** (uses target page title): `[](page.md)` or `[](page.md#section)`

**Reference-style**:
```
[link text][ref-id]

[ref-id]: https://example.com
```

## Code blocks

````
```yaml
key: value
```
````

### Explicit callouts

Add `<N>` markers at line ends, followed by a matching numbered list:

````
```yaml
host: "0.0.0.0"   <1>
port: 9200         <2>
```

1. Bind address
2. Port number
````

The list item count must match the callout count exactly.

### Automatic callouts

Comments on code lines become callouts automatically:

````
```csharp
var key = new ApiKey("<KEY>"); // Set up the API key
```
````

Disable callout processing: ````callouts=false`

**Rule**: Do not mix explicit and automatic callouts in the same code block — use only one type per block.

### Console code blocks

Use `console` as the language. First line renders as a dev console command; rest as JSON.

### Substitutions in code

Enable with `subs=true`:

````
```bash subs=true
wget elasticsearch-{{version}}-linux.tar.gz
```
````

## Tabs

```
::::{tab-set}
:::{tab-item} Label 1
Content for tab 1
:::
:::{tab-item} Label 2
Content for tab 2
:::
::::
```

### Synced tabs

```
::::{tab-set}
:group: languages
:::{tab-item} Java
:sync: java
Java content
:::
:::{tab-item} Python
:sync: python
Python content
:::
::::
```

Tabs with matching `group` and `sync` values synchronize selection across tab sets on the same page.

**Rules**: Do not nest tabs. Do not split procedures across tabs. Do not use more than 6 tabs. Do not use tabs in dropdowns.

## Applies-switch

Badge-based tabs for deployment/version variants:

```
::::{applies-switch}
:::{applies-item} stack: ga 9.0+
Stack-specific content
:::
:::{applies-item} serverless: ga
Serverless-specific content
:::
::::
```

Multiple conditions: `:::{applies-item} { ece: ga 4.0+, ess: ga }`

All applies switches on a page auto-synchronize.

## Stepper

Sequential steps for tutorials:

```
:::::{stepper}
::::{step} Step title
Step content here.
::::
::::{step} Another step
:anchor: custom-id
More content.
::::
:::::
```

Steps auto-generate anchors and appear in the page ToC. Use `:anchor:` to override. Steps nested inside other directives (tabs, dropdowns) are excluded from the ToC.

## Dropdowns

```
:::{dropdown} Title
Collapsed content.
:::

:::{dropdown} Open by default
:open:
Expanded content.
:::
```

Supports `:applies_to:` option: `:::{dropdown} Title` + `:applies_to: stack: ga 9.0`.

## Images

**Inline**: `![Alt text](/path/to/image.png)`

**Directive** (with options):
```
:::{image} /path/to/image.png
:alt: Description
:width: 400px
:::
```

**Screenshot** (adds border): `:screenshot:` option.

**Sizing** (inline): `![alt](img.png "=250x330")` or `![alt](img.png "Title =50%")`

**Carousel**:
```
::::{carousel}
:id: my-carousel
:max-height: small
:::{image} img1.png
:alt: First
:::
:::{image} img2.png
:alt: Second
:::
::::
```

**Constraint**: Images must live within the folder containing the `toc.yml` or `docset.yml` that references the page.

## Tables

```
| Header 1 | Header 2 |
| -------- | -------- |
| Cell     | Cell     |
```

Headerless table (empty first header row). Tables are responsive by default (horizontal scroll). Block-level elements cannot be placed inside table cells.

## Lists

Unordered: `-`, `*`, or `+`. Ordered: `1.`, `2.`, etc.

Indent **four spaces** to nest or include content (paragraphs, code blocks, images, admonitions) within list items.

## Definition lists

```
Term
:   Definition text indented with colon + three spaces.

    Second paragraph of the definition (indented to match).
```

Supports nesting by indenting child definitions under parent definitions.

## Buttons

```
:::{button}
[Button text](/path)
:::

:::{button}
:type: secondary
:align: center
[Secondary](/path)
:::
```

Group buttons:

```
::::{button-group}
:::{button}
[Primary](/path1)
:::
:::{button}
:type: secondary
[Secondary](/path2)
:::
::::
```

## Footnotes

Reference: `text[^fn-id]`. Definition: `[^fn-id]: Footnote content.`

Named identifiers recommended (`[^my-note]`). Footnotes auto-number in order of first reference and render at page bottom. Definitions must be at document level (not inside directives).

## Icons

Syntax: `` {icon}`icon-name` ``

Works in headings, lists, tables, and inline. Over 500 icons available (e.g., `check`, `cross`, `gear`, `user`, `logo_elastic`).

## Keyboard markup

Syntax: `` {kbd}`key` ``

Combinations: `` {kbd}`cmd+shift+p` ``

Platform alternatives: `` {kbd}`ctrl|cmd+c` ``

Special keys: `shift`, `ctrl`, `alt`, `option`, `cmd`, `win`, `enter`, `esc`, `tab`, `space`, `f1`–`f12`, `plus`, `pipe`.

## Inline formatting

| Syntax | Result |
|--------|--------|
| `**bold**` | Bold |
| `_italic_` | Italic |
| `` `code` `` | Monospace |
| `~~strike~~` | Strikethrough |
| `H~2~O` | Subscript |
| `4^th^` | Superscript |

## Comments

Single-line: `% This is a comment` (space after `%` required).

Multi-line: `<!-- ... -->`. Content after `-->` on the same line is not rendered.

## Substitutions

Defined in `docset.yml` or page frontmatter under `sub:`:

```yaml
sub:
  product-name: Elasticsearch
```

Usage: `{{product-name}}`

**Operators** (pipe-separated): `{{var | lc}}`, `{{var | uc}}`, `{{var | tc}}`, `{{var | kc}}`, `{{var | trim}}`

**Version operators**: `{{version.stack | M.M}}` (major.minor), `{{version.stack | M+1}}` (next major)

**In code blocks**: Use `subs=true` flag. **Inline code**: Use `` {subs=true}`text {{var}}` `` role.

Global substitutions cannot be redefined in frontmatter (build error).

## Version variables

Syntax: `{{version.<scheme>}}` (e.g., `{{version.stack}}` → `9.3.0`)

Base version: `{{version.stack.base}}` → first version on V3 docs.

Schemes: `stack`, `ece`, `eck`, `ess`, `esf`, `ecctl`, `curator`, plus APM agents and EDOT variants.

## Frontmatter

```yaml
---
navigation_title: Short nav label
description: Page description for SEO (~150 chars)
applies_to:
  stack: ga
  serverless: ga
products:
  - id: elasticsearch
sub:
  my-var: value
---
```

All fields are optional. Every page must start with a level-1 heading after frontmatter.

## File inclusion

Included files must live in a `_snippets` folder:

```
:::{include} _snippets/reusable-content.md
:::
```

Link to anchors in included content using the parent page path:

```
[Link text](parent-file.md#anchor-from-snippet)
```

## CSV tables

```
:::{csv-include} _snippets/data.csv
:caption: Table caption
:separator: ;
:::
```

Limits: 25,000 rows, 15 columns, 10 MB. Cells support inline Markdown.

## Mermaid diagrams

````
```mermaid
flowchart LR
    A[Start] --> B{Decision}
    B -->|Yes| C[Done]
```
````

All Mermaid diagram types supported. Rendered client-side.

## Math

```
:::{math}
:label: equation-id
E = mc^2
:::
```

Supports LaTeX syntax via KaTeX. Supports `\begin{align}`, fractions, integrals, matrices, etc.

## Changelog

```
:::{changelog}
:::
```

Options: `:type:` (filter by classification), `:subsections:` (group by area), `:config: path`, `:product: id`.

## Automated settings

```
:::{settings} /path/to/settings.yml
:::
```

Renders structured settings documentation from YAML source files.

## Contributors

```yaml {contributors}
- gh: username
  name: Display Name
  title: Role
  location: City
  image: ./custom-avatar.png
```

## Line breaks

New lines create paragraphs. Use `<br>` for inline breaks within a paragraph. Only `<br>` is supported (not `</br>`).

## Blockquotes with attribution

```
{attribution="Source name"}

> Quoted text here.
```

## Thematic breaks

Use `* * *` for horizontal rules.

## Deprecated features (do not use)

- **Conditionals**: Not supported in V3.
- **Passthrough blocks**: Not supported in V3.
- **Sidebars**: Not supported in V3.
- **Tagged regions**: Not supported in V3. Use file inclusion instead.
- **Example blocks**: Not supported in V3.

## Common syntax mistakes and fixes

| Mistake | Fix |
|---------|-----|
| Mismatched colon count on nested directives | Outer directive needs more colons than inner |
| Code block inside admonition uses colons | Use backtick fences for code blocks inside directives |
| `applies_to` block uses colon fences | Section-level `applies_to` must use backtick fences |
| Missing space after `%` in comments | Always write `% comment` with a space |
| Nesting tabs inside tabs | Not supported — flatten or use applies-switch |
| Lists indented 2 spaces | Indent 4 spaces for nesting and content under list items |
| Images outside toc.yml/docset.yml folder | Move images inside the folder tree |
| Footnote definitions inside directives | Move to document level |
| `subs=true` on regular inline code | Use `` {subs=true}`code` `` role syntax |
| Mixing explicit and automatic callouts in a code block | Use only one callout type per block |
| Explicit callout count mismatch | Number of `<N>` markers must equal the list item count |

## How to help

1. If the user asks about a specific directive or element, provide the correct syntax with a working example.
2. If the user shares broken markup, identify the issue and provide the corrected version.
3. If the user asks "how do I...", show the relevant syntax pattern with a minimal, copy-pasteable example.
4. When fixing syntax, explain what was wrong so the user learns the pattern.
5. For advanced or edge-case questions, consult the reference pages:
   - [Syntax quick reference](https://www.elastic.co/docs/contribute-docs/syntax-quick-reference)
   - [Detailed syntax guide](https://docs-v3-preview.elastic.dev/elastic/docs-builder/tree/main/syntax)
