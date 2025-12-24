# Invalid Flow Examples

Common mistakes and how to fix them.

## Technical Labels

**Wrong:**
```mermaid
A[POST /api/auth/login]
```

**Why it's wrong:** User doesn't see API calls. Flow should show user actions.

**Fixed:**
```mermaid
A[Click Login button]
```

---

## Decision Without Labels

**Wrong:**
```mermaid
B{Valid?}
B --> C
B --> D
```

**Why it's wrong:** No indication which path is which.

**Fixed:**
```mermaid
B{Valid?}
B -->|Yes| C
B -->|No| D
```

---

## No Error Handling

**Wrong:**
```mermaid
A[Submit form] --> B[Success page]
```

**Why it's wrong:** What happens when submission fails?

**Fixed:**
```mermaid
A[Submit form] --> B{Success?}
B -->|Yes| C[Success page]
B -->|No| D[Show error]
D --> A
```

---

## No Entry Point

**Wrong:**
```mermaid
A[First action] --> B[Second action]
```

**Why it's wrong:** How does user get here?

**Fixed:**
```mermaid
START([Open page]) --> A[First action]
A --> B[Second action]
```

---

## No Exit Point

**Wrong:**
```mermaid
A --> B --> C[Dashboard]
```

**Why it's wrong:** Flow doesn't indicate completion.

**Fixed:**
```mermaid
A --> B --> C[Dashboard] --> END([Flow complete])
```

---

## Too Many Steps

**Wrong:** A diagram with 20+ nodes in one flow.

**Why it's wrong:** Unreadable, impossible to maintain.

**Fixed:** Split into sub-flows:
- Main flow (5-8 steps)
- Sub-flow 1: Error handling (4-5 steps)
- Sub-flow 2: Edge case (3-4 steps)

---

## Missing Recovery Path

**Wrong:**
```mermaid
A --> ERR[Error occurred]
```

**Why it's wrong:** User is stuck with no way forward.

**Fixed:**
```mermaid
A --> ERR[Error occurred]
ERR -->|Retry| A
ERR -->|Exit| END([Leave])
```

---

## Redundant Steps

**Wrong:**
```mermaid
A[Click Login] --> B[Button pressed] --> C[Form submitting] --> D[Loading...] --> E[Response received] --> F[Dashboard]
```

**Why it's wrong:** Multiple steps for what user experiences as one action. User clicks, sees loading, sees result.

**Fixed:**
```mermaid
A[Click Login] --> B{Success?}
B -->|Yes| C[Dashboard]
B -->|No| D[Show error]
```

**Rule:** One screen or one user action = one step. Don't model internal states.
