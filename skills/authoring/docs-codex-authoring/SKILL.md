---
name: docs-codex-authoring
version: 1.0.0
description: Author and check Elastic internal documentation pages for Codex (codex.elastic.dev). Use when working in a repository with registry: internal in docset.yml, when the user mentions Codex or an internal Elastic engineering handbook, or when asked to draft or review runbooks, architecture notes, or operational procedures for an internal audience. Do not use for public Elastic documentation (elastic.co/docs).
argument-hint: <path> [--review]
context: fork
allowed-tools: Read, Glob, Grep, Bash, mcp__elastic-internal-docs
sources:
  - https://codex.elastic.dev/r/support-prod/users/mcp/approved-mcp-servers/codex
---

# Codex authoring guide

Author and check internal Elastic documentation pages for Codex (codex.elastic.dev).

## Mode

`--review` in `$ARGUMENTS`: run **review mode** on existing pages.  
Default: **authoring mode** — apply these rules while drafting or updating.

## Registry detection and scope confirmation

Look for `docset.yml` in the target path or its parents. Read `registry:`.

- `registry: internal` → Codex rules (primary path for this skill). Proceed.
- `registry: public` → public docs mode: use `mcp__elastic-docs` for cross-linking; require `applies_to` and `products` in frontmatter; drop ownership signal check. Proceed.
- No `docset.yml` found → scope is ambiguous. Run:

  ```bash
  echo "${CI:-local}"
  ```

  - Result is `ci` (agentic/workflow context): proceed with Codex rules.
  - Result is `local` (interactive): ask the user before proceeding:
    > "I could not find a `docset.yml` to confirm the docs registry. Are you working on internal Codex documentation, or public Elastic documentation?"
    
    Wait for the answer before continuing.

---

# AUTHORING MODE

## Page types

Identify the page type before writing. Each type has a required structure.

### Runbook

| Section | Required |
|---|---|
| H1 | State the problem, not the solution ("Elasticsearch cluster turns red") |
| Opening | Who uses this and when (on-call, incident response) |
| Symptoms | Observable signals: error messages, metrics, alert names |
| Prerequisites | Access, tools, permissions needed before starting |
| Resolution | Numbered steps — each step: action → expected result → verification |
| Escalation | When to stop and who to contact |

### Architecture note

| Section | Required |
|---|---|
| H1 | Name of the system or component |
| Opening | What it does (one sentence) and why it exists (one sentence) |
| How it works | Key components, data flow, dependencies |
| Key decisions | Non-obvious design choices and their rationale |
| Operational concerns | What breaks, how to detect it, who owns it |
| Related pages | Links to runbooks, source repos, public docs |

### Operational procedure

| Section | Required |
|---|---|
| H1 | Action verb + object ("Rotate API keys for the docs pipeline") |
| Opening | When to run this and the expected outcome |
| Before you begin | Required access, permissions, running systems |
| Steps | Numbered, one action per step, with verification after critical steps |
| After | Confirm success; update records or alert systems if needed |

### How-to

| Section | Required |
|---|---|
| H1 | Action verb + goal |
| Opening | What the reader achieves |
| Steps | Numbered; group under H2s if more than 7 steps |
| Result | What success looks like |

## Frontmatter

Always include:

```yaml
---
description: <one specific sentence, not a repeat of the H1>
navigation_title: <short title when H1 is longer than 50 characters>
---
```

Add an ownership signal: either a `team:` frontmatter field or a "Maintained by: @team-name" line at the end of the page.

## Directives

Use directives instead of buried prose:

| Content | Directive |
|---|---|
| Action that can cause data loss or downtime | `:::warning` |
| Non-obvious constraint or context | `:::note` |
| Shortcut or best practice | `:::tip` |
| Procedure with more than 5 steps | `::::{stepper}` |
| Content duplicated verbatim elsewhere | `:::{include}` |

Do not stack admonitions. One per section is enough.

## Cross-linking

After drafting, use the Codex MCP server to search for pages related to the topic. Link to any relevant Codex pages found. Also link to:

- Source PRs or commits that justify the change (cite them in the PR body too).
- elastic.co/docs for public Elastic product references.
- Internal repositories, dashboards, or runbooks when a procedure needs them.

Never use a raw URL as link text. Write descriptive link text.

## Quality bar

Before opening a PR:

- [ ] No `TODO`, `TBD`, `FIXME`, `WIP`, `placeholder`, or stub headings with no body.
- [ ] Every procedure step has a verification or expected result.
- [ ] Credentials and tokens are referenced by name (secret store, env var), never written inline.
- [ ] If the target repository is public: no internal hostnames, private repo paths, or internal-only URLs.
- [ ] The page stands alone — a teammate on call can follow it without asking for context.

---

# REVIEW MODE

Run all checks. Collect findings before reporting.

## 1. WIP markers

Flag: `TODO`, `TBD`, `FIXME`, `WIP`, `coming soon`, `placeholder`, `[insert`, trailing `...` in prose, headings with no body.

## 2. Frontmatter

- `description`: required, specific, not a repeat of the H1.
- `navigation_title`: required if H1 is longer than 50 characters.
- Ownership signal: flag if missing.

## 3. Structure

- Opening paragraph must state purpose. Flag preamble ("This document…", "This guide covers…").
- Heading hierarchy: no skipped levels, no single-child sections.
- Runbooks: flag missing Symptoms or Resolution sections.
- Procedures: flag steps with no verification or expected result.

## 4. Directives

Suggest:

- `:::warning` for prose warnings about data loss or downtime.
- `:::note` for buried caveats or constraints.
- `:::{include}` for content repeated verbatim elsewhere.

## 5. Links

- Flag pages with no outbound links.
- Use the Codex MCP to find related pages that should be linked but are not.
- Verify that existing Codex links resolve.
- Flag public Elastic product mentions with no link to elastic.co/docs.

## 6. Style

Flag:

- Passive voice: "is used", "can be configured", "will be shown"
- Third person: "the user should", "developers must", "teams need to"
- Marketing language: "leverage", "seamless", "powerful", "robust"
- Code blocks without a language tag
- CLI commands with no prerequisite context (directory, credentials, running service)

## Output

Flat list of findings grouped by check. For each finding: file and approximate line, problem (one sentence), fix (one sentence).

End with one line per file: page type, finding count, quality signal (clean / minor issues / needs work).
