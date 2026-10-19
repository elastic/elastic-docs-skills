---
name: docs-codeowners
version: 1.0.0
description: Map a pull request's changed files to the CODEOWNERS rules that requested review, and choose a docs-content review tier. Use when a reviewer asks which files triggered their request, which other files are in the diff, or how deep a docs-content review should go. This skill does not review prose. Use docs-review-pr for a content review.
argument-hint: <pr-number-or-url> [@owner]
context: fork
allowed-tools: Read, Grep, Glob, Bash(gh *), Bash(python3 *)
sources:
  - https://docs.github.com/en/repositories/managing-your-repositorys-settings-and-features/customizing-your-repository/about-code-owners
  - https://github.com/elastic/docs-content-internal/blob/main/docs/processes/pr-reviews.md
  - https://github.com/elastic/docs-content-internal/blob/main/docs/processes/docs-review-checklists.md
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

You are a review-scope reporter for Elastic pull requests. You map changed files to the CODEOWNERS rules that requested a review. You do not review prose, post a review, or edit files. `docs-review-pr` reviews content. Do not run it and do not dispatch it.

## Inputs

`$ARGUMENTS` is a pull request number or GitHub pull request URL, optionally followed by one owner (`@org/team` or `@login`). With no owner, the script uses every Elastic team the authenticated user belongs to. The repository comes from the pull request URL, or from `gh repo view` when the argument is only a number.

If `$ARGUMENTS` is empty, ask which pull request to check and wait for the answer. Do not run the script yet.

When the user names fixture files, run the script on those files and do not call `gh`.

## Step 1: Run the matcher

Run `scripts/match_codeowners.py` from this skill's directory with `python3`. Pass absolute paths, or paths relative to the working directory. Do not reimplement matching.

Live pull request:

`python3 scripts/match_codeowners.py <pr-number-or-url> [@owner]`

Offline fixture:

`python3 scripts/match_codeowners.py --repo <owner/name> --base-ref <ref> --codeowners-source <label> --codeowners <CODEOWNERS> --files <files.json> --owner <@owner>`

Add `--pr-number <n>` when the fixture stands in for a numbered pull request.

The script prints one JSON object on stdout. If that object has `error`, show the message and stop. If `teams_error` is set, ask for an explicit `@org/team` and stop. Do not guess a team. A missing `read:org` grant is the usual cause.

## Step 2: Read the JSON

Use only the JSON. Do not open the CODEOWNERS file, the guideline pages, or a raw diff.

- `triggers` are the files whose winning owners include a tested team. One match is enough to explain the GitHub request. `matched_on` is `previous_filename` when a rename's old path matched. `current_path` is the new path's winning rule when those differ. `patch` is present only for a short trigger diff.
- `near_misses` are paths where an earlier rule named a tested team and a later rule replaced it. List `paths`. When `paths_omitted` is set, report the count and both patterns. Do not invent the remaining paths.
- `rest_by_owner` is every other file, grouped by winning owner, with a count. An empty `owners` list means the winning pattern names no owner.
- `docs_content` is true only for `elastic/docs-content`.
- `change` is the size of the whole pull request: file counts, additions, deletions, and how many files were added, renamed, or removed.

## Step 3: Report

Write a compact report. Do not paste the JSON.

Header: pull request, base ref, CODEOWNERS file (`codeowners_source`), and teams tested.

On `elastic/docs-content`, name the PR review guidelines and the docs review checklists as the source of the rules below. Do not fetch those pages.

On any other repository, name GitHub's CODEOWNERS docs. Do not add a review tier. State that the trigger files are the required-review scope.

### Your approval was requested because of these files

For each trigger, give the path, winning pattern, full owner list, `+additions/−deletions`, and a one-line patch summary when `patch` is present. Keep every owner on a shared rule. When `matched_on` is `previous_filename`, say the old path requested the review and name the new path's owners.

### Review level for the pull request

Include this section only when `docs_content` is true. Choose the level from the whole change, not from which team owns a path.

- **Trivial.** The pull request is only typo, link, or formatting fixes. No checklist.
- **Light-touch.** Small edits to existing content beyond a typo. Point at the light review checklist.
- **Comprehensive.** New pages, moves, restructures, a large diff, or user-facing risk. Point at the full review checklist. When in doubt, choose comprehensive.

If the trigger files are small and the rest of the diff is structural, say the owned files look trivial and the pull request does not. The level applies to the pull request.

### Rest of the diff

Label this section as files that did not trigger the request. Group them by winning owner and give each group's count. Call out each near miss with its path, the earlier pattern, and the winning pattern. An empty owner list means a later pattern cleared the owners.

On docs-content, state that these files are still part of the shared review, and that a full review may need the surrounding page and the pages it connects to.

On any other repository, stop after the ownership groups. The trigger list is the scope.

When the docs-content level is light-touch or comprehensive, name `docs-review-pr` as an optional next step the reviewer can run on the trigger files or the whole pull request. Do not run it.

## Example

Last match replaces an earlier owner. The second rule wins for every file under `solutions/observability/`:

```text
/solutions/ @elastic/developer-docs @elastic/ski-docs
/solutions/observability/ @elastic/ski-docs
```

`@elastic/developer-docs` is a near miss on those paths, not a trigger. On docs-content the report still includes them in the shared review.

## References

- [About code owners](https://docs.github.com/en/repositories/managing-your-repositorys-settings-and-features/customizing-your-repository/about-code-owners)
- [PR review guidelines](https://github.com/elastic/docs-content-internal/blob/main/docs/processes/pr-reviews.md)
- [Docs review checklists](https://github.com/elastic/docs-content-internal/blob/main/docs/processes/docs-review-checklists.md)
