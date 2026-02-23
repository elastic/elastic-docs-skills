#!/usr/bin/env bash
set -euo pipefail

# elastic-docs-skills installer
# Interactive TUI for installing Claude Code skills from the catalog
# Zero external dependencies — uses Python 3 curses (ships with macOS/Linux)
#
# Usage:
#   curl -sSL https://raw.githubusercontent.com/elastic/elastic-docs-skills/main/install.sh | bash
#   curl -sSL https://raw.githubusercontent.com/elastic/elastic-docs-skills/main/install.sh | bash -s -- --list
#   curl -sSL https://raw.githubusercontent.com/elastic/elastic-docs-skills/main/install.sh | bash -s -- --all

REPO="elastic/elastic-docs-skills"
BRANCH="main"
RAW_BASE="https://raw.githubusercontent.com/$REPO/$BRANCH"
API_BASE="https://api.github.com/repos/$REPO"
INSTALL_DIR="$HOME/.claude/skills"

# Detect if running from a local clone
LOCAL_MODE=false
SCRIPT_DIR=""
SKILLS_DIR=""
if [[ -n "${BASH_SOURCE[0]:-}" ]] && [[ -f "${BASH_SOURCE[0]}" ]]; then
  SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
  if [[ -d "$SCRIPT_DIR/skills" ]]; then
    LOCAL_MODE=true
    SKILLS_DIR="$SCRIPT_DIR/skills"
  fi
fi

