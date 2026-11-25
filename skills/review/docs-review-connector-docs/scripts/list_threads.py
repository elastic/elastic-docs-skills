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
"""List the inline review threads on a PR, bots included. Read-only.

Usage: python3 list_threads.py <pr-number> [--repo elastic/kibana] [--docs-only]

Prints one block per thread: file and line, the ID to use as `in_reply_to`,
and each comment with its author.
"""

import argparse
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))
from _gh import gh_list  # noqa: E402


def main():
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("number")
    parser.add_argument("--repo", default="elastic/kibana")
    parser.add_argument("--docs-only", action="store_true", help="only threads on files under docs/")
    args = parser.parse_args()

    threads = {}
    for c in gh_list(f"repos/{args.repo}/pulls/{args.number}/comments?per_page=100"):
        threads.setdefault(c.get("in_reply_to_id") or c["id"], []).append(c)

    shown = 0
    for root, comments in threads.items():
        first = comments[0]
        if args.docs_only and not first["path"].startswith("docs/"):
            continue
        line = first.get("line")
        where = f"{first['path']}:{line}" if line else f"{first['path']} (outdated, was line {first.get('original_line')})"
        print(f"\n## {where}  in_reply_to={root}")
        for c in comments:
            print(f"- {c['user']['login']}: {c['body'].strip()}")
        shown += 1
    print(f"\n{shown} thread(s).")


if __name__ == "__main__":
    main()
