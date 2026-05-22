---
name: ux
version: 2.0.0
description: Senior UX product designer knowledge layer. Called by /explore, /prd, /journey, /figma, /epic, /implement, /verify when they need to clarify UX requirements, check edge-case coverage, validate state design, or look up decision frameworks. Transforms vague requirements into precise acceptance criteria via exhaustive questioning, and serves as the canonical reference for UX patterns across the design chain.
---

# UX Clarification Skill

Senior-UX-designer knowledge: exhaustive question matrix, edge-case catalog, decision frameworks. Other vorbit skills consult `_shared/ux-knowledge/` directly when they need UX patterns. This skill itself is the **workflow** for exhaustive Q&A → verbatim ACs.

**Core Principle:** Ask questions → User answers → Answers become acceptance criteria (verbatim).

> **Locate `_shared/`**: This skill ships as a plugin, so `_shared/` files live in the plugin cache, not your project. Before reading any `_shared/...` path below, run `ls -d ~/.claude/plugins/cache/local/vorbit/*/skills/_shared 2>/dev/null | head -1` and use the output as the absolute base for every `_shared/...` reference.

---

## When to Use This Skill

| Calling Skill | Trigger |
|---------------|---------|
| **/explore** | Sharpening compare-and-contrast prompts; checking edge-case coverage before drafting options |
| **/prd** | Building each user story; AC quality (verbatim user words rule); flow/error gaps |
| **/journey** | Flow patterns (entry/exit, decisions, errors) — what to ask about per question-matrix |
| **/figma** | UI state patterns (empty/loading/error/disabled), accessibility, microcopy decisions |
| **/epic** | No PRD exists; need to gather requirements before sub-issue planning |
| **/implement** | Requirements unclear, edge cases undefined mid-implementation |
| **/verify** | Looking up what to check (state design, accessibility, edge cases per category) |

Each calling skill may consult `_shared/ux-knowledge/` directly without invoking this full workflow — see "Direct Reference Access" below.

---

## Input

Receive from calling skill:
- **User Story** or **Task Description**
- **Context** (what's already known)

---

## Process: Exhaustive Q&A

### Step 1: Load Question Matrix

**>>> READ `_shared/ux-knowledge/question-matrix.md` NOW <<<**

This file contains 14 question categories. Use ALL relevant categories.

### Step 2: Question by Category

Use `AskUserQuestion` with 2-4 questions per batch. Go through each category:

| Category | Questions From | Output |
|----------|----------------|--------|
| 1. Entry & Happy Path | Matrix sections 1-2 | UX Expectation + Happy Path ACs |
| 2. Validation | Matrix section 3 | Validation ACs |
| 3. System Errors | Matrix section 4 | Error ACs |
| 4. Permissions | Matrix section 5 | Permission ACs |
| 5. Loading & Empty | Matrix sections 6-7 | State ACs |
| 6. Concurrent & Time | Matrix sections 8-9 | Edge Case ACs |
| 7. Device & Accessibility | Matrix sections 10-11 | Accessibility ACs |
| 8. Recovery & Notifications | Matrix sections 12-13 | Recovery ACs |

**Skip categories not relevant to the task.**

### Step 3: Cross-Check Edge Cases

**>>> READ `_shared/ux-knowledge/edge-case-catalog.md` NOW <<<**

After user answers:
1. Compare answers against catalog entries
2. Identify common edge cases NOT covered
3. Ask follow-up: "What should happen when [scenario]?"

### Step 4: Resolve Uncertainty

**>>> READ `_shared/ux-knowledge/ux-philosophy.md` WHEN USER IS UNSURE <<<**

If user says "I don't know" or "whatever you think":
1. Read philosophy file for decision frameworks
2. Present options with trade-offs
3. User's choice becomes the AC

---

## Output Format

Return structured UX content to calling skill:

```markdown
## UX Clarification: [Task/Story Title]

### UX Expectation
[User's description of ideal experience - their exact words]

### User Flow
[Describe textually in Entry → step → step → Exit form. For published diagrams, recommend `/vorbit:design:journey`.]

### Acceptance Criteria

**Happy Path:**
- [ ] [User's answer: step 1]
- [ ] [User's answer: step 2]
- [ ] [User's answer: success confirmation]

**Validation:**
- [ ] When [field] is [invalid], show "[user's error message]"

**Errors:**
- [ ] When API fails, [user's answer]
- [ ] When offline, [user's answer]

**States:**
- [ ] Loading: [user's answer]
- [ ] Empty: [user's answer]

**Permissions:**
- [ ] When unauthorized, [user's answer]

**Accessibility:**
- [ ] [user's keyboard answer]
- [ ] [user's mobile answer]

**Edge Cases:**
- [ ] [user's answer from concurrent/time questions]
- [ ] [gaps found from edge-case-catalog.md]
```

---

## Flow Diagrams — Delegate to /journey

`/ux` does NOT generate flow diagrams. If the user needs a visual flow during clarification:

- Describe the flow textually in the output (Entry → step → step → Exit form)
- Suggest `/vorbit:design:journey` for a published Excalidraw diagram with shareable URL

Single canonical tool for flow visualization (`/journey` → Excalidraw) avoids duplicate-artifact problems.

---

## Key Principle: Verbatim Answers

| Question | User Answer | Becomes |
|----------|-------------|---------|
| "What if email empty?" | "Show 'Email required'" | `- [ ] When email empty, show "Email required"` |
| "What during loading?" | "Spinner with text" | `- [ ] Loading: Show spinner with text` |
| "What if API fails?" | "Retry button, keep data" | `- [ ] When API fails, show retry, preserve data` |

**Never interpret.** Use user's exact words.

---

## Quick Mode

For simple tasks (< 3 acceptance criteria needed):
- Ask only relevant categories
- Skip edge case catalog
- Return minimal output

---

## Direct Reference Access (for consumer skills)

`/explore`, `/prd`, `/journey`, `/figma`, `/epic`, `/implement`, and `/verify` can read `_shared/ux-knowledge/` files directly without invoking this full skill. Each file is self-contained and serves a specific purpose:

| File | When to Read | Purpose | Used by |
|------|--------------|---------|---------|
| `_shared/ux-knowledge/question-matrix.md` | Designing questions for a feature | All 14 question categories with prompts | /explore, /prd, /journey, /ux |
| `_shared/ux-knowledge/edge-case-catalog.md` | Checking edge-case coverage | Concrete edge cases per input/state/network/auth/device | /prd, /figma, /implement, /verify, /ux |
| `_shared/ux-knowledge/ux-philosophy.md` | Making UX trade-off decisions | Decision frameworks (block vs warn, auto-save vs manual, etc.) + state design principles | /explore, /prd, /figma, /verify, /ux |

**Rule for consumer skills:** Direct read = quick lookup. Full /ux invocation = exhaustive Q&A producing structured ACs. Use direct read when you know what you need (e.g., "what does the catalog say about empty states?"). Use full /ux invocation when the requirements are vague and you need the whole question-batch ritual.
