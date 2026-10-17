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

"""Match changed paths to GitHub CODEOWNERS rules. Last match wins.

Pattern translation follows GitHub's gitignore-style CODEOWNERS rules
(see https://github.com/hmarr/codeowners). The script prints one JSON
object on stdout. It never prints the CODEOWNERS file or a full patch set.
"""

from __future__ import annotations

import argparse
import json
import re
import subprocess
import sys
from pathlib import Path
from urllib.parse import quote

CODEOWNERS_LOCATIONS = (".github/CODEOWNERS", "CODEOWNERS", "docs/CODEOWNERS")
PATCH_LINE_LIMIT = 40
PATCH_FILE_LIMIT = 15
NEAR_MISS_PATH_LIMIT = 10

EMAIL_RE = re.compile(r"\A[A-Z0-9a-z._%+\-]+@[A-Za-z0-9.\-]+\.[A-Za-z]{2,6}\Z")
TEAM_RE = re.compile(r"\A@[a-zA-Z0-9\-]+/[a-zA-Z0-9_\-]+\Z")
USER_RE = re.compile(r"\A@[a-zA-Z0-9\-_]+\Z")
PR_URL_RE = re.compile(r"github\.com/([^/]+)/([^/]+)/pull/(\d+)")


class Rule:
    def __init__(self, pattern: str, owners: list[str], line: int, regex: re.Pattern):
        self.pattern = pattern
        self.owners = owners
        self.line = line
        self.regex = regex

    def matches(self, path: str) -> bool:
        return self.regex.search(path) is not None


def build_regex(pattern: str) -> re.Pattern:
    """Compile one CODEOWNERS pattern. Raises ValueError on a pattern GitHub rejects."""
    if "***" in pattern:
        raise ValueError("pattern cannot contain three consecutive asterisks")
    if pattern == "":
        raise ValueError("empty pattern")
    if pattern == "/":
        return re.compile(r"\A\Z")

    segments = pattern.split("/")
    if segments[0] == "":
        segments = segments[1:]
    elif len(segments) == 1 or (len(segments) == 2 and segments[1] == ""):
        if segments[0] != "**":
            segments = ["**", *segments]

    if len(segments) > 1 and segments[-1] == "":
        segments[-1] = "**"

    last = len(segments) - 1
    need_slash = False
    parts = [r"\A"]
    for index, segment in enumerate(segments):
        if segment == "**":
            if index == 0 and index == last:
                parts.append(r".+")
            elif index == 0:
                parts.append(r"(?:.+/)?")
                need_slash = False
            elif index == last:
                parts.append(r"/.*")
            else:
                parts.append(r"(?:/.+)?")
                need_slash = True
            continue

        if segment == "*":
            if need_slash:
                parts.append("/")
            parts.append(r"[^/]+")
            need_slash = True
            continue

        if need_slash:
            parts.append("/")
        escaped = False
        literal = []
        for char in segment:
            if escaped:
                literal.append(re.escape(char))
                escaped = False
                continue
            if char == "\\":
                escaped = True
                continue
            if char == "*":
                literal.append(r"[^/]*")
            elif char == "?":
                literal.append(r"[^/]")
            else:
                literal.append(re.escape(char))
        parts.append("".join(literal))
        if index == last:
            parts.append(r"(?:/.*)?")
        need_slash = True

    parts.append(r"\Z")
    return re.compile("".join(parts))


def _pattern_char(char: str) -> bool:
    return char.isalnum() or char in "*?. /@_+-:\\()|{}[]~^"


def _owner_char(char: str) -> bool:
    return char.isalnum() or char in ".@/_%+-"


def parse_rule(line: str, line_number: int) -> Rule | None:
    """Return a rule, or None when the line is blank, a comment, or invalid."""
    stripped = line.strip()
    if not stripped or stripped[0] == "#":
        return None

    pattern_chars: list[str] = []
    owners: list[str] = []
    owner_chars: list[str] = []
    state = "pattern"
    escaped = False

    for char in stripped:
        if char == "#":
            break
        if state == "pattern":
            if char == "\\":
                escaped = True
                pattern_chars.append(char)
                continue
            if char in " \t" and not escaped:
                state = "owners"
            elif escaped or _pattern_char(char):
                pattern_chars.append(char)
            else:
                return None
            escaped = False
            continue
        if char in " \t":
            if owner_chars:
                owners.append("".join(owner_chars))
                owner_chars = []
            continue
        if _owner_char(char):
            owner_chars.append(char)
            continue
        return None

    if owner_chars:
        owners.append("".join(owner_chars))

    pattern = "".join(pattern_chars)
    if not pattern:
        return None
    for owner in owners:
        if not (TEAM_RE.match(owner) or USER_RE.match(owner) or EMAIL_RE.match(owner)):
            return None
    try:
        regex = build_regex(pattern)
    except (ValueError, re.error):
        return None
    return Rule(pattern, owners, line_number, regex)


