#!/usr/bin/env bash
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
TREE_CACHE=""

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

# Returns 0 (true) if $1 > $2 in SemVer ordering (major.minor.patch)
semver_gt() {
  local IFS=.
  local i a=($1) b=($2)
  for ((i=0; i<3; i++)); do
    local va=${a[i]:-0} vb=${b[i]:-0}
    (( va > vb )) && return 0
    (( va < vb )) && return 1
  done
  return 1
}

usage() {
  cat <<EOF
Usage: install.sh [OPTIONS]

Interactive installer for elastic-docs-skills catalog.
Works both from a local clone and via curl from GitHub.
Requires Python 3 (ships with macOS and most Linux distributions).

Options:
  --list            List all available skills and exit
  --all             Install all skills (non-interactive)
  --update          Update all installed skills to latest versions
  --uninstall NAME  Remove an installed skill
  --help            Show this help message

Without options, launches an interactive TUI to select skills.
EOF
}

# Attempt to fast-forward the local clone so the catalog reflects the latest
# upstream versions. Skips silently when not on main or when git is unavailable.
pull_latest_local() {
  command -v git &>/dev/null || return 0
  git -C "$SCRIPT_DIR" rev-parse --git-dir &>/dev/null 2>&1 || return 0

  local current_branch
  current_branch=$(git -C "$SCRIPT_DIR" symbolic-ref --short HEAD 2>/dev/null) || return 0

  if [[ "$current_branch" == "main" || "$current_branch" == "master" ]]; then
    info "Pulling latest from origin/$current_branch..."
    if git -C "$SCRIPT_DIR" pull --ff-only --quiet 2>/dev/null; then
      ok "Local clone is up to date"
    else
      warn "Could not fast-forward; using existing local versions"
    fi
  else
    warn "On branch '$current_branch' — skipping pull (checkout main for latest versions)"
  fi
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
  TREE_CACHE=$(curl -fsSL "${API_BASE}/git/trees/${BRANCH}?recursive=1" 2>/dev/null) || {
    err "Failed to fetch repository tree from GitHub"; exit 1
  }
  local skill_paths
  skill_paths=$(echo "$TREE_CACHE" | grep -o '"path":"skills/[^"]*SKILL\.md"' | sed 's/"path":"//;s/"//' | sort)
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

  # Fetch supplementary files (reuse cached tree when available)
  local tree_response extra_files
  if [[ -n "$TREE_CACHE" ]]; then
    tree_response="$TREE_CACHE"
  else
    tree_response=$(curl -fsSL "${API_BASE}/git/trees/${BRANCH}?recursive=1" 2>/dev/null) || true
  fi
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

cmd_update() {
  local catalog
  catalog="$(build_catalog)"
  [[ -z "$catalog" ]] && { err "No skills found in catalog"; exit 1; }
  mkdir -p "$INSTALL_DIR"

  local updated=0 skipped=0 total=0

  for installed_dir in "$INSTALL_DIR"/*/; do
    [[ ! -d "$installed_dir" ]] && continue
    local skill_name
    skill_name="$(basename "$installed_dir")"
    [[ ! -f "$installed_dir/SKILL.md" ]] && continue

    ((total++))

    local installed_version
    installed_version="$(parse_field "$installed_dir/SKILL.md" "version")"
    [[ -z "$installed_version" ]] && installed_version="0.0.0"

    local found=false
    while IFS=$'\t' read -r name version category description path; do
      if [[ "$name" == "$skill_name" ]]; then
        found=true
        if semver_gt "$version" "$installed_version"; then
          install_one "$name" "$path" "$version"
          info "  Updated v$installed_version → v$version"
          ((updated++))
        else
          ((skipped++))
        fi
        break
      fi
    done <<< "$catalog"

    if [[ "$found" == false ]]; then
      warn "Skill '$skill_name' is installed but not found in the catalog"
      ((skipped++))
    fi
  done

  echo ""
  if [[ $total -eq 0 ]]; then
    warn "No skills are currently installed at $INSTALL_DIR"
  elif [[ $updated -eq 0 ]]; then
    ok "All $total installed skill(s) are up to date"
  else
    ok "Updated $updated skill(s), $skipped already up to date"
  fi
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

  local actions=""
  if [[ -s "$result_file" ]]; then
    actions=$(cat "$result_file")
  fi
  rm -f "$result_file"

  if [[ -z "$actions" ]]; then
    echo ""
    warn "No changes selected."
    exit 0
  fi

  echo ""
  mkdir -p "$INSTALL_DIR"

  local installed=0 uninstalled=0
  while IFS= read -r action_line; do
    [[ -z "$action_line" ]] && continue
    local action="${action_line%%:*}"
    local skill_name="${action_line#*:}"

    if [[ "$action" == "uninstall" ]]; then
      local target="$INSTALL_DIR/$skill_name"
      if [[ -d "$target" ]]; then
        rm -rf "$target"
        ok "Uninstalled ${BOLD}$skill_name${NC}"
        ((uninstalled++))
      fi
    elif [[ "$action" == "install" ]]; then
      while IFS=$'\t' read -r name version category description path; do
        if [[ "$name" == "$skill_name" ]]; then
          install_one "$name" "$path" "$version"
          ((installed++))
          break
        fi
      done <<< "$catalog"
    fi
  done <<< "$actions"

  echo ""
  local summary=""
  [[ $installed -gt 0 ]] && summary="Installed $installed skill(s)"
  [[ $uninstalled -gt 0 ]] && {
    [[ -n "$summary" ]] && summary="$summary, "
    summary="${summary}Uninstalled $uninstalled skill(s)"
  }
  ok "$summary"
}

# ─── Main ────────────────────────────────────────────────────────────────────

main() {
  if [[ "$LOCAL_MODE" == true ]]; then
    info "Running from local clone: $SCRIPT_DIR"
    pull_latest_local
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
    --update)
      cmd_update
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
