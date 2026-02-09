---
description: "Elastic docs writing style: voice, tone, grammar, formatting, word choice, and accessibility guidelines"
globs: ["**/*.md"]
alwaysApply: false
---

# Writing Style Guide

## Voice Principles

- **Human and empathetic**: Write for people, not robots. Acknowledge user challenges.
- **User-focused**: Center content on what the user needs to accomplish.
- **Action-oriented**: Help users get their jobs done with clear, direct guidance.

## Tone

Match tone to context:

- **Stimulating**: Exciting new features, getting started content.
- **Friendly**: Tutorials, quick starts.
- **Informational**: Reference docs, concepts, how-tos (most common).
- **Empathetic**: Warnings, deprecation notices, upgrade guidance.
- **Supportive**: Error messages, licensing/billing, vulnerability content.
- **Stern**: Danger warnings only.

## Sentence Structure

- Write like a minimalist. Cut unnecessary words.
- Use active voice: "Elasticsearch indexes the document" not "The document is indexed by Elasticsearch."
- Use present tense: "The agent sends data" not "The agent will send data."
- Never use "please" in instructions.
- Don't confuse nouns and verbs (e.g., "setup" is a noun, "set up" is a verb).
- Avoid ambiguity: be specific about what "it", "this", or "that" refers to.

## Pronouns

- Use second person: "you" and "your."
- Use "they/them" for gender-neutral singular pronouns.
- Use first-person ("we") sparingly.

## Contractions

- Use contractions conversationally: "don't", "isn't", "you'll."
- Don't mix contractions with spelled-out forms in the same context.

## Capitalization

- Use sentence-style capitalization for headings: "Create an ingest pipeline" not "Create an Ingest Pipeline."
- Capitalize proper nouns and product names. Match UI capitalization.

## Abbreviations and Acronyms

- Spell out on first use: "application performance monitoring (APM)."
- Don't spell out in titles/headings.
- Don't use apostrophes for plurals: "APIs" not "API's."
- Avoid Latin abbreviations: use "for example" not "e.g.", "that is" not "i.e."

## Punctuation

- Use serial (Oxford) commas.
- Use em dashes (—) without spaces for parenthetical phrases.
- Use en dashes (–) for ranges: "pages 10–20."
- Avoid semicolons in docs; split into two sentences instead.

## Numbers

- Write out one through nine. Use numerals for 10 and above.
- Always use numerals in tables, with units, and with decimals.
- Use commas in numbers 1,000 and above.

## Formatting

- **Bold**: UI element names (`**Save**`, `**Settings**`).
- **Italic**: Introducing new terms or concepts on first use.
- **Monospace**: Code, file names, paths, field names, parameter values, API endpoints.
- Keep paragraphs short: under 7 lines.
- Use single line breaks between paragraphs.

## Lists

- Use bulleted lists for unordered collections.
- Use numbered lists for sequential procedures.
- Keep list items parallel in structure.
- Don't use a list for a single item.

## Tables

- Use tables for structured data with at least 2 rows and 2 columns.
- Always include a header row.
- Don't use tables for layout or for content that works better as a list.

## Code Samples

- Use consistent indentation.
- Include syntax highlighting with the language identifier.
- Add code callouts or comments for explanation.
- Never include secrets, credentials, or real user data.

## Word Choice

### Preferred Terms

| Use | Instead of |
|-----|-----------|
| add | (not "append" unless technically specific) |
| begin / start | (not "initiate" or "commence") |
| can | (not "may" for ability) |
| cancel | (not "abort") |
| create | (not "make" or "build" for UI actions) |
| delete | (not "destroy" or "kill") |
| edit | (not "modify" for UI actions) |
| enable | (not "activate" or "turn on") |
| enter | (not "type" for text input) |
| open | (not "launch" for UI elements) |
| remove | (not "eliminate") |
| select | (not "click" or "click on") |
| view | (not "see" or "look at") |

### Terms to Avoid

- **abort**: Use "cancel" or "stop."
- **blacklist / whitelist**: Use "blocklist / allowlist."
- **click**: Use "select." Be device-agnostic.
- **easy / simple**: These are subjective. Just explain the steps.
- **please**: Don't use in instructions.
- **type**: Use "enter" for text input.

## Accessibility

- Write scannable content with meaningful headings and short paragraphs.
- Provide alt text for all images.
- Use plain language: aim for an 8th-grade reading level.
- Write meaningful link text: "Learn about index templates" not "click here."
- Use device-agnostic language: "select" not "click," "enter" not "type."
- Avoid directional language: "the following section" not "the section below."

## Screenshots

- Use screenshots sparingly: only for complex UI, time-bound docs, or introductions.
- Aspect ratio: 16:9 or 4:3.
- Zoom: 100%.
- Add a border. Use brand colors for annotations.
- Include only essential UI components.
- Always provide alt text.

## UI Writing

- Describe use cases, don't document UI piece by piece.
- Keep procedures to 5-9 steps.
- Navigate to apps/pages using solution-agnostic patterns with the global search field.
- Use correct prepositions: "in" a field/menu/dialog, "on" a page/tab, "from" a list.
