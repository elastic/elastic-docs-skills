---
name: docs-changelog-tool
version: 1.0.2
description: Use before adding CLI options or profile fields, changing filter mechanisms, modifying the entry or bundle schema, updating the {changelog} directive or changelog render, or adding and modifying tests in docs-builder changelog commands.
allowed-tools: Read, Grep, Glob, Edit, Bash
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

You are a changelog feature development specialist for docs-builder. Your job is to ensure that changes to changelog commands remain internally consistent, schema-stable, and fully tested and documented.

## Breaking change identification and planning

**Before modifying any filter/precedence logic**: Run this systematic assessment to identify breaking changes:

### 1. Behavior change detection
- Document current behavior for all edge cases (empty products, disjoint contexts, partial rules)
- Document proposed behavior for same cases  
- Identify any cases where output changes → breaking change
- Test existing configurations with both old and new behavior

### 2. Configuration impact analysis  
- Test existing partial configurations (per-product rules missing some dimensions)
- Identify configs that rely on current inheritance/fallback behavior
- Document migration path for affected configurations
- Assess complexity of user migration required

### 3. User impact evaluation
- Assess if changelog tooling is in production use across organization
- Determine if breaking changes are acceptable given adoption level
- Plan migration documentation, warnings, and communication strategy
- Consider phased rollout or feature flags for major changes

**Breaking change is acceptable when**: Tooling not in broad production use AND new behavior is more logical/consistent AND migration path is straightforward.

**Required for all breaking changes**: 
- Comprehensive before/after behavior documentation  
- Migration examples showing old vs new configuration patterns
- Test suite covering both legacy and new behavior during transition

## Architecture map

Key files and their roles:

```
ChangelogCommand.cs              — CLI entry points; mode detection; mutual-exclusivity guards
ProfileFilterResolver.cs         — maps (profile + argument) → concrete filter
ChangelogBundlingService.cs      — bundles filtered changelogs; applies rules.bundle via GetBlockerForEntry → ResolveBlocker
ChangelogRemoveService.cs        — removes filtered changelogs; checks bundle deps
ChangelogConfigurationLoader.cs  — parses changelog.yml; forces Publish = null and emits deprecation warning
BundleConfiguration.cs           — model: directory, outputDirectory, resolve, repo, owner, profiles
ChangelogConfigurationYaml.cs    — internal YAML DTOs (always mirror model changes here)
PublishBlockerExtensions.cs      — shared ResolveBlocker helper; intersection + alphabetical first-match algorithm
ChangelogRenderUtilities.cs      — render-side ShouldHideEntry (feature-ID hiding only; no publish rules applied)
ChangelogRenderingService.cs     — validates bundles, resolves entries, merges hide-features, renders output
ChangelogBlock.cs                — {changelog} directive; discovers and merges pre-bundled entries; no rule resolution
BlockConfiguration.cs            — RulesConfiguration / BundleRules / PublishRules models
```

## Command roles and synchronization

Each command has a distinct role. Changes to one often require parallel changes to others:

| Command | Role | Must stay in sync with |
|---------|------|------------------------|
| `changelog add` | Creates a single changelog entry file from CLI args or a GitHub PR/issue | `changelog gh-release` (same creation logic), validation rules |
| `changelog bundle` | Bundles filtered entries into a bundle YAML file; applies `rules.bundle` filtering | `changelog remove` (same filters), `changelog gh-release` (bundle step) |
| `changelog remove` | Removes entry files using the same filters as `bundle` | `changelog bundle` (filter parity) |
| `changelog gh-release` | Does `add` + `bundle` in one step from a GitHub release | `changelog add` and `changelog bundle` (must stay functionally equivalent) |
| `changelog render` | Renders pre-bundled entries to Markdown or Asciidoc (legacy ES v8 docs); hides entries by feature ID only | `{changelog}` directive (bundle schema, rendered output format) |
| `changelog bundle-amend` | Appends entries to an existing bundle immutably | Bundle schema, `{changelog}` directive |
| `changelog init` | Scaffolds `changelog.yml`; expands as onboarding needs grow | `changelog.example.yml` (must always reflect the latest defaults) |
| `changelog evaluate-pr` | (CI) Evaluates a PR for changelog generation eligibility using config, PR metadata, and `rules.create` | `changelog add` (same creation logic triggered by the evaluation result) |

