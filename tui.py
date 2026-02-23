#!/usr/bin/env python3
"""Interactive TUI for elastic-docs-skills installer. Uses only Python built-in curses."""

import curses
import os
import sys

# Result actions written to RESULT_FILE:
#   install:<name>   — install skill
#   uninstall:<name> — uninstall skill


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
            items.append({
                "name": name,
                "version": version,
                "category": category,
                "description": description,
                "path": path,
                "installed": installed,
                # action: None (no change), "install", or "uninstall"
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
        if item["installed"]:
            # Installed: cycle None -> uninstall -> None
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
            if it["action"] == "install":
                actions.append(f"install:{it['name']}")
            elif it["action"] == "uninstall":
                actions.append(f"uninstall:{it['name']}")
        if result_file and actions:
            with open(result_file, "w") as f:
                f.write("\n".join(actions))

    def get_marker(item):
        if item["action"] == "install":
            return "[+]"
        elif item["action"] == "uninstall":
            return "[-]"
        elif item["installed"]:
            return "[*]"
        else:
            return "[ ]"

    def get_status_label(item):
        if item["action"] == "install":
            return " INSTALL"
        elif item["action"] == "uninstall":
            return " REMOVE"
        elif item["installed"]:
            return " installed"
        else:
            return ""

    while True:
        stdscr.erase()
        max_y, max_x = stdscr.getmaxyx()
        filtered = get_filtered()

        # ── Title ──
        title = " elastic-docs-skills installer "
        stdscr.attron(curses.color_pair(1) | curses.A_BOLD)
        stdscr.addnstr(0, max(0, (max_x - len(title)) // 2), title, max_x - 1)
        stdscr.attroff(curses.color_pair(1) | curses.A_BOLD)

        # ── Help line ──
        help_parts = [
            ("SPACE", "toggle"),
            ("ENTER", "confirm"),
            ("/", "filter"),
            ("a", "all"),
            ("n", "none"),
            ("q", "quit"),
        ]
        help_x = 1
        for key, desc in help_parts:
            if help_x >= max_x - 1:
                break
            stdscr.attron(curses.A_BOLD)
            stdscr.addnstr(1, help_x, key, max_x - help_x - 1)
            stdscr.attroff(curses.A_BOLD)
            help_x += len(key)
            label = f"={desc}  "
            stdscr.addnstr(1, help_x, label, max_x - help_x - 1)
            help_x += len(label)

        # ── Filter bar ──
        if filter_text:
            filter_display = f" / {filter_text}_ "
        else:
            filter_display = " Type / to filter "
        stdscr.addnstr(2, 0, filter_display, max_x - 1, curses.color_pair(1))

        # ── Column header ──
        header_y = 3
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
                # Highlighted row
                stdscr.attron(curses.color_pair(4) | curses.A_BOLD)
                stdscr.addnstr(y, 0, line[: max_x - 1].ljust(max_x - 1), max_x - 1)
                stdscr.attroff(curses.color_pair(4) | curses.A_BOLD)
            elif item["action"] == "install":
                stdscr.attron(curses.color_pair(2) | curses.A_BOLD)
                stdscr.addnstr(y, 0, line[: max_x - 1], max_x - 1)
                stdscr.attroff(curses.color_pair(2) | curses.A_BOLD)
            elif item["action"] == "uninstall":
                stdscr.attron(curses.color_pair(6))
                stdscr.addnstr(y, 0, line[: max_x - 1], max_x - 1)
                stdscr.attroff(curses.color_pair(6))
            elif item["installed"]:
                stdscr.attron(curses.color_pair(3))
                stdscr.addnstr(y, 0, line[: max_x - 1], max_x - 1)
                stdscr.attroff(curses.color_pair(3))
            else:
                stdscr.addnstr(y, 0, line[: max_x - 1], max_x - 1)

        # ── Status bar ──
        to_install = sum(1 for it in items if it["action"] == "install")
        to_uninstall = sum(1 for it in items if it["action"] == "uninstall")
        already = sum(1 for it in items if it["installed"])

        parts = [f" {len(items)} skills"]
        if already:
            parts.append(f"{already} installed")
        if to_install:
            parts.append(f"+{to_install} to install")
        if to_uninstall:
            parts.append(f"-{to_uninstall} to remove")
        parts.append("[*]=installed [+]=install [-]=remove ")
        status = " | ".join(parts)

        status_y = max_y - 1
        stdscr.attron(curses.color_pair(5) | curses.A_BOLD)
        stdscr.addnstr(status_y, 0, status[: max_x - 1].ljust(max_x - 1), max_x - 1)
        stdscr.attroff(curses.color_pair(5) | curses.A_BOLD)

        stdscr.refresh()
        key = stdscr.getch()

        if key == ord("q") or key == 27:  # q or ESC
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
                    2, 0, fd[: max_x - 1].ljust(max_x - 1), max_x - 1,
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
