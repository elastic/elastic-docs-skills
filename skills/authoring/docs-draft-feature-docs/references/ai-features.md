# AI-powered features

The AI features hub, the AI assistants, LLM connector guides, Automatic Import, and access management. Everything under `explore-analyze/ai-features/` except Agent Builder, which has its own file.

**Placement is the main risk in this area, and it is a three-way decision rather than the usual two.** Nearly every AI feature has a platform home plus up to two solution-specific homes, and the assistants are owned by three different engineering teams in three different plugin trees.

> Verified against docs-content and `elastic/kibana` on 2026-09-16. Pairs with `agent-builder.md`; load both if a request spans them. Find pages with `search_docs`; this file does not inventory them.

## What belongs here, and what does not

| The content is | Home |
|---|---|
| How a capability works, generically | The platform tree under `ai-features/` |
| A solution's own AI feature — Attack Discovery, EASE, Streams AI | The solution tree. These have no platform home, so do not add one for symmetry |
| A shared assistant behaving differently in one solution | The solution page, thin, linking back to the platform page |
| A tested-model list | The solution's performance matrix. There is no consolidated platform matrix, and the hub page says so |
| An LLM provider setup guide | `ai-features/llm-guides/`, even when one solution requested it |

Automatic Import is the pattern to copy: a platform page carrying the mechanics, plus a thin Observability page for the Observability framing. Add to the platform page by default.

Not this area: Agent Builder (`agent-builder.md`), Elastic Inference and NLP models, and vector or semantic search. The hub page links all of them, which does not make them yours to edit.

## Source of truth

| Question | Verify at |
|---|---|
| Observability AI Assistant | `x-pack/platform/plugins/shared/observability_ai_assistant` |
| Security AI Assistant | `x-pack/solutions/security/plugins/elastic_assistant` |
| Search Assistant | `x-pack/solutions/search/plugins/search_assistant` |
| Automatic Import | `x-pack/platform/plugins/shared/automatic_import` |
| Connector configuration and supported providers | `x-pack/platform/plugins/shared/stack_connectors` |

The three assistants live in three different plugin trees, one under `platform/` and two under `solutions/`. **Do not assume a behavior is shared across assistants** — verify per assistant, because a change to one is routinely not a change to the others. There is no `ai_assistant_management_selection` plugin, and Automatic Import was formerly the integration assistant, so `integration_assistant` no longer exists as a plugin path.

## Conventions

`{{obs-ai-assistant}}` renders "Elastic AI Assistant for Observability and Search" and `{{agent-builder}}` renders "Elastic Agent Builder", both defined in `docset.yml`. **There is no substitution for the Security AI Assistant**, so it is written out literally as "Elastic AI Assistant for Security". Do not invent one.

The Observability assistant covers Search as well, which its substitution reflects. Do not describe it as Observability-only.

Nearly every feature here needs an LLM connector, and pages state that in a requirements section rather than re-explaining connector setup. Link to `llm-guides/llm-connectors.md` instead.

The two performance matrices are named differently for the same concept — Observability's `llm-performance-matrix.md` and Security's `large-language-model-performance-matrix.md`. Link the right one and do not rename either as a drive-by.

Provider page filenames are `connect-to-<provider>.md` and are not reliably kebab-cased, because `connect-to-vLLM.md` preserves the product's own casing. Follow the existing file when editing, and match the product name when adding one.

Model pages: `explore-analyze/ai-features.md` for how thin a hub entry should be, and `llm-guides/llm-connectors.md` for what belongs on a connector page rather than a provider page. Read `ai-chat-experiences/ai-agent-or-ai-assistant.md` before writing either word.

## Navigation

Inline in `explore-analyze/toc.yml` under `ai-features.md`, with `llm-guides/llm-connectors.md` parenting the provider pages and `local-llms-overview.md` parenting the LM Studio pages.

Some pages are `hidden:` rather than absent, including `context-engine.md` and two Agent Builder pages. A page missing from the rendered nav may be deliberately unpublished, so check for a `hidden:` entry before treating it as an oversight, and ask before promoting one to `file:`.

## Known traps

- **The hub page is a deliberately generic catalog.** Its job is to say what exists and link out. The instinct on any new AI feature is to add a section there, which over time turns it into a second copy of the docs. Add a short entry pointing at the real page, and put the detail on the real page.
- **Do not assume the three assistants behave alike.** Separate plugins, separate teams, separate trees. A verified claim about one is an unverified claim about the others.
- **A solution-specific page is not licence to duplicate.** Solution pages carry the solution-specific delta and link back.
- **Seams that belong to other areas.** Security AI content meets `elastic-security.md`, creating alerts from Agent Builder meets `alerting-and-cases.md`, and Attack Discovery's workflow page meets `workflows.md`. Load the other file rather than guessing.
- **Names to keep straight.** Agent Builder, agent skills for coding agents, and the AI assistants are three different things whose names all collide. `ai-chat-experiences/ai-agent-or-ai-assistant.md` exists because readers confuse them.
