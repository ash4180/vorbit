---
name: ticket
description: Use when the user asks to create a Linear ticket for the current branch work ("create ticket", "create the Linear ticket", "make a ticket") or to post or refresh its short human-readable Linear summaries. It reads the branch prd.md and epic.md, creates or updates one compact summary ticket per user story with its goal and acceptance criteria, and records ticket IDs back into prd.md. Tickets stay summaries; implementation detail lives only in the branch spec files. Requires Linear and an existing branch PRD; do not use to write the PRD or epic plan, implement code, or create engineering sub-issues.
---

# Ticket Skill

Post short, human-readable Linear summaries of the branch spec files: one compact ticket per user story. Linear is the shared window for humans; the spec files stay the source of truth.

Read and follow `../_shared/execution-contract.md` before starting.

Read `../_shared/spec-files.md` for spec path resolution and the `## Linear Sync` record format.

Before any Linear call, read `_shared/mcp-tool-routing.md`. Verb names below describe intent; never substitute an operation name remembered from another runtime.

## Step 1: Read the Branch Specs

1. Resolve the spec folder per `../_shared/spec-files.md`.
2. Require `prd.md`. If missing, run `git worktree list`, report any sibling worktree that may hold it, direct the user to `/vorbit:design:prd`, and stop.
3. Read `epic.md` when present — it shows which criteria are done, for the checkboxes. Its absence is fine; every box then stays unchecked.
4. Parse the `## Linear Sync` section in `prd.md` when present: it maps `US-###` to previously created ticket IDs. This decides create vs update; never trust memory of earlier runs over this record.

## Step 2: Verify Linear and Resolve Team

1. Use the connector's verified lightweight identity/read operation to verify auth/session. On failure, tell the user to run `/mcp` to reconnect and stop.
2. Use its verified team-list operation with a scoped limit (for example 10-20). If multiple teams exist, ask the user which one.
3. Use its verified project-list operation scoped to the selected team. If multiple projects exist, ask; if none exist, omit the project field.

**Reliability rules:**
- Keep reads scoped by the selected team and a limit when the schema supports them; no unfiltered workspace-wide listing
- On temporary MCP/API error, retry once with the same parameters
- Only block execution when auth fails

## Step 3: Compose the Summaries

One ticket per user story (or per `TS-###` technical section). Write for a person who will never open the spec files — plain language, no engineering detail.

**Title:** `[Feature Name]: [Story title]` (feature name = `prd.md` H1)

**Description template:**

```markdown
[One-sentence story goal in plain words]

## What done looks like
- [ ] [Acceptance criterion, verbatim from prd.md]
- [ ] [Another criterion, verbatim]
```

The ticket holds only the goal and the criteria. No progress, branch, or date sections: Linear already shows the linked branch and PR, and QA results live in the linked QA report.

**Composition rules:**
- No task-level engineering detail, file paths, or tables
- Follow the execution contract's Tracker Communication rule: no Vorbit mentions, tool attribution, local commands, or private spec/worktree locations in the posted title or description. Check the composed text before the mutation preview
- Check a criterion's box only when `epic.md` shows every task quoting that criterion as `done`; otherwise leave it unchecked
- This description is a full replacement on every sync — do not try to merge with manual edits; warn in the preview that manual Linear edits to these tickets are overwritten

**Mutation preview (required):** show every composed ticket (create vs update, title, target team/project) and get one approval before writing. If the user asked for a preview only, stop here.

## Step 4: Create or Update Tickets

For each story, in PRD order:

1. **Mapped ID exists** (from `## Linear Sync`): fetch the ticket; if found, update its title and description with the composed summary. If the fetch shows it was deleted, report it and create a fresh ticket.
2. **No mapped ID:** call the operation whose inspected schema explicitly **creates an issue**, with the composed title/description and the selected team/project in the exact field/type the schema requires.
3. Record each successful `(US-###, ticket ID, URL)` immediately so a retry resumes instead of duplicating work.
4. On partial failure, stop and report which stories synced, which did not, and the resume point.

Do not create sub-issues, labels, statuses, comments, or any engineering breakdown. One flat summary ticket per story is the whole Linear footprint.

## Step 5: Record the Mapping and Report

1. Rewrite the `## Linear Sync` section at the end of `prd.md` (create it when absent), one line per story:
   `US-001 → ABC-123 — https://linear.app/... (synced YYYY-MM-DD)`
   Preserve every other part of `prd.md` byte-for-byte.
2. Report:
   - Tickets created and updated, with URLs, in PRD order
   - Criteria checked per story (checked / total)
   - Team and project used
   - Reminder: summaries go stale as work continues — re-run `/vorbit:ticket` after finishing tasks to refresh them
