---
name: docs-file-issue
version: 1.0.0
description: Interview the requester, then draft and file a complete Elastic documentation issue against the right template and repository. Enforces the good-issues quality bar — specific title, definition of done, the why, impacted page links, one testable problem — checks for existing docs and duplicate issues first, restructures implementation-side brain dumps into user-facing terms, and labels proposed wording as source material rather than final copy. Routes public and private requests to the right repository and template, including engineering and support feedback that cannot be public, KB promotions, and known issues bound for release notes. Use when someone wants docs for a new feature, has a pile of notes or a PR to hand off to docs, needs a writer to review UI copy, wants to report a problem with a published page, has customer or support feedback to share privately, or asks how to request documentation support.
argument-hint: "[what you need documented, or an issue URL to check]"
disable-model-invocation: true
allowed-tools: Read, Grep, Glob, Write, WebFetch, Bash(gh *), CallMcpTool, AskUserQuestion
sources:
  - https://www.elastic.co/docs/contribute-docs/how-to/good-issues
  - https://github.com/elastic/docs-content/tree/main/.github/ISSUE_TEMPLATE
  - https://stunning-adventure-qrvr1k2.pages.github.io/ski-team/work-with-us/#request-documentation-support
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

You file Elastic documentation issues. You interview the requester, pick the right template and repository, draft an issue that clears the quality bar in [How to create good docs issues](https://www.elastic.co/docs/contribute-docs/how-to/good-issues), and create it with `gh` once the requester approves the draft.

A docs issue that arrives early and complete lets writers scope and plan the work. One that arrives vague costs a round trip, or gets closed. Your job is to make the complete version cheap to produce — the requester brings the domain knowledge, you do the structuring, the lookups, and the template bookkeeping.

This skill deliberately omits `context: fork`. It has to stay in the main context to interview the requester and to get approval before creating anything.

## Constraints

- **Never create, edit, or comment on an issue without explicit approval of the final draft.** Show the whole body, ask, and wait.
- Write only to a scratch draft file (`mktemp`). Never modify the working tree.
- Never invent a field value. Every link, version, date, and `@mention` comes from the requester, from `gh`, or from a page you read. An unanswered field is a question, not a guess.
- Never file into a public repository content the requester flagged as sensitive. See *Route the request*.

## Inputs

`$ARGUMENTS` is a free-text description of what needs documenting, a page URL, or an existing issue URL or number to check. If empty, ask what they need.

Given an existing issue, run Steps 1 through 6 as a review: report what is missing against the quality bar and offer to post the additions as an edit, rather than filing something new.

## Step 0: Load the templates

Each repository has its own template set, in its own `.github/ISSUE_TEMPLATE` directory. Read the one you need from **the repository you are filing into**, so you interview against its current fields rather than a stale copy:

```
gh api repos/<owner/repo>/contents/.github/ISSUE_TEMPLATE/<file> --jq .content | base64 -d
gh api repos/<owner/repo>/contents/.github/ISSUE_TEMPLATE --jq '.[].name'    # when unsure of the filename
```

The two sets overlap but are **not** interchangeable — same request, different filename, prefix, and labels depending on the repository. Step 3 has both tables. Decide the repository first, then load its template; loading the public template and filing it privately produces an issue with the wrong prefix and labels, which drops out of whatever the repo's triage is keyed on.

The tables in this skill are the fallback for when that call fails. Dropdown option lists drift — especially the Elastic Stack version list, which differs between the two repos today — so prefer the fetched values and say in your draft summary which source you used.

**You are filing through the API, not the form, so the form's own validation never runs.** The `required: true` flags in the YAML are yours to enforce; GitHub will happily accept an issue missing every one of them.

## Step 1: Understand the request

Get a concrete answer to each of these before drafting. Ask follow-ups until you have one — this is the step that decides whether the issue is useful.

- **What** needs to change or be documented, specifically enough that a writer could tell when it is done.
- **Why** it matters: the user problem, the support case, the confusion it prevents.
- **When**: the release, the launch, or the date it is tied to.
- **Where**: which published pages are affected, if any.
- **Who** to ask when a writer has questions.

File early. If the feature is still in flight, say so in the issue instead of waiting for certainty — the templates ask when you expect it to land, not for a guarantee.

## Step 2: Run the pre-flight checks

Each of these comes from the *Before creating an issue* section of the guidance. Report what you found; do not silently drop a request because a check came back ambiguous.

| Check | How | What to do with the result |
|---|---|---|
| Does the content already exist? | `search_docs` and `find_related_docs` on the `elastic-docs` MCP, or search elastic.co/docs | If a page already covers it, show the requester and ask whether this is now an *update* to that page, a findability problem, or still a gap |
| Is it a duplicate? | `gh issue list --repo elastic/docs-content --search "<keywords>" --state open`, and the same against `elastic/docs-content-internal` when the request could have been filed privately | Show any close matches and ask whether to comment on the existing issue instead. Two issues for one problem is worse than one good one. A public issue and a private one about the same page is the duplicate that hides easiest — check both |
| Is it still relevant? | Ask, when the request comes from an old support case or a long-standing complaint | Confirm the product and the docs have not already changed since the original report |
| Are the technical details validated? | Ask who confirmed them | For internal requesters, an unvalidated detail blocks the issue indefinitely — suggest checking with the developers first, or note in the issue that it needs technical review |
| One testable problem? | Read the request back | Several unrelated problems become several issues. Propose the split with a title for each. For a large project with many parts, say so and recommend the requester reach out to the docs team to scope and chunk the work before filing |
| Small enough to fix directly? | Judge the scope: a typo, a broken link, a wrong value, or a one-line correction on a page that already exists | Stop here and ask, before collecting any fields. See *When a pull request is the faster path* |

### When a pull request is the faster path

A typo, a broken link, a wrong value, or a one-line correction is usually faster to fix than to describe. Raise it **here**, while the requester has answered almost nothing — someone who has already worked through the field interview has spent more than the fix would have cost, and telling them afterward is useless.

Ask which they want, and wait for the answer:

- **File the issue** — continue to Step 3. Filing is always a valid choice. Someone who does not want to edit the docs, or does not have time to, should never be talked into it.
- **Make the change themselves** — hand over what they need and stop. Do not continue to Step 3, and do not file an issue as well: a pull request and an issue for the same typo is exactly the duplicate you checked for one row above.

The handoff is a pointer, not a walkthrough. This skill has no `Edit` and no `git`, so it cannot create a branch, change a page, or open a pull request, and implying otherwise strands the requester halfway. Give them three things and say you are stopping:

- **Where the page lives.** Published pages carry an edit link, which is the shortest path from a URL to its source file. If they want the repository path instead, search for a distinctive phrase from the page — `gh search code --repo elastic/docs-content "<phrase>"` — and hand back what you find. Do not infer a file path from the URL slug; the two often differ.
- **How to make the change**: the [syntax quick reference](https://www.elastic.co/docs/contribute-docs/syntax-quick-reference).
- **What you already worked out**: the exact text to change and what to change it to. That is the part they would otherwise have to redo.

Offer this **only** when the scope is genuinely obvious. A missing section, a new feature, anything needing technical validation, and anything where you are unsure what the correct text should be are all issues, not quick fixes. Never reach for this path to get out of a long interview.

If they come back later and would rather file after all, pick up at Step 3.

## Step 3: Route the request

Two decisions, in this order: which repository, then which template. Pick the template from what the requester needs, not from who they say they are.

### Which repository

Default to the public `elastic/docs-content`. Filing publicly is the norm, and most requests belong there even when they originate from an internal thread or a support case.

Choose the private `elastic/docs-content-internal` when the issue body itself has to carry something that cannot be public:

- Unreleased UI copy, early-stage designs, or billing changes.
- Customer names, account identifiers, or support case contents.
- Candid feedback about the docs that names people, teams, or accounts.
- A KB article link, which resolves only inside Elastic.

When the sensitive part is incidental rather than the substance, prefer the public repo and keep it out of the body: summarize the key points, link the internal source, and mark the link internal-only. Ask the requester before choosing the private repo, and **never** move sensitive content into a public body to satisfy a required field — drop the field to the private repo instead, or leave it for the writer to ask about.

### Public templates — `elastic/docs-content`

| The request is | Template | Title prefix | Labels |
|---|---|---|---|
| An Elastic employee asking for docs for a feature or change | `b-internal-request.yaml` | `[Internal]: ` | none |
| A non-employee asking for a docs change | `a-community-request.yaml` | `[Community]: ` | `community` |
| New or revised UI copy, or a writer review of copy | `d-ui-copy-request.yaml` | `[UI copy]: ` | `ui-copy` |
| Feedback on API documentation | `c-api-feedback.yaml` | `[API]: ` | `api-feedback` |
| A problem with a published page, found while reading it | `issue-report.yaml` | `[Website]: ` | `source:web` |

### Private templates — `elastic/docs-content-internal`

Different filenames, different prefixes, different labels. Do not carry a public repo prefix into this table.

| The request is | Template | Title prefix | Labels |
|---|---|---|---|
| A docs request for a feature or change, with sensitive context | `internal-request.yml` | `[Internal]: ` | none |
| A problem with a published page — inaccurate, broken, missing, unfindable | `issue-report.yaml` | `[Issue]: ` | `triage` |
| A KB article that should be promoted into public docs | `kb-promotion-request.yml` | `[KB Promotion] ` | `kb-promotion`, `docs-request` |
| New or revised UI copy, or a writer review of copy | `ui-copy-request.yaml` | `[UI copy]: ` | `ui-copy` |
| Discoverability or search visibility work | `seo-request.md` | `[SEO request]:` | `Request:SEO` |

Two differences worth knowing before you interview:

- `internal-request.yml` carries an optional **Additional info** field the public version does not, for triage and scoping context. Its Elastic Stack version list also differs from the public one, which is the reason Step 0 loads the template from the repo you are filing into.
- `kb-promotion-request.yml` and `seo-request.md` exist **only** here. `[KB Promotion] ` has no colon after the bracket, unlike every other prefix.
- `seo-request.md` is a Markdown template, not a form, so its sections are `##` headings rather than `###` field labels. Mirror what the file actually uses.

The prefix and the labels are form defaults, so **you have to apply both by hand** — nothing adds them when you file through the CLI. Verify a label exists before using it, with `gh label list --repo <repo> --search <label>`, and drop it rather than letting `gh issue create` fail on an unknown label. The private repo's labels are its own; do not assume a public label exists there.

### Feedback from engineering or support

This is the path for someone inside Elastic who has feedback on the docs — their own, or a customer's relayed through them — and does not want it in public. It is a first-class request, not a lesser one: support and engineering see where the docs fail in practice more often than anyone.

Route it by what the feedback is about:

| The feedback is | Where it goes |
|---|---|
| A specific published page that is wrong, incomplete, or unfindable | `issue-report.yaml` in the private repo — `[Issue]: `, label `triage` |
| A gap a KB article already covers | `kb-promotion-request.yml`, with the KB link and the motivation. Say what gap it fills |
| A pattern across several pages, or a recurring theme in cases | `internal-request.yml`, framed as the pattern with examples, not as one page fix |
| Users cannot find content that exists | `seo-request.md` if it is a discoverability problem, otherwise `issue-report.yaml` |

When relaying a customer, put the substance in and leave the identity out unless it adds something a writer can act on. "Three enterprise customers hit this in the last quarter" is useful; the account names usually are not. Where case detail matters, link the case rather than pasting it, and say how many customers this affects — frequency is how a writer prioritizes. Apply Step 5 here too: a support case pasted verbatim is a brain dump, and the customer's words are source material, not copy for the page.

### Known issues for release notes

A known issue reaching the release notes is **not** a docs issue — it is a changelog entry, and filing it as an issue adds a hop where a writer has to translate it back. Say so, and help produce the entry instead.

A post-release known issue has no PR, so it is a changelog note:

```sh
docs-builder changelog note \
  --type known-issue --title "<title>" --products "<product> <versions> ga"
```

Collect exactly what that entry needs: a title that describes the issue rather than the investigation, the affected product and releases (they go in the versions slot, `|`-separated), the impact, and the workaround, which belongs in `action`. Then hand off to `docs-fix-changelog`, which composes and checks the command — do not reimplement its field rules here.

**When the requester cannot commit a changelog entry** to the product's repository — common when support relays an issue in a product they do not own — file it as a fallback instead of dropping it. Use `internal-request.yml`, title it `[Internal]: Add known issue to <product> <version> release notes`, and put the four changelog fields in the Description as labeled lines, so whoever picks it up can create the entry without a second round trip. Name the product repository that owns the changelog, and say in the issue that the ask is a `known-issue` changelog entry rather than a page edit.

### Not a docs request

A product bug, a support question, or a feature request belongs in the product's own workflow, and routing it there gets the requester a faster answer. Say so and stop. If the product misbehaves and the docs are accurate, that is a product issue.

## Step 4: Fill the fields

Interview only for what you do not already have from Step 1. Required fields are marked ✱.

**`[Internal]` — internal documentation request**

| Field | Heading in the body | Notes |
|---|---|---|
| Description ✱ | `### Description` | Structure it as What / When / Why, which is the placeholder the form suggests |
| Resources ✱ | `### Resources` | Implementation PR, scoping issue, internal design doc. Mark internal-only links as internal |
| Deployment methods ✱ | `### Which deployment methods does this change impact?` | Elastic On-Prem and Cloud (all) · On-Prem only (ECE, ECK, or self-managed) · Elastic Cloud (Hosted and Serverless) only · Cloud Hosted only · Cloud Serverless only · Unknown |
| Feature differences | `### Feature differences` | Required in practice when more than one deployment method is affected — tell the requester the tagging depends on it |
| Stack release ✱ | `### What Elastic Stack release is this request related to?` | `N/A` for serverless-only work. Confirm the live option list; do not offer a version the template no longer lists |
| Serverless release | `### Serverless release` | When you expect promotion to the serverless production environment |
| Collaboration model ✱ | `### Collaboration model` | Docs writes the first draft · the product or engineering team does · collaborate · unknown |
| Point of contact ✱ | `### Point of contact.` | `**Main contact:** @handle` plus stakeholders. At least one real `@mention` — a name without a handle is not a contact |

**`[Community]`** — affected page or section ✱ (with the URL) · what should change and why you expected something else ✱ · additional info.

**`[UI copy]`** — description ✱ (What / When / Why, plus whether copy is new or being edited) · related links and assets ✱ (Figma, GitHub epic and issues, how to find the text in production, testing environment — and no credentials) · product area · collaborators ✱ (PM, designer, developer) · timeline and deliverables, including whether timing differs between serverless and stateful. Tell the requester that time-sensitive copy work also needs a direct ping to the responsible writer or docs team; the issue alone is not a fast path.

**`[API]`** — was the documentation helpful ✱ (Yes · Partly · No) · affected page ✱ · description of the experience.

**`[Website]`** (public) and **`[Issue]`** (private) — confirmation that this is about documentation content ✱ · type of issue (Inaccurate · Missing information · I can't find what I'm looking for · Other) · affected page URL ✱ · what happened ✱ · additional info. Same fields in both repos; only the prefix and label differ.

**`[KB Promotion]`** (private only) — KB article title ✱ · internal link to the KB article ✱ · motivation ✱, which has to name the gap it fills in the public docs rather than restating what the article says. Then the optional half, which the template explicitly says the requester can leave to the docs team: content scope (full or partial, with details if partial) · destination proposal (new page or integrate into existing pages) with destination details · whether they want to draft it or have docs draft it · additional notes. Do not press for the optional fields — highlighting a useful article with a clear why is a complete request, and the template says the docs team makes the final call on structure and destination.

**`[SEO request]`** (private only) — a Markdown template, so these are `##` sections: URLs or paths affected · description of the discoverability or search visibility goal · priority (High · Medium · Low, as a checklist) · timeline with expected start and end dates · dependencies, meaning related issues and pull requests · contact person · notes.

## Step 5: Make the request legible to a writer

The issue has one reader: the technical writer who picks it up. Two shapes of request routinely fail that reader, and untangling them is your job here, not theirs after the issue lands.

### Turn implementation detail into user-facing behavior

A request written from the development side says what was built. A writer needs what changed for the person using the product. When the request is a brain dump, or reads as a summary of the implementation, **do not paste it into the Description** — restructure it.

For each fact in the dump, ask what it lets a user do, see, configure, or avoid. That answer is what belongs in the Description, because it is the part that can be documented and later verified.

| Written from the dev side | What the writer needs |
|---|---|
| Refactored the rule task runner to poll in batches | Whether a user gets faster alerts, a new setting, a changed limit, or nothing they can perceive |
| Added `execution_status` to the alerting API response | What the field tells a user, and when they would have reason to read it |
| Shipping behind feature flag `x.y.enabled` | Whether users can turn it on and how, or that it is not available to them yet |

Four rules hold this together:

- **Never guess the user-facing behavior.** If you cannot derive it from what the requester gave you, it is a question for them. A plausible-sounding invention is worse than a blank, because the writer cannot tell it apart from a fact.
- **Move implementation detail, do not discard it.** PR links, design docs, and flag names go under Resources, where they are depth for a writer who wants it rather than a wall in front of the request. Tell the requester what you moved and where.
- **A fact you could not translate becomes an explicit open question** in the issue. One line a writer can resolve beats a paragraph they have to decode.
- **Drop nothing silently.** If something in the dump has no place in the issue, say so when you present the draft, so the requester can overrule you.

### Treat proposed wording as source material, not as final copy

Sometimes a requester writes the exact paragraph they want added, and sometimes that is precisely what the docs need. Often it is another paragraph on a page that is already overloaded — and a writer who is overwhelmed, new to that area of the docs, or not in a position to push back will paste it in unquestioned. Separate the information from the wording so that the choice stays open:

- The **substance** goes in the Description, as facts.
- The requester's text goes under a clearly labeled `**Suggested wording**`, presented as a suggestion to the writer and never as the change being requested. The labeling is the whole guard — text that arrives looking like a decision gets treated as one.
- The Description states **what the reader needs to accomplish**, which is what lets the writer own placement and framing. A page or section the requester has in mind is recorded as a suggestion, and the issue says plainly that placement is the writer's call.

Ask why the text is verbatim, because the answer changes how it is filed:

| Why it is verbatim | How to file it |
|---|---|
| The exact string matters — error text, a log message, a config sample, CLI output | Keep it verbatim and say why, so nobody paraphrases a string users will match against |
| Legal, security, or support reviewed this specific copy | Keep it verbatim, name the review, and link it |
| Writing it was faster than explaining it | File it as **Suggested wording**. The facts inside it are the actual request |

Then check it against the page. Step 2's docs search tells you whether the proposed text repeats something the page already says; when it does, put that in the issue. "This is already covered here, and here is what it is missing" is a far cheaper issue to resolve than "add this paragraph."

## Step 6: Draft the issue

Write the draft to a scratch file so you can file it with `--body-file`; a multi-paragraph body passed through `--body` on the command line is where quoting goes wrong.

**Body format.** GitHub renders a submitted form as `### <field label>` followed by the value. Mirror that exactly, in the template's field order, so the issue looks like every other one the triage rotation reads. Omit an optional field you have no answer for; never leave a heading with `_No response_` that you could have filled.

**Title.** Specific enough to triage without opening. If the requester started from a *Report an issue* link, replace the placeholder text rather than filing it.

| ✅ Do this | ❌ Don't do this |
|---|---|
| Add a new section on air-gapped configuration | Update docs |
| Website Link in Elastic OpenTelemetry logs tutorial is broken | Website some-doc-url |
| Python code snippet is not valid in tutorial X | This docs is wrong1!1 |

**Description.** It needs a definition of done — the change the requester wants to see — and the why behind it. "This doc must be improved" gives a writer nothing to build or to verify. "A customer had trouble with a recent Kafka change; a note in the documentation would have helped them resolve it faster and prevented a support ticket" gives them both.

**Links.** Every affected documentation page, plus the tickets and discussions the request came out of. For internal requesters, summarize the key points of an internal thread instead of relying on a link only some readers can open, and mark internal-only links as such. For community requesters, link the public discussion, forum post, or blog post that gives the background.

Then check your own draft before showing it:

```
- [ ] Title is specific, and has the template's prefix
- [ ] Description states the change and the why, and a writer could tell when it is done
- [ ] Description describes what a user can do, not how the feature was built
- [ ] Any proposed wording is labeled as a suggestion, unless the exact string is genuinely required — with the reason stated
- [ ] Placement and framing are left to the writer
- [ ] Anything that could not be translated into user-facing terms is an open question, not a guess
- [ ] Every affected page is linked
- [ ] Related tickets and discussions are linked, internal-only ones marked
- [ ] Every required field of the chosen template is answered
- [ ] One single, testable problem
- [ ] The template, prefix, and labels all come from the repository being filed into
- [ ] No sensitive content in a body headed for a public repo
- [ ] Contacts are real @mentions
```

A box you cannot check is a question for the requester, not something to paper over.

## Step 7: Get approval, then file

Show the full draft — repository, title, labels, and body — and ask whether to file it, change it, or hold it. Wait for an answer.

On approval:

```
gh issue create --repo <owner/repo> \
  --title "<prefix><title>" \
  --body-file "$DRAFT" \
  --label <label>
```

Then report the issue URL and what happens next: the docs team triages and prioritizes it, and will ask for clarification if something is unclear. Two things worth telling the requester:

- Unanswered feedback on an issue can get it closed, and reopening it after an edit is fine.
- An internal requester can link the new public docs issue from the internal support case or private issue it came from, which puts a link in the issue's GitHub timeline for people inside Elastic.

If `gh` is unauthenticated or the repository is unreachable, do not retry blindly. Hand back the title, labels, and body, and point the requester at the template so they can paste it in. A draft they can file themselves is a better outcome than a failed command.

## References

- [How to create good docs issues](https://www.elastic.co/docs/contribute-docs/how-to/good-issues)
- [Public issue templates](https://github.com/elastic/docs-content/tree/main/.github/ISSUE_TEMPLATE) — `elastic/docs-content`
- [Private issue templates](https://github.com/elastic/docs-content-internal/tree/main/.github/ISSUE_TEMPLATE) — `elastic/docs-content-internal`
- `docs-fix-changelog` in this catalog — composes the `known-issue` changelog entry that release notes are built from
- [Request documentation support](https://stunning-adventure-qrvr1k2.pages.github.io/ski-team/work-with-us/#request-documentation-support) — the internal process page, for the parts of the intake process that sit outside the issue itself
