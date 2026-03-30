# Elastic Docs Skills

A catalog of [Claude Code](https://docs.anthropic.com/en/docs/claude-code) skills for Elastic documentation workflows.

Browse the catalog, pick the skills you need, and install them with a single command.

## Quick start

### Claude Code plugin (recommended)

Add the marketplace and install — no clone required:

```
/plugin marketplace add https://github.com/elastic/elastic-docs-skills
/plugin install elastic-docs-skills@elastic-docs-skills
```

Skills are available immediately as `/elastic-docs-skills:<skill-name>`, for example:

```
/elastic-docs-skills:docs-check-style
/elastic-docs-skills:docs-crosslink-validator
```

### Individual skills via npx

Install all skills with a single command (requires Node.js):

```bash
npx --yes skills@latest add elastic/elastic-docs-skills -g
```

This auto-detects your installed agents (Claude Code, Cursor, Codex, etc.) and prompts you to choose which ones to install to.

Update all installed skills to the latest versions:

```bash
npx --yes skills@latest update -g
```

Install a single skill by name:

```bash
npx --yes skills@latest add elastic/elastic-docs-skills --skill docs-check-style -g
```

Other useful commands:

```bash
# List installed skills.
npx --yes skills@latest list -g

# Check for available updates.
npx --yes skills@latest check -g

# Remove a skill.
npx --yes skills@latest remove docs-check-style -g
```

### Alternative: interactive TUI installer

If you prefer an interactive terminal UI (macOS and Linux only, requires Python 3):

```bash
curl -fsSL https://ela.st/docs-skills-install | bash
```

Optional flags:

```bash
# List available skills.
curl -fsSL https://ela.st/docs-skills-install | bash -s -- --list

# Install all skills.
curl -fsSL https://ela.st/docs-skills-install | bash -s -- --all

# Update installed skills.
curl -fsSL https://ela.st/docs-skills-install | bash -s -- --update
```

If you plan to contribute, clone the repository and run locally:

```bash
git clone https://github.com/elastic/elastic-docs-skills.git
cd elastic-docs-skills
./install.sh
```

## Creating new skills

If you have this repo cloned, the easiest way to add a skill is to use the built-in `/create-skill` command (available only within this repo):

```
/create-skill my-new-skill
```

This walks you through the process interactively and can open a PR for you.

### Manual creation

1. Create a directory under `skills/<category>/<skill-name>/`
2. Add a `SKILL.md` file with the required frontmatter
3. Open a PR

### SKILL.md frontmatter schema

Every skill must have YAML frontmatter with at least these fields:

```yaml
---
name: docs-my-skill              # Required — kebab-case skill invocation name
version: 1.0.0              # Required — SemVer (MAJOR.MINOR.PATCH)
description: What it does    # Required — when to use this skill
---
```

Optional fields:

```yaml
disable-model-invocation: true   # Only runs via /my-skill, not auto-triggered
argument-hint: [args]            # Hint shown in autocomplete
allowed-tools: Read, Grep        # Tools the skill can use without asking
context: fork                    # Run in isolated subagent
agent: Explore                   # Subagent type
sources:                         # Upstream URLs for freshness checks
  - https://www.elastic.co/docs/...
```

## Versioning

Skills follow [SemVer](https://semver.org/):

- **MAJOR** — Breaking changes to the skill's behavior or interface
- **MINOR** — New functionality, backwards-compatible
- **PATCH** — Bug fixes, wording improvements

Bump the `version` field in your `SKILL.md` frontmatter when making changes.

## Updating installed skills

```bash
npx --yes skills@latest update -g
```

Or, if using the TUI installer:

```bash
curl -fsSL https://ela.st/docs-skills-install | bash -s -- --update
```

## CI validation

All PRs that touch `skills/**` are validated by GitHub Actions in `.github/workflows/validate-skills.yml`. The workflow runs the following checks on every skill:

- Every `skills/**/SKILL.md` must have valid YAML frontmatter
- Required fields: `name`, `description`, `version`
- `name` must be kebab-case and unique across all skills
- `version` must be valid SemVer
- `evals/evals.json` (if present) must be valid JSON with required structure

## Repository structure

```
elastic-docs-skills/
├── .github/
│   ├── copilot-setup-steps.yml   # GitHub Copilot coding agent setup
│   └── workflows/
│       ├── validate-skills.yml   # Skill validation via skill-validator
│       └── skill-freshness.lock.yml
├── .claude/skills/               # Skills that work within this repo
├── skills/                       # The browsable catalog
│   └── <category>/
│       └── <skill-name>/
│           └── SKILL.md
├── install.sh                    # Interactive TUI installer
└── README.md
```

## Contributing

See [CONTRIBUTING.md](CONTRIBUTING.md) for detailed guidelines on creating skills, writing evals, choosing categories, and frontmatter conventions.

## License

This repository is licensed under the [Apache License, Version 2.0](https://www.apache.org/licenses/LICENSE-2.0). See [LICENSE.txt](LICENSE.txt) for the full text.
