# Area registry

`docs-draft-feature-docs` checks this file in Phase 1, after the baseline is loaded and before drafting.

Resolve in this order and stop at the first hit.

## 1. Specialist skills — delegate and stop

These areas already have a dedicated drafting skill. Hand off and do not draft a second opinion.

| Area | Delegate to | Scope |
|---|---|---|
| Workflows — `explore-analyze/workflows/` | `docs-draft-workflow-docs` | Step references, use cases, how-tos, concepts, overviews. Also handles workflow YAML as input. `alerting-cases-workflows.md` covers the boundary this shares with alerting, but drafting still goes to the specialist |
| Lens charts — `explore-analyze/visualize/charts/` | `docs-lens-chart-page` | Individual chart type pages. Pairs with `docs-lens-chart-settings` for verifying UI labels |

Both are `context: fork`, so they return a result rather than a running conversation.

This table is transitional. When a specialist's area knowledge is reduced to an area file below, it can retire and its row moves down. Until then, delegation wins — a specialist that is already installed and tested beats a generic draft.

## 2. Area files — load and apply

| Area | File | Notes |
|---|---|---|
| Elastic Security — `solutions/security/`, `reference/security/` | `elastic-security.md` | **Needs a refresh after the docset restructure** ([docs-content-internal#1541](https://github.com/elastic/docs-content-internal/issues/1541), deadline 2026-10-31). Read the note at the top of the file before trusting its paths |
| Alerting, Cases, and Workflows — `explore-analyze/alerting/`, `cases/`, `workflows/` | `alerting-cases-workflows.md` | Platform capabilities the solutions also surface, so placement is the main risk. **Alerting V2 is mid-GA-transition with its names unfrozen** — read the note at the top of the file before drafting any alerting page. Workflows drafting still delegates to the specialist above |

An area file **adds** facts and narrows choices. It can never override the style guide, content types, cumulative-docs rules, or the approval gates. When an area file appears to contradict the baseline, follow the baseline and flag the conflict.

## 3. Neither — derive and say so

Continue with the baseline alone. Derive conventions from sibling pages in the target directory, and state in the output that no area file existed, so the next person knows what to add.

## Adding an area

1. Copy `_template.md` to `<area-name>.md`, named for the docs area rather than the engineering team, since teams get reorganized and directories mostly do not.
2. Fill all six headings. Every path and label gets verified before it goes in — an area file is a source of truth, so a wrong path here is worse than a missing file. Record the date you verified it, and if a restructure or migration is already known to be coming, say so at the top of the file. A stale path that looks confident is the main way an area file does damage.
3. Add the row to the table above.
4. Keep it under about 150 lines. Past that, the area is really several areas, or facts are being duplicated from the baseline.

Record facts that are stable and checkable: where pages live, which code path settles a question, what local convention differs from the default. Do not record anything that restates the style guide, or anything that will be stale in a month.
