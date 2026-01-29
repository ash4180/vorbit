# UX Question Matrix

Exhaustive question catalog organized by category. For each user story, systematically ask questions from each category using `AskUserQuestion`.

## How to Use This Matrix

1. For each user story, go through categories in order
2. Ask 2-4 questions per `AskUserQuestion` call (batch by category)
3. Follow up on any answer that reveals complexity
4. Document all answers as acceptance criteria

---

## 1. Entry Points & Prerequisites

**Goal:** Understand how users arrive and what they need first.

| Question | Why It Matters |
|----------|----------------|
| How does the user get to this feature? | Determines entry state variations |
| What prerequisites must be met? (Logged in, verified, subscription) | Identifies gating conditions |
| Can users deep-link directly? What if not authenticated? | Determines redirect/auth flow |
| Is there onboarding for first-time users? | Identifies first-run experience |

---

## 2. Happy Path Flow

**Goal:** Define the ideal user journey step by step.

| Question | Why It Matters |
|----------|----------------|
| Walk through the ideal flow: what does user do first, then next? | Establishes baseline flow |
| At each step, what action does user take? (Click, type, drag) | Defines interaction patterns |
| What confirmation does user see at the end? | Determines success state |
| After completion, where does user go next? | Determines exit transitions |

---

## 3. Validation & Input Errors

**Goal:** Cover all ways user input can fail.

| Question | Why It Matters |
|----------|----------------|
| For each input: what makes it valid/invalid? | Defines validation rules |
| Should validation happen on blur, change, or submit? | Determines timing |
| What exact error messages for each failure? | Defines error copy |
| Are errors shown inline or as summary? | Determines UI pattern |
| Character limits? Min/max lengths? | Defines boundaries |

---

## 4. System & Network Errors

**Goal:** Handle all technical failure scenarios.

| Question | Why It Matters |
|----------|----------------|
| What if API call fails? (500, timeout, offline) | Defines error recovery |
| Should system auto-retry? How many times? | Determines retry logic |
| What does user see during failure? Can they retry? | Defines error UI |
| What happens to unsaved data on network error? | Data preservation |

---

## 5. Permissions & Authorization

**Goal:** Handle all auth and permission scenarios.

| Question | Why It Matters |
|----------|----------------|
| What user roles can access this? | Defines access control |
| What if unauthorized user tries to access? | Determines redirect |
| What if session expires during use? | Determines re-auth flow |

---

## 6. Loading & Transition States

**Goal:** Define what users see during async operations.

| Question | Why It Matters |
|----------|----------------|
| What shows while data loads? (Skeleton, spinner, progress) | Defines loading UI |
| How long before showing timeout message? | User patience threshold |
| Can users cancel long-running operations? | Defines cancellation |

---

## 7. Empty & Edge Data States

**Goal:** Handle all data absence scenarios.

| Question | Why It Matters |
|----------|----------------|
| First-time user: what do they see with no data? | Defines zero state |
| Search returns nothing: what message? Suggestions? | No results state |
| Partial data: some fields missing? | Handles incomplete records |

---

## 8. Concurrent & Multi-User Scenarios

**Goal:** Handle simultaneous actions.

| Question | Why It Matters |
|----------|----------------|
| Can multiple users edit same thing? | Collaboration model |
| What if another user changes data while viewing? | Real-time updates |
| What if open in multiple tabs? | Tab coordination |

---

## 9. Time-Based Scenarios

**Goal:** Handle all temporal edge cases.

| Question | Why It Matters |
|----------|----------------|
| Timezones: whose timezone for display? | Timezone handling |
| Expiration: what expires and when? Warning before? | Deadline handling |

---

## 10. Device & Platform

**Goal:** Cover cross-platform experience.

| Question | Why It Matters |
|----------|----------------|
| Mobile vs desktop: same features or reduced? | Responsive scope |
| Touch vs mouse: gesture-specific interactions? | Input method |
| Small screens: what gets hidden or collapsed? | Progressive disclosure |

---

## 11. Accessibility

**Goal:** Ensure inclusive design.

| Question | Why It Matters |
|----------|----------------|
| Keyboard navigation: can everything work without mouse? | Keyboard accessibility |
| Screen reader: what's announced at each step? | ARIA labels |
| Focus management: where does focus go after actions? | Focus control |

---

## 12. Undo & Recovery

**Goal:** Let users recover from mistakes.

| Question | Why It Matters |
|----------|----------------|
| Can users undo the action? For how long? | Undo window |
| Draft saving: auto-save or manual? How often? | Data preservation |
| Navigation away: warn about unsaved changes? | Exit warning |

---

## 13. Notifications & Feedback

**Goal:** Keep users informed.

| Question | Why It Matters |
|----------|----------------|
| Success feedback: toast, banner, inline, redirect? | Success pattern |
| Error feedback: same question | Error pattern |
| Long-running: notify when done? How? | Async notification |

---

## Question Priority by Feature Type

### Form/Input Features
Focus on: Validation, Errors, Accessibility, Undo

### Dashboard/Display Features
Focus on: Loading, Empty States, Time-based, Device

### Collaborative Features
Focus on: Concurrent, Permissions, Real-time

### Transaction Features
Focus on: Network Errors, Undo, Notifications
