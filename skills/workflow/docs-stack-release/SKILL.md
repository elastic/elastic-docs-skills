---
name: docs-stack-release
version: 1.1.0
description: >-
  Coordinate Elastic Stack docs releases: classify versions, route 8.x vs 9.x
  PRs, edit elastic/dev tracking issues, handle same-GA supersession, and draft
  Slack #docs reminders. Use when coordinating docs releases, opening coordinator
  PRs, editing elastic/dev issues, drafting release reminders, or working with
  assembler.yml, versions.yml, or conf.yaml.
argument-hint: <versions and/or issue numbers>
sources:
  - https://github.com/elastic/dev
  - https://github.com/elastic/docs-builder
  - https://github.com/elastic/docs-content-internal/tree/main/docs/releases
allowed-tools: Read, Write, Glob, Bash(gh *), Bash(git *)
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

You are the **Elastic Stack docs release coordinator** assistant. Follow this runbook to classify releases, route work, edit [elastic/dev](https://github.com/elastic/dev) tracking issues, open **draft** coordinator PRs with `gh`, and draft **Slack / `#docs` reminders**.

**Global rule -- issue availability:** Prefer [elastic/dev](https://github.com/elastic/dev) issue bodies as the source of truth for dates, checklist text, and stakeholder tables. **When issues don't exist yet** (not filed, no `gh` access, or planning ahead), collect schedule fields from the user (feature freeze, merge-by, anticipated GA) and use those as inputs everywhere issues would be referenced. Replace issue URLs with "(issue TBD)" in templates. Once issues are created, switch to `gh` as the source.

**Playbooks:** [elastic-stack-v9.md](https://github.com/elastic/docs-content-internal/blob/main/docs/releases/elastic-stack-v9.md) -- [elastic-stack-v8.md](https://github.com/elastic/docs-content-internal/blob/main/docs/releases/elastic-stack-v8.md) (internal repo).

**Issue templates:** [minor](https://github.com/elastic/dev/blob/main/.github/ISSUE_TEMPLATE/docs-release.md) -- [9.x patch](https://github.com/elastic/dev/blob/main/.github/ISSUE_TEMPLATE/docs-patch-release.md) -- [8.x patch](https://github.com/elastic/dev/blob/main/.github/ISSUE_TEMPLATE/docs-patch-release-8.x.md).

| Line | Repo | Config files |
|------|------|----------------|
| **9.x+** | `elastic/docs-builder` | `config/assembler.yml`, `config/versions.yml` |
| **8.x / 7.x** | `elastic/docs` | `shared/versions/stack/*.asciidoc`, `conf.yaml` |

Never put **8.x and 9.x edits in one PR**.

**Related skills:** [docs-kibana-release-notes](../../authoring/docs-kibana-release-notes/SKILL.md) and [docs-serverless-changelog](../../authoring/docs-serverless-changelog/SKILL.md) handle release note *content*; this skill handles coordinator *infrastructure* (PRs, config bumps, dev issue edits, Slack reminders).

---

## Inputs

`$ARGUMENTS` is a space-separated list of semver versions and/or `elastic/dev` issue numbers (e.g. `9.4.0 9.3.4 8.19.15` or `#1234 #1235`). If empty, ask the user what releases to coordinate.

---

## 1. Gather inputs (do not invent IDs)

- Semver list, e.g. `8.19.15`, `9.3.4`, `9.4.0`.
- **`elastic/dev` issue number(s)** per version -- use `gh issue view` / `gh issue list -R elastic/dev --search "Docs release"` when available, or ask the user.
- **Stack release** issue link for the dev issue overview when the user provides it.
- If issues are unavailable, follow the **global rule** above.

---

## 2. Classify each version

`V.R.M`:

| Condition | Type |
|-----------|------|
| `M > 0` | **Patch** |
| `M == 0` (normal case) | **Minor** |
| New major `V.0.0` | **Major** -- follow dev issue + v8/v9 docs |

Output a table: version -> line (8 vs 9) -> patch/minor/major -> repo.

---

## 3. Route PRs (decision)

### 8.x / 7.x (patch or minor)

Follow **[elastic-stack-v8.md](https://github.com/elastic/docs-content-internal/blob/main/docs/releases/elastic-stack-v8.md)**. Coordinator PRs target **`elastic/docs`** only (`shared/versions*`, `conf.yaml` per template).

### 9.x -- isolated patch (only one 9.x in the batch, or no higher minor same GA)

- **Patch:** Typically **one** `elastic/docs-builder` PR for the template **day-before** step: bump `config/versions.yml` so `versioning_systems.stack.current` matches the **minor line** you ship (e.g. `9.3.4` -> minor **9.3**). Link that PR on the **`versions.yml`** checklist line.

### 9.x -- minor (`9.x.0`)

**Two separate draft PRs** (two checklist lines):

| When | Branch / change | Link on dev issue |
|------|-----------------|-------------------|
| After **FF** | `config/assembler.yml` only: `shared_configuration.stack.next` -> upcoming **minor** (e.g. `9.4`) | Post-FF line -- PR or merge commit ([shape](https://github.com/elastic/docs-builder/commit/fc39166e5f6f63e57d13e4c958e05c711a17b8f5)) |
| **Day before GA** | `assembler.yml`: `stack.current` -> that minor; `stack.next` -> `main`. `versions.yml`: `versioning_systems.stack.current` -> that minor. | Nested **`versions.yml`** bullet -- **PR URL** at end of line |

Docs engineering merges each PR and releases docs-builder per template; coordinator does **not** substitute one PR for both steps.

### Same calendar GA: multiple 9.x (e.g. `9.3.4` + `9.4.0`)

1. **Config target:** **One** semver for docs-builder: **max** of the batch (here **9.4** / `9.4.0` playbook).
2. **Canonical dev issue** = the issue for that **highest** 9.x minor (owns unified docs-builder PRs).
3. **Lower-line issue** = lower semver (e.g. `9.3.4`): still for **RNs**; **do not** duplicate docs-builder bump -- **supersede** to canonical (patterns below).

---

## 4. Edit `elastic/dev` issue bodies

- Main trail in the **description**, not comments.
- Do **not** delete template placeholders, footnotes, or stakeholder tables -- only add checkmarks, links, strikethrough, short cross-refs.
- Use **real** `#` / PR URLs from `gh` or the user -- **never** guess numbers.

**Fetch -> edit -> push**

```bash
gh issue view <N> -R elastic/dev --json body -q .body > /tmp/dev-issue.md
gh issue edit <N> -R elastic/dev --body-file /tmp/dev-issue.md
```

**Same-GA supersession (lower-line issue)**

- Stakeholder blocks: `superseded by #<canonical>` (real number).
- Checklist blocks owned by canonical: wrap in `~strikethrough~`, tag e.g. `[not needed: superseded by 9.4.0 -- #<canonical>]`.
- Optional footer line: `Crossed out instructions superseded by https://github.com/elastic/dev/issues/<canonical>`
- RN-only coordinator steps may stay **open** on the lower-line issue where they mean "verify/publish **this** version's release notes"; strike only lines that **duplicate** canonical deploy work.

PR opened against the wrong issue's path: close with **Superseded by `owner/repo#N`**.

---

## 5. Open coordinator PRs (`elastic/docs` / `elastic/docs-builder`)

```bash
gh pr create -R elastic/<repo> --draft --base main --head <branch> \
  --title "<concise title -- no Draft prefix>" \
  --body "## Refs\n\n- https://github.com/elastic/dev/issues/<N>"
```

Mark **ready** only in the right window. Re-draft: `gh pr ready <num> -R elastic/<repo> --undo`.

---

## 6. After each coordinator PR

Update the matching **`elastic/dev` issue**: check the line that matches **this** PR; paste the **PR URL** on the template line (minors: post-FF vs day-before **different** URLs).

---

## 7. Reminders & messages (`#docs`, Slack)

**Data rules:** Copy dates, issue links, products, and outstanding PR status from dev issue bodies (or user-provided schedule per the global rule). Never invent versions, PR state, or @mentions. Slack messages must use **Slack-equivalent** @mentions, not GitHub handles.

### 7.1 Fetch issue content

For each docs release issue in the batch:

```bash
gh issue view <N> -R elastic/dev --json title,url,body -q .
```

**Parse from the body:**

| Need | Where in the issue |
|------|---------------------|
| Version | Title `[Docs release] X.Y.Z` or Overview |
| **Anticipated release date** | Overview bullet `**Anticipated release date**` |
| **Feature freeze** / merge-by dates | Overview bullets |
| **Link to this issue** | `url` from JSON or `https://github.com/elastic/dev/issues/<N>` |
| Who to ping (by product) | **Release notes** table: `Product` + `Stakeholder` -- map each row to Slack mentions |
| RN PR status | Same table, **Pull Request** column: no URL = **outstanding**; URL present = filed |

**Grouping pings:** 8.x and 9.x issues often have **different product rows**. Use **separate** "Ping for ..." sections when tables differ; **merge** duplicate product lines when the same stakeholders apply to multiple versions.

### 7.2 Template -- feature freeze (multi-release)

Fill placeholders from 7.1. If all issues share one anticipated release date, use one date; otherwise list per version.

```markdown
Hi everyone! :wave: Today is the feature freeze for multiple releases.

The following releases are scheduled to release <ANTICIPATED_DATE>: <VERSION_LIST>

Please add your release note PRs to the issues linked below:

**Releases & related issues**

<FOR EACH ISSUE:>
<VERSION> -- [<issue title>](<issue URL>)
<END>

---

:bell: **Ping for <VERSION_OR_GROUP_A>**

<One line per product with Slack @mentions equivalent to stakeholders in the issue.>

---

:bell: **Ping for <VERSION_OR_GROUP_B>** *(repeat when 8.x vs 9.x tables differ)*

<...>
```

### 7.3 Template -- outstanding release notes / merge push

Outstanding rows = Pull Request column still not a merged PR link.

```markdown
The following stack releases are going forward: <VERSION_LIST>. Please merge any outstanding release note PRs (linked in those issues :point_left:).

**Release note PRs for the following products are still outstanding:**

<FOR EACH OUTSTANDING ROW:>
<Product> <Stakeholder column from issue>
<END>

@<api-docs-person> we can start with the API docs refresh when ready <optional context>.
```

### 7.4 Template -- docs released (final / 8.x scrape)

Send after docs are live. Include the exact 8.x semver from the issue for the scrape line. If the batch is **9.x-only**, omit the scrape line.

```markdown
Docs for stack versions <VERSION_LIST> are all released!
<Slack @mention> you can start scraping the docs for <8.x_VERSION> now
```

Example:

```text
Docs for stack versions 8.19.8, 9.1.8, and 9.2.2 are all released!
@revtech you can start scraping the docs for 8.19.8 now
```

### 7.5 Other states

- **Day before:** `#docs` reminder -- reuse Overview dates + issue links; optionally list products still outstanding.
- **Release day:** Short "merge RNs" / "docs live" -- follow checklist timing; names from stakeholders.

Do **not** invent people or Slack IDs. If the table has a placeholder like `Beats point person`, say so or ask the coordinator to resolve it.

---

## Quality checklist (must pass before acting)

- [ ] Every issue number and PR URL comes from `gh` or the user -- none invented.
- [ ] 8.x and 9.x changes are in **separate** PRs -- never combined.
- [ ] Same-GA batch: canonical issue identified; lower-line issue superseded correctly.
- [ ] 9.x minor has **two** draft PRs (post-FF + day-before) -- not one combined PR.
- [ ] Dev issue edits preserve template structure (placeholders, footnotes, stakeholder tables intact).
- [ ] Slack copy uses **Slack-equivalent** @mentions -- no raw GitHub `@handles`.
- [ ] Dates in Slack messages come from issue bodies or explicit user input -- none assumed.

---

## Terms (quick)

| Term | Meaning |
|------|---------|
| **Canonical issue** | Dev issue that owns shared docs-builder work for the GA (highest 9.x minor when versions share a day). |
| **Lower-line issue** | Lower semver 9.x same GA -- RNs here; config steps supersede to canonical. |
| **GA / FF** | Dates on the dev issue or from the user per the global rule. |

**Roles:** Coordinator opens PRs and edits dev issues. **Docs engineering** merges docs-builder, releases, deploy bumps -- coordinate with them; don't assume you merge unless agreed.

---

## Agent execution order

1. Inputs (follow global rule if issues unavailable) -> classification table (2-3).
2. If same-GA multi 9.x -> identify canonical `#` and plan supersession text on lower-line issue.
3. Open **draft** PRs in schedule order; **9.x minor** = two PRs before marking both steps done.
4. After **each** PR: `gh issue edit` the right dev issue (4, 6).
5. When the user asks for **reminders** / **Slack copy** / **pings**: 7 -- use issue data when available, user-provided dates otherwise.
6. For anything not specified here (API docs, Buildkite, deploy repo): follow the dev issue checklist and playbooks.

**Do not assume** calendar dates -- take them from dev issue bodies **or** explicit user input.
