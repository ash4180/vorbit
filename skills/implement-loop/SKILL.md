---
name: implement-loop
version: 1.0.0
description: Use when user says "implement --loop", "loop mode", "iterate on issues", "auto-continue", or adds --loop flag to implement. Manages autonomous iteration through sub-issues until completion.
---

# Implement Loop Skill

Manages Ralph Wiggum-style iteration loops for the implement command. Handles sub-issue tracking, state management, and completion detection.

## When to Use

- User runs `/vorbit:implement:implement [issue] --loop`
- User runs `/vorbit:implement:implement [issue] --cancel`

## Loop Initialization

### Step 1: Parse Arguments

Extract from `$ARGUMENTS`:
- Issue ID or URL (required for loop mode)
- `--loop` flag (activates loop mode)
- `--cancel` flag (stops active loop)
- `--completion-signal "text"` (optional custom signal)

### Step 2: Handle --cancel

If `--cancel` detected:
1. Delete `.claude/.loop-state.json` if exists
2. Output: "🛑 Loop cancelled"
3. Stop immediately

### Step 3: Check for Sub-issues

**CRITICAL: Always check for sub-issues first!**

1. Fetch the parent issue from Linear
2. **Parse the "Implementation Order" section from description**
   - This section defines the sequence to follow
   - Extract issue IDs in order
3. Call `list_issues` with filter `parentId: [issue ID]` to get sub-issue details
4. Match sub-issues to the Implementation Order sequence

### Step 3b: Build Work Queue from Implementation Order

**Read the parent issue description and find "Implementation Order" section:**

```markdown
## Implementation Order
1. VIB-1862 - analyze-codebase-compatibility
2. VIB-1863 - update-incident-types
3. VIB-1878 - setup-incident-dashboard-folder
...
```

**Build work queue:**
1. Parse issue IDs from Implementation Order
2. For each issue, fetch its status from Linear
3. **Skip** issues with status: Done, Completed, Cancelled
4. **Keep** remaining issues in the Implementation Order sequence

**Example:**
```
Implementation Order from parent:
1. VIB-1862 → Status: Done → SKIP
2. VIB-1863 → Status: Done → SKIP
3. VIB-1878 → Status: Backlog → Queue position 1
4. VIB-1879 → Status: Backlog → Queue position 2
5. VIB-1864 → Status: In Progress → Queue position 3
...

Work queue = [VIB-1878, VIB-1879, VIB-1864, ...]
```

### Step 4: Create State File

Create `.claude/.loop-state.json`:

**If sub-issues exist:**
```json
{
  "active": true,
  "command": "/vorbit:implement:implement [issue ID]",
  "completionSignal": "✅ All acceptance criteria met",
  "maxIterations": 50,
  "iteration": 1,
  "issueId": "[issue ID]",
  "hasSubIssues": true,
  "subIssues": ["[sub-1-id]", "[sub-2-id]", "..."],
  "parallelSubIssues": ["[ids with Parallel label]"],
  "currentSubIssueIndex": 0,
  "completedSubIssues": []
}
```

**If NO sub-issues (single issue):**
```json
{
  "active": true,
  "command": "/vorbit:implement:implement [issue ID]",
  "completionSignal": "✅ All acceptance criteria met",
  "maxIterations": 50,
  "iteration": 1,
  "issueId": "[issue ID]",
  "hasSubIssues": false,
  "subIssues": [],
  "currentSubIssueIndex": 0,
  "completedSubIssues": []
}
```

### Step 5: Output Summary

```
🔄 Loop mode activated

📋 Issue: [issue title]
   Type: [Parent with N sub-issues | Single issue]

📝 Work queue:
   1. [first item to work on]
   2. [second item]
   ...

🎯 Completion: [completion signal]
```

## During Implementation

### Which Issue to Work On

Read `.claude/.loop-state.json` and determine current target:

**If `hasSubIssues: true`:**
- Get `subIssues[currentSubIssueIndex]`
- Fetch THAT sub-issue's details from Linear
- Work on THAT sub-issue's acceptance criteria
- Ignore parent issue until all sub-issues done

