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

# --- Install session end hook ---
SETTINGS_FILE="$GEMINI_HOME/settings.json"
HOOK_CMD="python3 $REPO_ROOT/scripts/hooks/gemini-session-end.py"

python3 - "$SETTINGS_FILE" "$HOOK_CMD" << 'PYEOF'
import json, sys
from pathlib import Path

settings_path = Path(sys.argv[1])
hook_cmd = sys.argv[2]

vorbit_hook = {
    "name": "vorbit-learn-capture",
    "type": "command",
    "command": hook_cmd,
}

if settings_path.exists():
    settings = json.loads(settings_path.read_text())
else:
    settings = {}

# Check if already installed
hooks = settings.get("hooks", {})
session_end = hooks.get("SessionEnd", [])
for group in session_end:
    for hook in group.get("hooks", []):
        if hook.get("name") == "vorbit-learn-capture":
            print(f"✓ SessionEnd hook already installed in {settings_path}")
            sys.exit(0)

# Add the hook
if not session_end:
    session_end = [{"hooks": []}]
session_end[0].setdefault("hooks", []).append(vorbit_hook)
hooks["SessionEnd"] = session_end
settings["hooks"] = hooks

settings_path.parent.mkdir(parents=True, exist_ok=True)
settings_path.write_text(json.dumps(settings, indent=2) + "\n")
print(f"✓ SessionEnd hook installed in {settings_path}")
PYEOF

echo ""
echo "Done. Restart Gemini CLI to pick up changes."
