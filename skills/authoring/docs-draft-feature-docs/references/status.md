# In-flight transitions

Everything in this skill that has a shelf life. Area files hold durable facts; anything that stops being true on a known event lives here instead, so there is one file to re-read rather than six.

**Read the entry, then resolve its tracking issues before you rely on it.** Each entry carries an *expires when* condition you can check with `gh issue view <n> --repo elastic/docs-content-internal --json state,title,body`. If the condition has been met, the entry is stale: say so, follow the issue rather than this file, and open a pull request here to remove the entry.

No dates. A date is a guess about when an event will happen, and it goes wrong without anything looking wrong. The event itself is checkable.

An entry may add a **Fast path**, a named person's manual confirmation that the issue is still open. It exists to skip the live `gh issue view` round trip for someone who already knows the answer, not to replace the expiry condition above — the fast path only ever confirms *open*, never *closed*, and it carries no date of its own, since a written date is exactly what this file exists to avoid. Whoever adds one is on the hook for removing it (and re-checking the entry properly) when the underlying event actually happens; name a real backstop — a scheduled check, a calendar reminder — outside this file rather than encoding one here.

## Alerting V2 GA

**Areas:** `alerting-and-cases.md`, and `workflows.md` at the trigger seam.
**Expires when:** every sub-entry below has expired. Each has its own condition, so resolve them one at a time and remove each sub-entry as its condition is met. [#920](https://github.com/elastic/docs-content-internal/issues/920) is the umbrella issue.

The ES|QL-based alerting system is moving from experimental to GA, serverless first. Four changes run on separate schedules, and one ending does not end the others: the names can be confirmed long before the *alert episode* rename finishes.

Two rules hold across all four:

- **Do not invent a label.** If you need one that does not exist yet, it is an open question.
- **Get `applies_to` values from `docs-applies-to-tagging`**, never from this file or a neighboring page. Which version carries GA is exactly the fact that moves.

The rules that outlast every sub-entry — the alert versus rule event versus series distinctions, the substitutions, the system note, and why a term pass is not a search-replace — are durable and live in `alerting-and-cases.md`.

### Serverless GA restructure

**Expires when:** [#1880](https://github.com/elastic/docs-content-internal/issues/1880) closes. Its table lists the docs-content pull requests in merge order.

The section is being moved, regrouped, and stripped of pre-GA language as a chain of stacked pull requests, so until the chain merges, `main` sits partway between the old layout and the new one.

While this is open:

- **Resolve paths from `main`, not from the area file.** The section moves from `explore-analyze/alerting/experimental-alerting-system/` to `explore-analyze/alerting/esql/`, and a later pull request regroups it under `get-started/`, a top-level Set up page, and `manage/`. Fetch, then check which pull requests in the #1880 table have merged.
- **Ask before adding, moving, or renaming a file in the section.** A page added on `main` collides with the stacked move and regroup. Name the collision at the first approval gate, and ask whether to base on the stack or wait for it.
- **Do not add back what the restructure removed on purpose.** That covers the production-readiness sentences, scoped or not, because the lifecycle badges carry maturity, and the "How to use the documentation" callouts.
- **The two system-flow diagrams are being removed, not redrawn.** They have ALERT EPISODE baked into the image. If they are still on `main`, do not write new alt text or generate replacements.
- **The Agent Builder page stays experimental after serverless GA.** The code declares its skills for rules and action policies experimental, and they need the **Alerting V2: Experimental Features** space setting. Check the registration rather than copying the neighbors' `serverless: ga`.
- **Project-type scoping is unsettled.** Only Observability projects get the navigation menu, and the plugin does not load in Security Search AI Lake projects. Carry it as an open question until question 1 in [#1758](https://github.com/elastic/docs-content-internal/issues/1758) is answered.
- **The `alerting:v2:enabled` setting is being removed.** Without it, the system is on wherever its plugin loads, and `xpack.alerting_v2.enabled` in `kibana.yml` is the only off switch. Verify at `HEAD` which state you are documenting. The Set up page and navigation steps are being rewritten to start from global search, so check the section for shared navigation snippets before writing a menu path.

On close, fold what is now permanent into `alerting-and-cases.md`: the section path, its `_snippets/` directory, and its *Navigation* section.

### System names

**Expires when:** question 20 in [#1758](https://github.com/elastic/docs-content-internal/issues/1758) is checked, confirming the names.

The working names are *Kibana ES|QL alerting* for the new system and *Kibana standard alerting* for the existing one. The restructure sets them in the `{{alerting-v2-system}}` and `{{alerting-v1-system}}` substitutions in `docset.yml`, so a late change is an edit to two variables rather than to pages.

While this is open:

- **Use the substitutions and never type either name in prose**, including "Alerting V2" and "experimental alerting system." Quote UI labels such as **Alerting V2 Preview** exactly as `HEAD` shows them. Check that `{{alerting-v1-system}}` exists in `docset.yml` before using it, because it arrives with the restructure.
- **Use the full names.** Short forms such as "ES|QL alerting" and "standard alerting," and any mention of the former names, wait on question 15 in #1758.
- **Do not rename other pages' `{{kib}} alerting` mentions as a side effect.** Those need their page owners' agreement and are tracked in [#1898](https://github.com/elastic/docs-content-internal/issues/1898).
- **Watch for three collisions the names create.** Security has its own ES|QL detection rules, the Elasticsearch query rule in standard alerting also accepts ES|QL, and Standard is also a subscription level. Qualify each on first use, and never write a bare "standard" in prose.

On close, move the confirmed names and the three collisions into `alerting-and-cases.md` as durable traps, and add the ES|QL detection rule collision to `elastic-security.md` from its side.

### Stack GA

**Expires when:** [#1738](https://github.com/elastic/docs-content-internal/issues/1738) closes.

While this is open:

- **Do not change the stack lifecycle tags yourself.** That change waits on the GA path, question 4 in #1758, and lands in [#1761](https://github.com/elastic/docs-content-internal/issues/1761).
- **Treat quoted navigation labels as unstable** until they are rechecked against the release after its feature freeze, in [#1893](https://github.com/elastic/docs-content-internal/issues/1893). That includes the navigation entry, the Rules page tabs, and the unified Alerts page. Verify every quoted label at `HEAD`.
- **Feature docs for the release are tracked in [#1652](https://github.com/elastic/docs-content-internal/issues/1652).** Read the item's doc issue there before starting.

### The "alert episode" to "alert" rename

**Areas:** also `workflows.md`, for the `alerting.episode*` trigger IDs and the `event.episodeId` payload field.
**Expires when:** [#1791](https://github.com/elastic/docs-content-internal/issues/1791) and [#1917](https://github.com/elastic/docs-content-internal/issues/1917) close.

The rename is confirmed, but it reaches the product in pieces with no fixed order, and the docs follow the product rather than lead it.

While this is open:

- **Keep "alert episode" in prose until the UI at `HEAD` says "alert."** Check the strings, not the plan.
- **Verify every stored name at `HEAD`.** Engineering is renaming the `.rule-events` fields, the `.alert-actions` fields, the action policy matchers, and the workflow trigger IDs, each on its own schedule. Quote what `HEAD` uses, and never infer a renamed field from the pattern.
- **Do not add a rename note to a page.** The section's shared system note carries one sentence saying the rename is in progress and pointing readers to the Serverless changelog ([#1899](https://github.com/elastic/docs-content-internal/issues/1899)).

On close, rewrite the terminology bullets in `alerting-and-cases.md` for the object name and field mapping that shipped, and update the trigger notes in `workflows.md`.

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
