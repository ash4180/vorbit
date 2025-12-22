#!/usr/bin/env bash
# Vorbit installer - install commands/rules for Claude, Cursor, or Gemini
set -euo pipefail

# Find Vorbit source directory
VORBIT_SOURCE="${VORBIT_SOURCE:-$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)}"

# Defaults
DRY_RUN=0
FORCE=0
GLOBAL=0
TARGET=""

usage() {
  cat <<'EOF'
Usage: tools/install.sh [OPTIONS] <target>

Targets:
  claude    Copy commands + update CLAUDE.md (local or global with --global)
  cursor    Update .cursorrules in current directory
  gemini    Update GEMINI.md (local or global with --global)

Options:
  --dry-run   Show what would be done without making changes
  --force     Overwrite existing files (required for claude if dest exists)
  --global    Install to global location (claude: ~/.claude/CLAUDE.md, gemini: ~/.gemini/GEMINI.md)
  -h, --help  Show this help

Examples:
  bash tools/install.sh claude              # .claude/commands/ + ./CLAUDE.md
  bash tools/install.sh --global claude     # ~/.claude/commands/ + ~/.claude/CLAUDE.md
  bash tools/install.sh --dry-run cursor
  bash tools/install.sh --global gemini
EOF
}

die() { echo "❌ $1" >&2; exit 1; }
info() { echo "$1"; }

# Parse arguments
while [[ $# -gt 0 ]]; do
  case "$1" in
    --dry-run) DRY_RUN=1; shift ;;
    --force) FORCE=1; shift ;;
    --global) GLOBAL=1; shift ;;
    -h|--help) usage; exit 0 ;;
    -*) die "Unknown option: $1" ;;
    *) TARGET="$1"; shift ;;
  esac
done

# Validate target
if [[ -z "$TARGET" ]]; then
  echo "Error: No target specified" >&2
  echo ""
  usage
  exit 1
fi

case "$TARGET" in
  claude|cursor|gemini) ;;
  *)
    echo "Unknown target: $TARGET" >&2
    echo ""
    usage
    exit 1
    ;;
esac

# Show config for dry-run
if [[ $DRY_RUN -eq 1 ]]; then
  info "Target: $TARGET"
  info "Dry run: $DRY_RUN"
fi

# --- VORBIT BLOCK MANAGEMENT ---

VORBIT_START="# --- VORBIT START ---"
VORBIT_END="# --- VORBIT END ---"

get_vorbit_content() {
  local agent_file="$VORBIT_SOURCE/AGENT.md"
  if [[ ! -f "$agent_file" ]]; then
    die "Missing AGENT.md: $agent_file"
  fi
  cat "$agent_file"
}

# Update or append vorbit block in a file
# Usage: update_vorbit_block <file> <content>
update_vorbit_block() {
  local file="$1"
  local content="$2"

  if [[ $DRY_RUN -eq 1 ]]; then
    info "[dry-run] Would update: $file"
    return 0
  fi

  local dir
  dir="$(dirname "$file")"
  mkdir -p "$dir"

  # Build the new block
  local block_file
  block_file="$(mktemp)"
  {
    echo "$VORBIT_START"
    echo "$content"
    echo "$VORBIT_END"
  } > "$block_file"

  if [[ -f "$file" ]]; then
    # Check if block already exists
    if grep -qF "$VORBIT_START" "$file"; then
      # Replace existing block: keep before start + new block + keep after end
      local tmp_out
      tmp_out="$(mktemp)"
      local in_block=0
      while IFS= read -r line || [[ -n "$line" ]]; do
        if [[ "$line" == "$VORBIT_START" ]]; then
          in_block=1
          cat "$block_file"
        elif [[ "$line" == "$VORBIT_END" ]]; then
          in_block=0
        elif [[ $in_block -eq 0 ]]; then
          printf '%s\n' "$line"
        fi
      done < "$file" > "$tmp_out"
      mv "$tmp_out" "$file"
    else
      # Append block
      echo "" >> "$file"
      cat "$block_file" >> "$file"
    fi
  else
    # Create new file with block
    cat "$block_file" > "$file"
  fi

  rm -f "$block_file"
  info "Updated: $file"
}

# --- TARGET HANDLERS ---

install_claude() {
  local src="$VORBIT_SOURCE/commands"
  local dest
  local claude_md

  if [[ $GLOBAL -eq 1 ]]; then
    dest="$HOME/.claude/commands/vorbit"
    claude_md="$HOME/.claude/CLAUDE.md"
  else
    dest=".claude/commands/vorbit"
    claude_md="CLAUDE.md"
  fi

  if [[ ! -d "$src" ]]; then
    die "Commands directory not found: $src"
  fi

  if [[ $DRY_RUN -eq 1 ]]; then
    info "[dry-run] Would copy: $src -> $dest"
    info "[dry-run] Would update: $claude_md"
    return 0
  fi

  # Check if destination exists
  if [[ -d "$dest" ]] && [[ $FORCE -eq 0 ]]; then
    die "Destination exists: $dest. Use --force to overwrite."
  fi

  # Create parent and copy commands
  mkdir -p "$(dirname "$dest")"
  rm -rf "$dest"
  cp -r "$src" "$dest"

  local count
  count="$(find "$dest" -type f -name "*.md" | wc -l | tr -d ' ')"
  info "Installed $count command files to: $dest"

  # Inject AGENT.md into CLAUDE.md
  local content
  content="$(get_vorbit_content)"
  update_vorbit_block "$claude_md" "$content"
}

install_cursor() {
  local file=".cursorrules"
  local content
  content="$(get_vorbit_content)"
  update_vorbit_block "$file" "$content"
}

install_gemini() {
  local file
  if [[ $GLOBAL -eq 1 ]]; then
    file="$HOME/.gemini/GEMINI.md"
  else
    file="GEMINI.md"
  fi

  local content
  content="$(get_vorbit_content)"
  update_vorbit_block "$file" "$content"
}

# --- MAIN ---

case "$TARGET" in
  claude) install_claude ;;
  cursor) install_cursor ;;
  gemini) install_gemini ;;
esac

exit 0
