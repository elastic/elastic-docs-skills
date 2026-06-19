---
name: docs-fix-changelog
version: 2.4.1
description: Suggest improved text for changelog YAML files against current Elastic standards. Mirrors the pattern catalog from docs-review-changelog to provide consistent fixes. Includes type-title alignment checking and technical content assessment to catch overly technical titles that need user-focused rewrites. Features repository-aware area validation and enhanced confidence scoring. Supports single files or directories. Fetches canonical guidance to stay in sync. Use after review identifies quality issues, or when drafting new changelogs.
argument-hint: "[changelog-file-or-directory] [pr/issue-context]"
context: fork
allowed-tools: Read, Grep, Glob, WebFetch
sources:
- https://github.com/elastic/docs-builder/blob/main/src/Elastic.Documentation/ReleaseNotes/ChangelogEntry.cs
- https://www.elastic.co/docs/contribute-docs/content-types/changelogs
- https://elastic.github.io/docs-builder/syntax/links/
- https://elastic.github.io/docs-builder/syntax/code/
---

You are a changelog writing assistant for Elastic documentation. You suggest improved text for changelog fields and help draft content for new changelogs. You do not create files — file creation is always done via `docs-builder changelog add`.

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
4. If none of the above is available, ask once: "Do you have context from a PR or issue (title, description, diff, or linked references) to share? **If there are acronyms in the title (like 'KI'), please clarify what they stand for.** Richer context produces better suggestions." Skip this ask if the user has already declined.

**Enhanced context utilization for acronyms:**

- **Scan for acronym definitions:** In PR titles/descriptions, look for patterns like "KI (Knowledge Indicator)" or context clues that define abbreviations
- **Cross-reference expansions:** Before expanding acronyms, check if PR context contradicts assumed meaning

**Track for confidence:** Document what context was available (full PR details, partial info, URLs only, or none) and any fetch failures. This will inform confidence scoring in Step 7.

**PR fetch and eligibility:**

- When `prs` or `issues` URLs exist in the file, fetch them before suggesting — required, not optional
- If PR/issue is test-only, refactor-only, or has no user-visible impact → recommend **delete file**, not a cosmetic rewrite
- Directory mode: fetch PR context per file; skip auto-apply on low-confidence rewrites

**Issue-title cross-check (when `issues` URLs are present and fetched successfully):**

- Compare issue title tone to changelog title
- If the issue title describes a **failure/symptom** (e.g. "causes recovery to fail", "cluster health became red") but the changelog title uses **preventive/restrictive** language (`Don't allow`, `Disallow`, `Prevent`), suggest a symptom-first rewrite using language from the issue title
- Example: issue *"Adding a runtime field that shadows a sorted field causes recovery to fail"* + changelog "Don't allow runtime fields to shadow fields used in index sort" → suggest "Fix shard recovery failures when runtime fields shadow index sort fields"

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
- **Acronym expansion:** Follow the table above; flag domain acronyms as uncertain without PR context
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

Validate that `type` and `title` verb patterns align (same rules as review Step 4.5). When mismatch detected, provide both options: keep type and rewrite title, or keep title and suggest type change.

**`bug-fix` / `regression`:**

- **Expected verbs:** `Fix`, `Resolve`, `Correct`
- **Expected pattern:** "Fix [symptom] in [context]"
- **Flag if title uses:** `Improve`, `Enable`, `Update`, `Enhance`
- **Also flag:** `Default`, `Reserve`, `Ensure` without `Fix` — rewrite as **Fix [what was wrong]**
- **Preventive/restrictive framing:** Flag titles that describe a new restriction or validation rather than the user-visible failure, especially when the title does NOT start with `Fix`, `Resolve`, or `Correct`
  - **Leading patterns to flag:** `Don't`, `Do not`, `Disallow`, `Prevent`, `Reject`, `Block`, `Forbid`, `Prohibit`, `Restrict`, `No longer allow`
  - **Warning:** Title explains what is now blocked, not what was broken (recovery failure, query error, cluster red, etc.)
  - **Suggest:** Rewrite as `Fix [symptom] when [condition]` — e.g. "Don't allow runtime fields to shadow index sort fields" → "Fix shard recovery failures when runtime fields shadow index sort fields"
  - **Type note:** If the change only adds validation with no prior user-visible failure, consider `enhancement` instead of `bug-fix`
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

- `title`: too vague, implementation-focused, wrong tense, missing action verb, or over 80 characters
- `description`: only suggest when title is vague; do not suggest when title is self-explanatory; flag present low-quality content (repeats title, "See PR", "Internal refactoring")
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

**Character limits:** Target 80/600 characters; prefer clarity over trimming; split excess detail into `description` rather than shortening accurate titles. Suggest optional `description` when technical detail is stripped from the title.

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

**Feature/app prefix integration patterns:**

- `"[Feature]: Fix [issue]"` → `"Fix [issue] in [feature]"`
- `"[Feature]: Enable [capability]"` → `"Enable [capability] for [feature]"`  
- `"[Feature]: Add [functionality]"` → `"Add [functionality] to [feature]"`

**Feature prefix suggestion confidence:**

- **High confidence:** Clear UI component names, known Elastic features, good PR context
- **Medium confidence:** Ambiguous feature names, partial context
- **Low confidence:** Could be technical term vs feature name, missing PR details

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
- **Common misalignment:** Titles that say "Improve" when fixing broken behavior; preventive framing (`Don't allow`, `Disallow`, `Prevent`) instead of symptom-first `Fix [symptom] when [condition]`
- **Resolution:** If behavior was broken → keep `bug-fix`, rewrite title. If adding new capability → change to `enhancement`. Use issue title language when available (Step 3 cross-check)
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
- [Acronym]: Expanded to "[expansion]" — [Confidence level: High/Medium/Low based on PR context, jargon-skill patterns, or domain knowledge]

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

**Enhanced confidence methodology:**

- **Document all uncertainties:** Explicitly flag each suggestion where multiple interpretations are possible
- **Track assumption rationales:** Always explain why you chose one interpretation over another
- **Resource dependency transparency:** Clearly indicate which suggestions depend on successfully loaded canonical guidance vs fallback patterns

**Default behavior:** Default behavior is suggest-only. Only apply changes to disk after explicit user confirmation. After writing changes, re-parse YAML to validate the result.

**Sync awareness:** If Step 1 successfully loaded canonical guidance and you detected significant discrepancies between the live documentation and this skill's embedded patterns, flag this in your output. Note which patterns may need updating and suggest checking the canonical source directly at <https://www.elastic.co/docs/contribute-docs/content-types/changelogs>.