### Key synchronization rules

- Entries created by `changelog add` (CLI-only) and entries created via GitHub PR/issue fetch must be indistinguishable — same fields, same validation, same downstream behavior.
- `changelog gh-release` must produce output equivalent to running `changelog add` (per PR) followed by `changelog bundle`. Any change to either of those commands must be evaluated for `gh-release` too.
- `changelog render` and the `{changelog}` directive both consume pre-bundled entries and do **not** apply rule resolution at runtime. All type/area/product filtering happens at bundle time via `rules.bundle` in `ChangelogBundlingService`. The two differ in their own display options (`changelog render`: `--hide-features`, `--subsections`, `--file-type`; directive: `:type:`, `:subsections:`). Keep them in sync for **bundle schema changes and rendered output format**; `render` must be kept in parallel for as long as Asciidoc/Markdown output is needed for legacy docs.

### Filter parity checklist (bundle and remove)

When implementing a new filter mechanism (for example, `source: github_release`):

1. Confirm that both `changelog bundle` and `changelog remove` support it with identical validation logic and error messages.
2. Confirm that all forbidden-option guards in profile mode cover the new mechanism in both commands.
3. Confirm that `ProfileFilterResolver` passes the result through to both `ChangelogBundlingService` and `ChangelogRemoveService` correctly.

## Rule resolution for filter/blocking logic

### `rules.bundle` vs `rules.publish`

`rules.bundle` is the only supported place for type/area/product filtering. `rules.publish` is deprecated: the loader emits a deprecation warning and forces `Publish = null`, so it is never applied anywhere at runtime. All type/area filtering must be moved to `rules.bundle`.

- `rules.bundle`: applied during `changelog bundle` and `changelog gh-release` via `ChangelogBundlingService.ApplyBundleFilter` → `GetBlockerForEntry` → `PublishBlockerExtensions.ResolveBlocker`.
- `rules.publish`: deprecated; accepted in YAML only to emit a warning, then discarded.
- `changelog render` and the `{changelog}` directive: neither applies rule resolution. Both consume pre-filtered bundles.

### Per-product rule resolution for multi-product entries

When an entry belongs to more than one product and per-product overrides are configured in `rules.bundle.products`, the applicable rule is chosen by the *intersection + alphabetical first-match* algorithm in `PublishBlockerExtensions.ResolveBlocker`:

1. Compute intersection of context IDs and the entry's own products.
2. Sort the intersection alphabetically (case-insensitive, ascending).
3. Return the rule for the first ID in the sorted intersection that has a configured override.
4. If the intersection is empty (entry products are disjoint from context), fall back to the entry's own products sorted alphabetically, then the global blocker.

**Inheritance source validation**: When debugging per-context rule issues, verify that each field in `BundlePerProductRule` inherits from the correct config level:
- Product filters (`include_products`, `exclude_products`, `match_products`) inherit from bundle level (`rules.bundle.*`)
- Type/area filters (`exclude_types`, `include_areas`, etc.) inherit from bundle level (`rules.bundle.*`)
- **NOT** from global level (`rules.*`) — this was the source of the `match_products` inheritance bug

The context differs by caller:

| Caller | Context IDs |
|--------|-------------|
| `changelog bundle` | `--output-products` when set; otherwise the entry's own products |
| `changelog gh-release` | same as `changelog bundle` |
| `changelog render` | does not call `ResolveBlocker`; feature-ID hiding only |
| `{changelog}` directive | does not call `ResolveBlocker`; feature-ID hiding from bundle metadata only |

Behavior table (mirrors `docs/contribute/changelog.md#changelog-bundle-multi-product-rules`):

| Entry products | Context (`--output-products`) | Intersection | Rule used |
|----------------|-------------------------------|--------------|-----------|
| [kibana] | kibana, security | {kibana} | kibana rule |
| [security] | kibana, security | {security} | security rule |
| [kibana, security] | kibana, security | {kibana, security} → [kibana, security] | kibana rule (k < s) |
| [elasticsearch] | kibana, security | empty → fallback to entry products | elasticsearch rule (if configured) or global |

