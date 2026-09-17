---
name: docs-draft-feature-docs
version: 2.5.0
description: Draft Elastic documentation for any feature or feature area, from a doc issue, a product pull request, or raw notes. Enforces the docs-content baseline on every draft — verify against product source at HEAD, find the canonical home, place content once, scope it cumulatively — and reads per-area reference files for local conventions when they exist. Use when picking up a doc issue, documenting a shipped or upcoming feature, or turning engineering notes into a page.
argument-hint: "[doc issue URL, product PR, page path, or what needs documenting]"
disable-model-invocation: true
allowed-tools: Read, Grep, Glob, Edit, Write, WebFetch, CallMcpTool, Skill, Agent, Bash(gh *), Bash(git *), Bash(date *), AskUserQuestion
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

You draft Elastic documentation for any feature or feature area. One skill and one baseline for every area, so that a page about Security and a page about Fleet arrive at review with the same structure, scoping, and voice.

<!-- Maintainers: `context: fork` is omitted on purpose. This skill interviews the
requester and takes approval before writing anything, so it stays in the main context. -->

## The baseline

**Read the baseline, apply it, and never restate it here.**

`AGENTS.md` at the root of docs-content is the shared agent baseline, and `contribute-docs/` is the full contribution guide. Between them they cover the core principles, the style guide, cumulative docs, content types, and the PR checklist. A skill that keeps its own copy of those rules becomes a second version that drifts from them.

So this file holds the *process*, the area reference files hold *area facts*, and every rule about how Elastic docs should read is loaded from the baseline at run time. When `AGENTS.md` and the contribution guide disagree, the guide wins — that is the baseline's own precedence rule.

## Where facts come from

Three sources, each answering something the other two cannot. Asking the wrong one produces a claim that looks verified and is not.

| Source | What it knows | What it cannot tell you |
|---|---|---|
| **`elastic-docs` MCP** at `https://www.elastic.co/docs/_mcp/`, no auth | Every published page: what exists, what it says, how it is structured, and what it relates to | Anything unpublished: `toc.yml`, `docset.yml`, `redirects.yml`, `_snippets/`, `hidden:` pages, or a page in an unmerged pull request |
| **Local checkouts** of docs-content and product repos | The files you are about to edit, plus navigation, redirects, and snippets | Nothing about the live site, and nothing about a repo you have not cloned |
| **Product source at `HEAD`** | UI strings, defaults, parameter names, limits, and behavior | Which release carries the change — see Step 4d |

**Find pages with the MCP rather than from a path list.** Do not encode a page inventory in this skill or in an area reference file when a search can find it and stay current. Area files record only what the MCP cannot answer: boundaries, product source paths, local conventions, navigation files, and known traps.

| MCP tool | Use it to |
|---|---|
| `search_docs` | Find published pages on the topic. This is the first move in Step 5, and the answer to "does this already exist?" |
| `find_related_docs` | Find the hub page, the siblings, and the cross-link targets around a topic |
| `get_document_by_url` | Read a candidate page. Pass `includeBody: true`, or you get headings and summaries only |
| `analyze_document_structure` | See a page's parent pages, which is how you place content in the hierarchy that already exists |
| `check_docs_coherence` | Check whether the topic is already covered coherently before adding to it |
| `find_docs_inconsistencies` | Find pages that already disagree with each other on this topic |

To get from a published page to the file that produces it, read the page with `get_document_by_url`, then find the file by its slug — `rg --files -g '*<slug>*' <repo>`. Do not infer the owning repo from the URL; Step 4e settles that.

If the MCP is not configured, WebFetch the same URLs with `.md` appended, which returns the whole page including its frontmatter. Check reachability with `npx @modelcontextprotocol/inspector --url https://www.elastic.co/docs/_mcp/`.

