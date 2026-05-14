---
name: docs-fix-changelog
version: 2.3.0
description: Suggest improved text for changelog YAML files against current Elastic standards. Mirrors the pattern catalog from docs-review-changelog to provide consistent fixes. Includes type-title alignment checking and technical content assessment to catch overly technical titles that need user-focused rewrites. Features repository-aware area validation and enhanced confidence scoring. Supports single files or directories. Fetches canonical guidance to stay in sync. Use after review identifies quality issues, or when drafting new changelogs.
argument-hint: "[changelog-file-or-directory] [pr/issue-context]"
context: fork
allowed-tools: Read, Grep, Glob, WebFetch
sources:
- https://github.com/elastic/docs-builder/blob/main/src/Elastic.Documentation/ReleaseNotes/ChangelogEntry.cs
- https://www.elastic.co/docs/contribute-docs/content-types/changelogs
- https://elastic.github.io/docs-builder/syntax/links/
- https://elastic.github.io/docs-builder/syntax/code/



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

## Step 4.5: Type-Title Alignment Check

**Before generating suggestions**, validate that `type` and `title` verb patterns align. This catches systematic misclassifications where the content doesn't match the declared type.

### Type-Verb Alignment Rules

**`bug-fix` / `regression`:**

- **Expected verbs:** `Fix`, `Resolve`, `Correct`
- **Expected pattern:** "Fix [symptom] in [context]"
- **Flag if title uses:** `Improve`, `Enable`, `Update`, `Enhance`
- **Action:** Suggest either changing type to `enhancement` OR rewriting title to describe what was broken

**`enhancement`:**

- **Expected verbs:** `Improve`, `Update`, `Optimize`, `Enable`, `Expand`, `Enhance`
- **Expected pattern:** "Improve [capability] for [context]"  
- **Flag if title uses:** `Fix`, `Resolve`, `Correct`
- **Action:** Suggest either changing type to `bug-fix` OR rewriting title to focus on improvement/capability

**`feature`:**

- **Expected verbs:** `Add`, `Introduce`, `Enable`, `Support`  
- **Expected pattern:** "Add [new capability] for [users]"
- **Flag if title uses:** `Fix`, `Improve` (unless truly new)
- **Action:** Major new functionality → `feature`. Minor additions → `enhancement`

**`docs`:**

- **Expected verbs:** `Update`, `Add`, `Clarify`, `Document`
- **Expected pattern:** "Update [documentation] for [clarity/accuracy]"

**`breaking-change` / `deprecation` / `known-issue` / `security`:**

- **Any appropriate verb** but should align with the actual change nature
- **Focus on clarity** rather than strict verb patterns

### Alignment Assessment Process

For each changelog:

1. **Extract leading verb** from title (first word after articles/prepositions)
2. **Check against expected verbs** for the declared type
3. **If mismatch detected**, provide both options:
   - **Option A:** Keep type, rewrite title with appropriate verb
   - **Option B:** Keep title, suggest more appropriate type
4. **Include confidence note** explaining which option is more likely correct based on PR context

## Step 4.6: Technical Content Assessment

**Before field-level assessment**, evaluate titles for overly technical language that focuses on implementation rather than user impact.

### Technical Jargon Detection

**Flag titles that prioritize implementation over user symptoms:**

- **Class/method references without context**: "constructing ColorSeries", "splitValue nullability", "when building QueryNode"
- **Internal process descriptions**: "coercion logic", "serialization handling", "initialization sequence"  
- **Implementation-focused terminology**: Technical terms that don't explain what users experience
- **Missing user-visible symptoms**: Titles describing code changes without explaining user impact

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
- Example: "Fix splitValue nullability coercion when constructing ColorSeries" → Should suggest user-focused alternative

**Low priority for rewrite (formatting only):**
- Title already describes user-visible symptoms clearly
- Technical terms support rather than obscure user understanding
- Example: "Fix inline charts with grey time series for ES|QL queries" → Minor formatting only

## Step 5: Assess fields

**Mode A & B** — identify fields that need improvement (apply to each file processed):

