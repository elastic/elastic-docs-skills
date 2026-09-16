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

# Missed-PR reconciliation reference

Use these recipes as starting points. Adjust version, dates, and branch names to the release.

## Candidate sets

### Version and release-note labels

Run one query per release-note type because GitHub label filters are conjunctive:

```bash
for type in feature enhancement fix deprecation breaking; do
  GH_PAGER=cat gh pr list \
    --repo elastic/kibana \
    --state merged \
    --search "label:vVERSION label:\"release_note:${type}\"" \
    --limit 1000 \
    --json number,title,mergedAt,labels,url
done
```

Confirm the repository's exact version-label format before running the query.

### Late merges

Use the initial generator date as the lower bound:

```bash
GH_PAGER=cat gh pr list \
  --repo elastic/kibana \
  --state merged \
  --search "merged:>=YYYY-MM-DD base:main" \
  --limit 1000 \
  --json number,title,mergedAt,baseRefName,labels,url
```

Filter the result for `release_note:*`, target-version, backport, and relevant feature/team labels. Do not discard unlabeled candidates until their release scope is checked.

### Labels changed after generation

Do not treat the merge date as the only post-generation boundary. Find merged PRs updated after the exact generator cutoff:

```bash
GH_PAGER=cat gh pr list \
  --repo elastic/kibana \
  --state merged \
  --search "updated:>=YYYY-MM-DD" \
  --limit 1000 \
  --json number,title,mergedAt,updatedAt,labels,url
```

Filter `updatedAt` against the exact generator timestamp. For each remaining candidate, inspect version and release-note label events:

```bash
gh api --paginate repos/elastic/kibana/issues/PR_NUMBER/events \
  --jq '.[] |
    select(.event == "labeled" or .event == "unlabeled") |
    select(.label.name == "vVERSION" or (.label.name | startswith("release_note:"))) |
    [.created_at, .event, .label.name] | @tsv'
```

Compare label state at the generator cutoff with current label state. Reconsider any PR whose target-version eligibility or release-note type changed after generation, even if it merged before the cutoff. Add newly eligible PRs and review already listed PRs that became ineligible or changed type.

### Release branch and backports

Fetch the release branch and compare it with the previous release point:

```bash
git fetch origin main TARGET_BRANCH
git log --oneline PREVIOUS_RELEASE..origin/TARGET_BRANCH
```

For suspicious commits, identify the PR and original/backport relationship:

```bash
GH_PAGER=cat gh pr view PR_NUMBER \
  --repo elastic/kibana \
  --json number,title,baseRefName,mergedAt,labels,body,comments,files,url
```

Check:

- `backport:*` and version labels
- `ONMERGE` backport targets in the PR body
- Merge or cherry-pick commits present in the release branch
- Original PRs that reached `main` after the generator cutoff

### Missing release metadata

Search the release window for likely candidates without relying on labels:

```bash
GH_PAGER=cat gh pr list \
  --repo elastic/kibana \
  --state merged \
  --search "merged:YYYY-MM-DD..YYYY-MM-DD base:main" \
  --limit 1000 \
  --json number,title,body,mergedAt,labels,url
```

Prioritize PRs that:

- Contain a Release Notes section or release-note text
- Modify user-facing code or configuration
- Have backport targets for the release
- Carry a relevant feature or team label but lack a version label
- Were merged near or after the generator cutoff

Fetch changed files for each candidate during manual inspection with `gh pr view`.

### Later reverts and disabled changes

For every included PR, search later PRs in the release window for its number, title terms, and affected implementation paths. Inspect PRs that revert, disable, or supersede the behavior even when they use `release_note:skip`. Remove an entry when the described behavior does not exist at the target release HEAD.

## Build-candidate verification

On an update pass, a `v<version>` + `release_note:*` label proves intent, not shipment. Confirm each candidate is in the latest build candidate before adding it.

```bash
# 1. Latest BC's Kibana commit (authoritative cutoff)
curl -s https://artifacts-api.elastic.co/v1/versions/<version>/builds/<version>-<hash> \
  | jq -r '.build.projects.kibana.commit_hash'

# 2. Candidate PR's backport merge commit on the release branch
git fetch origin <release-branch>
git log origin/<release-branch> --since=<window-start> --format='%H|%cI|%s' | grep -E '\(#<PR>\)'

# 3. Ancestry test: is the backport in the BC?
git merge-base --is-ancestor <backport-commit> <bc-kibana-commit> && echo IN || echo OUT
```

Add only `IN` results. An `OUT` PR merged after the BC: record it as deferred and re-check it on the next update run against the next BC. The BC commit is often an internal-build commit a little behind the branch tip, so a PR merged shortly before the BC finished can still be `OUT`. Always test ancestry. Never use the merge timestamp.

Keep those deferred comments in the unpublished target-version section only. When the entry later lands, delete the commented block from older version sections. Do not rewrite it to `Moved to <version>`.

## Comparison

Normalize each candidate to the original user-facing PR when possible. Record:

- PR number
- Original or backport PR
- Merge date
- Branch containing the change
- Version and release-note labels
- Expected product and section
- Present in `index.md`, `breaking-changes.md`, or `deprecations.md`
- Resolution

Compare:

```text
expected - actual = potentially missed
actual - expected = potentially stale or incorrectly included
```

Do not close the reconciliation with unexplained differences.

## Common failure modes

- The generator ran before a late merge.
- A version label was missing or added after generation.
- A version or `release_note:*` label was removed and later restored after generation.
- Post-generation reconciliation searched only new merges and missed label changes on older merged PRs.
- A PR had `release_note:*` but no recognized team or feature label.
- A new feature/team label was absent from generator configuration.
- A backport merged without matching metadata on the original PR.
- The target branch contains a cherry-pick not represented by the expected PR query.
- A later `release_note:skip` PR reverted or disabled an included change.
- Multiple matching areas had equal priority and routed nondeterministically.
- A solution PR was incorrectly routed into Kibana core notes.
- An internal PR was marked for release notes despite having no user-facing effect.
