#!/usr/bin/env python3
# Copyright Elasticsearch B.V. and/or licensed to Elasticsearch B.V. under one
# or more contributor license agreements. See the NOTICE file distributed with
# this work for additional information regarding copyright
# ownership. Elasticsearch B.V. licenses this file to you under
# the Apache License, Version 2.0 (the "License"); you may
# not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
# 	http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing,
# software distributed under the License is distributed on an
# "AS IS" BASIS, WITHOUT WARRANTIES OR CONDITIONS OF ANY
# KIND, either express or implied.  See the License for the
# specific language governing permissions and limitations
# under the License.

"""Generate a single-page skills catalog and JSON index for GitHub Pages."""

import json
import re
from pathlib import Path

SKILLS_DIR = Path("skills")
OUT_DIR = Path("_site")

REPO_URL = "https://github.com/elastic/elastic-docs-skills"
INSTALL_COMMANDS = {
    "Install": "curl -fsSL https://ela.st/docs-skills-install | bash",
    "List": "curl -fsSL https://ela.st/docs-skills-install | bash -s -- --list",
    "Update": "curl -fsSL https://ela.st/docs-skills-install | bash -s -- --update",
    "Skills CLI": "npx --yes skills@latest add elastic/elastic-docs-skills -g -a claude-code",
}

CATEGORY_META = {
    "authoring": {
        "icon": "edit-3",
        "color": "#00BFB3",
        "label": "Authoring",
        "description": "Skills that help write or edit documentation content",
    },
    "project": {
        "icon": "layers",
        "color": "#1BA9F5",
        "label": "Project",
        "description": "Skills scoped to specific Elastic product areas",
    },
    "review": {
        "icon": "check-circle",
        "color": "#F04E98",
        "label": "Review",
        "description": "Skills that validate, lint, or check existing content",
    },
    "workflow": {
        "icon": "git-branch",
        "color": "#FEC514",
        "label": "Workflow",
        "description": "Skills for meta-tasks like retros, session analysis, and project management",
    },
}


def parse_frontmatter(path: Path) -> dict | None:
    text = path.read_text()
    match = re.match(r"^---\n(.+?)\n---", text, re.DOTALL)
    if not match:
        return None
    fm = {}
    for line in match.group(1).splitlines():
        if line.startswith("  - "):
            fm.setdefault("_last_list", []).append(line[4:].strip())
            fm[fm["_last_key"]] = fm["_last_list"]
            continue
        if ":" in line:
            key, _, val = line.partition(":")
            key = key.strip()
            val = val.strip()
            if val:
                fm[key] = val
            else:
                fm["_last_key"] = key
                fm["_last_list"] = []
                fm[key] = []
    fm.pop("_last_key", None)
    fm.pop("_last_list", None)
    return fm


def collect_skills() -> dict[str, list[dict]]:
    categories: dict[str, list[dict]] = {}
    for skill_md in sorted(SKILLS_DIR.glob("**/SKILL.md")):
        parts = skill_md.relative_to(SKILLS_DIR).parts
        if len(parts) < 3:
            continue
        category = parts[0]
        fm = parse_frontmatter(skill_md)
        if not fm or "name" not in fm:
            continue
        fm["category"] = category
        fm["_path"] = str(skill_md)
        categories.setdefault(category, []).append(fm)
    return categories


