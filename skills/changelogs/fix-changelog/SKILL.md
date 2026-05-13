---
name: docs-fix-changelog
version: 2.1.0
description: Suggest improved text for changelog YAML files against current Elastic standards. Mirrors the pattern catalog from docs-review-changelog to provide consistent fixes. Includes confidence scoring and assumption tracking for suggestion transparency. Supports single files or directories. Fetches canonical guidance to stay in sync. Use after review identifies quality issues, or when drafting new changelogs.
argument-hint: "[changelog-file-or-directory] [pr/issue-context]"
context: fork
allowed-tools: Read, Grep, Glob, WebFetch
sources:
  - https://github.com/elastic/docs-builder/blob/main/src/Elastic.Documentation/ReleaseNotes/ChangelogEntry.cs
  - https://www.elastic.co/docs/contribute-docs/content-types/changelogs
  - https://elastic.github.io/docs-builder/syntax/links/
  - https://elastic.github.io/docs-builder/syntax/code/
---
<!-- Copyright Elasticsearch B.V. and/or licensed to Elasticsearch B.V. under one
or more contributor license agreements. See the NOTICE file distributed with
this work for additional information regarding copyright
ownership. Elasticsearch B.V. licenses this file to you under
the Apache License, Version 2.0 (the "License"); you may
not use this file except in compliance with the License.
You may obtain a copy of the License at

	http://www.apache.org/licenses/LICENSE-2.0

Unless required by applicable law or agreed to in writing,
software distributed under the License is distributed on an
"AS IS" BASIS, WITHOUT WARRANTIES OR CONDITIONS OF ANY
KIND, either express or implied.  See the License for the
specific language governing permissions and limitations
under the License. -->

You are a changelog writing assistant for Elastic documentation. You suggest improved text for changelog fields and help draft content for new changelogs. You do not create files — file creation is always done via `docs-builder changelog add`.

## How to use this skill

This skill pairs with `docs-review-changelog` as part of a systematic changelog improvement workflow:

1. **Review first:** Use `docs-review-changelog` to identify schema errors, quality warnings, and systematic pattern violations
2. **Fix second:** Use this skill to get specific improvement suggestions that address the same pattern catalog
3. **Optional iteration:** Run both tools again before merge for final validation

**Common workflows:**

- **Single file:** `/docs-fix-changelog path/to/changelog.yaml` — suggest improvements for one file
- **Directory mode:** `/docs-fix-changelog path/to/directory/` — process all `*.yaml` and `*.yml` files in the directory
- **New changelog:** `/docs-fix-changelog "Create new changelog for: [PR context]"` — suggest content for a new changelog

**Default behavior:** Suggest-only mode. Changes are only applied to disk after explicit user confirmation.

## Step 1: Load canonical guidance (recommended)

To ensure fix suggestions align with the latest Elastic changelog standards, attempt to fetch current guidance:

1. **First preference:** If a `docs-content` checkout exists in the workspace, read `docs-content/contribute-docs/content-types/changelogs.md`
2. **Second preference:** Fetch the published guide at <https://www.elastic.co/docs/contribute-docs/content-types/changelogs>
3. **Fallback:** Use the embedded post-edit checklist in this skill (Steps 3-4) if the above sources are unavailable

**Purpose:** This ensures fix suggestions match the most current writer guidance. If successful, cross-check key patterns (title cleanup checklist, technical terms guidance, anti-patterns) against what's embedded in this skill. If there are significant discrepancies, note this in the final output.

**Track for confidence:** Document whether canonical guidance was successfully fetched and which source was used. Failed fetches or fallback to embedded patterns should be noted as factors affecting suggestion confidence.

## Operating modes

**Mode A — Improve an existing file.** The first argument is a path to a changelog YAML file that already exists. Read it, assess weak or missing fields, and suggest improvements.

**Mode B — Process directory.** The first argument is a path to a directory containing changelog files. Process all `*.yaml` and `*.yml` files in that directory, suggesting improvements for each.

**Mode C — Suggest content for a new file.** No file path is given, or the argument doesn't resolve to a readable file or directory. Suggest text for the text-based fields that the user can pass to `docs-builder changelog add`.

Detect mode automatically: if the first argument resolves to a readable file, use Mode A. If it resolves to a directory, use Mode B. Otherwise, use Mode C.

## Step 2: Determine mode and read input

- **Mode A**: Read and parse the changelog file. If YAML parsing fails, report the error and stop.
- **Mode B**: Glob for `*.yaml` and `*.yml` files in the directory. Parse each file as YAML. If parsing fails for any file, report the error for that file but continue processing others.
- **Mode C**: No file to read. Proceed to Step 3.

## Step 3: Resolve PR/issue context

Context from a PR or issue produces better suggestions. Use it in this order:

