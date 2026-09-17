# In-flight transitions

Everything in this skill that has a shelf life. Area files hold durable facts; anything that stops being true on a known event lives here instead, so there is one file to re-read rather than six.

**Read the entry, then resolve its tracking issues before you rely on it.** Each entry carries an *expires when* condition you can check with `gh issue view <n> --repo elastic/docs-content-internal --json state,title,body`. If the condition has been met, the entry is stale: say so, follow the issue rather than this file, and open a pull request here to remove the entry.

No dates. A date is a guess about when an event will happen, and it goes wrong without anything looking wrong. The event itself is checkable.

## Alerting V2 GA

**Areas:** `alerting-and-cases.md`, and `workflows.md` at the trigger seam.
**Expires when:** [#1758](https://github.com/elastic/docs-content-internal/issues/1758) closes, which freezes the names. Full GA is tracked in [#920](https://github.com/elastic/docs-content-internal/issues/920), [#1652](https://github.com/elastic/docs-content-internal/issues/1652), and [#1738](https://github.com/elastic/docs-content-internal/issues/1738).

The ES|QL alerting system is moving from experimental to GA, and the object called an *alert episode* is being renamed to *alert*. Serverless GA lands before stack GA.

While this is open:

- **Do not draft the GA names as fact.** Final system names, capitalization, and which UI strings still say Episode are unfrozen. Keep the current experimental language, or mark new behavior as planned.
- **Do not invent a label.** If you need one that does not exist yet, it is an open question.
- **Production status is a scoping problem, not a sentence to delete.** The pages currently say the system is not ready for production. That becomes false for serverless and for the GA stack version while staying true for the experimental one, so it gets scoped rather than removed.
- **Do not present V2 as the default answer** to an alerting question until GA ships.
- Get the target `applies_to` values from `docs-applies-to-tagging` rather than from this file. Which version carries GA is exactly the fact that moves.

The rules that survive the rename — the alert versus rule event versus series distinctions, the substitutions, and why a term pass is not a search-replace — are durable and live in `alerting-and-cases.md`.

## Elastic Security docset restructure

**Areas:** `elastic-security.md`.
**Expires when:** [#1541](https://github.com/elastic/docs-content-internal/issues/1541) closes, meaning the pull request stack has fully merged.

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
