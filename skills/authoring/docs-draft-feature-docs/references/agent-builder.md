# Elastic Agent Builder

The AI agent platform — agents, skills, tools, MCP and A2A servers, and programmatic access. 63 of the 81 files under `explore-analyze/ai-features/`, so it gets its own area file rather than sharing one with the AI features hub.

Split from `ai-features.md`, which owns the hub page, the AI assistants, LLM connector guides, and Automatic Import. If a request touches both, load both.

> Verified against docs-content and `elastic/kibana` on 2026-09-16. Agent Builder reached GA on stack 9.3 after a 9.2 preview and is GA on serverless, so it is moving quickly — treat page inventories here as a starting point and check the tree.

## Where content lives

| Path | What belongs here |
|---|---|
| `explore-analyze/ai-features/elastic-agent-builder.md` | The landing page. **Note the filename** — it is not `agent-builder.md` |
| `explore-analyze/ai-features/agent-builder/` | Everything else: `get-started`, `chat`, `agents`, `skills`, `models`, `permissions`, `glossary`, `limitations-known-issues` |
| `agent-builder/tools/` | Tool types: `builtin-tools-reference`, `custom-tools`, `esql-tools`, `index-search-tools`, `mcp-tools`, `workflow-tools` |
| `agent-builder/troubleshooting/` | One page per symptom, named for the symptom — `context-length-exceeded.md`, `api-calls-return-403-forbidden.md` |
| `agent-builder/_snippets/api-tutorial/` | 22 request snippets composing the API tutorial. Edit the snippet, not the tutorial page |
| `solutions/security/ai/agent-builder/` | Security-specific only: `agent-builder.md`, `skills-model.md`, `skills-use-cases.md` |
| `solutions/observability/ai/agent-builder-observability.md` | Observability-specific only |

Reference pages carry the `-reference` suffix: `builtin-agents-reference.md`, `builtin-skills-reference.md`, `tools/builtin-tools-reference.md`. These are generated-feeling inventories — `builtin-skills-reference.md` is about 400 lines — so a new built-in belongs as a row there, not as a new page.

### Placement: platform or solution

The default is the platform tree, and the bar for a solution page is high. Ask what the content is actually about:

- **How the capability works** — the platform tree, always. A Security-flavored example does not make it Security content.
- **A solution-specific integration point** — the solution tree, kept thin and linking back. `solutions/security/ai/agent-builder/` holds three pages against 63 on the platform side, which is the ratio to aim for.
- **A solution feature that happens to use Agent Builder** — the feature's own home. `solutions/security/ai/attack-discovery/run-attack-discovery-from-agent-builder.md` sits with Attack Discovery, not here.

Do not mirror a platform page into a solution tree to make it easier to find. That is what navigation and links are for, and duplicated AI content drifts fast.

## Source of truth

| Question | Verify at |
|---|---|
| Agent, skill, and tool behavior; API shapes | `x-pack/platform/plugins/shared/agent_builder` in `elastic/kibana` |
| Navigation entries and deep links | `src/platform/packages/shared/deeplinks/agent_builder` |
| Built-in agents, skills, and tools | The plugin's registrations. The `-reference` pages are hand-maintained and go stale — the registration list is the truth |
| Connector and model support | `x-pack/platform/plugins/shared/stack_connectors`, plus `models.md` for the tested-model list |
| Availability by version and project type | The plugin config and feature flags, not the current `applies_to` on a neighboring page |

There is no `onechat` plugin. If a request or an older page refers to one, the code moved to `agent_builder` — verify against the current path.

## Read these first

- `explore-analyze/ai-features/elastic-agent-builder.md` — 114 lines. The landing page, and the model for how the area introduces itself and routes to Get started.
- `explore-analyze/ai-features/agent-builder/tools/esql-tools.md` — 153 lines. A good model for a capability page with worked examples.
- `explore-analyze/ai-features/agent-builder/glossary.md` — settles terminology, with an entry for each of agent, skill, and tool. Read it before inventing a term for anything in this area.
- `explore-analyze/ai-features/agent-builder/skills.md` — the authority on how skills relate to tools and to the system prompt. The glossary summarizes it; this page is the source.

## Local conventions

`{{agent-builder}}` renders "Elastic Agent Builder" and is defined at `docset.yml:387`. Use it rather than typing the product name. There is no substitution for the Security AI Assistant, so that name is written out literally.

Agent, skill, and tool are distinct concepts with a glossary entry each, and the hierarchy is load-bearing. As `skills.md` puts it, a tool performs a discrete operation while a skill bundles instructions, tools, and context, teaching the agent *how* and *when* to use them — skills sit one level above tools. A skill is not "a thing the agent can do", and the two words are not interchangeable. Check `glossary.md` before introducing a fourth noun.

`glossary.md` has its own format, and entries there are not ordinary prose: an explicit `$$$anchor$$$` on the line above the term, inline `{applies_to}` roles on the term line itself, a definition-list body indented with `:` , and cross-references in the empty-link-text `See [](skills.md#how-skills-are-invoked)` form. Copy the shape of a neighboring entry. Per-entry `applies_to` matters here because the concepts landed in different versions — Agent Builder is GA from 9.3, while skills are GA from 9.4.

API content composes from `_snippets/api-tutorial/`, one snippet per request. A change to a request body is a snippet edit, and it may appear on more than one page — grep for the snippet filename before editing.

Let `docs-applies-to-tagging` set `applies_to`. The landing page carries `stack: preview =9.2, ga 9.3+` with `serverless: ga`, and the preview-then-GA split means cumulative-docs rules apply to most pages here.

## Navigation

Inline in `explore-analyze/toc.yml`, under `ai-features.md` → `ai-features/elastic-agent-builder.md`, nesting four levels deep in places. The parent entry is the landing page, so a new page goes in that subtree rather than at the `ai-features.md` level.

**Some pages are deliberately `hidden:` rather than absent.** Under `ai-features`, `agent-builder/connectors.md` and `agent-builder/plugins.md` are hidden, and six entries are hidden across `explore-analyze/toc.yml`. A page missing from the rendered nav is not necessarily an oversight, so check for a `hidden:` entry before "fixing" it, and ask before changing one to `file:` — hiding is usually deliberate.

## Known traps

- **The landing page is `elastic-agent-builder.md`, not `agent-builder.md`.** It breaks the sibling-landing-page convention the other area files rely on. Do not create `agent-builder.md`, and do not assume the landing page is missing.
- **Landing page placement is inconsistent between trees.** The platform landing page is a sibling of its directory, but `solutions/security/ai/agent-builder/agent-builder.md` sits *inside* its directory. Match whichever tree you are editing.
- **A new built-in is a table row, not a page.** The `-reference` inventories exist so that built-ins live in one place. A new page per built-in fragments them.
- **The `-reference` pages are hand-maintained.** Treat an existing row as a claim to verify against the plugin registration, not as evidence.
- **Three seams into other areas, and each belongs to the other side.** `agent-builder/create-alerts.md` meets `alerting-and-cases.md`, `agent-builder/agents-and-workflows.md` and `tools/workflow-tools.md` meet `workflows.md`, and Attack Discovery's Agent Builder pages belong to `elastic-security.md`. Load the other area file rather than guessing, and prefer linking over restating.
- **`limitations-known-issues.md` is not a release note.** Known issues in release notes come from the changelog tooling; this page is the durable limitations list for the feature.
