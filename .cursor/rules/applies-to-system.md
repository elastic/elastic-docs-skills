---
description: "Elastic docs applies_to system: mark content for specific products, versions, deployment types, and lifecycle states"
globs: ["**/*.md"]
alwaysApply: false
---

# Applies-To System

The `applies_to` directive marks content for specific products, versions, deployment types, and lifecycle states. It controls badge display and content filtering.

## Three Dimensions

1. **Stack / Serverless**: `stack`, `serverless` (with sub-keys: `elasticsearch`, `observability`, `security`)
2. **Deployment**: `ece`, `eck`, `ess`, `self`, `serverless`
3. **Product**: `apm_agent_android`, `apm_agent_dotnet`, `apm_agent_go`, `apm_agent_ios`, `apm_agent_java`, `apm_agent_nodejs`, `apm_agent_php`, `apm_agent_python`, `apm_agent_ruby`, `apm_agent_rum`, `edot_collector`, `edot_dotnet`, `edot_java`, `edot_nodejs`, `edot_php`, `edot_python`, `edot_ios`, `edot_android`, `ecctl`, `curator`

## Lifecycle States

- `ga` — Generally available.
- `preview` — Early access, may change.
- `beta` — Feature complete, not production-ready.
- `deprecated` — Still works, will be removed.
- `removed` — No longer available.
- `unavailable` — Not applicable to this product/deployment.

## Version Syntax

- `x.x+` or `x.x` — From this version onward (e.g., `8.0+`, `8.0`).
- `x.x-y.y` — Version range (e.g., `8.0-8.5`).
- `=x.x` — Exact version only (e.g., `=8.0`).

## Page-Level (Frontmatter)

Every page should have a page-level `applies_to`. Use only one dimension at page level.

```yaml
---
applies_to:
  stack: ga 8.0+
  serverless: ga
---
```

Deployment-focused example:

```yaml
---
applies_to:
  serverless: ga
  ess: ga
  ece: ga 4.0+
  eck: ga 3.0+
---
```

Product-specific example:

```yaml
---
applies_to:
  edot_python: ga 1.0+
---
```

## Section-Level

Use triple backticks (not colons) for section-level applies_to. Place it directly after a heading:

````markdown
## My Section

```{applies_to}
stack: ga 9.0+
serverless: unavailable
```

Section content here.
````

With a custom anchor:

````markdown
## My Section [my-custom-anchor]

```{applies_to}
eck: ga 3.0+
```
````

## Inline-Level

For tagging individual elements within a paragraph:

```markdown
This feature {applies_to}`serverless: ga` is available in serverless.

This requires {applies_to}`stack: ga 9.1+` version 9.1 or later.
```

Multiple inline badges:

```markdown
{applies_to}`serverless: ga` {applies_to}`stack: ga 9.1+`
```

## Multiple Lifecycle States

Combine lifecycle states with automatic version inference:

```yaml
applies_to:
  stack: preview 9.0, ga 9.1
```

This is interpreted as: preview in exactly 9.0, GA from 9.1 onward.

More complex example:

```yaml
applies_to:
  stack: beta 9.1, ga 9.2, deprecated 9.5
```

## Applies-To in Components

### Admonitions

```markdown
:::{note}
:applies_to: stack: ga 9.0+
This note only applies to Stack 9.0+.
:::
```

### Dropdowns

```markdown
:::{dropdown} Deployment-specific configuration
:applies_to: ece: ga 4.0+
Content for ECE 4.0+.
:::
```

### Applies-Switch (Tabbed by Product/Version)

Use instead of regular tabs when content differs by product or deployment:

```markdown
::::{applies-switch}
:::{applies-item} stack: ga 9.1+
Stack-specific content.
:::
:::{applies-item} serverless: ga
Serverless-specific content.
:::
::::
```

All applies-switches on a page sync together automatically.

## Guidelines

### When to Tag

- Functionality was added in a specific version.
- A feature changed lifecycle state (GA → deprecated).
- Availability varies across products or deployments.

### When NOT to Tag

- Content-only changes (rewording, fixing typos).
- Every single paragraph (over-tagging reduces readability).
- Unversioned products with GA features (no badge needed).

### Placement Rules

- Page-level: Always include. Use one dimension only.
- Section-level: Place immediately after the heading.
- Inline-level: Place adjacent to the relevant text.
- Make badges visible but not disruptive. Don't break reading flow.
- Be consistent with placement within the same content type.

### Version Guidance

- Order versions newest first.
- Don't use version numbers in prose text; use `applies_to` badges instead.
- Don't use `applies_to` as a substitute for release notes.
- If content is not applicable, simply omit the key rather than marking it `unavailable` (use `unavailable` only when one section differs from the page-level scope).
