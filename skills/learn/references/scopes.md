# File Scopes

The skill reads and writes across three scopes. Know which scope you're in before touching any file.

| Scope | Root | What lives here | Writable? |
|---|---|---|---|
| **Project** | `$PROJECT_ROOT/` | CLAUDE.md, `.claude/rules/`, `.claude/learnings/pending.md`, `.claude/review-rules.md` | Yes — all modes |
| **User** | `~/.claude/` | `settings.json` (prompt hook), `rules/vorbit-learning.md`, session transcripts | Read-only from skill. Stop hook manages writes via bootstrap. |
| **Plugin** | vorbit plugin dir | `skills/*/SKILL.md`, `hooks/scripts/*.sh` | Yes — only for `skill-fix` and `script-fix` |

## Resolving plugin root

`${CLAUDE_PLUGIN_ROOT}` is only available in hooks, not in skills. To find the plugin directory:

```bash
# Search for the vorbit plugin manifest
find ~ -path "*/.claude-plugin/plugin.json" -maxdepth 6 2>/dev/null | head -5
```

Pick the result containing `vorbit`. The parent of `.claude-plugin/` is the plugin root.

## Absolute paths for skill-fix and script-fix

**For `skill-fix` and `script-fix` entries in pending.md**, always store the **full absolute path** in the Target field so the reviewing agent doesn't need to search:
```
- **Target:** /Users/ash/Desktop/vorbit/skills/learn/SKILL.md
```
