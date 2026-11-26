# Comment style

Write as a docs reviewer leaving quick notes for a developer: short, direct, and friendly. The developer should be able to accept a suggestion in one click and understand why in one line.

Comments post under the name of the user who runs the skill, so write in their voice. If they have a writing-style profile, follow it. The examples below come from one reviewer. Match their length and directness, not their exact phrasing or emoji.

## Rules

- **No thank-yous.** Not in comments, not in the review summary.
- **One-line review summary.** Examples: "Docs LGTM overall, with a few wording suggestions." "A few wording suggestions, and one question about the scopes." Add a second sentence only for something that must change before merge. A general editorial note, from the editorial basics in `page-outline.md`, goes in its own paragraph after the summary line.
- **One point per comment.** A short reason plus a suggestion block. The reason can come before or after the block. Keep it to one or two sentences.
- **Own preferences.** "I'd suggest", "I'd rather", "I think this fits better in…". Explain the effect on readers, not the rule.
- **Report the finding, not its scope.** Say what you found and why it matters to readers. Whether it's fixed in this PR or later is the developer's call, so don't label a point as out of scope or as a follow-up, and don't offer to open one.
- **Ask when you can't verify.** "Could you confirm…?" for any technical claim from the code or the vendor console. Don't explain what the code does.
- **Same change on many lines.** For markers, the first comment explains, and every other marked line gets "Same here:" with its suggestion. A repeated editorial pattern, such as joining semicolons, gets one general note in the review summary with the count, not a comment per line. Inline suggestions are for the lines that need a real rewrite, and they need no comment text when the rewrite speaks for itself.
- **An occasional emoji is fine** (🙏, 😅, `:)`), but not in every comment.
- **Plain style.** No em dashes, no semicolons joining clauses. This also applies to the text inside suggestion blocks, because it lands on the page.
- **Internal notes stay out.** The "why" field, priorities, and verification evidence are for the user, never posted.

## Real examples

These are short on purpose. Match their length.

````markdown
```suggestion
### Test connectors [sentinelone-v2-connector-test]
```
Should be the last subsection under the create H2
````

````markdown
Should those 2 sections be H3s under "Create" since they're the first things to do/consider when setting up the connector?
This has been done for other connectors recently too.
````

````markdown
```suggestion
  stack: preview 9.7
```
We're past the 9.6 window I think by now?
````

````markdown
```suggestion
### Test connectors [microsoft-sql-server-action-configuration]
```
We can put this under Create the connector as the verification step even though it's a bit empty as a section 😅
````

Review summaries from past reviews: "Docs LGTM", "LGTM overall with a few nits", "Docs LGTM, just please double check the stack release version 🙏".

## The marker comment

The first comment on a page with markers explains the change once:

````markdown
"Not yet available" doesn't tell readers what they can do with these actions today. They already work through the API, so I'd rather say that with `_(API only)_`. I've left a suggestion on each marked action, and I'd explain the marker here:

```suggestion
<standard note from availability-and-markers.md>
```

<heads-up line from availability-and-markers.md>
````

Each marked action line then gets "Same here:" plus its suggestion. Add the heads-up line only when the spec has no `docsUrl`.

## Review type

Let the user pick the review type per PR. Default to **Approve** when the comments are wording and outline only, and to **Comment** when a P1 is open. If the user approves a PR with an open P1, mention it once before posting, then respect the choice.
