# Elastic Workflows

Declarative YAML automations in `explore-analyze/workflows/`: step references, triggers, authoring techniques, use cases, concepts, and the reference set.

The boundary that matters: this area owns **how to author workflows**. A workflow that automates a Security or Observability task is still Workflows content, but documenting the underlying product feature is not — and the reverse trap is worse, so never park product feature content under a Workflows path for convenience. The seam with alerting is real and shared with `alerting-and-cases.md`; read both when drafting triggers.

> Migrated from the standalone `docs-draft-workflow-docs` skill, which held the same area knowledge plus its own copy of the drafting process. This file keeps the facts; the process comes from `SKILL.md`. Verified against `docs-content` and `kibana` on 2026-09-16.
>
> Elastic Workflows docs are the source of truth. **Never reference or link to the deprecated Keep HQ workflow docs.**

## Where content lives

| Path | What belongs here |
|---|---|
| `workflows/steps/` | Step references, 25 pages. Namespace and family pages (`cases.md`, `security.md`, `elasticsearch.md`, `kibana.md`, `ai-steps.md`, `data.md`, `streams.md`, `detection-rules.md`, `entity-store.md`, `alert-triage.md`, `attack-triage.md`, `external-systems-apps.md`) alongside per-construct pages (`foreach.md`, `if.md`, `switch.md`, `while.md`, `parallel.md`, `wait.md`, `loop-break.md`, `loop-continue.md`, `wait-for-input.md`, `wait-for-approval.md`). `action-steps.md`, `flow-control-steps.md`, and `composition.md` are the category hubs |
| `workflows/triggers/` | `manual-triggers.md`, `scheduled-triggers.md`, `alert-triggers.md`, `event-driven-triggers.md` |
| `workflows/authoring-techniques/` | How-tos: `anatomy.md`, `choose-the-right-step.md`, `pass-data-handle-errors.md`, `compose-workflows.md`, `manage-workflows.md`, `monitor-workflows.md`, `human-in-the-loop.md`, `use-yaml-editor.md`, `use-natural-language.md`, `settings.md`, `troubleshooting.md`, `migrate-from-9-3.md` |
| `workflows/reference/` | `cheat-sheet.md`, `step-types.md`, `context-variables.md`, `liquid-filters.md`, `glossary.md` |
| `workflows/use-cases/` | Domain outcome pages, nested by domain — for example `use-cases/security/` |
| `workflows/get-started/` | `setup.md` and `build-your-first-workflow.md` — tutorials |
| `workflows/templates/` | `start-from-a-template.md` |
| `workflows/_snippets/` | Exactly one snippet: `schema-location-legend.md`. Include it on namespace step pages that use a parameter-location column |

Single-file topics, with **no** matching directory: `concepts.md`, `templating.md`, `authorization.md`, `managed-workflows.md`. Adding `concepts/` to hold a new concept page would break the pattern — put concepts in `concepts.md` or argue the case explicitly.

## Source of truth

Workflows lives under `src/platform/`, not `x-pack/`. The old `x-pack/platform/plugins/shared/workflows/` path **no longer exists**, so a search there returns nothing and looks like a missing feature.

| Question | Verify at |
|---|---|
| Step parameters, YAML schema | `src/platform/packages/shared/kbn-workflows/spec/` — `schema.ts`, plus namespace directories `spec/elasticsearch/` and `spec/kibana/` |
| Built-in steps and triggers | `spec/builtin_step_definitions.ts`, `spec/builtin_trigger_definitions.ts` |
| Workflow inputs | `spec/builtin_workflow_input_definitions.ts` |
| Deprecated and renamed steps | `spec/deprecated_step_metadata.ts` — check this before documenting any step as current |
| Schema-valid example YAML | `spec/examples/` — prefer these over the `elastic/workflows` library, which is useful for realistic scenarios but not authoritative on schema |
| UI labels, step menu, YAML editor | `src/platform/plugins/shared/workflows_management/public/`; server-side step discovery in `workflows_management/server/` |
| Execution lifecycle, error handling, step output shape | `src/platform/plugins/shared/workflows_execution_engine/` |
| Product-registered and custom steps | `src/platform/plugins/shared/workflows_extensions/`, with internal guides at `dev_docs/STEPS.md`, `TRIGGERS.md`, and `MANAGED_WORKFLOWS.md` |
| Connector actions behind action steps | `x-pack/platform/plugins/shared/stack_connectors/` |

Search by step type identifier first — `cases.addComment`, `elasticsearch.search`, `foreach` — then read the definition or schema rather than an example that happens to use it.

## Read these first

- `workflows/reference/cheat-sheet.md` — **the authority for gotchas.** Check YAML examples against it before presenting them.
- `workflows/reference/step-types.md` — the full step index, and a required follow-up edit for any new step.
- `workflows/authoring-techniques/anatomy.md` — the canonical markup for version-split tabs. Copy the tab syntax from here; do not invent it.
- `workflows/steps/cases.md` — the model namespace step page: shared conventions, then a step catalog, then per-step sections.

