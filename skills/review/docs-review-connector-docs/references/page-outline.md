# Connector page outline and recurring asks

## Target outline

Every connector page follows one outline, so a reader who knows one page finds the same sections in the same place on any other.

1. **Intro, first after the H1.** What the connector does and where it's available. If some capabilities start later, an untagged lead-in sentence, then tagged bullets.
2. **Prerequisites.** What the reader needs to have, on the vendor side and the Elastic side: licenses, roles, privileges, setup done elsewhere. Things to have, never steps.
3. **Create connectors in {{kib}}.** In this order, as H3s: vendor-side setup (for example **Get API credentials**), connector configuration, networking configuration, then **Test connectors**. Every instruction lives here.
4. **Connector actions.** Reference for every action, split into H3s when it helps (read, lookup, write).
5. **Connector events**, only if the connector has them.
6. **How-tos.** Example-oriented tasks for one use case.

Tagging: the frontmatter carries the baseline lifecycle, so tag only what started later. Use one section tag for a group, not one per action. Put `serverless` first, then `stack`. When an existing page gains content that started in an earlier release, take the version from the minor that shipped it. Content new on `main` uses the version from SKILL.md step 2.

Ask for outline changes one comment at a time, anchored on the heading that moves. Don't rewrite whole sections in a suggestion.

## Recurring asks

Use these as starting points and adapt the anchor IDs to the page. Keep the page's existing anchor ID when you change a heading level, so links don't break.

**Create sentence with arrows.** Anchor on the line with `>`:

```suggestion
You can create connectors in **{{stack-manage-app}}** → **{{connectors-ui}}**.
```

**Menu paths in steps.** Same arrows, one bold element per menu item:

```suggestion
2. Go to **Administration** → **User Roles** and create or pick a role.
```

**Test connectors as the last H3 under Create:**

```suggestion
### Test connectors [<existing-anchor>]
```

Short reason: testing is the last step of creating the connector.

**Credentials and networking under Create.** No suggestion block, because the section moves. Ask on the heading:

> Should **Get API credentials** move up as the first H3 under **Create connectors in {{kib}}**? Readers need the credentials before they fill in the form, and that's the order we've been using on the other new connector pages.

**No `## Overview` heading.** Fold its content into the intro, or into the section it repeats.

**Section name.** Call the action reference **Connector actions**, without an extra "summary table" heading for the table.

**Test notes in user docs.** Flag phrases such as "in testing", "has not been verified", or a "Notes from live use" heading. Ask for reader guidance instead: what the reader should expect or do. A heading like **Usage notes** works.

**Duplicated content.** One explanation in one place. A trailing "Configure the connector" table that repeats the configuration fields should go, after any field it alone mentions moves up.

**Connector list.** One entry per connector in the snippet, alphabetical within its group. Similar connectors share a group, for example **Endpoint security** for EDR and XDR products. When several open PRs add to the same list, say "whoever lands last could move it there" instead of asking for a change that depends on merge order.

**Links to sibling connector pages.** Only when the target page exists on `main`. Otherwise, ask that the PR merging second adds the link.

**Style nits.** "Click" becomes "Select". Use US spelling. Replace em dashes and "e.g." with a colon, a new sentence, or "for example". When a page has many of the same nit, post one comment with one example suggestion and list the other lines. Don't post twenty separate nits.

## Don't flag

- A description, intro, or list line that mentions API-only actions. See `availability-and-markers.md`.
- Unchanged copy around the diff, unless a cross-reference in it is broken.
- A restructure beyond the target outline on this page.
- Points a bot or another reviewer already made in an open thread.
