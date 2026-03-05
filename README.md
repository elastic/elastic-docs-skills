# Elastic Docs Skills

A catalog of [Claude Code](https://docs.anthropic.com/en/docs/claude-code) skills for Elastic documentation workflows.

Browse the catalog, pick the skills you need, and install them with a single command.

## Quick start

Clone the repository and run the interactive installer:

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
name: my-skill              # Required — kebab-case, must match directory name
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
```

## Versioning

Skills follow [SemVer](https://semver.org/):

- **MAJOR** — Breaking changes to the skill's behavior or interface
- **MINOR** — New functionality, backwards-compatible
- **PATCH** — Bug fixes, wording improvements

Bump the `version` field in your `SKILL.md` frontmatter when making changes.

## CI validation

All PRs that touch `skills/**` are validated by GitHub Actions using [`skill-validator`](https://github.com/agent-ecosystem/skill-validator). The workflow (`.github/workflows/validate-skills.yml`) runs the following checks on every skill:

- **Structure** — `SKILL.md` exists with valid YAML frontmatter and required fields
- **Links** — all external URLs resolve successfully
- **Content analysis** — word density, code block ratios, instruction specificity
- **Contamination detection** — flags cross-language code examples that could confuse LLMs

Results are posted as inline annotations on the PR and rendered in the Actions step summary. Warnings are non-blocking; only errors fail the check.

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

1. Fork and clone this repository
2. Create a skill using `/create-skill` or manually
3. Ensure your `SKILL.md` has all required frontmatter fields
4. Open a PR — CI will validate your skill automatically

## License

This repository is licensed under the [Apache License, Version 2.0](https://www.apache.org/licenses/LICENSE-2.0). See [LICENSE.txt](LICENSE.txt) for the full text.
