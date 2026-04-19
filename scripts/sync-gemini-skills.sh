#!/bin/bash
set -euo pipefail

REPO_ROOT="$(cd "$(dirname "$0")/.." && pwd)"
GEMINI_HOME="${GEMINI_HOME:-$HOME/.gemini}"

# --- Sync skills ---
TARGET_DIR="$GEMINI_HOME/skills"
SOURCE_DIR="$REPO_ROOT/gemini/skills"

mkdir -p "$TARGET_DIR"

for item in "$SOURCE_DIR"/*; do
  [ -e "$item" ] || continue
  name="$(basename "$item")"
  target="$TARGET_DIR/$name"
  if [ -L "$target" ] || [ -e "$target" ]; then
    rm -rf "$target"
  fi
  ln -s "$item" "$target"
done

echo "✓ Skills synced into $TARGET_DIR"
echo ""
echo "Done. Restart Gemini CLI to pick up changes."
