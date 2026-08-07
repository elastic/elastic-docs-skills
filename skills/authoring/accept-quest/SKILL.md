---
name: docs-accept-quest
version: 1.0.1
description: Turn an Elastic documentation GitHub issue into a drafted docs PR. Triangulates linked product PRs, finds the canonical docs home (docs-content or in-product docs repos such as kibana and elasticsearch), drafts with cumulative applies_to, verifies claims against source at HEAD, sweeps a local pitfalls checklist, and opens a draft PR in the correct repo. Use when assigned a docs issue, asked to draft docs for a GitHub issue, or told to accept a docs quest.
argument-hint: <docs-issue-url-or-number>
context: fork
allowed-tools: Read, Grep, Glob, Edit, Write, CallMcpTool, WebFetch, Bash, AskUserQuestion, Agent
sources:
  - https://www.elastic.co/docs/contribute-docs/content-types
  - https://www.elastic.co/docs/contribute-docs/style-guide
  - https://www.elastic.co/docs/contribute-docs/how-to/cumulative-docs
  - https://www.elastic.co/docs/contribute-docs/how-to/seo
  - https://elastic.github.io/docs-builder/syntax/applies/
  - https://elastic.github.io/docs-builder/syntax/
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

# Docs accept quest

End-to-end workflow for turning a GitHub documentation issue into a drafted PR in the repo that owns the target pages. Most quests start from an `elastic/docs-content` issue, but the docs change may belong in `docs-content`, `kibana`, `elasticsearch`, or another product docs tree — confirm ownership before branching (see Phase 1 product-repo routing). Runs Phase 0 once per machine to locate the writer's docs-content clone (for corpus search and docs-content worktrees), pitfalls checklist, and editorial preferences.

We are professional documentation writers. Every factual claim must be traceable to a line of code or an authoritative source. Nothing is invented, assumed, or copied from issue body prose alone.

## Inputs

`$ARGUMENTS` is the issue reference. Accept any of:
- `elastic/docs-content#123` — repo-qualified (typical)
- `elastic/<other-docs-repo>#123` — when the quest issue lives elsewhere
- `#123` — issue number (assume `elastic/docs-content` unless the user names another repo)
- A full GitHub issue URL

---


## Phase 0: Resolve writer paths

Before Phase 1, resolve three local paths. Writers who already keep these files elsewhere keep using them in place — this step only records the paths.

### Variables

| Variable | Purpose |
|----------|---------|
| `$DOCS_CONTENT_ROOT` | Local clone of `elastic/docs-content` (corpus search + docs-content worktrees; still required when the PR opens in another repo) |
| `$DOCS_PITFALLS_PATH` | Pitfalls checklist markdown file |
| `$EDITORIAL_PREFERENCES_PATH` | Editorial preferences markdown file |

### Resolution order

For each variable, use the first match:

1. Environment variable of the same name (`DOCS_CONTENT_ROOT`, `DOCS_PITFALLS_PATH`, `EDITORIAL_PREFERENCES_PATH`)
2. Values from a local config file (first file that exists):
   - `~/.config/elastic-docs/docs-accept-quest.local.yml`
   - `<current workspace root>/docs-accept-quest.local.yml`
3. First-run setup (below)

Config file shape:

```yaml
docs_content_root: /absolute/or/~/path/to/docs-content
pitfalls_path: /absolute/or/~/path/to/docs-pitfalls.md
editorial_preferences_path: /absolute/or/~/path/to/editorial-preferences.md
```

Expand `~` to the home directory. Do not commit the local config file to git.

### First-run setup

If any path is still unresolved, ask once (prefer `AskUserQuestion` when available):

1. **docs-content clone** — absolute path to your local `elastic/docs-content` checkout (required).
2. **Pitfalls checklist** — if you already have one, paste its path. If not, choose where to create one; default `<parent of docs-content>/docs-pitfalls.md`, seeded by copying `pitfalls.examples.md` from this skill directory.
3. **Editorial preferences** — same pattern with `editorial-preferences.example.md`; default `<parent of docs-content>/editorial-preferences.md`.

Then:

1. Verify each path exists. When seeding from an example, copy the bundled file to the chosen path (do not overwrite an existing file).
2. Write `~/.config/elastic-docs/docs-accept-quest.local.yml` (create parent directories as needed).
3. State the three resolved paths once, then continue.

**Existing files stay put.** If a writer already has pitfalls and preferences at custom locations (for example under a personal docs workspace), record those paths in the config — do not move, rename, or replace them.

In later phases, Read `$DOCS_PITFALLS_PATH` and `$EDITORIAL_PREFERENCES_PATH` by those resolved paths only. Never hard-code a username or a fixed `~/Documents/github/...` layout.

Bundled starters live next to this skill:

- `pitfalls.examples.md`
- `editorial-preferences.example.md`

### Companion skills

Invoke when installed; do not fail the quest if missing:

| Skill | When |
|-------|------|
| `docs-applies-to-tagging` | Any version- or deployment-scoped content |
| `docs-content-type-checker` | New or restructured pages |
| `docs-page-opening-optimizer` | New page openings |
| `docs-check-style` | Optional style pass alongside Vale |

---
## Phase 1: Understand the issue

Read the issue using the GitHub MCP (`issue_read`). Extract:

