# Slack message templates

Read this file before drafting or sending any Slack for the docs-stack-release skill. Fill placeholders from the docs issue (§6.1).

## Mentions, preview, send

GitHub ≠ Slack. Never invent IDs. Appendix maps GitHub → Slack name (`@wajiha`), not a `U…`.

- Look up every ping with `slack_search_users`. Cache in `slack.handles`. Ask only if search is empty or ambiguous.
- User groups: copy the `S…` ID from the latest `#docs` freeze ping. Search will miss. Send as `<!subteam^S…>` -- `<@S…>` is how search displays a group and will not ping.
- Placeholder row (`` `Beats point person` ``): ping **only** the footnote GitHub person on the current issue. Do not add extra people from an older freeze ping. RN: `please update the table to confirm who's responsible`. API docs / docs-eng: `who can assist with this release?`. Match the latest `#docs` freeze ping for **phrasing** only.
- OOO: `slack_read_user_profile`. Flag palm_tree / OOO / PTO / sick. Not "in a meeting" or "outside of working hours".

**Preview:** the exact Slack draft in a fenced code block so every line break is visible. Do not render it as chat markdown -- that collapses the message onto one line. `@slack-name` from the appendix or profile (`@wajiha`, not `@Wajiha Parvez`). Links may be aliased (`<URL|text>`). Mentions must not: no `<@U…|Name>`, no full real names.

**Send:** people `<@U…>`; user groups `<!subteam^S…>`. No `|name` fallback. Confirm first ("send it" / "looks good"). Not on "update the thread". Follow-ups: thread on the FF ts + `reply_broadcast`. Then check the issue box.

Format: `*bold*` `_italic_` `~strike~`. One `•` per product.

## Feature freeze

**One version:** no `:bell: Ping for` line. Schedule line is `<VERSION> is scheduled to release <ANTICIPATED_DATE>.`

```markdown
Hi everyone! :wave: Today is the feature freeze for <VERSION>.

<VERSION> is scheduled to release <ANTICIPATED_DATE>.

Please add your release note PRs to the <ISSUE_URL|tracking issue>.

(One `•` per product. Named: `@slack-name`. Placeholder: footnote person + assign phrasing above.)
```

**Multiple versions:** if they share one GA date, use one date; otherwise list per version. Keep a `:bell: Ping for` heading per group (8.x vs 9.x when tables differ).

```markdown
Hi everyone! :wave: Today is the feature freeze for multiple releases.

The following releases are scheduled to release <ANTICIPATED_DATE>: <VERSION_LIST>

Please add your release note PRs to the issues linked below:

*Releases & related issues*

(Repeat for each issue in the batch:)
<VERSION> -- <ISSUE_SLACK_LINK>

---

:bell: *Ping for <VERSION_OR_GROUP_A>*

(One `•` per product.)

---

:bell: *Ping for <VERSION_OR_GROUP_B>*
```

## Outstanding release notes (day before)

```markdown
The <VERSION_LIST> release is scheduled for tomorrow. The following release note PRs are still outstanding:

(Repeat for each outstanding row:)
• <Product> @slack-name

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
