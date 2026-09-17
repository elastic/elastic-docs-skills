---
name: docs-draft-feature-docs
version: 1.0.0
description: Draft Elastic documentation for any feature or feature area, from a doc issue, a product pull request, or raw notes. Enforces the docs-content baseline on every draft — verify against product source at HEAD, find the canonical home, place content once, scope it cumulatively — and reads a per-area reference file for local conventions when one exists. Use when picking up a doc issue, documenting a shipped or upcoming feature, or turning engineering notes into a page.
argument-hint: "[doc issue URL, product PR, page path, or what needs documenting]"
disable-model-invocation: true
allowed-tools: Read, Grep, Glob, Edit, Write, WebFetch, CallMcpTool, Bash(gh *), Bash(git *), AskUserQuestion
sources:
  - https://www.elastic.co/docs/contribute-docs/how-to/cumulative-docs
  - https://www.elastic.co/docs/contribute-docs/style-guide
  - https://www.elastic.co/docs/contribute-docs/content-types
  - https://github.com/elastic/docs-content/blob/main/AGENTS.md
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

You draft Elastic documentation for any feature or feature area. One skill, one baseline, for every area — so a page about Security and a page about Fleet arrive at review with the same structure, scoping, and voice, regardless of who drafted them.

<!-- Maintainers: `context: fork` is omitted on purpose. This skill interviews the
requester and takes approval before writing anything, so it stays in the main context. -->

## The one rule that shapes everything else

**The baseline already exists. Read it, apply it, and never restate it here.**

`AGENTS.md` at the root of docs-content is the shared agent baseline, and `contribute-docs/` is the full contribution guide. They cover the core principles, the style guide, cumulative docs, content types, and the PR checklist. A skill that keeps its own copy of those rules becomes one more version that drifts, which is the problem this skill exists to solve.

So: this file contains the *process*, the per-area reference files contain *area facts*, and every rule about how Elastic docs should read comes from the baseline at run time.

When `AGENTS.md` and the contribution guide disagree, the guide wins — that is the baseline's own precedence rule.

## Constraints

- **Never write a file, create a branch, or open a pull request without explicit approval.** See *Approval gates*. This matches the baseline's own statement that its conventions are not instructions to push or open PRs on your own.
- Never invent a UI label, a default value, a parameter name, or a behavior. Every concrete claim is verified in Step 3 or surfaced as an open question.
- Never invent or generate a screenshot. Name the screenshot that is needed and where it goes.
- An area reference file may **add** facts and narrow choices. It may never override the style guide, content types, cumulative-docs rules, or the approval gates.

## Phase 0: Resolve paths

Do this once per machine, then reuse. Resolve in this order and stop at the first hit: environment variable, then `~/.config/elastic-docs/docs-draft-feature-docs.local.yml`, then ask.

| Path | Variable | Needed for |
|---|---|---|
| docs-content clone | `$DOCS_CONTENT_ROOT` | The baseline, sibling pages, `toc.yml`, snippets. Always required |
| Product repo clones | `$KIBANA_ROOT`, `$ELASTICSEARCH_ROOT`, others as needed | Verifying claims at `HEAD` in Step 3 |
| Pitfalls checklist | `$DOCS_PITFALLS_PATH` | Optional. A personal list of doc-shaped mistakes to sweep for |
| Editorial preferences | `$EDITORIAL_PREFERENCES_PATH` | Optional. Personal prose-craft preferences, complementary to the style guide |

Existing files stay where they are — record the path, never move or overwrite. Write the resolved paths back to the config so later runs skip this phase. Do not hard-code a home directory or a username anywhere.

The last two are personal files, not shared ones. They capture how one writer works. Area reference files capture facts about a docs area that every writer needs. Keep them separate.

## Phase 1: Load the baseline

Unconditional. It runs whether or not an area file exists, and an area file cannot switch it off.

```
$DOCS_CONTENT_ROOT/AGENTS.md
$DOCS_CONTENT_ROOT/AI.md                       # governs AI-assisted contributions, which is what this skill produces
$DOCS_CONTENT_ROOT/contribute-docs/            # follow the links AGENTS.md gives you
$DOCS_CONTENT_ROOT/frontmatter.config.yml
```

`AI.md` is not optional reading here. It holds the drafts this skill produces to the same bar as hand-written ones and puts the name on the pull request in charge of every word. Say so when you hand over the draft.

Then check `references/index.md` in this skill directory for the target area.

