#!/usr/bin/env sh
# SessionStart hook: injects the full adhd ruleset when the user has opted in
# by creating $CLAUDE_CONFIG_DIR/.vorbit-adhd-always (default ~/.claude).
# Never blocks session start: any failure exits 0.
#
# Vendored from ayghri/i-have-adhd hooks/always-on.sh (MIT) — keep diffable.
# Pure POSIX sh so it runs anywhere Claude Code runs a command hook (sh on
# macOS/Linux, Git Bash on Windows) without depending on a Node install being
# on PATH.

claude_dir="${CLAUDE_CONFIG_DIR:-$HOME/.claude}"
flag_path="$claude_dir/.vorbit-adhd-always"

# Only fire when the user has opted in.
[ -f "$flag_path" ] || exit 0

# $0 is the absolute script path substituted into hooks.json by Claude Code,
# so resolve SKILL.md relative to it instead of trusting an exported env var.
script_dir=$(cd "$(dirname -- "$0")" && pwd) || exit 0
skill_dir="$script_dir/../../skills/adhd"
skill_path="$skill_dir/SKILL.md"
[ -f "$skill_path" ] || exit 0

# Strip a leading YAML frontmatter block (--- ... --- at the very top of file).
body=$(awk '
  NR == 1 && $0 ~ /^---[[:space:]]*$/ { in_fm = 1; next }
  in_fm && $0 ~ /^---[[:space:]]*$/   { in_fm = 0; next }
  !in_fm                              { print }
' "$skill_path") || exit 0

printf 'ADHD MODE ACTIVE (always-on). The ruleset below applies to every response. Base directory for this skill: %s — resolve relative references in it against that directory. "stop adhd mode" turns it off for this session; delete %s to turn always-on off for good.\n\n%s\n' \
  "$skill_dir" "$flag_path" "$body"
