---
area: Elastic Workflows
verified: 2026-09-16
verified_against:
  - docs-content
  - elastic/kibana
status: references/status.md#alerting-v2-ga
---

# Elastic Workflows

Declarative YAML automations in `explore-analyze/workflows/`: step references, triggers, authoring techniques, use cases, concepts, and the reference set.

The boundary that matters: this area owns **how to author workflows**. A workflow that automates a Security or Observability task is still Workflows content, but documenting the underlying product feature is not — and the reverse trap is worse, so never park product feature content under a Workflows path for convenience. The seam with alerting is real and shared with `alerting-and-cases.md`; read both when drafting triggers.

> Migrated from the standalone `docs-draft-workflow-docs` skill, which held the same area knowledge plus its own copy of the drafting process. This file keeps the facts; the process comes from `SKILL.md`. Find pages with `search_docs`; this file does not inventory them.
>
> Elastic Workflows docs are the source of truth. **Never reference or link to the deprecated Keep HQ workflow docs**, even when they answer the question.

## What belongs here, and what does not

| The content is | Home |
|---|---|
| A new step | `workflows/steps/`, on the namespace or family page for its prefix. Per-construct pages such as `foreach.md` and `if.md` exist for flow control only |
| A trigger | `workflows/triggers/`. Read `alerting-and-cases.md` first when the trigger is alert-related |
| A how-to for authoring | `workflows/authoring-techniques/` |
| A lookup table — step types, context variables, Liquid filters, the cheat sheet | `workflows/reference/` |
| A domain outcome, end to end | `workflows/use-cases/`, nested by domain |
| A new concept | `concepts.md`, the existing file. So are `templating.md`, `authorization.md`, and `managed-workflows.md` — adding a `concepts/` directory breaks the pattern, so argue the case explicitly |
| How an agent invokes a workflow | `agent-builder.md` owns that seam |

`workflows/_snippets/` holds exactly one snippet, `schema-location-legend.md`. Include it on namespace step pages that use a parameter-location column.

## Source of truth

Workflows lives under `src/platform/`, not `x-pack/`. The old `x-pack/platform/plugins/shared/workflows/` path **no longer exists**, so a search there returns nothing and looks like a missing feature.

| Question | Verify at |
|---|---|
| Step parameters, YAML schema | `src/platform/packages/shared/kbn-workflows/spec/` — `schema.ts`, plus the `spec/elasticsearch/` and `spec/kibana/` namespace directories |
| Built-in steps and triggers | `spec/builtin_step_definitions.ts`, `spec/builtin_trigger_definitions.ts` |
| Workflow inputs | `spec/builtin_workflow_input_definitions.ts` |
| Deprecated and renamed steps | `spec/deprecated_step_metadata.ts` — check this before documenting any step as current |
| Schema-valid example YAML | `spec/examples/`. Prefer these over the `elastic/workflows` library, which is useful for realistic scenarios but not authoritative on schema |
| UI labels, step menu, YAML editor | `src/platform/plugins/shared/workflows_management/public/`; server-side step discovery in the same plugin's `server/` |
| Execution lifecycle, error handling, step output shape | `src/platform/plugins/shared/workflows_execution_engine/` |
| Product-registered and custom steps | `src/platform/plugins/shared/workflows_extensions/`, with internal guides at `dev_docs/STEPS.md`, `TRIGGERS.md`, and `MANAGED_WORKFLOWS.md` |
| Connector actions behind action steps | `x-pack/platform/plugins/shared/stack_connectors/` |

Search by step type identifier first — `cases.addComment`, `elasticsearch.search`, `foreach` — then read the definition or schema rather than an example that happens to use it.

## Conventions

### YAML examples

Two-space indent, copy-pasteable, descriptive step names (`search_for_alerts`, never `step1`), and explicit data flow between steps via `steps.<name>.output`. Use a `steps:` block for step-focused examples, and full workflow YAML only when triggers, inputs, or settings matter.

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

There are two shapes: a top-level `inputs:` in earlier stack versions, and `inputs` nested under the `type: manual` trigger in later stack versions and serverless. Get the cutover version from `schema.ts` rather than from this file or a neighboring page, then show both with an `applies-switch` or tabs, using the markup from `authoring-techniques/anatomy.md` rather than inventing it.

### Namespace step page structure

An H1 naming the step family with a shorter `navigation_title`; an intro covering what the `namespace.*` steps do and how they relate to overlapping steps elsewhere; **shared conventions before per-step detail** (parameters under `with`, single versus bulk ID fields, add/remove semantics that preserve existing values, required-field rules); a step catalog with jump links; then per-step sections with a one-sentence purpose, a `Parameter | Location | Type | Required | Description` table, and a YAML example; then Related.

**Document parameter names exactly as implemented and do not normalize them.** Real inconsistencies such as `alert_ids` versus `ids`, or `close_reason` versus `reason`, are facts about the product, not typos to tidy.

### Deprecations and preferred namespaces

New content documents the current replacement. If a deprecated form has to appear, mark it deprecated inline and link to the replacement. When new namespaced steps (`security.*`, `cases.*`) overlap legacy `kibana.*` PascalCase steps, document the namespaced step as the preferred path and add a cross-reference on the older page.

Model pages: `reference/cheat-sheet.md`, **the authority for gotchas**, which you check YAML examples against before presenting them; and `steps/cases.md` for a namespace step page — shared conventions, then a step catalog, then per-step sections.

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
- **Keep HQ docs are deprecated.** Never cite or link them.
- **`concepts.md` is a file, not a directory.** The standalone skill this file replaced recorded `concepts/` as a directory, which was already wrong — check the path rather than trusting a table.
- **Inconsistent parameter names are deliberate.** Normalizing `alert_ids` to `ids` in a table makes the docs wrong and the example uncopyable.
- **The alerting seam cuts both ways.** Trigger pages here and `workflows-alerting.md` in the alerting docset describe one feature from two sides. The V1 versus V2 trigger naming collision is tracked in `alerting-and-cases.md` — read its GA transition note before drafting trigger content.
- **This area spans two repos more often than most.** A settings change gating a workflows feature, or a new connector usable as an action step, lands in `elastic/kibana` rather than here — see `kibana-settings-reference.md` and Step 4e for the split and the merge order. Authoring content stays in docs-content.
