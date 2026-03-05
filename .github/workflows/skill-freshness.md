---
description: |
  Weekly check of all skills for staleness against their upstream source URLs.
  Compares each SKILL.md against the documentation it encodes and opens a PR
  if anything has drifted.

on:
  schedule: weekly
  workflow_dispatch:

permissions:
  contents: read
  pull-requests: read
  issues: read

network:
  allowed:
    - defaults
    - "www.elastic.co"
    - "docs-v3-preview.elastic.dev"

tools:
  github:
    lockdown: false
  web-fetch:
  edit:

safe-outputs:
  create-pull-request:
    title-prefix: "[skill-freshness] "
    labels: [automated, skill-freshness]
  add-comment:
  close-issue:
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

# Weekly Skill Freshness Check

Check all skills in `skills/**/SKILL.md` for staleness against their upstream source URLs.

## Process

1. Find every `SKILL.md` file under the `skills/` directory.
2. For each skill:
   - Read the SKILL.md file.
   - Identify every source URL in its reference/sources section.
   - When fetching a source URL, always append `.md` to the URL (e.g. `https://www.elastic.co/docs/contribute-docs/style-guide` becomes `https://www.elastic.co/docs/contribute-docs/style-guide.md`). The `.md` variant returns an LLM-friendly markdown version of the page.
   - Compare the fetched content against the rules, syntax, and options encoded in the skill.
   - If the skill is stale (new rules added, syntax changed, options removed, links broken), update the SKILL.md to reflect the current upstream state.
   - After updating a skill, run its evals to catch regressions (see "Post-update eval check" below).
3. If any files changed, open a pull request summarizing what drifted, why, and eval results.
4. If nothing changed, close this issue with a comment confirming all skills are current.

## Post-update eval check

After updating a skill, check whether `evals/evals.json` exists in the skill directory. If it does:

1. **Before editing**, read the original SKILL.md content and save it mentally as the "old version."
2. **After editing**, for each eval in `evals/evals.json`:
   - Read the eval prompt and expectations.
   - Follow the **updated** skill's instructions to accomplish the eval prompt.
   - Grade your output against each expectation (PASS/FAIL with evidence).
3. **Compare**: Note any expectations that the updated skill fails. If the update causes regressions (expectations that would have passed with the old version now fail), flag these in the PR body.
4. **Include results** in the PR body under a "### Eval results" section for each updated skill:

```markdown
### Eval results

#### <skill-name>
| Eval | Pass Rate | Regressions |
|------|-----------|-------------|
| 1 — <prompt summary> | 3/4 (75%) | None |
| 2 — <prompt summary> | 2/3 (67%) | ❌ "expectation text" — was passing before update |
```

If all evals pass, note "All evals passing" instead of the table.

If no evals exist for a skill, note "No evals available" and skip.
