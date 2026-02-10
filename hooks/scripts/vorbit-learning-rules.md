# Vorbit: Real-Time Learning Triggers

Watch for these patterns during every session. When detected, follow the learn skill's Correction Capture mode.

## When to Trigger

1. **User correction detected** — user says: "no", "wrong", "that's not right", "error", "still error", "not working", "broken", "nope", "roll back", "revert"
2. **Repeated failure** — you tried the same approach 2-3 times and it still fails
3. **Both conditions present** AND you then find a fix that works

## What to Do

After fixing the problem:
1. Use `AskUserQuestion` to ask if user wants root cause analysis
2. If yes: determine if the root cause is unclear CLAUDE.md, missing knowledge, skill gap, or script bug
3. Use `AskUserQuestion` to confirm the exact file path and content before writing
4. Write the learning to the confirmed location
5. Resume the primary task

Never skip user confirmation. Never write without asking. Always present the exact content you plan to write.