## Local conventions

### YAML examples

Two-space indent, copy-pasteable, descriptive step names (`search_for_alerts`, never `step1`), and explicit data flow between steps via `steps.<name>.output`. Use a `steps:` block for step-focused examples and full workflow YAML only when triggers, inputs, or settings matter.

### Syntax rules that are easy to get wrong

| Rule | Correct | Wrong |
|---|---|---|
| Arrays and objects in Liquid | `"${{ event.alerts }}"` | `"{{ event.alerts }}"` |
| Strings in Liquid | `"{{ inputs.name }}"` | — |
| `data.filter` and `if` conditions | KQL: `item._source.severity : 'critical'` | Liquid `==` comparisons |
| Cases step parameters | snake_case: `case_id`, `comment` | camelCase: `caseId` |
| Namespaced step IDs | lowercase dot notation: `security.setAlertStatus` | PascalCase, unless documenting the legacy step itself |
| Alert status legacy step | `kibana.SetAlertsStatus` — PascalCase is correct here | `kibana.set_alerts_status` |
| AI step identifiers | top-level `connector-id`, `agent-id`, literal kebab-case | nested under `with`, or Liquid-templated |
| JSON serialization | `\| json`, `\| json_parse` | `to_json`, which does not exist |
| `switch.cases` | array of `{ case:, steps: }` objects | a map keyed by case value |
| `workflow.execute` target | `workflow-id` inside `with` | a top-level field |

### Version split on inputs

Stack 9.4 and earlier use a top-level `inputs:`. Stack 9.5+ and serverless nest `inputs` under the `type: manual` trigger. Show both with an `applies-switch` or tabs, using the markup from `anatomy.md`.

### Directives

`applies-switch` or tabs for version splits, `stepper` for UI walkthroughs in authoring-technique pages only, and `:::{include}` from `_snippets/` when a matching snippet exists.

### Namespace step page structure

H1 naming the step family with a shorter `navigation_title`; an intro covering what the `namespace.*` steps do and how they relate to overlapping steps elsewhere; **shared conventions before per-step detail** (parameters under `with`, single versus bulk ID fields, add/remove semantics that preserve existing values, required-field rules); a step catalog with jump links; then per-step sections with a one-sentence purpose, a `Parameter | Location | Type | Required | Description` table, and a YAML example; then Related.

**Document parameter names exactly as implemented and do not normalize them.** Real inconsistencies such as `alert_ids` versus `ids`, or `close_reason` versus `reason`, are facts about the product, not typos to tidy.

### Deprecations and preferred namespaces

New content documents the current replacement. If a deprecated form has to appear, mark it deprecated inline and link to the replacement. When new namespaced steps (`security.*`, `cases.*`) overlap legacy `kibana.*` PascalCase steps, document the namespaced step as the preferred path and add a cross-reference on the older page, mirroring how `kibana.md` points at `cases.*`.

## Navigation

`explore-analyze/toc.yml`, under `- file: workflows.md`. One inline file with no per-section toc, nesting several levels deep for `use-cases/`, so place a new page against its actual parent entry rather than by counting indentation.

A new step or page is never a single-file change. Update these as follow-ups:

- `steps/action-steps.md` — add a category blurb and link when introducing a step family, matching the existing blurb shape
- `reference/step-types.md` — add a row for every new step type
- `reference/cheat-sheet.md` — add rows or update the task-oriented groupings
- overlapping sibling pages — add the preferred-namespace cross-reference
- hub pages summarize and link; remove reference detail that crept into them

## Known traps

- **`to_json` does not exist.** Use `| json` and `| json_parse`. This one reaches drafts constantly because it looks plausible.
- **The Kibana path moved.** `x-pack/platform/plugins/shared/workflows/` is gone; everything is under `src/platform/`. Verifying against the old path silently finds nothing.
- **PascalCase is right exactly once.** `kibana.SetAlertsStatus` keeps its casing as a legacy step. Every new namespaced step is lowercase dot notation. Do not regularize either direction.
- **Keep HQ docs are deprecated.** Never cite or link them, even when they answer the question.
- **`concepts.md` is a file, not a directory.** So are `templating.md`, `authorization.md`, and `managed-workflows.md`. The standalone skill this file replaced recorded `concepts/` as a directory, which was already wrong — check the path rather than trusting a table.
- **Inconsistent parameter names are load-bearing.** Normalizing `alert_ids` to `ids` in a table makes the docs wrong and the example uncopyable.
- **The alerting seam cuts both ways.** Trigger pages here and `workflows-alerting.md` in the alerting docset describe one feature from two sides. The V1 versus V2 trigger naming collision is tracked in `alerting-and-cases.md` — read its GA transition note before drafting trigger content.
