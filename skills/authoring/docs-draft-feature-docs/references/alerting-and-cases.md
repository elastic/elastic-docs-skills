---
area: Alerting and Cases
verified: 2026-10-09
verified_against:
  - docs-content
  - elastic/kibana
status: references/status.md#alerting-v2-ga
---

# Alerting and Cases

Two sections of the `explore-analyze/` docset that share one trait: each documents a **platform** capability that the solutions also surface in their own docs. Almost every mistake in this area is a placement mistake rather than a writing mistake.

The boundary that matters: this area owns the cross-solution behavior. When a capability exists only inside Security or Observability, it belongs to that solution's page instead.

> **Alerting V2, now named Kibana Universal Alerting, is mid-GA-transition.** Its names are final, but its section move, its follow-up pages, and its Stack release each finish on their own schedule. Read [`status.md`](status.md#alerting-v2-ga) and resolve each sub-entry's tracking issue before drafting any alerting page. Paths in this file describe the layout after the section move, elastic/docs-content#8516; `status.md` says what `main` has until it merges. The durable rules that survive all of it are below, in *Conventions* and *Known traps*.
>
> **Workflows is a sibling area file**, `workflows.md`, not a section of this one. The two meet at triggers and at `workflows-alerting.md`, so read both when drafting at that seam.

## What belongs here, and what does not

| The content is | Home |
|---|---|
| Cross-solution alerting or case behavior | Here, under `explore-analyze/alerting/` or `explore-analyze/cases/` |
| A new Observability rule type, or anything SLO | `solutions/observability/incident-management/`. **Observability alerting is its own system**, layered on Kibana Classic Alerting rather than a peer of it, and it owns its own rule-type catalog and Alerts page |
| A Security detection rule or its alerts | `solutions/security/detect-and-alert/`. A fifth system entirely, not a rule type of either platform system |
| What one solution adds to Cases | The solution's own case page, thin, linking to the core. Core case behavior is documented once and nowhere else |
| Creating alerts from Agent Builder | `agent-builder.md` owns that seam from its side |
| Anything about authoring workflows | `workflows.md` |

While `docs-draft-cases-docs` is registered as a specialist, **delegate Cases drafting to it.** The Cases material in this file is a placement aid, not a drafting ruleset — it is here so that an alerting request does not misfile case content.

Check for an alerting- or cases-specific `_snippets/` directory before writing shared prose. The Universal Alerting section has one, `alerting/esql/_snippets/`, holding the system note described in *Conventions*. Elsewhere, at last check, `main` had none beyond the docset-level `explore-analyze/_snippets/`, so shared prose in Classic Alerting and Cases was duplicated rather than included.

## Source of truth

Platform plugins sit under `x-pack/platform/plugins/shared/`. Workflows is the exception and lives under `src/platform/`.

| Question | Verify at |
|---|---|
| Classic Alerting's Rules and Connectors UI labels | `triggers_actions_ui/` — this is the UI for both, so most Classic Alerting label questions end here rather than in the framework plugin |
| Classic Alerting framework, rule execution, rule types | `alerting/` |
| Observability alerting and its rule types | `x-pack/solutions/observability/plugins/observability_alerting/`, plus `apm/`, `infra/`, and `synthetics/` in the same tree, which register their own rule types |
| Kibana Universal Alerting | `alerting_v2/` — **a separate plugin.** Searching `alerting/` for Universal Alerting behavior finds nothing and looks like the feature is absent. The plugin, its settings (`alerting:v2:*`), and its i18n IDs keep the V2 name, so search for that rather than the product name. Most i18n IDs are `xpack.alertingV2.*`, but the workflow triggers use `xpack.alertingVTwo.*` |
| The workflow triggers it emits | `alerting_v2/common/workflows/triggers/`, one file per trigger; `rg "= 'alerting\."` lists the IDs. The constants are named two ways, `RuleCreatedTriggerId` for rule triggers and `ALERT_ACKED_TRIGGER_ID` for alert triggers, so a search for either style alone misses half of them. Workflows' own `builtin_trigger_definitions.ts` does not carry them, which is the seam `workflows.md` describes |
| Connector and action types | `stack_connectors/` for individual connectors, `actions/` for the framework |
| Cases behavior, fields, templates | `cases/` |
| Watcher | The `elastic/elasticsearch` repo, not Kibana |
| In-product links to these pages | `src/platform/packages/shared/kbn-doc-links/src/get_doc_links.ts`, outside the plugins. A moved page keeps these links working only through its redirect, so name them as a Kibana follow-up when a page moves |

## Conventions

The three sections do **not** share one frontmatter shape, so copy from the neighbor rather than from another section. Classic alerting carries `mapped_pages` and is often `products: kibana` alone; Universal Alerting carries no `mapped_pages` because it is new; Cases pages carry all four products, reflecting the consolidation; and `compare-alerting-systems.md` also carries `elasticsearch` and `cloud-hosted`, because Watcher is an Elasticsearch feature.

Use the substitutions: `{{kib}}`, `{{stack-manage-app}}` for Stack Management, `{{rules-ui}}` for Rules, `{{connectors-ui}}` for Connectors, `{{siem-rules-ui}}` for Detection rules (SIEM), `{{alerting-v2-system}}` / `{{alerting-v2-system-cap}}` for Kibana Universal Alerting, and `{{alerting-v1-system}}` / `{{alerting-v1-system-cap}}` for Kibana Classic Alerting once `docset.yml` on `main` defines that pair — check before using it. **Never type either system's name in prose, old or new, even now that the names are final.** Both live in `docset.yml`, so a future rename is an edit to four values rather than to pages. Each `-cap` variant currently holds the same value as its plain one, because the names are proper nouns; use it at the start of a sentence anyway, so a rename to a lowercase name still renders correctly. Two things are exceptions: UI labels, which are quoted exactly as `HEAD` shows them, and `description:` fields, which do not expand substitutions reliably and so spell out the full name in plain text when they need one.

**Inside the Universal Alerting section, each page names its system in the first sentence, and a shared note on the landing pages points to the other system.** The first sentence uses `{{alerting-v2-system}}`, or the `-cap` form at the start of a sentence, and the H1 leaves the name out. The system note lives in the section's `_snippets/` and tells readers where to find the Classic Alerting docs. Only the section landing pages include it, directly under the H1 — at last check Get started, Rules, Alerts, and About action policies — and the overview carries its own fuller version, which also explains that both systems call their object an alert. **Do not add the note to any other page.** It was once on every page and was removed for repeating itself, so a page that is not a section landing page names the system in its first sentence and stops there. The landing-page include is the kind that Step 2 of `SKILL.md` exempts from its boilerplate rule.

**Terminology, and why a term pass is not a search-replace.** These distinctions held before the rename and hold after it, so they are the safest thing to rely on:

- The **alert** is the lifecycle object an operator triages on the **Alerts** page. Stack 9.5 called it an *alert episode*; Serverless and later Stack versions call it an *alert*, the same word Classic Alerting uses for its own object, so the system name now carries the disambiguation. The section says so once, in a sentence scoped to 9.5 in the overview and the glossary, and no other page adds a rename note.
- A **rule event** is one append-only evaluation document in `.rule-events`. A rule event with `type: alert` belongs to an alert; one with `type: signal` does not. **Never call a rule event an alert** — that collision is the reason the rename needs care. The rule form labels the two modes **Detect and respond** and **Collect evidence**, which were **Alert** and **Signal** in 9.5, while the stored `type` values stay `alert` and `signal`.
- A **series** groups recurrences over time via `group_hash` and can contain many alerts. It is not a synonym for alert, and snoozing and unsnoozing happen per series.
- **Both systems call their object an alert,** so on any page naming both, qualify each alert with its system in the same sentence.
- **Stored names were renamed with the object, but not uniformly.** Quote the name `HEAD` uses and never infer one from the pattern. Where prose and code use different words, add the one-line mapping the first time a query uses the field. At last check:

  | Where | 9.5 name | Current name | 9.5 name still works |
  |---|---|---|---|
  | `.rule-events` | `episode.id`, `episode.status`, `episode.status_count` | `alert.id`, `alert.status`, `alert.status_count` | Yes, as aliases |
  | `.alert-actions` and action policy matchers | `episode_id`, `episode_status` | `alert_id`, `alert_status` | No |
  | Workflow trigger IDs | `alerting.episode*`, such as `alerting.episodeAcked` | `alerting.actions.alert*`, such as `alerting.actions.alertAcked` | No |
  | Lifecycle trigger payload | `event.episodeId`, and `episodes` in the workflow payload | `event.alertId`, and `alerts` | No |
  | Action policy grouping mode | `per_episode` | `per_alert` | No |

  Where the 9.5 name still works, ES|QL examples keep it on purpose, because `episode.*` is the only form that runs on every version. Where it does not, the page shows the current name with the 9.5 name beside it, each under its own `applies_to` badge.

Because these docs are cumulative, the lifecycle badges carry maturity, not prose. The version that shipped as experimental stays experimental through its `applies_to` values, and pages do not add sentences about production readiness, scoped or not. `serverless: experimental` should not survive on a page describing the GA system unless the code still declares that capability experimental, so check the registration, as Step 4d says. Let `docs-applies-to-tagging` set the values — which version carries GA is the part that moves — including the inline ``{applies_to}`stack: ga <version>+` `` role form that per-item availability in tables and lists uses.

Cross-repo links use the `<repo>://` form, as in `detection-rules://index.md`. Reach for it instead of guessing a published URL.

Model pages: `alerting/compare-alerting-systems.md`, the routing page, which you read **before drafting anything about alerting**; `solutions/observability/incident-management/alerting.md` for how a solution documents a layer built on the platform framework; `cases/create-cases.md` for consolidated platform content; and the matching solution case page for a thin extras page.

## Navigation

`explore-analyze/toc.yml`, one inline file with no per-section toc. The three parents are `- file: alerting.md`, `- file: cases.md`, and `- file: workflows.md`, in that order near the end of the file.

Landing pages are mostly siblings of their directories, not `index.md` inside them, but check the actual file. The Universal Alerting section lives at `alerting/esql/`, and its entry point, `alerting/esql/system-overview.md`, sits inside that folder. Its children are `get-started.md`, `setup.md`, `manage.md`, `rules.md`, `alerts.md`, and `notifications-actions.md`, each a sibling of its folder where it has one. *About action policies* is the exception: it lives inside `action-policies/` and sits under `notifications-actions.md` in the toc, next to `workflows-alerting.md`. The tree nests several levels deep, so place a new page against its actual parent entry rather than by counting indentation. Classic Alerting's landing page is `alerting/alerts.md`.

## Known traps

- **"Alerting" names several separate systems, not one.** Kibana Classic Alerting, Observability alerting (built on top of it), Kibana Universal Alerting, Watcher (stack only), and Security detection rules (a separate product area). Both platform systems were renamed, so a request can use a former name for either: *{{kib}} alerting*, *Alerting V1*, or the working name *Kibana standard alerting* for Classic, and *Alerting V2*, *the experimental alerting system*, or the working name *Kibana ES|QL alerting* for Universal. A request that says "add an alerting doc" names none of them. Start at `compare-alerting-systems.md`, but note that it compares only the platform systems — Observability alerting and Security detection rules are not on it, so the routing page can look complete while omitting the two most likely answers for a solution request.
- **"ES|QL rule" names three things.** A Universal Alerting rule, which is always ES|QL-based and lives under `alerting/esql/`; a Security ES|QL detection rule; and Classic Alerting's Elasticsearch query rule, which also accepts ES|QL. Qualify on first use, and resolve which one a request means before placing it.
- **Observability alerting is a layer, not a peer.** It reuses the Classic Alerting framework and adds its own rule types and Alerts page. A framework-level change can therefore affect it without any Observability page mentioning it, and an Observability rule type is not a Classic Alerting rule type. Check both when a change touches the framework.
- **Universal Alerting's maturity differs by deployment and version, and the badges carry it.** Do not write a sentence about production readiness, and do not keep one for the experimental version either. The restructure removed them on purpose, and the `applies_to` values that `docs-applies-to-tagging` sets already say it.
- **Never search-replace "alert episode" to "alert".** The 9.5-scoped sentences have to keep *alert episode*, ES|QL examples keep `episode.*` on purpose, and file names and heading IDs such as `triage-alert-episodes.md` and `[alert-episode-lifecycle]` keep *episode* so existing links still resolve. The pages that teach the data model need rewriting rather than swapping: the sentence "events that share `episode.id` belong to the same alert" is still correct, and a term pass would wreck it.
- **A change to Universal Alerting reaches past its section.** The names, the "alert" rename, and the section's links also appear on `alerting.md`, `alerting/compare-alerting-systems.md`, Classic Alerting's `alerting/alerts.md`, the three workflow trigger pages (`workflows/triggers.md`, `triggers/alert-triggers.md`, and `triggers/event-driven-triggers.md`), `query-filter/languages/esql-kibana.md`, Agent Builder's `create-alerts.md`, and Security's `detect-and-alert.md`. When a change touches what the system is called or where its pages live, check those pages too.
- **Cases is documented once, with thin solution extras.** Copying core case behavior into a solution page is the single most likely review comment in this area.
- **Watcher is `serverless: unavailable`.** Scope it that way; do not tag it like the rest of the area.
- **Workflows and alerting meet, and the rename made the seam worse.** Classic Alerting's *alert triggers* and Universal Alerting's alert lifecycle triggers (`alerting.actions.alert*`) are both "alert triggers" now that both systems call their object an alert, so they need a system qualifier to stay distinct. Decide which section owns the page, and load `workflows.md` for the Workflows half.
