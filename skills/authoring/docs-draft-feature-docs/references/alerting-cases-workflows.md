# Alerting, Cases, and Workflows

Three sections of the `explore-analyze/` docset that share one trait: each documents a **platform** capability that the solutions also surface in their own docs. Almost every mistake in this area is a placement mistake rather than a writing mistake.

The boundary that matters: this area owns the cross-solution behavior. When a capability only exists inside Security or Observability, it belongs to that solution's page instead — see *Known traps* for the split, which is precise and already well established in the corpus.

> **Workflows delegates.** `explore-analyze/workflows/` has a dedicated skill, `docs-draft-workflow-docs`, and the registry resolves specialists before area files. Hand Workflows drafting to it. Workflows appears here only for the boundary facts it shares with alerting, and for the source paths, since the specialist and this file must not disagree about those.
>
> Verified against `docs-content` and `kibana` on 2026-09-16. The experimental alerting system is under active development at `experimental 9.5+`, so treat its page list and its `applies_to` values as the fastest-moving facts in this file and re-check them rather than trusting this file alone.

## Where content lives

| Path | What belongs here |
|---|---|
| `explore-analyze/alerting/` | The parent. `compare-alerting-systems.md` and `system-overview.md` route readers between systems and are the first thing to update when availability changes |
| `explore-analyze/alerting/alerts/` | {{kib}} alerting — the GA production system. Rule types, connectors, maintenance windows, troubleshooting |
| `explore-analyze/alerting/experimental-alerting-system/` | The ES\|QL-based experimental system. Deeply nested, with its own `rules/`, `alerts/`, `action-policies/`, `get-started/`, and glossary |
| `explore-analyze/alerting/watcher/` | Watcher. Legacy, stack-only, and unavailable on serverless |
| `explore-analyze/cases/` | The consolidated case documentation for **all** solutions. Core behavior lives here and nowhere else |
| `explore-analyze/workflows/` | Delegate to `docs-draft-workflow-docs` |

Not this area, and the most common misfiling:

| Path | Why it is separate |
|---|---|
| `solutions/observability/incident-management/` | Observability owns its own rule-type catalog — roughly 20 `create-*-rule.md` pages plus SLOs. A new Observability rule type goes here, not in `alerting/alerts/` |
| `solutions/security/detect-and-alert/` | Security detection rules are a fourth system entirely, not a rule type of {{kib}} alerting |
| `solutions/security/investigate/security-cases.md`, `solutions/observability/incident-management/observability-cases.md` | Solution-specific case extras only. See the Cases trap below |

Snippets: `explore-analyze/_snippets/` for the docset, and `explore-analyze/workflows/_snippets/` for Workflows. There is no alerting- or cases-specific snippets directory, so shared prose in those two sections is currently duplicated.

## Source of truth

Platform plugins sit under `x-pack/platform/plugins/shared/`. Workflows is the exception and lives under `src/platform/`, not `x-pack/`.

| Question | Verify at |
|---|---|
| Rules and Connectors UI labels | `x-pack/platform/plugins/shared/triggers_actions_ui/` — this is the UI for both, so most alerting label questions end here rather than in the framework plugin |
| Alerting framework, rule execution, rule types | `x-pack/platform/plugins/shared/alerting/` |
| The experimental system | `x-pack/platform/plugins/shared/alerting_v2/` — **a separate plugin.** Searching `alerting/` for experimental behavior finds nothing and looks like the feature is absent |
| Connector and action types | `x-pack/platform/plugins/shared/stack_connectors/` for individual connectors, `actions/` for the framework |
| Cases behavior, fields, templates | `x-pack/platform/plugins/shared/cases/` |
| Workflows | `src/platform/packages/shared/kbn-workflows`, plus `-library`, `-ui`, `-yaml`, and the `src/platform/plugins/shared/workflows_{management,execution_engine,extensions}` plugins |
| Watcher | The `elastic/elasticsearch` repo, not Kibana |

