# AI-powered features

The AI features hub, the AI assistants, LLM connector guides, Automatic Import, and access management. Everything under `explore-analyze/ai-features/` except Agent Builder, which has its own file.

**Placement is the main risk in this area, and it is a three-way decision rather than the usual two.** Nearly every AI feature has a platform home plus up to two solution-specific homes, and the assistants are owned by three different engineering teams in three different plugin trees.

> Verified against docs-content and `elastic/kibana` on 2026-09-16. Pairs with `agent-builder.md` — load both if a request spans them.

## Where content lives

| Path | What belongs here |
|---|---|
| `explore-analyze/ai-features.md` | The hub. A catalog of what exists, grouped by platform and then by solution, linking out. 178 lines |
| `ai-features/ai-chat-experiences.md` and `ai-chat-experiences/` | How the chat surfaces relate: `ai-agent-or-ai-assistant.md`, `ai-assistant.md`, `ai-assistant-host-doc-artifacts.md` |
| `ai-features/llm-guides/` | `llm-connectors.md` plus one `connect-to-*.md` per provider, and `local-llms-overview.md` for local models |
| `ai-features/automatic-import.md` | The platform home for Automatic Import |
| `ai-features/manage-access-to-ai-assistant.md` | Enabling and disabling AI features in a deployment |
| `ai-features/agent-skills.md` | The AI agent skills packages for coding agents |
| `ai-features/context-engine.md` | Present but `hidden:` in nav — see Navigation |
| `solutions/observability/ai/` | Observability's AI assistant, its LLM performance matrix, and its Automatic Import page |
| `solutions/security/ai/` | 30 files: AI assistant, knowledge base, Attack Discovery, EASE, use cases, performance matrix |

Not this area: Agent Builder (`agent-builder.md`), Elastic Inference and NLP models (`explore-analyze/elastic-inference/` and `machine-learning/`), and vector or semantic search (`solutions/search/`). The hub page links all of them, which does not make them yours to edit.

### Placement: platform or solution

| The content is | Home |
|---|---|
| How a capability works, generically | The platform tree under `ai-features/` |
| A solution's own AI feature — Attack Discovery, EASE, Streams AI | The solution tree. These have no platform home |
| A shared assistant behaving differently in one solution | The solution page, thin, linking back to the platform page |
| A tested-model list | The solution's performance matrix. There is no consolidated platform matrix, and the hub page says so explicitly |
| An LLM provider setup guide | `llm-guides/`, even when one solution requested it |

Automatic Import is the pattern to copy: a platform page at `ai-features/automatic-import.md` carrying the mechanics, plus a thin `solutions/observability/ai/automatic-import.md` for the Observability framing. Add to the platform page by default.

## Source of truth

| Question | Verify at |
|---|---|
| Observability AI Assistant | `x-pack/platform/plugins/shared/observability_ai_assistant` |
| Security AI Assistant | `x-pack/solutions/security/plugins/elastic_assistant` |
| Search Assistant | `x-pack/solutions/search/plugins/search_assistant` |
| Automatic Import | `x-pack/platform/plugins/shared/automatic_import` |
| Connector configuration and supported providers | `x-pack/platform/plugins/shared/stack_connectors` |

The three assistants live in three different plugin trees, one of them under `platform/` and two under `solutions/`. **Do not assume a behavior is shared across assistants** — verify per assistant, because a change to one is routinely not a change to the others. There is no `ai_assistant_management_selection` plugin; check the current tree if a request names one.

Automatic Import was formerly the integration assistant, and `integration_assistant` no longer exists as a plugin path.

## Read these first

- `explore-analyze/ai-features.md` — the hub, and the thing most requests will want to change. Read it to see how thin each entry is.
- `explore-analyze/ai-features/llm-guides/llm-connectors.md` — 68 lines, the model for connector guidance and what belongs on a provider page instead.
- `explore-analyze/ai-features/ai-chat-experiences/ai-agent-or-ai-assistant.md` — settles the agent-versus-assistant distinction. Read before writing either word.

## Local conventions

`{{obs-ai-assistant}}` renders "Elastic AI Assistant for Observability and Search" at `docset.yml:372`, and `{{agent-builder}}` renders "Elastic Agent Builder" at line 387. **There is no substitution for the Security AI Assistant**, so it is written out literally as "Elastic AI Assistant for Security". Do not invent one.

The Observability assistant covers Search as well, which its substitution reflects — do not describe it as Observability-only.

Nearly every feature here needs an LLM connector, and pages state that in a requirements section rather than re-explaining connector setup. Link to `llm-guides/llm-connectors.md` instead.

The two performance matrices are named differently for the same concept: `solutions/observability/ai/llm-performance-matrix.md` and `solutions/security/ai/large-language-model-performance-matrix.md`. Link the right one and do not rename either as a drive-by.

Provider page filenames are `connect-to-<provider>.md` and are not reliably kebab-cased — `connect-to-vLLM.md` preserves the product's own casing. Follow the existing file when editing; match the product name when adding one.

## Navigation

Inline in `explore-analyze/toc.yml` under `ai-features.md`, with `llm-guides/llm-connectors.md` as the parent of the provider pages and `local-llms-overview.md` parenting the LM Studio pages.

`context-engine.md` is `hidden:` rather than absent, as are two Agent Builder pages, for six hidden entries across the docset. A page missing from the rendered nav may be deliberately unpublished — check for a `hidden:` entry before treating it as an oversight, and ask before promoting one to `file:`.

## Known traps

- **The hub page is a deliberately generic catalog.** Its job is to say what exists and link out. The instinct on any new AI feature is to add a section there, which over time turns it into a second copy of the docs. Add a short entry pointing at the real page, and put the detail on the real page.
- **Do not assume the three assistants behave alike.** Separate plugins, separate teams, separate trees. A verified claim about one is an unverified claim about the others.
- **A solution-specific page is not licence to duplicate.** Solution pages carry the solution-specific delta and link back. `solutions/observability/ai/automatic-import.md` next to the platform page is the shape to copy.
- **Some features are solution-only and have no platform home.** Attack Discovery, EASE, and Streams AI belong in their solution trees. Do not add them to `ai-features/` for symmetry.
- **Seams that belong to other areas.** Security AI content meets `elastic-security.md`, `agent-builder/create-alerts.md` meets `alerting-and-cases.md`, and Attack Discovery's workflow page meets `workflows.md`. Load the other file rather than guessing.
- **Names to keep straight.** Agent Builder, agent skills for coding agents, and the AI assistants are three different things whose names all collide. `ai-chat-experiences/ai-agent-or-ai-assistant.md` exists because readers confuse them, so check it before choosing a word.
