# Area registry

`docs-draft-feature-docs` checks this file in Phase 1, after the baseline is loaded and before drafting.

Resolve in this order. Stop at the first hit **for a single-area request** — but a request can span areas, and several rows below name the seams where that happens. When it does, load every file that owns a piece of the request and say which half went where.

## 1. Specialist skills — delegate and stop

These areas already have a dedicated drafting skill. Hand off and do not draft a second opinion.

| Area | Delegate to | Scope |
|---|---|---|
| Lens charts — `explore-analyze/visualize/charts/` | `docs-lens-chart-page` | Individual chart type pages. Pairs with `docs-lens-chart-settings` for verifying UI labels |
| Cases — `explore-analyze/cases/`, solution case pages, case settings reference | `docs-draft-cases-docs` | **Migration pending.** Delegate for now: `alerting-and-cases.md` covers Cases in about a dozen lines while this skill has a full area-specific ruleset. Once those rules move into a `cases.md` area file, this row moves down and the skill retires |

`docs-lens-chart-page` runs `context: fork`, so it returns a result rather than a running conversation. **Confirm a specialist is actually installed before routing to it** — a delegation to a skill that is not on the machine fails, and deriving from the area file or sibling pages is better than stopping.

This table is transitional, and Workflows has already made the trip: its area knowledge moved into `workflows.md` and its row moved down. Do the same for any remaining specialist whose value is facts rather than process. Until then, delegation wins for the rows above — a specialist that is installed and tested beats a generic draft.

## 2. Area files — load and apply

| Area | File | Notes |
|---|---|---|
| Elastic Security — `solutions/security/`, `reference/security/` | `elastic-security.md` | **Needs a refresh after the docset restructure** ([docs-content-internal#1541](https://github.com/elastic/docs-content-internal/issues/1541), deadline 2026-10-31). Read the note at the top of the file before trusting its paths |
| Alerting and Cases — `explore-analyze/alerting/`, `explore-analyze/cases/` | `alerting-and-cases.md` | Platform capabilities the solutions also surface, so placement is the main risk. **Alerting V2 is mid-GA-transition with its names unfrozen** — read the note at the top of the file before drafting any alerting page |
| Elastic Workflows — `explore-analyze/workflows/` | `workflows.md` | Step references, triggers, authoring techniques, use cases, concepts, reference. Migrated from the `docs-draft-workflow-docs` skill. Meets `alerting-and-cases.md` at triggers |
| Kibana settings reference — `reference/kibana/advanced-settings`, `reference/kibana/configuration-reference/` | `kibana-settings-reference.md` | **Not in docs-content** — these publish from `elastic/kibana` under `docs/`, and the content is settings YAML rather than prose. Read the file before assuming `$DOCS_CONTENT_ROOT` is the working tree |
| Elastic Agent Builder — `explore-analyze/ai-features/agent-builder/` | `agent-builder.md` | Agents, skills, tools, MCP and A2A servers. The landing page is `elastic-agent-builder.md`, not `agent-builder.md`. Split from `ai-features.md` on size |
| AI-powered features — `explore-analyze/ai-features/`, `solutions/*/ai/` | `ai-features.md` | The hub, AI assistants, LLM connector guides, Automatic Import. **Placement is a three-way platform-or-solution decision** and the three assistants are separate plugins. Meets `elastic-security.md` |

An area file **adds** facts and narrows choices. It can never override the style guide, content types, cumulative-docs rules, or the approval gates. When an area file appears to contradict the baseline, follow the baseline and flag the conflict.

## 3. Neither — derive and say so

Continue with the baseline alone. Derive conventions from sibling pages in the target directory, and state in the output that no area file existed, so the next person knows what to add.

## Adding an area

1. Copy `_template.md` to `<area-name>.md`, named for the docs area rather than the engineering team, since teams get reorganized and directories mostly do not.
2. Fill all six headings and the verification note the template asks for. Every path and label gets verified before it goes in — an area file is a source of truth, so a wrong path here is worse than a missing file.
3. Add the row to the table above, and name any area it shares a seam with. Add the reciprocal line to that area's file too, so the seam is visible from both sides.
4. Keep it under about 150 lines. Past that, the area is really several areas, or facts are being duplicated from the baseline.

Record facts that are stable and checkable: where pages live, which code path settles a question, what local convention differs from the default. Do not record anything that restates the style guide, or anything that will be stale in a month.
