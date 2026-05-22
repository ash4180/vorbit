# Explore Output Schema & Validation

Reference for `/vorbit:design:explore` (see SKILL.md for the imperative flow). **The agent MUST read this file in Step 7 before drafting** and render the Template below in chat with placeholders filled in.

## Required Sections

| Section | Required | Rules |
|---------|----------|-------|
| Context Summary | Yes | 10+ Q&A insights required. Constraints and Competitors sub-lines optional — omit cleanly if not raised. |
| Problem Statement | Yes | One sentence, root cause focus |
| User Flow | Yes | Linear happy path. 3-8 steps. Plain English. Each step = one user action OR one system response. |
| Reference Patterns | If Mobbin ran | Step blocks map 1:1 to User Flow steps. Main screen reference per step + optional specific element bullets. |
| Recommendation | Yes | Direction + why, UX/product level |
| Follow-up Questions for PRD | Optional | Implementation specifics that surfaced — deferred to PRD |

## User Flow Format

The User Flow describes how the user moves through the experience from trigger to success.

**Rules:**
- Happy path only (no branches, no error paths — those go in PRD)
- Minimum 3 steps, soft ceiling around 8
- Each step is one user action or one system response — not both
- Plain English, no jargon, no component names ("Taps Continue" not "Triggers onSubmit")
- Optional compact form: `[Start] → [Step 1] → ... → [Done]`

**Example:**

```
1. User opens the alert detail page
2. Taps "Escalate" in the action bar
3. Picks an escalation level and target team
4. Confirms — system updates status to "Escalated" and notifies the team
5. Returns to the alert list with the new status visible
```

## Reference Patterns Format

When Step 3 ran, Reference Patterns map **1:1 to User Flow steps**. Each Step block contains:

- **Main screen reference** — one Mobbin URL from the anchor flow world showing the canonical screen for that step
- **Specific elements to borrow** (optional) — 0-5 bullets calling out particular blocks, buttons, copy lines, colors, or micro-interactions worth taking

**Anchor flow world** sets the overall design language. All Main screen references MUST come from this one world.

**Specific element bullets** prefer the anchor world. If a different app has a markedly better treatment for a small detail, you may cite it — but the bullet MUST include `(Borrowed from [App](URL) — [reason anchor world lacks this])`.

**Skip system-only steps** (e.g. "System notifies the team", "Status updates in background"). They have no screen, so no Reference Pattern block.

If the anchor world has no screen for a user-facing step, write `Main screen: no match in [anchor world] — treat as gap` rather than reaching into a different flow for the main screen.

## Validation Rules

- Context includes 10+ Q&A insights
- Problem identifies root cause, not symptom
- User Flow has 3-8 plain-English steps
- Each User Flow step is a single user action OR single system response
- If Reference Patterns present:
  - Anchor flow world named
  - Every "Step N" block matches a "Step N" in User Flow
  - Every Step block has a Main screen reference line (or explicit "no match / gap" note)
  - Main screen references come from the anchor world — no exceptions
  - Specific element bullets stay within the anchor world by default; cross-world borrows must include `(Borrowed from [App](URL) — [reason])`
  - Specific element bullets capped at ~5 per step — quality over volume
- Every URL is a clickable `[App](URL)`
- Recommendation addresses constraints from Context
- **Scope check**: NO frontend file paths, line numbers, LOC estimates, PR breakdowns, code snippets, Tailwind/CSS classes, hex colors, or i18n keys. Move them to "Follow-up Questions for PRD".

## Template

```markdown
# Explore: [TOPIC]

## Context Summary
Key insights from conversation:
- [Insight from Q1]
- [Insight from Q2]
- ...
- [Insight from Q10+]

Constraints (if any): [budget, timeline, compliance]
Competitors mentioned (if any): [list]

## Problem Statement
[One sentence — root cause, not symptom]

## User Flow
Happy path only. As many steps as the flow needs (3-8 typical).

1. **[What happens]** — short note if needed
2. **[What happens next]** — ...
3. **[...]** — ...

Compact form: [Start] → [Step 1] → [Step 2] → ... → [Done]

## Reference Patterns
Anchor flow world: [e.g. "incident.io escalation flow"] — sets the design language.
Each block below maps to a User Flow step. Skip system-only steps.

**Step 1 — [user-facing action]**
Main screen reference: [App](Mobbin URL) — from the anchor world
Specific elements to borrow:
- [What to borrow]: [why this exact treatment] ([App](URL))
- [What to borrow]: [why] ([App](URL))

**Step 2 — [user-facing action]**
Main screen reference: [App](URL)
Specific elements to borrow:
- [What to borrow]: [why] ([App](URL))

(Step 3 skipped — system-only, no screen)

**Step 4 — [user-facing action]**
Main screen reference: [App](URL)
Specific elements to borrow:
- [What to borrow]: [why] ([App](URL))
- [Button copy "X"]: [why clearer than alternatives] (Borrowed from [App](URL) — anchor world uses vaguer term)

Gaps: [steps where anchor world has no main-screen match]

## Recommendation
[Direction + why, addressing constraints. Names what to build first.]

## Follow-up Questions for PRD
- [Optional — anything implementation-level that came up]
```

## Notion Mapping

| Notion Field | Explore Field | Notes |
|--------------|---------------|-------|
| Name | Topic | title property |
| Type | `["Exploration"]` | multi_select, if exists |

Content goes in page body as markdown.

## Anytype Mapping

| Anytype Field | Explore Field | Notes |
|---------------|---------------|-------|
| name | Topic | object name |
| body | Full exploration content | markdown format |
| type_key | "page" | or custom type if available |
