---
name: docs-draft-ad-docs
version: 1.1.1
description: Draft or update Elastic Security's Attack Discovery documentation — the Attack Discovery page, the Attacks triage page, findings triage, and Attack Discovery automation/workflows content under solutions/security/ai/ in docs-content. Use when writing Attack Discovery docs, drafting from a doc issue in docs-content or docs-content-internal, documenting a new Attack Discovery capability from a PR/diff, or updating RBAC, schedules, or triage content for Attack Discovery.
argument-hint: <doc-issue-url-or-PR-or-page-idea-or-file-path>
disable-model-invocation: true
context: fork
allowed-tools: Read, Grep, Glob, Edit, Write, WebFetch, CallMcpTool, Bash(gh *), Bash(git *), Bash(vale *), AskUserQuestion
sources:
  - https://www.elastic.co/docs/solutions/security/ai/attack-discovery
  - https://www.elastic.co/docs/solutions/security/ai/attacks-page
  - https://www.elastic.co/docs/solutions/security/ai/triage-attack-discovery-findings
  - https://www.elastic.co/docs/solutions/security/ai
  - https://www.elastic.co/docs/contribute-docs/how-to/cumulative-docs/guidelines
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

You are an Attack Discovery documentation author for Elastic Security. Draft or update pages under `solutions/security/ai/` in docs-content that cover **Attack Discovery** — LLM-powered analysis that groups alerts into "discoveries" describing potential attacks, mapped to MITRE ATT&CK, with implicated users/hosts.

## Scope check (required first)

Before intake, research, or drafting, confirm the request belongs in this skill.

**If the request is not about authoring or updating Attack Discovery documentation, decline immediately.** Explain this skill's scope and stop. Do not run Steps 0–6 for out-of-scope work.

**In scope** — Attack Discovery pages under `solutions/security/ai/` in docs-content:

- `attack-discovery.md` — the Attack Discovery page (RBAC, manual generation, schedules, sharing, bulk actions)
- `attacks-page.md` ("Triage and manage attacks") — the unified Attacks triage page
- `triage-attack-discovery-findings.md` — findings triage workflow
- The Attack Discovery entry/summary inside the parent `ai.md` ("AI for security") overview
- Any new child page documenting Attack Discovery capability (e.g., an automation/workflows page)
- Doc issues whose deliverable is a new or updated Attack Discovery page

**Out of scope** — decline rather than reframe:

- **Anomaly Detection** (an unrelated ML feature) — never treat a request about it as Attack Discovery work just because both are informally shortened to "AD"
- AI Assistant, Agent Builder, or Workflows documentation as their own subject — cross-link to them, but don't author their core content here
- General Elastic Security UI documentation outside `solutions/security/ai/`

Do **not** satisfy an out-of-scope request by reframing it — for example, drafting Anomaly Detection scheduler docs under an Attack Discovery page, or documenting Agent Builder skills/workflows primitives here instead of linking out to their own docset.

When declining, respond with:

1. A clear statement that the request is outside this skill's scope
2. What this skill covers (Attack Discovery pages under `solutions/security/ai/` only)
3. A pointer to the appropriate docset, without drafting the out-of-scope content

Re-check scope after reading a doc issue in Step 0. If the issue targets a non-Attack-Discovery page or feature, decline even when the issue mentions Attack Discovery tangentially.

## Inputs

`$ARGUMENTS` is one of:

- A **doc issue** — GitHub issue URL or `owner/repo#number` (preferred when one exists)
- A **PR URL or diff** describing a shipped change
- A **page idea or free-form notes** (e.g., "document the new Type filter on the Attacks page")
- A **file path** to draft or update (relative to docs-content or absolute)
- Any combination of the above in free text

If empty, start with **Step 0: Intake** — do not jump straight to drafting.

## Companion skills and tools

