# UX Question Matrix

Exhaustive question catalog organized by category. For each user story, systematically ask questions from each category using `AskUserQuestion`.

## How to Use This Matrix

1. For each user story, go through categories in order
2. Ask 2-4 questions per `AskUserQuestion` call (batch by category)
3. Follow up on any answer that reveals complexity
4. Document all answers for the edge case matrix

---

## 1. Entry Points & Prerequisites

**Goal:** Understand how users arrive and what they need first.

| Question | Why It Matters |
|----------|----------------|
| How does the user get to this feature? (Direct link, navigation, notification, etc.) | Determines entry state variations |
| What prerequisites must be met? (Logged in, verified email, subscription, etc.) | Identifies gating conditions |
| Can users deep-link directly to this? What if they're not authenticated? | Determines redirect/auth flow needs |
| Is there an onboarding flow for first-time users? | Identifies first-run experience |
| Can users arrive mid-flow from another feature? | Determines state restoration needs |

**Follow-up triggers:**
- Multiple entry points → ask about each one's expected state
- Prerequisites → ask what happens when not met
- Deep linking → ask about query parameter handling

---

## 2. Happy Path Flow

**Goal:** Define the ideal user journey step by step.

| Question | Why It Matters |
|----------|----------------|
| Walk me through the ideal flow: what does the user do first, then next? | Establishes baseline flow |
| At each step, what action does the user take? (Click, type, drag, etc.) | Defines interaction patterns |
| What confirmation does the user see at the end? | Determines success state |
| How long should each step take? Any time limits? | Identifies timeout scenarios |
| After completion, where does the user go next? | Determines exit transitions |

**Follow-up triggers:**
- Multiple steps → ask about saving progress between steps
- Time limits → ask about expiration behavior
- Confirmation → ask about undo capability

---

## 3. Validation & Input Errors

**Goal:** Cover all ways user input can fail.

| Question | Why It Matters |
|----------|----------------|
| For each input field: what makes it valid/invalid? | Defines validation rules |
| Should validation happen on blur, on change, or on submit? | Determines timing |
| What exact error messages should show for each validation failure? | Defines error copy |
| Are errors shown inline (per-field) or as a summary (top of form)? | Determines UI pattern |
| Can users submit with warnings vs. hard blockers? | Identifies soft vs hard validation |
| What about character limits? Minimum/maximum lengths? | Defines boundary conditions |
| Special character handling? (Emojis, Unicode, HTML, SQL injection) | Security and edge cases |

**Follow-up triggers:**
- Multiple fields → ask about field interdependencies
- Complex validation → ask about real-time feedback
- Character limits → ask about counter display

---

## 4. System & Network Errors

**Goal:** Handle all technical failure scenarios.

| Question | Why It Matters |
|----------|----------------|
| What if the API call fails? (500 error, timeout, network offline) | Defines error recovery |
| Should the system auto-retry? How many times? | Determines retry logic |
| What does the user see during a failure? Can they retry manually? | Defines error UI |
| If offline, what functionality remains? | Determines offline capability |
| What happens to unsaved data when a network error occurs? | Data preservation |
| Rate limiting: what if user hits API limits? | Defines throttle handling |
| Partial failure: what if some parts succeed and others fail? | Determines rollback/partial state |

**Follow-up triggers:**
- Auto-retry → ask about exponential backoff
- Offline mode → ask about sync when back online
- Partial failure → ask about transaction atomicity

---

## 5. Permissions & Authorization

**Goal:** Handle all auth and permission scenarios.

| Question | Why It Matters |
|----------|----------------|
| What user roles can access this feature? | Defines access control |
| What happens if an unauthorized user tries to access? | Determines redirect behavior |
| Can permissions change mid-session? (Role revoked while using) | Handles real-time permission changes |
| What if the session expires during use? | Determines re-auth flow |
| Multi-tenant: can users see other organization's data? | Security boundary |
| Feature flags: is this behind a feature flag? Who has access? | Determines rollout scope |

**Follow-up triggers:**
- Multiple roles → ask about role-specific UI variations
- Session expiry → ask about data preservation
- Feature flags → ask about graceful degradation

---

## 6. Loading & Transition States

**Goal:** Define what users see during async operations.

| Question | Why It Matters |
|----------|----------------|
| What shows while data is loading? (Skeleton, spinner, progress bar) | Defines loading UI |
| How long before showing a timeout message? | User patience threshold |
| Can users cancel/abort a long-running operation? | Defines cancellation |
| What about partial loading? (Header loads, then content) | Progressive loading |
| Page transitions: fade, slide, instant? | Defines motion design |
| Optimistic updates: show success before server confirms? | Determines UX responsiveness |

**Follow-up triggers:**
- Long operations → ask about background processing option
- Partial loading → ask about priority order
- Optimistic updates → ask about rollback on failure

---

## 7. Empty & Edge Data States

**Goal:** Handle all data absence scenarios.

