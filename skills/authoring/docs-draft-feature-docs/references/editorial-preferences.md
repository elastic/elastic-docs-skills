# Editorial preferences

Prose-craft and drafting defaults for Elastic docs, additive to the Elastic style guide and to `AGENTS.md`. These are the judgment calls a reviewer makes on a draft that already passes Vale — the things a linter cannot check.

**This file is opt-in and is not loaded automatically.** Point `$EDITORIAL_PREFERENCES_PATH` at it to use it, or at your own file instead. The skill's consistency guarantee comes from the baseline, not from here, so a writer who ignores this file still produces conforming docs.

## Precedence and scope

The [Elastic style guide](https://www.elastic.co/docs/contribute-docs/style-guide) wins on every published page. Where this file is silent, the style guide and `AGENTS.md` still apply in full. Where it conflicts, it loses — and say so rather than silently following the preference. Some rules here restate the style guide on purpose, so a writer reading only this file still gets them; the style guide remains the source when the two drift.

Apply it to **new prose you write**. Do not rewrite unchanged surrounding copy to match it — that turns a focused edit into a diff no one can review, and the skill's lightest-change rule already forbids it. Chat replies are out of scope.

Read it twice per draft: in Step 7 before you write the first sentence, and again in the Step 9b user-oriented review pass. Drafting rules leak, and the pass is where they get caught.

**This file is the single source for these preferences.** If you keep a copy in a local agent file or an editor rule, point it here rather than duplicating the text. Three hand-synced copies of a voice standard is the drift this skill exists to prevent.

## Drafting defaults

Apply these on every draft.

| Avoid | Use instead |
|-------|-------------|
| click | select |
| choose | select |
| hit | select |
| type | enter |
| launch | open |
| execute | run |
| utilize | use |
| in order to | to |
| prior to | before |
| e.g. | for example |
| i.e. | that is |
| above / below / under / over / left / right, as a reference to page position | restructure, name the element, or link |
| please / easy / simply / just | omit |
| em dash | comma, colon, or rewrite |
| semicolon joining clauses mid-sentence | a period and two sentences, or rewrite |

- Second person, present tense, active voice. Sentence case for headings.
- **A new option or mode leads with the user's job.** Before the first sentence, answer three questions: what is this option, what does it help the reader do, and what can they do with it. Open with that. The draft is user-oriented when a reader who came for that job can see themselves in the heading and the opening. Do not open by walking the settings popover, listing every sibling control, or treating the new value as equal to the default. The heading names the job (`View documents as JSON`), not only the control (`Switch the view mode`); the control belongs in the how-to sentence.
- **Verified labels are a checklist, not an outline.** The i18n strings, defaults, and ranges you confirmed in Step 6 must all be true. They do not set paragraph order. Matching a sibling section's structure is not enough when the new capability has its own job, and a parenthetical list of every verified action label is still an outline.
- **Capitalize the first word after a colon**, including in list-item descriptions, because Elastic docs use American English. If the next token is code, an identifier, or a quoted UI string, lead with a real word instead of recapitalizing it.
- Bold UI element names: **Save**, **Add panel**, **Settings**. Icon-only controls take the icon role: `` {icon}`gear` **Settings** ``.
- Use "can" for capability, "might" for possibility, "may" for permission.
- Never stack consecutive admonitions. If two would land back to back, the content belongs in the prose.
- **Cross-discoverability is bidirectional.** When new content points at an existing section, add a reciprocal pointer at the start of that section. For a narrow, single-fact mention rather than a broad topical relationship, the reciprocal pointer can instead live in a more specific sibling page's **Next steps** or **Related** list, when one fits the fact better than the section's own intro.
- For a UI rename with no `applies_to` badge, write **New label** or **Old label** (depending on your {{stack}} version), naming the product or the stack in the parenthetical. Prefer this over the slash form unless the page already uses slashes consistently.
- **No directional page-position language when pointing at other content**, in skill and reference files as much as in published docs: not "above," "below," "under," "over," "left," or "right." These assume a fixed, sighted layout, which breaks for screen readers and for content that gets reflowed or reordered. Name the element or the section, or link to it. Sequencing and temporal language is fine and not covered by this rule — "the following list," "the retention list on this page," and "the API key you saved earlier" all work, because each names its referent rather than relying on position to identify it.

### Simplified Technical English overlay

Adapted from ASD-STE100.

- Keep one main idea per sentence, but combine closely related ideas when the connection improves the flow. Short sentences are not a reason to write a control inventory: why, and what the reader can do, come before how the popover is laid out.
- Vary sentence openings and structure when it improves readability, and use transitions to show how ideas relate.
- Do not split a sentence when splitting it makes the prose abrupt or repetitive.
- Keep instructions concise. Treat 20 words for an instruction and 25 for an explanatory note as targets, not limits. These sit under the style guide's paragraph-level guidance rather than replacing it — a paragraph over about seven lines still wants splitting.
- Use the imperative for direct procedures, and allow explanatory or connective sentences where they guide the reader better.
- State a condition before the instruction that depends on it: "If the build fails, check the logs."
- Prefer short, common words over jargon or fancy synonyms.
- Use one term per concept. Do not switch synonyms for the same thing.
- Avoid hedging such as "should probably" or "might want to" when the intent is a direct instruction or a fact.
- Use a list for three or more items or steps, when those items are user-facing effects or actions. Do not list the object types that store a setting, or sibling action labels, only because there happen to be three of them.
- Order information: setup before use, cause before effect, condition before action.

### Integrating new content

Default to weaving new information into existing prose or steps. When the content is situational — a corner case, or a condition most readers skip — work down this ladder and stop at the first rung that fits:

1. Fold it into the prose flow without breaking the paragraph.
2. Make it a bullet in a nearby list, with its own `{applies_to}` when it is version-scoped.
3. Use `:::{note}`, `:::{tip}`, `:::{warning}`, or `:::{important}` when folding would split a coherent sentence.

Safety warnings, non-obvious gotchas, and version-scoped prose that fits no inline `applies_to` placement also warrant an admonition.

## Voice and prose

- One precise sentence beats three vague ones. Do not pad. If a sentence restates what the UI already makes obvious, cut it.
- One precise **active** sentence in FAQ and situational prose. No padded passive ("can be offered," "can be turned off") and no menu restatements.
- Match the language of the existing docs, not the language of the pull request or issue body. Developer jargon — `embeddable`, `by-reference panel`, `DSL filter`, `unquoted remainder` — does not belong in user docs. Use a technical term only when it is widely known, already defined on the page, or when the page introduces a feature and must explain the term.
- Lead with concrete action or benefit, not an "X means Y" definition or an unearned analogy.
- When describing a UI control, lead with what it does to the data or the model; the visual effect is subordinate. A section that only restates the popover is feature-description mode. Rewrite until a reader searching for the job — inspect JSON, copy a field, filter in the table — can see themselves in the opening.
- When a behavior depends on a toggle or a mode, state that condition in its own sentence. Do not bury it in a relative clause that reads as unconditional.
- **Do not anthropomorphize administrators.** Frame availability as defaults plus configurable settings: "By default, {{kib}} offers… On [deployment types], administrators can enable or disable… in the [settings]."
- Prefer factual, verifiable contrasts over salesy benefit framing such as "spend less time…".
- When a fact cannot be verified against source, **surface it as unverified** in the draft output or the pull request comment. Do not omit it silently, and do not assert it. This is the same rule as Step 6, restated because it is easiest to break while writing.

## Formatting

- **Capitalize the first word after a colon**, including in linked list descriptions. British English usually leaves that word lowercase; Elastic docs use [American English](https://www.elastic.co/docs/contribute-docs/style-guide/grammar-spelling). Do not recapitalize code, identifiers, API names, or quoted UI strings — if one of those would be the first token, add a leading word.

  - Don't: `[Data in this cluster or project](#id): wildcards, comma-separated names, or a minus sign to exclude`
  - Do: `[Data in this cluster or project](#id): Wildcards, comma-separated names, or a minus sign to exclude`
  - Don't: `` [Data in another cluster](#id): `cluster:index` syntax for {{ccs}} ``
  - Do: `` [Data in another cluster](#id): Use `cluster:index` syntax for {{ccs}} ``

- Separate menu and navigation steps with ` → `, never `>` or `=>`: **Add** → **Controls** → **Variable control**. Vale checks this as `Elastic.MenuArrows` and `Elastic.MenuArrowsBold`. Leave `>` inside code and queries alone.
- Do not add icons to text-labeled buttons unless the product actually shows one.
- Do not reach for an admonition when the content can flow into the prose. Admonitions are for situational, off-the-main-path content.
- Frame limitations constructively: prefer "X doesn't work with Y" or "Y is required for X" over a list of things that are "not supported."
- **Cross-links:** prefer `<repo>://path/to/file.md` when the target lives in another docs repo, and link to a real file path that resolves. Use `#anchor` only when pointing at a section within a page; a link to the page itself omits the fragment.
- Capitalize **Markdown** as a proper noun.

## Per-user versus admin scope

- For a **per-user preference** that applies to the open Kibana, scope the effect: "select the language you prefer **for your current project or deployment**," not a bare "the language you prefer."
- **Chrome preference surfaces** — the Language and Appearance modals versus the **Edit profile** editors — depend on product source (`user.elastic_cloud_user`, `cloud.isCloudEnabled`), not on deployment labels alone. Verify which path applies before tagging, and include **ECE** and **ECK** when they share the self-managed profile path.

## UI labels, navigation, and terminology

- **Bold** a literal page or feature name on **first mention** when it appears as a UI page header and you have verified it against a screenshot. Not every generic mention in running prose.
- A **page title or selector-card label** is not necessarily a left-nav entry. Write the path readers actually use; do not invent a standalone app entry.
- Open a Kibana app by **naming it** — "in the **Dashboards** app" — rather than linking the app overview page, when the task is to use an object inside the app.
- Icon-plus-link-styled controls do not need a verb in the label. Reserve verb-plus-noun ("Manage X") for filled toolbar buttons.
- For destructive or irreversible actions, avoid **restore**. Use **reset** when the user has to reconfigure from scratch afterward.
- Do not borrow API reference terminology — schema or field names — for UI voice. Use API docs only to verify structural facts.
- Prefer **Visualizations** over **Lens** when both editor modes sit behind the same UI.
- Use **time field**, not "date field," in Kibana and Vega time-range docs, to match **time filter** and `%timefield%`.

## Structure and information architecture

- **No scattered tips when the content is reusable.** Prefer a dedicated page that other pages link to over a duplicated tip.
- **Place new content where its content type belongs.** A workflow step belongs in a how-to, a behavior detail in reference, and an overview covers what and why rather than how. Do not flag a gap on an overview page for specifics that belong in reference.
- **Match page scope to feature scope.** Document narrower-scope behavior on the narrower page, and leave a one-line cross-reference on the broader one.
- **Read `toc.yml` before an IA call.** The parent page's scope and its existing children decide section versus child page versus peer page. The page body alone does not.
- **Classify each addition by content type before choosing a section:** a behavior the user performs is a procedure step, a failure or symptom is troubleshooting, a capability or limit is reference, and what-and-why is overview. Do not put a behavior note in a limitations list because the issue suggested it.
- **Requirements and license gates** belong at the start of the section they gate, before the enablement or how-it-works prose — not mid-paragraph. Do not repeat a page-level **Requirements** privilege inside a subsection on the same settings surface.
- **Mixed content types on one page** are acceptable when there is no natural better home. Default to the content-type home, and mix only when splitting would scatter the reader's task.
- **A thin overview that links out** is right when the authoritative detail lives elsewhere, such as the Terraform Registry or an API spec. Orient and link rather than duplicating a schema that will drift.
- For a **stage-by-tool workflow**, prefer a comparison table over a diagram or a stepper when mapping stages across two tools.
- Gather **sibling caveats or alternatives** under one umbrella H2 with ordered H3s, and state the ordering principle in the lead-in.
- **Overview pages** take a descriptive, conceptual voice, not the click-by-click steps that belong on a how-to.
- When two contexts share the **same rule**, fold both subjects into one bullet or sentence rather than adding a parallel bullet that restates it.
- **Avoid a compound heading** when the child covers only half the topic. Use parallel sibling headings instead.
- Surface **related layouts or variants** together where the reader first meets the concept, and link out to the detailed workflows from there.
- A **platform-wide feature** in a solution space gets a neutral, version-tagged discovery pointer. Do not imply the feature is solution-specific.
- When removing a duplicated section, do not keep an empty heading for the legacy fragment. Move the routing prose and preserve the anchors with an invisible `$$$anchor$$$` at the destination.

## Lists, tables, and version-scoped prose

- For **supported types** with per-item availability, prefer a two-column table of item and description with inline `{applies_to}` in the cell, badged only where it differs from the page default.
- Inside a version-scoped block, say **"in later versions"** rather than a bare stack version in forward-looking prose.
- When **Inspect** covers more than one request path, broaden the heading — for example, **Inspect requests** — rather than leaving search-API-only wording in place after ES|QL is added.
- Situational states, such as empty panels after enablement or a reload tip, belong in a `:::{tip}` rather than inline after a procedure list. Reload {{kib}}, not "reload the page."
- **List `serverless` first** whenever `applies_to` names both serverless and stack, unless serverless is `unavailable`. This covers sibling bullets, `applies-item` and `applies-switch` keys, consecutive inline `{applies_to}` tags, and `:applies_to:` objects. When serverless is `unavailable`, list it after stack.
- **Version-variant bullets are their own list.** When two tagged bullets state the same fact at different versions, do not mix them into a list of unrelated items. Lead with an untagged sentence stating the shared condition, and put the newest variant first.

## Snippets and generated content

- Do not add a duplicate framing sentence in the wrapper before an `{{include}}` when the snippet already opens with its topic sentence.
- When a **generated snippet owns an inventory**, do not duplicate it in a manual table. Add manual subsections only for the items that need extra explanation.

## Worked examples and intros

- For **parser-backed query examples**, do not treat in-app help as the complete capability list. Audit the pinned grammar and the tests, and run each example against a complete real API response shape.
- When an intro **lists data sources**, enumerate every mechanism verified in product source, nest query languages under Elasticsearch, and link extension topics on the page.

## Agent and meta files

In a file loaded into every agent context, state a cross-cutting policy once rather than repeating it in every section.

## Exceptions

None of this applies to code, identifiers, API names, CLI flags, configuration keys, or quoted and verbatim external text. Reproduce those exactly, including casing that looks wrong — the area files record the cases where non-obvious casing is deliberate.