def parse_codeowners(text: str) -> tuple[list[Rule], int]:
    rules = []
    skipped = 0
    for line_number, line in enumerate(text.splitlines(), start=1):
        stripped = line.strip()
        if not stripped or stripped[0] == "#":
            continue
        rule = parse_rule(line, line_number)
        if rule is None:
            skipped += 1
            continue
        rules.append(rule)
    return rules, skipped


def _owner_key(owner: str) -> str:
    return owner.casefold()


def _intersects(owners: list[str], teams: set[str]) -> bool:
    return any(_owner_key(owner) in teams for owner in owners)


def _matching_rules(rules: list[Rule], path: str) -> list[Rule]:
    normalized = path.replace("\\", "/").lstrip("/")
    return [rule for rule in rules if rule.matches(normalized)]


def _outcome(rules: list[Rule], path: str, teams: set[str]) -> tuple[Rule | None, Rule | None, bool]:
    matched = _matching_rules(rules, path)
    if not matched:
        return None, None, False
    winner = matched[-1]
    earlier = None
    for rule in matched[:-1]:
        if _intersects(rule.owners, teams):
            earlier = rule
    return winner, earlier, _intersects(winner.owners, teams)


def _short_patch(patch: str | None, budget: list[int]) -> str | None:
    if not patch or budget[0] <= 0:
        return None
    if len(patch.splitlines()) > PATCH_LINE_LIMIT or len(patch) > 4000:
        return None
    budget[0] -= 1
    return patch


def _rule_fields(rule: Rule | None) -> dict:
    if rule is None:
        return {"pattern": None, "line": None, "owners": []}
    return {"pattern": rule.pattern, "line": rule.line, "owners": list(rule.owners)}


def match_files(codeowners_text: str, files: list[dict], teams: list[str]) -> dict:
    rules, skipped = parse_codeowners(codeowners_text)
    team_set = {_owner_key(team) for team in teams}
    triggers = []
    near_groups: dict[tuple, dict] = {}
    rest_groups: dict[tuple, dict] = {}
    patch_budget = [PATCH_FILE_LIMIT]
    change = {
        "files": 0,
        "additions": 0,
        "deletions": 0,
        "added": 0,
        "modified": 0,
        "removed": 0,
        "renamed": 0,
        "copied": 0,
    }

    for entry in files:
        path = entry.get("filename") or entry.get("path")
        if not path:
            continue
        previous = entry.get("previous_filename") or None
        status = entry.get("status") or "modified"
        additions = int(entry.get("additions") or 0)
        deletions = int(entry.get("deletions") or 0)
        change["files"] += 1
        change["additions"] += additions
        change["deletions"] += deletions
        if status in change:
            change[status] += 1

        path_winner, path_earlier, path_hit = _outcome(rules, path, team_set)
        prev_winner, prev_earlier, prev_hit = (None, None, False)
        if previous:
            prev_winner, prev_earlier, prev_hit = _outcome(rules, previous, team_set)

        if path_hit or prev_hit:
            if path_hit:
                winner = path_winner
                matched_on = "path"
            else:
                winner = prev_winner
                matched_on = "previous_filename"
            item = {
                "path": path,
                "previous_filename": previous,
                "matched_on": matched_on,
                "status": status,
                "additions": additions,
                "deletions": deletions,
                "pattern": winner.pattern if winner else None,
                "line": winner.line if winner else None,
                "owners": list(winner.owners) if winner else [],
            }
            if matched_on == "previous_filename" and path_winner is not None:
                item["current_path"] = _rule_fields(path_winner)
            patch = _short_patch(entry.get("patch"), patch_budget)
            if patch is not None:
                item["patch"] = patch
            triggers.append(item)
            continue

        earlier = path_earlier or prev_earlier
        winner = path_winner if path_earlier else (prev_winner if prev_earlier else path_winner)
        if earlier is not None and winner is not None and not _intersects(winner.owners, team_set):
            key = (
                earlier.pattern,
                earlier.line,
                tuple(earlier.owners),
                winner.pattern,
                winner.line,
                tuple(winner.owners),
            )
            group = near_groups.setdefault(
                key,
                {
                    "earlier_pattern": earlier.pattern,
                    "earlier_line": earlier.line,
                    "earlier_owners": list(earlier.owners),
                    "winning_pattern": winner.pattern,
                    "winning_line": winner.line,
                    "winning_owners": list(winner.owners),
                    "count": 0,
                    "paths": [],
                },
            )
            group["count"] += 1
            if len(group["paths"]) < NEAR_MISS_PATH_LIMIT:
                group["paths"].append(path)
            continue

        owners = tuple(path_winner.owners) if path_winner else ()
        group = rest_groups.setdefault(
            owners,
            {
                "owners": list(owners),
                "count": 0,
                "additions": 0,
                "deletions": 0,
            },
        )
        group["count"] += 1
        group["additions"] += additions
        group["deletions"] += deletions

    near_misses = []
    for group in near_groups.values():
        if group["count"] > len(group["paths"]):
            group["paths_omitted"] = group["count"] - len(group["paths"])
        near_misses.append(group)

    return {
        "skipped_lines": skipped,
        "change": change,
        "triggers": triggers,
        "near_misses": near_misses,
        "rest_by_owner": sorted(rest_groups.values(), key=lambda item: (-item["count"], item["owners"])),
    }


