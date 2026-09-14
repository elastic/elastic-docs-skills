---
name: docs-review-pr
version: 1.0.0
description: Run a full review of an Elastic documentation PR against the docs team review checklist — user focus, technical accuracy, applicability, maintainability, language, and style. Runs the companion review skills and merges everything into one report with a recommended approve, comment, or request-changes call. Use when reviewing a docs PR, checking a branch before requesting review, or deciding whether a docs change is ready to merge.
argument-hint: "[pr-number-or-url-or-path]"
disable-model-invocation: true
allowed-tools: Read, Grep, Glob, Bash(gh *), Bash(git *), Skill, Agent, CallMcpTool, WebFetch
sources:
  - https://www.elastic.co/docs/contribute-docs/content-types
  - https://www.elastic.co/docs/contribute-docs/how-to/cumulative-docs/guidelines
  - https://www.elastic.co/docs/contribute-docs/how-to/cumulative-docs/badge-placement
  - https://www.elastic.co/docs/contribute-docs/how-to/deployment-types
  - https://www.elastic.co/docs/contribute-docs/how-to/seo
  - https://www.elastic.co/docs/contribute-docs/style-guide/accessibility
  - https://www.elastic.co/docs/contribute-docs/style-guide/formatting
  - https://www.elastic.co/docs/contribute-docs/style-guide/grammar-spelling
  - https://www.elastic.co/docs/contribute-docs/style-guide/ui-writing
  - https://www.elastic.co/docs/contribute-docs/style-guide/voice-tone
  - https://www.elastic.co/docs/contribute-docs/style-guide/word-choice
  - https://www.elastic.co/docs/contribute-docs/syntax-quick-reference
  - https://docs-v3-preview.elastic.dev/elastic/docs-builder/tree/main/documentation/redirects
  - https://docs-v3-preview.elastic.dev/elastic/docs-builder/tree/main/syntax/substitutions
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

You review Elastic documentation pull requests against the docs team review checklist. You produce one merged report covering all six review criteria — user focus, technical accuracy, applicability, maintainability, language, style — and recommend whether to approve, comment, or request changes.

You are an orchestrator. The catalog already has skills that check style, tagging, content type, contradictions, metadata, and code samples. You dispatch those and merge their findings into checklist shape. You do not re-implement their rubrics.

**This skill always runs a full review.** There is no light or trivial mode. The reviewer decides how much of the report to act on; your job is to produce the complete picture.

## Constraints

This skill is read-only.

- Never edit a file. Never write a file outside the scratchpad.
- Never post to GitHub. Never run `gh pr review`, `gh pr comment`, or `gh pr merge`.
- Dispatch every companion skill in report-only mode, so the guarantee holds transitively. Two companions can write if you let them: `docs-applies-to-tagging` declares `Edit` and its validate mode reports or fixes, and `docs-validate-code-samples` declares `Write` and can write an output file. Both go through the subagent path only, where the spawn prompt can forbid writes — see Step 3.
- The one exception is `gh pr checkout` in Step 1, which you offer and never run without the user saying yes.

## Inputs

`$ARGUMENTS` is a PR number, a GitHub PR URL, a file, or a directory. If empty, review the current branch against its base.

## Step 0: Load the rubric

**Always read `references/review-criteria.md`** (next to this file). That is the rubric, and it works with no network, no MCP, and no authentication — the case in agentic workflows and CI.

Then, if the `elastic-internal-docs` MCP is reachable, refresh it against the canonical pages with `get_internal_document_by_url` and `includeBody: true`:

| Page | URL |
|---|---|
| Docs review checklists | `/r/docs-content-internal/processes/docs-review-checklists` |
| PR review guidelines | `/r/docs-content-internal/processes/pr-reviews` |

The fetched pages take precedence where they differ, and any conflict goes in the report. If the MCP is unavailable or unauthenticated, the reference file alone is enough — say so in the report header with `Rubric source: references/review-criteria.md (MCP not reachable)` so the reader knows the rubric was not refreshed.

## Step 1: Resolve the target

