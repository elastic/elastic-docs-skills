# Editorial preferences

Starter prose-craft and drafting defaults for Elastic docs work. Copy this file, customize it, and point `docs-accept-quest` at your copy during first-run setup. These preferences complement the [style guide](https://www.elastic.co/docs/contribute-docs/style-guide) and Vale — they are not mechanically checkable like the pitfalls checklist.

**Read when (required for writing tasks):** before drafting or editing docs prose (`docs-accept-quest` Phase 4) and again at self-review (Phase 6). Read this file with the Read tool — do not rely on ambient memory alone.

**Do not encode here:** quest workflow gates, full `applies_to` syntax, or product-accuracy rules — those belong in `docs-accept-quest`, `docs-applies-to-tagging`, or the pitfalls checklist.

---

## Drafting defaults (must not fail)

Apply these on every docs draft:

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
| above / below (positional) | restructure or link |
| please / easy / simply / just | (omit) |
| em dash (—) | comma, colon, or rewrite |
| semicolon joining clauses mid-sentence | period (two sentences), or rewrite |

- Second person ("you"), present tense, active voice. Sentence case for headings.
- Bold UI element names: **Save**, **Add panel**, **Settings**. Icon-only controls: `` {icon}`gear` **Settings** ``.
- "can" for capability, "might" for possibility, "may" for permission.
- Never stack consecutive admonitions. If two would appear back-to-back, the content belongs in the prose.
- **Cross-discoverability is bidirectional.** When new content points at an existing section ("see also Y"), add a reciprocal pointer at the **top** of Y.
- For UI renames without `applies_to` badges, prefer **New label** or **Old label** (depending on your {{product}} version) — for example **Reset** or **Reset changes** (depending on your {{stack}} version). Name the product or stack in the parenthetical. Prefer this over slash forms (**New**/**Old**) unless the surrounding page already uses slashes consistently.

### Integrating new content (admonition ladder)

Default: weave new information into existing prose or steps. When content is situational (corner case, condition most readers skip), use this ladder:

1. Fold into the natural prose flow without breaking the paragraph.
2. Become a bullet in a nearby list (with its own `{applies_to}` if version-scoped).
3. Use `:::{note}` / `:::{tip}` / `:::{warning}` / `:::{important}` when folding would split a coherent sentence.

Safety warnings, non-obvious gotchas, and version-scoped prose that does not fit any inline `applies_to` placement also warrant an admonition.

---

## Voice and prose

- One precise sentence beats three vague ones. Don't pad. If a sentence restates what the UI already makes obvious, omit it.
- One precise **active** sentence in FAQ and situational prose; no padded passive ("can be offered", "can be turned off") or menu restatements.
- Match the language of the existing docs, not the PR or issue body. Developer jargon (`embeddable`, `by-reference panel`, `DSL filter`) does not belong in user docs.
- Lead with concrete action or benefit, not "X means Y" definitions or unearned analogies.
- When describing a UI control, lead with what it does to the data or model; visual effect is subordinate.
- When a behavior depends on a toggle or mode, state that condition in its own sentence — don't bury it in a relative clause that reads unconditional.
- **Don't anthropomorphize administrators.** Frame availability as defaults plus configurable settings: "By default, {{kib}} offers… On [deployment types], administrators can enable or disable… in the [settings]."
- Prefer factual, verifiable contrasts over salesy benefit framing ("spend less time…").
- When a fact can't be verified against source, **surface it as unverified** in the draft or PR comment — don't omit silently and don't assert it.

## Formatting

- Separate menu/navigation steps with ` → `, never `>` or `=>`: **Add** → **Controls** → **Variable control**. (Vale: `Elastic.MenuArrows` / `Elastic.MenuArrowsBold`; leave `>` inside code/queries alone.)
- Don't add icons to text-labeled buttons unless the product actually shows one.
- Don't reach for admonitions when content can flow into the prose. Admonitions are for situational, off-the-main-path content (a corner case, a non-obvious gotcha, a version-scoped note).
- "Limitations" framed constructively: prefer "X doesn't work with Y" or "Y is required for X" over "is not supported" lists.
- **Cross-links:** prefer `<repo>://path/to/file.md` when the target lives in another docs repo. Link to a real file path that resolves. Use `#anchor` only when pointing at a section below the page H1; links to the page itself should omit the fragment.

## Per-user vs admin scope

- For a **per-user preference** that applies to the open Kibana, scope the effect: "select the language you prefer **for your current project or deployment**" — not a bare "the language you prefer."
- **Chrome preference UIs** (Language / Appearance modals vs **Edit profile** editors) depend on product source (`user.elastic_cloud_user`, `cloud.isCloudEnabled`), not deployment labels alone. Verify which path applies before tagging; include **ECE** and **ECK** when they share the self-managed profile path.

## UI labels, navigation, and terminology

- **Bold** literal page or feature names on **first mention** when they appear as UI page headers (verified against screenshots) — not every generic mention in running prose.
- A **page title or selector-card label** is not necessarily a left-nav entry. Write the path readers actually use; don't invent a standalone app entry.
- Open a Kibana app by **naming it** ("in the **Dashboards** app"), not by linking the app overview page when the task is to use an object inside the app.
- Icon-plus-link-styled controls don't need a verb in the label; reserve verb+noun ("Manage X") for filled toolbar buttons.
- For destructive or irreversible actions, avoid **restore** — use **reset** when the user must re-configure from scratch afterward.
- Don't borrow API reference terminology (schema or field names) for UI voice; use API docs only to verify structural facts.
- Prefer **Visualizations**, not **Lens**, when both editor modes sit behind the same UI.
- Use **time field**, not "date field", in Kibana/Vega time-range docs (matches **time filter** and `%timefield%` corpus).

## Structure and IA

- **No scattered tips when content is reusable.** Prefer a dedicated page that other pages link to over duplicated tips.
- **Place new content where its content type belongs.** A workflow step belongs in a how-to. A behavior detail belongs in reference. An overview is for what + why, not how. Don't flag gaps on overview pages for missing specifics that belong in reference.
- **Match page scope to feature scope.** Document narrower-scope behavior on the narrower page; leave a one-line cross-reference on the broader one.
- **Read `toc.yml` before IA calls.** The parent page's scope and its existing children decide section vs. child page vs. peer page — not the page body alone.
- **Classify each addition by content type before choosing a section:** behavior the user performs → procedure step; failure/symptom → troubleshooting; capability or limit → reference; what/why → overview. Don't put a behavior note in a limitations list because the issue suggested it.
- **Requirements / license gates** belong at the **start** of the section they gate, before enablement or how-it-works prose — not mid-paragraph.
- Don't repeat a page-level **Requirements** privilege inside a subsection on the same settings surface.
- **Mixed content types on one page** are acceptable when there is no natural better home — default to the content-type home; mix only when splitting would scatter the reader's task.
- **Thin overview that links out** when authoritative detail lives elsewhere (Terraform Registry, API spec) — orient and link, don't duplicate schemas that will drift.
- **Stage×tool workflows:** prefer a comparison table over diagrams or steppers when mapping stages across two tools.
- **Sibling caveats/alternatives:** gather under one umbrella H2 with ordered H3s; state the ordering principle in the lead-in.
- **Overview pages:** descriptive, conceptual voice — not click-by-click steps that belong on a how-to.
- When two contexts share the **same rule**, fold subjects into one bullet or sentence — don't add a parallel bullet that restates the rule.
- **Avoid compound headings** when the child covers only half the topic; use parallel sibling headings instead.
- Surface **related layouts or variants** together where the reader first meets the concept; link out to detailed workflows from there.
- A **platform-wide feature** in a solution space gets a neutral, version-tagged discovery pointer — don't imply the feature is solution-specific.
- When removing duplicated sections, don't keep empty headings for legacy fragments; move routing prose and preserve anchors with invisible `$$$anchor$$$` at the destination.

## Lists, tables, and version-scoped prose

- For **supported types** with per-item availability, prefer a two-column table (item | description) with inline `{applies_to}` in the cell — badged only where it differs from the page default.
- Inside a version-scoped block, say **"in later versions"** — not a bare stack version ("in 9.5 and later") in forward-looking prose.
- When **Inspect** covers more than one request path, broaden the heading (for example **Inspect requests**) — don't leave search-API-only wording after ES|QL is added.
- Situational states (empty panels after enablement, reload tips) belong in a **`:::{tip}`** — not inline after a procedure list. Reload {{kib}}, not "reload the page."

## Snippets and generated content

- Don't add a **duplicate framing sentence** in the wrapper before a `{{include}}` when the snippet already opens with its topic sentence.
- When a **generated snippet owns an inventory**, don't duplicate it in a manual table; add manual subsections only for items that need extra explanation.

## Worked examples and intros

- **Parser-backed query examples:** don't treat in-app help as the complete capability list; audit pinned grammar and tests; run each example against a **complete** real API response shape.
- When an intro **lists data sources**, enumerate every mechanism verified in product source; nest query languages under Elasticsearch; link extension topics on-page.

## Agent and meta files

- In files loaded into every agent context, state a cross-cutting policy **once** (for example "reach for a skill first…") — not in every section.
- Capitalize **Markdown** as a proper noun.
