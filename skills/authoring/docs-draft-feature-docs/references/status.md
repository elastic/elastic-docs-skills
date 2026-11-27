# In-flight transitions

Everything in this skill that has a shelf life. Area files hold durable facts; anything that stops being true on a known event lives here instead, so there is one file to re-read rather than six.

**Read the entry, then resolve its tracking issues before you rely on it.** Each entry carries an *expires when* condition you can check with `gh issue view <n> --repo elastic/docs-content-internal --json state,title,body`. If the condition has been met, the entry is stale: say so, follow the issue rather than this file, and open a pull request here to remove the entry.

No dates. A date is a guess about when an event will happen, and it goes wrong without anything looking wrong. The event itself is checkable.

An entry may add a **Fast path**, a named person's manual confirmation that the issue is still open. It exists to skip the live `gh issue view` round trip for someone who already knows the answer, not to replace the expiry condition above — the fast path only ever confirms *open*, never *closed*, and it carries no date of its own, since a written date is exactly what this file exists to avoid. Whoever adds one is on the hook for removing it (and re-checking the entry properly) when the underlying event actually happens; name a real backstop — a scheduled check, a calendar reminder — outside this file rather than encoding one here.

## Alerting V2 GA

**Areas:** `alerting-and-cases.md`, and `workflows.md` at the trigger seam.
**Expires when:** every sub-entry below has expired. Each has its own condition, so resolve them one at a time and remove each sub-entry as its condition is met. [#920](https://github.com/elastic/docs-content-internal/issues/920) is the umbrella issue.

The ES|QL-based alerting system, now named Kibana Universal Alerting, is GA on Serverless. Its section moved to `explore-analyze/alerting/esql/` with that release, and its pages now describe only the GA version, a decision recorded in `alerting-and-cases.md`. Two changes are still open, and each finishes on its own schedule: the Classic Alerting name on pages outside the section, and the Stack release.

Two rules hold across both:

- **Do not invent a label.** If you need one that does not exist yet, it is an open question.
- **Get `applies_to` values from `docs-applies-to-tagging`**, never from this file or a neighboring page. Which version carries Stack GA is exactly the fact that can still move.

The rules that outlast every sub-entry — the system names and substitutions, the GA-only scope and its upgrade note, the alert versus rule event versus series distinctions, the stored-name mapping, the system note, the section layout and product navigation, and why a term pass is not a search-replace — are durable and live in `alerting-and-cases.md`.

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

- **The Stack tags already say GA, with no 9.5 value.** elastic/docs-content#9019 set them, following docs-content-internal#2079. [#1761](https://github.com/elastic/docs-content-internal/issues/1761) is still open and still describes the earlier plan to keep `experimental =9.5`, but #2079 superseded that plan, so do not follow #1761's task list. If the Stack GA path changes (question 4 in #1758), the fix is a lifecycle or version edit that `docs-applies-to-tagging` makes, never a return to 9.5 content.
- **Verify every quoted label at `HEAD`.** They are rechecked against the release after its feature freeze in [#1893](https://github.com/elastic/docs-content-internal/issues/1893). elastic/kibana#294597 shipped the Rules tabs, alert source labels, banners, badges, maintenance-window scope options, privilege labels, and the first Advanced Settings renames; elastic/kibana#296790 subsequently finalized the two remaining Advanced Settings labels. Quote what `HEAD` shows, never an earlier plan.
- **Check elastic/docs-content#8536 before editing the rule settings pages.** It is open against `main` and edits four pages that elastic/docs-content#9019 also cut heavily: the recovery, alert delay, and no-data handling pages, and the YAML rule schema reference. Check with `gh pr view 8536 --repo elastic/docs-content --json state`, and expect it to need a rebase onto the GA-only pages.
- **Do not say whether the APIs work outside Observability projects.** The docs send Serverless readers to an Observability project, but whether the APIs also work in other project types is still question 1 in #1758.
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
