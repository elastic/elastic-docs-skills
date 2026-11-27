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
"""Copy the selections and edits saved in the canvas back into drafts.json. Offline.

Usage: python3 apply_canvas.py drafts.json <name>.canvas.data.json

Cursor saves the canvas state next to the canvas, in <name>.canvas.data.json. This
script applies its selected, edits, summaries, and events to drafts.json in place,
and prints every change so the user can confirm it.
"""

import argparse
import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))
from _gh import load_drafts  # noqa: E402


def main():
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("drafts")
    parser.add_argument("state")
    args = parser.parse_args()

    drafts = load_drafts(args.drafts)
    state_path = Path(args.state)
    state = json.loads(state_path.read_text()) if state_path.exists() else {}
    selected = state.get("selected", {})
    edits = state.get("edits", {})
    summaries = state.get("summaries", {})
    events = state.get("events", {})

    known = set()
    changes = []
    for review in drafts["reviews"]:
        n = str(review["number"])
        if n in summaries and summaries[n] != review["body"]:
            review["body"] = summaries[n]
            changes.append(f"#{n} summary edited")
        if n in events and events[n] != review["event"]:
            changes.append(f"#{n} event {review['event']} -> {events[n]}")
            review["event"] = events[n]
        for group in ("comments", "body_extras", "replies"):
            for item in review.get(group) or []:
                known.add(item["id"])
                if item["id"] in selected and selected[item["id"]] != item.get("selected", True):
                    item["selected"] = selected[item["id"]]
                    changes.append(f"#{n} {item['id']} {'selected' if item['selected'] else 'unselected'}")
                if item["id"] in edits and edits[item["id"]] != item["body"]:
                    item["body"] = edits[item["id"]]
                    changes.append(f"#{n} {item['id']} edited")

    stale = sorted((set(selected) | set(edits)) - known)
    Path(args.drafts).write_text(json.dumps(drafts, indent=2, ensure_ascii=False) + "\n")
    for c in changes:
        print(c)
    if stale:
        print("Ignored canvas state for IDs no longer in drafts.json: " + ", ".join(stale))
    print(f"{len(changes)} change(s) applied to {args.drafts}")


if __name__ == "__main__":
    main()