### Requirement: behavior table in plans

Any plan that touches filter/rule/matching logic **must** include a behavior table showing at least four cases: (1) single-product entry matching context, (2) single-product entry not in context, (3) multi-product entry with matching context, (4) edge case (empty intersection or all-match). This prevents logic inversion bugs (for example, include semantics accidentally becoming exclude, or "any-blocks" instead of "first-match").

Reference: "Area matching behavior" and "Per-product rule resolution" tables in `docs/contribute/changelog.md` are the canonical format.

### Critical: Filter semantic consistency across all dimensions

**Before implementing any filter logic**: Verify that ALL filter types (product, type, area) use identical semantic patterns:

- **Rule selection logic**: All filters must use the same precedence algorithm (intersection + alphabetical first-match)
- **Rule application logic**: All filters must use the same replacement semantics (all-or-nothing vs per-dimension fallback)  
- **Edge case handling**: All filters must handle disjoint/empty cases identically

**Required semantic consistency validation**:
1. Document the semantic model (replacement vs inheritance) for each filter dimension
2. Verify all filter types use the same semantic model - no mixed semantics
3. Test cross-filter consistency with partial per-product rules
4. Add tests that verify semantic consistency across filter types

**Example semantic inconsistency bug**: Product filters used per-dimension fallback while type/area used all-or-nothing replacement, creating unintuitive behavior where some global rules were inherited and others weren't.

**Current semantic model**: All-or-nothing replacement - when a per-product rule is selected, it completely replaces global rules for ALL filter dimensions.

### Critical: Disjoint fallback logic validation

**Context-aware filtering bug pattern**: When implementing intersection-based rules that depend on bundle context, verify disjoint fallback behavior is **logically consistent**:

- **Context-specific bundles** (`--output-products` set): Disjoint changelogs should use **global rules only** to prevent unrelated product-specific rules from applying
- **Bundle-everything mode** (no `--output-products`): Disjoint changelogs can use their own product-specific rules

**Required disjoint tests**: For any intersection-based filtering logic, add tests that verify:
1. **Conflicting product-specific rule doesn't apply**: Disjoint changelog with conflicting product rule should use global rules when building context-specific bundle
2. **Multi-product disjoint**: Multi-product changelog disjoint from bundle context should use global rules, not alphabetically-first product rule  
3. **Bundle-everything preservation**: Same disjoint scenario with no bundle context should use changelog's own product rules

**Example bug caught**: Before fix, building a `security` bundle with an `elasticsearch` changelog would incorrectly apply `rules.bundle.products.elasticsearch.*` rules. After fix, it correctly applies global `rules.bundle.*` rules.

### Intersection-based logic validation checklist

When implementing or modifying logic that uses set intersection (e.g., bundle context ∩ changelog products):

1. **Empty intersection behavior**: What happens when sets are disjoint? Document and test explicitly.
2. **Context awareness**: Does disjoint behavior depend on whether bundle context is explicit vs. implicit?
3. **Rule precedence consistency**: Do all filter types (product, type, area) use the same intersection and fallback logic?
4. **Multi-value scenario**: Test changelogs with multiple products/areas against both overlapping and disjoint bundle contexts.
5. **Edge case coverage**: Test empty arrays, single values, and complete overlaps in addition to partial intersections.

## Invocation modes (bundle and remove)

Two mutually exclusive modes:

- **Profile mode** (`<profile> <arg> [<report>]`): all filter and output settings come from `changelog.yml`. Any filter CLI option is an error.
- **Option-based mode** (`--all`, `--input-products`, `--prs`, `--issues`, `--report`, `--release-version`): exactly one filter must be provided. Profile arguments are not allowed.

Profiles are a convenience wrapper — they make the same filters repeatable without CLI flags. The underlying behavior is identical.

### Forbidden options in profile mode

In profile mode the following options are **always forbidden** — all configuration comes from `changelog.yml`:

