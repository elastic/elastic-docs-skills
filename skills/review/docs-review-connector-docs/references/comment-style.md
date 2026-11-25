# Comment style

Write as a docs reviewer leaving quick notes for a developer: short, direct, and friendly. The developer should be able to accept a suggestion in one click and understand why in one line.

Comments post under the name of the user who runs the skill, so write in their voice. If they have a writing-style profile, follow it. The examples below come from one reviewer. Match their length and directness, not their exact phrasing or emoji.

## Rules

- **No thank-yous.** Not in comments, not in the review summary.
- **One-line review summary.** Examples: "Docs LGTM overall, with a few wording suggestions." "A few wording suggestions, and one question about the scopes." Add a second sentence only for something that must change before merge.
- **One point per comment.** A short reason plus a suggestion block. The reason can come before or after the block. Keep it to one or two sentences.
- **Own preferences.** "I'd suggest", "I'd rather", "I think this fits better in…". Explain the effect on readers, not the rule.
- **Ask when you can't verify.** "Could you confirm…?" for any technical claim from the code or the vendor console. Don't explain what the code does.
- **Same change on many lines.** The first comment explains, and the others say "Same here:" with the suggestion.
- **An occasional emoji is fine** (🙏, 😅, `:)`), but not in every comment.
- **Plain style.** No em dashes, no semicolons joining clauses.
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

Heads-up: `connector_spec_quality_contract.test.ts` checks these lines for the old `_(not yet available)_` text, so it needs a matching change there.
````

Each marked action line then gets "Same here:" plus its suggestion. The heads-up line goes only on pages the test checks.

## Review type

Let the user pick the review type per PR. Default to **Approve** when the comments are wording and outline only, and to **Comment** when a P1 is open. If the user approves a PR with an open P1, mention it once before posting, then respect the choice.
