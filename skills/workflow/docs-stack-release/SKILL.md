---
name: docs-stack-release
version: 1.6.7
description: >-
  Coordinate Elastic Stack docs releases: classify versions, route 8.x vs 9.x
  PRs, edit elastic/dev tracking issues, handle same-GA supersession, draft
  Slack #docs reminders, and watch docs-internal-workflows deploys. Use when
  the user says "how's my release", "how's my release doing", or asks for
  release status; also when coordinating docs releases, opening coordinator
  PRs, editing elastic/dev issues, drafting release reminders, or working with
  assembler.yml, versions.yml, or conf.yaml.
argument-hint: <versions and/or issue numbers>
sources:
  - https://github.com/elastic/dev
  - https://github.com/elastic/docs-builder
  - https://github.com/elastic/docs-internal-workflows
  - https://github.com/elastic/docs-content-internal/blob/main/docs/releases/elastic-stack-v9.md
  - https://github.com/elastic/docs-content-internal/blob/main/docs/releases/elastic-stack-v8.md
  - https://github.com/elastic/dev/blob/main/.github/ISSUE_TEMPLATE/docs-release.md
  - https://github.com/elastic/dev/blob/main/.github/ISSUE_TEMPLATE/docs-patch-release.md
  - https://github.com/elastic/dev/blob/main/.github/ISSUE_TEMPLATE/docs-patch-release-8.x.md
allowed-tools: Read, Write, Glob, Bash(gh *), Bash(git *), CallMcpTool
---

**Docs release issue** (`[Docs release] X.Y.Z` in `elastic/dev`) is the source of truth -- not the eng `[Release]` issue. Create missing docs issues (§1.1) or collect dates from the user. Missing issue URLs: `(issue TBD)`.