- **What changed**: the feature, setting, or workflow that was updated
- **User value**: how this affects readers (new capability, changed behavior, removed option)
- **Affected versions**: stack (for example 9.4+), serverless, or both. Treat a version in the issue's availability table, or a `vX.Y.Z` label on the dev PR, as a **backport target, not proof of a shipped release**. Before you use a version as the availability floor, confirm that patch actually shipped. If the minor reached its final patch before the backport landed, for example a `v9.3.9` label when 9.3 ended at 9.3.8, that minor never carried the change and must not drive `applies_to`. Carry the verified floor into Phase 3.
- **Affected product and area**: Kibana, Elasticsearch, etc. and the feature area

**Companion PRs:** When the docs change belongs in another repo (for example Kibana release notes or advanced settings YAML), open a companion PR there instead of stopping at "out of scope."

**Product-repo routing:** Before branching, confirm where the target page is sourced. Kibana release notes (`docs/release-notes/`) and `{settings}` reference YAML (`docs/reference/advanced-settings-space.yml` and siblings) live in `elastic/kibana`. For any published URL, check `elastic-docs` MCP `get_document_by_url` → `relatedProducts[].repository` — ES|QL reference pages, for example, live in `elastic/elasticsearch`, not docs-content.

**Bugfix vs new capability:** When a linked implementation PR carries `release_note:fix`, read behavior at the PR's **base commit** (`git show <base-sha>:<path>`) before planning docs. A fix usually restores already-documented behavior — often no new `applies_to` badge and sometimes no docs at all. When the change restores inherent/correct behavior, fold it into the adjacent rule as a plain fact; don't document the pre-fix buggy state or tag it as a versioned feature addition.

**Accuracy-only issues (no linked PR):** When the issue reports a wrong example or claim with no implementation PR, verify the underlying product rule in source (field types, parser behavior, API schema) — grep/read the relevant product repo instead of triangulating a diff.

**Resuming or reviewing an existing PR:** Before recommending revert of a lifecycle or availability edit, verify it against all sibling product PRs — a later PR may have already promoted or corrected the same surface.

### Follow all linked PRs and issues

For every PR or issue URL in the body, fetch it from the correct repo:
- `pull_request_read(method: "get")` — PR metadata, description, and labels
- `pull_request_read(method: "get_files")` — list of changed files (reveals the implementation repo)
- `pull_request_read(method: "get_diff")` — full diff; this is the primary source of truth

Look for concrete signals in the diff:
- i18n strings (`.defaultMessage:`) — exact user-visible label text
- Config schema or constants — actual default values and setting key names
- Files in `*/public/components/` or `*/public/pages/` — UI elements
- Feature flag or uiSettings keys — configurable behavior

**Check the implementation scope**: Look at the paths of the changed files — this is the authoritative signal for determining which apps are affected.
- If files are under `shared/`, `platform/`, `common/`, or a plugin whose name doesn't map to a single app (e.g., `unified_search`, `data`, `embeddable`), the feature likely surfaces in **multiple Kibana apps**. You must discover all consumers yourself — do not rely on the PR title or the issue's gap analysis to enumerate them, as both can be incomplete. The PR title may only name the apps the developer focused on, not every app the shared component is used in.
- If files are under an app-specific plugin (e.g., `plugins/dashboard/`, `plugins/discover/`), the change is probably scoped to that app.
- Use this scope assessment to build your own complete list of affected surfaces before moving to Phase 2.

**Search for sibling PRs**: A feature is often shipped across several PRs, and follow-up PRs often refine, rename, or revert behavior introduced by the original. After reading the explicitly linked PRs, run all of the following searches in the implementation repo. Each catches a different class of sibling PR — none alone is sufficient.

1. **Product-issue back-link** — catches PRs the author linked to the same product issue:
   ```
   "#12345" repo:elastic/kibana is:pr is:merged
   ```

2. **Team or feature label, narrow time window** — catches related work by the same team:
   ```
   label:Feature:Unified-search label:release_note:feature merged:2026-03-01..2026-04-30
   ```

3. **Path-scoped follow-up search (highest signal, do not skip)** — catches polish, rename, and removal PRs filed against new issues. For each non-trivial implementation file the original PR touched, run:
   ```
   repo:elastic/kibana is:pr is:merged path:legend_settings.tsx merged:>=2026-03-17
   ```
   Use the original PR's `merged_at` as the lower bound and "today" as the upper bound. Polish PRs frequently carry `release_note:skip` and link no issue, so they are invisible to searches 1 and 2 but always show up here.

4. **"Known issues" / "Limitations" / "Follow-ups" check** — if the original PR's body has any of these sections, treat it as a strong signal that follow-up PRs exist. Resolve each linked issue and search for the PRs that closed it.

Read the diff of every sibling PR you find. They may add, refine, rename, or remove behavior the original PR introduced — and any of those outcomes change what belongs in the docs.

**Premise check**: The issue body may overstate or misdescribe the change. If the diff only partially supports the claim, narrow the scope of your edits to what the diff actually confirms. Note the discrepancy explicitly.

**Whether-to-document gate — run before drafting.** Ask the user if any of these fit:

