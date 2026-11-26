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
"""Build the draft-selection canvas for Cursor from drafts.json. Read-only on GitHub.

Usage: python3 build_canvas.py drafts.json --out <canvases-dir>/<name>.canvas.tsx

Reads each anchored line at the drafted head, so the canvas shows the same diff the
developer gets. Fills assets/review-canvas.tsx and writes the result to --out.
"""

import argparse
import datetime
import json
import re
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))
from _gh import load_drafts, raw_file  # noqa: E402

TEMPLATE = Path(__file__).parent.parent / "assets" / "review-canvas.tsx"
DATA_SLOT = re.compile(r"/\*DATA:BEGIN\*/.*?/\*DATA:END\*/", re.S)


def location(c):
    name = c["path"].split("/")[-1]
    start = c.get("start_line")
    return f"{name}:{start}-{c['line']}" if start else f"{name}:{c['line']}"


def build(drafts):
    repo = drafts["repo"]
    files = {}
    prs = []
    for review in drafts["reviews"]:
        head = review["head"]
        items = []
        for c in review.get("comments") or []:
            key = (c["path"], head)
            if key not in files:
                files[key] = raw_file(repo, c["path"], head).split("\n")
            start = c.get("start_line") or c["line"]
            items.append({
                "id": c["id"],
                "kind": "inline",
                "priority": c.get("priority", "P3"),
                "title": c.get("title") or c.get("expect") or c["id"],
                "why": c.get("why", ""),
                "selected": c.get("selected", True),
                "body": c["body"],
                "location": location(c),
                "startLine": start,
                "original": "\n".join(files[key][start - 1 : c["line"]]),
            })
        for e in review.get("body_extras") or []:
            items.append({
                "id": e["id"], "kind": "summary", "priority": e.get("priority", "P3"),
                "title": e.get("title") or e["id"], "why": e.get("why", ""),
                "selected": e.get("selected", True), "body": e["body"], "location": "review summary",
            })
        for r in review.get("replies") or []:
            items.append({
                "id": r["id"], "kind": "reply", "priority": r.get("priority", "P3"),
                "title": r.get("title") or r["id"], "why": r.get("why", ""),
                "selected": r.get("selected", True), "body": r["body"],
                "location": f"reply to comment {r['in_reply_to']}",
            })
        prs.append({
            "number": review["number"],
            "title": review.get("title", ""),
            "author": review.get("author", ""),
            "head": head,
            "status": review.get("status", ""),
            "summary": review["body"],
            "event": review["event"],
            "notes": review.get("notes", []),
            "checks": review.get("checks", []),
            "drafts": items,
        })
    return {"repo": repo, "generated": datetime.date.today().isoformat(), "prs": prs}


def main():
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("drafts")
    parser.add_argument("--out", required=True, help="path of the .canvas.tsx file to write")
    args = parser.parse_args()

    if not args.out.endswith(".canvas.tsx"):
        sys.exit("--out must end in .canvas.tsx")
    data = build(load_drafts(args.drafts))
    template = TEMPLATE.read_text()
    if not DATA_SLOT.search(template):
        sys.exit(f"{TEMPLATE}: data markers not found")
    out = DATA_SLOT.sub(lambda _: json.dumps(data, ensure_ascii=False, indent=2), template, count=1)
    Path(args.out).write_text(out)
    n = sum(len(p["drafts"]) for p in data["prs"])
    print(f"Wrote {args.out}: {len(data['prs'])} PR(s), {n} draft(s)")


if __name__ == "__main__":
    main()
