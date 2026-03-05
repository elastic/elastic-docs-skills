---
description: |
  Review skills changed in a PR for quality issues based on Claude Skills
  documentation and skill-validator criteria. Posts a PR comment with findings.

on:
  pull_request:
    paths: ['skills/**']

permissions:
  contents: read
  pull-requests: read
  issues: read

network:
  allowed:
    - defaults
    - "docs.anthropic.com"
    - "www.elastic.co"

tools:
  github:
    lockdown: false
  web-fetch:

safe-outputs:
  add-comment:
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

# Skill Quality Review

Review skills changed in this PR for quality issues and post a comment with findings.

## Process

1. List the files changed in this PR. Identify every `SKILL.md` under `skills/`.
2. For each changed skill, read the full `SKILL.md` file.
3. Evaluate the skill against the criteria below.
4. Post a single comment on the PR summarizing your findings across all changed skills. This is advisory only.

## Evaluation criteria

### Structure (from skill-validator)

- File starts with valid YAML frontmatter between `---` delimiters.
- Required frontmatter fields: `name`, `description`, `version`.
- `name` is kebab-case and matches the directory name.
- `version` is valid SemVer.
- No unclosed code fences in the markdown body.
- No broken internal links (references to files that don't exist in the skill directory).

### Content quality (from skill-validator)

- **Token efficiency**: The skill body should be under 500 lines. Longer skills should justify their length with proportionally more actionable content.
- **Code block ratio**: Code examples should be present but not dominate. A ratio above 0.4 suggests the skill may be a code dump rather than instructional content.
- **Imperative language**: Skills should use imperative voice ("Use X", "Add Y", "Check Z"). A very low imperative ratio (< 0.05) suggests the skill is descriptive rather than actionable.
- **Instruction specificity**: Rules and instructions should be specific enough to act on without ambiguity. Vague guidance like "follow best practices" is not useful.

### Clarity and actionability (from Claude Skills documentation)

- **Clear trigger**: The `description` field should make it obvious when to use the skill. It should describe both what the skill does and the situations that trigger it.
- **Scoped purpose**: The skill should do one thing well. If it tries to cover too many topics, it becomes harder for the agent to apply correctly.
- **Actionable instructions**: Every section should tell the agent what to do, not just describe concepts. Prefer concrete rules over abstract guidance.
- **Examples**: Non-trivial syntax or patterns should include examples. Examples should be minimal and focused — just enough to illustrate the point.
- **No redundancy with training data**: Skills are most valuable when they encode information the model doesn't already know — project-specific conventions, proprietary syntax, or domain rules. Restating widely-known information (standard markdown, common git commands) wastes tokens and can degrade output quality.

### Contamination awareness

- Code examples should be in the language relevant to the skill's domain. Mixing unrelated languages (e.g., Python examples in a markup-focused skill) can confuse the agent.
- If multiple languages are necessary, they should be clearly scoped to specific sections.

## Comment format

Post a single comment with this structure:

```
## Skill Quality Review

### <skill-name>

**Overall**: [Brief 1-sentence assessment]

**Strengths**:
- [What the skill does well]

**Issues** (if any):
- [Specific issue with actionable suggestion]

**Suggestions** (if any):
- [Optional improvements, not blockers]
```

If all skills look good, keep it short:

```
## Skill Quality Review

### <skill-name>

Looks good — clear trigger, actionable instructions, appropriate scope.
```

Do not nitpick formatting or stylistic preferences. Focus on issues that would affect the skill's effectiveness when used by an agent.