| Signal | Default |
|--------|---------|
| Invisible/automatic change; no new setting, step, or user choice | Recommend **no docs** (or release note only) |
| Convenience only (autocomplete, fewer clicks); existing prose still accurate | **No docs** or release notes only |
| Restriction of a previously **undocumented** internal | Release note only; don't add reference prose that introduces the internal |
| UI layout change; same instruction still correct ("select a data view") | **Screenshot refresh** only; no version-scoped prose |
| User-visible option expands to a new surface; docs never scoped it as unavailable | **Document the extension** — catch up on the feature where readers will look for it; release notes alone are not enough if the option was previously absent or implied form-only |

If the issue body itself says docs may not be needed, treat that as a signal — don't draft until the user confirms.

**Scanner override signal**: If the issue body says docs are "not needed" or the automated scanner did not flag a gap, but a human expert still filed the issue, treat the filing as a deliberate signal — the person saw something the scanner missed. Do not reuse the scanner's conclusion or the issue body's gap assessment as your own. Perform a full independent gap analysis regardless.

---

## Phase 2: Find existing docs

Use the Elastic Docs MCP to locate all pages that document this feature:

```
search_docs(query: "<feature name> <product>")
find_related_docs(url: "<known page URL>")
get_document_by_url(url: "<page URL>", includeBody: true)
```

Search broadly — find every page that mentions the feature, not just the obvious one. **Run a legacy-UI residue sweep in the source repo:** build a search fingerprint from the canonical and implementation terms, every added/removed/renamed UI label, legacy labels and icon/action instructions in the canonical docs, and referenced screenshot filenames or alt text. Search all of `docs-content` for each term; classify every plausible procedural or screenshot hit as affected shared UI, unrelated app-specific UI, valid conceptual mention, or historical/API content before finalizing Phase 3. The issue's suggested pages are starting points, not scope boundaries.

**Grep the source tree for the exact UI label before choosing placement.** `search_docs` and the issue's suggested page are starting points, not the whole map — they can miss a canonical hub that already documents the feature. Before planning any edit, run `grep -rn "<UI label>" .` across `docs-content` (for example `grep -rn "Fast mode" .`) to find: (a) the **canonical hub** for the feature, (b) every **sibling page** that already documents it, and (c) the `applies_to` scoping and link target those siblings use. When a hub exists, the update usually belongs there — with a light cross-reference from the page named in the issue — not as a new standalone block on the suggested page. Skipping this grep is the single most common cause of a first draft that has to be reshaped: you invent a standalone paragraph and the wrong link because you never saw the section that was already there.

**URL-to-file mapping** (elastic/docs-content):
Strip `https://www.elastic.co/docs/` and append `.md`:
```
https://www.elastic.co/docs/explore-analyze/dashboards/create-dashboard
→ explore-analyze/dashboards/create-dashboard.md
```

**Read source at a fresh ref, never the stale local clone.** The workspace clone (`$DOCS_CONTENT_ROOT`) can be dozens of commits behind `origin/main`, and reading a page from it can hide entire sections that already exist on main. Before reading any page's source, `git fetch origin` and read from a ref you've confirmed is current: the quest worktree (created from `origin/main` in Phase 4) or `git show origin/main:<path>`. Check the distance with `git rev-list --left-right --count HEAD...origin/main` before trusting the clone. Never conclude "this section doesn't exist yet" — or derive placement, scoping, or link targets — from the stale clone. (Treat `docs-content` with the same freshness bar as product code repos.) If you need to read source before the worktree exists, use `git show origin/main:<path>`.

For each relevant page, read the source file at a fresh ref (see the rule above) and:

**1. Identify the content type.** Fetch https://www.elastic.co/docs/contribute-docs/content-types if you need to verify the definitions. Every page has a content type that controls what belongs there:

| Content type | Purpose | What belongs | What does not |
|---|---|---|---|
| Overview | Explain what a feature is and why it exists | Concepts, architecture, use cases | Step-by-step instructions, exhaustive option lists |
| How-to | Guide a user through a specific task | Sequential steps, required inputs, expected outcomes | Background theory, full reference tables |
| Tutorial | Teach through a worked example | End-to-end scenario with explanation | API details, exhaustive option lists |
| Troubleshooting | Help users diagnose and fix problems | Symptoms, causes, fixes | Conceptual background |
| Reference / settings | Enumerate options, values, parameters | Every valid value, default, type | Narrative prose, step-by-step instructions |

A gap is only real if the missing information belongs on this type of page. A how-to that omits architectural background is not a gap — that belongs on an overview. A reference page that omits a valid value is always a gap.

**2. Note what the page currently says**, whether it is factually wrong given the change, and whether a new step, option, or note is needed.

**Gap quality gate — be strict.** Only flag a gap when:
- The page says something the change makes wrong or misleading
- A workflow now has a new step or option users would miss
- A status badge or availability note needs updating
- A reference or settings section omits a valid value (even if the omission predates the current PR)

Do NOT flag gaps on overview or conceptual pages for missing specifics that belong on a reference or how-to page instead.

Before accepting the issue's suggested section, ask: "Where is the reader when they'd need this?" Match section purpose to content type, not the issue heading.


**Pre-existing gaps triggered by new additions**: When a PR adds a new option to a settings list or dropdown, check whether the existing options are also enumerated in the docs. If they are not, the PR is the trigger to bring the whole list up to standard — add the pre-existing values without an `applies_to` tag, and add the new value with the appropriate version tag. Do not document only the new addition while leaving undocumented options in place.