**That fallback replaces reading, not searching.** WebFetch needs a URL you already have, and nothing in the fallback answers "what pages exist on this topic." Step 5 loses its first move outright rather than running a narrower version of it, so the local greps in Step 5.2 become the only discovery you have, across only the repos you cloned. Say in the output that no corpus search ran, and **do not report "nothing covers this yet" as a finding** — you were not in a position to look. A corpus nobody searched is the likeliest way this skill ends up placing a second copy of a page that already exists.

## Constraints

- **Never write a file or open a pull request without explicit approval.** See *Approval gates*. This matches the baseline's own statement that its conventions are not instructions to push or open pull requests on your own. Creating the working branch in Step 3 is the one exception, because an empty local branch changes nothing and is reversible.
- **Never commit to, or write on, a default branch.** Step 3 puts you on a working branch before anything else happens.
- Never invent a UI label, a default value, a parameter name, or a behavior. Every concrete claim is verified in Step 6 or surfaced as an open question.
- Never invent or generate a screenshot. Name the screenshot that is needed and say where it goes.
- An area reference file may **add** facts and narrow choices. It may never override the style guide, content types, cumulative-docs rules, or the approval gates.

## Inputs

`$ARGUMENTS` is a doc issue URL or `owner/repo#number`, a product pull request, a page path, or a free-text description. If empty, ask what needs documenting.

## Step 1: Resolve paths

Do this once per machine, then reuse. Resolve in this order and stop at the first hit: environment variable, then `~/.config/elastic-docs/docs-draft-feature-docs.local.yml`, then ask.

The config file uses one key per row of the table below, named after the variable in lower snake case, so `$DOCS_CONTENT_ROOT` is `docs_content_root`. Use those exact keys when writing it back, so a later hand-edit and a first run agree:

```yaml
docs_content_root: /path/to/docs-content
kibana_root: /path/to/kibana
editorial_preferences_path: /path/to/preferences.md   # optional
docs_pitfalls_path: /path/to/pitfalls.md              # optional
```

| Path | Variable | Needed for |
|---|---|---|
| docs-content clone | `$DOCS_CONTENT_ROOT` | The baseline, navigation, snippets, and the files you edit. Always required |
| Product repo clones | `$KIBANA_ROOT`, `$ELASTICSEARCH_ROOT`, others as needed | Verifying claims at `HEAD` in Step 6, and **as the working tree** when the product repo owns the page |
| Pitfalls checklist | `$DOCS_PITFALLS_PATH` | Optional. A personal list of doc-shaped mistakes to sweep for |
| Editorial preferences | `$EDITORIAL_PREFERENCES_PATH` | Optional. Prose-craft preferences, complementary to the style guide. Consumed in Step 7. Can point at `references/ste-overlay.md` or at the writer's own file |

The last two rows are **per-writer, not per-area**. They tune how one person drafts, which is why they are opt-in and why the overlay that ships with this skill stays off until pointed at. Area reference files are the opposite: facts about a docs area that every writer needs, so Step 2 loads them automatically. Never move a preference into an area file, or an area fact into a preference file.

Existing files stay where they are — record the path, never move or overwrite. Write the resolved paths back to the config so later runs skip this step. Do not hard-code a home directory or a username anywhere.

A product repo plays one of two roles, and confusing them wastes a whole pass. Usually it is **read-only**: you verify claims there and write the page in docs-content. Sometimes it **owns the page** and is where the edit lands, because reference content often lives in the product repo's own `docs/` tree with its own `docset.yml`, `toc.yml`, and `redirects.yml`. Step 4e settles which, and a published URL is not evidence: `elastic.co/docs/reference/kibana/` publishes from `elastic/kibana`, not from docs-content.

## Step 2: Load the baseline and the area file

Loading the baseline is unconditional. It runs whether or not an area file exists, and an area file cannot switch it off.

```
$DOCS_CONTENT_ROOT/AGENTS.md
$DOCS_CONTENT_ROOT/AI.md                       # governs AI-assisted contributions, which is what this skill produces
$DOCS_CONTENT_ROOT/contribute-docs/            # follow the links AGENTS.md gives you
$DOCS_CONTENT_ROOT/frontmatter.config.yml
```