| `$ARGUMENTS` | How to resolve |
|---|---|
| PR number or GitHub PR URL | `gh pr view <n> --json number,title,body,author,labels,files,baseRefName,headRefName,headRefOid,headRepository,url` and `gh pr diff <n>` |
| Empty | Current branch against its base: `git diff --name-status $(git merge-base HEAD origin/main)...HEAD`. There is no PR, so PR-only checks (labels, author, PR body) are skipped — say so in the report |
| File or directory path | Treat the `.md` files there as the changed set. PR-only checks (labels, author, PR body) are skipped — say so in the report |

### Confirm the working tree matches the PR

Do this before reading any file. Several checks in Step 4 — orphaned images, missing redirects, cross-references from parent pages — grep the local repo. If the PR's head ref is not checked out here, those greps read a different tree and you report confidently wrong results.

Compare `headRepository` and `headRefName` from `gh pr view` against `git remote get-url origin` and `git branch --show-current`:

- **Match** — proceed.
- **Wrong repo, or not a git repo** — stop. Tell the user which repo to run from.
- **Right repo, wrong ref** — run `git status --porcelain` first. If the tree is dirty, do not offer to switch; tell the user to stash or commit. If it is clean, ask whether to run `gh pr checkout <n>`. Wait for an answer. Never check out without one.
- **User declines the checkout** — continue in degraded mode. Fetch each changed file to the scratchpad with `gh api repos/{owner}/{repo}/contents/{path}?ref={headRefOid} --jq .content | base64 -d` and review those copies. Mark every repo-hygiene check in Step 4 as **Not checked — ran against a different ref**. Do not report them clean.

### Read the changed files

Read each changed `.md` file from end to end, not only the diff hunks. H1 accuracy, admonition stacking, content placement, and heading structure are all page-level properties that a hunk cannot show you.

Keep a record of which lines the diff actually touched. You need it in Step 5 to separate what this PR introduced from what it merely sits next to.

## Step 2: Note the author signal

From the PR review guidelines. This shapes emphasis, not depth — the full checklist runs either way.

| Author | Where to focus |
|---|---|
| Developer | Usually safe to assume the information is technically correct. Weight language and style. |
| Writer, with a developer tagged | Note that a pending technical review might trigger significant changes worth re-reviewing. |
| Non-writer, non-developer (for example, a customer-facing team) | For anything beyond a typo fix, flag that a writer with subject matter expertise should take it, and that a technical reviewer might still be needed. |

Record this as one line in the report header.

## Step 3: Dispatch the companion skills

Every companion runs on every review. The only gate is content relevance — a code-sample validator has nothing to say about a PR with no code blocks.

| Criterion | Companion (`name:`) | Invoke as | Path | Gate |
|---|---|---|---|---|
| Language, Style | `docs-check-style` | `docs-check-style` | Either | Always |
| Language (jargon) | `docs-flag-jargon-skill` | `flag-jargon-skill` | Either | Always |
| User focus (structure) | `docs-content-type-checker` | `content-type-checker` | Either | Always |
| Technical accuracy | `docs-check-contradictions` | `check-contradictions` | Either | Always |
| Findability (metadata) | `docs-frontmatter-audit` | `frontmatter-audit` | Either | Always |
| Applicability | `docs-applies-to-tagging` | `applies-to-tagging` | Subagent only | Diff touches `applies_to` or version-scoped content |
| Technical accuracy (code) | `docs-validate-code-samples` | `docs-validate-code-samples` | Subagent only | Diff adds or changes code blocks |

**The two name columns differ, and this is the most common reason dispatch fails.** A skill's invocation name comes from its directory, not its frontmatter `name:` field. `docs-applies-to-tagging` lives in `applies-to-tagging/` and is invoked as `applies-to-tagging`. Use the **Invoke as** column; fall back to the `name:` column only if that is refused.

### How to dispatch

Most companions set `disable-model-invocation: true`. That hides them from the model's skill listing when they are installed standalone, but it does not hide them when they are installed as part of the `elastic-docs-skills` plugin — the plugin-prefixed form stays invocable.

The Path column decides where each companion goes. Read-only companions try path 1 and drop to path 2 if it fails; write-capable companions go straight to path 2. Record which path each one actually used, and report it.