**Look for shared snippets before drafting per-page edits**: When the affected feature surfaces in multiple apps, search the docs-content source for `{include}` directives that are already shared across those pages:
```bash
grep -r "include.*snippet-name" "$DOCS_CONTENT_ROOT"/
```
If a shared snippet already covers the relevant section, one edit to the snippet propagates to all consumers — always prefer this over duplicating content across pages. If no snippet exists but the new content would be identical across two or more pages, consider whether a new snippet is warranted and where it would best be included.

---

## Phase 3: Plan the edits

For each gap, start from the lightest change that resolves it. After you have picked changes for all the gaps, look at the page as a whole — if adding content alone would leave it incoherent, restructuring may be the right next step (see "Make sure the page still flows" below).

| Need | Action |
|------|--------|
| Wrong value or stale statement | Update the sentence |
| New option or step | Add a sentence or bullet |
| New capability that fits an existing section | Add a short section |
| Entirely new task not covered anywhere | Create a new how-to page |

**For a new page or an overview page, write a short persona and goal brief before drafting.** These are the cases most prone to feature-description mode — restating what the feature is instead of serving a reader — so name the reader and their end goal up front:

- **Reader**: who this is for (role, experience level, deployment type).
- **Goal**: what they are trying to accomplish that no existing page covers.
- **Outcome**: what they can do or understand after reading.

Derive all three from the issue and the evidence you gathered in Phases 1 and 2, and record them in your plan. If you cannot — the issue names a topic but not an audience, the "why" is missing, or two plausible readers would want different pages — ask the user rather than invent a generic reader. These three are also the exact inputs the Phase 7 reader test runs on, so pinning them down now pays off twice.

For new pages, run `docs-page-opening-optimizer` on the planned opening — define what the thing is and how data reaches it before recommending a preferred path.

Skip the brief for an edit to an existing how-to, reference, tutorial, or troubleshooting page. That page already encodes its audience; inherit it and match the reader the existing content is written for rather than re-deriving one.

**If you're creating a new page, plan it around its content type.** A new page is not just prose on the right topic — it must match the structure its content type prescribes, and that structure is easy to skip because well-written prose can pass every style rule while still being the wrong shape. Before drafting, fetch the guidelines and template for the type (usually **how-to** for a new task):

- Guidelines: `https://www.elastic.co/docs/contribute-docs/content-types/<type>s` (for example, `how-tos`, `overviews`, `tutorials`)
- Template: the matching file under `contribute-docs/content-types/_snippets/templates/` in `elastic/docs-content`

List the type's **required elements** in your Phase 3 plan so the draft is built around them, not retrofitted afterward. For a **how-to** the spine is: action-verb title, an outcome-focused introduction, a **Before you begin** (requirements) section, **numbered steps** with imperative phrasing, a **success checkpoint**, and a **Related pages** section (usually **Next steps** too). Non-linear alternatives (two ways to open a dialog, three independent toggles) can stay as bullets, but the overall task must have a numbered spine. If you're unsure which type fits, run `docs-content-type-checker` in classify mode on your page idea before drafting.

**Choose placement deliberately:**

If the issue body suggests a specific section, take that suggestion seriously — it reflects the issue author's knowledge of the page structure. Before overriding it, ask why they chose that section. The answer usually makes the right placement obvious.

For each candidate section, identify its purpose before placing content in it:
- **Conceptual / intro sections** — explain what the feature is and why it exists. Do not add specific behaviors or interaction details here.
- **Reference or options sections** — enumerate settings, behaviors, and interactions. This is where specific defaults, toggles, and per-feature details belong.
- **Task / how-to sections** — describe steps to accomplish something. Add content here only if it changes or extends the steps.

Confirm that the new content's type (default behavior, new option, renamed label, etc.) matches the purpose of the target section before drafting.

**Match page scope to feature scope.** A product-wide page (e.g. an editor that exists across several apps, a feature available in multiple deployment types) is the wrong host for content that applies only in a narrower context. When a feature is scoped narrower than the candidate page — Discover-only, Stack-only, a single security workflow — prefer documenting it on the narrower-scope page and leaving a one-line cross-reference on the broader page. Look for sibling content on the narrower page that already documents context-specific behavior and place the new section near it. This keeps the broader page from accumulating exceptions and saves readers from skipping over content that doesn't apply to them.

**Match sibling scoping and link targets for an already-documented UI surface.** When the same control, option, or feature is already documented elsewhere in the corpus (found via the source grep in Phase 2), adopt the `applies_to` lifecycle and the link target those pages already use — don't derive them independently. In particular, do not take the version from the issue's availability table when siblings tag the same UI differently: a Kibana UI control that the corpus consistently tags `preview 9.5` stays `preview`, even if the issue lists the underlying engine feature as `ga` in 9.5. Verify against source only if you have a specific reason to believe the sibling scoping is now wrong.

**Make sure the page still flows after your edits:**

A new section, table, or paragraph rarely lands in isolation. Once you have picked where each piece goes, read the section it lives in (and its siblings) end to end as a first-time visitor and check:

