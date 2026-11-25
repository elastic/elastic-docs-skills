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
"""Compare the first drafts with what was posted. Read-only, works offline.

Usage: python3 compare_drafts.py drafts.initial.json drafts.json

Prints, per PR, every change between the two files: review type, summary,
drafts turned on or off, drafts added or removed, and word-level edits to each
body. Removed words show as [-old-] and added words as {+new+}.
"""

import argparse
import difflib
import json
import re

CONTEXT = 60  # characters of unchanged text kept on each side of an edit


def load(path):
    with open(path) as f:
        return {r["number"]: r for r in json.load(f)["reviews"]}


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
    args = parser.parse_args()

    initial, final = load(args.initial), load(args.final)
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
