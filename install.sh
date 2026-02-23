#!/usr/bin/env bash
set -euo pipefail

# elastic-docs-skills installer
# Interactive TUI for installing Claude Code skills from the catalog
# Can be run locally or via: curl -sSL https://raw.githubusercontent.com/elastic/elastic-docs-skills/main/install.sh | bash

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

# ─── Helpers ────────────────────────────────────────────────────────────────

info()  { echo -e "${CYAN}${BOLD}ℹ${NC} $1"; }
ok()    { echo -e "${GREEN}${BOLD}✓${NC} $1"; }
warn()  { echo -e "${YELLOW}${BOLD}⚠${NC} $1"; }
err()   { echo -e "${RED}${BOLD}✗${NC} $1" >&2; }

usage() {
  cat <<EOF
Usage: install.sh [OPTIONS]

Interactive installer for elastic-docs-skills catalog.
Works both from a local clone and via curl from GitHub.

  curl -sSL $RAW_BASE/install.sh | bash
  curl -sSL $RAW_BASE/install.sh | bash -s -- --list
  curl -sSL $RAW_BASE/install.sh | bash -s -- --all

Options:
  --list            List all available skills and exit
  --all             Install all skills (non-interactive)
  --uninstall NAME  Remove an installed skill
  --help            Show this help message

Without options, launches an interactive TUI to select skills.
Requires gum (https://github.com/charmbracelet/gum).
EOF
}

# ─── Gum dependency ─────────────────────────────────────────────────────────

check_gum() {
  command -v gum &>/dev/null
}

install_gum() {
  echo ""
  warn "gum is required for the interactive installer."
  echo "  https://github.com/charmbracelet/gum"
  echo ""

  if command -v brew &>/dev/null; then
    read -rp "Install gum via Homebrew? [Y/n] " answer
    if [[ "${answer:-Y}" =~ ^[Yy]$ ]]; then
      brew install gum
      return 0
    fi
  elif command -v apt-get &>/dev/null; then
    read -rp "Install gum via apt? [Y/n] " answer
    if [[ "${answer:-Y}" =~ ^[Yy]$ ]]; then
      sudo mkdir -p /etc/apt/keyrings
      curl -fsSL https://repo.charm.sh/apt/gpg.key | sudo gpg --dearmor -o /etc/apt/keyrings/charm.gpg
      echo "deb [signed-by=/etc/apt/keyrings/charm.gpg] https://repo.charm.sh/apt/ * *" | sudo tee /etc/apt/sources.list.d/charm.list
      sudo apt-get update && sudo apt-get install -y gum
      return 0
    fi
  elif command -v dnf &>/dev/null; then
    read -rp "Install gum via dnf? [Y/n] " answer
    if [[ "${answer:-Y}" =~ ^[Yy]$ ]]; then
      echo '[charm]
name=Charm
baseurl=https://repo.charm.sh/yum/
enabled=1
gpgcheck=1
gpgkey=https://repo.charm.sh/yum/gpg.key' | sudo tee /etc/yum.repos.d/charm.repo
      sudo dnf install -y gum
      return 0
    fi
  fi

  err "Please install gum manually: https://github.com/charmbracelet/gum#installation"
  exit 1
}

# ─── Skill scanning ─────────────────────────────────────────────────────────

# Parse frontmatter value from content (stdin or file)
parse_field_from_content() {
  local content="$1" field="$2"
  echo "$content" | sed -n '/^---$/,/^---$/p' | grep "^${field}:" | head -1 | sed "s/^${field}: *//"
}

parse_field() {
  local file="$1" field="$2"
  sed -n '/^---$/,/^---$/p' "$file" | grep "^${field}:" | head -1 | sed "s/^${field}: *//"
}

# Collect all skills into parallel arrays
declare -a SKILL_PATHS=()
declare -a SKILL_NAMES=()
declare -a SKILL_VERSIONS=()
declare -a SKILL_DESCRIPTIONS=()
declare -a SKILL_CATEGORIES=()

scan_skills_local() {
  while IFS= read -r skill_file; do
    local name version description category rel_path

    name="$(parse_field "$skill_file" "name")"
    version="$(parse_field "$skill_file" "version")"
    description="$(parse_field "$skill_file" "description")"

    rel_path="${skill_file#"$SKILLS_DIR/"}"
    category="$(echo "$rel_path" | cut -d'/' -f1)"

    if [[ -z "$name" ]]; then
      warn "Skipping $skill_file — missing name field"
      continue
    fi

    SKILL_PATHS+=("$skill_file")
    SKILL_NAMES+=("$name")
    SKILL_VERSIONS+=("${version:-0.0.0}")
    SKILL_DESCRIPTIONS+=("${description:-No description}")
    SKILL_CATEGORIES+=("$category")
  done < <(find "$SKILLS_DIR" -name "SKILL.md" -type f 2>/dev/null | sort)
}

scan_skills_remote() {
  info "Fetching skill catalog from GitHub..."

  # Use GitHub API to recursively find all SKILL.md files under skills/
  local tree_response
  tree_response=$(curl -fsSL "${API_BASE}/git/trees/${BRANCH}?recursive=1" 2>/dev/null) || {
    err "Failed to fetch repository tree from GitHub"
    exit 1
  }

  # Extract paths matching skills/**/SKILL.md
  local skill_paths
  skill_paths=$(echo "$tree_response" | grep -o '"path":"skills/[^"]*SKILL\.md"' | sed 's/"path":"//;s/"//' | sort)

  if [[ -z "$skill_paths" ]]; then
    err "No skills found in the remote catalog"
    exit 1
  fi

  while IFS= read -r remote_path; do
    local content name version description category

    # Fetch the raw file content
    content=$(curl -fsSL "${RAW_BASE}/${remote_path}" 2>/dev/null) || {
      warn "Failed to fetch $remote_path"
      continue
    }

    name="$(parse_field_from_content "$content" "name")"
    version="$(parse_field_from_content "$content" "version")"
    description="$(parse_field_from_content "$content" "description")"

    # Extract category: skills/<category>/<name>/SKILL.md
    category="$(echo "$remote_path" | cut -d'/' -f2)"

    if [[ -z "$name" ]]; then
      warn "Skipping $remote_path — missing name field"
      continue
    fi

    SKILL_PATHS+=("$remote_path")
    SKILL_NAMES+=("$name")
    SKILL_VERSIONS+=("${version:-0.0.0}")
    SKILL_DESCRIPTIONS+=("${description:-No description}")
    SKILL_CATEGORIES+=("$category")
  done <<< "$skill_paths"
}

scan_skills() {
  SKILL_PATHS=()
  SKILL_NAMES=()
  SKILL_VERSIONS=()
  SKILL_DESCRIPTIONS=()
  SKILL_CATEGORIES=()

  if [[ "$LOCAL_MODE" == true ]]; then
    scan_skills_local
  else
    scan_skills_remote
  fi

  if [[ ${#SKILL_NAMES[@]} -eq 0 ]]; then
    err "No skills found"
    exit 1
  fi
}

# ─── Installation ────────────────────────────────────────────────────────────

install_skill_local() {
  local index="$1"
  local name="${SKILL_NAMES[$index]}"
  local version="${SKILL_VERSIONS[$index]}"
  local source_dir
  source_dir="$(dirname "${SKILL_PATHS[$index]}")"
  local target="$INSTALL_DIR/$name"

  mkdir -p "$target"
  cp -r "$source_dir"/* "$target"/
  ok "Installed ${BOLD}$name${NC} v$version → $target"
}

install_skill_remote() {
  local index="$1"
  local name="${SKILL_NAMES[$index]}"
  local version="${SKILL_VERSIONS[$index]}"
  local remote_path="${SKILL_PATHS[$index]}"
  local remote_dir
  remote_dir="$(dirname "$remote_path")"
  local target="$INSTALL_DIR/$name"

  mkdir -p "$target"

  # Fetch the SKILL.md
  curl -fsSL "${RAW_BASE}/${remote_path}" -o "$target/SKILL.md" 2>/dev/null || {
    err "Failed to download $name"
    return 1
  }

  # Check for additional files in the skill directory via the tree API
  local tree_response
  tree_response=$(curl -fsSL "${API_BASE}/git/trees/${BRANCH}?recursive=1" 2>/dev/null) || true

  local extra_files
  extra_files=$(echo "$tree_response" | grep -o "\"path\":\"${remote_dir}/[^\"]*\"" | sed 's/"path":"//;s/"//' | grep -v "SKILL\.md$" || true)

  while IFS= read -r extra_path; do
    [[ -z "$extra_path" ]] && continue
    local filename="${extra_path#"$remote_dir/"}"
    local target_subdir="$target/$(dirname "$filename")"
    mkdir -p "$target_subdir"
    curl -fsSL "${RAW_BASE}/${extra_path}" -o "$target/$filename" 2>/dev/null || {
      warn "Failed to download supplementary file: $filename"
    }
  done <<< "$extra_files"

  ok "Installed ${BOLD}$name${NC} v$version → $target"
}

install_skill() {
  if [[ "$LOCAL_MODE" == true ]]; then
    install_skill_local "$1"
  else
    install_skill_remote "$1"
  fi
}

# ─── Commands ────────────────────────────────────────────────────────────────

cmd_list() {
  scan_skills

  printf "\n${BOLD}%-20s %-12s %-10s %s${NC}\n" "NAME" "CATEGORY" "VERSION" "DESCRIPTION"
  printf "%-20s %-12s %-10s %s\n" "────────────────────" "────────────" "──────────" "────────────────────────────────────────"

  for i in "${!SKILL_NAMES[@]}"; do
    local installed=""
    if [[ -f "$INSTALL_DIR/${SKILL_NAMES[$i]}/SKILL.md" ]]; then
      installed=" ${GREEN}(installed)${NC}"
    fi
    printf "%-20s %-12s %-10s %s${installed}\n" \
      "${SKILL_NAMES[$i]}" \
      "${SKILL_CATEGORIES[$i]}" \
      "${SKILL_VERSIONS[$i]}" \
      "${SKILL_DESCRIPTIONS[$i]:0:50}"
  done
  echo ""
}

cmd_uninstall() {
  local name="$1"
  local target="$INSTALL_DIR/$name"

  if [[ ! -d "$target" ]]; then
    err "Skill '$name' is not installed at $target"
    exit 1
  fi

  rm -rf "$target"
  ok "Uninstalled skill '$name'"
}

cmd_install_all() {
  scan_skills
  mkdir -p "$INSTALL_DIR"

  info "Installing all ${#SKILL_NAMES[@]} skills..."
  echo ""

  for i in "${!SKILL_NAMES[@]}"; do
    install_skill "$i"
  done

  echo ""
  ok "All skills installed to $INSTALL_DIR"
}

cmd_interactive() {
  if ! check_gum; then
    install_gum
    if ! check_gum; then
      exit 1
    fi
  fi

  scan_skills

  # Build display lines for gum filter
  local options=()
  for i in "${!SKILL_NAMES[@]}"; do
    local installed=""
    if [[ -f "$INSTALL_DIR/${SKILL_NAMES[$i]}/SKILL.md" ]]; then
      installed=" [installed]"
    fi
    options+=("$(printf "%-20s  %-12s  v%-8s  %s%s" \
      "${SKILL_NAMES[$i]}" \
      "${SKILL_CATEGORIES[$i]}" \
      "${SKILL_VERSIONS[$i]}" \
      "${SKILL_DESCRIPTIONS[$i]:0:45}" \
      "$installed")")
  done

  # Header
  gum style \
    --border rounded \
    --border-foreground 212 \
    --padding "1 2" \
    --margin "1 0" \
    "🛠  elastic-docs-skills installer" \
    "" \
    "Select skills to install (use TAB to select, ENTER to confirm)"

  # Multi-select with gum filter
  local selected
  selected=$(printf '%s\n' "${options[@]}" | gum filter --no-limit --height 20 --placeholder "Type to filter skills...") || true

  if [[ -z "$selected" ]]; then
    warn "No skills selected."
    exit 0
  fi

  echo ""
  mkdir -p "$INSTALL_DIR"

  # Match selections back to skill indices and install
  local count=0
  while IFS= read -r line; do
    local selected_name
    selected_name="$(echo "$line" | awk '{print $1}')"

    for i in "${!SKILL_NAMES[@]}"; do
      if [[ "${SKILL_NAMES[$i]}" == "$selected_name" ]]; then
        install_skill "$i"
        ((count++))
        break
      fi
    done
  done <<< "$selected"

  echo ""
  gum style \
    --foreground 212 \
    --bold \
    "✓ Installed $count skill(s) to $INSTALL_DIR"
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
