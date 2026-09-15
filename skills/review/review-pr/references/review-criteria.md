# Docs PR review criteria

The rubric `docs-review-pr` applies. Six criteria: user focus, technical accuracy, applicability, maintainability, language, style.

This file is the **floor**, not a fallback. It is written to work with no network, no MCP, and no authentication — the case in agentic workflows and CI. When the `elastic-internal-docs` MCP is reachable, Step 0 of the skill fetches the canonical checklist and that takes precedence; note any conflict in the report.

Each criterion below cites the public Elastic documentation that governs it. When a check is ambiguous, the cited page decides, not this summary.

---

## User focus

Sources: [content types](https://www.elastic.co/docs/contribute-docs/content-types), [formatting](https://www.elastic.co/docs/contribute-docs/style-guide/formatting), [SEO](https://www.elastic.co/docs/contribute-docs/how-to/seo)

### Content completeness

- The change serves a real user task, goal, or intent.
- The benefit of the feature or path is stated, not only its mechanics.
- Every page the change affects is assessed and updated, including reference pages that use a newly introduced concept.
- A new feature is contextualized on its parent page, against the surrounding product landscape.

### Scannability

- Paragraphs stay short, and lists, tables, and admonitions break up dense content.
- Lead-in sentences set topic boundaries and tell the reader how to think about what follows.
- The change sits in the correct place on the page.

### Findability

- The page sits in the correct place in the information architecture.
- Cross-references point into the page from its parents, so users are not stranded.
- The page has one clear goal and matches an Elastic Docs content type.
- The page declares that type in frontmatter as `type:`. When a change makes the content type clear on a page that does not declare one, recommend adding it, even if nothing consumes the field yet. This applies to edited pages as much as to new ones — an existing page never went through a template, so the field is the one most often missed.
- Screenshots and diagrams appear only where they are necessary.
- Instructions are unambiguous.
- Headings run about 50–60 characters where practical, and describe the page distinctly from similar ones.

### Logical flow

- Content is ordered and located the way a reader would need it.
- The page discloses progressively.
- Conceptual choices use contrasting pairs.
- Options carry value propositions near the decision point.
- Branching decisions use nested navigation where that helps.

---

## Technical accuracy

Sources: no single public page governs this. A subject matter expert or an authoritative source establishes correctness.

### Correctness

- The content is written by a subject matter expert, or backed by engineering or another authoritative source: an issue, a Slack thread, an engineering review.
- Claims are tested where testing is possible.
- Nothing contradicts the rest of the documentation corpus.
- New code samples are tested.
- When the change references a code PR or commit, the documentation matches it: setting and parameter names, default values and limits, and behavior asserted by the tests in that change. The code PR's base branch matches the page's `applies_to`, and an unmerged code PR is reported as intended rather than settled behavior.

A reviewer cannot confirm that a subject matter expert reviewed a change. Report whether the evidence exists and where, or that it is absent. Never infer technical correctness from confident prose.

### Precise prerequisites

- Permissions, setup, and assumed knowledge are stated.
- No new permission or setup dependency is left unstated.
- Deployment types and versions appear in prerequisites when they differ from page-level tagging.

---

## Applicability

Sources: [cumulative docs guidelines](https://www.elastic.co/docs/contribute-docs/how-to/cumulative-docs/guidelines), [badge placement](https://www.elastic.co/docs/contribute-docs/how-to/cumulative-docs/badge-placement), [deployment types](https://www.elastic.co/docs/contribute-docs/how-to/deployment-types)

### applies_to tags

- Product, version, and lifecycle are specified correctly.
- A single applicability facet applies at page level. Do not mix stack or serverless with deployment dimensions.
- The versioning scheme matches the product.

### Cumulative structure

- Version-specific changes are tagged.
- For versioned products, changes are non-destructive: older information stays findable, with correct lifecycle and range tags.
- For unversioned products, only current functionality is documented.
- Version-insensitive information carries no version tags.

### Markup correctness

- Ranges, precise versions, and open-ended ranges are used correctly.
- Section-level and line-level tags work alongside page-level tags.

### Deployment types

- Scope is set correctly, and relevant types are covered or signposted.
- Shared processes stay deployment-agnostic.
- Self-managed, ECE, and ECK are distinct deployment types. Do not collapse them into a single group on the grounds that the customer operates them rather than Elastic. They share the same core Elasticsearch functionality — the difference is how a deployment is run, not what it can do — so scope each one explicitly wherever the steps differ.

> **Known divergence from the internal checklist.** The Codex checklist phrases this as "self-managed (vanilla Elasticsearch) not conflated with self/ECE/ECK grouping." That wording is wrong and the correction above is deliberate: "vanilla Elasticsearch" implies a difference in core capability, when the distinction is purely about deployment type. If a Step 0 fetch returns the older phrasing, keep the wording here and note the conflict rather than adopting it.

### Scope discipline

- The change commits to no roadmap items and no future plans.
- The change carries no implementation details or decision history that users do not need.

---

## Maintainability

Sources: [redirects](https://docs-v3-preview.elastic.dev/elastic/docs-builder/tree/main/documentation/redirects), [SEO: interlinking](https://www.elastic.co/docs/contribute-docs/how-to/seo)

### Single source of truth

- No procedure or value is duplicated from somewhere it already lives. A cross-reference or a snippet is better.

### Repository hygiene

- Every renamed, moved, or deleted page has a matching redirect entry, including renamed anchors. A missing redirect is High severity, because it breaks live links. The file is `redirects.yml` or `_redirects.yml`, next to the content set's `docset.yml` or `_docset.yml`. Check both names before reporting one missing.
- No remaining page links to or references a deleted or moved page by its old path.
- No deleted image or snippet is still referenced by another page.
- No image or snippet is left behind unused after the page that used it is removed.
- No generated or automated reference material is hand-edited. The fix belongs at the source.

### High-maintenance content

- Screenshots, diagrams, and especially non-Elastic external links earn their ongoing maintenance cost.

---

## Language

Sources: [grammar and spelling](https://www.elastic.co/docs/contribute-docs/style-guide/grammar-spelling), [word choice](https://www.elastic.co/docs/contribute-docs/style-guide/word-choice), [substitutions](https://docs-v3-preview.elastic.dev/elastic/docs-builder/tree/main/syntax/substitutions)

### Mechanics

- Grammar, spelling, and punctuation support clarity. Simplify punctuation where that helps.

### Plain language and terminology

- The content is accessible to someone new to the topic.
- Jargon, acronyms, and internal terms are defined or linked on first use.
- Wording is minimal and the tone is informational.
- Terms are used consistently, and ambiguous terms follow the word choice guidance.
- No promotional language or superlatives.

### Variables

- Version variables and substitutions are used correctly.

---

## Style

Sources: [voice and tone](https://www.elastic.co/docs/contribute-docs/style-guide/voice-tone), [formatting](https://www.elastic.co/docs/contribute-docs/style-guide/formatting), [accessibility](https://www.elastic.co/docs/contribute-docs/style-guide/accessibility), [UI writing](https://www.elastic.co/docs/contribute-docs/style-guide/ui-writing), [SEO: headings](https://www.elastic.co/docs/contribute-docs/how-to/seo)

### Voice and tense

- Active voice, except where passive is genuinely necessary.
- Voice and tone fit the content type.
- Present tense, unless future is genuinely required.

### Flagged language

Avoid: directional terms, Latinisms, parentheses cruft, italics or bold for emphasis, "and/or," and "please."

### Titles and headings

- Sentence case.
- The title describes the page distinctly from similar titles.
- Action-oriented where appropriate, using a gerund or a verb.
- Content sits between consecutive headings. No empty heading stacks.
- Heading style is consistent at each level.

### Formatting and admonitions

- Formatting is consistent.
- Admonitions are used sparingly, roughly three or fewer in one area, so they still stand out.
- No admonitions are stacked back to back. Merge them into one callout or into the narrative.

### Links, accessibility, and preview

- Link text is meaningful, and new or changed links resolve.
- Tables and images have clear alt text and surrounding explanation.
- The preview is clean: badges render, tables and tabsets stay intact, no stray bullets or comments, and no literal `{{` reaches the output.

---

## Deciding the review action

Match the action to the state of the PR.

| Action | When |
|---|---|
| **Approve** | The content meets the quality threshold. Minor optional suggestions go in as comments rather than blocking. |
| **Comment** | You have questions or non-blocking feedback. |
| **Request changes** | The content is below the quality threshold, or the change would prevent users from succeeding with the product or feature. |

Blocking a PR is a normal part of maintaining quality, not a judgment on the author. Holding a PR is better than shipping content that confuses or misleads users.

## Review etiquette

- When one issue repeats across the PR, report it once as a pattern with a count and a couple of examples, rather than commenting on every instance.
- Where the content is strong, say so. Positive feedback reinforces good writing habits and makes the review less daunting.
- Who wrote the PR tells you where to focus. A developer's information is usually technically sound, so weight language and style. A writer's PR with a developer tagged might still change after the technical review. A PR from outside both groups needs a writer with subject matter expertise for anything beyond a typo fix.
- Treat automated output as a first pass, not a substitute for review. It is not always accurate and needs human judgment before anyone acts on it.

---

## Rule citations

Cite the governing guideline on every Language and Style finding, and on any other finding a specific page decides. A writer who disagrees with a finding needs somewhere to go and check, and "the style guide says so" is not that.

Link to the section, not the page, when one of these covers the rule:

| Rule | Link |
|---|---|
| Active and passive voice | [voice-tone#active-and-passive-voice](https://www.elastic.co/docs/contribute-docs/style-guide/voice-tone#active-and-passive-voice) |
| Informational tone | [voice-tone#informational](https://www.elastic.co/docs/contribute-docs/style-guide/voice-tone#informational) |
| Minimal wording | [voice-tone#write-like-a-minimalist](https://www.elastic.co/docs/contribute-docs/style-guide/voice-tone#write-like-a-minimalist) |
| "please" | [voice-tone#please-avoid-please-please](https://www.elastic.co/docs/contribute-docs/style-guide/voice-tone#please-avoid-please-please) |
| Verb tense | [grammar-spelling#verb-tense](https://www.elastic.co/docs/contribute-docs/style-guide/grammar-spelling#verb-tense) |
| Screenshots | [ui-writing#screenshots](https://www.elastic.co/docs/contribute-docs/style-guide/ui-writing#screenshots) |
| Heading length and phrasing | [seo#headings](https://www.elastic.co/docs/contribute-docs/how-to/seo#headings) |
| Cross-references | [seo#interlinking](https://www.elastic.co/docs/contribute-docs/how-to/seo#interlinking) |
| Images and diagrams | [seo#multimedia](https://www.elastic.co/docs/contribute-docs/how-to/seo#multimedia) |
| Mixing applicability facets | [cumulative-docs/guidelines#dimensions](https://www.elastic.co/docs/contribute-docs/how-to/cumulative-docs/guidelines#dimensions) |

Otherwise link the page that governs the criterion, from the Sources line of the section the finding sits under:

| Area | Link |
|---|---|
| Word choice | [style-guide/word-choice](https://www.elastic.co/docs/contribute-docs/style-guide/word-choice) |
| Grammar, spelling, punctuation | [style-guide/grammar-spelling](https://www.elastic.co/docs/contribute-docs/style-guide/grammar-spelling) |
| Formatting, lists, admonitions | [style-guide/formatting](https://www.elastic.co/docs/contribute-docs/style-guide/formatting) |
| Alt text, link text, directional language | [style-guide/accessibility](https://www.elastic.co/docs/contribute-docs/style-guide/accessibility) |
| Writing about the UI | [style-guide/ui-writing](https://www.elastic.co/docs/contribute-docs/style-guide/ui-writing) |
| Voice, tone, tense | [style-guide/voice-tone](https://www.elastic.co/docs/contribute-docs/style-guide/voice-tone) |
| Content types and page structure | [content-types](https://www.elastic.co/docs/contribute-docs/content-types) |
| applies_to and cumulative docs | [cumulative-docs/guidelines](https://www.elastic.co/docs/contribute-docs/how-to/cumulative-docs/guidelines) |
| Badge placement | [cumulative-docs/badge-placement](https://www.elastic.co/docs/contribute-docs/how-to/cumulative-docs/badge-placement) |
| Deployment scope | [how-to/deployment-types](https://www.elastic.co/docs/contribute-docs/how-to/deployment-types) |
| Redirects | [docs-builder redirects](https://docs-v3-preview.elastic.dev/elastic/docs-builder/tree/main/documentation/redirects) |
| Substitutions and variables | [docs-builder substitutions](https://docs-v3-preview.elastic.dev/elastic/docs-builder/tree/main/syntax/substitutions) |

When a companion skill reports a rule name of its own — a Vale rule such as `Elastic.OxfordComma`, for instance — pass that through as well. It tells the writer which check fired and how to reproduce it.

Do not invent an anchor. If no listed link covers the finding, cite the page and say which part of it applies.
