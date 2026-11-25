#!/usr/bin/env python3
# Copyright Elasticsearch B.V. and/or licensed to Elasticsearch B.V. under one
# or more contributor license agreements. See the NOTICE file distributed with
# this work for additional information regarding copyright
# ownership. Elasticsearch B.V. licenses this file to you under
# the Apache License, Version 2.0 (the "License"); you may
# not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#	http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing,
# software distributed under the License is distributed on an
# "AS IS" BASIS, WITHOUT WARRANTIES OR CONDITIONS OF ANY
# KIND, either express or implied.  See the License for the
# specific language governing permissions and limitations
# under the License.
"""Check connector review drafts against the current state of each PR. Read-only.

Usage: python3 check_drafts.py drafts.json [--preview preview.md]

Exit code 0 when every selected draft can be posted as is, 1 otherwise.
"""

import argparse
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))
from _gh import GhError, commentable_lines, gh_json, gh_list, load_drafts, raw_file, review_body, selected  # noqa: E402

DOCS_PREFIX = "docs/"


def check_review(repo, review):
    n = review["number"]
    problems, warnings = [], []
    pr = gh_json("pr", "view", str(n), "--repo", repo, "--json", "state,headRefOid,autoMergeRequest,isDraft")
    head = pr["headRefOid"]
    print(f"\n#{n}  state={pr['state']}  head={head[:12]}  drafted={review['head'][:12]}")

    if pr["state"] != "OPEN":
        problems.append(f"PR is {pr['state']}")
    if pr["autoMergeRequest"]:
        warnings.append("AUTO-MERGE ON: disable it before posting (--disable-auto-merge)")
    if not head.startswith(review["head"]):
        changed = gh_json("api", f"repos/{repo}/compare/{review['head']}...{head}", "--jq", "[.files[].filename]") or []
        docs = [f for f in changed if f.startswith(DOCS_PREFIX)]
        problems.append("HEAD MOVED since drafting. Docs files changed: " + (", ".join(docs) or "none"))

    files = {f["filename"]: commentable_lines(f.get("patch")) for f in gh_list(f"repos/{repo}/pulls/{n}/files?per_page=100")}
    contents = {}
    for c in selected(review.get("comments")):
        start = c.get("start_line") or c["line"]
        span = f"{start}-{c['line']}" if start != c["line"] else str(c["line"])
        label = f"{c['id']} {c['path'].split('/')[-1]}:{span}"
        lines = files.get(c["path"])
        if lines is None:
            problems.append(f"OUTSIDE DIFF {label}: file not in the PR")
            continue
        if not all(x in lines for x in range(start, c["line"] + 1)):
            problems.append(f"OUTSIDE DIFF {label}")
            continue
        if c["path"] not in contents:
            contents[c["path"]] = raw_file(repo, c["path"], head).split("\n")
        target = "\n".join(contents[c["path"]][start - 1 : c["line"]])
        if c.get("expect") and c["expect"] not in target:
            problems.append(f"EXPECT MISMATCH {label}: expected {c['expect']!r}, found {target[:80]!r}")
        else:
            print(f"  OK {label}")

    for r in selected(review.get("replies")):
        try:
            gh_json("api", f"repos/{repo}/pulls/comments/{r['in_reply_to']}")
            print(f"  OK reply {r['id']} -> {r['in_reply_to']}")
        except GhError:
            problems.append(f"REPLY TARGET MISSING {r['id']}: comment {r['in_reply_to']}")

    for w in warnings:
        print(f"  WARN {w}")
    for p in problems:
        print(f"  BAD  {p}")
    return problems


def write_preview(drafts, path):
    out = []
    for review in drafts["reviews"]:
        comments, replies = selected(review.get("comments")), selected(review.get("replies"))
        out.append(f"# #{review['number']}: {review['event']}, {len(comments)} inline comments, {len(replies)} replies\n")
        out.append("## Review summary\n\n" + review_body(review) + "\n")
        for c in comments:
            where = f"{c['path'].split('/')[-1]}:{str(c['start_line']) + '-' if c.get('start_line') else ''}{c['line']}"
            out.append(f"---\n**{where}** ({c['id']})\n\n{c['body']}\n")
        for r in replies:
            out.append(f"---\n**Reply to comment {r['in_reply_to']}** ({r['id']})\n\n{r['body']}\n")
    Path(path).write_text("\n".join(out))
    print(f"\nPreview written to {path}")


def main():
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("drafts")
    parser.add_argument("--preview", help="write the exact payload to this Markdown file")
    args = parser.parse_args()

    drafts = load_drafts(args.drafts)
    total = 0
    for review in drafts["reviews"]:
        total += len(check_review(drafts["repo"], review))
    if args.preview:
        write_preview(drafts, args.preview)
    print(f"\n{'Ready to post.' if total == 0 else f'{total} problem(s) block posting.'}")
    sys.exit(1 if total else 0)


if __name__ == "__main__":
    main()
