# Alerting and Cases

Two sections of the `explore-analyze/` docset that share one trait: each documents a **platform** capability that the solutions also surface in their own docs. Almost every mistake in this area is a placement mistake rather than a writing mistake.

The boundary that matters: this area owns the cross-solution behavior. When a capability only exists inside Security or Observability, it belongs to that solution's page instead — see *Known traps* for the split, which is precise and already well established in the corpus.

> **Workflows is a sibling area file**, `workflows.md`, not a section of this one. The two meet at triggers and at `workflows-alerting.md`, so read both when drafting at that seam.
>
> **Alerting V2 is going GA, and this is the most volatile area in the catalog.** Verified against `docs-content` and `kibana` on 2026-09-16. Stack GA targets 9.6 on 2026-10-27, which the team considers more or less confirmed. Serverless GA lands first and its date is genuinely unsettled — the writer's current target is 2026-09-22 while [#920](https://github.com/elastic/docs-content-internal/issues/920) still says the week of the 9.6 release. **Treat both dates as unconfirmed and check the issues, not this file.** The work is tracked in [#920](https://github.com/elastic/docs-content-internal/issues/920), [#1652](https://github.com/elastic/docs-content-internal/issues/1652), and [#1738](https://github.com/elastic/docs-content-internal/issues/1738).
>
> The rename is **not yet safe to draft against.** Final system names, capitalization, and which UI strings still say Episode are blocked on scope finalization around 2026-10-06 ([#1758](https://github.com/elastic/docs-content-internal/issues/1758)). Until those are frozen, keep current 9.5 experimental language or mark new behavior as planned, and do not invent the new labels. The durable rules that survive the transition are in *Local conventions*; the dates above are the part of this file that goes stale first.

## Where content lives

| Path | What belongs here |
|---|---|
| `explore-analyze/alerting/` | The parent. `compare-alerting-systems.md` and `system-overview.md` route readers between systems and are the first thing to update when availability changes |
| `explore-analyze/alerting/alerts/` | {{kib}} alerting — the GA production system. Rule types, connectors, maintenance windows, troubleshooting |
| `explore-analyze/alerting/experimental-alerting-system/` | The ES\|QL-based experimental system. Deeply nested, with its own `rules/`, `alerts/`, `action-policies/`, `get-started/`, and glossary |
| `explore-analyze/alerting/watcher/` | Watcher. Legacy, stack-only, and unavailable on serverless |
| `explore-analyze/cases/` | The consolidated case documentation for **all** solutions. Core behavior lives here and nowhere else |
| `explore-analyze/workflows/` | Covered by the `workflows.md` area file |

Not this area, and the most common misfiling:

| Path | Why it is separate |
|---|---|
| `solutions/observability/incident-management/` | **Observability alerting is its own system, layered on {{kib}} alerting GA rather than a peer of it.** Observability owns the rule-type catalog — roughly 20 `create-*-rule.md` pages plus SLOs — and its own Alerts page, which aggregates Observability, {{ml}} anomaly detection, and {{stack-manage-app}} rules. A new Observability rule type goes here, not in `alerting/alerts/` |
| `solutions/security/detect-and-alert/` | Security detection rules are a fourth system entirely, not a rule type of {{kib}} alerting |
| `solutions/security/investigate/security-cases.md`, `solutions/observability/incident-management/observability-cases.md` | Solution-specific case extras only. See the Cases trap below |

Snippets: `explore-analyze/_snippets/` for the docset, and `explore-analyze/workflows/_snippets/` for Workflows. There is no alerting- or cases-specific snippets directory, so shared prose in those two sections is currently duplicated.

## Source of truth

Platform plugins sit under `x-pack/platform/plugins/shared/`. Workflows is the exception and lives under `src/platform/`, not `x-pack/`.

| Question | Verify at |
|---|---|
| Rules and Connectors UI labels | `x-pack/platform/plugins/shared/triggers_actions_ui/` — this is the UI for both, so most alerting label questions end here rather than in the framework plugin |
| Alerting framework, rule execution, rule types | `x-pack/platform/plugins/shared/alerting/` |
| Observability alerting and its rule types | `x-pack/solutions/observability/plugins/observability_alerting/`, plus `apm/`, `infra/`, and `synthetics/` in the same tree, which register their own rule types |
| The experimental system | `x-pack/platform/plugins/shared/alerting_v2/` — **a separate plugin.** Searching `alerting/` for experimental behavior finds nothing and looks like the feature is absent |
| Connector and action types | `x-pack/platform/plugins/shared/stack_connectors/` for individual connectors, `actions/` for the framework |
| Cases behavior, fields, templates | `x-pack/platform/plugins/shared/cases/` |
| Workflows | `src/platform/packages/shared/kbn-workflows`, plus `-library`, `-ui`, `-yaml`, and the `src/platform/plugins/shared/workflows_{management,execution_engine,extensions}` plugins |
| Watcher | The `elastic/elasticsearch` repo, not Kibana |

## Read these first

- `explore-analyze/alerting/compare-alerting-systems.md` — read this **before drafting anything about alerting.** It is the routing page, with a use-case table and per-system availability. Note that it deliberately compares only the three platform systems and carries a note pointing at Security detection rules; it does not cover Observability alerting at all. So it is the right starting point and not a complete map — see *Known traps*.
- `solutions/observability/incident-management/alerting.md` — the Observability system's overview, and the model for how a solution documents a layer built on the platform framework. Its Alerts page section shows the aggregation across rule types with inline `{applies_to}` badges.
- `explore-analyze/cases/create-cases.md` — the model for consolidated platform content. Its five `mapped_pages` entries span the old Kibana, Security, Observability, and serverless URLs, which is the fingerprint of a page that absorbed three docsets.
- `solutions/security/investigate/security-cases.md` — the model for a solution extras page. Links to the core, then documents only what Security adds, with inline `{applies_to}` badges per capability.
- `explore-analyze/alerting/experimental-alerting-system/how-it-works.md` — the model for a conceptual page on a preview feature.

## Local conventions

The three sections do **not** share one frontmatter shape, so copy from the neighbor rather than from another section.

- Classic alerting carries `mapped_pages` and is often `products: kibana` alone.
- The experimental system carries **no** `mapped_pages`, because it is new, and uses `applies_to: stack: experimental 9.5+` with `serverless: experimental`.
- Cases pages carry all four products — `kibana`, `security`, `observability`, `cloud-serverless` — reflecting the consolidation.
- `compare-alerting-systems.md` also carries `elasticsearch` and `cloud-hosted`, because Watcher is an Elasticsearch feature.

Use the substitutions: `{{kib}}`, `{{stack-manage-app}}` for Stack Management, `{{rules-ui}}` for Rules, `{{connectors-ui}}` for Connectors, `{{siem-rules-ui}}` for Detection rules (SIEM), and `{{alerting-v2-system}}` / `{{alerting-v2-system-cap}}` for the experimental alerting system. Never type "experimental alerting system" literally — the substitution will be repointed to the GA name, so hardcoded prose is what breaks. An `alerting-v1-system` pair is planned for the same reason. Meta `description:` fields are the exception: they do not expand substitutions reliably, so write the name in plain text there and expect to revisit those pages at GA.

**Terminology, and why a term pass is not a search-replace.** These distinctions hold before and after the rename, so they are the safest thing to rely on:

- The **alert** is the lifecycle object an operator triages on the **Alerts** page. Today the V2 name for it is *alert episode*; at GA it becomes *alert*, with the system name carrying the disambiguation instead.
- A **rule event** is one append-only evaluation document in `.rule-events`. A rule event with `type: alert` belongs to an alert; one with `type: signal` does not. **Never call a rule event an alert** — that collision is the reason the rename needs care.
- A **series** groups recurrences over time via `group_hash` and can contain many alerts. It is not a synonym for alert, and snoozing happens per series.
- On any page naming two systems, qualify the object with the system in the same sentence.
- Stored names stay unless engineering migrates them: `episode.id`, `episode.status`, `episode_id`, `episode_status`, and the `alerting.episode*` workflow trigger IDs. Prose says alert while code says `episode.*`, so add the one-line mapping the first time a query uses it.

At GA the target tags are `stack: experimental 9.5, ga 9.6` with `serverless: ga`. Because these docs are cumulative, 9.5 keeps its experimental language in tagged sections rather than losing it, and `serverless: experimental` should not survive on a page describing the GA system. Let `docs-applies-to-tagging` set the values.

Per-item availability inside tables and bullet lists uses the inline role form, as in ``{applies_to}`stack: ga 9.4+` ``, rather than a frontmatter-only tag. Let `docs-applies-to-tagging` decide the values.

Cross-repo links use the `<repo>://` form — `detection-rules://index.md` appears in `create-manage-rules.md`. Reach for it instead of guessing a published URL.

## Navigation

`explore-analyze/toc.yml` — one inline file of about 660 lines, with no per-section toc. The three parents are `- file: alerting.md`, `- file: cases.md`, and `- file: workflows.md`, in that order near the end of the file.

Landing pages are siblings of their directories, not `index.md` inside them: `alerting.md` next to `alerting/`, `cases.md` next to `cases/`. The experimental alerting tree nests five and six levels deep, so place a new page against its actual parent entry in the file rather than by counting indentation.

## Known traps

- **There are five alerting systems, not one.** {{kib}} alerting (GA, becoming Alerting V1), Observability alerting (built on top of {{kib}} alerting GA, documented in `solutions/observability/incident-management/`), the experimental ES|QL system (Alerting V2, going GA), Watcher (stack only), and Security detection rules (a separate product area). A request that says "add an alerting doc" names none of them. Start at `compare-alerting-systems.md`, but remember it only compares the three platform systems — Observability alerting and Security detection rules are not on it, so the routing page can look complete while omitting the two most likely answers for a solution request.
- **Observability alerting is a layer, not a peer.** It reuses the {{kib}} alerting framework and adds its own rule types and Alerts page. That means a framework-level change can affect it without any Observability page mentioning it, and an Observability rule type is not a {{kib}} alerting rule type. Check both when a change touches the framework.
- **Alerting V2's production status is version-dependent, and about to flip.** Today its pages say it is not ready for production. At GA that becomes false for serverless and 9.6 while staying true for 9.5, so it is a scoping problem rather than a sentence to delete. Until the names are frozen, do not draft the GA wording as fact; until GA ships, do not present V2 as the default answer to an alerting question.
- **Never search-replace "alert episode" to "alert".** Roughly 50 pages use the term and the pages that teach the data model need rewriting rather than swapping — the sentence "events that share `episode.id` belong to the same alert" is correct and a term pass would wreck it. The same applies to the two system-flow diagrams, which have **ALERT EPISODE** baked into the image and need design work, not new alt text. Do not generate replacements.
- **Cases is documented once, with thin solution extras.** Core behavior goes in `explore-analyze/cases/`. A solution page documents only what that solution adds and links to the core — `observability-cases.md` is 16 lines and almost entirely a pointer. Copying core case behavior into a solution page is the single most likely review comment in this area.
- **Watcher is `serverless: unavailable`.** Scope it that way; do not tag it like the rest of the area.
- **Workflows and alerting meet, and the rename makes the seam worse.** The experimental system has a `workflows-alerting.md` page, and Workflows has its own trigger docs under `workflows/triggers/`. V1 *alert triggers* and V2 *alert episode lifecycle triggers* both collapse to "alert triggers" once the object is renamed, so they need a system qualifier to stay distinct. Decide which section owns the page, and load `workflows.md` for the Workflows half.
