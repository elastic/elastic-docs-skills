---
name: docs-stack-release
version: 1.0.0
description: >-
  Executable runbook: classify Stack versions, route 8.x vs 9.x, open draft PRs,
  edit elastic/dev issue bodies (two-PR minors, same-GA supersession), and build
  Slack / #docs reminders and messages from issue data (tables, dates). Use when
  coordinating docs releases, multiple versions, elastic/dev, docs-builder,
  reminders, Slack or #docs pings, assembler.yml, versions.yml, conf.yaml.
sources:
  - https://github.com/elastic/dev
  - https://github.com/elastic/docs-builder
  - https://github.com/elastic/docs-content-internal/tree/main/docs/releases
allowed-tools: Bash, Read, Write, Glob
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

You are the **Elastic Stack docs release coordinator** assistant. Follow this runbook to classify releases, route work to `elastic/docs` vs `elastic/docs-builder`, edit [elastic/dev](https://github.com/elastic/dev) tracking issues, open **draft** coordinator PRs with `gh`, and draft **Slack / `#docs` reminders** from issue bodies.

**Source of truth:** Dates and checklist text in each [elastic/dev](https://github.com/elastic/dev) docs release issue. Longer playbooks: [elastic-stack-v9.md](https://github.com/elastic/docs-content-internal/blob/main/docs/releases/elastic-stack-v9.md) · [elastic-stack-v8.md](https://github.com/elastic/docs-content-internal/blob/main/docs/releases/elastic-stack-v8.md) (internal repo).

**Templates (open new tracking issues):** [minor](https://github.com/elastic/dev/blob/main/.github/ISSUE_TEMPLATE/docs-release.md) · [9.x patch](https://github.com/elastic/dev/blob/main/.github/ISSUE_TEMPLATE/docs-patch-release.md) · [8.x patch](https://github.com/elastic/dev/blob/main/.github/ISSUE_TEMPLATE/docs-patch-release-8.x.md).

| Line | Repo | Config files |
|------|------|----------------|
| **9.x+** | `elastic/docs-builder` | `config/assembler.yml`, `config/versions.yml` |
| **8.x / 7.x** | `elastic/docs` | `shared/versions/stack/*.asciidoc`, `conf.yaml` |

Never put **8.x and 9.x edits in one PR**.

---

## 1. Gather inputs (do not invent IDs)

- Semver list, e.g. `8.19.15`, `9.3.4`, `9.4.0`.
- **`elastic/dev` issue number(s)** per version—or ask the user; use `gh issue list -R elastic/dev --search "Docs release"` if needed.
- **Stack release** issue link for the dev issue overview when the user provides it.

---

## 2. Classify each version

`V.R.M`:

| Condition | Type |
|-----------|------|
| `M > 0` | **Patch** |
| `M == 0` (normal case) | **Minor** |
| New major `V.0.0` | **Major** — follow dev issue + v8/v9 docs |

Output a table: version → line (8 vs 9) → patch/minor/major → repo.

---

## 3. Route PRs (decision)

### 8.x / 7.x (patch or minor)

Follow **[elastic-stack-v8.md](https://github.com/elastic/docs-content-internal/blob/main/docs/releases/elastic-stack-v8.md)**. Coordinator PRs target **`elastic/docs`** only (`shared/versions*`, `conf.yaml` per template).

### 9.x — isolated patch (only one 9.x in the batch, or no higher minor same GA)

- **Patch:** Typically **one** `elastic/docs-builder` PR for the template **day-before** step: bump `config/versions.yml` so `versioning_systems.stack.current` matches the **minor line** you ship (e.g. `9.3.4` → minor **9.3**). Link that PR on the **`versions.yml`** checklist line.

### 9.x — minor (`9.x.0`)

**Two separate draft PRs** (two checklist lines):

| When | Branch / change | Link on dev issue |
|------|-----------------|-------------------|
| After **FF** | `config/assembler.yml` only: `shared_configuration.stack.next` → upcoming **minor** (e.g. `9.4`) | Post–FF line — PR or merge commit ([shape](https://github.com/elastic/docs-builder/commit/fc39166e5f6f63e57d13e4c958e05c711a17b8f5)) |
| **Day before GA** | `assembler.yml`: `stack.current` → that minor; `stack.next` → `main`. `versions.yml`: `versioning_systems.stack.current` → that minor. | Nested **`versions.yml`** bullet — **PR URL** at end of line |

Docs engineering merges each PR and releases docs-builder per template; coordinator does **not** substitute one PR for both steps.

### Same calendar GA: multiple 9.x (e.g. `9.3.4` + `9.4.0`)

1. **Config target:** **One** semver for docs-builder: **max** of the batch (here **9.4** / `9.4.0` playbook).
2. **Canonical dev issue** = the issue for that **highest** 9.x minor (owns unified docs-builder PRs).
3. **Lower-line issue** = lower semver (e.g. `9.3.4`): still for **RNs**; **do not** duplicate docs-builder bump—**supersede** to canonical (patterns below).

---

## 4. Edit `elastic/dev` issue bodies

- Main trail in the **description**, not comments.
- Do **not** delete template placeholders, footnotes, or stakeholder tables—only add checkmarks, links, strikethrough, short cross-refs.
- Use **real** `#` / PR URLs from `gh` or the user—**never** guess numbers.

**Fetch → edit → push**

```bash
gh issue view <N> -R elastic/dev --json body -q .body > /tmp/dev-issue.md
# edit /tmp/dev-issue.md
gh issue edit <N> -R elastic/dev --body-file /tmp/dev-issue.md
```

**Same-GA supersession (lower-line issue)**

- Stakeholder blocks: `superseded by #<canonical>` (real number).
- Checklist blocks owned by canonical: wrap in `~strikethrough~`, tag e.g. `[not needed: superseded by 9.4.0 — #<canonical>]`.
- Optional footer line: `Crossed out instructions superseded by https://github.com/elastic/dev/issues/<canonical>`
- RN-only coordinator steps may stay **open** on the lower-line issue where they mean “verify/publish **this** version’s release notes”; strike only lines that **duplicate** canonical deploy work.

PR opened against the wrong issue’s path: close with **Superseded by `owner/repo#N`**.

---

## 5. Open coordinator PRs (`elastic/docs` / `elastic/docs-builder`)

```bash
gh pr create -R elastic/<repo> --draft --base main --head <branch> \
  --title "<concise title — no Draft prefix>" \
  --body "## Refs\n\n- https://github.com/elastic/dev/issues/<N>"
```

Mark **ready** only in the right window. Re-draft: `gh pr ready <num> -R elastic/<repo> --undo`.

---

## 6. After each coordinator PR

Update the matching **`elastic/dev` issue**: check the line that matches **this** PR; paste the **PR URL** on the template line (minors: post–FF vs day-before **different** URLs).

---

## 7. Reminders & messages (`#docs`, Slack)

Coordinators usually ask for **reminders** (feature freeze, day before, merge RNs, docs live / scrape)—not “announcements.” Same §7 templates apply. Build copy **from issue data** only.

**Rule:** Copy **dates**, **issue links**, **which products** need RNs, and **outstanding** PR status **only** from [elastic/dev](https://github.com/elastic/dev) issue bodies—do **not** invent versions or PR state. **Who to ping** comes from the stakeholder column, but **Slack** messages must use **Slack-equivalent** @mentions (usergroups / members)—**not** GitHub `@user` / `@org/team` strings copied verbatim unless your org uses the same form in Slack.

### 7.1 Fetch issue content

For each docs release issue in the batch:

```bash
gh issue view <N> -R elastic/dev --json title,url,body -q .
```

Or save bodies for editing:

```bash
gh issue view <N> -R elastic/dev --json body -q .body > /tmp/issue-<N>.md
```

**Parse from the body:**

| Need | Where in the issue |
|------|---------------------|
| Version | Usually title `[Docs release] X.Y.Z` or Overview |
| **Anticipated release date** | Overview bullet `**Anticipated release date**` |
| **Feature freeze** / merge-by dates | Overview bullets |
| **Link to this issue** | `url` from JSON or `https://github.com/elastic/dev/issues/<N>` |
| Who to ping (by product) | **Release notes** table: `Product` + `Stakeholder` — use to **map** each row to Slack mentions; GitHub handles in the issue are the source of truth for *identity*, Slack handles for *delivery* |
| RN PR status | Same table, **Pull Request** column: `❔` / empty / no `http` URL ⇒ **outstanding**; `http…` ⇒ treat as filed (verify still open in GitHub if needed) |

**Grouping pings:** 8.x issues (AsciiDoc template) and 9.x issues (new RN URLs) often have **different product rows** (e.g. Enterprise Search vs Observability). Use **separate** “Ping for …” sections when tables differ; **merge** duplicate product lines when the same stakeholder list applies to multiple versions in one sentence (e.g. “9.1.8 and 9.2.2”).

### 7.2 Template — feature freeze (multi-release)

Fill placeholders from §7.1. If every issue’s **Anticipated release date** is the same, use one date in the opening sentence; if they differ, list `version — date` per line. Adjust emoji to your Slack workspace.

```markdown
Hi everyone! :wave: Today is the feature freeze for multiple releases.

The following releases are scheduled to release <ANTICIPATED_DATE>: <VERSION_LIST>

Please add your release note PRs to the issues linked below:

**Releases & related issues**

<FOR EACH ISSUE:>
<VERSION> — [<issue title>](<issue URL>)
<END>

---

:bell: **Ping for <VERSION_OR_GROUP_A>**

<Copy Product + one line per product; **Slack** @mentions (usergroups / users) **equivalent** to each stakeholder in the issue—not pasted GitHub `@…` unless they match Slack.>

---

:bell: **Ping for <VERSION_OR_GROUP_B>** *(repeat when 8.x vs 9.x tables differ)*

<…>
```

### 7.3 Template — outstanding release notes / merge push

Use when reminding people to merge before GA; **outstanding** rows = Pull Request column still not a merged PR link (from issues).

```markdown
The following stack releases are going forward: <VERSION_LIST>. Please merge any outstanding release note PRs (linked in those issues :point_left:).

**Release note PRs for the following products are still outstanding:**

<FOR EACH OUTSTANDING ROW:>
<Product> <Stakeholder column from issue>
<END>

<Optional API docs coordination — pull API docs point person from the 9.x issue stakeholder block / footnotes if present:>

@<api-docs-person> we can start with the API docs refresh when ready <optional context from issue or thread>.
```

### 7.4 Template — docs released (final / 8.x scrape)

Send after coordinator confirms docs are live for the batch. **Version list** = semver from each issue title / Overview in the batch (same order as elsewhere). Second line: Slack usergroup / mention (e.g. Revtech) for the team that re-scrapes the **classic** (AsciiDoc) docs—**Slack-equivalent** @, not GitHub. **Include the exact 8.x patch/minor semver** `<8.x_VERSION>` from the `[Docs release] X.Y.Z` issue for that line (e.g. `8.19.8`) in the scrape sentence. If the batch is **9.x-only**, omit the scrape line or confirm with the coordinator.

```markdown
Docs for stack versions <VERSION_LIST> are all released!
<Slack @mention> you can start scraping the docs for <8.x_VERSION> now
```

Example (8.x in batch is `8.19.8`):

```text
Docs for stack versions 8.19.8, 9.1.8, and 9.2.2 are all released!
@revtech you can start scraping the docs for 8.19.8 now
```

### 7.5 Other states (same data rules)

- **Day before:** `#docs` reminder — reuse Overview dates + issue links from §7.1; optionally list products still `❔` from tables.
- **Release day (before final):** Short “you can merge RNs” / docs live — follow checklist timing on each issue; names from stakeholders + Docs engineering / API blocks.

**Do not** invent people or Slack IDs: if the table still says `` `Beats point person` `` or a placeholder, say so or ask the coordinator to resolve footnotes in the issue before sending pings.

---

## Terms (quick)

| Term | Meaning |
|------|---------|
| **Canonical issue** | Dev issue that owns shared docs-builder work for the GA (highest 9.x minor when versions share a day). |
| **Lower-line issue** | Lower semver 9.x same GA—RNs here; config steps supersede to canonical. |
| **GA / FF** | Dates on the dev issue + schedule. |

**Roles:** Coordinator opens PRs and edits dev issues. **Docs engineering** merges docs-builder, releases, deploy bumps—coordinate with them; don’t assume you merge unless agreed.

---

## Agent execution order

1. Inputs → classification table (§2–3).
2. If same-GA multi 9.x → identify canonical `#` and plan supersession text on lower-line issue.
3. Open **draft** PRs in schedule order; **9.x minor** = two PRs before marking both steps done.
4. After **each** PR: `gh issue edit` the right dev issue (§4, §6).
5. When the user asks for **reminders**, **Slack** / **`#docs` copy**, **pings**, or similar: **§7** — fetch each issue’s `title`, `url`, `body`; use templates §7.2–§7.4 (FF, outstanding RNs, docs released / scrape).
6. For anything not specified here (API docs, Buildkite, deploy repo): follow the **dev issue checklist** and [elastic-stack-v9.md](https://github.com/elastic/docs-content-internal/blob/main/docs/releases/elastic-stack-v9.md) / [elastic-stack-v8.md](https://github.com/elastic/docs-content-internal/blob/main/docs/releases/elastic-stack-v8.md).

**Do not assume:** calendar dates; v8 `conf.yaml` edge cases (ECS, etc.)—see v8 doc.
