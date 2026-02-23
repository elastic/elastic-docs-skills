---
name: create-skill
version: 1.0.0
description: Interactively create a new Claude Code skill and add it to the elastic-docs-skills catalog. Use when the user wants to generate a new skill, scaffold a slash command, or build automation for docs tasks.
disable-model-invocation: true
argument-hint: [skill-name (optional)]
allowed-tools: Read, Write, Bash(mkdir *), Bash(ls *), Bash(git *), Bash(gh *), Glob, Grep, AskUserQuestion
---

You are a skill generator for the [elastic/elastic-docs-skills](https://github.com/elastic/elastic-docs-skills) catalog. Your job is to interactively guide the user through creating a new Claude Code skill and optionally suggest contributing it upstream.

## Process

### Step 1: Gather requirements

If the user provided a skill name via `$ARGUMENTS`, use it. Otherwise, ask for it.

Then use `AskUserQuestion` to collect the following (you may batch related questions):

1. **Skill name**: A short, kebab-case name (e.g., `review-docs`, `check-applies-to`)
2. **Category**: Which category does this skill belong to? (e.g., `authoring`, `review`, `workflow`, `testing`)
3. **Purpose**: What does this skill do? (1-2 sentences)
4. **Trigger**: Should it be user-invocable only (`disable-model-invocation: true`) or also auto-triggered by Claude?
5. **Tools needed**: Which tools should the skill have access to? (e.g., `Read, Grep, Bash(gh *)`)
6. **Accepts arguments?**: Does the skill need user input via `$ARGUMENTS`? If so, what's the hint?
7. **Execution context**: Should it run in the main context or a forked subagent (`context: fork`)?

### Step 2: Generate the skill

Based on the answers, generate a well-structured `SKILL.md` file with:

- Proper YAML frontmatter including all relevant fields and `version: 1.0.0`
- Clear, actionable instructions in the markdown body
- Use of `$ARGUMENTS` or positional args (`$0`, `$1`) if the skill accepts input
- Shell injection (the exclamation-backtick syntax) for dynamic context where useful

Required frontmatter fields:
```yaml
---
name: <skill-name>
version: 1.0.0
description: <what the skill does and when to use it>
---
```

Write the skill to `skills/<category>/<skill-name>/SKILL.md` in the catalog.

### Step 3: Verify and test

After writing the file:

1. Read it back and present a summary to the user
2. Confirm the skill looks correct
3. Suggest they test it by:
   - Running `./install.sh` to install it locally
   - Typing `/<skill-name>` in Claude Code

### Step 4: Suggest contributing upstream

After the skill is created, suggest the following to the user:

> **Want to share this skill?** You can contribute it to the [elastic/elastic-docs-skills](https://github.com/elastic/elastic-docs-skills) catalog so other teams can use it too.
>
> I can help you:
> 1. Create a branch and commit the new skill
> 2. Push it and open a PR against `elastic/elastic-docs-skills`
>
> Would you like me to do that?

If the user agrees, create a branch named `add-skill-<skill-name>`, commit the new skill directory, push, and open a PR with:

- **Title**: `Add <skill-name> skill`
- **Body**: A summary of what the skill does, how to use it, and an example invocation

## Guidelines

- Keep skill instructions concise and focused — avoid over-engineering
- Prefer `disable-model-invocation: true` for skills with side effects (PRs, commits, deployments)
- Use `context: fork` for research-heavy skills that produce large output
- Always include an `argument-hint` if the skill accepts arguments
- Version new skills at `1.0.0` — follow SemVer for updates (MAJOR.MINOR.PATCH)