**If `hasSubIssues: false`:**
- Work on the main `issueId` directly
- Check its acceptance criteria

### Parallel Sub-issues

Sub-issues with the **"Parallel"** label in Linear can run in parallel:
- Check if current sub-issue is in `parallelSubIssues`
- If yes, can use Task tool to spawn agents for other parallel issues
- Mark all parallel issues complete together

## Loop Completion

### After Each Implementation Cycle

1. **Read current state** from `.claude/.loop-state.json`

2. **Get current target issue:**
   - If `hasSubIssues`: use `subIssues[currentSubIssueIndex]`
   - If not: use `issueId`

3. **Check completion for CURRENT issue:**
   - Fetch its acceptance criteria from Linear
   - Verify ALL criteria are met
   - Verify tests pass

4. **If current issue COMPLETE:**

   For sub-issues:
   - Update Linear: mark sub-issue "Done"
   - Add comment with what was implemented
   - Update state: add to `completedSubIssues`, increment `currentSubIssueIndex`
   - Output: "✅ Sub-issue complete: [title] ([done]/[total])"

   For single issue:
   - Update Linear: mark issue "Done"
   - Output completion signal: "✅ All acceptance criteria met"

5. **If all sub-issues done:**
   - Check if `currentSubIssueIndex >= subIssues.length`
   - Fetch PARENT issue acceptance criteria
   - If parent criteria met: Output completion signal
   - If not: Continue loop to address parent requirements

6. **If current issue NOT complete:**
   - Don't update state
   - Describe what still needs work
   - Loop continues on same issue

### Progress Output

Each iteration should show:
```
📍 Current: [issue title]
   Acceptance criteria:
   - [x] Criteria 1 (done)
   - [ ] Criteria 2 (pending)

📊 Progress: [completed]/[total] issues done
```

## State File Location

- Path: `.claude/.loop-state.json`
- Gitignored (runtime only, not committed)
- Deleted when loop completes or is cancelled

## Stop Hook Integration

The stop hook (`hooks/scripts/loop-controller.sh`):
- Reads state file
- Checks for completion signal in Claude's output
- If found: deletes state, allows exit
- If not found: increments iteration, re-feeds command
- Enforces max iterations limit

## Linear Updates (REQUIRED)

**You MUST call Linear MCP tools to update issues. Don't just describe updates - actually call the tools!**

### When Starting a Sub-issue

**IMMEDIATELY call Linear to update status:**
```
Tool: update_issue
Parameters:
  - issueId: [current sub-issue ID]
  - stateId: [In Progress state ID]
```

**Add a comment:**
```
Tool: create_comment
Parameters:
  - issueId: [current sub-issue ID]
  - body: "🤖 Starting implementation via loop mode (iteration [N])"
```

### During Implementation

**Add progress comments for significant updates:**
```
Tool: create_comment
Parameters:
  - issueId: [current sub-issue ID]
  - body: "Progress: [what was done]\n\nFiles changed:\n- [file1]\n- [file2]"
```

### When Sub-issue Completes

**Update status to Done:**
```
Tool: update_issue
Parameters:
  - issueId: [current sub-issue ID]
  - stateId: [Done state ID]
```

**Add completion comment:**
```
Tool: create_comment
Parameters:
  - issueId: [current sub-issue ID]
  - body: "✅ Implementation complete\n\n## What was done\n[summary]\n\n## Files changed\n- [files]\n\n## Tests\n[test status]"
```

### When All Sub-issues Done

**Update parent issue:**
```
Tool: update_issue
Parameters:
  - issueId: [parent issue ID]
  - stateId: [Done state ID]

Tool: create_comment
Parameters:
  - issueId: [parent issue ID]
  - body: "✅ All sub-issues complete\n\nCompleted: [count] sub-issues\nIterations: [total]"
```

### Getting State IDs

Before updating, get available states:
```
Tool: list_issue_statuses
```
Find the state IDs for "In Progress" and "Done" from the response.