- `title`: too vague, implementation-focused, wrong tense, missing action verb, or over 80 characters
- `description`: absent but would add value, or present but low quality (repeats title, says "See PR", says "Internal refactoring")
- `impact` / `action`: absent on `breaking-change`, `deprecation`, or `known-issue`
- `areas` if present: must be an array of strings; validate against repository configuration from Step 1 if available (only flag areas not in `docs/changelog.yml` pivot.areas section), otherwise use generic validation
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

**Type-Title Alignment Confidence:**

- **High confidence type corrections:**
  - Clear functional behavior (Fix broken → `bug-fix`)
  - Clear new capability (Add substantial → `feature`)  
  - PR context confirms the classification

- **Medium confidence:**
  - Performance improvements (could be `enhancement` or `bug-fix` depending on whether previous performance was "broken")
  - Minor additions (could be `enhancement` or `feature` depending on scope)

- **Low confidence - provide both options:**
  - Ambiguous PR context about whether behavior was broken or just suboptimal
  - Edge cases between types (e.g., "fixing" by adding a missing capability)

**Technical Content Assessment Confidence:**

- **High confidence user-impact rewrites:**
  - Titles heavy in class names, method names, or implementation details without user context
  - Multiple technical terms that don't explain user symptoms
  - Clear implementation focus over user experience (e.g., "Fix splitValue nullability coercion when constructing ColorSeries")

- **Medium confidence:**
  - Technical terms mixed with some user-facing language
  - Partial user context but still implementation-heavy

- **Low priority formatting-only suggestions:**
  - Titles already focused on user symptoms and impact
  - Technical terms support rather than obscure user understanding
  - Clear user-facing language with minimal technical jargon

**Repository Validation Confidence:**

- **High confidence:** Repository configuration loaded successfully, using authoritative area validation
- **Medium confidence:** Repository config partially available or unclear
- **Low confidence:** No repository configuration found, using generic validation rules

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

Omit `--impact` and `--action` when not applicable to the type. Note that inside shell-quoted values, backticks must be escaped with a backslash (`\``) and double quotes must be escaped (`\"`).

Remind the user that `--products`, `--prs`, `--issues`, and other non-text options must be provided separately. Refer them to `docs-builder changelog add --help` for the full list.

### Enhanced Type-specific guidance

**`bug-fix` / `regression`:**

- **Title pattern:** "Fix [symptom] in [context]" (base-form verb)
- **Common misalignment:** Titles that say "Improve" when fixing broken behavior
- **Resolution:** If behavior was broken → keep `bug-fix`, rewrite title. If adding new capability → change to `enhancement`
- **Description should explain:** What was wrong, what's now correct
- **Required fields:** `impact` and `action` recommended for regressions

**`enhancement`:**  

- **Title pattern:** "Improve [existing capability]" or "Add [minor capability]"
- **Common misalignment:** Titles that say "Fix" for performance improvements
- **Resolution:** If fixing objectively broken behavior → change to `bug-fix`. If optimizing working functionality → keep `enhancement`, rewrite title
- **Description should explain:** What users can now do better/faster

**`feature`:**

- **Title pattern:** "Add [substantial new capability]"  
- **Common misalignment:** Minor improvements labeled as features
- **Resolution:** Major new functionality → `feature`. Minor additions → `enhancement`
- **Description should explain:** What users can now do that they couldn't before

**`breaking-change`:**

- **Title pattern:** Any clear verb, but focus on impact clarity
- **Required fields:** `impact` must explain what breaks and who is affected; `action` must give ordered, prescriptive migration steps — include code examples if context allows; `subtype` is strongly recommended

**`deprecation`:**

- **Title pattern:** "Deprecate [functionality]" or "Remove [functionality]" 
- **Required fields:** `action` should name the replacement and link to migration guidance
- **Optional fields:** `impact` recommended for high-impact deprecations

**`known-issue`:**

- **Title pattern:** Describe the issue clearly, not the investigation
- **Required fields:** Include all affected versions and contexts; describe any available workaround in `action`

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

**Mode C:** Present the suggested field text, followed by the ready-to-copy `docs-builder changelog add` command. Invite the user to confirm or adjust before running the command. Make clear that the skill does not create the file — `changelog add` does.

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