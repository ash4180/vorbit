#!/bin/bash
set -euo pipefail

PLUGIN_NAME="vorbit"
MARKETPLACE_NAME="local"
PLUGIN_SOURCE="$(cd "$(dirname "$0")" && pwd)"
MARKETPLACE_DIR="$HOME/.claude/plugins/marketplaces/$MARKETPLACE_NAME"
INSTALLED_PLUGINS="$HOME/.claude/plugins/installed_plugins.json"

echo "Setting up $PLUGIN_NAME from: $PLUGIN_SOURCE"

# 1. Create local marketplace structure
echo "→ Creating local marketplace..."
mkdir -p "$MARKETPLACE_DIR/.claude-plugin"
mkdir -p "$MARKETPLACE_DIR/plugins"

# 2. Write marketplace manifest
cat > "$MARKETPLACE_DIR/.claude-plugin/marketplace.json" <<EOF
{
  "\$schema": "https://anthropic.com/claude-code/marketplace.schema.json",
  "name": "$MARKETPLACE_NAME",
  "version": "0.0.0",
  "description": "Local development plugins",
  "owner": { "name": "$(whoami)" },
  "plugins": [
    {
      "name": "$PLUGIN_NAME",
      "description": "TDD-first product development workflows for Claude Code",
      "source": "./plugins/$PLUGIN_NAME",
      "category": "development"
    }
  ]
}
EOF

# 3. Symlink plugin source into marketplace (skip if already exists)
if [ -L "$MARKETPLACE_DIR/plugins/$PLUGIN_NAME" ]; then
  echo "→ Symlink already exists, skipping"
elif [ -e "$MARKETPLACE_DIR/plugins/$PLUGIN_NAME" ]; then
  echo "→ Warning: $MARKETPLACE_DIR/plugins/$PLUGIN_NAME exists but is not a symlink. Remove it manually."
  exit 1
else
  ln -s "$PLUGIN_SOURCE" "$MARKETPLACE_DIR/plugins/$PLUGIN_NAME"
  echo "→ Symlinked plugin source"
fi

# 4. Register marketplace (skip if already registered)
if claude plugin marketplace list --json 2>/dev/null | grep -q "\"name\": *\"$MARKETPLACE_NAME\""; then
  echo "→ Marketplace '$MARKETPLACE_NAME' already registered, skipping"
else
  claude plugin marketplace add "$MARKETPLACE_DIR"
  echo "→ Registered marketplace"
fi

# 5. Install plugin (skip if already installed)
if claude plugin list --json 2>/dev/null | grep -q "\"id\": *\"$PLUGIN_NAME@$MARKETPLACE_NAME\""; then
  echo "→ Plugin already installed, skipping"
else
  claude plugin install "$PLUGIN_NAME@$MARKETPLACE_NAME"
  echo "→ Installed plugin"
fi

# 6. Enable plugin
claude plugin enable "$PLUGIN_NAME@$MARKETPLACE_NAME" 2>/dev/null || true
echo "→ Enabled plugin"

# 7. Create real cache directory with symlinked contents (for live editing)
# The plugin system deletes symlinked version directories (detects as orphaned).
# Fix: make the version directory REAL, but symlink each item inside it.
# ${CLAUDE_PLUGIN_ROOT} resolves to the cache version dir, so paths like
# ${CLAUDE_PLUGIN_ROOT}/hooks/scripts/foo.sh follow the content symlinks to source.
CACHE_DIR="$HOME/.claude/plugins/cache/$MARKETPLACE_NAME/$PLUGIN_NAME"
VERSION=$(grep -o '"version": *"[^"]*"' "$PLUGIN_SOURCE/.claude-plugin/plugin.json" | head -1 | sed 's/.*": *"//;s/"//')
CACHE_VERSION_DIR="$CACHE_DIR/$VERSION"

# Remove old cache (whether symlink or real copy)
if [ -L "$CACHE_VERSION_DIR" ] || [ -d "$CACHE_VERSION_DIR" ]; then
  rm -rf "$CACHE_VERSION_DIR"
fi

# Create real directory and symlink each item from source
mkdir -p "$CACHE_VERSION_DIR"
for item in "$PLUGIN_SOURCE"/*  "$PLUGIN_SOURCE"/.[!.]* ; do
  [ -e "$item" ] || continue
  basename="$(basename "$item")"
  # Skip .git to avoid confusing the plugin system
  [ "$basename" = ".git" ] && continue
  ln -s "$item" "$CACHE_VERSION_DIR/$basename"
done
echo "→ Created cache directory with symlinked contents"

echo ""

# 8. Python tooling (via asdf + pip)
echo "→ Setting up Python tooling..."
if command -v asdf &>/dev/null; then
  if ! asdf plugin list 2>/dev/null | grep -q "^python$"; then
    echo "  Adding asdf python plugin..."
    asdf plugin add python
  fi
  echo "  Running asdf install (pins Python version from .tool-versions)..."
  asdf install 2>/dev/null || echo "  Warning: asdf install failed — run 'asdf install' manually if needed"
else
  echo "  Warning: asdf not found — Python version not pinned. Install asdf to use .tool-versions."
fi

PIP_CMD=$(command -v pip3 2>/dev/null || command -v pip 2>/dev/null || true)
if [[ -n "$PIP_CMD" ]]; then
  echo "  Installing dev dependencies via pip (pytest)..."
  # pip >= 22 supports editable installs from pyproject.toml; older pip needs fallback
  if "$PIP_CMD" install -e ".[dev]" --quiet 2>/dev/null; then
    echo "  Installed via 'pip install -e \".[dev]\"'"
  else
    "$PIP_CMD" install "pytest>=7.0" --quiet 2>/dev/null || echo "  Warning: pip install failed — run 'pip install pytest' manually"
  fi
else
  echo "  Warning: pip not found — run 'pip install pytest' manually to install pytest"
fi

echo ""
echo "Done! Restart Claude Code to load $PLUGIN_NAME."
echo "\${CLAUDE_PLUGIN_ROOT} → $CACHE_VERSION_DIR (real dir, contents symlinked to $PLUGIN_SOURCE)"