`AI.md` is not optional reading. It holds the drafts this skill produces to the same bar as hand-written ones and puts the name on the pull request in charge of every word. Say so when you hand over the draft.

Then check `references/index.md` in this skill directory for the target area.

Naming the area takes the request in hand, so skim `$ARGUMENTS` first — the title and body, when it is an issue. That skim is not Step 4: the full intake, the open questions, and the decision about whether to document at all still happen there, after the branch exists. Read just enough to know which file to open.

- **A specialist skill is registered for the area** — hand off and stop. Do not draft a second opinion.
- **An area file exists** — load it. It tells you the area's boundary, which product source settles a fact, the local conventions, which navigation file to edit, and the known traps. It does not list pages; use `search_docs` for that. Check its age and any `status:` entry before relying on it, as below.
- **Neither exists** — continue anyway. Derive conventions from sibling pages found through `find_related_docs`, and say in your output that no area file was available so the user knows what to add later.

A request can straddle two areas — two area files, or an area file and a specialist's territory. Split it: draft each part against the file that owns it, and delegate any specialist's part. Say which half went where, so nothing looks silently dropped.

Before routing to a specialist, confirm it is installed. Delegating to a skill that is not on the machine fails, and falling back to the area file or sibling pages beats stopping.

### How much to trust the area file

An area file is a snapshot, so check its age before relying on it. Read the frontmatter, get today's date with `date +%F`, and compare:

| `verified` is | The file's paths and labels are | So |
|---|---|---|
| Within 90 days | Current enough to act on | Use them, and still verify any concrete claim in Step 6 |
| Older than 90 days | Hints, not facts | Confirm each path and label against the repo or the MCP before you use it, and say in the output how old the file is |

Ninety days is roughly a release and a half. A file older than that predates at least one minor, which is long enough for a plugin directory to move. Report the age either way, so a reader of your output knows what the draft rested on.

**If the frontmatter carries a `status:` key, the area has an in-flight transition.** Read that entry in `references/status.md`, then resolve its tracking issues with `gh issue view <n> --repo elastic/docs-content-internal --json state,title,body`. The issue wins over the entry and the entry wins over the area file, because that is the order they go stale in. When the expiry condition has already been met — the issue is closed — say so and open a pull request to remove the entry rather than following it.

Never carry a date out of `status.md` into a draft. The entries name events rather than dates for exactly this reason, and a release date is `docs-applies-to-tagging`'s answer from the plugin config, not this skill's.

### What an area file cannot ask for

The precedence rule itself is in *Constraints*. What it does not spell out is which instructions trip it, because two kinds arrive dressed as local house style:

- **Formatting that contradicts the guide**, such as title-case headings where the guide says sentence case. Follow the guide.
- **Boilerplate**, meaning any convention that puts the same sentence, admonition, or requirement at the top of every page in the area. That is a "place each detail once" violation, and the style guide separately warns against loading a page with admonitions, so the convention usually fails twice. Work out what it is trying to achieve and do that properly instead: a version or deployment requirement is an `applies_to` badge, which `docs-applies-to-tagging` owns, and a caveat that matters everywhere belongs on the one page that owns the concept, with the others linking to it.

In both cases apply whatever the file legitimately adds, follow the baseline where they disagree, and tell the user which instruction you did not follow and why. **Do not apply an override silently.** An area file reads as authoritative precisely because it is usually right, which is what makes the rare bad instruction in one worth naming out loud.

## Step 3: Create the working branch

Create it before reading the issue, so no draft, edit, or `toc.yml` change can land on the default branch. Unlike a file write or a pull request, a new local branch is empty and reversible, so this is not gated — but report what you created and what you based it on.

**Follow `references/branch-setup.md` for the commands.** The four rules it enforces:

- **Resolve the canonical remote by URL**, matching `github.com/elastic/`, rather than trusting the name `origin`. On a fork, `origin/main` is the writer's own stale copy, and basing on it starts the work from old content with nothing looking wrong.
- **Resolve the default branch** off that remote instead of assuming `main`, and base on the remote-tracking ref rather than the local branch of the same name.
- **Stop and ask** on an uncommitted tree, a non-default branch, or a detached HEAD. Never stash, reset, or discard anything to clear the way.
- **Pass `--no-track`** when creating the branch, so a stray `git pull` cannot merge the default branch into the work.

Do this in `$DOCS_CONTENT_ROOT` now. When Step 4e names a second repo, branch there at that point the same way. If the run ends without writing anything — Step 4c concluded no docs are needed, or the user declined at gate 1 — switch back and delete the branch.

## Step 4: Understand the request

### 4a. Read the issue and the code

For a doc issue, read it with `gh issue view <n> --repo <owner/repo> --json title,body,comments,labels`. Extract the writer brief — scope, target pages, acceptance criteria, suggested work — and track every deliverable through to the draft as addressed, deferred, or blocked.

For any linked implementation pull request, read the metadata and the diff:

```
gh pr view <n> --repo <owner/repo> --json title,body,state,mergedAt,baseRefName,files
gh pr diff <n> --repo <owner/repo>
```

Pass the number with `--repo`, or a full URL. The shorthand `gh pr view elastic/kibana#12345` does **not** work — `gh` reads it as a branch name.

**One pull request is rarely the whole change.** Search for siblings before concluding: by the same author around the same date, by shared issue reference, by the feature flag or identifier name, and by the linked epic. A follow-up pull request that renamed the setting makes the first diff misleading.

### 4b. Classify the open questions

Sort every unknown into resolved, unresolved, or researchable. Answer the researchable ones yourself in Step 6. Ask the user the unresolved ones and **do not draft until they are answered**, or until the user says to proceed on stated assumptions, which you then record in the output.

Ask for an audience you can actually write to. "Operators" is not enough. Get the technical level, the role, and whether this is a day-0 task or something a user reaches later.

### 4c. Decide whether to document at all

| The change | What to do |
|---|---|
| Invisible or automatic, no new setting, step, or user choice | Recommend no page change. Stop and confirm. Release notes come from the changelog tooling, so never hand-edit them here |
| Already documented by the product pull request | Show what it covers and narrow or drop the request |
| A page states something that is now false | Real gap. Draft it |
| A workflow gained a step or option users would otherwise miss | Real gap. Draft it |
| A page is deliberately general and the request adds specifics | Usually not a gap. Say so |
| A page documents something the current version removed | Real gap, but not a deletion. Scope it — see below |

Concluding that nothing needs documenting is a valid result. Report it and stop rather than finding something to write.

**"Remove X" is a scoping request, not a deletion.** When a feature, field, or setting goes away, the content usually stays — the docs are cumulative, and readers on the versions that still have it still need it. Keep the content and add a `removed` tag, which `docs-applies-to-tagging` owns.

The removal scenarios name two cases where the content can go instead: the feature was only ever beta or technical preview, or it only ever existed in an unversioned product. Both are permissions rather than instructions, so scoping is never the wrong answer and deleting sometimes is. Check the case against those scenarios rather than inferring it, and when the feature's lifecycle is not one they name — `experimental`, for instance — scope it and say which reading you took, rather than deleting on an analogy you made yourself.

This is the request shape where doing literally what the issue asks is most often wrong. "Remove the tags section" describes the product change, not the edit to make, and deleting the section produces a clean-looking pull request that quietly takes documentation away from readers on supported versions.

### 4d. Establish the availability floor

**A backport label is not a shipped release.** Neither is a merged pull request. Establish which released version actually carries the change before any version reaches the page, and say which evidence you used. Collect the deployment answers too — stack, serverless, and the deployment types — since the content is scoped, not versioned.

**The code declares the lifecycle; the request only describes it.** When a registration carries a stability or maturity field, that field is the answer and it outranks how the request reads — a release-note label, a bare version number, and "on by default" each describe something that shipped, and none of them mean generally available. Read the declared value and pass it to `docs-applies-to-tagging` rather than mapping it yourself.