def _normalize_owner(owner: str) -> str:
    owner = owner.strip()
    if owner and not owner.startswith("@") and "/" in owner and "@" not in owner:
        owner = "@" + owner
    return owner


def _run_gh(args: list[str]) -> subprocess.CompletedProcess[str]:
    return subprocess.run(["gh", *args], capture_output=True, text=True)


def _decode_json_values(text: str) -> list:
    decoder = json.JSONDecoder()
    index = 0
    length = len(text)
    values = []
    while index < length:
        while index < length and text[index].isspace():
            index += 1
        if index >= length:
            break
        value, end = decoder.raw_decode(text, index)
        values.append(value)
        index = end
    return values


def _gh_pages(args: list[str]) -> list:
    completed = _run_gh(args)
    if completed.returncode != 0:
        raise RuntimeError(completed.stderr.strip() or f"gh {' '.join(args)} failed")
    pages = _decode_json_values(completed.stdout)
    rows = []
    for page in pages:
        if isinstance(page, list):
            rows.extend(page)
        else:
            rows.append(page)
    return rows


def _parse_pr(pr: str, repo: str | None) -> tuple[str, int]:
    match = PR_URL_RE.search(pr)
    if match:
        return f"{match.group(1)}/{match.group(2)}", int(match.group(3))
    if pr.isdigit():
        if not repo:
            completed = _run_gh(["repo", "view", "--json", "nameWithOwner", "--jq", ".nameWithOwner"])
            if completed.returncode != 0:
                raise RuntimeError(completed.stderr.strip() or "gh repo view failed")
            repo = completed.stdout.strip()
        return repo, int(pr)
    raise RuntimeError(f"not a pull request number or GitHub URL: {pr}")


def _elastic_teams() -> tuple[list[str], str | None]:
    completed = _run_gh(["api", "--paginate", "user/teams"])
    if completed.returncode != 0:
        return [], completed.stderr.strip() or "user/teams failed. Pass an explicit @org/team."
    teams = []
    for team in _flatten_teams(_decode_json_values(completed.stdout)):
        org = ((team.get("organization") or {}).get("login") or "")
        slug = team.get("slug")
        if org.casefold() == "elastic" and slug:
            teams.append(f"@{org}/{slug}")
    if not teams:
        return [], "No Elastic teams for the authenticated user. Pass an explicit @org/team."
    return teams, None