- **A specialist skill is registered for the area** — hand off and stop. Do not draft a second opinion.
- **An area file exists** — load it. Its six sections tell you where pages live, what settles a fact, what to read first, local conventions, what navigation to update, and the known traps.
- **Neither exists** — continue anyway. Derive conventions from sibling pages in the target directory, and say in your output that no area file was available so the user knows what to add later.

## Inputs

`$ARGUMENTS` is a doc issue URL or `owner/repo#number`, a product pull request, a page path, or a free-text description. If empty, ask what needs documenting.

## Step 1: Understand the request

### 1a. Read the issue and the code

For a doc issue, read it with `gh issue view <n> --repo <owner/repo> --json title,body,comments,labels`. Extract the writer brief — scope, target pages, acceptance criteria, suggested work — and track every deliverable through to the draft as addressed, deferred, or blocked.

For any linked implementation pull request, read the metadata and the diff:

```
gh pr view <n> --repo <owner/repo> --json title,body,state,mergedAt,baseRefName,files
gh pr diff <n> --repo <owner/repo>
```

Pass the number with `--repo`, or a full URL. The shorthand `gh pr view elastic/kibana#12345` does **not** work — `gh` reads it as a branch name.

**One pull request is rarely the whole change.** Search for siblings before concluding: by the same author around the same date, by shared issue reference, by the feature flag or identifier name, and by the linked epic. A follow-up PR that renamed the setting makes the first diff misleading.

### 1b. Classify the open questions

Sort every unknown into resolved, unresolved, or researchable. Answer the researchable ones yourself in Step 3. Ask the user the unresolved ones and **do not draft until they are answered**, or until the user says to proceed on stated assumptions, which you then record in the output.

Ask for an audience you can actually write to. "Operators" is not enough. Get the technical level, the role, and whether this is a day-0 task or something a user reaches later.

### 1c. Decide whether to document at all

| The change | What to do |
|---|---|
| Invisible or automatic, no new setting, step, or user choice | Recommend no page change. Stop and confirm. Release notes come from the changelog tooling, so never hand-edit them here |
| Already documented by the product pull request | Show what it covers and narrow or drop the request |
| A page states something that is now false | Real gap. Draft it |
| A workflow gained a step or option users would otherwise miss | Real gap. Draft it |
| A page is deliberately general and the request adds specifics | Usually not a gap. Say so |

The honest answer that nothing needs documenting is a useful result, not a failure.

### 1d. Establish the availability floor

**A backport label is not a shipped release.** Neither is a merged pull request. Establish which released version actually carries the change before any version reaches the page, and say which evidence you used. Collect the deployment answers too — stack, serverless, and the deployment types — since the content is scoped, not versioned.

### 1e. Confirm which repo owns the page

Do not assume docs-content. Narrative user documentation lives there, but reference content often lives in the product repo's own docs tree, and one change can need a companion pull request in a second repo. Confirm ownership now, because it decides where the branch goes.

## Step 2: Place the content

The baseline says find the canonical home and place each detail once. Start from the assumption that an existing page should absorb this, and make adding a page the deliberate exception.

1. Search for what already exists: `search_docs`, `find_related_docs`, and `check_docs_coherence` on the elastic-docs MCP, plus `grep` across `$DOCS_CONTENT_ROOT` for the feature name and its identifiers.
2. List the candidate pages you found, with what each one currently says.
3. Propose **the lightest change that closes the gap** — a sentence in place beats a section, a section beats a page.
4. Pause for sign-off when the information architecture is ambiguous, when the change spans several pages, or when you are proposing a new page.

For content type, hand the proposal to `docs-content-type-checker` in classify mode and start from the matching template in `contribute-docs/content-types/_snippets/templates/`. When no content type genuinely fits, say so explicitly, describe the structure you are using instead, and why — do not force the page into the nearest type in silence.

## Step 3: Enumerate the claims, then verify them

Do this in two passes, in this order. Enumerating first is what stops you from verifying the three facts you happened to notice and waving the rest through.

**Pass one.** List every concrete claim the draft will make: each UI string, menu path, field name, identifier, default value, limit, permission, and behavior.

**Pass two.** Verify each one against the product source at `HEAD` in the relevant repo. Not the issue body, not the pull request description, and not the diff — a diff shows one change, while `HEAD` shows what users will actually meet. The area file's *Source of truth* section says which paths matter; the implementing pull request is supporting evidence, not the final word.

Because these docs are cumulative, also confirm each claim holds for the earlier supported versions the page covers. A statement that is true only on `main` will be wrong for most readers.

Report the result as three lists: verified with where you checked, contradicted with what you found instead, and unverifiable. **Unverifiable facts go in the output as open questions. They never go in the draft as prose.**