**Playbooks:** [v9](https://github.com/elastic/docs-content-internal/blob/main/docs/releases/elastic-stack-v9.md) -- [v8](https://github.com/elastic/docs-content-internal/blob/main/docs/releases/elastic-stack-v8.md). **Templates:** [minor](https://github.com/elastic/dev/blob/main/.github/ISSUE_TEMPLATE/docs-release.md) -- [9.x patch](https://github.com/elastic/dev/blob/main/.github/ISSUE_TEMPLATE/docs-patch-release.md) -- [8.x patch](https://github.com/elastic/dev/blob/main/.github/ISSUE_TEMPLATE/docs-patch-release-8.x.md).

| Line | Repo | Config files | Deploy watch |
|------|------|----------------|--------------|
| **9.x+** | `elastic/docs-builder` | `config/assembler.yml`, `config/versions.yml` | `docs-internal-workflows` bump PRs + prod version-bump (§0.3) |
| **8.x / 7.x** | `elastic/docs` | `shared/versions/stack/*.asciidoc`, `conf.yaml` | **None** -- do not use `docs-internal-workflows` |

## Invariants

- IDs, dates, PR URLs, @mentions: from `gh`, the docs issue, Slack, or the user. Never invent. Missing → `(issue TBD)` or `[@handle]` and ask.
- Never mix 8.x and 9.x in one PR. 8.x/7.x: `elastic/docs` only; no `docs-internal-workflows`.
- Checklist is the step index. Live-fetch only open work. RN merge is not a checkbox -- always `gh pr view` blocking RN URLs.
- A PR URL in the RN table is blocking until merged. Skip only `No changes` / `N/A`. Do not exempt Fleet, Agent, or any product by name.
- Check boxes this skill just completed. Do not check anyone else's work (including docs-eng). Do not wait to be asked.
- Slack: read [slack-templates.md](./slack-templates.md) before drafting or sending. Confirm before send; thread follow-ups on the FF announcement.
- Live/released Slack only after the **gate** (§0.3) and a user eyeball of the site. Do not draft before the gate.
- Empty args / "how's my release": session state → active docs issue. Do not ask which version if one is in flight. After closed-issue cleanup leaves none, stop -- do not rediscover.
- Cleanup = docs issue `CLOSED` only. 404 = drop that ID and rediscover. No TTL.
- RC varies each release -- read from the `#mission-control` coordination thread or eng issue. Never hardcode a name.
- Do not offer a Slack ping or PR whose issue box is already checked, or that the user already said they sent.

---

## Inputs

`$ARGUMENTS` is a space-separated list of semver versions and/or `elastic/dev` issue numbers (e.g. `9.4.0 9.3.4 8.19.15` or `#1234 #1235`). If empty: load session state (§0.1). If it has an **active** release (anticipated date is today, in the last 2 days, or tomorrow, and the docs issue is not CLOSED), use that. Otherwise ask.

**"How's my release" / "how's my release doing"** (no versions given): empty-args status. Load session state and run §0. Do not ask which version if an active release is in state. If cleanup left no versions, say the tracked issues are closed and stop.

Match the user's request to the relevant section (status, PRs, reminders) -- they may skip the full pipeline.

---

## 0. Check status (run on every invocation)

When versions or issue numbers are known (from `$ARGUMENTS` or session state), check state before proposing actions.

### 0.1 Session state (fast path)

**Path:** `~/.elastic-docs/stack-release-state.json`. Local coordinator cache -- never commit it.

**On every invocation:**

1. Read the file. Fall back to scratch if missing, unreadable, invalid JSON, no matching version, or the user says "start fresh".
2. Cached **IDs only** skip discovery: `docsIssue`, `engIssue`, `coordinatorPrs.{repo:{number,sha,url}}`, `rnPrs[].{product,url}`, `slack.{docsChannelId,docsFfThreadTs,missionControlChannelId,coordinationThreadTs,beginPublishingTs,handles}`, `deploys` (9.x only: `configSha`, `stagingBumpPr`, `prodBumpPr`, `stagingRunId`, `prodRunId`). Also `line`, `type`, `anticipatedDate`.
3. **Live-refresh only what the docs issue still has open** (§0.2). Do not re-`gh pr view` / `gh run view` checked lines. Always live-refresh RN PR merge state (the table stores URLs, not merge). Never trust cached JSON for merge/deploy conclusions; do trust a **checked issue line that already cites a PR or run URL**.
4. Cached ID 404 / missing message: drop that field and rediscover just that piece. Empty `slack_read_thread` on a Buildkite/bot parent (`begin publishing`, `release build declared`) is **not** a 404.
5. End of §0: drop CLOSED docs issues, then write or delete the file.

`deploys` is 9.x only. Omit it for 8.x / 7.x.

**Closed-issue cleanup:** Finished only if `state` is `CLOSED`. Report status this turn, then drop that version from `releases` and `active`. `announced` while OPEN is not enough. A 404 is not finished -- drop `docsIssue` and rediscover (step 4).

- **Some versions still open:** write remaining entries + `updatedAt` now. Mention which version was dropped.
- **None remain:** **delete** the file. Do not write `{ "active": [], "releases": {} }`. Mention that local state was cleared.

### 0.2 Stage from the docs issue (do this before extra fetches)

After session state, the first GitHub call is `gh issue view`. Parse checkboxes immediately. Jump to that stage. Do not walk §1–§5. Do not re-verify checked lines.

```bash
gh issue view <N> -R elastic/dev --json body,state
```

| If the issue shows | Stage | Live-fetch only |
| --- | --- | --- |
| Docs issue **CLOSED** | done / cleanup | None. Report closed, then closed-issue cleanup (§0.1). |
| Day-before ping or coordinator-PR box **unchecked** | pre-release | Coordinator PR search (if no cached number) + RN table URLs. Skip `#mission-control` and §0.3. |
| Coordinator PR **checked**, merge-RN ping **unchecked** | waiting to tell writers | RN PR states + (release day only) cached `#mission-control` threads. |
| Config-merge / prod-bump (9.x) / `elastic/docs` PR (8.x) **unchecked** | waiting on publish infra | That PR/deploy (§0.3 for 9.x) + RN PR states + cached `#mission-control` threads. |
| Prod-bump line **checked** with a run URL (9.x), or `elastic/docs` merge **checked** (8.x) | waiting on RNs / announce | **RN PR merge states only.** Skip coordinator `gh pr view`, bump PRs, `gh run view`. |
| Website-confirm and `#mission-control` live boxes **checked** | announced | Report done. No extra fetches unless the user asks. |

**RN merge is never a checkbox.** Always `gh pr view` each blocking RN URL.

If a checked line's cited URL 404s, rediscover **that line only**.

Stakeholder resolution (§ below): run **only** when a row still has a placeholder, a "specify who's responsible" footnote, or 2+ named people. Skip the `#docs` FF-thread search when every row already has a single named stakeholder.

### GitHub state

If session state has the docs issue number, `gh issue view` it directly. Otherwise search `[Docs release] <version>`. **Do not** `gh pr list` by version if the issue or session state already has the coordinator PR URL.

Search coordinator PRs only when §0.2 still needs them, **and only in the repo for that line** (9.x → `docs-builder`, 8.x → `docs`). Never `gh pr list` `elastic/docs` for a 9.x-only batch.

```bash
gh pr list -R elastic/docs-builder --search "<version>" --json number,title,state,url
gh pr list -R elastic/docs --search "<version>" --json number,title,state,url
```

- **Issue checkboxes:** If an item is unchecked but this skill already completed it (a Slack message you sent, a PR you opened), check it now using §4. Do not ask. Do not check items for work this skill did not do.
- **RN PR status:** One shell loop over every PR URL in the Release Notes table:

```bash
gh pr view <url> --json state,mergedAt,title
```

**Skip vs blocking:** Skip only `No changes` / `N/A`. A **PR URL is blocking** until merged -- do not exempt Fleet, Agent, or any other product by name. Named stakeholder is the owner; do not add `?` on a named row.

Report: X/Y merged (skipping N/A rows), Z outstanding. When all blocking RN PRs are merged: "All RN PRs merged."

**Then, by line -- only if §0.2 says publish infra is still open:**
- **9.x:** After the `docs-builder` coordinator PR is merged **and** the prod-bump issue line is still unchecked, continue to §0.3. If that line is already checked with a run URL, skip §0.3.
- **8.x / 7.x:** Skip §0.3. Config lives in `elastic/docs`. No `docs-internal-workflows` bump or deploy.

### Resolve stakeholder assignments

Run only when a row still needs it (§0.2). Cases: backtick placeholder (e.g. `` `Beats point person` ``) or "specify who's responsible" footnote; 2+ named people and one confirmed in thread; named stakeholder out and someone else confirmed covering.

1. FF announcement thread (`slack_search_public` for the version in `#docs`, then `slack_read_thread`).
2. Scan replies: "I can handle [product]", "I'll do [product]", "I'm drafting the X.Y.Z [product] release notes", or explicit coverage.
3. Reverse-map Slack display name → GitHub handle via the issue appendix lookup table. If missing, `slack_search_users` and ask the user for the GitHub handle.
4. Update the issue body (§4): replace placeholder, narrow to the confirmed person, or swap in the covering person.
5. Report: "Updated [Product] stakeholder: [old] → @new-handle (confirmed in thread)."

No confirmation: leave as-is and flag. Do not guess. Ambiguous ("I can help" with no product): ask.

### #mission-control (release day only)

If session state has thread timestamps, `slack_read_thread` those first.

**Do not** `slack_read_channel` the whole of `#mission-control`. **Do not** `slack_search_public` for `"begin publishing"` without a version **and** `after:` today's date.

Empty thread on `beginPublishingTs` / `releaseBuildDeclaredTs` is expected for Buildkite bot posts. Treat the parent as the signal; do not rediscover.

Only search when a **needed** cached ts is missing (not merely an empty thread): `slack_search_public` query like `9.5.2 in:#mission-control after:YYYY-MM-DD`, limit 5.

Signals matching tracked versions (link each thread in the status report):

1. **Coordination thread:** "Coordination for ... release, scheduled on" -- timing, who's RC (never assume), schedule changes in replies.
2. **"release build declared":** "We are officially declaring X.Y.Z as the release build".
3. **"begin publishing":** "All pre-finalize steps for X.Y.Z are complete. Please begin the publishing process." -- docs action trigger. Read for go/hold from **whoever is RC** (step 1).

### 0.3 Watch `docs-internal-workflows` (**9.x only**)

**Skip this section for 8.x / 7.x.** Do not search that repo, do not poll bump PRs or version-bump runs, and do not require a prod version-bump for 8.x live messages.

**Skip §0.3** when the docs issue already checks the "Watch for the prod version-bump deploy" line (or equivalent) and cites a successful prod run URL. Do not re-list bump PRs or re-view runs.

For **9.x**, after the `docs-builder` coordinator PR merges **and** that issue line is still unchecked:

The coordinator merges docs-builder config PRs and watches the prod version-bump. Do not wait on docs engineering. Merging the coordinator PR (config SHA = merge commit short SHA) automatically opens:

- `[bump] [staging] docs-builder configuration: <sha>`
- `[bump] [prod] docs-builder configuration: <sha>`

Those merges kick off `Staging / Docs / Deploy / version-bump / ...` and `Prod / Docs / Deploy / version-bump / ...`.

Care about two things only:

1. **Bump PRs merged** -- staging and prod `[bump] ... <sha>` are `MERGED`.
2. **Prod version-bump deploy succeeded** for that SHA. A **failed staging** version-bump **blocks** -- report immediately; do not treat prod as done.

Ignore unrelated workflows (edge, AI enrich, zizmor, dependabot, assembler ingest, link-index) unless the user asks. Do not wait on staging **success** once prod has succeeded, as long as staging did not **fail**.

```bash
gh pr list -R elastic/docs-internal-workflows --state all \
  --search "[bump] docs-builder configuration: <sha>" \
  --json number,title,state,mergedAt,url
gh run list -R elastic/docs-internal-workflows --limit 20 \
  --json name,conclusion,status,displayTitle,url,databaseId,createdAt
```

Match runs by `version-bump` in the name plus timing after the bump PR merge. Cache bump PR numbers and run IDs.

When prod version-bump is `completed/success` and staging did not fail: "Prod deploy succeeded for <sha>."

**Gate -- do not draft "docs are live" / "docs released" until all required:**

| Line | Gate |
|------|------|
| **9.x** | All blocking RN PRs merged **and** prod version-bump succeeded (staging did not fail) |
| **8.x / 7.x** | All blocking RN PRs merged **and** the `elastic/docs` coordinator PR is merged |

Until the gate is met: do not draft those messages, do not ask "ready to send?", do not check website-confirm or `#mission-control` boxes.

Once the gate is met: ask the user to **eyeball the website**, then §6.5. Visual check is required before sending. 8.x "docs released" still includes the scrape line.

### Propose next action

Summarize the §0.2 stage, what is still blocking, and the **single** next action. Do not offer a Slack ping or PR whose box is already checked / the user already sent.

---

## 1. Gather inputs

- Semver list.
- **Docs release issue(s)** -- `[Docs release] X.Y.Z`, not the eng release issue. `gh issue list -R elastic/dev --search "[Docs release] <version>" --json number,title,url`.
- **Eng release issue** -- RC's parent (`[Release] X.Y.Z`, `X.Y.Z release`, etc.). Canonical schedule (FF, code freeze, GA), often links to docs issues, identifies the RC. Use for dates when the docs issue does not exist yet, which versions share a GA, and RC name.
- If docs issues don't exist yet, §1.1.

### 1.1 Create docs release issues (when they don't exist)

1. Template: 9.x minor → `docs-release.md`; 9.x patch → `docs-patch-release.md`; 8.x → `docs-patch-release-8.x.md`.
2. Dates from the **eng release issue** (FF, code freeze, anticipated GA). If none, ask the user.
3. `gh issue create -R elastic/dev --template <template-file> --title "[Docs release] <version>"`
4. Fill Overview (version, dates) and the **release coordinator** from the eng issue if listed. **Leave the rest of the template as-is** -- do not copy stakeholders from a previous release.
5. Report: "Created #NNNN for X.Y.Z. Filled in dates from eng issue #MMMM. Please review."
6. If the eng issue doesn't already reference the new docs issue: `gh issue comment <eng-issue> -R elastic/dev --body "Docs tracking: https://github.com/elastic/dev/issues/<new-docs-issue>"`

User-provided schedule wins over the eng issue.

---

## 2. Classify each version

Patch if the patch number `> 0`; minor if `V.R.0`; major if `V.0.0` (follow the dev issue + v8/v9 playbooks). Then route with §3.

---

## 3. Route PRs (decision)

### 8.x / 7.x (patch or minor)

Follow **[elastic-stack-v8.md](https://github.com/elastic/docs-content-internal/blob/main/docs/releases/elastic-stack-v8.md)**. Coordinator PRs target **`elastic/docs`** only (`shared/versions*`, `conf.yaml` per template).

### 9.x -- isolated patch (only one 9.x in the batch, or no higher minor same GA)

- **Patch:** One `elastic/docs-builder` PR: bump `config/versions.yml` so `versioning_systems.stack.current` matches the **minor line** you ship (e.g. `9.3.4` -> minor **9.3**). Link on the **`versions.yml`** checklist line.
- **Timing gate:** Don't open this PR if more patch releases are expected on the same minor line before GA. If the current published version is more than one patch behind (e.g. current `9.3.2`, shipping `9.3.4`), an intermediate patch is likely first -- wait or confirm with the user.

### 9.x -- minor (`9.x.0`)

**Two separate draft PRs** (two checklist lines):

| When | Branch / change | Link on dev issue |
|------|-----------------|-------------------|
| After **FF** | `config/assembler.yml` only: `shared_configuration.stack.next` -> upcoming **minor** (e.g. `9.4`) | Post-FF line -- PR or merge commit ([shape](https://github.com/elastic/docs-builder/commit/fc39166e5f6f63e57d13e4c958e05c711a17b8f5)) |
| **Before GA** (see timing below) | `assembler.yml`: `stack.current` -> that minor; `stack.next` -> `main`. `versions.yml`: `versioning_systems.stack.current` -> that minor. | Nested **`versions.yml`** bullet -- **PR URL** at end of line |

**Timing for the versions.yml PR (minors):** Don't open early -- many patches land between FF and GA. Open when no more patches are expected before GA (typically 1-2 days before). Check `#mission-control` or ask if another patch is queued.

The coordinator merges each docs-builder PR when it is time; bump PRs and deploys are automatic. Do **not** substitute one PR for both post-FF assembler and pre-GA versions.yml steps.

### Same calendar GA: multiple 9.x (e.g. `9.3.4` + `9.4.0`)

Only one will be a minor -- the others are patches. There will not be two minors on the same day.

1. **Assembler PR:** The minor still gets its own post-FF `assembler.yml` PR (`stack.next` bump).
2. **versions.yml PR:** Only **one** -- targets the **highest** version in the batch.
3. **Canonical issue** = highest 9.x minor (owns the versions.yml PR).
4. **Lower-line issue** = lower semver patch: still for **RNs**; do not duplicate the versions.yml bump -- **supersede** to canonical (§4).

---

## 4. Edit `elastic/dev` issue bodies

- Main trail in the **description**, not comments.
- Do **not** delete template placeholders, footnotes, or stakeholder tables -- only add checkmarks, links, strikethrough, short cross-refs.
- Real `#` / PR URLs from `gh` or the user -- never guess numbers.
- **Check off as you go.** After any skill-flow action that matches a checklist item, check it immediately. Nested boxes for the same action get checked together. Do not wait to be asked. Do not report the item as pending.
- **Do not check items you did not complete.** Other teams' steps (including docs-eng), user-completed work outside this skill, and future release-day items stay unchecked.
- **After each coordinator PR this skill opens:** check the parent and nested lines and paste the **PR URL** (minors: post-FF vs version-bump have **different** URLs on different lines).

Match by checklist wording, not by assuming one template:

| Skill action | Checklist line |
|--------------|----------------|
| Outstanding-RNs / day-before `#docs` ping sent | Post in #docs to remind ... PRs that have not been opened and/or approved |
| Coordinator PR opened | Open a PR ... plus the nested versions.yml / assembler.yml / conf.yaml line |
| Merge-RN `#docs` ping sent | Post in #docs ... they can merge their release note PRs |
| Coordinator PR merged | Merge the docs-builder config PR (or the 8.x equivalent) |
| Prod version-bump deploy succeeded (**9.x only**) | Watch for the prod version-bump deploy -- check only after §0.3 prod deploy success (staging did not fail). **Do not use this line for 8.x.** |
| User confirmed website eyeball | Confirm that the updated docs appear on the website -- only after the gate (§0.3) and the user says the site looks right |
| `#mission-control` "docs are live" reply | Post in #mission-control that the docs are live -- only after the gate **and** website eyeball; still confirm before sending Slack |

```bash
gh issue view <N> -R elastic/dev --json body -q .body > /tmp/dev-issue.md
gh issue edit <N> -R elastic/dev --body-file /tmp/dev-issue.md
```

**Same-GA supersession (lower-line issue)**

- Stakeholder blocks: `superseded by #<canonical>` (real number).
- Checklist blocks owned by canonical: wrap in `~strikethrough~`, tag e.g. `[not needed: superseded by 9.4.0 -- #<canonical>]`.
- Optional footer: `Crossed out instructions superseded by https://github.com/elastic/dev/issues/<canonical>`
- RN-only coordinator steps may stay **open** on the lower-line issue ("verify/publish **this** version's release notes"); strike only lines that **duplicate** canonical deploy work.

PR opened against the wrong issue's path: close with **Superseded by `owner/repo#N`**.

---

## 5. Open coordinator PRs (`elastic/docs` / `elastic/docs-builder`)

Branch: `stack-<version>` (e.g. `stack-9.5-post-ff`, `stack-9.5`, `stack-8.19.16`) -- no `docs/` prefix, no `pre-ga` / "day before" in the name. Existing checkout if available; otherwise clone to a temp directory.

```bash
gh pr create -R elastic/<repo> --draft --base main --head <branch> \
  --title "<concise title -- no Draft prefix>" \
  --body "## Refs\n\n- https://github.com/elastic/dev/issues/<N>"
```

Mark **ready** only in the right window. Re-draft: `gh pr ready <num> -R elastic/<repo> --undo`.

Immediately after the PR exists: check the matching docs-issue lines and paste the PR URL (§4).

---

## 6. Reminders & messages (`#docs`, Slack)

Copy dates, issue links, products, and outstanding PR status from the docs issue (or user-provided schedule). Never invent versions, PR state, or @mentions.

If the body is not already in context from §0, `gh issue view <N> -R elastic/dev --json title,url,body`. Parse: version from title/Overview; anticipated GA / FF / merge-by from Overview; stakeholders and RN PR column from the Release Notes table. Skip vs blocking as in §0. URL present = blocking until merged.

**Grouping:** 8.x and 9.x tables often differ -- separate "Ping for ..." sections when they do; merge duplicate product lines when the same stakeholders apply to multiple versions.

Unresolved stakeholders and Slack send/preview: [slack-templates.md](./slack-templates.md).

### Templates, mentions, send

Read [slack-templates.md](./slack-templates.md) for templates, handle lookup, and OOO checks. If the user doesn't specify the reminder type, present options: feature freeze, outstanding RNs, docs released, or other.

**Docs-released:** one version → singular template (`version` / `are released`); two or more → plural (`versions` / `are all released`). Never "versions" / "all" for a single version. Omit the 8.x scrape line on a 9.x-only batch.

**Send (do this even if you skip the templates file):**

1. Preview in a fenced code block (slack-templates.md) so line breaks are preserved. Then "Send?"
2. Wait for confirmation. "Send it" / "looks good" counts. "Update the thread" / "check the boxes" does **not**.
3. Payload mentions: people `<@U…>`; user groups `<!subteam^S…>`. Never guess an ID.
4. Follow-ups: thread on the FF announcement (`docsFfThreadTs`) **and** `reply_broadcast: true`.
5. After send: check the matching docs-issue item (§4).

### 6.5 Replying in #mission-control threads (release day)

Do not enter until the **gate** is met (§0.3): 9.x = blocking RNs merged + prod version-bump; 8.x = blocking RNs merged + `elastic/docs` coordinator PR merged. If not met, say what is outstanding and stop -- do not draft live/released messages.

Once the gate is met:

1. Ask the user to eyeball the website (9.x: current docs / this version's release notes; 8.x: v8 playbook pages).
2. After they confirm: check the "docs appear on the website" box (§4). Draft the `#mission-control` reply (`X.Y.Z docs are live.`) and the `#docs` "docs released" ping (8.x scrape line only when an 8.x version is in the batch). Show both; send only with confirmation (slack-templates.md).
3. On confirm: reply in the begin-publishing thread (`thread_ts` from §0), send the `#docs` ping, and check the `#mission-control` box.

---

## 7. Background poller (in-session)

When the user says "watch the PRs", "watch the deploy", or "let me know when they're all merged":

### 7.1 Release-note PRs

1. Blocking RN PR URLs from the issue table (skip N/A / No changes only).
2. Background shell (`block_until_ms: 0`) every 5 minutes: `gh pr view <url> --json state -q .state`.
3. All `MERGED` → emit `ALL_RN_PRS_MERGED` (`notify_on_output`).
4. Report: "All RN PRs are merged." Persist to the session file.

### 7.2 docs-internal-workflows deploys (**9.x only**)

Skip for 8.x / 7.x.

After the **9.x** `docs-builder` coordinator PR is merged (or when the user asks to watch 9.x deploys):

1. Config SHA + staging/prod bump PRs + version-bump run IDs (§0.3). Prefer session state.
2. Poll `gh run view <id>` every 30s. Emit `DEPLOY_STAGING_FAILED` (blocks; alert immediately), `DEPLOY_PROD_FAILED`, `DEPLOY_PROD_DONE` (prod `completed/success` and staging did not fail).
3. On `DEPLOY_PROD_DONE`: "Prod deploy succeeded." If blocking RN PRs are still open, list them -- do not offer live/released Slack. If they are all merged, ask the user to eyeball, then §6.5.
4. Write run IDs and conclusions to session state.

Pollers only run in the current session. Next session: §0.1 + §0, not full rediscovery.

For anything not specified here (API docs, Buildkite): follow the docs issue checklist and playbooks.