def _fetch_live(repo: str, number: int, owners: list[str]) -> dict:
    view = _run_gh([
        "pr", "view", str(number), "--repo", repo,
        "--json", "baseRefName,number,url",
    ])
    if view.returncode != 0:
        raise RuntimeError(view.stderr.strip() or "gh pr view failed")
    meta = json.loads(view.stdout)
    base_ref = meta.get("baseRefName") or "HEAD"
    header = {
        "repo": repo,
        "pr": meta.get("number", number),
        "url": meta.get("url"),
        "base_ref": base_ref,
        "codeowners_source": None,
        "teams": list(owners),
        "teams_error": None,
        "codeowners_text": "",
        "files": [],
    }
    if not header["teams"]:
        teams, teams_error = _elastic_teams()
        header["teams"] = teams
        header["teams_error"] = teams_error
        if teams_error:
            return header

    header["files"] = _gh_pages(["api", "--paginate", f"repos/{repo}/pulls/{number}/files"])

    ref = quote(base_ref, safe="")
    last_error = "CODEOWNERS not found"
    for location in CODEOWNERS_LOCATIONS:
        completed = _run_gh([
            "api",
            "-H", "Accept: application/vnd.github.raw",
            f"repos/{repo}/contents/{location}?ref={ref}",
        ])
        if completed.returncode == 0 and not completed.stdout.lstrip().startswith('{"message"'):
            header["codeowners_text"] = completed.stdout
            header["codeowners_source"] = location
            return header
        last_error = completed.stderr.strip() or last_error
    raise RuntimeError(last_error)


def _flatten_teams(values: list) -> list:
    rows = []
    for value in values:
        if isinstance(value, list):
            rows.extend(value)
        elif isinstance(value, dict):
            rows.append(value)
    return rows


def _emit(payload: dict) -> int:
    json.dump(payload, sys.stdout, indent=2)
    sys.stdout.write("\n")
    if payload.get("error"):
        return 1
    return 0


def build_payload(header: dict, codeowners_text: str, files: list[dict], teams: list[str]) -> dict:
    matched = match_files(codeowners_text, files, teams) if not header.get("teams_error") else {
        "skipped_lines": 0,
        "change": {
            "files": len(files),
            "additions": 0,
            "deletions": 0,
            "added": 0,
            "modified": 0,
            "removed": 0,
            "renamed": 0,
            "copied": 0,
        },
        "triggers": [],
        "near_misses": [],
        "rest_by_owner": [],
    }
    repo = header.get("repo") or ""
    payload = {
        "repo": repo,
        "pr": header.get("pr"),
        "url": header.get("url"),
        "base_ref": header.get("base_ref"),
        "codeowners_source": header.get("codeowners_source"),
        "docs_content": repo.casefold() == "elastic/docs-content",
        "teams": teams,
        "teams_error": header.get("teams_error"),
        **matched,
    }
    return payload


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Match pull request files against CODEOWNERS.")
    parser.add_argument("pr", nargs="?", help="Pull request number or GitHub URL")
    parser.add_argument("owners", nargs="*", help="Owner to test, such as @org/team")
    parser.add_argument("--owner", action="append", default=[], help="Owner to test. Repeatable.")
    parser.add_argument("--repo", help="owner/name. Required for a bare PR number when not in that repo.")
    parser.add_argument("--base-ref", help="Base ref label recorded in the JSON.")
    parser.add_argument("--pr-number", type=int, help="PR number to record for an offline fixture.")
    parser.add_argument("--codeowners", help="Path to a CODEOWNERS file. Offline mode.")
    parser.add_argument("--codeowners-source", help="Label for the CODEOWNERS path, such as .github/CODEOWNERS.")
    parser.add_argument("--files", help="Path to a GitHub pull request files JSON array. Offline mode.")
    args = parser.parse_args(argv)

    owners = [_normalize_owner(owner) for owner in [*args.owners, *args.owner] if owner.strip()]

    try:
        if args.codeowners or args.files:
            if not args.codeowners or not args.files:
                raise RuntimeError("offline mode needs both --codeowners and --files")
            if not args.repo:
                raise RuntimeError("offline mode needs --repo")
            if not owners:
                raise RuntimeError("offline mode needs at least one owner")
            codeowners_text = Path(args.codeowners).read_text()
            files = json.loads(Path(args.files).read_text())
            if not isinstance(files, list):
                raise RuntimeError("--files must be a JSON array")
            header = {
                "repo": args.repo,
                "pr": args.pr_number,
                "url": None,
                "base_ref": args.base_ref,
                "codeowners_source": args.codeowners_source or args.codeowners,
                "teams_error": None,
            }
            return _emit(build_payload(header, codeowners_text, files, owners))

        if not args.pr:
            raise RuntimeError("pass a pull request number or URL, or pass --codeowners and --files")
        repo, number = _parse_pr(args.pr, args.repo)
        live = _fetch_live(repo, number, owners)
        teams = live["teams"]
        return _emit(build_payload(live, live["codeowners_text"], live["files"], teams))
    except (OSError, json.JSONDecodeError, RuntimeError) as exc:
        return _emit({"error": str(exc)})


if __name__ == "__main__":
    sys.exit(main())