- Filter options: `--all`, `--input-products`, `--prs`, `--issues`, `--release-version`, `--report`
- Connection options: `--repo`, `--owner`
- Output options: `--output`, `--directory`

Any violation must emit an error that **names the specific offending options** (not a generic message listing every possible flag). Both `bundle` and `remove` must enforce the same list — verify both whenever this set changes.

## Config extension steps

When adding a field to `bundle.*` or `bundle.profiles.<name>`:

1. `BundleConfiguration.cs` — add an `init`-only property with XML doc
2. `ChangelogConfigurationYaml.cs` — add a matching `{ get; set; }` property to the YAML DTO
3. `ChangelogConfigurationLoader.cs` — map the field in `ParseBundleConfiguration`
4. `config/changelog.example.yml` — add a commented-out example

Array fields must use `YamlLenientList` to support both comma-separated strings and YAML lists.

### Configuration inheritance hierarchy validation

**CRITICAL**: When adding fields that inherit defaults, verify the inheritance chain is correct in `ChangelogConfigurationLoader.cs`:

```
rules.match (global)
  ↓ inheritedMatch
rules.bundle.match_products (bundle level) 
  ↓ matchProducts
rules.bundle.products.<context>.match_products (per-context)
  ↓ must inherit from matchProducts, NOT inheritedMatch
```

**Required inheritance tests**: For any new inheritable field, add tests verifying:
1. **Bundle-level inheritance**: `rules.bundle.<field>` correctly inherits from global `rules.<field>`
2. **Per-context inheritance**: `rules.bundle.products.<context>.<field>` correctly inherits from bundle-level `rules.bundle.<field>`
3. **Chain validation**: Global → Bundle → Context produces expected values at each level

**Common bug pattern**: Per-context fields inheriting directly from global instead of bundle level. Always check variable names in inheritance assignments:
- ✅ `var contextField = bundleLevelField;` (correct)
- ❌ `var contextField = inheritedMatch;` (skips bundle level)

**Inheritance source validation**: When adding new inheritable fields, verify in code review that the inheritance source is correct by tracing the variable name back to its assignment. Look for these patterns in `ChangelogConfigurationLoader.cs`:
- Bundle-level fields should inherit from global-level variables
- Per-context fields should inherit from bundle-level variables (not global-level)

### Systematic precedence validation

**When modifying rule precedence**: Validate the entire precedence chain systematically to prevent inheritance bugs:

**1. Single-source validation**: Each configuration level must have clear, single inheritance source
- Document which variable each level inherits from
- Verify variable names match expected inheritance chain
- Check for accidental inheritance from wrong level (common bug: per-context inheriting from global instead of bundle)

**2. Chain validation**: Global → Bundle → Context inheritance must be explicit and testable
- Test each inheritance level independently  
- Test complete chain: verify global value appears at context level when intermediate levels don't override
- Test override behavior: verify explicit values at each level properly override inherited values

**3. Filter type consistency**: All filter types must use same precedence chain
- Product filters: inherit through same chain as type/area filters
- No mixed inheritance patterns between filter dimensions
- Consistent fallback behavior across all filter types

**4. Edge case precedence**: Document and test precedence for edge cases
- Empty configurations at various levels
- Disjoint scenarios (context not matching any configured products)
- Missing intermediate levels in inheritance chain

**Critical validation pattern**:
```csharp
// CORRECT: Per-context inheriting from bundle level
var contextMatchProducts = matchProducts; // bundle-level variable

// WRONG: Per-context inheriting from global level  
var contextMatchProducts = inheritedMatch; // global-level variable
```

**Required precedence tests**: For any new inheritable field:
1. Global-only test: Set field only at global, verify it propagates correctly
2. Bundle-override test: Set field at bundle level, verify it overrides global
3. Context-override test: Set field at context level, verify it overrides bundle  
4. Chain test: Set different values at all levels, verify context gets context value

## Owner/repo precedence

**Option-based mode**: `--repo > bundle.repo config`. `--owner > bundle.owner config > "elastic"`. Enforced in `ApplyConfigDefaults`.

