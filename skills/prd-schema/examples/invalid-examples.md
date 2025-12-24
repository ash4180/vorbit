# Invalid PRD Examples

Common mistakes and how to fix them.

## Technical Details in Requirements

**Wrong:**
```json
{"id": "FR-001", "must": "Use JWT tokens for session management"}
```

**Why it's wrong:** Implementation detail. PRD defines WHAT, not HOW.

**Fixed:**
```json
{"id": "FR-001", "must": "System MUST maintain user sessions across page refreshes"}
```

---

## Vague Success Criteria

**Wrong:**
```json
{"success_criteria": ["Users should be happy with login"]}
```

**Why it's wrong:** Not measurable. How do you verify "happy"?

**Fixed:**
```json
{"success_criteria": ["90% of users complete login in under 10 seconds"]}
```

---

## Implementation in Problem Statement

**Wrong:**
```json
{"problem": "We need to implement OAuth2 for authentication"}
```

**Why it's wrong:** Prescribes solution, not problem.

**Fixed:**
```json
{"problem": "Users cannot access personalized features without accounts"}
```

---

## Jargon in Name

**Wrong:**
```json
{"name": "OAuth2 JWT Token Auth Implementation"}
```

**Why it's wrong:** Technical jargon. Business stakeholders can't understand.

**Fixed:**
```json
{"name": "User Login and Signup"}
```

---

## Description Too Long

**Wrong:**
```json
{"description": "This feature will allow users to create accounts using their email address and password, then log in to access personalized features across the platform including dashboards and settings"}
```

**Why it's wrong:** Over 100 characters. Too detailed.

**Fixed:**
```json
{"description": "Secure login/signup for web and mobile users"}
```

---

## Missing MUST Language

**Wrong:**
```json
{"id": "FR-001", "must": "The system should probably validate email addresses"}
```

**Why it's wrong:** Weak language. Unclear if required.

**Fixed:**
```json
{"id": "FR-001", "must": "System MUST validate email format before account creation"}
```

---

## UNCLEAR Markers Left

**Wrong:**
```json
{"problem": "Users need [UNCLEAR: what type of access?] to the platform"}
```

**Why it's wrong:** Unresolved questions. PRD not ready.

**Fixed:** Clarify with stakeholder first, then:
```json
{"problem": "Users need authenticated access to view their personal data"}
```