# Colors
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[0;33m'
CYAN='\033[0;36m'
BOLD='\033[1m'
NC='\033[0m'

info()  { echo -e "${CYAN}${BOLD}ℹ${NC} $1"; }
ok()    { echo -e "${GREEN}${BOLD}✓${NC} $1"; }
warn()  { echo -e "${YELLOW}${BOLD}⚠${NC} $1"; }
err()   { echo -e "${RED}${BOLD}✗${NC} $1" >&2; }

usage() {
  cat <<EOF
Usage: install.sh [OPTIONS]

Interactive installer for elastic-docs-skills catalog.
Works both from a local clone and via curl from GitHub.
Requires Python 3 (ships with macOS and most Linux distributions).

Options:
  --list            List all available skills and exit
  --all             Install all skills (non-interactive)
  --uninstall NAME  Remove an installed skill
  --help            Show this help message

Without options, launches an interactive TUI to select skills.
EOF
}

# ─── Skill scanning ─────────────────────────────────────────────────────────

parse_field() {
  local file="$1" field="$2"
  sed -n '/^---$/,/^---$/p' "$file" | grep "^${field}:" | head -1 | sed "s/^${field}: *//"
}

parse_field_from_content() {
  local content="$1" field="$2"
  echo "$content" | sed -n '/^---$/,/^---$/p' | grep "^${field}:" | head -1 | sed "s/^${field}: *//"
}

# Builds a TSV catalog: name\tversion\tcategory\tdescription\tpath
build_catalog_local() {
  while IFS= read -r skill_file; do
    local name version description category rel_path
    name="$(parse_field "$skill_file" "name")"
    [[ -z "$name" ]] && continue
    version="$(parse_field "$skill_file" "version")"
    description="$(parse_field "$skill_file" "description")"
    rel_path="${skill_file#"$SKILLS_DIR/"}"
    category="$(echo "$rel_path" | cut -d'/' -f1)"
    printf '%s\t%s\t%s\t%s\t%s\n' "$name" "${version:-0.0.0}" "$category" "${description:-No description}" "$skill_file"
  done < <(find "$SKILLS_DIR" -name "SKILL.md" -type f 2>/dev/null | sort)
}

build_catalog_remote() {
  info "Fetching skill catalog from GitHub..."
  local tree_response
  tree_response=$(curl -fsSL "${API_BASE}/git/trees/${BRANCH}?recursive=1" 2>/dev/null) || {
    err "Failed to fetch repository tree from GitHub"; exit 1
  }
  local skill_paths
  skill_paths=$(echo "$tree_response" | grep -o '"path":"skills/[^"]*SKILL\.md"' | sed 's/"path":"//;s/"//' | sort)
  [[ -z "$skill_paths" ]] && { err "No skills found in the remote catalog"; exit 1; }

  while IFS= read -r remote_path; do
    local content name version description category
    content=$(curl -fsSL "${RAW_BASE}/${remote_path}" 2>/dev/null) || continue
    name="$(parse_field_from_content "$content" "name")"
    [[ -z "$name" ]] && continue
    version="$(parse_field_from_content "$content" "version")"
    description="$(parse_field_from_content "$content" "description")"
    category="$(echo "$remote_path" | cut -d'/' -f2)"
    printf '%s\t%s\t%s\t%s\t%s\n' "$name" "${version:-0.0.0}" "$category" "${description:-No description}" "$remote_path"
  done <<< "$skill_paths"
}

build_catalog() {
  if [[ "$LOCAL_MODE" == true ]]; then
    build_catalog_local
  else
    build_catalog_remote
  fi
}

# ─── Installation ────────────────────────────────────────────────────────────

install_one_local() {
  local name="$1" path="$2" version="$3"
  local source_dir target
  source_dir="$(dirname "$path")"
  target="$INSTALL_DIR/$name"
  mkdir -p "$target"
  cp -r "$source_dir"/* "$target"/
  ok "Installed ${BOLD}$name${NC} v$version → $target"
}

install_one_remote() {
  local name="$1" remote_path="$2" version="$3"
  local remote_dir target
  remote_dir="$(dirname "$remote_path")"
  target="$INSTALL_DIR/$name"
  mkdir -p "$target"

  curl -fsSL "${RAW_BASE}/${remote_path}" -o "$target/SKILL.md" 2>/dev/null || {
    err "Failed to download $name"; return 1
  }

  # Fetch supplementary files
  local tree_response extra_files
  tree_response=$(curl -fsSL "${API_BASE}/git/trees/${BRANCH}?recursive=1" 2>/dev/null) || true
  extra_files=$(echo "$tree_response" | grep -o "\"path\":\"${remote_dir}/[^\"]*\"" | sed 's/"path":"//;s/"//' | grep -v "SKILL\.md$" || true)
  while IFS= read -r extra_path; do
    [[ -z "$extra_path" ]] && continue
    local filename="${extra_path#"$remote_dir/"}"
    mkdir -p "$target/$(dirname "$filename")"
    curl -fsSL "${RAW_BASE}/${extra_path}" -o "$target/$filename" 2>/dev/null || true
  done <<< "$extra_files"

  ok "Installed ${BOLD}$name${NC} v$version → $target"
}

install_one() {
  if [[ "$LOCAL_MODE" == true ]]; then
    install_one_local "$@"
  else
    install_one_remote "$@"
  fi
}

# ─── Commands ────────────────────────────────────────────────────────────────

cmd_list() {
  local catalog
  catalog="$(build_catalog)"
  [[ -z "$catalog" ]] && { err "No skills found"; exit 1; }

  printf "\n${BOLD}%-20s %-12s %-10s %s${NC}\n" "NAME" "CATEGORY" "VERSION" "DESCRIPTION"
  printf "%-20s %-12s %-10s %s\n" "────────────────────" "────────────" "──────────" "────────────────────────────────────────"

  while IFS=$'\t' read -r name version category description path; do
    local installed=""
    [[ -f "$INSTALL_DIR/$name/SKILL.md" ]] && installed=" ${GREEN}(installed)${NC}"
    printf "%-20s %-12s %-10s %s${installed}\n" "$name" "$category" "$version" "${description:0:50}"
  done <<< "$catalog"
  echo ""
}

cmd_uninstall() {
  local name="$1"
  local target="$INSTALL_DIR/$name"
  [[ ! -d "$target" ]] && { err "Skill '$name' is not installed at $target"; exit 1; }
  rm -rf "$target"
  ok "Uninstalled skill '$name'"
}

cmd_install_all() {
  local catalog
  catalog="$(build_catalog)"
  [[ -z "$catalog" ]] && { err "No skills found"; exit 1; }
  mkdir -p "$INSTALL_DIR"

  local count=0
  while IFS=$'\t' read -r name version category description path; do
    install_one "$name" "$path" "$version"
    ((count++))
  done <<< "$catalog"

  echo ""
  ok "Installed $count skill(s) to $INSTALL_DIR"
}

cmd_interactive() {
  # Check Python 3 is available
  local python_cmd=""
  for cmd in python3 python; do
    if command -v "$cmd" &>/dev/null && "$cmd" -c "import sys; assert sys.version_info >= (3, 6)" 2>/dev/null; then
      python_cmd="$cmd"
      break
    fi
  done
  if [[ -z "$python_cmd" ]]; then
    err "Python 3.6+ is required for the interactive installer."
    echo "  Use --list and --all for non-interactive mode."
    exit 1
  fi

  # Build catalog
  local catalog
  catalog="$(build_catalog)"
  [[ -z "$catalog" ]] && { err "No skills found"; exit 1; }

  # Get the TUI script (local or fetch from GitHub)
  local tui_script=""
  if [[ "$LOCAL_MODE" == true ]] && [[ -f "$SCRIPT_DIR/tui.py" ]]; then
    tui_script="$SCRIPT_DIR/tui.py"
  else
    tui_script=$(mktemp "${TMPDIR:-/tmp}/elastic-tui-XXXXXX.py")
    curl -fsSL "${RAW_BASE}/tui.py" -o "$tui_script" 2>/dev/null || {
      err "Failed to download TUI component"
      rm -f "$tui_script"
      exit 1
    }
    trap "rm -f '$tui_script'" EXIT
  fi

  # Run TUI: curses needs /dev/tty for display and input
  # Results are written to a temp file
  local result_file
  result_file=$(mktemp "${TMPDIR:-/tmp}/elastic-result-XXXXXX")

  CATALOG="$catalog" RESULT_FILE="$result_file" "$python_cmd" "$tui_script" </dev/tty >/dev/tty 2>/dev/null || true

  local selected=""
  if [[ -s "$result_file" ]]; then
    selected=$(cat "$result_file")
  fi
  rm -f "$result_file"

  if [[ -z "$selected" ]]; then
    echo ""
    warn "No skills selected."
    exit 0
  fi

  echo ""
  mkdir -p "$INSTALL_DIR"

  local count=0
  while IFS= read -r selected_name; do
    [[ -z "$selected_name" ]] && continue
    while IFS=$'\t' read -r name version category description path; do
      if [[ "$name" == "$selected_name" ]]; then
        install_one "$name" "$path" "$version"
        ((count++))
        break
      fi
    done <<< "$catalog"
  done <<< "$selected"

  echo ""
  ok "Installed $count skill(s) to $INSTALL_DIR"
}

# ─── Main ────────────────────────────────────────────────────────────────────

main() {
  if [[ "$LOCAL_MODE" == true ]]; then
    info "Running from local clone: $SCRIPT_DIR"
  else
    info "Running in remote mode — fetching from github.com/$REPO"
  fi

  case "${1:-}" in
    --help|-h)
      usage
      ;;
    --list)
      cmd_list
      ;;
    --all)
      cmd_install_all
      ;;
    --uninstall)
      if [[ -z "${2:-}" ]]; then
        err "Usage: install.sh --uninstall <skill-name>"
        exit 1
      fi
      cmd_uninstall "$2"
      ;;
    "")
      cmd_interactive
      ;;
    *)
      err "Unknown option: $1"
      usage
      exit 1
      ;;
  esac
}

main "$@"
