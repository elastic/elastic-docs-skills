# In-flight transitions

Everything in this skill that has a shelf life. Area files hold durable facts; anything that stops being true on a known event lives here instead, so there is one file to re-read rather than six.

**Read the entry, then resolve its tracking issues before you rely on it.** Each entry carries an *expires when* condition you can check with `gh issue view <n> --repo elastic/docs-content-internal --json state,title,body`. If the condition has been met, the entry is stale: say so, follow the issue rather than this file, and open a pull request here to remove the entry.

No dates. A date is a guess about when an event will happen, and it goes wrong without anything looking wrong. The event itself is checkable.

An entry may add a **Fast path**, a named person's manual confirmation that the issue is still open. It exists to skip the live `gh issue view` round trip for someone who already knows the answer, not to replace the expiry condition above — the fast path only ever confirms *open*, never *closed*, and it carries no date of its own, since a written date is exactly what this file exists to avoid. Whoever adds one is on the hook for removing it (and re-checking the entry properly) when the underlying event actually happens; name a real backstop — a scheduled check, a calendar reminder — outside this file rather than encoding one here.

## Alerting V2 GA

**Areas:** `alerting-and-cases.md`, and `workflows.md` at the trigger seam.
**Expires when:** every sub-entry below has expired. Each has its own condition, so resolve them one at a time and remove each sub-entry as its condition is met. [#920](https://github.com/elastic/docs-content-internal/issues/920) is the umbrella issue.

The ES|QL-based alerting system, now named Kibana Universal Alerting, is moving from experimental to GA, serverless first. Four changes run on separate schedules, and one ending does not end the others. The section move lands with the Serverless release, but its follow-up pull requests, the short-name decision, and Stack GA each finish later.

Two rules hold across all four:

- **Do not invent a label.** If you need one that does not exist yet, it is an open question.
- **Get `applies_to` values from `docs-applies-to-tagging`**, never from this file or a neighboring page. Which version carries GA is exactly the fact that moves.

The rules that outlast every sub-entry — the system names and substitutions, the alert versus rule event versus series distinctions, the stored-name mapping, the system note, the section layout, and why a term pass is not a search-replace — are durable and live in `alerting-and-cases.md`.

### Before the section move merges

**Expires when:** elastic/docs-content#8516 merges. Check with `gh pr view 8516 --repo elastic/docs-content --json state`. It is held for the Serverless release, and merging it also closes [#1791](https://github.com/elastic/docs-content-internal/issues/1791) and [#1917](https://github.com/elastic/docs-content-internal/issues/1917), the "alert episode" rename issues.

elastic/docs-content#8516 holds everything that ships with the release: the move, the regroup, the final names, the "alert episode" to "alert" rename, the `serverless: ga` tags, and a redirect for each moved page. Eight pull requests were squash-merged into it rather than into `main`, so until it merges, `main` has none of that.

While this is open:

- **`main` does not match the area file.** The section is still at `explore-analyze/alerting/experimental-alerting-system/`, the overview is still at `alerting/system-overview.md`, the section has no `_snippets/`, `{{alerting-v2-system}}` still renders the old name, `{{alerting-v1-system}}` does not exist, and the pages say "alert episode." The area file describes the layout after the merge, so resolve paths from `main` or from the pull request branch, depending on which one you are drafting against.
- **Ask before adding, moving, or renaming a file in the section.** A page added on `main` collides with the move. Name the collision at the first approval gate, and ask whether to base on elastic/docs-content#8516 or wait for it.
- **Use the substitutions anyway**, because they are what the merge changes, but do not draft against the text they render on `main`.
- **Do not rename "alert episode" by hand, redraw the two system-flow diagrams, or write alt text for them.** The merge renames the term and removes the diagrams.

On close, remove this sub-entry. The area file already describes the merged layout, so recheck its *Navigation* section against `main` and bump its `verified:` date.

### Serverless GA follow-ups

**Expires when:** [#1880](https://github.com/elastic/docs-content-internal/issues/1880) closes. Its tables list the pull requests that merge after elastic/docs-content#8516, each with what it waits for. Expect it to stay open well after the section move merges.

While this is open:

- **Check the open follow-up pull requests before editing what they touch.** elastic/docs-content#8736 replaces the navigation steps on the section's pages, elastic/docs-content#8734 and elastic/docs-content#8735 rewrite the Set up page, and elastic/docs-content#8536 documents the unified rule query schema on the rule query pages. Each is stacked on elastic/docs-content#8516, so an edit to the same page on `main` collides with it.
- **Do not add back what the restructure removed on purpose.** That covers the production-readiness sentences, scoped or not, because the lifecycle badges carry maturity; the "How to use the documentation" callouts; and the system note on every page, which now appears only on the section landing pages.
- **The Agent Builder page stays experimental after serverless GA.** The code declares its skills for rules and action policies experimental, and they need the `alerting:v2:experimentalFeatures` space setting, labeled **Universal Alerting experimental features** at `HEAD`. elastic/kibana#296790 might relabel it again, so quote the label `HEAD` shows. Check the registration rather than copying the neighbors' `serverless: ga`.
- **Project-type scoping is unsettled.** Only Observability projects get the **Alerting** menu, the plugin does not load in Security Search AI Lake projects, and elastic/kibana#295505 hides the Universal Alerting privileges in serverless projects other than Observability. Carry it as an open question until question 1 in [#1758](https://github.com/elastic/docs-content-internal/issues/1758) is answered.
- **The `alerting:v2:enabled` setting stays, but its default is in flight.** Its label is **Universal Alerting**, and at `HEAD` it still defaults to off. elastic/kibana#296546, still open, turns it on by default, and the Set up page update in elastic/docs-content#8735 waits for that pull request to deploy. Turning the setting off hides the UI and rejects API requests but does not stop rules from running; only `xpack.alerting_v2.enabled: false` in `kibana.yml` does that. Verify the default at `HEAD` before writing it down.
- **The navigation changed, and three labels are easy to get wrong.** **Alerting V2 Preview** is gone from Serverless and later Stack versions, and 9.5 keeps it. In the Observability **Alerting** menu, **Alerts** opens the Universal Alerting alerts page, and **Alerts (V1)** opens the Classic one, but only when the `alerting:v1:showV1ObservabilityAlertsTable` space setting, **Show V1 Observability alerts table**, is on. **Inbox** is a global search keyword, not a label, so never quote it as one. Check the section for shared navigation snippets before writing a menu path.

On close, fold the navigation that is now permanent into the *Navigation* section of `alerting-and-cases.md`.

### Short forms, former names, and other pages

**Expires when:** [#1898](https://github.com/elastic/docs-content-internal/issues/1898) closes.

The names themselves are final: Kibana Universal Alerting and Kibana Classic Alerting, decided in elastic/rna-program#1108, and recorded in `alerting-and-cases.md`. What is still open is how far they reach beyond the section.

While this is open:

- **Use the full names, through the substitutions.** The decision lists short names (Universal Alerting, Classic Alerting) and object forms (Universal rules, Classic alerts), but #1898 allows a short name only where the system is already clear, and whether the landing pages mention the former names waits on question 15 in [#1758](https://github.com/elastic/docs-content-internal/issues/1758).
- **Do not rename other pages' `{{kib}} alerting` mentions as a side effect.** #1898 lists them. Six are H1s, so they change page titles in search results and need their page owners' agreement first. A handful of general uses, meaning alerting in {{kib}} rather than the system by name, stay as they are.
- **Leave the Streams significant events attribution alone.** The Streams operator guide credits `{{kib}} alerting` for rules that write to `.rule-events`, which belongs to Universal Alerting. Which system to name waits on question 16 in #1758.

On close, move the short-form rule into the substitutions paragraph of `alerting-and-cases.md`, and drop the former-name list from its first trap if the docs no longer mention them anywhere.

### Stack GA

**Expires when:** [#1738](https://github.com/elastic/docs-content-internal/issues/1738) closes.

While this is open:

- **Do not change the stack lifecycle tags yourself.** That change waits on the GA path, question 4 in #1758, and lands in [#1761](https://github.com/elastic/docs-content-internal/issues/1761). The 9.5 label is disputed too: the docs say experimental, and the Kibana settings reference says preview (question 5).
- **Verify every quoted label at `HEAD`.** They are rechecked against the release after its feature freeze in [#1893](https://github.com/elastic/docs-content-internal/issues/1893). Some renames have shipped: elastic/kibana#294597 renamed the Roles privilege category to **Universal Alerting** and the **Observability Alerts** feature to **Classic Observability Alerts**, along with the two settings above. Others have not: elastic/rna-program#1108 still plans to rename the Rules page tabs, the alert source labels, banners, badges, and the maintenance window scope options. A few UI strings, and many API reference summaries, still say "alert episode." Quote what `HEAD` shows, never the plan.
- **The unified alerts table is not documented yet.** It shows alerts from both systems together and ships with the Serverless release, announced only in the release notes. Its docs are elastic/docs-content#8226, part of question 8 in #1758. Until they land, do not describe it from a neighboring page.
- **Read question 7 in #1758 before writing about upgrading from 9.5.** The field rename recreates `.rule-events` and deletes older `.alert-actions` data, so upgrading erases alert history and triage actions. Whether users get a release note or an upgrade note is still open, and release notes come from Kibana pull request labels rather than from the docs.
- **The API routes might be renamed to match the system name** (question 10 in #1758). There is no tracking pull request yet, so quote the route `HEAD` uses, `/api/alerting/v2/` at last check.
- **Feature docs for the release are tracked in [#1652](https://github.com/elastic/docs-content-internal/issues/1652).** Read the item's doc issue there before starting.

## Elastic Security docset restructure

**Areas:** `elastic-security.md`.
**Expires when:** [#1541](https://github.com/elastic/docs-content-internal/issues/1541) closes, meaning the pull request stack has fully merged.
**Fast path:** Confirmed still open by nastasha.solomon@elastic.co — no PRs are landing in the restructured TOC yet, only in the current structure on main. Skip the live issue check and treat this entry as open until this line is removed.
<!-- A scheduled daily check of #1541 (task "security-restructure-skill-update-reminder") notifies nastasha.solomon@elastic.co when it closes. When that happens, remove this whole entry per "Adding an entry" below — not just this fast-path line. -->

The Security docset is being reorganized around reader posture, shipping as a stack of pull requests. Most of the change regroups `toc.yml` and keeps paths, but a few directories actually move.

While this is open:

- **Treat every path in `elastic-security.md` as a hint.** Mid-stack the repo is half-moved, so resolve paths with `search_docs` and the local tree rather than from the file.
- A directory that moved needs a redirect; one that only got regrouped does not. Check which happened before adding to `redirects.yml`.
- On close, refresh the *Navigation* and *Known traps* sections of `elastic-security.md`, and recheck the eval asserting that Security navigation is inline in `solutions/toc.yml` with no per-solution toc. That holds only if the new wrapper sections did not adopt nested sub-tocs.

## Cases specialist migration

**Areas:** `index.md`, `alerting-and-cases.md`.
**Expires when:** a `cases.md` area file exists in this directory and the `docs-draft-cases-docs` row is removed from the specialist table in `index.md`.

`docs-draft-cases-docs` is registered as a specialist and delegated to, but it is not in this catalog — it exists only as a locally installed skill, so anyone running from the plugin will not have it. `alerting-and-cases.md` covers Cases only as a placement aid.

While this is open:

- **Check whether the specialist is installed before delegating.** When it is not, draft from `alerting-and-cases.md` and say in the output that Cases has no area file yet, so the gap is visible.
- Most of that skill is duplicated drafting process, so the migration is smaller than its size suggests. Only the Cases-specific rules need to move.

## Adding an entry

An entry belongs here when it will stop being true on an event someone can check. If it will stop being true on a date, find the event behind the date. If there is no event, it is probably a durable fact that belongs in an area file.

1. Name the transition, the areas it touches, and the *expires when* condition with its tracking issues.
2. Say what to do while it is open, as instructions rather than status.
3. Add `status: references/status.md#<anchor>` to the frontmatter of every area file it affects.
4. Leave the durable rules in the area file. Only the part with a shelf life comes here.
5. When one transition is really several that end on different events, give each its own *expires when* as a `###` sub-entry under a single `##` entry. Area files point at the `##` anchor, which is the only level CI checks, and each sub-entry can then expire on its own.
