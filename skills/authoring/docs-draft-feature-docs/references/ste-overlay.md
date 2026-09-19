# Simplified Technical English overlay

Adapted from ASD-STE100. A prose-craft layer for drafting, additive to the Elastic style guide.

**This file is opt-in and is not loaded automatically.** Point `$EDITORIAL_PREFERENCES_PATH` at it to use it, or at your own file instead. The skill's consistency guarantee comes from the baseline, not from here, so a writer who ignores this overlay still produces conforming docs.

## Precedence and scope

The [Elastic style guide](https://www.elastic.co/docs/contribute-docs/style-guide) wins on every published page. Where this overlay is silent, the style guide and `AGENTS.md` still apply in full. Where it conflicts, it loses.

Apply it to **new prose you write**. Do not rewrite unchanged surrounding copy to match it — that turns a focused edit into a diff no one can review, and the skill's lightest-change rule already forbids it. Chat replies are out of scope.

**This file is the single source for the overlay.** If you keep a copy in `AGENTS.local.md` or a Cursor rule such as `~/.cursor/rules/ste-artifacts.mdc`, point those at this file rather than duplicating the text. Three hand-synced copies of a voice standard is the drift this skill exists to prevent.

## Sentences

- Keep one main idea per sentence, but combine closely related ideas when the connection improves the flow.
- Do not split a sentence when doing so makes the prose abrupt or repetitive.
- Vary sentence openings and structure when it improves readability.
- Use transitions to show relationships between ideas.
- Keep instructions concise. Treat 20 words for an instruction and 25 for an explanatory note as targets, not limits. These sit under the style guide's paragraph-level guidance rather than replacing it — a paragraph over about seven lines still wants splitting.

## Instructions

- Use the imperative for direct procedures, and allow explanatory or connective sentences where they guide the reader better.
- State a condition before the instruction that depends on it: "If the build fails, check the logs."
- Avoid hedging such as "should probably" or "might want to" when the intent is a direct instruction or a fact.

## Structure

- Use a list for three or more items or steps.
- Order information: setup before use, cause before effect, condition before action.

## Already covered by the style guide

These belong to the overlay's spirit but are not repeated as rules here, because the style guide is their source and a second copy would drift from it:

- **Plain words over jargon** — `style-guide/accessibility.md` requires plain language and links the plainlanguage.gov guidelines.
- **One term per concept** — `style-guide/voice-tone.md` and the word-choice section cover consistent terminology and its preferred verbs.
- **Em dashes, semicolons, and active voice** — `style-guide/grammar-spelling.md` covers em dashes and semicolons; `style-guide/voice-tone.md` covers active voice, including when passive is acceptable.

Read the style guide for these rather than inferring them from this file.

## Exceptions

None of the above applies to code, identifiers, API names, CLI flags, configuration keys, or quoted and verbatim external text. Reproduce those exactly, including casing that looks wrong — see the area files for cases where non-obvious casing is deliberate.
