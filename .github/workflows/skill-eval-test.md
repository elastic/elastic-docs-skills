---
description: |
  Run eval test cases against skills changed in a PR. For each changed skill
  that has evals/evals.json, execute the test prompts with the skill and grade
  the outputs against expectations. Posts results as a PR comment.

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
    - "www.elastic.co"
    - "docs-v3-preview.elastic.dev"

tools:
  github:
    lockdown: false
  web-fetch:
  edit:

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

# Skill Eval Testing

Run eval test cases against skills changed in this PR and report results.

## Process

1. List files changed in this PR. Identify skills that were modified (any file under `skills/<category>/<skill-name>/`).
2. For each changed skill, check if `evals/evals.json` exists in the skill directory.
3. If evals exist, run the evaluation process below. If no evals exist, note it and skip.
4. Post a single comment on the PR with all results.

## Running evals

For each eval in `evals/evals.json`:

### Step 1: Read the skill

Read the skill's `SKILL.md` file completely. This is the skill you're testing.

### Step 2: Execute the eval prompt

Follow the skill's instructions to accomplish the eval prompt. Act as if you are a Claude Code agent with the skill loaded. Do your best to complete the task described in the prompt.

Save your output (the response you would give the user) to a workspace directory.

### Step 3: Grade against expectations

After completing the task, evaluate your own output against each expectation in the eval:

- **PASS**: Your output clearly satisfies the expectation with specific evidence
- **FAIL**: Your output does not satisfy the expectation, or you can't find evidence

Be honest and strict. The purpose is to catch regressions, not to rubber-stamp.

### Step 4: Compile results

For each eval, record:
- The prompt (truncated to first 100 chars)
- Pass/fail for each expectation
- Overall pass rate
- Any notable observations

## Comment format

Post a single comment with this structure:

```
## Skill Eval Results

### <skill-name>

| Eval | Prompt | Pass Rate | Details |
|------|--------|-----------|---------|
| 1 | <first 80 chars of prompt>... | 3/4 (75%) | ❌ expectation that failed |
| 2 | <first 80 chars of prompt>... | 4/4 (100%) | All passed |

**Overall**: X/Y expectations passed (Z%)

<Brief assessment of skill quality based on eval results>
```

If a skill has no evals:

```
### <skill-name>

⚠️ No evals found. Consider adding `evals/evals.json` with test cases.
```

## Important notes

- This is an advisory check — it does not block the PR.
- Focus on whether the skill's instructions lead to correct behavior, not on cosmetic issues.
- If an eval requires external resources (files, APIs) that aren't available, note it as "skipped — requires external resource" rather than failing.
- Do not modify any files in the repository.
