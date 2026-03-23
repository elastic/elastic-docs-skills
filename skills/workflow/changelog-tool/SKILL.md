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