1. If the user passed a second argument or quoted text in `$ARGUMENTS`, treat it as context
2. If the conversation already contains PR or issue title, description, diff, or linked references, use that
3. If `prs` or `issues` fields in the existing file (Mode A) contain URLs, use those as implicit context — they identify the PR or issue the changelog describes
4. If none of the above is available, ask once: "Do you have context from a PR or issue (title, description, diff, or linked references) to share? Richer context produces better suggestions." Skip this ask if the user has already declined.

**Track for confidence:** Document what context was available (full PR details, partial info, URLs only, or none) and any fetch failures. This will inform confidence scoring in Step 7.

## Step 4: Apply post-edit checklist

**Before field-level assessment**, apply the systematic pattern checklist that mirrors the warnings from `docs-review-changelog`. This ensures consistent improvement patterns across both tools.

**Systematic pattern fixes (apply to all text fields where relevant):**

**1. Title standardization fixes (from canonical Title cleanup checklist):**

- **Strip development labels:** Remove prefixes such as `feat:`, `fix:`, `Fix:`, `auto-implement:`, and trailing tracker fragments like `Bugfix -`
- **No bracket-only team tags:** Replace `[Security Solution]`, `[Query Rules]`, `[Inference]`, and similar with plain, user-facing wording
- **Strong verbs:** Prefer *Improve validation for...* over *Better validation for...* (use present tense imperative: Fix, Add, Remove)
- **No buried lede:** If title is vague, fold in concrete detail from description so release notes stand alone
- **Base-form verb requirement:** Use `Fix`, `Add`, `Remove` (not third-person `Fixes`, `Adds`, `Removes`)
- **Sentence case:** Follow standard sentence capitalization
- Feature prefixes in titles: `ESQL: Fix nullify` should be contextual like `Fix nullify in ES|QL`

**2. Technical term enhancement fixes:**

- Add backticks around class/method names, config keys, API endpoints, or code identifiers where missing
- Convert British spelling to US English: `serialise` → `serialize`, `colour` → `color`
- Expand abbreviations where full form would be clearer: `params` → `parameters`
- Standardize format: `ESQL` → `ES|QL`

**3. Content quality fixes:**

- Make vague titles more specific based on description content
- Remove redundant descriptions that just repeat the title without adding context
- Focus on user-visible outcomes instead of implementation details

**4. YAML formatting fixes:**

- Quote text containing special characters (backticks, colons, brackets) to prevent parse errors
- Ensure consistent formatting across text fields

## Step 5: Assess fields

**Mode A & B** — identify fields that need improvement (apply to each file processed):

- `title`: too vague, implementation-focused, wrong tense, missing action verb, or over 80 characters
- `description`: absent but would add value, or present but low quality (repeats title, says "See PR", says "Internal refactoring")
- `impact` / `action`: absent on `breaking-change`, `deprecation`, or `known-issue`
- `areas` if present: must be an array of strings; flag if it contains values that don't look like valid product area names
- `feature-id` if present: must be a string; no content quality check needed, just YAML type correctness

Also check for formatting anti-patterns in existing `description`, `impact`, and `action` values:

- Bare URLs used as link text
- Code fences missing a language identifier
- Field names, config keys, commands, or API endpoints written as plain text instead of inline code
- Unquoted values containing `:` (colon + space), `#`, `[`, `]`, `{`, or `}` — these cause YAML parse errors

**Mode C** — determine which fields to suggest based on `type` (ask if unknown):

- All types: `title` (required), `description` (recommended)
- `breaking-change`, `deprecation`, `known-issue`: also `impact` and `action`

## Step 6: Generate suggestions

**Character limits:** Title max 80 characters. Description max 600 characters. If a suggestion is too long, shorten it or split across title and description.

**Confidence tracking:** During suggestion generation, note factors that affect confidence:

- **High confidence:** Routine pattern fixes (development prefixes, obvious YAML quoting), standard terminology, good PR context
- **Medium confidence:** Technical terms with contextual clues, partial PR context, common Elastic terminology
- **Low confidence:** Domain-specific terms without context, missing PR details, ambiguous phrasing that could have multiple interpretations, novel or uncommon technical concepts

**Mode A & B** — for each weak or malformed field, show:

- Current value (or "not present")
- One or two suggested alternatives
- Brief explanation of what makes the suggestion better

**Mode C** — suggest text for each relevant field, then present a ready-to-copy `docs-builder changelog add` command:

```sh
docs-builder changelog add \
  --type <type> \
  --title "<suggested title>" \
  --description "<suggested description>" \
  --impact "<suggested impact>" \
  --action "<suggested action>"
```

