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

Usage: python3 post_reviews.py drafts.json [--yes] [--disable-auto-merge]

Without --yes, prints what it would post and posts nothing. Run check_drafts.py
first, and post only after the user validated the exact payload.
"""

import argparse
import json
import sys
import time
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))
from _gh import GhError, gh, gh_json, gh_list, load_drafts, review_body, selected  # noqa: E402

PAUSE_BETWEEN_PRS = 20
RATE_LIMIT_WAIT = 120
SERVER_ERROR_WAIT = 15
MAX_ATTEMPTS = 3


def existing_review(repo, n, viewer, head, body):
    for r in gh_list(f"repos/{repo}/pulls/{n}/reviews?per_page=100"):
        if r["user"]["login"] == viewer and r.get("commit_id") == head and r.get("body") == body:
            return r
    return None


def post_review(repo, n, payload, viewer):
    """Post a review. On a 5xx or a rate limit, check whether it posted before retrying."""
    for attempt in range(1, MAX_ATTEMPTS + 1):
        found = existing_review(repo, n, viewer, payload["commit_id"], payload["body"])
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
    found = existing_review(repo, n, viewer, payload["commit_id"], payload["body"])
    if found:
        return found
    raise GhError(f"#{n}: review not posted after {MAX_ATTEMPTS} attempts")


def post_reply(repo, n, reply, viewer):
    thread = gh_list(f"repos/{repo}/pulls/{n}/comments?per_page=100")
    if any(c.get("in_reply_to_id") == reply["in_reply_to"] and c["user"]["login"] == viewer and c["body"] == reply["body"] for c in thread):
        print(f"  reply {reply['id']} already exists")
        return
    out = gh_json("api", "-X", "POST", f"repos/{repo}/pulls/{n}/comments/{reply['in_reply_to']}/replies", "-f", f"body={reply['body']}")
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
    args = parser.parse_args()

    drafts = load_drafts(args.drafts)
    repo = drafts["repo"]
    viewer = gh("api", "user", "--jq", ".login").strip()
    failures = 0

    for i, review in enumerate(drafts["reviews"]):
        n = review["number"]
        pr = gh_json("pr", "view", str(n), "--repo", repo, "--json", "headRefOid,autoMergeRequest,state")
        payload = build_payload(review, pr["headRefOid"])
        replies = selected(review.get("replies"))
        print(f"\n#{n}: {payload['event']}, {len(payload['comments'])} comments, {len(replies)} replies")

        if not pr["headRefOid"].startswith(review["head"]):
            print("  SKIP: head moved since drafting. Run check_drafts.py and update the drafts.")
            failures += 1
            continue
        if pr["autoMergeRequest"] and not args.disable_auto_merge:
            print("  SKIP: auto-merge is on. Rerun with --disable-auto-merge once the user agreed.")
            failures += 1
            continue
        if not args.yes:
            print("  dry run: nothing posted")
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