**Availability given as a patch release is a question, not a value.** A patch number does not reach the page as written, and resolving it sometimes removes the need for a tag entirely, so hand it over rather than deciding.

### 4e. Confirm which repos own the work

Do not assume docs-content, and do not assume a single owner. Narrative user documentation lives there, but reference content often lives in the product repo's own docs tree, so **one request routinely splits across two repos** — a Workflows change can need authoring content in docs-content, a setting in `kibana/docs/reference/`, and a connector page in the same Kibana tree.

Split it the way Step 2 splits a request across two areas: assign each deliverable to the repo that owns it, and say which half went where so nothing looks silently dropped. Then run Step 3 in each newly named repo, resolving its canonical remote and base separately.

Then order the halves, because this decides more than where the branch goes:

- **A page in repo A links to a page you are adding in repo B**, so B merges and publishes first. Otherwise A ships a link to a target that does not exist yet. Cross-repo links do not resolve against your local checkout, so nothing local will catch it.
- **Neither side links to new content in the other**, so the order is free and they can go in parallel.

State the order and the reason at the first approval gate. When the order forces a wait, say so plainly — the second pull request is blocked until the first publishes, not merely until it merges.

## Step 5: Place the content

The baseline says find the canonical home and place each detail once. Start from the assumption that an existing page should absorb this, and make adding a page the deliberate exception.

1. **Search the published corpus first**, with `search_docs` on the feature name and on the reader's task, then `find_related_docs` for the hub and siblings, then `check_docs_coherence` on the topic. Read the best candidates with `get_document_by_url` and `includeBody: true`, and use `analyze_document_structure` to see what each one's parents are.
2. **Then grep the local trees** for the feature name and its identifiers, in `$DOCS_CONTENT_ROOT` **and the docs tree of every product repo Step 4e named**. This catches what the MCP cannot see: pages that are `hidden:`, unpublished, or in flight. A grep limited to docs-content cannot see `kibana/docs/`, so it reports a gap that is already filled and you place a second copy.
3. List the candidate pages you found, with what each one currently says and its URL or path.
4. Propose **the lightest change that closes the gap**: a sentence in place, then a section, then a new page, in that order of preference.
5. Pause for sign-off when the information architecture is ambiguous, when the change spans several pages, or when you are proposing a new page.

For content type, hand the proposal to `docs-content-type-checker` in classify mode and start from the matching template in `contribute-docs/content-types/_snippets/templates/`. That directory carries how-to, overview, troubleshooting, and tutorial; changelog has no template there, so work from the content-type guide itself for those rather than bending one of the four. When no content type genuinely fits, say so explicitly, describe the structure you are using instead, and why — do not force the page into the nearest type in silence.

## Step 6: Enumerate the claims, then verify them

Do this in two passes, in this order. Enumerate first, or you verify the few facts you happened to notice and wave the rest through.

**Pass one.** List every concrete claim the draft will make: each UI string, menu path, field name, identifier, default value, limit, permission, and behavior.

**Pass two.** Verify each one against the product source at `HEAD` in the relevant repo. Not the issue body, not the pull request description, and not the diff — a diff shows one change, while `HEAD` shows what users will actually meet. The area file's *Source of truth* section says which paths matter; the implementing pull request is supporting evidence, not the final word.

**Confirm the clone is current before trusting it.** Fetch the product repo's remote-tracking ref and compare its date against the merge date of the implementing pull request. A clone a few days behind reports removed code as still present and new code as missing, and it does so silently — a confident wrong answer with nothing to flag. If it is behind the change you are verifying, fetch it or read the file through the GitHub API at `?ref=main`.

**Verify the integration, not just the component.** A feature built on a shared package inherits everything that package documents, but the host app decides which capabilities are switched on. Check the call sites and the options the host passes. A capability the package ships and the host leaves disabled will otherwise read as verified.

Because these docs are cumulative, also confirm each claim holds for the earlier supported versions the page covers. A statement that is true only on `main` will be wrong for most readers.

