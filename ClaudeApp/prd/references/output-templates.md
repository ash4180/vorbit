# PRD Output Templates

Copy-paste templates for generating PRD outputs.

---

## PRD Template

```markdown
# [Feature Name]

## Problem
[Max 3 sentences - user pain, not technical gap]

## Users
[Who has this problem]

## User Stories

[Insert Enhanced User Story Template for each story]

## Constraints
- [Budget, timeline, compliance, tech stack]

## Out of Scope
- [What we're NOT building]

## Success Criteria
- [Measurable metric with number]
- [Another measurable metric]
```

---

## Enhanced User Story Template

```markdown
### US-XXX: [User Story Title]

As a [user type], I want [goal], so that [benefit].

**UX Expectation:**
[User's description of the ideal experience - their exact words from Q&A]

**Acceptance Criteria:**

Happy Path:
- [ ] [User's answer: first step]
- [ ] [User's answer: second step]
- [ ] [User's answer: success confirmation]

Validation:
- [ ] When [field] is empty, show "[user's error message]"
- [ ] When [field] format is invalid, show "[user's error message]"
- [ ] Validation occurs [user's answer: on blur/submit]

Errors:
- [ ] When API fails, [user's answer]
- [ ] When offline, [user's answer]
- [ ] When timeout, [user's answer]

States:
- [ ] Loading: [user's answer]
- [ ] Empty: [user's answer]

Permissions:
- [ ] When unauthorized, [user's answer]
- [ ] When session expires, [user's answer]

Accessibility:
- [ ] [user's answer: keyboard navigation]
- [ ] [user's answer: screen reader]
- [ ] [user's answer: mobile]

Edge Cases:
- [ ] [user's answer: multi-tab behavior]
- [ ] [user's answer: concurrent editing]
```

---

## Report Template

```markdown
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

## Acceptance Criteria Categories

When compiling user story, group ACs by category:

| Category | Examples |
|----------|----------|
| **Happy Path** | Success flow steps, confirmation message |
| **Validation** | Empty field, invalid format, too long/short |
| **Errors** | API failure, offline, timeout, server error |
| **States** | Loading, empty, partial, stale data |
| **Permissions** | Unauthorized, session expired, role-specific |
| **Accessibility** | Keyboard nav, screen reader, touch targets |
| **Edge Cases** | Multi-tab, concurrent edit, deep links |
