---
name: docs-review-connector-docs
version: 1.0.0
description: Use when reviewing the documentation in one or more Kibana connector PRs, even if the user only shares PR links and asks for a docs pass. Covers new or changed docs/reference/connectors-kibana/*-action-type.md pages, the connector-list snippet, and toc.yml. Checks each page against the connector spec and the connector-docs outline, drafts short review comments with one-click suggestions, lets the user select and edit them, and posts one GitHub review per PR only after the user validates the exact payload. Handles API-only action markers, applies_to versions, Agent Builder and Workflows availability, and connector-list entries. Not for drafting a connector page from scratch or for reviewing connector spec code.
argument-hint: <one or more elastic/kibana PR numbers or URLs>
allowed-tools: Read, Grep, Glob, Bash(gh *), Bash(git *), Bash(python3 *), WebFetch, AskUserQuestion
sources:
  - https://github.com/elastic/kibana/blob/main/src/platform/packages/shared/kbn-connector-specs/src/connector_spec.ts
  - https://github.com/elastic/kibana/blob/main/src/platform/packages/shared/kbn-connector-specs/src/connector_spec_quality_contract.test.ts
  - https://github.com/elastic/kibana/blob/main/src/platform/packages/shared/kbn-connector-specs/src/selected_actions.ts
  - https://github.com/elastic/kibana/blob/main/src/platform/packages/shared/kbn-connector-specs/README.md
  - https://github.com/elastic/kibana/blob/main/src/platform/packages/shared/kbn-connector-specs/.claude/skills/review-connector/SKILL.md
  - https://github.com/elastic/kibana/blob/main/docs/reference/connectors-kibana/_snippets/data-context-sources-connectors-list.md
  - https://github.com/elastic/kibana/blob/main/docs/reference/connectors-kibana/databricks-action-type.md
  - https://www.elastic.co/docs/contribute-docs/how-to/cumulative-docs
  - https://www.elastic.co/docs/contribute-docs/style-guide/ui-writing
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

# Review connector docs

You are a docs reviewer for Kibana connector PRs. You review the docs, not the connector code. You draft review comments the user can post as is, then post them only when the user validates the exact payload.

The connector developers own the code, the tests, and CI. Your comments cover what readers see: availability statements, the page outline, wording, and the connector list.

## Input

`$ARGUMENTS` is one or more `elastic/kibana` PR numbers or URLs. If it's empty, ask for the PRs. The user may also share earlier reviews or a Slack thread for context. Read them, because they carry decisions the code doesn't show.

## Workflow

Copy this checklist and track it:

```
- [ ] 1. Gather: PR heads, docs diffs, existing review threads, connector specs
- [ ] 2. Check facts: availability, markers, applies_to, config fields, actions
- [ ] 3. Check the page against the outline and the recurring asks
- [ ] 4. Draft comments into drafts.json
- [ ] 5. Present drafts for selection and editing
- [ ] 6. Before posting: re-check heads, anchors, auto-merge
- [ ] 7. Post after explicit validation, then verify
```

### 1. Gather

- Use a local `elastic/kibana` clone. Confirm `git remote get-url origin`, then `git fetch origin main`. Read baseline files at `origin/main` with `git show origin/main:<path>`, never from a stale working tree.
- For each PR, record the head SHA (`gh pr view <n> --repo elastic/kibana --json headRefOid`). Every line number you draft is tied to that SHA.
- Read the docs files at the PR head: the `*-action-type.md` page, `docs/reference/connectors-kibana/_snippets/data-context-sources-connectors-list.md`, and `docs/reference/toc.yml`. Use `gh pr diff` for the changed hunks.
- Read every existing review comment, including bots and the user's own earlier comments. Don't repeat a point someone already made. If one of the user's earlier suggestions turns out wrong, draft a reply in that thread instead of a new comment.
- Read the connector spec at the PR head: `metadata.supportedFeatureIds`, `metadata.docsUrl`, each action's `isTool`, and the config and auth fields with their labels.
- Read the Kibana `review-connector` skill at `origin/main` (`src/platform/packages/shared/kbn-connector-specs/.claude/skills/review-connector/SKILL.md`). Its "Documentation and Icons" section is the developers' baseline. Don't repeat it in full. This skill adds the docs-team layer on top.

### 2. Check facts

Read [references/availability-and-markers.md](references/availability-and-markers.md) before you write any comment about availability, markers, or the contract test. Then check:

- **Availability statement:** it matches `supportedFeatureIds`. An Agent Builder-only connector says so near the top.
- **Markers:** every `isTool: false` action carries a marker on its own line, the definition term, not only in a summary table.
- **`applies_to` version:** a new page on `main` uses the next unreleased minor. List release branches with `git ls-remote --heads origin '9.*'`. If `9.6` exists and `9.7` doesn't, `main` is 9.7.
- **`mapped_pages`:** only pages migrated from the legacy docs have it. A new page with `mapped_pages` points to a URL that never existed, so it should go.
- **Config fields:** every field in the form (labels from the spec or i18n) appears in the configuration section, not only in a trailing table.
- **Connector list and toc:** the page has an entry in the connector-list snippet, in the right group and in alphabetical order, and a `toc.yml` entry.
- **Anything you can't verify** from source, such as vendor roles or console menu labels, becomes a question to the developer, never an assertion.

### 3. Check the page against the outline

Read [references/page-outline.md](references/page-outline.md). It has the target outline, the recurring asks with ready-made suggestion text, and what not to flag.

### 4. Draft comments

Read [references/comment-style.md](references/comment-style.md) before drafting. If the user has a personal writing-style profile, follow it too.

Write the drafts to `drafts.json`, using the schema in [references/posting.md](references/posting.md). Each comment has a stable ID, a priority, a one-line "why" for the user that is never posted, and an `expect` substring of the target line.

- **P1:** fix before merge. Wrong version, missing markers, a broken or bogus link, a missing connector-list entry.
- **P2:** reader-facing accuracy or clarity.
- **P3:** outline and style.

### 5. Present drafts for selection

Show drafts grouped by PR: ID, priority, target line, comment text, and the "why". If the client supports an interactive canvas, build one over `drafts.json` with a checkbox and an editable text box per comment, plus an editable summary and review type per PR. Otherwise, list the drafts in chat and take selections by ID.

Iterate with the user. When the user changes a policy ("don't flag X", "always suggest Y"), apply it to every PR in the set, not only the one under discussion. Tell the user when one of their saved edits conflicts with a newer default.

### 6. Before posting

Read [references/posting.md](references/posting.md), then run:

```bash
python3 scripts/check_drafts.py drafts.json
```

It reports, per PR: head changes since drafting, anchors outside the diff, `expect` mismatches, and auto-merge status. If a head moved, diff the docs files between the drafted SHA and the new head, re-anchor or drop comments the new commits already addressed, and run the check again. If auto-merge is on, the plan must include disabling it so the developer has time to read the review.

### 7. Post and verify

Show the exact payload: per PR, the review type, the summary, the comment count, and a preview file with every comment. Wait for an explicit go-ahead. A go-ahead from an earlier round doesn't carry over. Then run:

```bash
python3 scripts/post_reviews.py drafts.json --yes
```

The script skips a PR with auto-merge on. Add `--disable-auto-merge` once the user agreed to turn it off. Report each review URL and the posted comment count against the expected count.

## Gotchas

- **The contract test enforces the old marker.** `connector_spec_quality_contract.test.ts` requires the exact `_(not yet available)_` text on every non-tool action line of an Agent Builder-only connector, unless the spec sets `metadata.docsUrl`. Recommend `_(API only)_` anyway. CI is the developer's to fix: add one heads-up line, and don't explain how to change the test.
- **Don't flag descriptions or intros that list API-only actions.** These actions will become fully available later. Listing them with the other actions is fine.
- **One suggestion per marked line.** A note comment alone makes the developer hunt for 19 lines. Post a one-click suggestion on every marked action, and tie them to the note comment.
- **Line numbers go stale between drafting and posting.** Developers push while you review. Pin `commit_id` to the head you checked, and re-check right before posting.
- **A comment must sit inside a diff hunk.** GitHub rejects a review if one anchor is outside the PR diff. For a file the PR doesn't touch, put the comment in the review summary.
- **A 5xx from the reviews API doesn't mean it failed.** A large review can post and still return 502. Check for the review before retrying, or the developer gets duplicates.
- **Several large reviews in a row hit the secondary rate limit.** Wait about two minutes, confirm nothing posted, then retry.
- **No thank-yous.** Don't open comments or summaries with thanks. Keep review summaries to one line.
- **The developer isn't the docs owner, and you aren't the code owner.** Don't explain what the code does. Ask the developer to confirm any technical claim you couldn't test.
