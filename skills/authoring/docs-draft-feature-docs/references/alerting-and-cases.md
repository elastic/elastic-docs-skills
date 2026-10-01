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

> **Alerting V2 is mid-GA-transition: its section is moving, its names are being confirmed, and its core object is being renamed, each on its own schedule.** Read [`status.md`](status.md#alerting-v2-ga) and resolve each sub-entry's tracking issue before drafting any alerting page. Paths and names in this file describe `main` at last check. The durable rules that survive all of it are below, in *Conventions* and *Known traps*.
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

Check for an alerting- or cases-specific `_snippets/` directory before writing shared prose. At last check `main` had none beyond the docset-level `explore-analyze/_snippets/`, so shared prose in these two sections was duplicated rather than included. The restructure in `status.md` adds one to the Alerting V2 section, holding the system note described in *Conventions*.

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

Use the substitutions: `{{kib}}`, `{{stack-manage-app}}` for Stack Management, `{{rules-ui}}` for Rules, `{{connectors-ui}}` for Connectors, `{{siem-rules-ui}}` for Detection rules (SIEM), `{{alerting-v2-system}}` / `{{alerting-v2-system-cap}}` for Alerting V2, and `{{alerting-v1-system}}` / `{{alerting-v1-system-cap}}` for {{kib}} alerting once `docset.yml` defines that pair — check before using it. Never type either system's name in prose, old or new: both names live in `docset.yml`, so hardcoded prose is what breaks when they change. UI labels are the exception and are quoted exactly as `HEAD` shows them. [`status.md`](status.md#alerting-v2-ga) has the working names.

**Inside the Alerting V2 section, a shared note names the system so page openings do not have to.** Check the section's `_snippets/` for the system note. Where it exists, every page in the section opens with an include of it directly under the H1, and the H1, the `description:`, and the first sentence leave the system name out. The section's landing page is the exception, because it introduces the system by name. This is the kind of include that Step 2 of `SKILL.md` exempts from its boilerplate rule. Outside the section, a `description:` that has to name a system writes the name in plain text, because descriptions do not expand substitutions reliably.

**Terminology, and why a term pass is not a search-replace.** These distinctions hold before and after the rename, so they are the safest thing to rely on:

- The **alert** is the lifecycle object an operator triages on the **Alerts** page. The V2 name for it is *alert episode*, which is being renamed to *alert*, with the system name carrying the disambiguation instead. The docs switch when the product does, not before, and [`status.md`](status.md#alerting-v2-ga) tracks the rename.
- A **rule event** is one append-only evaluation document in `.rule-events`. A rule event with `type: alert` belongs to an alert; one with `type: signal` does not. **Never call a rule event an alert** — that collision is the reason the rename needs care.
- A **series** groups recurrences over time via `group_hash` and can contain many alerts. It is not a synonym for alert, and snoozing happens per series.
- On any page naming two systems, qualify the object with the system in the same sentence.
- Stored names change only when engineering migrates them, and several migrations are in flight. Quote the field or trigger ID that `HEAD` actually uses, such as `episode.id` or an `alerting.episode*` trigger, and never infer a renamed one from the pattern. Where prose and code use different words, add the one-line mapping the first time a query uses the field.

Because these docs are cumulative, the lifecycle badges carry maturity, not prose. The version that shipped as experimental stays experimental through its `applies_to` values, and pages do not add sentences about production readiness, scoped or not. `serverless: experimental` should not survive on a page describing the GA system unless the code still declares that capability experimental, so check the registration, as Step 4d says. Let `docs-applies-to-tagging` set the values — which version carries GA is the part that moves — including the inline ``{applies_to}`stack: ga <version>+` `` role form that per-item availability in tables and lists uses.

Cross-repo links use the `<repo>://` form, as in `detection-rules://index.md`. Reach for it instead of guessing a published URL.

Model pages: `alerting/compare-alerting-systems.md`, the routing page, which you read **before drafting anything about alerting**; `solutions/observability/incident-management/alerting.md` for how a solution documents a layer built on the platform framework; `cases/create-cases.md` for consolidated platform content; and the matching solution case page for a thin extras page.

## Navigation

`explore-analyze/toc.yml`, one inline file with no per-section toc. The three parents are `- file: alerting.md`, `- file: cases.md`, and `- file: workflows.md`, in that order near the end of the file.

Landing pages are mostly siblings of their directories, not `index.md` inside them, but check the actual file: the restructure in `status.md` moves the Alerting V2 landing page, `system-overview.md`, inside its folder. That tree nests several levels deep and is being regrouped, so resolve its current path and place a new page against its actual parent entry rather than by counting indentation.

## Known traps

- **"Alerting" names several separate systems, not one.** {{kib}} alerting (Alerting V1), Observability alerting (built on top of it), the ES|QL-based system (Alerting V2), Watcher (stack only), and Security detection rules (a separate product area). Both platform systems are being renamed, so a request can use the old or the new name for either. A request that says "add an alerting doc" names none of them. Start at `compare-alerting-systems.md`, but note that it compares only the platform systems — Observability alerting and Security detection rules are not on it, so the routing page can look complete while omitting the two most likely answers for a solution request.
- **Observability alerting is a layer, not a peer.** It reuses the {{kib}} alerting framework and adds its own rule types and Alerts page. A framework-level change can therefore affect it without any Observability page mentioning it, and an Observability rule type is not a {{kib}} alerting rule type. Check both when a change touches the framework.
- **Alerting V2's maturity differs by deployment and version, and the badges carry it.** Do not write a sentence about production readiness, and do not keep one for the experimental version either. The restructure removed them on purpose, and the `applies_to` values that `docs-applies-to-tagging` sets already say it.
- **Never search-replace "alert episode" to "alert".** Dozens of pages use the term, and the pages that teach the data model need rewriting rather than swapping: the sentence "events that share `episode.id` belong to the same alert" is correct, and a term pass would wreck it.
- **Cases is documented once, with thin solution extras.** Copying core case behavior into a solution page is the single most likely review comment in this area.
- **Watcher is `serverless: unavailable`.** Scope it that way; do not tag it like the rest of the area.
- **Workflows and alerting meet, and the rename makes the seam worse.** V1 *alert triggers* and V2 *alert episode lifecycle triggers* both collapse to "alert triggers" once the object is renamed, so they need a system qualifier to stay distinct. Decide which section owns the page, and load `workflows.md` for the Workflows half.
