---
name: prd
description: Use when user asks to "write PRD", "create requirements", "define feature", "document requirements", "product spec", "clarify user flow", "UX analysis", "edge case analysis", "analyze user stories", "find edge cases", "user journey", or wants to create a complete Product Requirements Document with user stories built through exhaustive questioning.
---

# PRD Skill

Create complete Product Requirements Documents through exhaustive questioning. User stories are built with UX detail - each answer becomes an acceptance criterion.

**Key Principle:** Ask questions, capture answers, answers become acceptance criteria. Never assume.

---

## Step 1: Problem & Users (Quick Context)

Use `AskUserQuestion` to clarify:

1. **Problem** - "What problem does this solve? (1-2 sentences)"
2. **Users** - "Who has this problem?"
3. **Scope** - "What are the main things users need to do?" (This seeds user stories)

Keep this fast - detailed work happens per user story.

---

## Step 2: Identify User Stories

From Step 1 scope answer, identify distinct user stories:

```
Based on your scope, I see these user stories:
- US-001: [Goal 1]
- US-002: [Goal 2]
- US-003: [Goal 3]

Does this capture everything? Any to add/remove?
```

Get user confirmation before proceeding.

---

## Step 3: Build Each User Story (Exhaustive UX Questioning)

**For EACH user story, do exhaustive UX questioning.**

### 3.1 Announce the User Story
```
Building US-XXX: [Title]
As a [user], I want [goal]...
```

### 3.2 Question by Category

**>>> READ `references/question-matrix.md` for full question list <<<**

Use `AskUserQuestion` with 2-4 questions per batch. Go through each category:

| Category | Questions | Output |
|----------|-----------|--------|
| 1. Entry & Happy Path | How user arrives, step-by-step flow | UX Expectation + Happy Path ACs |
| 2. Validation | Field rules, error messages, timing | Validation ACs |
| 3. System Errors | API failures, offline, retries | Error ACs |
| 4. Loading & Empty | Loading UI, zero state, no results | State ACs |
| 5. Permissions | Roles, session expiry, unauthorized | Permission ACs |
| 6. Device & Accessibility | Mobile, keyboard, screen reader | Accessibility ACs |
| 7. Concurrent & Time | Multi-tab, multi-user, timezone | Edge Case ACs |
| 8. Recovery | Undo, drafts, exit warning | Recovery ACs |

**Skip categories not relevant to the task.**

### 3.3 Compile User Story

Format each user story using template from `references/output-templates.md`:

```markdown
### US-XXX: [Title]

As a [user], I want [goal], so that [benefit].

**UX Expectation:**
[User's description of ideal experience - their exact words]

**Acceptance Criteria:**

Happy Path:
- [ ] [User's answer: step 1]
- [ ] [User's answer: step 2]
- [ ] [User's answer: success confirmation]

Validation:
- [ ] When [field] is [invalid], show "[user's error message]"

Errors:
- [ ] When API fails, [user's answer]
- [ ] When offline, [user's answer]

States:
- [ ] Loading: [user's answer]
- [ ] Empty: [user's answer]

Permissions:
- [ ] When unauthorized, [user's answer]

Accessibility:
- [ ] [user's keyboard answer]
- [ ] [user's mobile answer]

Edge Cases:
- [ ] [user's answer from concurrent/time questions]
```

**>>> REPEAT Step 3 for EACH user story <<<**

---

## Step 4: Constraints & Success Criteria

After all user stories are built:

Use `AskUserQuestion`:
- "Any constraints? (Budget, timeline, compliance, tech stack)"
- "What's explicitly out of scope?"
- "How do we measure success? (Include specific numbers)"

---

## Step 5: Review Complete PRD

Show the complete PRD to user:

```markdown
# [Feature Name]

## Problem
[From Step 1 - max 3 sentences]

## Users
[From Step 1]

## User Stories

[All compiled user stories from Step 3]

## Constraints
[From Step 4]

## Out of Scope
[From Step 4]

## Success Criteria
[From Step 4 - with numbers]
```

Ask: "Here's the complete PRD with X user stories and Y acceptance criteria. Ready to save?"

---

## Step 6: Save Document

**Only proceed after user confirms.**

Save the PRD as a markdown file in the user's workspace folder.

Filename format: `prd-[feature-name-kebab-case].md`

---

## Step 7: Report

```
## PRD Complete

**File:** [link to saved file]

### Summary
- User stories: X
- Total acceptance criteria: Y

### User Stories
| Story | ACs |
|-------|-----|
| US-001: [title] | X |
| US-002: [title] | Y |

### Next Steps
Ready to implement! Each acceptance criterion becomes a testable requirement.
```

---

## Key Principle: User Answers = Acceptance Criteria

| Question | User Answer | Becomes |
|----------|-------------|---------|
| "What if email empty?" | "Show 'Email required'" | `- [ ] When email empty, show "Email required"` |
| "What during loading?" | "Spinner with text" | `- [ ] Loading: Show spinner with text` |
| "What if API fails?" | "Retry button, keep data" | `- [ ] When API fails, show retry, preserve data` |

**Never interpret.** Use user's exact words in acceptance criteria.

---

## Reference Files

| File | When to Read | Purpose |
|------|--------------|---------|
| `references/question-matrix.md` | Step 3.2 | All UX questions by category |
| `references/output-templates.md` | Step 3.3, 5 | Exact format for PRD and user story outputs |
