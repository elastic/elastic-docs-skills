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

# Contributing to Elastic Docs Skills

## Quick start

The fastest way to add a skill is to use the built-in command within this repo:

```
/create-skill my-new-skill
```

This walks you through the process interactively and can open a PR for you.

## Manual creation

### 1. Choose a category

| Category | Purpose | Examples |
|----------|---------|---------|
| `authoring` | Help write or edit documentation content | syntax help, redirects, tagging |
| `changelogs` | Work with changelog YAML, release notes, and changelog tooling | changelog review, changelog fixes, release notes |
| `project` | Support a specific documentation area or product workflow | Lens chart pages, Lens chart settings |
| `review` | Validate, lint, or check existing content | style checks, frontmatter audits, skill reviews |

If your skill doesn't fit an existing category, propose a new one in your PR description.

### 2. Create the skill directory

```
skills/<category>/<skill-name>/
  SKILL.md
```

The directory name must be kebab-case. Skill names must also be kebab-case, start with `docs-`, and be unique across the catalog.

### 3. Write the SKILL.md

Every skill needs YAML frontmatter followed by markdown instructions.

#### Required frontmatter

```yaml
---
name: docs-my-skill
version: 1.0.0
description: One-line description of what the skill does and when to trigger it.
---
```

#### Optional frontmatter

```yaml
argument-hint: <file-or-directory>    # Autocomplete hint (add if skill accepts input)
disable-model-invocation: true        # Only runs via /my-skill, not auto-triggered
context: fork                         # Run in an isolated subagent context
allowed-tools: Read, Grep, Glob       # Tools available without asking for permission
sources:                              # Upstream URLs this skill encodes
  - https://www.elastic.co/docs/...
```

#### Frontmatter guidelines

- **`context: fork`**: Use for catalog skills so they run in an isolated subagent context.
- **`allowed-tools`**: List only the tools the skill actually needs. Include `Edit` or `Write` only if the skill modifies files.
- **`sources`**: List every upstream documentation URL that the skill's rules are derived from. The weekly freshness checker uses these to detect drift.
- **`argument-hint`**: Add this whenever the skill accepts `$ARGUMENTS`. Use angle brackets for placeholders: `<file-or-directory>`.
- **`disable-model-invocation`**: Use for skills that should only run when explicitly invoked via `/skill-name`, not auto-triggered by Claude's judgment.

#### Markdown body

The body is the system prompt that drives the skill. Write it as instructions to Claude:

- Start with "You are a..." role statement
- Define inputs (`$ARGUMENTS`)
- Describe the step-by-step process
- Include examples and edge cases
- End with reference URLs (if the skill is derived from upstream docs)

### 4. Add evals (recommended)

Create `evals/evals.json` in your skill directory:

```json
{
  "skill_name": "my-skill",
  "evals": [
    {
      "id": 1,
      "prompt": "A realistic user prompt that exercises the skill",
      "expected_output": "Brief description of correct output",
      "expectations": [
        "Specific, testable assertion about the output",
        "Another assertion"
      ]
    }
  ]
}
```

#### Eval guidelines

- Write 3-5 evals covering common use cases and edge cases
- Each eval needs an `id`, `prompt`, and `expectations` array
- Expectations should be specific and independently verifiable
- `expected_output` is a human-readable summary; `expectations` are the grading criteria
- Evals run automatically on PRs that modify skills (via the `skill-eval-test` workflow)

### 5. Open a PR

CI will validate:

- SKILL.md has valid YAML frontmatter with required fields
- `name` is kebab-case, starts with `docs-`, and is unique across all skills
- `version` is valid SemVer
- `evals.json` (if present) has valid structure

## Versioning

Follow SemVer when editing existing skills:

- **PATCH** (1.0.0 -> 1.0.1): Bug fixes, wording improvements, updated URLs
- **MINOR** (1.0.0 -> 1.1.0): New capabilities, additional rules covered
- **MAJOR** (1.0.0 -> 2.0.0): Breaking changes to behavior, output format, or interface

## Avoiding contradictions

Before writing a new skill, check existing skills for overlapping scope:

- Read all skills in the same category
- Search for keywords from your skill's domain across all SKILL.md files
- If two skills could give conflicting advice, either merge them or clearly delineate their scopes in the descriptions

## gh-aw workflows

Agentic workflows live as `.md` files in `.github/workflows/`. They are compiled to `.lock.yml` files via `gh aw compile`. Rules:

- Edit the `.md` file, never the `.lock.yml`
- Run `gh aw compile .github/workflows/my-workflow.md` to regenerate the lock file
- Commit both the `.md` and `.lock.yml` together
