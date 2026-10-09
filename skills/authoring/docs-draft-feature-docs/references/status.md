# In-flight transitions

Everything in this skill that has a shelf life. Area files hold durable facts; anything that stops being true on a known event lives here instead, so there is one file to re-read rather than six.

**Read the entry, then resolve its tracking issues before you rely on it.** Each entry carries an *expires when* condition you can check with `gh issue view <n> --repo elastic/docs-content-internal --json state,title,body`. If the condition has been met, the entry is stale: say so, follow the issue rather than this file, and open a pull request here to remove the entry.

No dates. A date is a guess about when an event will happen, and it goes wrong without anything looking wrong. The event itself is checkable.

An entry may add a **Fast path**, a named person's manual confirmation that the issue is still open. It exists to skip the live `gh issue view` round trip for someone who already knows the answer, not to replace the expiry condition above — the fast path only ever confirms *open*, never *closed*, and it carries no date of its own, since a written date is exactly what this file exists to avoid. Whoever adds one is on the hook for removing it (and re-checking the entry properly) when the underlying event actually happens; name a real backstop — a scheduled check, a calendar reminder — outside this file rather than encoding one here.

## Alerting V2 GA

**Areas:** `alerting-and-cases.md`, and `workflows.md` at the trigger seam.
**Expires when:** every sub-entry below has expired. Each has its own condition, so resolve them one at a time and remove each sub-entry as its condition is met. [#920](https://github.com/elastic/docs-content-internal/issues/920) is the umbrella issue.

The ES|QL-based alerting system, now named Kibana Universal Alerting, is moving from experimental to GA, serverless first. Four changes run on separate schedules, and one ending does not end the others: the names are final and the product says "alert," but the section has not reached `main` and the pages outside it still say "alert episode."

Two rules hold across all four:

- **Do not invent a label.** If you need one that does not exist yet, it is an open question.
- **Get `applies_to` values from `docs-applies-to-tagging`**, never from this file or a neighboring page. Which version carries GA is exactly the fact that moves.

The rules that outlast every sub-entry — the system names and substitutions, the alert versus rule event versus series distinctions, the stored-name mapping, the system note, and why a term pass is not a search-replace — are durable and live in `alerting-and-cases.md`.

### Serverless GA restructure

**Expires when:** [#1880](https://github.com/elastic/docs-content-internal/issues/1880) closes. Its table lists the docs-content pull requests in merge order.

The section is being moved, regrouped, renamed, and stripped of pre-GA language as a chain of stacked pull requests. Everything merged so far has merged into the base of the stack, elastic/docs-content#8516, not into `main`, so until it merges, `main` still has the old layout, the old names, and "alert episode" throughout the section.

While this is open:

- **Resolve paths from `main`, not from the area file.** elastic/docs-content#8516 moves the section from `explore-analyze/alerting/experimental-alerting-system/` to `explore-analyze/alerting/esql/` and regroups it under `get-started/`, a top-level Set up page, `rules/`, `alerts/`, `action-policies/`, and `manage/`. The `esql` path is final even though the system name leaves out ES|QL, because docs own the path and it has to stay stable. Fetch, then check which pull requests in the #1880 table have merged.
- **Ask before adding, moving, or renaming a file in the section.** A page added on `main` collides with the stacked move and regroup. Name the collision at the first approval gate, and ask whether to base on the stack or wait for it.
- **Check `docset.yml` on `main` before using a system substitution.** Until elastic/docs-content#8516 merges, `{{alerting-v2-system}}` on `main` still renders the old name, and `{{alerting-v1-system}}` does not exist. Use the substitutions anyway, because they are what the stack changes, but do not draft against the rendered text.
- **Do not add back what the restructure removed on purpose.** That covers the production-readiness sentences, scoped or not, because the lifecycle badges carry maturity; the "How to use the documentation" callouts; and the system note on every page, which now appears only on the section landing pages.
- **The two system-flow diagrams are being removed, not redrawn.** They have ALERT EPISODE baked into the image. If they are still on `main`, do not write new alt text or generate replacements.
- **The Agent Builder page stays experimental after serverless GA.** The code declares its skills for rules and action policies experimental, and they need the **Alerting V2: Experimental Features** space setting. Check the registration rather than copying the neighbors' `serverless: ga`.
- **Project-type scoping is unsettled.** Only Observability projects get the navigation menu, and the plugin does not load in Security Search AI Lake projects. Carry it as an open question until question 1 in [#1758](https://github.com/elastic/docs-content-internal/issues/1758) is answered.
- **The `alerting:v2:enabled` setting stays, and turns on by default.** elastic/kibana#296546 replaced the plan to remove it: the setting now defaults to on, a stored `false` stays off, and turning it off hides the UI and rejects API requests but does not stop rules from running. Only `xpack.alerting_v2.enabled: false` in `kibana.yml` does that. Verify at `HEAD` which state you are documenting; the Set up page update in elastic/docs-content#8735 waits on that pull request deploying to Serverless.
- **Navigation steps are moving to the new menu.** elastic/docs-content#8736 replaces the **Alerting V2 Preview** steps with the **Alerting** menu for Serverless and later Stack versions, and keeps the old steps for 9.5. Check the section for shared navigation snippets before writing a menu path.

On close, fold what is now permanent into `alerting-and-cases.md`: the section path, its `_snippets/` directory, and its *Navigation* section.

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

- **Do not change the stack lifecycle tags yourself.** That change waits on the GA path, question 4 in #1758, and lands in [#1761](https://github.com/elastic/docs-content-internal/issues/1761).
- **Treat quoted navigation labels as unstable** until they are rechecked against the release after its feature freeze, in [#1893](https://github.com/elastic/docs-content-internal/issues/1893). That includes the navigation entry, the Rules page tabs, and the unified Alerts page. Verify every quoted label at `HEAD`.
- **Some labels are renamed to match the system names, but not yet.** elastic/rna-program#1108 renames the Rules page tabs to **Classic** and **Universal**, some privilege labels, and the maintenance window scope options, and elastic/rna-program#1206 renames the **Alerting V2** and **Alerting V2: Experimental Features** settings to **Universal Alerting** and **Universal Alerting: Experimental Features**. Quote the label `HEAD` shows until each one ships, never the planned one.
- **Feature docs for the release are tracked in [#1652](https://github.com/elastic/docs-content-internal/issues/1652).** Read the item's doc issue there before starting.

### The "alert episode" to "alert" rename

**Areas:** also `workflows.md`, for the trigger IDs and the `event.alertId` payload field.
**Expires when:** [#1791](https://github.com/elastic/docs-content-internal/issues/1791) and [#1917](https://github.com/elastic/docs-content-internal/issues/1917) close.

The product rename has shipped: Kibana `main` says "alert" in the UI (elastic/kibana#295620), and the stored names were renamed with it, as the mapping table in `alerting-and-cases.md` records. elastic/docs-content#8532 renamed the term across the section and the workflow trigger pages, on the restructure stack. #1791 and #1917 track what is left.

While this is open:

- **Do not "fix" a label the product has not fixed.** Four UI strings on `main` still say "alert episode," and so do about 40 summaries in the API reference. Quote them as `HEAD` shows them until Kibana changes them.
- **Expect "alert episode" on `main` until the restructure merges.** That is the stack waiting, not a page to rename by hand. Edit those pages on the stack, or wait for it.
- **Do not add a rename note to a page.** The overview and the glossary carry the only one, a sentence scoped to 9.5 saying that the UI there calls an alert an *alert episode*.

On close, remove this sub-entry. The durable rules it produced are already in `alerting-and-cases.md`, so only recheck that its mapping table still matches `HEAD`.

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