def render_html(categories: dict[str, list[dict]]) -> str:
    total = sum(len(v) for v in categories.values())

    cards_html = ""
    for cat, skills in sorted(categories.items()):
        meta = CATEGORY_META.get(cat, {"icon": "box", "color": "#888", "label": cat.title(), "description": ""})
        cards_html += f"""
    <section class="category" id="{cat}">
      <div class="category-header">
        <div class="category-icon" style="--cat-color: {meta['color']}">
          <i data-feather="{meta['icon']}"></i>
        </div>
        <div>
          <h2>{meta['label']}</h2>
          <p class="category-desc">{meta['description']}</p>
        </div>
        <span class="badge" style="--cat-color: {meta['color']}">{len(skills)}</span>
      </div>
      <div class="skills-grid">
"""
        for skill in sorted(skills, key=lambda s: s["name"]):
            name = skill["name"]
            version = skill.get("version", "")
            desc = skill.get("description", "")
            # Truncate long descriptions for the card
            short_desc = desc if len(desc) <= 160 else desc[:157] + "..."
            context = skill.get("context", "")
            auto = skill.get("disable-model-invocation", "") != "true"
            sources = skill.get("sources", [])
            if isinstance(sources, str):
                sources = [sources]

            tags_html = ""
            if context == "fork":
                tags_html += '<span class="tag tag-readonly">read-only</span>'
            if auto:
                tags_html += '<span class="tag tag-auto">auto-trigger</span>'
            else:
                tags_html += '<span class="tag tag-manual">manual</span>'

            sources_html = ""
            if sources:
                sources_html = f'<div class="sources">{len(sources)} source{"s" if len(sources) != 1 else ""}</div>'

            skill_url = f"{REPO_URL}/blob/main/{skill['_path']}"
            cards_html += f"""
        <a class="skill-card" href="{skill_url}" target="_blank" rel="noopener">
          <div class="skill-header">
            <code class="skill-name">/{name}</code>
            <span class="version">v{version}</span>
          </div>
          <p class="skill-desc">{short_desc}</p>
          <div class="skill-footer">
            <div class="tags">{tags_html}</div>
            {sources_html}
          </div>
        </a>
"""
        cards_html += """
      </div>
    </section>
"""

    return f"""<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="utf-8">
  <meta name="viewport" content="width=device-width, initial-scale=1">
  <title>Elastic Docs Skills Catalogue</title>
  <link rel="preconnect" href="https://fonts.googleapis.com">
  <link href="https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700&family=JetBrains+Mono:wght@400;500&display=swap" rel="stylesheet">
  <script src="https://unpkg.com/feather-icons"></script>
  <style>
    :root {{
      --bg: #0D1117;
      --surface: #161B22;
      --surface-hover: #1C2129;
      --border: #30363D;
      --text: #E6EDF3;
      --text-muted: #8B949E;
      --accent: #00BFB3;
    }}

    * {{ margin: 0; padding: 0; box-sizing: border-box; }}

    body {{
      font-family: 'Inter', -apple-system, BlinkMacSystemFont, sans-serif;
      background: var(--bg);
      color: var(--text);
      line-height: 1.6;
      min-height: 100vh;
    }}

    .hero {{
      text-align: center;
      padding: 4rem 2rem 3rem;
      background: linear-gradient(180deg, #161B22 0%, var(--bg) 100%);
      border-bottom: 1px solid var(--border);
    }}

    .hero-logo {{
      display: inline-flex;
      align-items: center;
      gap: 0.75rem;
      margin-bottom: 1.5rem;
    }}

    .hero-logo svg {{
      color: var(--accent);
    }}

    .hero h1 {{
      font-size: 2.5rem;
      font-weight: 700;
      letter-spacing: -0.02em;
      margin-bottom: 0.5rem;
    }}

    .hero h1 span {{
      background: linear-gradient(135deg, #00BFB3, #F04E98);
      -webkit-background-clip: text;
      -webkit-text-fill-color: transparent;
      background-clip: text;
    }}

    .hero p {{
      color: var(--text-muted);
      font-size: 1.125rem;
      max-width: 600px;
      margin: 0 auto;
    }}

    .stats {{
      display: flex;
      justify-content: center;
      gap: 2rem;
      margin-top: 2rem;
    }}

    .stat {{
      text-align: center;
    }}

    .stat-value {{
      font-size: 1.75rem;
      font-weight: 700;
      color: var(--accent);
    }}

    .stat-label {{
      font-size: 0.8rem;
      color: var(--text-muted);
      text-transform: uppercase;
      letter-spacing: 0.05em;
    }}

    .container {{
      max-width: 1100px;
      margin: 0 auto;
      padding: 2rem;
    }}

    .category {{
      margin-bottom: 3rem;
    }}

    .category-header {{
      display: flex;
      align-items: center;
      gap: 1rem;
      margin-bottom: 1.5rem;
      padding-bottom: 1rem;
      border-bottom: 1px solid var(--border);
    }}

    .category-icon {{
      width: 44px;
      height: 44px;
      border-radius: 12px;
      background: color-mix(in srgb, var(--cat-color) 15%, transparent);
      display: flex;
      align-items: center;
      justify-content: center;
      color: var(--cat-color);
      flex-shrink: 0;
    }}

    .category-icon svg {{
      width: 22px;
      height: 22px;
    }}

    .category-header h2 {{
      font-size: 1.25rem;
      font-weight: 600;
    }}

    .category-desc {{
      color: var(--text-muted);
      font-size: 0.875rem;
      margin-top: 0.125rem;
    }}

    .badge {{
      margin-left: auto;
      background: color-mix(in srgb, var(--cat-color) 15%, transparent);
      color: var(--cat-color);
      font-size: 0.8rem;
      font-weight: 600;
      padding: 0.25rem 0.75rem;
      border-radius: 999px;
      flex-shrink: 0;
    }}

    .skills-grid {{
      display: grid;
      grid-template-columns: repeat(auto-fill, minmax(320px, 1fr));
      gap: 1rem;
    }}

    .skill-card {{
      background: var(--surface);
      border: 1px solid var(--border);
      border-radius: 12px;
      padding: 1.25rem;
      transition: border-color 0.2s, transform 0.2s, box-shadow 0.2s;
      display: flex;
      flex-direction: column;
      text-decoration: none;
      color: inherit;
      cursor: pointer;
    }}

    .skill-card:hover {{
      border-color: var(--accent);
      transform: translateY(-2px);
      box-shadow: 0 4px 24px rgba(0, 191, 179, 0.08);
    }}

    .install-banner {{
      margin-top: 2rem;
      display: inline-flex;
      flex-direction: column;
      align-items: stretch;
      gap: 0.5rem;
      width: min(100%, 900px);
    }}

    .install-row {{
      display: flex;
      align-items: center;
      gap: 0.5rem;
      width: 100%;
    }}

    .cmd-label {{
      min-width: 74px;
      text-align: right;
      color: var(--text-muted);
      font-size: 0.8rem;
      font-weight: 600;
    }}

    .install-banner code {{
      background: var(--surface);
      border: 1px solid var(--border);
      padding: 0.5rem 1rem;
      border-radius: 8px;
      font-family: 'JetBrains Mono', monospace;
      font-size: 0.8rem;
      color: var(--text);
      user-select: all;
      text-align: left;
      flex: 1;
      overflow-x: auto;
    }}

    .install-banner .copy-btn {{
      background: var(--surface);
      border: 1px solid var(--border);
      border-radius: 8px;
      padding: 0.5rem;
      cursor: pointer;
      color: var(--text-muted);
      display: flex;
      align-items: center;
      justify-content: center;
      transition: color 0.2s, border-color 0.2s;
    }}

    .install-banner .copy-btn:hover {{
      color: var(--accent);
      border-color: var(--accent);
    }}

    .install-banner .copy-btn svg {{
      width: 16px;
      height: 16px;
    }}

    .skill-header {{
      display: flex;
      align-items: center;
      justify-content: space-between;
      margin-bottom: 0.75rem;
    }}

    .skill-name {{
      font-family: 'JetBrains Mono', monospace;
      font-size: 0.95rem;
      font-weight: 500;
      color: var(--accent);
    }}

    .version {{
      font-family: 'JetBrains Mono', monospace;
      font-size: 0.75rem;
      color: var(--text-muted);
      background: color-mix(in srgb, var(--text-muted) 10%, transparent);
      padding: 0.15rem 0.5rem;
      border-radius: 4px;
    }}

    .skill-desc {{
      color: var(--text-muted);
      font-size: 0.85rem;
      line-height: 1.5;
      flex: 1;
      margin-bottom: 1rem;
    }}

    .skill-footer {{
      display: flex;
      align-items: center;
      justify-content: space-between;
      gap: 0.5rem;
    }}

    .tags {{
      display: flex;
      gap: 0.375rem;
      flex-wrap: wrap;
    }}

    .tag {{
      font-size: 0.7rem;
      font-weight: 500;
      padding: 0.2rem 0.5rem;
      border-radius: 4px;
      text-transform: uppercase;
      letter-spacing: 0.03em;
    }}

    .tag-readonly {{
      background: rgba(0, 191, 179, 0.12);
      color: #00BFB3;
    }}

    .tag-auto {{
      background: rgba(136, 132, 216, 0.12);
      color: #8884D8;
    }}

    .tag-manual {{
      background: rgba(254, 197, 20, 0.12);
      color: #FEC514;
    }}

    .sources {{
      font-size: 0.7rem;
      color: var(--text-muted);
      white-space: nowrap;
    }}

    footer {{
      text-align: center;
      padding: 2rem;
      border-top: 1px solid var(--border);
      color: var(--text-muted);
      font-size: 0.8rem;
    }}

    footer a {{
      color: var(--accent);
      text-decoration: none;
    }}

    footer a:hover {{
      text-decoration: underline;
    }}

    @media (max-width: 640px) {{
      .hero h1 {{ font-size: 1.75rem; }}
      .skills-grid {{ grid-template-columns: 1fr; }}
      .category-header {{ flex-wrap: wrap; }}
    }}
  </style>
</head>
<body>
  <header class="hero">
    <div class="hero-logo">
      <i data-feather="zap"></i>
      <span style="font-size: 0.9rem; font-weight: 600; color: var(--text-muted);">elastic/docs-skills</span>
    </div>
    <h1><span>Elastic Docs Skills Catalogue</span></h1>
    <p>Claude Code skills for Elastic documentation workflows, available as slash commands.</p>
    <div class="stats">
      <div class="stat">
        <div class="stat-value">{total}</div>
        <div class="stat-label">Skills</div>
      </div>
      <div class="stat">
        <div class="stat-value">{len(categories)}</div>
        <div class="stat-label">Categories</div>
      </div>
    </div>
    <div class="install-banner">
      <div class="install-row">
        <span class="cmd-label">Install</span>
        <code id="install-cmd">{" ".join(INSTALL_COMMANDS["Install"].split())}</code>
        <button class="copy-btn" onclick="copyCmd('install-cmd', this)" title="Copy install command">
          <i data-feather="clipboard"></i>
        </button>
      </div>
      <div class="install-row">
        <span class="cmd-label">List</span>
        <code id="list-cmd">{" ".join(INSTALL_COMMANDS["List"].split())}</code>
        <button class="copy-btn" onclick="copyCmd('list-cmd', this)" title="Copy list command">
          <i data-feather="clipboard"></i>
        </button>
      </div>
      <div class="install-row">
        <span class="cmd-label">Update</span>
        <code id="update-cmd">{" ".join(INSTALL_COMMANDS["Update"].split())}</code>
        <button class="copy-btn" onclick="copyCmd('update-cmd', this)" title="Copy update command">
          <i data-feather="clipboard"></i>
        </button>
      </div>
      <div class="install-row">
        <span class="cmd-label">Skills CLI</span>
        <code id="skills-cli-cmd">{" ".join(INSTALL_COMMANDS["Skills CLI"].split())}</code>
        <button class="copy-btn" onclick="copyCmd('skills-cli-cmd', this)" title="Copy skills CLI command">
          <i data-feather="clipboard"></i>
        </button>
      </div>
    </div>
  </header>

  <main class="container">
{cards_html}
  </main>

  <footer>
    Built from <a href="https://github.com/elastic/elastic-docs-skills">elastic/elastic-docs-skills</a> &middot; Auto-generated on each push to <code>main</code>
  </footer>

  <script>
    function copyCmd(id, button) {{
      const value = document.getElementById(id).textContent;
      navigator.clipboard.writeText(value).then(() => {{
        button.innerHTML = "<i data-feather='check'></i>";
        feather.replace();
        setTimeout(() => {{
          button.innerHTML = "<i data-feather='clipboard'></i>";
          feather.replace();
        }}, 2000);
      }});
    }}

    feather.replace();
  </script>
</body>
</html>
"""


def build_catalog_json(categories: dict[str, list[dict]]) -> list[dict]:
    """Build a flat list of skill metadata for the JSON catalog."""
    catalog = []
    for cat, skills in sorted(categories.items()):
        for skill in sorted(skills, key=lambda s: s["name"]):
            sources = skill.get("sources", [])
            if isinstance(sources, str):
                sources = [sources]
            catalog.append(
                {
                    "name": skill["name"],
                    "version": skill.get("version", ""),
                    "description": skill.get("description", ""),
                    "category": cat,
                    "path": skill.get("_path", ""),
                    "context": skill.get("context", ""),
                    "autoTrigger": skill.get("disable-model-invocation", "") != "true",
                    "sources": sources,
                }
            )
    return catalog


def main():
    categories = collect_skills()
    OUT_DIR.mkdir(parents=True, exist_ok=True)

    html = render_html(categories)
    (OUT_DIR / "index.html").write_text(html)

    catalog = build_catalog_json(categories)
    (OUT_DIR / "catalog.json").write_text(json.dumps(catalog, indent=2) + "\n")

    (OUT_DIR / ".nojekyll").touch()

    total = len(catalog)
    print(f"Generated catalog: {total} skills in {len(categories)} categories")


if __name__ == "__main__":
    main()