Report the result as three lists: verified with where you checked, contradicted with what you found instead, and unverifiable. **Unverifiable facts go in the output as open questions. They never go in the draft as prose.**

Then sweep the pitfalls checklist from Step 1, if there is one.

## Step 7: Draft

Apply the baseline's core principles and style guide **as you write**. Drafting freely and cleaning up in Step 9 produces a page that passes the linters and still reads like a changelog entry. The rubric your draft will be measured against in Step 9 is the review checklist in `docs-review-pr`, at `references/review-criteria.md` in that skill — read it if you want to know what the reviewer will look for.

Three moves the baseline leaves to your judgment:

- **Order for progressive disclosure.** What it is, then how to use it, then the edge cases. The content-type template gives you the sections; the sequence and weight inside them are yours.
- **Translate the framing you were handed.** The input describes an implementation. Write what a reader can now do, see, configure, or avoid. Nothing downstream will do this for you.
- **Cut what does not serve the reader's task**, including anything that exists only because the issue mentioned it.

If `$EDITORIAL_PREFERENCES_PATH` resolved in Step 1, read that file now and apply it to the prose you write. It is additive prose craft, so it never overrides the style guide, content types, or an area file — where it conflicts with the baseline, the baseline wins, and say so rather than silently following the preference. Apply it only to new prose: do not restyle surrounding copy you were not otherwise changing. An optional Simplified Technical English overlay ships at `references/ste-overlay.md`; it stays off unless the variable points at it.

Frontmatter follows `frontmatter.config.yml` and the conventions in the area file. Check the nearest `_snippets/` directory before writing shared prose. For `applies_to` values and badge placement, use `docs-applies-to-tagging` — collect the version, lifecycle, and deployment answers, and let that skill decide the tags, including whether the page needs any.

Where a screenshot is needed, name it and describe what it should show. Never generate one.

## Step 8: Navigation and links

Add new pages to the right `toc.yml`. Navigation is per-docset and orchestrated by `docset.yml`, some sections have nested sub-tocs and some keep their whole tree inline, so confirm against the area file or the actual files rather than reasoning by analogy. The MCP cannot help here — navigation is not published. When the work spans repos, each repo has its own `toc.yml`, `docset.yml`, and `redirects.yml`, so update the one in the repo you are editing.

Add the page to its hub or index, add a short Related section, and resolve every outbound link with `get_document_by_url`. Moved, renamed, or deleted pages need `redirects.yml` — hand that to `docs-redirects`.

**One class of link cannot resolve yet, and that is expected.** A cross-repo link to a page you are adding in the other repo has no target until that pull request publishes. Do not treat it as broken, and do not drop it or point it at a placeholder. List it as a pending cross-repo link, name the pull request it waits on, and carry it into the ordering from Step 4e. Every other unresolved link is a real defect.

## Step 9: Validate

Two passes, because the draft and the branch are checkable in different ways. Orchestrate the skills below; never reimplement their rules.

### 9a. Check the draft, before gate 1

Invoke each of these on the draft. Run the ones that apply, and do not fail when one is not installed — report it as not checked instead.

| Skill | What it decides | Run it when |
|---|---|---|
| `docs-content-type-checker` | Which content type the page is, and whether its structure matches | Always. Also used in classify mode in Step 5 |
| `docs-applies-to-tagging` | Whether the content needs scoping at all, the `applies_to` values, and where the badges go | The page is version- or deployment-scoped, which is almost always |
| `docs-page-opening-optimizer` | The H1, the opening paragraph, and the requirements section | Always, for a new page or a rewritten opening |
| `docs-check-style` | Style guide compliance, and runs Vale when it is available | Always |
| `docs-flag-jargon-skill` | Jargon and unexplained terms | Always |
| `docs-check-contradictions` | New content that conflicts with pages elsewhere in the corpus | Always. "Place it once" fails quietly when another page already says something different |
| `docs-syntax-help` | MyST and Elastic directive syntax | The draft uses admonitions, tabs, applies-switches, includes, or settings directives |
| `docs-validate-code-samples` | Whether code and YAML samples are valid and runnable | The draft contains a code block |
| `docs-frontmatter-description` | The `description` field, for search | Always |
| `docs-frontmatter-audit` | The rest of the frontmatter against the repo schema | Always |
| `docs-redirects` | The `redirects.yml` entries for anything moved, renamed, or deleted | Step 8 moved, renamed, or deleted a page |

