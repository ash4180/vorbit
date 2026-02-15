# File Scopes

The skill reads and writes across three scopes. Know which scope you're in before touching any file.

| Scope | Root | What lives here | Writable? |
|---|---|---|---|
| **Project** | `{origin_path}/` | CLAUDE.md, `.claude/rules/`, `.claude/review-rules.md` | Yes — all modes |
| **User** | `~/.claude/` | `rules/vorbit-learning.md`, `rules/unprocessed-corrections.md`, `rules/{topic}.md` for universal learnings | Yes — digest processing writes universal learnings here, stop hook writes corrections digest |
| **Plugin** | vorbit plugin dir | `skills/*/SKILL.md`, `hooks/scripts/*.sh` | Yes — only for `skill-fix` and `script-fix` |

## Resolving plugin root

`${CLAUDE_PLUGIN_ROOT}` is only available in hooks, not in skills. To find the plugin directory:

```bash
# Search for the vorbit plugin manifest
find ~ -path "*/.claude-plugin/plugin.json" -maxdepth 6 2>/dev/null | head -5
```

Pick the result containing `vorbit`. The parent of `.claude-plugin/` is the plugin root.

## Absolute paths for skill-fix and script-fix

Always store the **full absolute path** in routing so the agent doesn't need to search:
```
- **Target:** /Users/ash/Desktop/vorbit/skills/learn/SKILL.md
```