| Question | Why It Matters |
|----------|----------------|
| First-time user: what do they see when there's no data yet? | Defines zero state |
| Search/filter returns nothing: what message? Any suggestions? | Defines no results state |
| Data was deleted: what replaces it? | Handles removed content |
| List pagination: what if there's only 1 item? Or 10,000? | Boundary conditions |
| Partial data: some fields missing from API response? | Handles incomplete records |
| Stale data: how old is too old? Show warning? | Data freshness |

**Follow-up triggers:**
- Zero state → ask about onboarding/CTA in empty state
- Large lists → ask about infinite scroll vs pagination
- Stale data → ask about auto-refresh behavior

---

## 8. Concurrent & Multi-User Scenarios

**Goal:** Handle simultaneous actions.

| Question | Why It Matters |
|----------|----------------|
| Can multiple users edit the same thing simultaneously? | Determines collaboration model |
| What if another user changes data while I'm viewing? | Real-time updates |
| What if I have this open in multiple tabs? | Tab coordination |
| What if I'm editing and someone else deletes the item? | Conflict resolution |
| Last-write-wins or merge conflicts? | Determines conflict strategy |
| Should users see who else is viewing/editing? | Presence indicators |

**Follow-up triggers:**
- Simultaneous editing → ask about conflict resolution UI
- Multiple tabs → ask about cross-tab communication
- Presence → ask about privacy considerations

---

## 9. Time-Based Scenarios

**Goal:** Handle all temporal edge cases.

| Question | Why It Matters |
|----------|----------------|
| Timezones: whose timezone for display? User's or data's? | Timezone handling |
| Scheduling: can users schedule for the past? | Date validation |
| Expiration: what expires and when? What warning before? | Deadline handling |
| Date edge cases: leap years, daylight saving, end of month? | Calendar edge cases |
| Time-limited actions: what if they start but don't finish in time? | Timeout mid-flow |
| Historical data: how far back can users go? | Data retention |

**Follow-up triggers:**
- Timezone → ask about display format preferences
- Expiration → ask about grace periods
- Historical → ask about archival vs deletion

---

## 10. Device & Platform

**Goal:** Cover cross-platform experience.

| Question | Why It Matters |
|----------|----------------|
| Mobile vs desktop: same feature set or reduced? | Responsive scope |
| Touch vs mouse: any gesture-specific interactions? | Input method |
| Portrait vs landscape: layout changes? | Orientation handling |
| Small screens: what gets hidden or collapsed? | Progressive disclosure |
| Offline mobile: different from offline desktop? | Platform-specific offline |
| Native app vs web: any differences in behavior? | Platform parity |

**Follow-up triggers:**
- Reduced mobile → ask about feature parity priority
- Gestures → ask about discoverability
- Small screens → ask about critical vs nice-to-have

---

## 11. Accessibility

**Goal:** Ensure inclusive design.

| Question | Why It Matters |
|----------|----------------|
| Screen reader: what's announced at each step? | ARIA labels |
| Keyboard navigation: can everything be done without mouse? | Keyboard accessibility |
| Focus management: where does focus go after actions? | Focus control |
| Color contrast: sufficient for low vision users? | WCAG compliance |
| Motion: respect reduced-motion preference? | Motion sensitivity |
| Error announcements: are errors announced to screen readers? | Error accessibility |

**Follow-up triggers:**
- Complex interactions → ask about alternative input methods
- Animations → ask about pause/stop capability
- Dynamic content → ask about live region announcements

---

## 12. Undo & Recovery

**Goal:** Let users recover from mistakes.

| Question | Why It Matters |
|----------|----------------|
| Can users undo the action? For how long? | Undo window |
| Soft delete vs hard delete? | Deletion permanence |
| Draft saving: auto-save or manual? How often? | Data preservation |
| Can users restore previous versions? | Version history |
| Accidental navigation away: warn about unsaved changes? | Exit warning |
| Bulk actions: undo all or individual? | Batch undo |

**Follow-up triggers:**
- Undo → ask about undo across sessions
- Drafts → ask about draft visibility to others
- Versions → ask about diff/comparison view

---

## 13. Notifications & Feedback

**Goal:** Keep users informed.

| Question | Why It Matters |
|----------|----------------|
| Success feedback: toast, banner, inline, redirect? | Success pattern |
| Error feedback: same question | Error pattern |
| Long-running: notify when done? How? (Email, push, in-app) | Async notification |
| Real-time updates: how are users notified of changes? | Live updates |
| Notification preferences: can users customize? | User control |

**Follow-up triggers:**
- Multiple channels → ask about notification deduplication
- Real-time → ask about notification batching
- Preferences → ask about default settings

---

## 14. Data Export & Integration

**Goal:** Handle data portability.

| Question | Why It Matters |
|----------|----------------|
| Can users export this data? What formats? | Data portability |
| Can users import data? What validation? | Data import |
| API/webhook integrations: what events trigger them? | Integration points |
| Copy to clipboard: what format? | Quick sharing |
| Print view: different from screen view? | Print optimization |

**Follow-up triggers:**
- Export → ask about large data set handling
- Import → ask about duplicate detection
- Integrations → ask about failure handling

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

### Admin/Settings Features
Focus on: Permissions, Time-based, Audit