## Read these first

- `explore-analyze/alerting/compare-alerting-systems.md` — read this **before drafting anything about alerting.** It is the routing page between all four systems, with a use-case table and per-system availability, and it is the fastest way to confirm a request is aimed at the right system.
- `explore-analyze/cases/create-cases.md` — the model for consolidated platform content. Its five `mapped_pages` entries span the old Kibana, Security, Observability, and serverless URLs, which is the fingerprint of a page that absorbed three docsets.
- `solutions/security/investigate/security-cases.md` — the model for a solution extras page. Links to the core, then documents only what Security adds, with inline `{applies_to}` badges per capability.
- `explore-analyze/alerting/experimental-alerting-system/how-it-works.md` — the model for a conceptual page on a preview feature.

## Local conventions

The three sections do **not** share one frontmatter shape, so copy from the neighbor rather than from another section.

- Classic alerting carries `mapped_pages` and is often `products: kibana` alone.
- The experimental system carries **no** `mapped_pages`, because it is new, and uses `applies_to: stack: experimental 9.5+` with `serverless: experimental`.
- Cases pages carry all four products — `kibana`, `security`, `observability`, `cloud-serverless` — reflecting the consolidation.
- `compare-alerting-systems.md` also carries `elasticsearch` and `cloud-hosted`, because Watcher is an Elasticsearch feature.

Use the substitutions: `{{kib}}`, `{{stack-manage-app}}` for Stack Management, `{{rules-ui}}` for Rules, `{{connectors-ui}}` for Connectors, `{{siem-rules-ui}}` for Detection rules (SIEM), and `{{alerting-v2-system}}` / `{{alerting-v2-system-cap}}` for the experimental alerting system. Never type "experimental alerting system" literally — the substitution exists because the name is expected to change.

Per-item availability inside tables and bullet lists uses the inline role form, as in ``{applies_to}`stack: ga 9.4+` ``, rather than a frontmatter-only tag. Let `docs-applies-to-tagging` decide the values.

Cross-repo links use the `<repo>://` form — `detection-rules://index.md` appears in `create-manage-rules.md`. Reach for it instead of guessing a published URL.

## Navigation

`explore-analyze/toc.yml` — one inline file of about 660 lines, with no per-section toc. The three parents are `- file: alerting.md`, `- file: cases.md`, and `- file: workflows.md`, in that order near the end of the file.

Landing pages are siblings of their directories, not `index.md` inside them: `alerting.md` next to `alerting/`, `cases.md` next to `cases/`. The experimental alerting tree nests five and six levels deep, so place a new page against its actual parent entry in the file rather than by counting indentation.

## Known traps

- **There are four alerting systems, not one.** {{kib}} alerting (GA), the experimental ES|QL system (`experimental 9.5+`), Watcher (stack only), and Security detection rules (a separate product area). A request that says "add an alerting doc" names none of them. Route it through `compare-alerting-systems.md` first.
- **The experimental system is explicitly not production-ready.** Its own parent page says so. Never draft it as the default answer to an alerting question, and never let a request for "the new alerting docs" quietly become a rewrite of the GA pages.
- **Cases is documented once, with thin solution extras.** Core behavior goes in `explore-analyze/cases/`. A solution page documents only what that solution adds and links to the core — `observability-cases.md` is 16 lines and almost entirely a pointer. Copying core case behavior into a solution page is the single most likely review comment in this area.
- **Observability rule types are not {{kib}} alerting rule types.** A new SLO or threshold rule belongs in `solutions/observability/incident-management/`, beside the other `create-*-rule.md` pages.
- **Watcher is `serverless: unavailable`.** Scope it that way; do not tag it like the rest of the area.
- **Workflows and alerting now touch.** The experimental system has a `workflows-alerting.md` page and Workflows has security use cases. Drafting at that seam means deciding which section owns it, then delegating the Workflows half to `docs-draft-workflow-docs`.
