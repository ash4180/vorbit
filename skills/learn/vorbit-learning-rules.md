# Vorbit: Real-Time Learning Triggers

Watch for these patterns during every session. When detected, follow the learn skill's Correction Capture mode.

## When to Trigger

**Correction keywords** — any single word/phrase triggers Correction Capture:
"nope", "wrong", "that's not right", "still error", "not working", "broken", "roll back", "revert", "that's not how"

<!-- correction-keywords: nope,wrong,that's not right,still error,not working,broken,roll back,revert,that's not how -->

Repeated failure is NOT required. One correction = one trigger.

**Voluntary capture keywords** — triggers Voluntary Capture:
"remember this", "save this", "note this", "keep this", "don't forget this", "log this", "learn this"

<!-- voluntary-keywords: remember this,save this,note this,keep this,don't forget this,log this,learn this -->

## Stop-Hook Voluntary Capture Flow

When you see a message starting with `[VORBIT:VOLUNTARY-CAPTURE]`, the stop hook detected the user explicitly asking to save something. Run this flow:

**1. Identify what to save**
- Read the `USER:` message in context — what learning did the user want to capture?
- Read surrounding `A:` context to understand the full situation

**2. Present via `AskUserQuestion`**
Use `AskUserQuestion` with three fields:
- **Root cause** — classify the learning type (from `references/format.md`: `claude-md`, `knowledge`, `skill`, `script`, `agent-mistake`, `user-preference`, `tool-behavior`, `general`)
- **Rule** — the concise imperative rule to save (commit-message style)
- **Destination** — absolute path of the file to write to (resolved from `references/routing.md`)

**3. On approve** — write a structured entry to `~/.claude/rules/unprocessed-corrections.md`
**4. On reject** — do nothing, session ends

Never skip `AskUserQuestion`. Never write without user confirmation. Always show the exact root cause, rule, and destination before writing.

## Stop-Hook Correction Flow

When you see a message starting with `[VORBIT:CORRECTION-CAPTURE]`, the stop hook has detected correction keywords and injected context from the just-ended session. Run this flow:

**1. Read references**
- Read `references/format.md` to classify the correction type (scope + type)
- Read `references/routing.md` to determine the destination file

**2. Consolidate**
- If multiple corrections in the context are about the **same underlying error**, treat them as ONE learning
- Derive a single root cause, rule, and destination covering all of them

**3. Present via `AskUserQuestion`**
Use `AskUserQuestion` with three fields:
- **Root cause** — why this happened (classify using `format.md`: `claude-md`, `knowledge`, `skill`, `script`, `agent-mistake`, `user-preference`, `tool-behavior`, `general`)
- **Rule** — the concise imperative rule to add (commit-message style, from `format.md` Title Format)
- **Destination** — absolute path of the file to write to (resolved from `routing.md`)

**4. On approve** — write a structured entry to `~/.claude/rules/unprocessed-corrections.md`
**5. On reject** — do nothing, session ends

Never skip `AskUserQuestion`. Never write without user confirmation. Always show the exact root cause, rule, and destination before writing.

## Real-Time Correction Capture (mid-session)

> This flow is for **user-reported corrections only**. If the agent self-discovers an error, write the labeled learning fields (see format below) in your response — the stop hook picks them up automatically.

After fixing the problem:
1. Use `AskUserQuestion` to ask if user wants root cause analysis
2. If yes: determine if the root cause is unclear CLAUDE.md, missing knowledge, skill gap, or script bug
3. Use `AskUserQuestion` to confirm the exact file path and content before writing
4. Write the learning to the confirmed location
5. Resume the primary task

Never skip user confirmation. Never write without asking. Always present the exact content you plan to write.

## Self-Discovered Learning Format

When the agent discovers and fixes an error without user prompting, write these labeled fields as plain lines in your response. The stop hook reads the field names below and assembles the output — the agent only provides the values.

<!-- learning-fields: ROOT_CAUSE,RULE,DESTINATION -->

<!-- vorbit-learning-rules -->
