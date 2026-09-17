# Branch setup

The commands behind Step 3 of `SKILL.md`. Run this in every repo the work touches, each with its own branch and its own base, because a fork on one side tells you nothing about the other.

## 1. Find the canonical remote

**Never assume `origin` is the canonical repo.** When the checkout is a fork, `origin` is the writer's own copy, and `origin/main` goes stale the moment the fork falls behind. Basing on it starts the work from old content with nothing looking wrong.

Identify it by URL rather than by name, because the name varies and a busy clone can carry dozens of collaborators' forks as remotes:

```
git -C <repo> remote -v | grep '(fetch)' | grep -E 'github\.com[:/]elastic/'
```

| Result | What it means | Base on | Push to |
|---|---|---|---|
| One match, named `origin` | Direct clone | `origin` | `origin` |
| One match under another name, usually `upstream` | Fork | that remote | `origin`, the fork |
| No match | Fork with no canonical remote configured | Ask first | — |
| Several matches | Ambiguous | Ask which is canonical | — |

With no match, offer `git remote add upstream https://github.com/elastic/<repo>.git` rather than guessing. Branching from a fork's own default branch is a fallback the user chooses knowingly, not one you pick for them.

## 2. Resolve the default branch

**Never assume the default branch is `main`.** Fetch first, then read it off the canonical remote:

```
git -C <repo> fetch <canonical>
git -C <repo> symbolic-ref refs/remotes/<canonical>/HEAD    # fallback: gh repo view elastic/<repo> --json defaultBranchRef
```

Base on the remote-tracking ref `<canonical>/<default>`, never on the local branch of the same name, since a local `main` is only as fresh as the last pull. The default branch is the right base in nearly every case; targeting a released version branch instead is an exception the user has to name.

## 3. Check the checkout is safe

Stop and ask in each of these cases. **Never stash, reset, or discard anything to clear the way.**

- **Uncommitted changes**, meaning `git status --porcelain` is non-empty. Switching carries them onto the new branch and mixes unrelated work into yours.
- **Already on a non-default branch.** It may be one the user made for this exact task, or unrelated work in progress. Ask whether to use it or branch fresh.
- **Detached HEAD.**

## 4. Create the branch

Name it from the issue where there is one. `docs-issue-<number>-<short-slug>` is the clearest convention in use in docs-content, though naming there is not uniform, so check recent history before assuming a shape in another repo:

```
gh pr list --repo <owner/repo> --state merged --limit 20 --json headRefName
git -C <repo> switch --no-track -c <branch> <canonical>/<default>
```

**Pass `--no-track`.** Branching from a remote-tracking ref otherwise makes the new branch track `<canonical>/<default>`, because `branch.autoSetupMerge` defaults to true. That upstream is wrong in two ways: a stray `git pull` merges the default branch into the work, and GitHub Desktop reads the upstream to check branch protection, so it warns that a fresh branch is protected. The real upstream gets set when the branch is pushed at gate 3.

## 5. Clean up if the run writes nothing

If Step 4c concludes no docs are needed, or the user declines at gate 1, switch back and delete the branch. It is empty, so nothing is lost.

## Pushing at gate 3

Push the existing branch rather than creating a new one. When the checkout is a fork, push to the fork and open the pull request against the canonical repo:

```
gh pr create --draft --repo elastic/<repo> --head <fork-owner>:<branch>
```
