#!/bin/bash
set -euo pipefail

REPO_ROOT="$(cd "$(dirname "$0")/.." && pwd)"
CODEX_HOME="${CODEX_HOME:-$HOME/.codex}"

# --- Sync skills ---
TARGET_DIR="$CODEX_HOME/skills"
SOURCE_DIR="$REPO_ROOT/codex/skills"

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

# --- Enable hooks feature ---
CONFIG="$CODEX_HOME/config.toml"
if [ -f "$CONFIG" ]; then
  if ! grep -q "codex_hooks" "$CONFIG" 2>/dev/null; then
    printf '\n[features]\ncodex_hooks = true\n' >> "$CONFIG"
    echo "✓ Enabled codex_hooks in $CONFIG"
  fi
else
  mkdir -p "$CODEX_HOME"
  printf '[features]\ncodex_hooks = true\n' > "$CONFIG"
  echo "✓ Created $CONFIG with codex_hooks enabled"
fi

# --- Install stop hook ---
HOOKS_FILE="$CODEX_HOME/hooks.json"
HOOK_CMD="python3 $REPO_ROOT/scripts/hooks/codex-stop.py"

python3 - "$HOOKS_FILE" "$HOOK_CMD" << 'PYEOF'
import json, sys
from pathlib import Path

hooks_path = Path(sys.argv[1])
hook_cmd = sys.argv[2]

vorbit_hook = {
    "name": "vorbit-learn-capture",
    "type": "command",
    "command": hook_cmd,
}

if hooks_path.exists():
    hooks = json.loads(hooks_path.read_text())
else:
    hooks = {}

# Check if already installed
stop_hooks = hooks.get("Stop", [])
for hook in stop_hooks:
    if hook.get("name") == "vorbit-learn-capture":
        print(f"✓ Stop hook already installed in {hooks_path}")
        sys.exit(0)

# Add the hook
stop_hooks.append(vorbit_hook)
hooks["Stop"] = stop_hooks

hooks_path.parent.mkdir(parents=True, exist_ok=True)
hooks_path.write_text(json.dumps(hooks, indent=2) + "\n")
print(f"✓ Stop hook installed in {hooks_path}")
PYEOF

echo ""
echo "Done. Restart Codex CLI to pick up changes."
