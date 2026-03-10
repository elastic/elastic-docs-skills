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

"""Interactive TUI for elastic-docs-skills installer. Uses only Python built-in curses."""

import curses
import os
import sys

# Result actions written to RESULT_FILE:
#   install:<name>   — install skill
#   uninstall:<name> — uninstall skill


def parse_semver(v):
    """Parse a version string into a comparable tuple of ints."""
    parts = v.split(".")
    result = []
    for p in parts[:3]:
        try:
            result.append(int(p))
        except (ValueError, IndexError):
            result.append(0)
    while len(result) < 3:
        result.append(0)
    return tuple(result)


def get_installed_version(install_dir, name):
    """Read the version from an installed skill's SKILL.md frontmatter."""
    skill_path = os.path.join(install_dir, name, "SKILL.md")
    try:
        with open(skill_path) as f:
            in_frontmatter = False
            for line in f:
                stripped = line.strip()
                if stripped == "---":
                    if in_frontmatter:
                        break
                    in_frontmatter = True
                    continue
                if in_frontmatter and stripped.startswith("version:"):
                    return stripped.split(":", 1)[1].strip()
    except OSError:
        pass
    return None


def main(stdscr):
    curses.curs_set(0)
    curses.use_default_colors()
    curses.start_color()
    curses.init_pair(1, curses.COLOR_CYAN, -1)                    # title
    curses.init_pair(2, curses.COLOR_GREEN, -1)                   # selected / installed
    curses.init_pair(3, curses.COLOR_YELLOW, -1)                  # installed tag
    curses.init_pair(4, curses.COLOR_BLACK, curses.COLOR_CYAN)    # cursor highlight
    curses.init_pair(5, curses.COLOR_BLACK, curses.COLOR_GREEN)   # status bar
    curses.init_pair(6, curses.COLOR_RED, -1)                     # uninstall marker
    curses.init_pair(7, curses.COLOR_MAGENTA, -1)                 # update available

    install_dir = os.path.expanduser("~/.claude/skills")
    result_file = os.environ.get("RESULT_FILE", "")

    # Parse catalog from env (TSV: name\tversion\tcategory\tdescription\tpath)
    catalog_raw = os.environ.get("CATALOG", "")
    items = []
    for line in catalog_raw.strip().split("\n"):
        if not line.strip():
            continue
        parts = line.split("\t")
        if len(parts) >= 5:
            name, version, category, description, path = (
                parts[0], parts[1], parts[2], parts[3], parts[4],
            )
            installed = os.path.isfile(os.path.join(install_dir, name, "SKILL.md"))
            installed_version = get_installed_version(install_dir, name) if installed else None
            update_available = (
                installed
                and installed_version is not None
                and parse_semver(version) > parse_semver(installed_version)
            )
            items.append({
                "name": name,
                "version": version,
                "category": category,
                "description": description,
                "path": path,
                "installed": installed,
                "installed_version": installed_version,
                "update_available": update_available,
                # action: None, "install", "update", or "uninstall"
                "action": None,
            })

    if not items:
        return

    cursor = 0
    scroll_offset = 0
    filter_text = ""

    def get_filtered():
        if not filter_text:
            return list(range(len(items)))
        ft = filter_text.lower()
        return [
            i for i, it in enumerate(items)
            if ft in it["name"].lower()
            or ft in it["category"].lower()
            or ft in it["description"].lower()
        ]

    def toggle_item(idx):
        item = items[idx]
        if item["update_available"]:
            # Has update: cycle None -> update -> uninstall -> None
            if item["action"] is None:
                item["action"] = "update"
            elif item["action"] == "update":
                item["action"] = "uninstall"
            else:
                item["action"] = None
        elif item["installed"]:
            # Installed, up to date: cycle None -> uninstall -> None
            if item["action"] is None:
                item["action"] = "uninstall"
            else:
                item["action"] = None
        else:
            # Not installed: cycle None -> install -> None
            if item["action"] is None:
                item["action"] = "install"
            else:
                item["action"] = None

    def write_result():
        actions = []
        for it in items:
            if it["action"] in ("install", "update"):
                actions.append(f"install:{it['name']}")
            elif it["action"] == "uninstall":
                actions.append(f"uninstall:{it['name']}")
        if result_file and actions:
            with open(result_file, "w") as f:
                f.write("\n".join(actions))

    def get_marker(item):
        if item["action"] == "install":
            return "[+]"
        elif item["action"] == "update":
            return "[^]"
        elif item["action"] == "uninstall":
            return "[-]"
        elif item["update_available"]:
            return "[^]"
        elif item["installed"]:
            return "[*]"
        else:
            return "[ ]"

    def get_status_label(item):
        if item["action"] == "install":
            return " INSTALL"
        elif item["action"] == "update":
            return f" UPDATE {item['installed_version']}->{item['version']}"
        elif item["action"] == "uninstall":
            return " REMOVE"
        elif item["update_available"]:
            return f" v{item['version']} available"
        elif item["installed"]:
            return " installed"
        else:
            return ""

    banner_lines = [
        r"  ___ _         _   _      ___               ___ _   _ _ _    ",
        r" | __| |__ _ __| |_(_)__  |   \ ___  __ ___ / __| |_(_) | |___",
        r" | _|| / _` (_-<  _| / _| | |) / _ \/ _(_-< \__ \ / / | | (_-<",
        r" |___|_\__,_/__/\__|_\__| |___/\___/\__/__/ |___/_\_\_|_|_/__/",
    ]
    banner_width = max(len(l) for l in banner_lines)
    fallback_title = " Elastic Docs Skills "

    while True:
        stdscr.erase()
        max_y, max_x = stdscr.getmaxyx()
        filtered = get_filtered()

        # ── Title: banner if it fits, simple text otherwise ──
        if max_x >= banner_width + 2:
            for i, bline in enumerate(banner_lines):
                if i >= max_y - 1:
                    break
                x = max(0, (max_x - len(bline)) // 2)
                stdscr.attron(curses.color_pair(1) | curses.A_BOLD)
                stdscr.addnstr(i, x, bline, max_x - x - 1)
                stdscr.attroff(curses.color_pair(1) | curses.A_BOLD)
            banner_h = len(banner_lines)
        else:
            x = max(0, (max_x - len(fallback_title)) // 2)
            stdscr.attron(curses.color_pair(1) | curses.A_BOLD)
            stdscr.addnstr(0, x, fallback_title, max_x - 1)
            stdscr.attroff(curses.color_pair(1) | curses.A_BOLD)
            banner_h = 1

        # ── Help line (centered, with highlighted keys) ──
        help_parts = [
            ("SPACE", "toggle"),
            ("ENTER", "confirm"),
            ("/", "filter"),
            ("a", "all"),
            ("u", "updates"),
            ("n", "none"),
            ("q", "quit"),
        ]
        # Calculate total width to center
        help_str = "  ".join(f"{k} {d}" for k, d in help_parts)
        help_y = banner_h + 1
        help_x = max(1, (max_x - len(help_str)) // 2)
        for i, (key, desc) in enumerate(help_parts):
            if help_x >= max_x - 1:
                break
            stdscr.attron(curses.color_pair(4))
            stdscr.addnstr(help_y, help_x, f" {key} ", max_x - help_x - 1)
            stdscr.attroff(curses.color_pair(4))
            help_x += len(key) + 2
            label = f" {desc}"
            stdscr.addnstr(help_y, help_x, label, max_x - help_x - 1)
            help_x += len(label)
            if i < len(help_parts) - 1:
                stdscr.addnstr(help_y, help_x, "  ", max_x - help_x - 1)
                help_x += 2

        # ── Filter bar ──
        filter_y = banner_h + 2
        if filter_text:
            filter_display = f" / {filter_text}_ "
        else:
            filter_display = " Type / to filter "
        stdscr.addnstr(filter_y, 0, filter_display, max_x - 1, curses.color_pair(1))

        # ── Column header ──
        header_y = banner_h + 3
        hdr = f"      {'NAME':<20s} {'CATEGORY':<12s} {'VER':<8s} DESCRIPTION"
        stdscr.attron(curses.A_BOLD | curses.A_UNDERLINE)
        stdscr.addnstr(header_y, 0, hdr[: max_x - 1], max_x - 1)
        stdscr.attroff(curses.A_BOLD | curses.A_UNDERLINE)

        # ── List area ──
        list_start_y = header_y + 1
        list_height = max_y - list_start_y - 2
        if list_height < 1:
            list_height = 1

        # Adjust scroll
        if cursor < scroll_offset:
            scroll_offset = cursor
        if cursor >= scroll_offset + list_height:
            scroll_offset = cursor - list_height + 1

        for row_idx in range(list_height):
            fi = scroll_offset + row_idx
            if fi >= len(filtered):
                break
            item_idx = filtered[fi]
            item = items[item_idx]

            marker = get_marker(item)
            status_label = get_status_label(item)
            desc_width = max(10, max_x - 60)
            line = (
                f"  {marker} {item['name']:<20s} {item['category']:<12s} "
                f"{item['version']:<8s} {item['description'][:desc_width]}{status_label}"
            )

            y = list_start_y + row_idx
            if y >= max_y - 2:
                break

            is_cursor = fi == cursor

            if is_cursor:
                stdscr.attron(curses.color_pair(4) | curses.A_BOLD)
                stdscr.addnstr(y, 0, line[: max_x - 1].ljust(max_x - 1), max_x - 1)
                stdscr.attroff(curses.color_pair(4) | curses.A_BOLD)
            elif item["action"] == "install":
                stdscr.attron(curses.color_pair(2) | curses.A_BOLD)
                stdscr.addnstr(y, 0, line[: max_x - 1], max_x - 1)
                stdscr.attroff(curses.color_pair(2) | curses.A_BOLD)
            elif item["action"] == "update":
                stdscr.attron(curses.color_pair(2) | curses.A_BOLD)
                stdscr.addnstr(y, 0, line[: max_x - 1], max_x - 1)
                stdscr.attroff(curses.color_pair(2) | curses.A_BOLD)
            elif item["action"] == "uninstall":
                stdscr.attron(curses.color_pair(6))
                stdscr.addnstr(y, 0, line[: max_x - 1], max_x - 1)
                stdscr.attroff(curses.color_pair(6))
            elif item["update_available"]:
                stdscr.attron(curses.color_pair(7) | curses.A_BOLD)
                stdscr.addnstr(y, 0, line[: max_x - 1], max_x - 1)
                stdscr.attroff(curses.color_pair(7) | curses.A_BOLD)
            elif item["installed"]:
                stdscr.attron(curses.color_pair(3))
                stdscr.addnstr(y, 0, line[: max_x - 1], max_x - 1)
                stdscr.attroff(curses.color_pair(3))
            else:
                stdscr.addnstr(y, 0, line[: max_x - 1], max_x - 1)

        # ── Status bar ──
        to_install = sum(1 for it in items if it["action"] == "install")
        to_update = sum(1 for it in items if it["action"] == "update")
        to_uninstall = sum(1 for it in items if it["action"] == "uninstall")
        updates_avail = sum(
            1 for it in items if it["update_available"] and it["action"] != "update"
        )
        already = sum(1 for it in items if it["installed"])

        parts = [f" {len(items)} skills"]
        if already:
            parts.append(f"{already} installed")
        if updates_avail:
            parts.append(f"{updates_avail} update(s) available")
        if to_install:
            parts.append(f"+{to_install} to install")
        if to_update:
            parts.append(f"^{to_update} to update")
        if to_uninstall:
            parts.append(f"-{to_uninstall} to remove")
        parts.append("[*]=installed [+]=install [^]=update [-]=remove ")
        status = " | ".join(parts)

        status_y = max_y - 1
        stdscr.attron(curses.color_pair(5) | curses.A_BOLD)
        stdscr.addnstr(status_y, 0, status[: max_x - 1].ljust(max_x - 1), max_x - 1)
        stdscr.attroff(curses.color_pair(5) | curses.A_BOLD)

        stdscr.refresh()
        key = stdscr.getch()

        if key == curses.KEY_RESIZE:
            stdscr.clear()
            continue
        elif key == ord("q") or key == 27:  # q or ESC
            return
        elif key in (ord("\n"), curses.KEY_ENTER, 10, 13):
            write_result()
            return
        elif key == curses.KEY_UP or key == ord("k"):
            if cursor > 0:
                cursor -= 1
        elif key == curses.KEY_DOWN or key == ord("j"):
            if cursor < len(filtered) - 1:
                cursor += 1
        elif key == ord(" "):
            if filtered:
                toggle_item(filtered[cursor])
                if cursor < len(filtered) - 1:
                    cursor += 1
        elif key == ord("a"):
            for fi in filtered:
                item = items[fi]
                if not item["installed"]:
                    item["action"] = "install"
        elif key == ord("u"):
            for fi in filtered:
                item = items[fi]
                if item["update_available"]:
                    item["action"] = "update"
        elif key == ord("n"):
            for fi in filtered:
                items[fi]["action"] = None
        elif key == ord("/"):
            filter_text = ""
            cursor = 0
            scroll_offset = 0
            stdscr.nodelay(False)
            while True:
                if filter_text:
                    fd = f" / {filter_text}_ (ESC to clear) "
                else:
                    fd = " / _ (type to search, ESC to clear) "
                stdscr.addnstr(
                    filter_y, 0, fd[: max_x - 1].ljust(max_x - 1), max_x - 1,
                    curses.color_pair(1),
                )
                stdscr.refresh()
                fk = stdscr.getch()
                if fk == 27:  # ESC
                    filter_text = ""
                    cursor = 0
                    scroll_offset = 0
                    break
                elif fk in (ord("\n"), 10, 13):
                    cursor = 0
                    scroll_offset = 0
                    break
                elif fk in (curses.KEY_BACKSPACE, 127, 8):
                    filter_text = filter_text[:-1]
                    cursor = 0
                    scroll_offset = 0
                elif 32 <= fk <= 126:
                    filter_text += chr(fk)
                    cursor = 0
                    scroll_offset = 0


if __name__ == "__main__":
    curses.wrapper(main)
