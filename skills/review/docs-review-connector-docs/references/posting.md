# Drafts file and posting

Read this before writing `drafts.json`, and again before posting.

## drafts.json

One file holds every draft for the review set. The selection UI edits it, and the scripts read it. Keep it outside the Kibana repo, for example in a scratch directory.

```json
{
  "repo": "elastic/kibana",
  "reviews": [
    {
      "number": 306420,
      "head": "9a429f1fec520d696e81b4d31bfa2280e0ab8dd9",
      "event": "APPROVE",
      "body": "Docs LGTM overall, with a few wording suggestions.",
      "comments": [
        {
          "id": "mde-test",
          "priority": "P3",
          "why": "Recurring outline ask. Not posted.",
          "selected": true,
          "path": "docs/reference/connectors-kibana/microsoft-defender-for-endpoint-action-type.md",
          "line": 62,
          "expect": "## Test connectors",
          "body": "I'd make this the last subsection of **Create connectors in {{kib}}**, since testing is the last step of creating the connector:\n\n```suggestion\n### Test connectors [microsoft-defender-for-endpoint-action-configuration]\n```"
        }
      ],
      "body_extras": [],
      "replies": []
    }
  ]
}
```

Fields:

- `head`: the PR head SHA you read when drafting. The scripts refuse to post if the PR moved.
- `event`: `APPROVE`, `COMMENT`, or `REQUEST_CHANGES`.
- `comments[].line`: the last line of the range, on the new side of the diff. Add `start_line` for a multi-line suggestion. A suggestion replaces every line from `start_line` to `line`. An empty suggestion block deletes them.
- `comments[].expect`: a substring of the target line or lines at `head`. It catches drift that line numbers alone miss.
- `body_extras[]`: `{id, selected, body}` text appended to the review summary, for a point about a file the PR doesn't touch.
- `replies[]`: `{id, selected, in_reply_to, body}` for a reply in an existing review thread. `in_reply_to` is the numeric ID of the thread's first comment, as printed by `list_threads.py`.
- `selected: false` keeps a draft in the file without posting it.

The canvas also reads these optional fields. The other scripts ignore them, and none of them is posted:

- `comments[].title`, `body_extras[].title`, `replies[].title`: a short label for the draft card, for example "RTR sessions: break the paragraph into three".
- `title`, `author`: the PR title and author, for the canvas header.
- `status`: one line on the PR state, such as approvals, auto-merge, and points bots already raised.
- `notes[]`: blockers the user should see before posting, such as a pending review or auto-merge.
- `checks[]`: `{area, finding, status}` rows from step 2, with `OK`, `NO`, or `Open` as the status.

## Check

```bash
python3 <skill-dir>/scripts/check_drafts.py drafts.json --preview preview.md
```

It exits non-zero when something blocks posting:

- **ALREADY REVIEWED:** the user already reviewed the current head. Show the existing review and ask whether a second one makes sense.
- **PENDING REVIEW:** the user has an unsubmitted review on the PR. GitHub allows only one, so `post_reviews.py` can't post a second one. Show the user the pending comments, and offer to add the selected drafts to that review instead. Once the user validates the payload, add each inline draft with the GraphQL `addPullRequestReviewThread` mutation, passing the pending review's `node_id`, `path`, `line`, `side: RIGHT`, and `body`. GitHub doesn't let you set the summary of a pending review, so give the user the summary text to paste when they submit the review on GitHub.
- **HEAD MOVED:** the PR has new commits. It lists the docs files that changed. Re-read them, fix line numbers and `expect`, drop comments the new commits addressed, update `head`, and check again.
- **OUTSIDE DIFF:** the anchor isn't on a line GitHub can comment on. Move the point to `body_extras` or to a line inside a hunk.
- **EXPECT MISMATCH:** the target line doesn't contain `expect`. Re-anchor.
- **AUTO-MERGE ON:** a warning. Include disabling it in the plan you show the user.

`--preview` writes the exact text of every selected review, comment, and reply. Show that file, or its content, as the payload the user validates.

## Post

Only after the user validates the payload in this round:

```bash
python3 <skill-dir>/scripts/post_reviews.py drafts.json --yes [--disable-auto-merge] [--second-review]
```

The script re-checks each head, posts one review per PR with `commit_id` pinned, then posts replies. It skips a PR where the user already reviewed the current head, unless `--second-review` is set. It handles the two known failures this way:

- **5xx:** it waits, checks whether the review posted anyway, and retries only if it didn't.
- **Secondary rate limit (403):** it waits two minutes, checks, and retries, up to three times.

It waits between PRs, then prints each review URL with the posted and expected comment counts. Without `--yes`, it prints each review's type, summary, and comment locations, and posts nothing. The full comment text is in `preview.md`.
