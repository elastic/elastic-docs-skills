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
"""Small helpers around the gh CLI, shared by check_drafts.py and post_reviews.py."""

import json
import re
import subprocess
import sys


class GhError(RuntimeError):
    def __init__(self, message, stderr=""):
        super().__init__(message)
        self.stderr = stderr

    @property
    def is_server_error(self):
        return bool(re.search(r"HTTP 5\d\d|Server Error|Bad Gateway|timed out", self.stderr))

    @property
    def is_rate_limited(self):
        return "secondary rate limit" in self.stderr or "HTTP 429" in self.stderr


def gh(*args, stdin=None):
    """Run gh and return stdout. Raise GhError with stderr on failure."""
    proc = subprocess.run(["gh", *args], input=stdin, capture_output=True, text=True)
    if proc.returncode != 0:
        raise GhError(f"gh {' '.join(args[:3])} failed: {proc.stderr.strip()[:300]}", proc.stderr)
    return proc.stdout


def gh_json(*args):
    out = gh(*args)
    return json.loads(out) if out.strip() else None


def gh_list(path):
    """GET a paginated list endpoint and return all items."""
    out = gh("api", "--paginate", path, "--jq", ".[] | tojson")
    return [json.loads(line) for line in out.splitlines() if line.strip()]


def raw_file(repo, path, ref):
    return gh("api", f"repos/{repo}/contents/{path}?ref={ref}", "-H", "Accept: application/vnd.github.raw")


def commentable_lines(patch):
    """Return the set of new-side line numbers a review comment can target in a file patch."""
    lines, right = set(), 0
    for row in (patch or "").splitlines():
        hunk = re.match(r"^@@ -\d+(?:,\d+)? \+(\d+)", row)
        if hunk:
            right = int(hunk.group(1))
            continue
        if row.startswith("-") or row.startswith("\\"):
            continue
        lines.add(right)
        right += 1
    return lines


def load_drafts(path):
    with open(path) as f:
        drafts = json.load(f)
    if "reviews" not in drafts:
        sys.exit(f"{path}: missing 'reviews' array")
    drafts.setdefault("repo", "elastic/kibana")
    return drafts


def selected(items):
    return [i for i in items or [] if i.get("selected", True)]


def review_body(review):
    extras = [e["body"] for e in selected(review.get("body_extras"))]
    return "\n\n".join([review["body"], *extras])
