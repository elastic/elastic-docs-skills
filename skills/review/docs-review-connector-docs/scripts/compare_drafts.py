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
"""Compare the first drafts with what was posted. Read-only.

Usage: python3 compare_drafts.py drafts.initial.json drafts.json [--live]

Prints, per PR, every change between the first drafts and the posted reviews:
review type, summary, drafts turned on or off, drafts added or removed, and
word-level edits to each body. Removed words show as [-old-] and added words as
{+new+}.

With --live, the posted side comes from GitHub: the user's review on the head
recorded in drafts.json, as it reads now. Edits made on GitHub after posting
then count as changes. Without --live, it compares the two files offline.
"""

import argparse
import copy
import difflib
import json
import re
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))
from _gh import gh_list, own_reviews, review_body, viewer_login  # noqa: E402

CONTEXT = 60  # characters of unchanged text kept on each side of an edit
EVENTS = {"APPROVED": "APPROVE", "COMMENTED": "COMMENT", "CHANGES_REQUESTED": "REQUEST_CHANGES"}


def load(path):
    with open(path) as f:
        drafts = json.load(f)
    return drafts.get("repo", "elastic/kibana"), {r["number"]: r for r in drafts["reviews"]}


def flatten_summary(review):
    """Fold selected summary extras into the body, the way GitHub shows it."""
    flat = copy.deepcopy(review)
    flat["body"], flat["body_extras"] = review_body(review), []
    return flat


def live_review(repo, review, viewer):
    """Rebuild a review entry from the user's posted review on GitHub, or None if there is none."""
    n = review["number"]
    posted = [r for r in own_reviews(repo, n, viewer) if r["state"] in EVENTS and r.get("commit_id", "").startswith(review["head"])]
    if not posted:
        return None
    r = posted[-1]
    # The per-review comments endpoint omits line numbers, so filter the PR's comment list instead.
    comments = [c for c in gh_list(f"repos/{repo}/pulls/{n}/comments?per_page=100") if c.get("pull_request_review_id") == r["id"]]
    by_anchor = {(c["path"], c.get("line") or c.get("original_line")): c["body"].replace("\r\n", "\n") for c in comments}
    live = flatten_summary(review)
    live["event"], live["body"] = EVENTS[r["state"]], (r["body"] or "").replace("\r\n", "\n")
    for c in live["comments"]:
        body = by_anchor.pop((c["path"], c["line"]), None)
        c["selected"] = body is not None
        if body is not None:
            c["body"] = body
    for (path, line), body in by_anchor.items():
        live["comments"].append({"id": f"github:{path.split('/')[-1]}:{line}", "path": path, "line": line, "body": body})
    return live


def word_diff(before, after):
    a, b = re.split(r"(\s+)", before), re.split(r"(\s+)", after)
    out = []
    for op, i1, i2, j1, j2 in difflib.SequenceMatcher(None, a, b, autojunk=False).get_opcodes():
        if op == "equal":
            same = "".join(a[i1:i2])
            out.append(same if len(same) <= CONTEXT * 2 + 5 else f"{same[:CONTEXT]} ... {same[-CONTEXT:]}")
            continue
        if i2 > i1:
            out.append("[-" + "".join(a[i1:i2]) + "-]")
        if j2 > j1:
            out.append("{+" + "".join(b[j1:j2]) + "+}")
    return "".join(out)


def is_on(item):
    return item.get("selected", True)


def compare_items(kind, before, after):
    """Yield one line per change between two lists of drafts keyed by id."""
    old = {i["id"]: i for i in before or []}
    new = {i["id"]: i for i in after or []}
    for id_, item in new.items():
        if id_ not in old:
            state = "posted" if is_on(item) else "not posted"
            yield f"- ADDED {kind} {id_} ({state}):\n  {item['body']}"
            continue
        was = old[id_]
        if is_on(was) != is_on(item):
            yield f"- TURNED {'ON' if is_on(item) else 'OFF'} {kind} {id_}"
        if was["body"] != item["body"]:
            yield f"- EDITED {kind} {id_}{'' if is_on(item) else ' (not posted)'}:\n  {word_diff(was['body'], item['body'])}"
        if (was.get("start_line"), was.get("line")) != (item.get("start_line"), item.get("line")):
            yield f"- MOVED {kind} {id_}: line {was.get('line')} -> {item.get('line')}"
    for id_ in old.keys() - new.keys():
        yield f"- REMOVED {kind} {id_}"


def main():
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("initial", help="the drafts as first presented to the user")
    parser.add_argument("final", help="the drafts as posted")
    parser.add_argument("--live", action="store_true", help="read the posted side from GitHub")
    args = parser.parse_args()

    _, initial = load(args.initial)
    repo, final = load(args.final)
    if args.live:
        viewer = viewer_login()
        for n, review in list(final.items()):
            live = live_review(repo, review, viewer)
            if live is None:
                print(f"\n#{n}: no posted review found on GitHub at {review['head'][:12]}, using drafts.json")
                continue
            final[n] = live
            if n in initial:
                initial[n] = flatten_summary(initial[n])
    total = 0
    for n in sorted(initial.keys() | final.keys()):
        if n not in final:
            print(f"\n#{n}: dropped from the round")
            total += 1
            continue
        if n not in initial:
            print(f"\n#{n}: added to the round after the first drafts")
            total += 1
            continue
        was, now = initial[n], final[n]
        changes = []
        if was["event"] != now["event"]:
            changes.append(f"- REVIEW TYPE {was['event']} -> {now['event']}")
        if was["body"] != now["body"]:
            changes.append(f"- SUMMARY:\n  {word_diff(was['body'], now['body'])}")
        for kind, key in (("comment", "comments"), ("summary extra", "body_extras"), ("reply", "replies")):
            changes.extend(compare_items(kind, was.get(key), now.get(key)))
        posted = sum(is_on(c) for c in now.get("comments") or [])
        drafted = sum(is_on(c) for c in was.get("comments") or [])
        print(f"\n#{n}: {drafted} inline comments selected at first, {posted} posted")
        print("\n".join(changes) if changes else "- no changes")
        total += len(changes)
    print(f"\n{total} change(s) in total.")


if __name__ == "__main__":
    main()
