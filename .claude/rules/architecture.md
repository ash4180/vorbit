# Architecture Rules

- **`.agent/workflows/` is for Gemini, not duplication:** `commands/` + `skills/` are Claude Code. `.agent/workflows/` is Google Antigravity (Gemini). Parallel implementations for different platforms. Gemini workflows must be self-contained — they can't access Claude Code's skills or commands.
