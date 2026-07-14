<!-- GENERATED from skills/ux/SKILL.md — edit the canonical file, then run: python3 -m vorbit_core.project_skills --write -->

> Skill assets: paths like `references/...` in this workflow resolve inside the installed `vorbit-ux` skill directory (a sibling of `vorbit-shared`).

# UX Clarification Skill

Exhaustive UX questioning to transform vague requirements into precise, testable acceptance criteria.

Read and follow `../references/execution-contract.md` before starting.

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

**>>> READ `references/question-matrix.md` NOW <<<**

This file contains 14 question categories. Use ALL relevant categories.

### Step 2: Question by Category

Use plain-text chat questions with 2-4 questions per batch. Go through each category:

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

**>>> READ `references/edge-case-catalog.md` NOW <<<**

After user answers:
1. Compare answers against catalog entries
2. Identify common edge cases NOT covered
3. Ask follow-up: "What should happen when [scenario]?"

### Step 4: Resolve Uncertainty

**>>> READ `references/ux-philosophy.md` WHEN USER IS UNSURE <<<**

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

| Evidence (preserved exactly) | Confirmed normalized criterion |
|----------|-------------|
| `E-01`: "Show 'Email required'" | When email is empty on submit, show "Email required" next to the field. |
| `E-02`: "Spinner with text" | Ask which text; after confirmation, record the loading criterion. |
| `E-03`: "Retry button, keep data" | When the request fails, keep entered data and show a Retry button. |

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