**How to invoke one.** Use the `Skill` tool with the plugin-prefixed frontmatter name, `elastic-docs-skills:docs-check-style`, and fall back to the bare name if the prefixed form is refused. About half set `disable-model-invocation: true`, and the prefixed form is what reaches those. If both name forms are refused, spawn a subagent that locates the skill's `SKILL.md` under `~/.claude/skills/*/`, `~/.claude/plugins/**/skills/**/`, or the local `skills/**/` tree and follows it verbatim. Names above are frontmatter names, which is what invocation needs; directory names differ and are only for finding files on disk.

**Read the target skill's own `argument-hint` before calling it.** Most take one file or directory and glob `$ARGUMENTS`, so a space-separated list of targets reads as a single bad path — pass one target per call. Three break that shape: `docs-redirects` needs an old path *and* a new one, `docs-syntax-help` takes a question rather than a file, and `docs-validate-code-samples` accepts flags after its target. Handing a lone file path to those either errors or quietly checks the wrong thing, which looks the same as passing in the output.

If `AGENTS.md` names a task-to-skill mapping that is not in this table, run that one too, and open a pull request here to add the row.

### 9b. Read the draft as its audience

Run a reader test in an isolated subagent. Paste the block below as the subagent's first message, verbatim and with the placeholders filled. Send no other context, because the value depends on the reader not having seen you write the page.

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

### 9c. Review the branch, after gate 2 and before gate 3

Once the files are written, run `docs-review-pr` against the branch — with no argument, it reviews the current branch against its base. It returns the docs team review checklist with an approve, comment, or request-changes call, and it is read-only, so it cannot undo the write.

**Fetch first, and compare against the merge base** — `git diff <base>...HEAD`, three dots, not two. Two dots compare the branch tip to the base tip, so everything the base gained since you branched reads as a file you changed. One commit of drift is enough to bury the files you actually touched in unrelated ones, and the review then spends its attention on those. When the branch is behind, say so rather than reviewing through the noise.

This re-runs most of the 9a table against real files rather than a draft in the conversation, which is where frontmatter, includes, and link resolution actually get exercised. It does not cover `docs-page-opening-optimizer`, `docs-syntax-help`, `docs-frontmatter-description`, or `docs-redirects`, so 9a is still the only pass those get.

Fix what it raises, then go to gate 3. Report its recommendation in the output: opening a pull request that your own pre-review would have blocked wastes the reviewer's first pass. When it is not installed, say so and note that the checklist review did not run.

## Step 10: Draft the pull request description

Compose it now, before gate 3, so the user approves the description along with the pull request. **Derive it from work already done** — Step 5's placement decision, Step 6's verification, Step 7's screenshot audit, Step 8's pending links, Step 9's review. Do not re-gather anything.

Read the template in the repo you are opening against, at `.github/PULL_REQUEST_TEMPLATE.md`, and fill its sections. Each repo has its own, so read the one that applies rather than reusing the last. Never invent or drop a template section.

**Write it for the reviewer's decision.** They need to know what changed, where, and what to check, in plain language and short enough to read before opening the diff. A description that restates the page content wastes the reviewer's time.

