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

"""Unit checks for GitHub last-match CODEOWNERS behavior."""

import importlib.util
import json
import subprocess
import unittest
from pathlib import Path

SCRIPT = Path(__file__).with_name("match_codeowners.py")
FIXTURES = Path(__file__).resolve().parents[1] / "evals" / "fixtures"


def load_matcher():
    spec = importlib.util.spec_from_file_location("match_codeowners", SCRIPT)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


class MatcherTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.mod = load_matcher()

    def match(self, text, files, teams):
        return self.mod.match_files(text, files, teams)

    def test_directory_glob_ownerless_and_unanchored(self):
        text = "\n".join([
            "* @elastic/docs",
            "docs/* @elastic/docs",
            "**/*.yaml @elastic/cloud-docs",
            "apps/ @elastic/developer-docs",
            "/secrets/ @elastic/developer-docs",
            "/secrets/local/",
            "*.js @js-owner # inline comment",
            "* bad-owner",
        ])
        result = self.match(text, [
            {"filename": "docs/start.md"},
            {"filename": "docs/nested/topic.md"},
            {"filename": "config/settings.yaml"},
            {"filename": "pkg/apps/readme.md"},
            {"filename": "secrets/local/keys.txt"},
            {"filename": "src/app.js"},
        ], ["@elastic/developer-docs", "@elastic/cloud-docs"])

        by_path = {item["path"]: item for item in result["triggers"]}
        self.assertEqual(result["skipped_lines"], 1)
        self.assertIn("config/settings.yaml", by_path)
        self.assertEqual(by_path["config/settings.yaml"]["pattern"], "**/*.yaml")
        self.assertIn("pkg/apps/readme.md", by_path)
        self.assertEqual(by_path["pkg/apps/readme.md"]["pattern"], "apps/")
        self.assertNotIn("docs/start.md", by_path)
        self.assertNotIn("src/app.js", by_path)

        near_paths = [path for group in result["near_misses"] for path in group["paths"]]
        self.assertIn("secrets/local/keys.txt", near_paths)
        cleared = result["near_misses"][0]
        self.assertEqual(cleared["winning_owners"], [])
        self.assertEqual(cleared["earlier_pattern"], "/secrets/")

        rest_paths_owners = {tuple(group["owners"]): group["count"] for group in result["rest_by_owner"]}
        self.assertEqual(rest_paths_owners[("@elastic/docs",)], 2)
        self.assertNotIn("docs/nested/topic.md", by_path)

    def test_docs_star_does_not_match_nested(self):
        regex = self.mod.build_regex("docs/*")
        self.assertIsNotNone(regex.search("docs/start.md"))
        self.assertIsNone(regex.search("docs/nested/topic.md"))

    def test_pr_8516_fixture(self):
        report = json.loads(subprocess.check_output([
            "python3", str(SCRIPT),
            "--repo", "elastic/docs-content",
            "--base-ref", "main",
            "--pr-number", "8516",
            "--codeowners-source", ".github/CODEOWNERS",
            "--codeowners", str(FIXTURES / "pr-8516" / "CODEOWNERS"),
            "--files", str(FIXTURES / "pr-8516" / "files.json"),
            "--owner", "@elastic/developer-docs",
        ], text=True))
        self.assertTrue(report["docs_content"])
        self.assertEqual(report["codeowners_source"], ".github/CODEOWNERS")
        triggers = {item["path"]: item for item in report["triggers"]}
        self.assertEqual(set(triggers), {
            "explore-analyze/ai-features/agent-builder/create-alerts.md",
            "explore-analyze/query-filter/languages/esql-kibana.md",
        })
        self.assertEqual(
            triggers["explore-analyze/ai-features/agent-builder/create-alerts.md"]["owners"],
            ["@elastic/developer-docs"],
        )
        self.assertEqual(
            triggers["explore-analyze/query-filter/languages/esql-kibana.md"]["owners"],
            ["@elastic/developer-docs", "@elastic/ski-docs"],
        )
        self.assertIn("patch", triggers["explore-analyze/ai-features/agent-builder/create-alerts.md"])
        near = [path for group in report["near_misses"] for path in group["paths"]]
        self.assertEqual(near, [
            "solutions/observability/nightshift/get-started.md",
            "solutions/observability/nightshift/investigations.md",
        ])
        self.assertEqual(report["near_misses"][0]["earlier_pattern"], "/solutions/")
        self.assertEqual(report["near_misses"][0]["winning_pattern"], "/solutions/observability/")
        self.assertEqual(report["near_misses"][0]["winning_owners"], ["@elastic/ski-docs"])
        docs = next(group for group in report["rest_by_owner"] if group["owners"] == ["@elastic/docs"])
        self.assertEqual(docs["count"], 2)
        self.assertGreater(report["change"]["additions"], 100)
        self.assertEqual(report["change"]["added"], 1)

    def test_rename_matches_previous_filename(self):
        report = json.loads(subprocess.check_output([
            "python3", str(SCRIPT),
            "--repo", "elastic/kibana",
            "--base-ref", "main",
            "--codeowners", str(FIXTURES / "rename" / "CODEOWNERS"),
            "--files", str(FIXTURES / "rename" / "files.json"),
            "--owner", "@elastic/developer-docs",
        ], text=True))
        self.assertFalse(report["docs_content"])
        self.assertEqual(len(report["triggers"]), 1)
        trigger = report["triggers"][0]
        self.assertEqual(trigger["path"], "new-path/page.md")
        self.assertEqual(trigger["matched_on"], "previous_filename")
        self.assertEqual(trigger["pattern"], "/old-path/")
        self.assertEqual(trigger["current_path"]["owners"], ["@elastic/ski-docs"])
        self.assertEqual(report["rest_by_owner"][0]["owners"], ["@elastic/ski-docs"])
        self.assertEqual(report["rest_by_owner"][0]["count"], 1)


if __name__ == "__main__":
    unittest.main()
