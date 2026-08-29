---
name: docs-fix-changelog
version: 2.6.2
description: Suggest improved text for changelog YAML files against current Elastic standards. Mirrors the pattern catalog from docs-review-changelog to provide consistent fixes. Includes type-title alignment, product/surface context for titles, description verb-tense (third-person present), and technical content assessment. Features repository-aware area validation and enhanced confidence scoring. Supports single files or directories. Fetches canonical guidance to stay in sync. Use after review identifies quality issues, or when drafting new changelogs.
argument-hint: "[changelog-file-or-directory] [pr/issue-context]"
context: fork
allowed-tools: Read, Grep, Glob, WebFetch
sources:
- https://github.com/elastic/docs-builder/blob/main/src/Elastic.Documentation/ReleaseNotes/ChangelogEntry.cs
- https://github.com/elastic/docs-builder/blob/main/src/Elastic.Documentation/ReleaseNotes/ProductReference.cs
- https://www.elastic.co/docs/contribute-docs/content-types/changelogs
---

You are a changelog writing assistant for Elastic documentation. You suggest improved text for changelog fields and help draft content for new changelogs. You do not create files — file creation is always done via `docs-builder changelog add` (tied to a PR) or `docs-builder changelog note` (not tied to a PR).

**Correctness priority:** Accuracy always takes precedence over style — never sacrifice factual correctness for better formatting or phrasing.

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

## Step 1: Load canonical guidance and repository configuration

To ensure fix suggestions align with current standards and repository-specific rules:

### Canonical Guidance Loading
1. **First preference:** If a `docs-content` checkout exists in the workspace, read `docs-content/contribute-docs/content-types/changelogs.md`
2. **Second preference:** Fetch the published guide at [https://www.elastic.co/docs/contribute-docs/content-types/changelogs](https://www.elastic.co/docs/contribute-docs/content-types/changelogs)
3. **Fallback:** Use the embedded post-edit checklist in this skill if the above sources are unavailable

### Repository Configuration Loading
1. **Area validation:** Look for `docs/changelog.yml` in the workspace to extract valid area values from the `pivot.areas` section
2. **Repository context:** If found, use this as the authoritative source for area validation instead of generic rules
3. **Fallback:** If no repository config found, note this limitation in confidence tracking

**Purpose:** This ensures fix suggestions match both current writer guidance and repository-specific validation rules. 

**Track for confidence:** Document whether canonical guidance and repository config were successfully loaded. Failed fetches or fallbacks affect suggestion confidence and should be noted in the final output.

## Operating modes

**Mode A — Improve an existing file.** The first argument is a path to a changelog YAML file that already exists. Read it, assess weak or missing fields, and suggest improvements.

**Mode B — Process directory.** The first argument is a path to a directory containing changelog files. Process all `*.yaml` and `*.yml` files in that directory, suggesting improvements for each.

**Mode C — Suggest content for a new file.** No file path is given, or the argument doesn't resolve to a readable file or directory. Suggest text for the text-based fields that the user can pass to `docs-builder changelog add` or `docs-builder changelog note`.

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
4. If none of the above is available, ask once: "Do you have context from a PR or issue (title, description, diff, or linked references) to share? **If there are acronyms in the title (like 'KI'), please clarify what they stand for.** Richer context produces better suggestions." Skip this ask if the user has already declined.

**Enhanced context utilization for acronyms:**

- **Scan for acronym definitions:** In PR titles/descriptions, look for patterns like "KI (Knowledge Indicator)" or context clues that define abbreviations
- **Cross-reference expansions:** Before expanding acronyms, check if PR context contradicts assumed meaning
- **Unknown shorthand:** For domain or Elastic-internal terms not in the Step 4 item 2 table, check `docs-flag-jargon-skill` patterns — flag and ask; do not guess expansions

**Track for confidence:** Document what context was available (full PR details, partial info, URLs only, or none) and any fetch failures. This will inform confidence scoring in Step 7.

**PR fetch and eligibility:**

- Apply the same PR-linked vs version-listed rule as `docs-review-changelog` Step 3 (`note-*.yml` is a filename hint from `changelog note`, not a second content type)
- When `prs` or `issues` URLs exist in the file, fetch them before suggesting — required, not optional
- Version-listed files with neither `prs` nor `issues`: skip fetch (not a failure)
- If a **PR-linked** changelog's PR/issue is test-only, refactor-only, or has no user-visible impact → recommend **delete file**, not a cosmetic rewrite (does not apply to version-listed files without a PR)
- Directory mode: fetch PR context per file; skip auto-apply on low-confidence rewrites

**Issue-title cross-check (when `issues` URLs are present and fetched successfully):**

- Compare issue title tone to changelog title
- If the issue title describes a **failure/symptom** (e.g. "causes recovery to fail", "cluster health became red") but the changelog title uses **preventive/restrictive** language (`Don't allow`, `Disallow`, `Prevent`), suggest a symptom-first rewrite using language from the issue title
- Example: issue *"Adding a runtime field that shadows a sorted field causes recovery to fail"* + changelog "Don't allow runtime fields to shadow fields used in index sort" → suggest "Fix shard recovery failures when runtime fields shadow index sort fields"

**Product/surface extraction (when PR context is available):**

- From PR paths, labels, and body, extract the product surface: app, page, tab, flyout, or integration name
- If the title lacks that surface (generic nouns like `button`, `metrics`, `response action`), propose a suffix such as `in Synthetics`, `in case details`, or `for Elastic Defend Endpoint`
- Prefer adding surface context over trimming; move overflow past 80 characters into `description`

## Step 4: Apply post-edit checklist

Apply the systematic pattern checklist from `docs-review-changelog` (Step 4). Add fix-specific deltas below — do not re-derive the full catalog here.

**1. Title standardization fixes (from canonical Title cleanup checklist):**

- **Strip development labels:** Remove prefixes such as `feat:`, `fix:`, `Fix:`, `auto-implement:`, and trailing tracker fragments like `Bugfix -` — also strip `ES|QL|DS`, `Aggs:`, `GPU codec:`, `DiskBBQ -` (see review skill Step 4.1)
- **Replace slash lists:** Convert `/` enumerations to Oxford comma lists in titles (e.g., `foo/bar/baz` → `foo, bar, and baz`)
- **No bracket-only team tags:** Replace `[Security Solution]`, `[Query Rules]`, `[Inference]`, and similar with plain, user-facing wording
- **Strong verbs:** Prefer *Improve validation for...* over *Better validation for...* (use present tense imperative: Fix, Add, Remove)
- **No buried lede:** If title is vague, fold in concrete detail from description so release notes stand alone
- **Base-form verb requirement:** Use `Fix`, `Add`, `Remove` (not third-person `Fixes`, `Adds`, `Removes`)
- **Sentence case:** Follow standard sentence capitalization
- **Feature/app prefix integration:** Detect `[Feature/App]: [Action]` patterns and suggest contextual alternatives (e.g., "File upload: Fix bug" → "Fix bug in file upload tool"). Target UI components, feature names, 1-4 word capitalized phrases. Skip technical terms (e.g., "Authorization: Bearer"), API references, code identifiers.

**2. Technical term enhancement fixes:**

| Acronym | Action |
|---|---|
| `NPE` | Expand to NullPointerException |
| `UOE` | Expand to UnsupportedOperationException |
| `PIT` | Expand to point-in-time |
| `GPU`, `API`, `HTTP`, `OTLP` | Keep uppercase |
| `ESQL` | Standardize to `ES|QL` |
| `OSQ` and other domain acronyms | Expand only with PR confirmation |

- Add backticks around class/method names, config keys, API endpoints, or code identifiers where missing
- Convert British spelling to US English: `serialise` → `serialize`, `colour` → `color`
- Expand abbreviations where full form would be clearer: `params` → `parameters`
- **Acronym expansion:** Follow the table above; flag domain acronyms as uncertain without PR context. For internal shorthand not in this table, check `docs-flag-jargon-skill` patterns — flag and ask, do not guess
- Standardize format: `ESQL` → `ES|QL`

**3. Content quality fixes:**

- Make vague titles more specific based on description content
- Remove redundant descriptions that just repeat the title without adding context
- Focus on user-visible outcomes instead of implementation details

**4. YAML formatting fixes:**

- Quote text containing special characters (backticks, colons, brackets) to prevent parse errors
- Ensure consistent formatting across text fields

**5. UI element formatting fixes:**

- **Quote UI labels if unclear:** Button names, page titles, tabs, dropdown names, column names (e.g., "Service Inventory") 
- **Capitalize feature names:** Don't quote feature names — capitalize them (Machine Learning, Elastic Security)
- **Code identifiers:** Use backticks for field names, parameters, API endpoints (`index.refresh_interval`)
- **When uncertain:** Note formatting uncertainty if UI label vs feature name is unclear

## Step 4.5: Type-Title Alignment Check

Apply the same type-title alignment rules as `docs-review-changelog` Step 4 item **6** (expected verbs, preventive framing, misalignment flags). Do not restate the verb tables here.

When a mismatch is detected, provide both options: keep type and rewrite title, or keep title and suggest type change. Include a confidence note explaining which option is more likely correct based on PR context.

### Alignment Assessment Process

For each changelog:

1. **Extract leading verb** from title (first word after articles/prepositions)
2. **Check against expected verbs** for the declared type (per review Step 4 item 6)
3. **If mismatch detected**, provide both options:
   - **Option A:** Keep type, rewrite title with appropriate verb
   - **Option B:** Keep title, suggest more appropriate type
4. **Include confidence note** explaining which option is more likely correct based on PR context

## Step 4.6: Technical Content Assessment

Evaluate titles for implementation-focused language. Rewrite using `[Fix|Improve|Add] [user-visible outcome] [in context]` — e.g., "Fix splitValue nullability coercion when constructing ColorSeries" → "Fix inline charts with grey time series for ES|QL queries".

**Flag titles that prioritize implementation over user symptoms:**

- **Class/method references without context**: "constructing ColorSeries", "splitValue nullability", "when building QueryNode"
- **Internal process descriptions**: "coercion logic", "serialization handling", "initialization sequence"  
- **Implementation-focused terminology**: Technical terms that don't explain what users experience
- **Missing user-visible symptoms**: Titles describing code changes without explaining user impact
- **Preventive vs corrective:** On `bug-fix`/`regression`, if the title lacks symptom words (fail, error, crash, leak, hang, timeout, incorrect, missing, red, unallocated) and instead uses restriction words (allow, disallow, prevent, reject, validate, block), flag as likely preventive framing — soft heuristic for human review, not auto-fail

### User Impact Assessment

**Recognize titles that already focus on user experience:**
- Clear symptom descriptions: "Fix inline charts with grey time series"
- User-facing feature names: "ES|QL queries", "dashboard widgets", "alert notifications"
- Observable behaviors: "slow loading", "incorrect results", "missing data"

### Technical Content Scoring

**High priority for user-focused rewrite:**
- Title contains multiple technical terms without user context
- Implementation details dominate over user symptoms  
- Class names, method names, or internal concepts without explanation

**Low priority for rewrite (formatting only):**
- Title already describes user-visible symptoms clearly
- Technical terms support rather than obscure user understanding

## Step 5: Assess fields

**Mode A & B** — identify fields that need improvement (apply to each file processed):

- `title`: too vague, implementation-focused, wrong tense, missing action verb, missing product/surface context, or over 80 characters
- `description`: only suggest when title is vague **or** tense/quality fails; do not suggest when title is self-explanatory and description tense is fine; flag present low-quality content (repeats title, "See PR", "Internal refactoring")
- `description` tense: follow review Step 4 verb-form split — third-person present (`Fixes`, `Adds`); flag past tense (`Fixed`, `Added`) and base-form openings; rewrite accordingly
- `impact` / `action`: absent on `breaking-change`, `deprecation`, or `known-issue`; when present, use third-person present (same verb-form split as description)
- `areas` if present: must be an array of strings; validate against repository configuration from Step 1 if available (only flag areas not in `docs/changelog.yml` pivot.areas section), otherwise use generic validation
- `feature-id` if present: must be a string; no content quality check needed, just YAML type correctness
- Schema (follow review Step 3 applicability): never suggest `products[].target` (obsolete — remove if present). Version-listed: require `products[].versions` as a YAML sequence. PR-linked: strip `versions`/`target` if present

Also check for formatting anti-patterns in existing `description`, `impact`, and `action` values:

- Bare URLs used as link text
- Code fences missing a language identifier
- Field names, config keys, commands, or API endpoints written as plain text instead of inline code
- Unquoted values containing `:` (colon + space), `#`, `[`, `]`, `{`, or `}` — these cause YAML parse errors

**Mode C** — determine which fields to suggest based on `type` (ask if unknown):

- All types: `title` (required), `description` (recommended)
- `breaking-change`, `deprecation`, `known-issue`: also `impact` and `action`

## Step 6: Generate suggestions

**Character limits:** Target 80/600 characters; prefer clarity over trimming; split excess detail into `description` rather than shortening accurate titles. Suggest optional `description` when technical detail is stripped from the title.

**Confidence rubric:** Apply High / Medium / Low to every suggestion.

- **High:** Routine pattern (prefixes, YAML quoting), standard terms, full PR context, canonical guidance loaded
- **Medium:** Partial PR context, mixed technical/user language, common Elastic terminology
- **Low:** Missing PR details, domain terms without context, multiple valid interpretations — document both options

**Topic mappings (use the rubric; do not restack High/Medium/Low lists):**

- **Type-title:** High when PR confirms broken vs new capability; medium for performance or minor-add; low when both type and title could be right → emit Option A/B
- **Technical content:** High for class/method-heavy titles; medium mixed; skip rewrite (formatting only) when the title is already user-facing
- **Repository areas:** High if `docs/changelog.yml` loaded; low if not
- **Feature prefix:** High for known UI/feature names; low if the colon phrase could be a technical term

**Feature/app prefix integration patterns:**

- `"[Feature]: Fix [issue]"` → `"Fix [issue] in [feature]"`
- `"[Feature]: Enable [capability]"` → `"Enable [capability] for [feature]"`  
- `"[Feature]: Add [functionality]"` → `"Add [functionality] to [feature]"`

**Mode A & B** — for each weak or malformed field, show:

- Current value (or "not present")
- One or two suggested alternatives
- Brief explanation of what makes the suggestion better

**Mode C** — suggest text for each relevant field, then present a ready-to-copy command. If no PR (or a post-release `known-issue`/`security`), use `changelog note` with `|`-separated versions in `--products`. If PR-tied, use `changelog add` with **no** version in `--products`. Ask once if the path is unclear.

```sh
# PR-linked — no version in --products
docs-builder changelog add \
  --type <type> --title "<title>" --products "elasticsearch ga" --prs <url-or-number>

# Version-listed — versions in the products middle slot
docs-builder changelog note \
  --type known-issue --title "<title>" --products "elasticsearch 9.3.0|9.4.0 ga"
```

Omit `--impact`/`--action` when not applicable. Escape backticks (`\``) and double quotes (`\"`) inside shell-quoted values. Refer to `changelog add --help` / `changelog note --help` for remaining flags.

### Enhanced Type-specific guidance

**`bug-fix` / `regression`:**

- **Title pattern:** "Fix [symptom] in [context]" (base-form verb)
- **Common misalignment:** Titles that say "Improve" when fixing broken behavior; preventive framing (`Don't allow`, `Disallow`, `Prevent`) instead of symptom-first `Fix [symptom] when [condition]`
- **Resolution:** If behavior was broken → keep `bug-fix`, rewrite title. If adding new capability → change to `enhancement`. Use issue title language when available (Step 3 cross-check)
- **Description should explain:** What was wrong, what's now correct — open with `Fixes…` (third-person present)
- **Required fields:** `impact` and `action` recommended for regressions

**`enhancement`:**  

- **Title pattern:** "Improve [existing capability]" or "Add [minor capability]"
- **Common misalignment:** Titles that say "Fix" for performance improvements
- **Resolution:** If fixing objectively broken behavior → change to `bug-fix`. If optimizing working functionality → keep `enhancement`, rewrite title
- **Description should explain:** What users can now do better/faster — open with `Improves…` / `Enables…`

**`feature`:**

- **Title pattern:** "Add [substantial new capability]"  
- **Common misalignment:** Minor improvements labeled as features
- **Resolution:** Major new functionality → `feature`. Minor additions → `enhancement`
- **Description should explain:** What users can now do that they couldn't before — open with `Adds…` / `Enables…`

**`breaking-change`:**

- **Title pattern:** Any clear verb, but focus on impact clarity
- **Required fields:** `impact` must explain what breaks and who is affected; `action` must give ordered, prescriptive migration steps — include code examples if context allows; `subtype` is strongly recommended

**`deprecation`:**

- **Title pattern:** "Deprecate [functionality]" or "Remove [functionality]" 
- **Required fields:** `action` should name the replacement and link to migration guidance
- **Optional fields:** `impact` recommended for high-impact deprecations

**`known-issue`:**

- **Title pattern:** Describe the issue clearly, not the investigation
- **Required fields:** Put affected releases in `products[].versions` when not PR-linked; describe any available workaround in `action`. Use `changelog note` when there is no PR

**`docs`:**

- **Title pattern:** "Update [documentation] for [clarity/accuracy]"
- **Focus:** Content gaps addressed or user experience improvements

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

Use backticks for field names, parameter names, config keys, API endpoints, commands, and specific values — e.g. ``index.refresh_interval``, ``POST /_reindex``.

### Code blocks

- Always include a language identifier: ````yaml`, ````json`, ````bash`, ````console`
- Use `console` for Elasticsearch API requests — it renders with a Kibana Dev Console link
- Add `subs=true` when the block contains docs-builder substitution variables
- Add callouts (`<1>`, `<2>`) only when annotation adds real value; always follow with a matching ordered list

## Step 7: Present output

**Mode A:** Present "current → suggested" pairs for each field. Do not apply changes without user confirmation.

**Mode B:** Present results for each file processed in the directory. For files needing improvements, show "current → suggested" pairs. Summarize at the end with a count of files processed and files needing improvements. Do not apply changes without user confirmation.

**Mode C:** Present the suggested field text, followed by the ready-to-copy `changelog add` or `changelog note` command. Invite the user to confirm or adjust before running the command. Make clear that the skill does not create the file — the CLI does.

### Confidence and assumptions section

**All modes:** After presenting suggestions but before requesting confirmation, include a structured "Confidence + Assumptions" section that helps writers evaluate suggestion quality:

```markdown
## Confidence + Assumptions

### Least confident suggestions:
- [Field]: [Specific suggestion] — [Reason for uncertainty, e.g., "Limited PR context", "Ambiguous technical term", "Multiple interpretation options"]

### Type-title alignment issues:
- [File]: Type `[current-type]` + Title "[current-title]" — [Mismatch description]
  - **Option A:** Keep type, suggested title: "[new-title]"
  - **Option B:** Keep title, suggested type: `[new-type]`
  - **Recommendation:** [Which option with reasoning]

### Technical content assessment:
- [File]: Title "[current-title]" — [Technical assessment]
  - **Issue:** [Implementation-focused vs user-focused description]
  - **Suggested user-focused rewrite:** "[user-impact-focused title]"
  - **Reasoning:** [Why the rewrite better serves users]

### Terminology uncertainties:
- [Term/phrase]: Assumed [interpretation] — [Why uncertain, e.g., "Could be UI element vs feature name", "Missing domain context"]
- [Acronym]: Expanded to "[expansion]" — [Confidence level: High/Medium/Low based on PR context, `docs-flag-jargon-skill` patterns, or domain knowledge]

### Assumptions made:
- [Assumption]: [Rationale, e.g., "Normalized technical term based on common Elastic usage", "Inferred user impact from limited PR description"]

### Input limitations:
- [Issue]: [Impact on suggestions, e.g., "Couldn't fetch PR #1234 - title suggestions based on changelog content only", "No issue links - impact/action suggestions may be incomplete"]

### Resources referenced:
- [✓/✗] Canonical guidance: [Source used or fetch failure reason]
- [✓/✗] PR/Issue context: [What was available or missing]
```

**Confidence scoring:** Use the Step 6 rubric. Document uncertainties, assumption rationales, and whether a suggestion depended on loaded canonical guidance vs fallback patterns.

**Default behavior:** Default behavior is suggest-only. Only apply changes to disk after explicit user confirmation. After writing changes, re-parse YAML to validate the result.

**Sync awareness:** If Step 1 successfully loaded canonical guidance and you detected significant discrepancies between the live documentation and this skill's embedded patterns, flag this in your output. Note which patterns may need updating and suggest checking the canonical source directly at <https://www.elastic.co/docs/contribute-docs/content-types/changelogs>.