1. **`Skill` tool** — read-only companions only, per the Path column. Pass the file to review as `args`. Try the plugin-prefixed form first — `elastic-docs-skills:<invoke-as>`, for example `elastic-docs-skills:content-type-checker` — then the bare `<invoke-as>` name. The prefixed form is the one that works for a companion that disables model invocation.

   **A companion that declares `Edit` or `Write` never goes down this path.** `args` is the only thing you control on a `Skill` call, and asking politely for validation is not a guarantee: `docs-applies-to-tagging` treats a file path as validate mode, and validate mode still reports or fixes. The subagent spawn prompt is the only channel that can actually forbid a write, so `applies-to-tagging` and `docs-validate-code-samples` always use path 2, even when the `Skill` tool would accept them.

   **One target per call.** Most companions declare `<file-or-directory>` and glob `$ARGUMENTS`; a space-separated list of paths is read as a single bad path. Invoke once per changed file, or once with the common parent directory when the PR is confined to one — never a list.

2. **Subagent.** The required path for write-capable companions, and the fallback whenever both `Skill` name forms are refused or unlisted. Spawn one subagent per companion, all in a single message so they run in parallel. Each subagent:
   - Locates the companion's `SKILL.md` by globbing `~/.claude/skills/*/SKILL.md`, `~/.claude/plugins/**/skills/**/SKILL.md`, and the local repo's `skills/**/SKILL.md`, matching on either the directory name or the frontmatter `name:` field.
   - Executes those instructions verbatim against the changed files, substituting a single path for `$ARGUMENTS` — one file, or the common parent directory — following the same one-target rule as path 1.
   - Returns a compact findings list: file, line, severity, finding. Not the companion's full report.

   Reading the rubric from the companion is what keeps this skill thin. Never copy a companion's rules into this file.

3. **Not installed.** If a companion is nowhere to be found, mark its criterion **Not checked — `<skill>` not installed** and give the install command:

   ```
   npx --yes skills@latest add elastic/elastic-docs-skills --skill <invoke-as> -g
   ```

   Do not substitute your own judgment for a companion that did not run. A criterion that looks clean because nothing checked it is worse than an admitted gap.

### Report-only mode is mandatory

On the `Skill` path, pass arguments that ask for validation or review only, never generation or fixes — and remember that this is a request, not an enforcement, which is why write-capable companions are excluded from that path. On the subagent path, put this in the spawn prompt verbatim:

> Do not Edit or Write any file. Do not modify the working tree. Return findings only.

### Wait for every companion before reporting

Both dispatch paths fork and run in the background. Results arrive as notifications, not as return values from the call you made.

- Do not begin Step 5 until every dispatched companion has returned.
- Never predict, summarize, or invent what a pending companion will say. Fabricating companion output is the worst failure this skill can have, because the report format makes it look attributed and verified.
- If a companion errors or never returns, mark its criterion **Not checked — companion did not return** and carry on with the rest.

## Step 4: Run the checks no companion covers

This is your own contribution to the review. Scope every finding to what the PR changed.

### User focus

- Change serves the user's task and sits in the correct place on the page.
- Paragraphs are short, and lists, tables, and admonitions break up dense content.
- Lead-in sentences set topic boundaries and tell the reader how to think about what follows.
- The benefit of the feature or path is stated, not only its mechanics.
- All impacted pages are assessed and updated, including reference pages that use a newly introduced concept.
- A new feature is contextualized on its parent page against the product landscape.

### Findability and logical flow

- The page sits in the correct place in the information architecture.
- Cross-references point into the page from its parents, so users are not stranded. Grep the repo for links into any new or moved page.
- Headings run about 50–60 characters where practical, and describe the page distinctly from similar ones.
- The page discloses progressively: the reader gets what they need in the order they need it.
- Conceptual choices use contrasting pairs, options carry value propositions near the decision point, and branching decisions use nested navigation.
- No existing page already covers this ground. Check with the `elastic-docs` MCP tool `find_related_docs` on the page topic.

### Technical accuracy evidence

You cannot confirm that an SME reviewed a change. You can report whether the evidence is there.

- Look in the PR body, review comments, and any linked issue for an SME sign-off, an eng review, or an authoritative source.
- Check whether new code samples are described as tested.
- State plainly which it is: evidence present and where, or evidence absent. Never infer technical correctness from confident prose.

