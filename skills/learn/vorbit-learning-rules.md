# Vorbit: Real-Time Learning Triggers

Watch for these patterns during every session. When detected, follow the learn skill's Correction Capture mode.

## When to Trigger

**Correction keywords** — any single word/phrase triggers Correction Capture:
"no", "wrong", "that's not right", "error", "still error", "not working", "broken", "nope", "roll back", "revert", "actually", "that's not how"

Repeated failure is NOT required. One correction = one trigger.

**Voluntary capture keywords** — triggers Voluntary Capture:
"remember this", "save this", "note this", "keep this", "don't forget this", "log this"

## What to Do

> This flow is for **user-reported corrections only**. If the agent self-discovers an error, write directly to `~/.claude/rules/unprocessed-corrections.md` instead.

After fixing the problem:
1. Use `AskUserQuestion` to ask if user wants root cause analysis
2. If yes: determine if the root cause is unclear CLAUDE.md, missing knowledge, skill gap, or script bug
3. Use `AskUserQuestion` to confirm the exact file path and content before writing
4. Write the learning to the confirmed location
5. Resume the primary task

Never skip user confirmation. Never write without asking. Always present the exact content you plan to write.

<!-- vorbit-learning-rules -->
