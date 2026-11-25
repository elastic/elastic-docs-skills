# Learn from the round

Read this after the reviews are posted. Every change the user made between your first drafts and the posted reviews is a signal about the skill. Turn the signals that generalize into a skill edit, so the next round drafts closer to what gets posted.

Most rounds produce no lesson, or only one. A lesson needs both the user's confirmed reason and a rule that applies to the next connector PR.

## 1. Collect the changes

```bash
python3 <skill-dir>/scripts/compare_drafts.py drafts.initial.json drafts.json
```

It lists, per PR, the review type and summary changes, drafts turned on or off, drafts added or removed, and word-level edits to each body.

Add what the comparison can't show:

- Policy changes the user gave in chat, such as "don't flag X" or "always suggest Y".
- Drafts you fixed yourself after a check, for example a claim that failed verification before posting.
- Points the user raised that no draft covered.

## 2. Find the reason behind each change

For each change, write one line: what changed, and your best guess at why. Then sort it:

- **Lesson:** the reason would hold on the next connector PR. Typical signs: the same edit on several comments or PRs, a draft type the user turns off by default, a claim type that failed verification, or a review type and summary that drifted apart.
- **Local:** the reason depends on this PR, its developer, or its thread. Leave it out.
- **Voice:** a rewording that matches the user's personal style. It belongs in the user's own writing profile, not in this skill. Mention it once, so the user can update their profile.

If the skill already covers a lesson and you drafted against it anyway, the fix is a sharper or more visible rule, not a second copy of it.

## 3. Choose where each lesson goes

| Lesson about | File |
| --- | --- |
| Tone, length, summaries, review type | `references/comment-style.md` |
| Outline asks, ready-made suggestion text, what not to flag | `references/page-outline.md` |
| Availability, markers, the contract test | `references/availability-and-markers.md` |
| `drafts.json`, checks, posting | `references/posting.md` or `scripts/` |
| A trap that cost a round of rework | `SKILL.md`, under **Gotchas** |
| Behavior a grader can check | a new expectation in `evals/evals.json` |

Prefer sharpening an existing line over adding a new one. State the rule and its reason in general terms, without the PR number or the developer's name, and phrase it as the behavior to follow.

## 4. Confirm with the user

Present each candidate lesson with:

- The observed change, quoted before and after.
- Your inferred reason.
- The proposed skill edit: the file and the exact text.

Ask whether the reason is right and whether to encode it. Use a structured question when the client supports one, with one question per lesson. When the user gives a different reason, rewrite the edit around their reason.

If nothing qualifies, say so in one sentence and end the round.

## 5. Edit the skill on GitHub

The skill lives in `elastic/elastic-docs-skills`, under `skills/review/docs-review-connector-docs/`.

1. Check for an open PR that already changes this skill: `gh pr list --repo elastic/elastic-docs-skills --state open --search docs-review-connector-docs`. If the user owns one, pull its branch and add the edit there. Otherwise, create a branch from the latest `main`, on a fork if the user can't push to the repo.
2. Apply the confirmed edits and nothing else.
3. Bump `version` in `SKILL.md`: PATCH for a clarified rule or wording, MINOR for a new rule, check, or script option. Skip the bump while the skill's first PR is still open. CI also fails unless the PR raises the version in `.claude-plugin/plugin.json` above the one on `main`.
4. Validate: `python3 -m json.tool evals/evals.json`, and run any script you changed against the round's `drafts.json`.
5. Show the user the diff. For a new PR, also show the title and body: the behavior that changes, and the observation that led to it. Push or open the PR only after the user approves.