- **Narrative flow**: does the page tell a coherent story, or does the new content feel bolted on?
- **Progressive disclosure**: does each piece of information appear when the reader needs it, no earlier and no later? An overview should not carry reference details; a procedure should not require the reader to re-read background to follow it.
- **Content type fit**: the target section's content type (overview, how-to, reference, etc.) still controls what belongs there. If new API detail wants to land in an overview "because that's where the feature is mentioned", you probably need a different target section.
- **TOC scannability**: when two sibling sections describe alternatives, their titles should signal the alternative relationship — through parallel construction (e.g., `Export as X`, `Export as Y`) or by sitting together under an umbrella heading. A reader scanning the TOC should be able to choose between them without opening the page.
- **Heading parallelism with siblings**: when you add a new heading among existing siblings, match their grammatical pattern — noun phrase vs verb phrase, with-article vs without, casing — so the new entry doesn't stand out in the TOC. If the siblings are noun phrases (`Query formatting`, `Warnings`, `Query statistics`), don't introduce a verb phrase (`Browse data sources and fields`); rephrase as a noun (`Data source and fields browsers`).

If any of these checks fail, restructuring is on the table. It is not the default move, but it is the right move when adding content alone would leave the page incoherent. Keep the change as small as the problem requires — adding a comparison table, promoting an umbrella heading with H3 children, or reordering paragraphs is usually enough. Surface any proposed restructure in your Phase 3 plan so the user can approve or adjust the shape before you draft.

When fixing heading levels in one section, audit the whole page spine before opening the PR.

**When restructuring means splitting one page into several files, two build-breaking gotchas won't show up in your own repo checkout:**