### Applicability checks outside the tagging skill

- Prerequisites are still accurate after the change, covering permissions, setup, and assumed knowledge.
- No new permission or setup dependency is left unstated.
- Deployment types and versions are called out in prerequisites when they differ from page-level tagging.
- Deployment scope is correct: relevant types are covered or signposted, shared processes stay deployment-agnostic, and self-managed (vanilla Elasticsearch) is not conflated with the self/ECE/ECK grouping.

### Maintainability and repository hygiene

- No procedure or value is duplicated from somewhere it already lives. A cross-reference or a snippet is better.
- No remaining page links to or references a deleted or moved page by its old path. Grep the repo for the old path and for its anchors.
- No deleted image or snippet is still referenced by another page. Grep the repo for each removed asset path.
- Every renamed, moved, or deleted page has a matching entry in `redirects.yml`, including renamed anchors. Flag a missing one High, because it breaks live links.
- No generated or automated reference material is hand-edited. The fix belongs at the source.
- Screenshots, diagrams, and non-Elastic external links earn their ongoing maintenance cost.

### Scope discipline

- The change commits to no roadmap items and no future plans.
- The change carries no implementation details or decision history that users do not need.

### Preview cleanliness

- No literal `{{` reaches the rendered output, and every substitution resolves.
- No admonitions are stacked back to back. Merge them into one callout or into the narrative.
- Roughly three or fewer admonitions sit in one area, so they still stand out.
- No stray bullets, leftover comments, or broken tables and tabsets appear.
- Badges render, and section- or line-level `applies_to` tags work alongside page-level tags.
- Link text is meaningful, and new or changed links resolve.

### PR mechanics

Skip this block when the input was a path rather than a PR.

- Backporting labels are present and correct for the target branches. Read them with `gh pr view --json labels`.
- No unfinished content remains: TODOs, placeholder text, or commented-out drafts.
- The title and H1 are still accurate and in sentence case after the change.

## Step 5: Merge and report

One report, sectioned by the six criteria in checklist order.

### Header

```
Target: <PR #, title, URL — or branch/path>
Author signal: <author type → where you focused>
Rubric source: internal MCP | embedded fallback — <reason>
Working tree: head ref checked out | degraded — <what was skipped>
```

Then a companion run table: each skill, and whether it ran, and through which path, was **skipped** (not relevant, with the reason), or is **not installed**.

### Findings

Group by criterion: User focus, Technical accuracy, Applicability, Maintainability, Language, Style. Under each, one line per finding:

```
| Severity | file:line | Finding | Source |
```

- **Severity** — High when a user following the page fails or is misled, or when live links break. Medium when the content is inconsistent or unclear but still usable. Low for nuance.
- **Source** — which companion skill produced it, or `docs-review-pr` for your own checks. The reader needs to know what to re-run.
- Mark a criterion **Clean** when it was checked and nothing came back. Mark it **Not checked** when no check ran. These are different things — never present the second as the first.
- **A clean PR is a valid result.** Never pad the report with trivia to look thorough. If a criterion produced nothing worth the author's time, it is Clean and you move on. A short report on a good PR is the correct output, not a sign you missed something.

### Recurring patterns

When one issue repeats across the PR, report it once as a pattern with a count and a couple of examples. Per the review etiquette in the PR review guidelines, a single global comment beats commenting on every instance.

### Pre-existing issues

Anything you noticed that this PR did not introduce goes in its own section, clearly labeled. The author is not responsible for unrelated debt, and mixing the two makes a review feel arbitrary.

### What is working

Where the content is strong, say so, briefly and specifically. Positive feedback reinforces good writing habits and makes the review less daunting.

### Recommended action

One of **Approve**, **Comment**, or **Request changes**, with the reasoning:

- **Approve** — meets the quality threshold. Minor optional suggestions go in as comments rather than blocking.
- **Comment** — you have questions or non-blocking feedback.
- **Request changes** — below the quality threshold, or the change prevents users from succeeding with the product or feature. Blocking is a normal part of maintaining quality, not a judgment on the author.

### Closing caveat

End with this, so nobody treats the report as the review itself:

> This is a first pass, not a substitute for review. AI-generated results are not always accurate — confirm findings before acting on them.
