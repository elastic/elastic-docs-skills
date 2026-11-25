# Eval fixtures

Each folder freezes the inputs for one eval, so the result depends on what the agent reads, not on the live state of a PR. Treat these files as the only source of truth. Don't fetch the PR, its files, or Kibana `main` from GitHub, and don't post anything.

Review evals (`1-`, `2-`, `3-`, `5-`) hold one Kibana connector PR at one commit:

| File | Stands for |
| --- | --- |
| `pr.json` | `gh pr view` at that commit: title, head, labels, auto-merge, your existing reviews, open review threads, and the docs files the PR changes (`added` files are commentable on every line) |
| `head/<path>` | Docs files at the PR head, with their Kibana paths. The connector-list snippet is included even when the PR doesn't change it. |
| `spec.json` | Summary of the connector spec at that commit: `supportedFeatureIds`, `docsUrl`, each action's `isTool`, form labels, and, when the eval needs it, the auth types and their fields |
| `main.json` | The `version` in Kibana's `package.json` on `main` when the PR was open |

`4-posting` holds the drafts the user approved and the output of `check_drafts.py` on them. `6-learn-from-round` holds a real posted round: the first drafts, the final drafts, and the output of `compare_drafts.py --live`.
