# Slack message templates

Read this file before drafting or sending any Slack for the docs-stack-release skill. Fill placeholders from the docs issue (§6.1).

## Handle resolution

GitHub handle ≠ Slack handle. Never assume they are the same. Never invent people or Slack IDs.

1. Issue template / appendix lookup table first.
2. Unmapped: `slack_search_users` (server: `user-slack`) by display name or real name.
3. Confident match (exact display name or single result): use it. Uncertain: `[@handle]` and ask.
4. **Always resolve to user IDs.** Messages must use `<@USER_ID>` (e.g. `<@U07EN8ZFRTL>`). Display names like `@wajiha` render as plain text and do not ping.
5. **OOO before pinging.** For each resolved user, `slack_read_user_profile`. If status suggests unavailable (`:palm_tree:`, "OOO", "On vacation", "PTO", `:face_with_thermometer:`, `:no_entry:`): "Heads up: [name] appears to be out ([status]). Who should cover for them?" -- before drafting.

Batch-ask for any still-missing: "I need Slack equivalents for these handles: ..."

## Formatting

- **Mentions:** `<@USER_ID>`. Display names do not resolve.
- **Links:** `<URL|display text>` (e.g. `<https://github.com/elastic/dev/issues/3600|tracking issue>`). Markdown `[text](url)` does not render.
- **Bold / italic / strike:** `*bold*`, `_italic_`, `~text~` -- not `**bold**`.

## Send (always)

1. Draft from a template below.
2. Show the user: "Here's what I'll post to `#docs`:\n[preview]\nSend?"
3. Send only on confirmation ("send it" / "looks good" counts). Never send on "update the thread" or checkbox catch-up without a preview.
4. Follow-ups (outstanding RNs, day-before, docs released): thread reply on the FF announcement **and** post to channel (`reply_broadcast: true`). Use `docsFfThreadTs` from session state if present; otherwise `slack_search_public` for the version in `#docs`, then persist the ts.
5. After send: check the matching docs-issue checklist item (§4). Report: "Sent to #docs (threaded on the FF announcement). Checked [line] on #[issue]."

## Feature freeze (multi-release)

If all issues share one anticipated release date, use one date; otherwise list per version.

```markdown
Hi everyone! :wave: Today is the feature freeze for multiple releases.

The following releases are scheduled to release <ANTICIPATED_DATE>: <VERSION_LIST>

Please add your release note PRs to the issues linked below:

**Releases & related issues**

(Repeat for each issue in the batch:)
<VERSION> -- <ISSUE_SLACK_LINK>

---

:bell: **Ping for <VERSION_OR_GROUP_A>**

(One line per product with `<@USER_ID>` for stakeholders in the issue.)

---

:bell: **Ping for <VERSION_OR_GROUP_B>** *(repeat when 8.x vs 9.x tables differ)*
```

## Outstanding release notes (day before)

```markdown
The <VERSION_LIST> release is scheduled for tomorrow. The following release note PRs are still outstanding:

(Repeat for each outstanding row:)
• <Product> <@USER_ID>

Please file and/or get approval on your PRs today. Tracking issue: <ISSUE_SLACK_LINK>
```

## Merge release notes (release day)

```markdown
The <VERSION_LIST> release has kicked off. If you haven't already, you can merge your release notes PRs.

<@api-docs-person> it is safe to update APIs.
```

## Docs released (final / 8.x scrape)

Send after the gate and website eyeball. Include the exact 8.x semver from the issue for the scrape line. If the batch is **9.x-only**, omit the scrape line.

**One version** -- singular; do not use "versions" or "all":

```markdown
Docs for stack version <VERSION> are released!
<@scrape-person> you can start scraping the docs for <8.x_VERSION> now
```

**Multiple versions:**

```markdown
Docs for stack versions <VERSION_LIST> are all released!
<@scrape-person> you can start scraping the docs for <8.x_VERSION> now
```

## #mission-control thread reply (release day)

Reply in the "begin publishing" thread after confirming docs are live:

```markdown
<VERSION_LIST> docs are live.
```

Keep it short -- this thread is noisy and read by many teams.
