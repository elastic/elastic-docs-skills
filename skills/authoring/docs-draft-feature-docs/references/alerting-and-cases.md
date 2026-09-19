---
area: Alerting and Cases
verified: 2026-09-16
verified_against:
  - docs-content
  - elastic/kibana
status: references/status.md#alerting-v2-ga
---

# Alerting and Cases

Two sections of the `explore-analyze/` docset that share one trait: each documents a **platform** capability that the solutions also surface in their own docs. Almost every mistake in this area is a placement mistake rather than a writing mistake.

The boundary that matters: this area owns the cross-solution behavior. When a capability exists only inside Security or Observability, it belongs to that solution's page instead.

> **Alerting V2 is mid-GA-transition and its names are not frozen.** Read [`status.md`](status.md#alerting-v2-ga) and resolve its tracking issues before drafting any alerting page. The durable rules that survive the rename are below, in *Conventions* and *Known traps*.
>
> **Workflows is a sibling area file**, `workflows.md`, not a section of this one. The two meet at triggers and at `workflows-alerting.md`, so read both when drafting at that seam.

## What belongs here, and what does not

| The content is | Home |
|---|---|
| Cross-solution alerting or case behavior | Here, under `explore-analyze/alerting/` or `explore-analyze/cases/` |
| A new Observability rule type, or anything SLO | `solutions/observability/incident-management/`. **Observability alerting is its own system**, layered on {{kib}} alerting GA rather than a peer of it, and it owns its own rule-type catalog and Alerts page |
| A Security detection rule or its alerts | `solutions/security/detect-and-alert/`. A fifth system entirely, not a rule type of {{kib}} alerting |
| What one solution adds to Cases | The solution's own case page, thin, linking to the core. Core case behavior is documented once and nowhere else |
| Creating alerts from Agent Builder | `agent-builder.md` owns that seam from its side |
| Anything about authoring workflows | `workflows.md` |

While `docs-draft-cases-docs` is registered as a specialist, **delegate Cases drafting to it.** The Cases material in this file is a placement aid, not a drafting ruleset — it is here so that an alerting request does not misfile case content.

Check for an alerting- or cases-specific `_snippets/` directory before writing shared prose. At last check there was none and only the docset-level `explore-analyze/_snippets/` existed, which means shared prose in these two sections is duplicated rather than included.

## Source of truth

Platform plugins sit under `x-pack/platform/plugins/shared/`. Workflows is the exception and lives under `src/platform/`.

| Question | Verify at |
|---|---|
| Rules and Connectors UI labels | `triggers_actions_ui/` — this is the UI for both, so most alerting label questions end here rather than in the framework plugin |
| Alerting framework, rule execution, rule types | `alerting/` |
| Observability alerting and its rule types | `x-pack/solutions/observability/plugins/observability_alerting/`, plus `apm/`, `infra/`, and `synthetics/` in the same tree, which register their own rule types |
| The experimental system | `alerting_v2/` — **a separate plugin.** Searching `alerting/` for experimental behavior finds nothing and looks like the feature is absent |
| The workflow triggers it emits | `alerting_v2/common/workflows/triggers/`, one file per trigger; `rg "TriggerId = '"` lists the IDs. Workflows' own `builtin_trigger_definitions.ts` does not carry them, which is the seam `workflows.md` describes |
| Connector and action types | `stack_connectors/` for individual connectors, `actions/` for the framework |
| Cases behavior, fields, templates | `cases/` |
| Watcher | The `elastic/elasticsearch` repo, not Kibana |

## Conventions

The three sections do **not** share one frontmatter shape, so copy from the neighbor rather than from another section. Classic alerting carries `mapped_pages` and is often `products: kibana` alone; the experimental system carries no `mapped_pages` because it is new; Cases pages carry all four products, reflecting the consolidation; and `compare-alerting-systems.md` also carries `elasticsearch` and `cloud-hosted`, because Watcher is an Elasticsearch feature.

Use the substitutions: `{{kib}}`, `{{stack-manage-app}}` for Stack Management, `{{rules-ui}}` for Rules, `{{connectors-ui}}` for Connectors, `{{siem-rules-ui}}` for Detection rules (SIEM), and `{{alerting-v2-system}}` / `{{alerting-v2-system-cap}}` for the experimental alerting system. Never type "experimental alerting system" literally — the substitution will be repointed to the GA name, so hardcoded prose is what breaks. An `alerting-v1-system` pair is planned for the same reason. Meta `description:` fields are the exception, because they do not expand substitutions reliably, so write the name in plain text there and expect to revisit those pages at GA.

**Terminology, and why a term pass is not a search-replace.** These distinctions hold before and after the rename, so they are the safest thing to rely on:

- The **alert** is the lifecycle object an operator triages on the **Alerts** page. Today the V2 name for it is *alert episode*; at GA it becomes *alert*, with the system name carrying the disambiguation instead.
- A **rule event** is one append-only evaluation document in `.rule-events`. A rule event with `type: alert` belongs to an alert; one with `type: signal` does not. **Never call a rule event an alert** — that collision is the reason the rename needs care.
- A **series** groups recurrences over time via `group_hash` and can contain many alerts. It is not a synonym for alert, and snoozing happens per series.
- On any page naming two systems, qualify the object with the system in the same sentence.
- Stored names stay unless engineering migrates them: `episode.id`, `episode.status`, `episode_id`, `episode_status`, and the `alerting.episode*` workflow trigger IDs. Prose says alert while code says `episode.*`, so add the one-line mapping the first time a query uses it.

Because these docs are cumulative, the experimental version keeps its experimental language in tagged sections rather than losing it at GA, and `serverless: experimental` should not survive on a page describing the GA system. Let `docs-applies-to-tagging` set the values — which version carries GA is the part that moves — including the inline ``{applies_to}`stack: ga <version>+` `` role form that per-item availability in tables and lists uses.

Cross-repo links use the `<repo>://` form, as in `detection-rules://index.md`. Reach for it instead of guessing a published URL.

Model pages: `alerting/compare-alerting-systems.md`, the routing page, which you read **before drafting anything about alerting**; `solutions/observability/incident-management/alerting.md` for how a solution documents a layer built on the platform framework; `cases/create-cases.md` for consolidated platform content; and the matching solution case page for a thin extras page.

## Navigation

`explore-analyze/toc.yml`, one inline file with no per-section toc. The three parents are `- file: alerting.md`, `- file: cases.md`, and `- file: workflows.md`, in that order near the end of the file.

Landing pages are siblings of their directories, not `index.md` inside them. The experimental alerting tree nests several levels deep, so place a new page against its actual parent entry in the file rather than by counting indentation.

## Known traps

- **"Alerting" names several separate systems, not one.** {{kib}} alerting (becoming Alerting V1), Observability alerting (built on top of it), the experimental ES|QL system (Alerting V2), Watcher (stack only), and Security detection rules (a separate product area). A request that says "add an alerting doc" names none of them. Start at `compare-alerting-systems.md`, but note that it compares only the platform systems — Observability alerting and Security detection rules are not on it, so the routing page can look complete while omitting the two most likely answers for a solution request.
- **Observability alerting is a layer, not a peer.** It reuses the {{kib}} alerting framework and adds its own rule types and Alerts page. A framework-level change can therefore affect it without any Observability page mentioning it, and an Observability rule type is not a {{kib}} alerting rule type. Check both when a change touches the framework.
- **Alerting V2's production status is version-scoped, and the scoping flips at GA.** Treat "not ready for production" as a statement about specific versions rather than a sentence to keep or delete. [`status.md`](status.md#alerting-v2-ga) has the current rule.
- **Never search-replace "alert episode" to "alert".** Dozens of pages use the term, and the pages that teach the data model need rewriting rather than swapping: the sentence "events that share `episode.id` belong to the same alert" is correct, and a term pass would wreck it. The same applies to the two system-flow diagrams, which have **ALERT EPISODE** baked into the image and need design work, not new alt text. Do not generate replacements.
- **Cases is documented once, with thin solution extras.** Copying core case behavior into a solution page is the single most likely review comment in this area.
- **Watcher is `serverless: unavailable`.** Scope it that way; do not tag it like the rest of the area.
- **Workflows and alerting meet, and the rename makes the seam worse.** V1 *alert triggers* and V2 *alert episode lifecycle triggers* both collapse to "alert triggers" once the object is renamed, so they need a system qualifier to stay distinct. Decide which section owns the page, and load `workflows.md` for the Workflows half.
