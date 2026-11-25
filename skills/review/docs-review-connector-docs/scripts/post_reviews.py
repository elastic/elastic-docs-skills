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
"""Post one GitHub review per PR from drafts.json, then any thread replies.

Usage: python3 post_reviews.py drafts.json [--yes] [--disable-auto-merge] [--second-review]

Without --yes, prints what it would post and posts nothing. Run check_drafts.py
first, and post only after the user validated the exact payload. A PR where the
user already reviewed the current head is skipped unless --second-review is set.
"""

import argparse
import json
import sys
import time
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))
from _gh import (  # noqa: E402
    GhError,
    gh,
    gh_json,
    gh_list,
    load_drafts,
    own_reviews,
    review_body,
    review_status,
    selected,
    viewer_login,
)

PAUSE_BETWEEN_PRS = 20
RATE_LIMIT_WAIT = 120
SERVER_ERROR_WAIT = 15
MAX_ATTEMPTS = 3


def new_review(repo, n, viewer, head, before):
    """Return a review by the viewer on head that wasn't there before the first attempt."""
    return next((r for r in own_reviews(repo, n, viewer) if r["id"] not in before and r.get("commit_id") == head), None)


def post_review(repo, n, payload, viewer):
    """Post a review. On a 5xx or a rate limit, check whether it posted before retrying."""
    before = {r["id"] for r in own_reviews(repo, n, viewer)}
    for attempt in range(1, MAX_ATTEMPTS + 1):
        found = new_review(repo, n, viewer, payload["commit_id"], before)
        if found:
            print(f"  review already exists: {found['html_url']}")
            return found
        try:
            return json.loads(gh("api", "-X", "POST", f"repos/{repo}/pulls/{n}/reviews", "--input", "-", stdin=json.dumps(payload)))
        except GhError as e:
            if e.is_rate_limited:
                wait = RATE_LIMIT_WAIT
            elif e.is_server_error:
                wait = SERVER_ERROR_WAIT
            else:
                raise
            print(f"  attempt {attempt} failed ({'rate limit' if e.is_rate_limited else 'server error'}), waiting {wait}s")
            time.sleep(wait)
    found = new_review(repo, n, viewer, payload["commit_id"], before)
    if found:
        return found
    raise GhError(f"#{n}: review not posted after {MAX_ATTEMPTS} attempts")


def post_reply(repo, n, reply, viewer):
    thread = gh_list(f"repos/{repo}/pulls/{n}/comments?per_page=100")
    target = int(reply["in_reply_to"])
    if any(c.get("in_reply_to_id") == target and c["user"]["login"] == viewer and c["body"] == reply["body"] for c in thread):
        print(f"  reply {reply['id']} already exists")
        return
    out = gh_json("api", "-X", "POST", f"repos/{repo}/pulls/{n}/comments/{target}/replies", "-f", f"body={reply['body']}")
    print(f"  reply {reply['id']}: {out['html_url']}")


def build_payload(review, head):
    comments = []
    for c in selected(review.get("comments")):
        item = {"path": c["path"], "line": c["line"], "side": "RIGHT", "body": c["body"]}
        if c.get("start_line"):
            item.update(start_line=c["start_line"], start_side="RIGHT")
        comments.append(item)
    return {"commit_id": head, "event": review["event"], "body": review_body(review), "comments": comments}


def main():
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("drafts")
    parser.add_argument("--yes", action="store_true", help="actually post")
    parser.add_argument("--disable-auto-merge", action="store_true", help="turn off auto-merge before posting")
    parser.add_argument("--second-review", action="store_true", help="post even if the user already reviewed this head")
    args = parser.parse_args()

    drafts = load_drafts(args.drafts)
    repo = drafts["repo"]
    viewer = viewer_login()
    failures = 0

    for i, review in enumerate(drafts["reviews"]):
        n = review["number"]
        pr = gh_json("pr", "view", str(n), "--repo", repo, "--json", "headRefOid,autoMergeRequest,state")
        head = pr["headRefOid"]
        payload = build_payload(review, head)
        replies = selected(review.get("replies"))
        print(f"\n#{n}: {payload['event']}, {len(payload['comments'])} comments, {len(replies)} replies")

        pending, on_head, _ = review_status(own_reviews(repo, n, viewer), head)
        skip = None
        if not head.startswith(review["head"]):
            skip = "head moved since drafting. Run check_drafts.py and update the drafts."
        elif pending:
            skip = "you have an unsubmitted review on this PR. Submit or delete it on GitHub first."
        elif on_head and not args.second_review:
            urls = ", ".join(r["html_url"] for r in on_head)
            skip = f"you already reviewed this head ({urls}). Rerun with --second-review if the user wants another review."
        elif pr["autoMergeRequest"] and not args.disable_auto_merge:
            skip = "auto-merge is on. Rerun with --disable-auto-merge once the user agreed."

        if not args.yes:
            print("  summary: " + payload["body"].replace("\n", "\n           "))
            for c in payload["comments"]:
                span = f"{c['start_line']}-{c['line']}" if c.get("start_line") else str(c["line"])
                print(f"  comment: {c['path'].split('/')[-1]}:{span}")
            for r in replies:
                print(f"  reply to comment {r['in_reply_to']}")
            print(f"  {'would SKIP: ' + skip if skip else 'dry run: nothing posted.'} The full comment text is in preview.md.")
            continue
        if skip:
            print(f"  SKIP: {skip}")
            failures += 1
            continue

        if i:
            time.sleep(PAUSE_BETWEEN_PRS)
        if pr["autoMergeRequest"]:
            gh("pr", "merge", str(n), "--repo", repo, "--disable-auto")
            print("  auto-merge disabled")
        try:
            posted = post_review(repo, n, payload, viewer)
        except GhError as e:
            print(f"  FAILED: {e}")
            failures += 1
            continue
        count = len(gh_list(f"repos/{repo}/pulls/{n}/reviews/{posted['id']}/comments?per_page=100"))
        status = "OK" if count == len(payload["comments"]) else "COUNT MISMATCH"
        print(f"  {status}: {posted['html_url']} ({count}/{len(payload['comments'])} comments)")
        failures += status != "OK"
        for reply in replies:
            post_reply(repo, n, reply, viewer)

    sys.exit(1 if failures else 0)


if __name__ == "__main__":
    main()
