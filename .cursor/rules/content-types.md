---
description: "Elastic docs content types: how-tos, overviews, tutorials, troubleshooting, and changelogs with templates and guidelines"
globs: ["**/*.md"]
alwaysApply: false
---

# Content Types

## How-To

Short set of instructions for a specific task. Think cooking recipe: focused, actionable, goal-oriented.

### Required Elements

- **Filename**: Use an action verb (e.g., `create-api-key.md`).
- **Frontmatter**: `applies_to`, `description`, `products`.
- **Title**: Start with a precise action verb ("Create an API key", "Configure TLS encryption").
- **Introduction**: 1-3 sentences explaining what the user will accomplish and why.
- **"Before you begin" section**: Prerequisites, permissions, required setup.
- **Numbered steps**: Clear, sequential instructions.
- **Success checkpoint**: How the user knows they succeeded.

### Recommended

- **Next steps**: What to do after completing the task.
- **Related pages**: Links to relevant content.

### Best Practices

- Focus on the user's goal, not the product's features.
- Write recipes, not lessons. Skip lengthy explanations.
- Keep each how-to focused on one task.
- Show alternatives where relevant (UI vs API).
- Test every step before publishing.

### Template

```markdown
---
applies_to:
  stack: ga
navigation_title: "Verb + object"
---

# Verb + object

Brief introduction explaining what this achieves and why it matters.

## Before you begin

- Prerequisite 1
- Prerequisite 2

## Verb + object

1. First step.
2. Second step.
3. Third step.

You've successfully [completed action]. You can now [next logical action].
```

## Overview

Conceptual information answering "What is it?", "How does it work?", and "Why does it matter?"

### Required Elements

- **Filename**: Descriptive noun or `index.md` for section landing pages.
- **Frontmatter**: `applies_to`, `description`, `products`.
- **Title**: Clear noun phrase ("Ingest pipelines", "Index lifecycle management").
- **Introduction**: What it is and why users should care.
- **Core content sections**: Organized with H2 headings.

### Recommended

- Use cases or examples.
- "How it works" section.
- Next steps and related pages.

### Best Practices

- Focus on a single concept.
- Lead with user value, not technical details.
- Use the inverted pyramid: most important information first.
- Keep content conceptual. Link to how-tos for procedures.
- Use concrete examples to illustrate abstract concepts.

### Template

```markdown
---
applies_to:
  stack: ga
---

# Concept name

Brief explanation of what this is and why it matters.

## How it works

Explanation of the core mechanism or architecture.

## Use cases

- Use case 1
- Use case 2

## Key concepts

### Sub-concept A

Details about sub-concept A.

### Sub-concept B

Details about sub-concept B.
```

## Tutorial

Comprehensive hands-on learning experience. Think of it as a chain of related how-tos with explanatory context.

### Required Elements

- **Filename**: End with `-tutorial.md` (e.g., `observability-tutorial.md`).
- **Frontmatter**: `applies_to`, `description`, `products`.
- **Title**: Descriptive ("Monitor Kubernetes with Elastic Observability").
- **Overview**: What the user will learn and build. Include learning objectives.
- **"Before you begin"**: Prerequisites, tools, and setup.
- **Instructional steps**: Detailed, sequential, with explanatory context.
- **Checkpoints**: Verify progress at key milestones.
- **Code annotations**: Explain code samples.
- **Next steps**: Where to go after completing the tutorial.

### Best Practices

- Focus on learning outcomes, not just task completion.
- Gradually introduce complexity.
- Provide context when introducing new concepts (unlike how-tos).
- Use realistic examples with real-world data.
- Include checkpoints so users can verify their progress.

### Template

```markdown
---
applies_to:
  stack: ga
---

# Tutorial: Descriptive title

In this tutorial, you'll learn to [outcome]. By the end, you'll have [tangible result].

## Before you begin

- Prerequisite 1
- Prerequisite 2

## Step 1: Set up the environment

Explanation of why this step matters.

1. First action.
2. Second action.

Verify: You should see [expected result].

## Step 2: Configure the integration

Context about what this step accomplishes.

1. First action.
2. Second action.

## Next steps

- [Related how-to](path/to/how-to.md)
- [Advanced topic](path/to/advanced.md)
```

## Troubleshooting

Help users fix specific problems they encounter.

### Required Elements

- **Filename**: Succinctly describe the problem (e.g., `cluster-health-red.md`).
- **Frontmatter**: `applies_to`, `description`, `products`.
- **Title**: Written from the user's perspective ("Cluster health status is red").
- **Symptoms section**: What the user observes (error messages, logs, behavior).
- **Resolution section**: Step-by-step fix.

### Best Practices

- One primary issue per page.
- Be explicit about which setups and versions are affected.
- Optimize for fast resolution: symptoms first, then fix.
- Don't use troubleshooting pages for teaching or explaining concepts.

### Template

```markdown
---
applies_to:
  stack: ga
---

# Problem description from user perspective

## Symptoms

Users may experience:

- Symptom 1 (error message or behavior)
- Symptom 2

## Resolution

1. Diagnostic step.
2. Fix step.
3. Verification step.
```

## Changelog

Describe product changes: features, enhancements, bug fixes, breaking changes, deprecations.

### Changelog Types

`breaking-change`, `bug-fix`, `deprecation`, `docs`, `enhancement`, `feature`, `known-issue`, `regression`, `security`

### Required Elements

- **products**: Which products are affected.
- **type**: One of the changelog types above.
- **title**: Max 80 characters. Use action verbs. Be user-focused.

### Optional Elements

- **description**: Max 600 characters.
- **impact**: For breaking changes and deprecations. What happens if the user takes no action.
- **action**: Steps users should take to adapt.

### Title Examples

- Good: "Add configurable retry limit for failed indexing requests"
- Bad: "Update retry logic" (too vague)
- Good: "Remove deprecated `_source` parameter from search API"
- Bad: "API cleanup" (not specific)

## Mixing Content Types

- Don't mix procedural and conceptual content heavily. Link between them instead.
- A how-to can have a brief intro paragraph but shouldn't become an overview.
- An overview can mention steps briefly but should link to the how-to for details.