**Profile mode (`source: github_release`)**: `profile.Repo ?? config.Bundle.Repo`, `profile.Owner ?? config.Bundle.Owner ?? "elastic"` — in `ProfileFilterResolver.ResolveFromGitHubReleaseAsync`.

Profile fields used during `remove`: `source`, `repo`, `owner`. Fields ignored during `remove`: `output`, `output_products`, `hide_features`.

## Product/version/lifecycle uniformity

`product`, `target` (version), and `lifecycle` are used uniformly across all commands. When adding a command or filter that involves product metadata:

- Use `VersionLifecycleInference.InferLifecycle` for lifecycle inference.
- Use `ProductsConfiguration.GetProductByRepositoryName` for repo-to-product mapping.
- Never hard-code lifecycle strings.

See `docs/contribute/changelog.md#product-format` for valid values.

### Changelog files are the authoritative source of product metadata

When `--output-products` (option mode) or the `output_products` profile field is not explicitly set, the products array in the bundle is **always** assembled from the matched changelog files' own `products` fields — regardless of which filter was used to select those files.

**Never auto-infer `output_products` from a release tag, repository name, or any external source.** This applies to all filter options (`--prs`, `--issues`, `--report`, `--all`, `--release-version`) and all profile types equally.

The only legitimate exceptions are `changelog gh-release` and `changelog add`, which *create* new changelog files from scratch and embed product metadata directly into them as part of that creation step.

### `{lifecycle}` inference source varies by profile type

When `{lifecycle}` appears in a `products`, `output`, or `output_products` pattern, its source differs by profile type. This is intentional but must be documented clearly:

- **Standard profiles** (all profile types except `source: github_release`): lifecycle is inferred from the version string the user passes as the second command argument, via `VersionLifecycleInference.InferLifecycle`.
- **`source: github_release` profiles**: lifecycle is inferred from the **raw release tag** returned by GitHub, stored in `ProfileFilterResult.Lifecycle`. This must use the tag *before* `ExtractBaseVersion` strips the pre-release suffix, so `v9.2.0-beta.1` → `beta` (not `ga`).

When adding a new profile type or a new pattern placeholder, define explicitly which input drives its value and document an inference table in the docs.

## Full test list

Run with: `dotnet test tests/Elastic.Changelog.Tests/`

**Always run:**

- `BundleChangelogsTests.cs` — filter modes, config fallbacks, output, profiles
- `ChangelogRemoveTests.cs` — filter modes, dry-run, force, bundle deps, profile mode
- `BundleLoading/BundleLoaderTests.cs`
- `BundleAmendTests.cs`
- `ChangelogConfigurationTests.cs`

**Run when changing `changelog add` or GitHub fetching:**

- `Create/BasicInputTests.cs`, `Create/ValidationTests.cs`, `Create/BlockingLabelTests.cs`
- `Create/FlagsAndFeaturesTests.cs`, `Create/LabelMappingTests.cs`, `Create/TitleProcessingTests.cs`
- `Create/PrFetchFailureTests.cs`, `ReleaseNotesExtractorTests.cs`

**Run when changing rendering or bundle schema:**

- All files under `Render/` — `BasicRenderTests.cs`, `OutputFormatTests.cs`, `HideFeaturesTests.cs`, `HighlightsRenderTests.cs`, `ChecksumValidationTests.cs`, `BundleValidationTests.cs`, `DuplicateHandlingTests.cs`, `BlockConfigurationTests.cs`, `ErrorHandlingTests.cs`, `TitleTargetTests.cs`

**New tests required for any new filter or profile field:**

- Dedicated test class under `tests/Elastic.Changelog.Tests/Changelogs/`
- Must cover: happy path, dry-run (where applicable), error cases (missing inputs, mutual exclusivity), config fallback behavior
- **Use valid product names**: Only use products from the test environment's allowed list: `cloud-hosted, cloud-serverless, elasticsearch, kibana, security`

### Comprehensive edge case testing requirements

**For any filter/precedence logic change**: Must include tests covering ALL combinations from this matrix:

**Product scenarios**: 
- Empty products list: `products: []`
- Single product: `products: [kibana]`  
- Multi-product: `products: [kibana, security]`
- Disjoint products: `products: [elasticsearch]` when context is `[kibana, security]`

