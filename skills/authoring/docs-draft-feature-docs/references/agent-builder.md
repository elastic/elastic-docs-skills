---
area: Elastic Agent Builder
verified: 2026-09-16
verified_against:
  - docs-content
  - elastic/kibana
---

# Elastic Agent Builder

The AI agent platform: agents, skills, tools, MCP and A2A servers, and programmatic access. Split from `ai-features.md`, which owns the hub page, the AI assistants, LLM connector guides, and Automatic Import. If a request touches both, load both.

> This area went preview and then GA quickly and is still moving, so get availability from the plugin config rather than from a neighboring page's `applies_to`. Find pages with `search_docs`; this file does not inventory them.

## What belongs here, and what does not

The default is the platform tree, and the bar for a solution page is high. Ask what the content is actually about.

| The content is | Home |
|---|---|
| How the capability works | The platform tree, always. A Security-flavored example does not make it Security content |
| A solution-specific integration point | The solution tree, kept thin and linking back. Security carries a handful of pages against the platform side's dozens, which is the ratio to aim for |
| A solution feature that happens to use Agent Builder | The feature's own home. Attack Discovery's Agent Builder page sits with Attack Discovery, not here |
| A new built-in agent, skill, or tool | A row on the matching `-reference` page, not a new page |

Do not mirror a platform page into a solution tree to make it easier to find. That is what navigation and links are for, and duplicated AI content drifts fast.

API content composes from `_snippets/api-tutorial/`, one snippet per request. A change to a request body is a snippet edit, and the snippet may appear on more than one page, so grep for its filename before editing.

## Source of truth

| Question | Verify at |
|---|---|
| Agent, skill, and tool behavior; API shapes | `x-pack/platform/plugins/shared/agent_builder` in `elastic/kibana` |
| Navigation entries and deep links | `src/platform/packages/shared/deeplinks/agent_builder` |
| Built-in agents, skills, and tools | The plugin's registrations. The `-reference` pages are hand-maintained and go stale, so the registration list is the truth |
| Connector and model support | `x-pack/platform/plugins/shared/stack_connectors`, plus the tested-model list on `models.md` |
| Availability by version and project type | The plugin config and feature flags, not the current `applies_to` on a neighboring page |

There is no `onechat` plugin. If a request or an older page refers to one, the code moved to `agent_builder`.

## Conventions

`{{agent-builder}}` renders "Elastic Agent Builder" and is defined in `docset.yml`. Use it rather than typing the product name. There is no substitution for the Security AI Assistant, so that name is written out literally.

Agent, skill, and tool are distinct concepts with a glossary entry each, and the hierarchy between them matters: a tool performs a discrete operation, while a skill bundles instructions, tools, and context and teaches the agent *how* and *when* to use them. Skills sit one level above tools. A skill is not "a thing the agent can do", and the two words are not interchangeable. Read `agent-builder/glossary.md` before introducing a fourth noun, and `agent-builder/skills.md` when the answer matters, since the glossary only summarizes it.

`glossary.md` has its own format, and entries there are not ordinary prose: an explicit `$$$anchor$$$` on the line above the term, inline `{applies_to}` roles on the term line itself, a definition-list body indented with `:`, and cross-references in the empty-link-text `See [](skills.md#how-skills-are-invoked)` form. Copy the shape of a neighboring entry. Per-entry `applies_to` matters here because the concepts landed in different versions.

Model pages: `explore-analyze/ai-features/elastic-agent-builder.md` for how the area introduces itself and routes to Get started, and `agent-builder/tools/esql-tools.md` for a capability page with worked examples.

Let `docs-applies-to-tagging` set `applies_to`. Most pages here went preview and then GA, so cumulative-docs rules apply.

## Navigation

Inline in `explore-analyze/toc.yml`, under `ai-features.md` → `ai-features/elastic-agent-builder.md`, nesting several levels deep in places. The parent entry is the landing page, so a new page goes in that subtree rather than at the `ai-features.md` level.

**Some pages are deliberately `hidden:` rather than absent**, including two under `agent-builder/`. A page missing from the rendered nav is not necessarily an oversight, so check for a `hidden:` entry before fixing it, and ask before changing one to `file:`.

## Known traps

- **The landing page is `elastic-agent-builder.md`, not `agent-builder.md`.** It breaks the sibling-landing-page convention the other area files rely on. Do not create `agent-builder.md`, and do not assume the landing page is missing.
- **Landing page placement is inconsistent between trees.** The platform landing page is a sibling of its directory, but `solutions/security/ai/agent-builder/agent-builder.md` sits *inside* its directory. Match whichever tree you are editing.
- **A new built-in is a table row, not a page.** The `-reference` inventories exist so that built-ins live in one place, and a page per built-in fragments them.
- **The `-reference` pages are hand-maintained.** Treat an existing row as a claim to verify against the plugin registration, not as evidence.
- **Three seams into other areas, and each belongs to the other side.** Creating alerts from Agent Builder meets `alerting-and-cases.md`, the agents-and-workflows and workflow-tools pages meet `workflows.md`, and Attack Discovery's Agent Builder pages belong to `elastic-security.md`. Load the other area file rather than guessing, and prefer linking over restating.
- **`limitations-known-issues.md` is not a release note.** Known issues in release notes come from the changelog tooling; this page is the durable limitations list for the feature.
