# Vorbit: Runtime Learn Triggers

These rules drive automatic **capture**. Durable publication still requires review.

## Trigger keywords

**Correction keywords** — any one match is enough:
"nope", "wrong", "that's not right", "still error", "not working", "broken", "roll back", "revert", "that's not how"

<!-- correction-keywords: nope,wrong,that's not right,still error,not working,broken,roll back,revert,that's not how -->

**Voluntary capture keywords** — explicit user asks to save a learning:
"remember this", "save this", "note this", "keep this", "don't forget this", "log this", "learn this"

<!-- voluntary-keywords: remember this,save this,note this,keep this,don't forget this,log this,learn this -->

## Runtime behavior

When a runtime adapter detects one of the patterns above:

1. Normalize the event into a canonical capture record under Vorbit's store
2. Create a pending review item under `pending/`
3. Propose a scope and destination
4. Stop there

No adapter is allowed to publish a durable rule automatically.

## Claude compatibility bridge

Claude still mirrors pending items into `~/.claude/rules/pending-capture.md` and the optional Obsidian export so existing flows remain visible.

When `pending-capture.md` appears in Claude context, it is a **review reminder**, not a durable rule source. The real review action is:

```bash
python3 scripts/vorbit-learning.py pending --project-root <project-root>
python3 scripts/vorbit-learning.py approve <review-id> --approved-by <name>
python3 scripts/vorbit-learning.py reject <review-id> --reason "<why>"
```

## Review requirements

- Every durable learning requires human review
- `pending/*.json` must never be treated as live rules
- Shared scopes only become active after approval
- Agent-local rules must stay local to the source agent after approval

<!-- vorbit-learning-rules -->