**Context scenarios**:
- No bundle context: `--all` mode, no `--output-products`
- Single context: `--output-products kibana`
- Multi-context: `--output-products kibana,security`  
- Disjoint context: context `[security]` with changelog `[elasticsearch]`

**Rule configuration scenarios**:
- No per-product rules: only global `rules.bundle` 
- Partial per-product rules: `kibana: { include_areas: [ui] }` (missing type filters)
- Complete per-product rules: all dimensions defined
- Conflicting per-product rules: rules that would change global behavior

**Expected behavior documentation**: Create a behavior table showing expected outcome for each significant combination BEFORE implementing the logic.

**Systematic edge case validation**:
1. **Matrix coverage**: Test at least one example from each major combination category
2. **Boundary testing**: Test edge cases like empty arrays, single items, complete overlaps
3. **Consistency validation**: Verify same logical scenario produces consistent results across all filter types
4. **Regression prevention**: Add tests for any bugs found during development

**Inheritance tests required for any inheritable field:**

- Test global → bundle inheritance: field set only at global level should propagate to bundle
- Test bundle → context inheritance: field set only at bundle level should propagate to per-context rules
- Test override behavior: explicit per-context value should override inherited bundle value
- Test inheritance chain: global → bundle → context shows correct resolution at each level

Example test pattern:
```csharp
[Test]
public void ParseBundleConfiguration_WithGlobalOnlyField_InheritsCorrectlyToContext()
{
    // Set field only at global level, verify it appears in per-context rules
}

[Test] 
public void ParseBundleConfiguration_WithBundleOnlyField_InheritsCorrectlyToContext()
{
    // Set field only at bundle level, verify it appears in per-context rules
}
```

**Disjoint logic testing pattern**:
```csharp
[Test]
public void BundleChangelogs_DisjointWithConflictingRule_UsesGlobalRules()
{
    // Bundle context: [security]
    // Changelog products: [elasticsearch] (disjoint)
    // Config: elasticsearch rule that would exclude the entry
    // Expected: Entry included via global rules (conflicting elasticsearch rule ignored)
}
```

### Cross-filter integration testing

**For changes affecting multiple filter dimensions**: Add integration tests that verify filter types work together correctly:

**1. Filter interaction tests**:
- Test entries that should pass product filters but fail type filters
- Test entries that should fail product filters but pass type filters  
- Test entries with complex multi-dimensional filtering (product AND type AND area)
- Verify filter order doesn't affect final outcome

**2. Precedence consistency tests**:
- Same changelog tested against multiple contexts to verify consistent rule selection
- Multi-product changelog tested with overlapping and disjoint contexts
- Verify same precedence algorithm used for all filter types

**3. Configuration permutation tests**:
- Global-only configuration vs per-product-only vs mixed configurations
- Partial per-product rules vs complete per-product rules
- Conflicting rules (global vs per-product that produce opposite outcomes)

**Example integration test pattern**:
```csharp
[Test]
public void FilterIntegration_ProductPassTypesFail_ProducesCorrectResult()
{
    // Config: global exclude_types: [docs], kibana include_products: [kibana]
    // Entry: products: [kibana], type: docs, areas: [ui]
    // With all-or-nothing: kibana rule replaces global → entry included  
    // With per-dimension: product pass + type fail → entry excluded
}
```

**Critical integration validation**: After any semantic change, run full test suite to catch unexpected interactions between filter types.

## Documentation accuracy validation

**After any filter/precedence logic change**: Verify documentation accurately reflects actual implementation behavior:

### 1. Precedence documentation accuracy
- **Test documented precedence**: For each documented precedence rule, write a test that verifies the rule matches implementation
- **Validate examples**: Test all code examples in documentation against actual system behavior  
- **Cross-reference validation**: Ensure CLI docs, contribute guide, and inline comments describe same behavior

### 2. Fallback behavior verification  
- **Document all fallbacks**: Every fallback case (disjoint, empty, missing config) must be documented with examples
- **Test fallback claims**: Each documented fallback must have corresponding test proving it works as described
- **Edge case coverage**: Documentation must cover all edge cases handled in code

