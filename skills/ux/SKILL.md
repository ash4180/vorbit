---
name: ux
description: Use only when the user explicitly invokes UX clarification or another Vorbit workflow deliberately delegates unresolved experience requirements. It conducts exhaustive, category-based questioning and returns acceptance criteria using the user's answers. It does not design screens, write a PRD, implement code, or make product decisions for the user; avoid implicit use for ordinary clarification.
---

# UX Clarification Skill

Exhaustive UX questioning to transform vague requirements into precise, testable acceptance criteria.

Read and follow `../_shared/execution-contract.md` before starting.

**Core Principle:** Ask questions → preserve answers verbatim as evidence → normalize a testable criterion → get confirmation → assign the criterion to its user story.

---

## When to Use This Skill

| Calling Skill | Trigger |
|---------------|---------|
| **PRD** | Building each user story |
| **Epic** | A PRD has an unresolved UX requirement that must be confirmed before planning |
| **Implement** | Requirements unclear, edge cases undefined |

---

## Input

Receive from calling skill:
- **User Story ID** (`US-###`) and story text, or a task description that will later be assigned to a user story
- **Context** (what's already known)
- **Next available flow number** when adding flow steps to an existing PRD

Do not finalize acceptance criteria without an owning user story. If the caller has not assigned `US-###`, return provisional criteria candidates and require the caller to assign and confirm the story ID before adding them to a PRD.

---

## Process: Exhaustive Q&A

### Step 1: Load Question Matrix

Read `references/question-matrix.md` first.

This file contains 14 question categories. Use ALL relevant categories.

### Step 2: Question by Category

Use `AskUserQuestion` with 2-4 questions per batch. Go through each category:
the categories and their questions are defined in the matrix file loaded in Step 1.

**Skip categories not relevant to the task.**

### Step 3: Cross-Check Edge Cases

Read `references/edge-case-catalog.md` first.

After user answers:
1. Compare answers against catalog entries
2. Identify common edge cases NOT covered
3. Ask follow-up: "What should happen when [scenario]?"

### Step 4: Resolve Uncertainty

Read `references/ux-philosophy.md` when the user is unsure.

If user says "I don't know" or "whatever you think":
1. Read philosophy file for decision frameworks
2. Present options with trade-offs
3. Record the user's choice verbatim as evidence, then normalize and confirm it in Step 5

### Step 5: Preserve Evidence and Confirm Normalized ACs

For every answer that creates a requirement:

1. Record the question and the user's answer verbatim as `E-01`, `E-02`, ... Evidence may be fragmentary, subjective, or use the user's own terminology; do not clean it up.
2. Draft one observable, testable AC from that evidence. Preserve exact UI copy and domain terms, but normalize shorthand into an explicit condition/action/result.
3. Show any normalization that adds specificity to the user and ask for confirmation. Never turn an inference into a confirmed requirement.
4. After confirmation, record the criterion as a plain checkbox item under its owning `US-###` story heading. Acceptance criteria carry no IDs of their own — the story heading is what scopes them.
5. Link each normalized criterion to its evidence ID(s). If one answer produces multiple behaviors, split them into multiple criteria and cite the same evidence.

Raw evidence is immutable. User corrections create a new evidence entry and supersede the earlier one; do not rewrite what the user originally said.

### Step 6: Build Flow Coverage

Using the next available document-wide flow number, write the flow as a numbered list of steps under a `Flow N: [Name]` heading. Each step names what the user did, which screen or field it happened on, and what they saw as a result. Anchor the first step with **Entry:** and the last with **Exit:**. Steps carry no IDs and no coverage tags.

Preserve branches, retries, and loops in plain English inside the step text, referencing targets as "Flow N, step M" (e.g. "User retries → back to Flow 1, step 2").

Then run a completeness check before returning: walk every confirmed acceptance criterion and verify at least one flow step satisfies it. Do not return final UX content until every confirmed criterion is covered by at least one step — if one is uncovered, add the missing step or ask the user for the missing behavior. Never drop the criterion.

---

## Output Format

Return structured UX content to calling skill:

```markdown
## UX Clarification: [Task/Story Title]

### UX Expectation
[User's description of ideal experience - their exact words]

### Evidence
- `E-01` Question: "[exact question]"
  - Verbatim answer: "[exact user answer]"
- `E-02` Question: "[exact question]"
  - Verbatim answer: "[exact user answer]"

### User Flow

#### Flow 1: [Name] (Happy flow)
1. **Entry:** [which screen, and its starting state]. [User action and what they see]
2. [which screen or field]. [User action and what they see]
3. **Exit:** [observable end state]

#### Flow 2: [Name] (Error/retry)
1. **Entry:** [which screen, and its starting state]. [User action and what they see]
2. [which screen or field]. [Failure the user sees and the recovery offered]
3. User retries → back to Flow 1, step 2

### Acceptance Criteria

#### US-001: [Story Title]

**Happy Path:**
- [ ] [Confirmed observable behavior]. Evidence: `E-01`
- [ ] [Confirmed observable behavior]. Evidence: `E-02`

**Validation:**
- [ ] When [field] is [invalid], show "[user's exact error message]". Evidence: `E-03`

**Errors:**
- [ ] When the request fails, [confirmed visible result and recovery]. Evidence: `E-04`
- [ ] When offline, [confirmed visible result and recovery]. Evidence: `E-05`

**States:**
- [ ] While loading, [confirmed visible state]. Evidence: `E-06`
- [ ] When no data exists, [confirmed visible state]. Evidence: `E-07`

**Permissions:**
- [ ] When unauthorized, [confirmed visible result]. Evidence: `E-08`

**Accessibility:**
- [ ] [Confirmed keyboard behavior]. Evidence: `E-09`
- [ ] [Confirmed mobile behavior]. Evidence: `E-10`

**Edge Cases:**
- [ ] [Confirmed concurrent/time behavior]. Evidence: `E-11`
- [ ] [Confirmed catalog-derived behavior]. Evidence: `E-12`
```

The numbering above is illustrative. Evidence IDs continue sequentially across the clarification; flow steps restart at 1 within each flow. Acceptance criteria are plain checkboxes grouped under their owning `US-###` story — never give them IDs of any kind.

---

## Flow Diagram Generation

For complex flows, hand the confirmed evidence, normalized ACs, and all branches/retries to the **journey** skill. Do not call `generate_diagram` directly from UX or keep a second set of Mermaid rules here. Journey owns the current Figma prerequisite, splitting strategy, and requirement coverage check.

---

## Evidence Is Verbatim; Acceptance Criteria Are Testable

Do not silently interpret. Exact copy and terms stay exact; added conditions, timing, placement, or outcomes require confirmation. This separates audit evidence from an executable contract.

---

## Quick Mode

For simple tasks (< 3 acceptance criteria needed):
- Ask only relevant categories
- Skip edge case catalog
- Return minimal evidence plus confirmed normalized AC candidates

---

## Reference Files

| File | When to Read | Purpose |
|------|--------------|---------|
| `references/question-matrix.md` | Step 1 | All questions by category |
| `references/edge-case-catalog.md` | Step 3 | Cross-check for gaps |
| `references/ux-philosophy.md` | Step 4 | Decision frameworks when user unsure |
