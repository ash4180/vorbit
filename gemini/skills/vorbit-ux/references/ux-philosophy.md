# UX Philosophy & Principles

Core principles that guide UX decisions during analysis. Reference these when making trade-offs or prioritizing edge cases.

---

## Core Philosophy

### 1. Users Are Human

**People make mistakes.** Design assumes users will:
- Click the wrong button
- Enter invalid data
- Get distracted mid-task
- Not read instructions
- Forget what they were doing

**Implication:** Every flow needs error recovery, confirmation for destructive actions, and clear feedback.

### 2. Clarity Over Cleverness

**If users have to think about how to use it, it's too complex.**

- Labels should describe what happens, not be cute
- Actions should have predictable outcomes
- Visual hierarchy should guide attention
- Don't hide essential features behind gestures

**Implication:** When in doubt, be explicit. A "boring" but clear design beats a "clever" confusing one.

### 3. Respect User Time

**Every extra step costs user attention and patience.**

- Minimize clicks to accomplish tasks
- Don't ask for information you already have
- Don't require re-entry after errors
- Load fast, fail fast, recover fast

**Implication:** If there's a way to do it in fewer steps, do it that way.

### 4. Fail Gracefully

**Errors are inevitable. Catastrophic failures are not.**

- Never lose user data
- Always provide a way forward (retry, alternative, back)
- Explain what went wrong in human terms
- Don't blame the user for system problems

**Implication:** Error states deserve as much design attention as success states.

### 5. Inclusive by Default

**Accessibility is not an afterthought.**

- Design for keyboard navigation from the start
- Color is never the only indicator
- Touch targets are 44px minimum
- Motion respects user preferences

**Implication:** Accessible design is better design for everyone.

---

## Decision Frameworks

### When to Block vs. Warn

| Block (Prevent Action) | Warn (Allow with Confirmation) |
|------------------------|-------------------------------|
| Data loss is permanent and unrecoverable | Action is reversible or recoverable |
| Security violation (unauthorized access) | Unusual but valid action |
| Invalid data that would corrupt system | Data that might not be what user meant |
| Action violates business rules | Action is outside normal usage |

**Example:**
- Block: Deleting account without "type DELETE to confirm"
- Warn: Sending email to 1000+ recipients

### When to Auto-Save vs. Manual Save

| Auto-Save | Manual Save |
|-----------|-------------|
| Document editing (text, code) | Form submissions with consequences |
| User preferences | Financial transactions |
| Draft content | Published content |
| Settings changes | Batch operations |

**Principle:** Auto-save for exploration, manual save for commitment.

### When to Show vs. Hide Complexity

| Show | Hide |
|------|------|
| Actions user will need | Rarely-used options |
| Information affecting decisions | Technical details |
| Errors and warnings | Loading internals |
| Current state | Implementation details |

**Principle:** Progressive disclosure - show the minimum needed, reveal more on demand.

### When to Ask Permission vs. Forgiveness

| Ask First | Act First (Undo Available) |
|-----------|---------------------------|
| Irreversible actions | Quick, reversible actions |
| Actions affecting others | Personal preference changes |
| High-impact operations | Navigation and exploration |
| First-time critical actions | Repeated familiar actions |

**Example:**
- Ask first: "Delete all 47 items?"
- Act first: Archive message (with undo toast)

---

## State Design Principles

### Loading States

**Perception matters more than actual speed.**

| Technique | When to Use |
|-----------|-------------|
| Skeleton screens | Content with known structure |
| Progress bar | Operations with measurable progress |
| Spinner | Short operations (<3 seconds) |
| Background processing | Long operations (>30 seconds) |

**Rule:** Show skeletons for content, spinners for actions, progress for uploads.

### Empty States

**Empty is an opportunity, not an error.**

| Empty Type | Design Goal |
|------------|-------------|
| First-run empty | Teach and motivate |
| Search/filter empty | Help refine or reset |
| Deleted-all empty | Confirm and offer creation |
| Permission empty | Explain and guide |

**Rule:** Every empty state should have a clear next action.

### Error States

**Errors should educate, not frustrate.**

| Component | Purpose |
|-----------|---------|
| What happened | Clear description of the problem |
| Why it happened | Context if helpful (not blame) |
| How to fix | Specific actionable step |
| Alternative path | What to do if fix doesn't work |