### 3. Semantic model documentation
- **Rule application semantics**: Document whether rules use replacement vs inheritance semantics
- **Filter consistency**: Ensure all filter types are documented with same semantic model  
- **Breaking change clarity**: When semantics change, clearly document old vs new behavior with migration examples

### 4. Example validation process
- **Live example testing**: Every configuration example in docs must be tested against actual implementation
- **Example coverage**: Examples should demonstrate edge cases, not just happy path
- **Version alignment**: Examples must reflect current implementation, not outdated behavior

**Required after any logic change**: 
1. Test all existing documentation examples against new implementation
2. Update any examples that no longer work or produce different output
3. Add new examples for any new edge cases or behaviors introduced
4. Verify cross-references between CLI docs and contribute guide remain accurate

**Documentation debt prevention**: Any time code behavior changes, corresponding documentation change is mandatory in same commit.

## Documentation checklist

Every change must update the relevant files:

**CLI reference** (`docs/cli/release/`):

- `changelog-bundle.md` — options, profile config fields table, examples
- `changelog-remove.md` — options, profile-based removal section, "ignored fields" note
- `changelog-add.md`, `changelog-render.md`, `changelog-init.md`, `changelog-bundle-amend.md` — when those commands change
- `changelog gh-release` — documented only in `docs/contribute/changelog.md` (no dedicated CLI ref page)

**How-to guide**: `docs/contribute/changelog.md` — update the relevant section; anchors here are the cross-reference targets for CLI ref pages.

**Syntax reference**: `docs/syntax/changelog.md` — update if bundle schema or directive options change.

**Config example**: `config/changelog.example.yml` — add commented examples for new fields.

Per-feature checklist:

- New CLI option → update options table and all mutual-exclusivity statements
- New profile field → add to "Profile configuration fields" in `changelog-bundle.md`; update "ignored fields" note in `changelog-remove.md`
- Bundle schema change → update `changelog-bundle.md`, `docs/syntax/changelog.md`, and downstream command docs
- Precedence chain → document explicitly in option description and contribute guide
- **Fallback chain** for any option or field → document the full resolution order explicitly (for example: "CLI flag > profile field > bundle-level default > hardcoded default"). Use a table when there are more than two levels. **Never mark a field as "required" without first verifying that no fallback exists** in `ApplyConfigDefaults`, `ChangelogConfigurationLoader`, or the relevant service.
- **Rule/filter logic change** → add or update a behavior table in `docs/contribute/changelog.md` following the format of the existing "Area matching behavior" and "Per-product rule resolution" tables. The plan for the change must include the proposed table before implementation begins.

## Architectural consistency validation

**Before starting any major filter/precedence changes**: Validate architectural consistency to prevent lengthy refactoring cycles:

### 1. Cross-dimensional consistency check
- **Semantic alignment**: Ensure all filter dimensions (product, type, area) use same semantic model
- **Precedence alignment**: Verify all filters use same rule selection algorithm
- **Edge case alignment**: Check that all filters handle edge cases identically
- **Implementation consistency**: Look for mixed patterns in existing code before extending

### 2. Upfront architectural decisions
Document these decisions BEFORE implementation:
- **Replacement vs inheritance**: Will new rules completely replace or merge with existing rules?
- **Precedence algorithm**: What algorithm determines which rule applies? 
- **Edge case behavior**: How will empty/disjoint/missing cases be handled?
- **Breaking change scope**: What existing behavior will change and is it acceptable?

### 3. Implementation approach validation
- **Incremental vs comprehensive**: Can change be made incrementally or requires comprehensive overhaul?
- **Backward compatibility**: What compatibility guarantees are needed?
- **Migration complexity**: How difficult will migration be for existing users?
- **Test strategy**: What test patterns will validate the new behavior?

**Red flags requiring architectural review**:
- Mixed semantic models across filter types
- Inconsistent precedence algorithms  
- Ad-hoc edge case handling
- Complex inheritance chains without systematic validation
- Filter logic that works differently for different input methods

**Prevention strategy**: Spend time upfront documenting the complete architectural approach rather than implementing incrementally and discovering inconsistencies later.
