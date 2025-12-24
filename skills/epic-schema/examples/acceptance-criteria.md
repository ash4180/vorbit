# Acceptance Criteria Examples

Good vs bad acceptance criteria with fixes.

## Vague Criteria

**Wrong:**
```
- User can log in
- Login should work
- Handle errors appropriately
```

**Why it's wrong:** No specific conditions. Can't verify "appropriately" means.

**Fixed:**
```
1. Given I have an account with email "test@example.com"
   When I enter correct password
   Then I am redirected to /dashboard

2. Given I enter wrong password
   When I submit login form
   Then I see "Invalid email or password" message
```

---

## Missing Edge Cases

**Wrong:**
```
1. Given valid input
   When form submitted
   Then user created
```

**Why it's wrong:** What about invalid input? Duplicates?

**Fixed:**
```
1. Given valid email and password (8+ chars)
   When form submitted
   Then user created, 201 response

2. Given email already exists
   When form submitted
   Then 409 conflict, "Email already registered"

3. Given password under 8 characters
   When form submitted
   Then 400 error, password validation message
```

---

## Implementation Details

**Wrong:**
```
1. Given POST /api/users called
   When JSON body has email and password
   Then INSERT into users table
```

**Why it's wrong:** Tests implementation, not behavior. Brittle.

**Fixed:**
```
1. Given I am on signup page
   When I enter valid email and password
   Then my account is created and I can log in
```

---

## No Testable Outcome

**Wrong:**
```
1. Given user clicks button
   When action happens
   Then system processes request
```

**Why it's wrong:** "Processes request" isn't verifiable.

**Fixed:**
```
1. Given user clicks "Submit" button
   When form is valid
   Then success message appears
   And user redirected to dashboard within 2 seconds
```

---

## Good Criteria Checklist

Each criterion should answer:
- [ ] **Given**: What's the starting state?
- [ ] **When**: What action triggers the behavior?
- [ ] **Then**: What observable outcome happens?

And be:
- [ ] **Specific**: Exact values, not "appropriate" or "correctly"
- [ ] **Testable**: Can write a test that passes/fails
- [ ] **User-focused**: What the user sees, not internal state
- [ ] **Independent**: Each criterion stands alone

---

## Template

```
**Given** [precondition - the starting state]
**When** [trigger - the action taken]
**Then** [outcome - observable result]
**And** [additional outcome if needed]
```

## Multiple Conditions

```
**Given** I am logged in
**And** I have items in cart
**When** I click checkout
**Then** I see payment form
**And** cart total is displayed
```