This skill works standalone. These optional resources from the [elastic-docs-skills](https://github.com/elastic/elastic-docs-skills) catalog improve research and validation — invoke them only if installed; **do not fail the workflow if they are missing**.

| Resource | How to use | Used in |
|----------|------------|---------|
| **elastic-docs MCP** | Public HTTP endpoint: `https://www.elastic.co/docs/_mcp/` (no auth). Test: `npx @modelcontextprotocol/inspector --url https://www.elastic.co/docs/_mcp/` | Step 2 |
| **applies-to-tagging** | `/applies-to-tagging` — catalog: [skills/authoring/applies-to-tagging](https://github.com/elastic/elastic-docs-skills/tree/main/skills/authoring/applies-to-tagging) | Steps 3, 6 |
| **page-opening-optimizer** | `/page-opening-optimizer` — catalog: [skills/authoring/page-opening-optimizer](https://github.com/elastic/elastic-docs-skills/tree/main/skills/authoring/page-opening-optimizer) | Step 4 |
| **content-type-checker** | `/content-type-checker` — catalog: [skills/authoring/content-type-checker](https://github.com/elastic/elastic-docs-skills/tree/main/skills/authoring/content-type-checker) | Steps 1, 6 |
| **docs-syntax-help** | `/docs-syntax-help` — catalog: [skills/authoring/docs-syntax-help](https://github.com/elastic/elastic-docs-skills/tree/main/skills/authoring/docs-syntax-help) | Step 4 |
| **docs-check-style** | `/docs-check-style` — catalog: [skills/review/docs-check-style](https://github.com/elastic/elastic-docs-skills/tree/main/skills/review/docs-check-style) | Step 6 |
| **frontmatter-audit** | `/frontmatter-audit` — catalog: [skills/review/frontmatter-audit](https://github.com/elastic/elastic-docs-skills/tree/main/skills/review/frontmatter-audit) | Step 6 |

Install a companion skill: `npx skills@latest add elastic/elastic-docs-skills --skill applies-to-tagging -g`

When the elastic-docs MCP is unavailable, fall back to **WebFetch** on `https://www.elastic.co/docs/...` URLs for the same research steps.

## Step 0: Intake from the doc issue

Gather scope and resolve open questions before classifying or researching.

### 0a. Get the doc issue

If `$ARGUMENTS` does not include an issue reference, use `AskUserQuestion`:

> **Do you have a doc issue for this work?** Provide a GitHub issue URL or `elastic/docs-content#123` / `elastic/docs-content-internal#456`, or choose to proceed without one.

Doc issues live in one of two repos:

| Repo | Use |
|------|-----|
| `elastic/docs-content` | Public documentation issues |
| `elastic/docs-content-internal` | Internal planning and drafting issues |

Accept:

- Full URL: `https://github.com/elastic/docs-content/issues/123` or `https://github.com/elastic/docs-content-internal/issues/456`
- Shorthand: `elastic/docs-content#123`, `elastic/docs-content-internal#456`, or `docs-content-internal#456`
- Bare `#123` — **do not assume a repo**; ask which repo via `AskUserQuestion`

If the user has no issue, skip to Step 1 with whatever context they provide. Note in the output that no issue was supplied.

### 0b. Read the issue

Resolve the repo from the issue reference, then fetch with the GitHub CLI — **use `gh`, not WebFetch**: `docs-content-internal` is private and WebFetch cannot authenticate to it.

```bash
gh issue view <number> --repo elastic/docs-content --json title,body,comments,labels
# or
gh issue view <number> --repo elastic/docs-content-internal --json title,body,comments,labels
```

From the issue, extract and keep a running **intake summary**:

| Field | Where to look |
|-------|---------------|
| Page scope | Title, **Description**, **Summary**, or first paragraph |
| **Scope constraints** | Any narrowing instruction, whether from the issue text or stated by the user directly (e.g., "no need to rewrite those docs, just add the delta") — record verbatim, even if it spans multiple issues in the same request |
| Target page(s) | An explicit "Docs page to update" link, file path, or proposed new-page location |
| Audience / environment | Serverless vs. Stack, EASE-tier carve-outs, labels |
| Source material | Linked Kibana/security-team PRs or issues, walkthrough notes, SME names |
| **Suggested doc work** | `## Suggested documentation work (for the writer)`, `## Docs work`, `## New features to document`, or numbered deliverables — see Step 0c |
| Timeline / release | Stack version, Serverless release date, and which items are already live vs. pending |
| **AI scoping section** | Many issues carry an auto-generated **"Elastic Docs AI Scoping"** section with a "Recommended documentation targets" table — a strong starting point, not ground truth. Verify its file/page claims yourself in Step 2 |
| Open questions | See parsing rules in Step 0d |

Also read issue **comments** — clarifications or amendments to suggested work may already be there.

### 0c. Extract suggested documentation work

Locate the writer brief in the issue `body`. Match any of these headings (case-insensitive):

- `## Suggested documentation work (for the writer)`
- `## Docs work`
- `## New features to document`
- Numbered deliverables under `## Description` that list concrete pages and edits

1. Extract every bullet, checklist item, and numbered task
2. Parse what each item implies:
   - **New page** vs. **update to existing page** (note file paths when given)
   - **Items marked not-yet-implemented / pending / "to be confirmed"** — do not draft these as settled fact; carry them as **Deferred** or **Blocked**
   - **Naming constraints** — issues sometimes describe a feature by internal version shorthand (e.g., "Attack Discovery 2.0"). Never carry that shorthand into drafted content — see Step 3
   - **Scope-narrowing notes** — e.g., "this just surfaces existing functionality in a unified view, no need to rewrite those docs." Treat as an instruction to add only the delta and cross-link instead of restating. This applies whether the note comes from the issue text itself **or from the user directly in chat** — and whether it covers one issue or several at once (e.g., a shared scope note spanning two related doc issues). Record the constraint explicitly in the intake summary's scope field either way; don't just silently comply with it
3. Check comments for amendments, deferrals, or scope cuts
4. Check for a **hold note** — holds can apply to the **whole issue** (e.g., "Hold documentation until the v2 flyout is fully assembled and confirmed as the shipped UI") or to **one deliverable within a larger issue** (e.g., a suggested-work table row for a specific page reading "Hold substantive edits until the Detections tab scope is confirmed" while the rest of the issue is ready to draft). Check every deliverable individually — don't assume a hold is all-or-nothing for the issue. When present, don't take the original note at face value either way:
   - If a later comment or an **AI Scoping** section claims the hold no longer applies (e.g., "both PRs are now merged"), verify that yourself — `gh pr view <number> --repo elastic/kibana --json state,mergedAt` — before trusting it
   - If the hold condition is still open (PR unmerged, behavior unconfirmed, feature flag still off), mark that deliverable (or the whole issue, if the hold is issue-wide) **Blocked** and stop for that scope; do not draft speculative UI documentation
   - Watch for **partial holds**: a scoping section may confirm one absorbed sub-feature shipped (e.g., a Visualizations accordion) while explicitly flagging another as still stubbed (e.g., "see all" links that are TODO no-ops in code) — draft only the confirmed part and note the stub as not-yet-documentable
5. Check for a **consolidation note** — e.g., "Consolidated issue... absorbs #7298." Treat the current issue as the sole authoritative source; don't separately fetch a closed/absorbed issue, and don't inherit scope or maturity labels from it that the consolidating issue doesn't restate

Track each deliverable through drafting with status:

| Status | Meaning |
|--------|---------|
| **Addressed** | Reflected in the draft |
| **Deferred** | Out of scope for this pass — note why (not yet implemented, or explicit scope cut) |
| **Blocked** | Cannot draft without an unresolved question, missing source, or an unresolved hold |

Present suggested work in the intake summary before drafting:

```markdown
## Suggested documentation work
| # | Suggestion (from issue) | Status |
|---|--------------------------|--------|
| 1 | Add Run and Settings buttons section | Addressed — see "Run and Settings buttons" section |
| 2 | Document GA promotion of the Attacks page | Deferred — pending implementation, not yet merged |
```

**Do not invent content that contradicts these suggestions.** If unclear, ask the user before drafting.

### 0d. Parse open questions

Scan the issue `body` and `comments` for unresolved items:

- Headings: `## Open questions`, `## Open items to confirm before publishing`, `## Questions`
- Checklist items still open: `- [ ] ...`
- Explicit markers: `TBD`, `TODO`, `⚠️`, `to be confirmed`, `Need input from`

For each question, classify as:

- **Resolved** — answered in the issue body, a comment, or a linked PR
- **Unresolved** — still open
- **Researchable** — answerable from Kibana source or published docs without asking the user (handle in Step 2)

### 0e. Ask the user to answer unresolved questions

If any questions are **Unresolved**, use `AskUserQuestion`. Ask only unresolved questions, batch related ones, and quote the original question text.

**Do not proceed to Step 2 (research) or Step 4 (draft)** until all unresolved questions are answered, or the user explicitly says to proceed with stated assumptions (record those assumptions in the output).

## Step 1: Classify the target page

| Page | Covers |
|------|--------|
| `solutions/security/ai.md` | Parent "AI for security" overview — links Attack Discovery, AI Assistant, Agent Builder |
| `solutions/security/ai/attack-discovery.md` | RBAC, setup, generating discoveries manually, schedules, sharing, bulk actions, search/filter |
| `solutions/security/ai/attacks-page.md` ("Triage and manage attacks") | The **Attacks** page: unified triage hub for attacks (scheduled + manually generated) alongside correlated alerts — filtering, status, assignment, tags, cases, workflows |
| `solutions/security/ai/triage-attack-discovery-findings.md` | Triage workflow for saved findings (ES\|QL/API examples) |

New capability areas that don't fit an existing page (most often automation/workflows content) typically become a **new child page** nested under `attack-discovery.md` in `solutions/toc.yml`. Check the issue for a proposed filename/nav title before inventing your own; if none is given, propose one and confirm with the user.

Run [`/content-type-checker`](https://github.com/elastic/elastic-docs-skills/tree/main/skills/authoring/content-type-checker) if the page type (how-to vs. reference vs. overview) is ambiguous — skip if not installed.

## Step 2: Research before writing

Never guess RBAC privilege names, index patterns, or UI copy. Gather facts first.

### Published docs (preferred)

Use the elastic-docs MCP (`https://www.elastic.co/docs/_mcp/`) or WebFetch on the same URLs:

1. `search_docs` — don't trust semantic search alone; pages gated behind `preview`, or a newly added child page, don't always surface
2. `get_document_by_url` with `includeBody: true` — fetch the actual target page and its siblings
3. `find_related_docs` — discover cross-link targets

### docs-content source

Confirm the current file inventory directly against `github.com/elastic/docs-content` (Grep/WebFetch `solutions/security/ai/` and `solutions/toc.yml`) before assuming a page does or doesn't exist yet — this is more reliable than search for a page that just shipped.

### Kibana / security-team source

When the issue links Kibana or security-team PRs/issues, read them for exact button labels, privilege names, feature-flag names, and index patterns rather than paraphrasing from the doc issue's description.

Check the linked PR diff for **stubbed or TODO code** (placeholder handlers, disabled buttons, no-op links) before documenting a UI element as functional — e.g., a "See all" link that's a TODO stub in the merged code should not be documented as a working navigation path yet.

Don't treat an AI Scoping section's **line-number citations** (e.g., "lines 146–158") as stable — locate the target section by heading text and read it fresh; line numbers drift as the file changes between when the scoping note was generated and when you draft.

Attack Discovery's data-anonymization behavior reuses **AI Assistant**'s settings — don't re-explain anonymization from scratch, cross-link to the AI Assistant settings docs instead.

## Step 3: Apply Attack Discovery authoring rules

These conventions are non-negotiable.

### Version gating

This feature's docs are heavily version-gated — new behavior almost never fully replaces old behavior, it layers on top per Stack/Serverless version.

1. **Read the full target page first.** Note how existing sections use per-version blocks (e.g. `{ "stack": "ga 9.4+", "serverless": "ga" }` admonitions, or separate RBAC variants for successive version ranges). When documenting a change, add a **new** version-gated block rather than rewriting an old one — instructions for older Stack versions must stay correct.
2. **Apply `applies_to` tagging** for any new lifecycle state or version-gated section — follow the [`applies-to-tagging`](https://github.com/elastic/elastic-docs-skills/tree/main/skills/authoring/applies-to-tagging) skill exactly (syntax, placement, validation rules).
3. Only widen a page's minimum supported version in frontmatter if the page's actual minimum requirement changed.

### Naming constraint

**Never publish internal version-shorthand names** like "Attack Discovery 2.0"/"AD 2.0" (or "1.0" for prior behavior), even if the source issue or PR uses that shorthand throughout. Describe changes by capability instead ("skill-augmented analysis," "scheduled runs," "workflow step"), and distinguish old vs. new behavior with `applies_to` version tags or an `applies-switch` block — never a version-number label in prose or headings.

### RBAC callouts

Any new capability that reads or writes discoveries/attacks needs a privilege statement: the Kibana feature privilege plus the Elasticsearch index privilege on `.alerts-security.attack.discovery.alerts-<space-id>` (and its `.internal.*` / `.adhoc.*` variants). Prefer linking to the existing RBAC section over duplicating the table; document only privileges that are genuinely new.

### Voice and style

- **Task-based H2s**, imperative mood, matching existing style: "Generate discoveries manually," "Schedule discoveries," "Take bulk actions."
- Use product substitutions (`{{product.kibana}}`, etc.), bold for UI elements, monospace for technical elements — never hardcode product names.
- Follow the [`page-opening-optimizer`](https://github.com/elastic/elastic-docs-skills/tree/main/skills/authoring/page-opening-optimizer) skill for the H1, opening paragraph, and "Before you begin" section on a brand-new page.

## Step 4: Draft the page

When a doc issue was provided, draft content that **addresses every item** in the suggested documentation work unless explicitly deferred (Step 0c). Map each suggestion to a section or follow-up edit.

- **New page**: create the file with frontmatter (`applies_to`, `description`, `navigation_title` if the H1 exceeds ~50 characters), H1 with anchor, opening paragraph, RBAC/"Before you begin" section, task steps.
- **Update**: locate the exact section by heading, insert new content adjacent to — never in place of — existing version-gated content.

### Frontmatter

```yaml
---
navigation_title: <Short nav label>
description: <One sentence — include "Attack Discovery" or "Attacks" and the specific topic>
applies_to:
  stack: ga 9.5
  serverless: ga
---
```

Consult [`/docs-syntax-help`](https://github.com/elastic/elastic-docs-skills/tree/main/skills/authoring/docs-syntax-help) for any directive (e.g., `applies-switch`, dropdowns) you cannot resolve from sibling pages — skip if not installed.

### Screenshots tied to a version-gated UI change

When new content replaces or sits beside a UI that changed shape (e.g., a legacy expand/collapse list vs. a new tabbed flyout), don't simply swap the existing screenshot. Match the file's existing pattern for versioned images — e.g., keep the old screenshot under the pre-change `applies_to` block and add a new, separately captioned screenshot under the new version-gated block — and flag in your output if no screenshot is available yet so the reviewer knows to add one before publishing.

## Step 5: Cross-link and navigation

After drafting:

1. Add links **to** the new/updated page from `ai.md`, the parent AD page, or the Attacks page as appropriate
2. Add or update a **Next steps** section (3–5 links)
3. Update `solutions/toc.yml` if adding a new file — nest new capability pages under `attack-discovery.md`; confirm placement with the user
4. If the change also affects the Attack Discovery API, note that API reference content is auto-generated from the OpenAPI spec — don't hand-write API reference content here, only conceptual/how-to docs
5. Remove duplicated content from hub pages — `ai.md` should summarize and link, not restate

## Step 6: Validate

Before presenting the draft:

1. Run `vale <file>` — style/voice (see [`docs-check-style`](https://github.com/elastic/elastic-docs-skills/tree/main/skills/review/docs-check-style) for interpreting results)
2. Run [`applies-to-tagging`](https://github.com/elastic/elastic-docs-skills/tree/main/skills/authoring/applies-to-tagging) on the file — confirm tags are correct
3. Validate outbound links — use elastic-docs MCP `get_document_by_url` (or WebFetch) to resolve each cross-link
4. If new page: run [`frontmatter-audit`](https://github.com/elastic/elastic-docs-skills/tree/main/skills/review/frontmatter-audit)
5. Cross-check the draft against the **suggested documentation work** table — every non-deferred item must be addressed or explained
6. Confirm no internal version-shorthand ("2.0", "1.0", "AD 2.0") made it into the draft

Report any items you could not verify against source, and note any companion skills or MCP tools that were unavailable.

## Output format

Present:

1. **Intake summary** — issue link, scope, **suggested documentation work** (with status per item), resolved and unresolved questions (omit if no issue was used)
2. **Page classification** — target file path(s), rationale
3. **Research summary** — source pages and Kibana/security-team references consulted
4. **Draft content** — full markdown with frontmatter, ready to write to docs-content
5. **Follow-up edits** — other files to update (`toc.yml`, `ai.md`, hub links); include deferred items from suggested doc work
6. **Open questions** — anything still needing SME review after drafting

If the user provided a file path, write the draft to that path. Otherwise, propose the path and show the content for review first.