- **A heading's custom `[id]` anchor only resolves for cross-file links when the heading is H2 or lower.** If a sub-heading you're promoting to become a new page's title turns into an H1 (`# Title [old-id]`), `#old-id` stops working as a link target — docs-builder does not register custom anchors on a page's H1, only on H2+. (The custom-anchor example in `https://elastic.github.io/docs-builder/syntax/headings/` is always H4+, never H1 — that's the tell.) Any existing link that reached that content via `#old-id` needs fixing: drop the fragment if the whole new page now covers what that fragment used to scope (the common case), or add a real H2+ anchor if a more specific target is still needed.
- **Cross-repo backlinks into the anchor you're moving are invisible to any grep of `docs-content`.** Other Elastic repos (`kibana`, `elasticsearch`, `beats`, and so on) link straight into specific `docs-content` anchors from in-product help text, indexed in a cross-repo link index that only the real build checks against. "No more `page.md#anchor` references anywhere in `docs-content`" does not mean the anchor is safe to remove — it could still be load-bearing for another repo's UI. If you must remove an anchor a split makes obsolete, keep a real H2+ anchor with the old id somewhere reasonable (even if you no longer link to it internally) as cheap insurance, unless you've confirmed via a green build that nothing depends on it.

Because of both, **a page split's links are not verified until the actual CI build has run clean** — a hand-rolled "does a heading with this id exist" script will pass on both failure modes above and give false confidence. If you can't run the real build before opening the PR, say so, and treat the first CI run as verification, not a formality: watch it, and if `build / build` fails on a missing-anchor error, it's almost always one of the two gotchas above.

**Check SEO impact**: if the H1 title or meta `description` in the frontmatter no longer reflects the page content after your edits, update them. Keep titles under 60 characters and descriptions 120–160 characters, written to answer the reader's intent. Fetch https://www.elastic.co/docs/contribute-docs/how-to/seo if you need guidance.

**Assess screenshots — value first**: screenshots are not the default. Most readers already have the product open in front of them; decorative shots of menus, buttons, or generic panels add maintenance cost without helping anyone. A screenshot earns its place only when it provides value the prose cannot. Strong reasons to include one:

- The action is genuinely hard to find or non-obvious (e.g. a hidden gesture, a context-menu nested several levels deep, an unlabeled icon in an unexpected location).
- The content is intrinsically visual and the reader needs to see the outcome (e.g. the result of a chart or visualization, a layout change, a rendered diagram).
- The page is aimed at prospects, evaluators, or new users (overview or getting-started content) rather than hands-on practitioners.

For each page you are editing, scan the source file for image directives (`![`, `:::{image}`, `:::{figure}`) and run two checks:

- **Outdated existing screenshot**: if the UI change in the PR would make an existing screenshot wrong (new panel, renamed button, changed layout, added option), flag it. If the screenshot also fails the value test above, mention that removal is an option alongside updating.
- **Missing screenshot for new content**: weigh the value test above. Sibling sections carrying screenshots is a useful hint — it can suggest the page is aimed at new users or prospects, where screenshots tend to help — but it isn't on its own a reason to add one. If after weighing audience, novelty, and visual nature you still conclude a screenshot would help, flag it and say specifically what it would show and why prose alone is not enough.

Do not add, update, or remove screenshots yourself — flag each one that needs attention as a todo item under `Screenshots to add or update` in the PR description.

Apply the cumulative docs model — docs serve all active versions simultaneously. Fetch https://www.elastic.co/docs/contribute-docs/how-to/cumulative-docs if you need to verify the rules:
1. Do users on earlier versions still need the old content? (Usually yes — preserve it alongside new content.)
2. What is the simplest version-scoping format? Tagged paragraph → tagged bullets → `applies-switch` tabs.

---

## Phase 4: Draft the edits

### Branch setup

When the target pages live in `docs-content`:

```bash
cd "$DOCS_CONTENT_ROOT"
git fetch origin
git worktree add "$DOCS_CONTENT_ROOT/../docs-content-<short-slug>" -b docs-issue-<N>-<short-slug> origin/main
cd "$DOCS_CONTENT_ROOT/../docs-content-<short-slug>"
```

When product-repo routing puts the change in another repo (for example `elastic/kibana` or `elastic/elasticsearch`), use that repo's local clone the same way: fetch, worktree from `origin/main`, branch `docs-issue-<N>-<short-slug>`. Ask the user for the clone path if it is not already known. Keep using `$DOCS_CONTENT_ROOT` for corpus grep and published-page mapping even when the PR opens elsewhere.

### Writing rules — always apply

This phase does **not** embed house-style or `applies_to` manuals. Before you write any prose, load the sources below. Skipping them is a process failure.

**1. Writing preferences (required Read):**
When working on writing tasks, make sure to respect these preferences: `$EDITORIAL_PREFERENCES_PATH`. Read that file with the Read tool (full file) before drafting. Ambient injection is not enough — re-read at the start of Phase 4.

**2. `applies_to` / cumulative model (required when any content is version- or deployment-scoped):**
Invoke the `docs-applies-to-tagging` skill and follow it. Do not invent tag syntax from memory. That skill owns placement forms, version syntax, lifecycle append vs replace, minor-level tagging, rename patterns without badges, and cumulative preservation. Editorial model overview: https://www.elastic.co/docs/contribute-docs/how-to/cumulative-docs. Also honor Phase 1: a `vX.Y.Z` backport label is a target, not proof the minor shipped.

**3. Elastic style guide + MyST (fetch when drafting):**
- https://www.elastic.co/docs/contribute-docs/style-guide — voice/tone/formatting baseline (Vale enforces much of it)
- https://elastic.github.io/docs-builder/ — MyST directive syntax

**New page structure — build to the content type's template first:**
If you are creating a new file (not editing an existing page), assemble the required elements of its content type *before* you write the body. Style and `applies_to` can pass on prose that is still the wrong shape. Use the guidelines and template from Phase 3. For a how-to: action-verb H1, outcome-focused intro, **Before you begin**, **numbered steps**, success checkpoint, **Related pages**.

**Constraints:**
- Restructure or rename headings only when your Phase 3 plan calls for it; never silently mid-draft
- Do not create new files unless no existing page can absorb the content
- Do not add screenshots
- Do not invent behavior you cannot verify from the linked PR diff
- Do not change files outside the task scope unless a cross-reference is factually broken

---

## Phase 5: Verify every factual claim

Before committing, trace every specific claim in your draft back to the source code. This is non-negotiable — we do not publish things we cannot confirm.

### Locate the source repo

The implementation PR's `owner/repo` is the starting point. Common repos:

| Product area | Repo |
|--------------|------|
| Kibana UI, plugins | `elastic/kibana` |
| Elasticsearch | `elastic/elasticsearch` |
| Fleet / Elastic Agent | `elastic/elastic-agent` |
| Beats | `elastic/beats` |
| Logstash | `elastic/logstash` |

If uncertain, check the linked PR — its repo is the answer.

### Enumerate every claim before you verify any

Verification fails most often by omission, not by error: you confidently verify the claims you happen to think of and silently skip the rest. Force completeness with an explicit checklist before opening any source file.

Re-read your draft and list every concrete claim that could be wrong. Group them by type:

- **UI strings**: every button label, tooltip, menu item, heading, placeholder, aria-label, status message
- **Identifiers**: every setting key, config field, prop name, CLI flag, API endpoint, URL path
- **Values**: every default, range, limit, version number, file size
- **Behavior**: every "when X happens, Y" claim, every state transition, every conditional

A claim that does not appear on this list will not get verified. Aim to over-list — it is fine to write down something you are sure of and confirm it in five seconds.

### What to verify and how

For each item on your checklist, find the backing evidence:

| Claim type | Where to look |
|------------|---------------|
| Default value | Config schema, constants file, or settings definition |
| UI label text | i18n string (`.defaultMessage:`) in the source file at HEAD — not the issue body, scanner text, or PR title |
| Setting or config key name | Config schema or TypeScript type definition |
| Behavior description | Handler, service, reducer, or hook logic at HEAD — not mocked unit tests alone |
| Version, lifecycle, or availability | Product source at HEAD — never issue body, PR description, Slack, release digest, or another docs page (including in-flight docs PRs) |
| Kibana REST API public / GA | Route config `access: 'public'` and `since:` — not schema or embeddable registration alone |
| Elasticsearch serverless lifecycle | REST API spec `stability` and `visibility` on the endpoint — `@ServerlessScope(PUBLIC)` proves availability, not preview vs GA |

Use the GitHub MCP:
- `get_file_contents(owner, repo, path, ref)` — read a specific file from the implementation branch
- `search_code(query, owner, repo)` — find a config key, i18n ID, or constant by name

**Verify against HEAD, not just the original PR's diff.** The diff shows what the original PR changed at a single moment; it cannot show that a follow-up PR renamed, restructured, or removed the same code before release. For every UI label, prop name, component name, or numeric range you intend to document:

1. Pull the current state of the implementation file: `get_file_contents(owner, repo, path)` with no `ref` (defaults to HEAD).
2. Confirm the i18n key, constant, or component you saw in the original diff is still present at HEAD. If it is gone or renamed, treat it as a red flag — a follow-up PR changed the feature. Loop back to Phase 1's path-scoped sibling search and read every PR that touched this file since the original merged.
3. As a quick sanity check, run `search_code` on the i18n key or constant name. Zero results in the current source means the symbol no longer exists; do not document it.

**When the diff removes an i18n string, find its replacement.** A redesign rarely deletes a label without adding one; the new label often lives in a different file (a hook, a sibling component, a renamed constants module). If the diff shows `i18n.translate('foo.bar.runQuery', ...)` being removed:

1. Do not reuse the removed label in your draft, even if it still feels like the natural name for the feature. The user-visible string has changed.
2. Find the new label by reading the surrounding component on HEAD — follow the prop, hook, or memo that now produces the button/tooltip/menu text — and quote that string instead.
3. Be especially suspicious of label memory built up across earlier read passes. If you read the file at an older `ref` first, your recollection of the label is a snapshot of the old version. Re-read at HEAD before quoting it.

**Test IDs, data attributes, and component names are not user-visible labels.** A `data-test-subj="ESQLEditor-run-query-button"` or a component named `RunQueryButton` is an internal identifier the developer chose; the user sees whatever string the i18n call returns. Never quote a test ID or component name as if it were a UI label, and never let one bias your guess at the label.

**Common traps (still Phase 5, not the pitfalls checklist):**

- A removed feature gate or a setting defaulting to on is not proof of GA — require explicit lifecycle evidence.
- Scanner and quest issue bodies often quote the Kibana PR title, not the shipped i18n label.
- A PR title verb can describe internal plumbing, not the user-facing capability you are documenting.
- Automatic fallback, default detection, or migration scope stated in a PR summary may be narrower in code — trace the constant or call site.
- An in-flight docs PR's `applies_to` tags can be wrong — verify lifecycle in product source before trusting them.

### Sweep the pitfalls checklist

Read `$DOCS_PITFALLS_PATH`. For every entry whose **When** trigger matches the diff, run its **Check**. These are doc-shaped mistakes (links, structure, corpus terms, transcribed issue prose) — not a second pass of source verification. If a check fails, correct the draft before proceeding.

### Decision rules

- **Confirmed by code**: write the claim as fact.
- **Consistent with diff but detail not fully visible**: write conservatively and flag it in a PR comment for the reviewer to verify.
- **Contradicted by code**: correct your draft before proceeding.
- **Not findable in any accessible source**: omit the claim or rephrase as "see the [product] documentation for current default values" — never guess.
- **Reference exists in the product but has no public docs page yet** (e.g., an API endpoint shipped before its reference page is published): refer to it in plain prose without a hyperlink, and add a `Pending links` entry to the PR body listing each spot that needs a link once the reference is published (file path + which paragraph or table cell). This gives the next maintainer a checklist instead of a needle-in-haystack search.

### Commit

```bash
git add <changed files>
git commit -m "docs: <short present-tense description> (#<issue-number>)"
git push -u origin <branch-name>
```

---

## Phase 6: Self-review

Before opening the PR, run Vale on the changed files if available:

```bash
vale --output=line <changed files>
```

Then check your changes against this list:

**Style:**
- [ ] No em dashes
- [ ] No "click" — use "select"
- [ ] No "please", "easy", "simply", "just"
- [ ] Present tense, active voice, second person
- [ ] UI element names in bold
- [ ] No consecutive admonitions

**applies_to:**
- [ ] Every new page has `applies_to` in frontmatter
- [ ] No inline `applies_to` floating in prose
- [ ] Version syntax correct, no overlapping ranges
- [ ] No version numbers in prose adjacent to a badge

**Content type (any new or restructured page):**
- [ ] The page matches a single content type and follows that type's template
- [ ] How-to has all required elements: action-verb title, outcome-focused intro, **Before you begin**, numbered steps, success checkpoint, **Related pages**
- [ ] No overview prose, reference tables, or multiple chained tasks smuggled into a how-to
- [ ] Ran `docs-content-type-checker` on every newly created file and resolved the real gaps

**Links and anchors (any page split, or any anchor removed/renamed):**
- [ ] No link anywhere points at a custom `[id]` anchor that now lives on an H1 (page title) — docs-builder doesn't resolve those cross-file; drop the fragment or move the anchor to an H2+
- [ ] Pushed and watched the actual CI build go green — a local "anchor exists somewhere in this file" check cannot see the H1 exception above or cross-repo backlinks from other Elastic repos, so it is not sufficient on its own

**Accuracy:**
- [ ] Every UI string in the draft (labels, tooltips, menu items, headings, placeholders) appears on your Phase 5 enumeration and was checked at HEAD
- [ ] No UI string was quoted from memory or from an older `ref` read; every quoted label was confirmed against the file at HEAD in this session
- [ ] No test IDs, data attributes, or component names quoted as if they were UI labels
- [ ] Every default value and setting name traced to source code
- [ ] No claims copied verbatim from issue body prose without code confirmation
- [ ] Cumulative model applied (old content preserved where needed)
- [ ] Ran every pitfalls checklist check (`$DOCS_PITFALLS_PATH`) whose **When** trigger matches this change, and resolved any failures
- [ ] Re-read `$EDITORIAL_PREFERENCES_PATH` in Phase 4 and again here; draft respects those writing preferences
- [ ] Invoked `docs-applies-to-tagging` for any version- or deployment-scoped content (not invented from memory)

Fix any real issue. Vale false positives (technical terms, product names, code samples) can be ignored.

---

## Phase 7: Reader comprehension test

Phases 5 and 6 confirm the draft is *correct* and *well-formed*. Neither confirms it is *understandable to someone who wasn't in the room while you wrote it*. Run a fresh-reader test to catch that before opening the PR.

**Dispatch a subagent that has none of your context.** The value of this test comes entirely from isolation: a subagent starts with a fresh context window, so it cannot see your issue analysis, the PR diffs, the contribution guidelines, or your drafting rationale — unless you paste them in. Do not paste them in. If you hand the reader tester your reasoning, it understands the draft the way you already do and the test proves nothing.

Give the subagent only:

- The **intended reader** and their **goal** — the Reader and Goal from your Phase 3 persona brief. For an edit to an existing page (where you wrote no brief), use the audience that page is already written for.
- The **expected outcome** — the Outcome from that brief: what the reader should be able to do or know after reading.
- The **full proposed content** of every changed page or section, exactly as it will render.
- Only the **linked passages** a reader must follow to use the draft (for example, the target of a "see X" cross-reference). Nothing more.

Withhold your drafting rationale, the implementation evidence, the contribution guidelines, and the issue's gap analysis. The test must show whether the documentation stands on its own.

Paste this into the subagent prompt:

```
You are the intended reader of the documentation below. You know only your
profile, your goal, and what the documentation tells you — nothing about how
it was written or why.

Reader: <who they are>
Goal: <what they are trying to do or learn>
Expected outcome: <what they should be able to do or know afterward>

Documentation:
<full proposed content of every changed page or section>

Do this:
1. Predict 3–5 realistic questions you would ask while trying to reach the goal.
2. Answer each using ONLY the documentation above. Mark an answer
   "Not established" when the docs do not support it.
3. Report blocking gaps (ambiguity, missing prerequisite, contradiction,
   assumed knowledge, unclear next action) separately from optional improvements.
   A gap is blocking only if it stops you from reaching or verifying the outcome.
4. Do NOT assess style, word choice, markup syntax, or technical accuracy
   against outside knowledge. This is a comprehension test only.

Return exactly: Questions, Blocking gaps, Optional improvements, Verdict: pass | fail.
```

**Act on the result:**

- **Pass, or only optional improvements** → go to Phase 8. Optional improvements do not block the PR; note any you deliberately skip.
- **Blocking gap you can close from context you already gathered** → make the smallest fix that closes it, then re-run the test once. Stop after at most two rounds.
- **Any fix that adds a new factual claim** (a value, a label, a behavior) → run that claim back through Phase 5 before re-testing. A comprehension fix is not exempt from verification.
- **Blocking gap that needs context you don't have** (unverifiable behavior, or a decision only the issue author can make) → do not paper over it. Surface it to the user with the exact question the reader could not answer, and hold the PR until it's resolved.

---

## Phase 8: Open the PR

Use the GitHub MCP `create_pull_request` tool on the **target docs repo** (the one that owns the edited files — often `elastic/docs-content`, sometimes `elastic/kibana`, `elastic/elasticsearch`, or another product docs tree). Always set `draft: true`. If the quest needs both a docs-content PR and a companion PR elsewhere, open each in its owning repo.

**PR title:** `docs: <what changed, present tense> (#<issue-number>)`

**The PR body must always describe what is currently in the PR.** On first creation, build it from the template below. After any push that materially changes the diff (new sections, dropped sections, restructured headings, scope expansion or reduction), update the description before requesting re-review.

**PR body:**

Build the body from the sections below. **Omit any section whose content does not apply — leave no empty headings or placeholder bullets.** A reader scanning the PR should see only sections that carry information.

```markdown
## Summary

This PR addresses #<issue-number> with the following changes:

- **`<file-path>`**: <what changed and why, one sentence>
- **`<file-path>`**: <what changed and why, one sentence>

## Resolves

Closes #<issue-number>

## Pending links

<!-- Include this section ONLY if your draft refers to a feature, API, setting, or page that has no public reference yet. Omit the heading entirely if there is nothing to track. -->
- `<file-path>` — `<location: section, paragraph, or table cell>`: link to <what> once <reference> is published.

## Screenshots to add or update

<!-- Include this section ONLY if at least one existing screenshot is now outdated, or new content is intrinsically visual / hard to follow without a picture. Do not flag missing screenshots just because sibling sections have one. Omit the heading entirely if there is nothing to flag. -->
- [ ] `<file-path>` — `<image filename>`: <why it is likely outdated>
- [ ] `<file-path>` — new `<section-name>` section: consider adding a screenshot of <what it would show> because <why prose alone isn't enough>.

---

> **AI-generated draft** — review all generated content for factual accuracy before merging.
```

After opening the PR, suggest a conversation title:

```
Suggested conversation title: #<issue-number> — <issue-title-as-written-in-the-GitHub-issue>
```

If a chat-rename tool is available in the current agent (for example Cursor `rename_chat`), apply that title. Otherwise leave the suggestion for the user.