- **Summary.** One paragraph, usually three sentences. What a reader can now do, in user terms rather than implementation terms. Any migration or compatibility fact a reviewer would otherwise flag, such as a feature replacing an older one while the old behavior keeps working. Then the placement decision and its reason — "to avoid duplicating this across pages, X now links to the canonical reference instead of repeating it" — because that is the judgment call most likely to be questioned. Close with `Fixes #<issue>.`, or say why there is no issue.
- **One bullet per changed page**, under a `## Previews` heading. Name the page, then say what changed on it and why, so a reviewer knows what to look at on each. Note version scoping where it applies, since cumulative docs are easy to review wrongly. This heading is a convention rather than part of the template, and it is the section reviewers use most.
- **A short note for anything deliberately incomplete.** Pending cross-repo or cross-pull-request links from Step 8, a missing anchor that lands elsewhere, a screenshot still needed. Name what unblocks each one, rather than letting a reviewer find it.
- **The generative AI disclosure**, answered honestly with the tool and model, because this skill drafted the content. `AI.md` governs this, and the name on the pull request is accountable for every word.

Do not fabricate preview URLs. Previews build automatically once the pull request exists and a bot posts the links, so write the bullets now and let the links arrive with the build.

For the title, follow the convention in the target repo's recent merged history rather than inventing a format — in docs-content that is area tags then an imperative, as in `[Observability/Kibana][Alerting] Document per-alert snooze`. Check with `gh pr list --repo <owner/repo> --state merged --limit 10`.

When the work spans repos, each pull request gets its own description written to its own repo's template, and each one says that the other exists.

## Approval gates

Three gates. Never skip ahead, and never bundle two approvals into one question, including one gate-3 approval per repo.

1. **Present.** Show the draft, the file paths you intend to write, the verification results, the Step 9a and 9b results, and the open questions. When the work spans repos, show the per-repo split and the order from Step 4e here.
2. **Write.** On approval, write the page, the `toc.yml` entry, and any `redirects.yml` change onto the Step 3 branch. Confirm you are on it first, rather than assuming — a gate 1 that ran long is enough time for a branch to change underneath you. Writing to a second repo is part of this gate only if its split was presented at gate 1. Then run Step 9c.
3. **Pull request.** Only on a separate, explicit approval, and show the Step 10 description and the Step 9c recommendation as part of asking. The branch already exists from Step 3, so push it and open the pull request as a **draft**, using the approved description as the body. `references/branch-setup.md` has the push recipe, including the fork case.

Open the pull requests in the Step 4e order, and cross-reference them in both bodies so a reviewer seeing one knows the other exists. Do not open the blocked one early: it cannot pass its own link check until the first publishes.

## Output

1. **Setup** — paths used, whether the MCP was reachable, the branch created in each repo with its base and whether that checkout is a fork, and which area file was found with its age and any `status.md` entry you resolved
2. **Intake** — scope, audience, deliverables with status, answered and open questions
3. **Placement** — target pages, why this shape, content type and why
4. **Verification** — verified with sources, contradicted, unverifiable
5. **Draft** — the full content with frontmatter
6. **Follow-ups** — navigation, cross-links, redirects, screenshots needed
7. **Validation** — which skills ran, which were not installed, the reader test verdict, and what you changed
8. **Pull request** — the drafted title and description, ready to paste
9. **Open questions** — what still needs a human

When the work spans repos, group sections 3, 5, 6, and 8 by repo rather than merging them into one list, and lead the output with the split and the merge order. A reader who cannot tell which file lands in which repo cannot review either half.

## References

- `references/index.md` — the area registry. Check it in Step 2
- `references/status.md` — every in-flight transition, each with an expiry condition to resolve rather than a date to trust. Read it when an area file's frontmatter names it
- `references/branch-setup.md` — the git recipe for Step 3 and for the gate-3 push
- `references/_template.md` — copy to add an area. It states what belongs in an area file, what the MCP should answer instead, and the rules that keep a file from going stale
- `references/ste-overlay.md` — optional Simplified Technical English prose overlay. Opt in through `$EDITORIAL_PREFERENCES_PATH`; not loaded by default
- Baseline: `AGENTS.md` and `contribute-docs/` in docs-content. Read at run time, never copied here
- Companion skills: the table in Step 9a. Collect what they need and do not restate their rules