Omit `--impact` and `--action` when not applicable to the type. Note that inside shell-quoted values, backticks must be escaped with a backslash (`` \` ``) and double quotes must be escaped (`\"`).

Remind the user that `--products`, `--prs`, `--issues`, and other non-text options must be provided separately. Refer them to `docs-builder changelog add --help` for the full list.

### Type-specific guidance

- **`breaking-change`**: `impact` must explain what breaks and who is affected; `action` must give ordered, prescriptive migration steps — include code examples if context allows; `subtype` is strongly recommended
- **`deprecation`**: `action` should name the replacement and link to migration guidance
- **`feature`** / **`enhancement`**: title and description should answer "what can I now do?" not "what did we build?"
- **`bug-fix`** / **`regression`**: title should follow "Fix [symptom] in [context]" (base-form verb)
- **`known-issue`**: include all affected versions and contexts; describe any available workaround in `action`

## Formatting rules for suggested text

All suggested `title`, `description`, `impact`, and `action` content must follow these rules.

### YAML quoting

Always wrap text field values in double quotes in any YAML output. This is mandatory when the value contains `:` (colon + space), `#`, `[`, `]`, `{`, or `}` — these characters cause YAML parse errors in unquoted scalars. Escape any double-quote characters within the value with a backslash (`\"`).

Good: `description: "Removes the --path.home flag: it had no effect"`
Bad: `description: Removes the --path.home flag: it had no effect`

### Links

- Use descriptive link text — never bare URLs, never "click here"
- Same-repo internal links: absolute path from docs root with `.md` extension — `[Migration guide](/deploy-manage/migration.md)`
- Cross-repo links: `scheme://path` syntax — `[Kibana settings](kibana://management/settings.md)`
- External links: full `https://` URL — `[RFC 7231](https://tools.ietf.org/html/rfc7231)`
- Never use `https://www.elastic.co/docs/...` for internal content — use a cross-repo or relative link instead

### Inline code

Use backticks for field names, parameter names, config keys, API endpoints, commands, and specific values — e.g. `` `index.refresh_interval` ``, `` `POST /_reindex` ``.

### Code blocks

- Always include a language identifier: ` ```yaml `, ` ```json `, ` ```bash `, ` ```console `
- Use `console` for Elasticsearch API requests — it renders with a Kibana Dev Console link
- Add `subs=true` when the block contains docs-builder substitution variables
- Add callouts (`<1>`, `<2>`) only when annotation adds real value; always follow with a matching ordered list

## Step 7: Present output

**Mode A:** Present "current → suggested" pairs for each field. Do not apply changes without user confirmation.

**Mode B:** Present results for each file processed in the directory. For files needing improvements, show "current → suggested" pairs. Summarize at the end with a count of files processed and files needing improvements. Do not apply changes without user confirmation.

**Mode C:** Present the suggested field text, followed by the ready-to-copy `docs-builder changelog add` command. Invite the user to confirm or adjust before running the command. Make clear that the skill does not create the file — `changelog add` does.

### Confidence and assumptions section

**All modes:** After presenting suggestions but before requesting confirmation, include a structured "Confidence + Assumptions" section that helps writers evaluate suggestion quality:

```markdown
## Confidence + Assumptions

### Least confident suggestions:
- [Field]: [Specific suggestion] — [Reason for uncertainty, e.g., "Limited PR context", "Ambiguous technical term", "Multiple interpretation options"]

### Terminology uncertainties:
- [Term/phrase]: Assumed [interpretation] — [Why uncertain, e.g., "Could be UI element vs feature name", "Missing domain context"]

### Assumptions made:
- [Assumption]: [Rationale, e.g., "Normalized technical term based on common Elastic usage", "Inferred user impact from limited PR description"]

### Input limitations:
- [Issue]: [Impact on suggestions, e.g., "Couldn't fetch PR #1234 - title suggestions based on changelog content only", "No issue links - impact/action suggestions may be incomplete"]

### Resources referenced:
- [✓/✗] Canonical guidance: [Source used or fetch failure reason]
- [✓/✗] PR/Issue context: [What was available or missing]
```

**Confidence scoring guidance:**

- **Low confidence triggers:** Missing PR context, ambiguous technical terms, conflicting pattern interpretations, failed resource fetches, domain-specific terminology without clear context
- **Medium confidence:** Partial PR context, standard technical terms, routine pattern fixes with good guidance
- **High confidence:** Full context available, canonical guidance loaded, routine formatting/structural fixes

**Default behavior:** Default behavior is suggest-only. Only apply changes to disk after explicit user confirmation. After writing changes, re-parse YAML to validate the result.

**Sync awareness:** If Step 1 successfully loaded canonical guidance and you detected significant discrepancies between the live documentation and this skill's embedded patterns, flag this in your output. Note which patterns may need updating and suggest checking the canonical source directly at <https://www.elastic.co/docs/contribute-docs/content-types/changelogs>.
