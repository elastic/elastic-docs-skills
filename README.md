# elastic-docs-skills

A catalog of [Claude Code](https://docs.anthropic.com/en/docs/claude-code) skills for Elastic documentation workflows.

Browse the catalog, pick the skills you need, and install them with a single command.

## Quick start

No clone needed — just curl and run:

```bash
curl -sSL https://raw.githubusercontent.com/elastic/elastic-docs-skills/main/install.sh | bash
```

This fetches the skill catalog from GitHub and launches an interactive TUI (powered by [gum](https://github.com/charmbracelet/gum)) where you can select which skills to install.

### Other install options

```bash
# List available skills
curl -sSL https://raw.githubusercontent.com/elastic/elastic-docs-skills/main/install.sh | bash -s -- --list

# Install all skills
curl -sSL https://raw.githubusercontent.com/elastic/elastic-docs-skills/main/install.sh | bash -s -- --all
```

Or from a local clone:

```bash
git clone https://github.com/elastic/elastic-docs-skills.git
cd elastic-docs-skills
./install.sh                   # Interactive TUI
./install.sh --list            # List all available skills
./install.sh --all             # Install everything
./install.sh --uninstall NAME  # Remove an installed skill
```

Skills are installed to `~/.claude/skills/` so they're available in all your projects.

## Skill catalog

| Name | Category | Version | Description |
|------|----------|---------|-------------|
| `create-skill` | workflow | 1.0.0 | Interactively create a new Claude Code skill and add it to the catalog |

## Creating new skills

The easiest way to add a skill is to use the `create-skill` skill itself:

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

All PRs are validated by GitHub Actions (`.github/workflows/validate-skills.yml`):

- Every `skills/**/SKILL.md` must have valid YAML frontmatter
- Required fields: `name`, `description`, `version`
- `version` must be valid SemVer
- Directory name must match the `name` field

## Repository structure

```
elastic-docs-skills/
├── .github/workflows/        # CI validation
├── .claude/skills/            # Skills that work within this repo
├── skills/                    # The browsable catalog
│   └── <category>/
│       └── <skill-name>/
│           └── SKILL.md
├── install.sh                 # Interactive TUI installer
└── README.md
```

## Contributing

1. Fork and clone this repository
2. Create a skill using `/create-skill` or manually
3. Ensure your `SKILL.md` has all required frontmatter fields
4. Open a PR — CI will validate your skill automatically

## License

This repository is licensed under the [Creative Commons Attribution 4.0 International License (CC-BY-4.0)](https://creativecommons.org/licenses/by/4.0/). See [LICENSE.txt](LICENSE.txt) for the full text.