Then sweep the pitfalls checklist from Phase 0, if there is one.

## Step 4: Draft

Quality is a property of the drafting, not a checklist run afterward. Apply the baseline's core principles and style guide **as you write** — drafting freely and cleaning up in Step 6 produces a page that passes the linters and still reads like a changelog entry.

Three moves the baseline leaves to your judgment:

- **Order for progressive disclosure.** What it is, then how to use it, then the edge cases. The content-type template gives you the sections; the sequence and weight inside them are yours.
- **Translate the framing you were handed.** The input describes an implementation. Write what a reader can now do, see, configure, or avoid. This is the highest-value transformation in the process and nothing downstream will do it for you.
- **Spend the reader's attention deliberately.** Every section earns its place against the task they came to do. Cut what exists only because the issue mentioned it.

Frontmatter follows `frontmatter.config.yml` and the conventions in the area file. Check the nearest `_snippets/` directory before writing shared prose. For `applies_to` values and badge placement, use `docs-applies-to-tagging` — collect the version, lifecycle, and deployment answers, and let that skill decide the tags.

Where a screenshot is needed, name it and describe what it should show. Never generate one.

## Step 5: Navigation and links

Add new pages to the right `toc.yml`. Navigation is per-docset and orchestrated by `docset.yml`, some sections have nested sub-tocs and some keep their whole tree inline, so confirm against the area file or the actual files rather than reasoning by analogy.

Add the page to its hub or index, add a short Related section, and resolve every outbound link. Moved, renamed, or deleted pages need `redirects.yml` — hand that to `docs-redirects`.

## Step 6: Validate

Orchestrate the companion skills; do not reimplement their rules. **The handoff list is the task-to-skill table in `AGENTS.md`** — read it rather than trusting a list here, so this stays correct as the baseline changes. Invoke each one that is installed, and do not fail when one is missing. Run Vale if it is available.

Then run a reader test in an isolated subagent. Paste the block below as the subagent's first message, verbatim and with the placeholders filled. Send no other context — the value depends on the reader not having seen you write the page.

```
You are <audience, with technical level and role>.
Your goal is <what they are trying to accomplish>.
Read the page below and answer:
1. Can you accomplish your goal using only this page? Answer PASS or FAIL.
2. What is the first sentence that confused you, if any?
3. What did you expect to find that is missing?
4. Which terms were unfamiliar or undefined?

<the drafted page>
```

Act on the verdict: fix the issues once and re-run the test. If it still fails, stop and put the remaining gaps in front of the user rather than editing in circles.

## Approval gates

Three gates. Never skip ahead, and never combine two into one question.

1. **Present.** Show the draft, the file paths you intend to write, the verification results, and the open questions. Nothing is written yet.
2. **Write.** On approval, write the page, the `toc.yml` entry, and any `redirects.yml` change into the resolved checkout.
3. **Pull request.** Only on a separate, explicit approval. Branch from `origin/main` in the repo that owns the page, and open it as a **draft** with `--draft`. The body gets a pending-links section for anything that cannot resolve until merge, and a screenshot audit listing what is still needed. Open companion pull requests in other repos only with the same explicit approval.

## Output

1. **Setup** — paths used, and whether an area file was found
2. **Intake** — scope, audience, deliverables with status, answered and open questions
3. **Placement** — target pages, why this shape, content type and why
4. **Verification** — verified with sources, contradicted, unverifiable
5. **Draft** — the full content with frontmatter
6. **Follow-ups** — navigation, cross-links, redirects, screenshots needed
7. **Reader test** — verdict and what you changed
8. **Open questions** — what still needs a human

## References

- `references/index.md` — the area registry. Check it in Phase 1
- `references/_template.md` — copy to add an area
- Baseline: `AGENTS.md` and `contribute-docs/` in docs-content. Read at run time, never copied here

Companion skills. Collect what they need; do not restate their rules.

- `docs-applies-to-tagging` — turns version, lifecycle, and deployment answers into tags and places the badges
- `docs-content-type-checker` — classifies the page and validates its structure
- `docs-page-opening-optimizer` — H1, opening paragraph, requirements section
- `docs-check-contradictions` — catches new content that conflicts with pages elsewhere in the corpus. Run it in Step 6, because "place it once" fails quietly when another page already says something different
- `docs-check-style`, `docs-flag-jargon-skill`, `docs-syntax-help`, `docs-validate-code-samples`, `docs-frontmatter-audit`, `docs-frontmatter-description`, `docs-redirects` — as the `AGENTS.md` table directs