**Rule:** Error messages should be written by humans for humans.

---

## Interaction Principles

### Feedback Timing

| Timing | Use For |
|--------|---------|
| Immediate (0-100ms) | Input acknowledgment, hover states |
| Fast (100-300ms) | Transitions, micro-interactions |
| Normal (300-1000ms) | Async operations, API calls |
| Slow (>1000ms) | Show loading indicator |

**Rule:** Under 100ms feels instant. Over 1 second needs feedback.

### Touch vs. Cursor

| Touch Consideration | Mouse Consideration |
|--------------------|---------------------|
| 44px min tap targets | Hover states for preview |
| No hover states available | Fine-grained click targets OK |
| Swipe for common actions | Right-click for context menu |
| Hold for secondary actions | Double-click for alternate |

**Rule:** Touch-first, then enhance for cursor. Not the other way around.

### Form Design

| Principle | Implementation |
|-----------|----------------|
| One primary action | Single prominent submit button |
| Label above input | Not placeholder-only labels |
| Inline validation | Validate on blur, not every keystroke |
| Error near field | Don't only show errors at top |
| Smart defaults | Pre-fill what you can |
| Remember choices | Don't ask the same thing twice |

**Rule:** Forms are conversations, not interrogations.

---

## Cognitive Load Principles

### Miller's Law
**People can hold 7±2 items in working memory.**

- Navigation: 5-7 top-level items max
- Options: Group beyond 7 items
- Steps: Show progress for 4+ steps

### Hick's Law
**Decision time increases with number of choices.**

- Primary action: 1 clear option
- Secondary actions: 2-3 max visible
- More options: Hidden in menu

### Fitts's Law
**Time to target depends on distance and size.**

- Important buttons: Larger
- Destructive buttons: Smaller or separated
- Common actions: Easily reachable positions
- Mobile: Bottom of screen > top

---

## Consistency Principles

### Internal Consistency
**Same action, same result, everywhere.**

- If "Cancel" goes back in one form, it goes back everywhere
- If blue buttons submit, all blue buttons submit
- If swipe left deletes in one list, it deletes in all lists

### External Consistency
**Follow platform conventions.**

- iOS: Back on top left, bottom tab bar
- Android: Back in system nav, floating action button
- Web: Logo links home, underlined text is clickable
- Desktop: Ctrl/Cmd+S saves, Esc cancels

### Linguistic Consistency
**Same concept, same word.**

- Don't switch between "Cancel," "Close," "Dismiss"
- Don't switch between "Remove," "Delete," "Trash"
- Pick terms and use them consistently

---

## Priority Framework for Edge Cases

When resources are limited, prioritize edge cases by:

### Priority 1: Safety & Data
- Prevents data loss
- Prevents security issues
- Affects payment/financial

### Priority 2: Core Flow Blockers
- Breaks primary user journey
- Affects >10% of users
- Causes support tickets

### Priority 3: Usability Issues
- Creates confusion
- Increases task time
- Degrades experience

### Priority 4: Polish
- Visual inconsistencies
- Rare scenarios
- Nice-to-have improvements

---

## Red Flags During Analysis

Watch for these patterns that indicate UX problems:

| Red Flag | What It Means |
|----------|---------------|
| "Users should know..." | You're assuming knowledge they don't have |
| "They can just..." | You're adding hidden steps |
| "It's obvious that..." | It probably isn't |
| "Edge case, won't happen" | It will happen at scale |
| "We can add that later" | Tech debt for UX |
| "The backend requires..." | Exposing implementation to users |
| "Users will figure it out" | They won't, they'll leave |

---

## Questions to Always Ask

For every feature, ensure answers to:

1. **What does success look like?** (Clear completion state)
2. **What can go wrong?** (Error scenarios covered)
3. **How do users recover?** (Path forward from errors)
4. **What if there's no data?** (Empty states designed)
5. **How long does it take?** (Loading states needed)
6. **Can users undo?** (Recovery from mistakes)
7. **Does it work on mobile?** (Responsive design)
8. **Is it accessible?** (Keyboard, screen reader)
9. **What's the first-time experience?** (Onboarding)
10. **What happens at scale?** (Performance edge cases)
