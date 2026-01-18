# Sample PRD: User Authentication

*This is an example output from the PRD skill.*

---

## Problem

Users cannot access personalized content without creating an account. Currently there's no way for users to securely log in, and they lose their preferences when switching devices.

## Users

- End users who want to save their preferences
- Returning users who need to access their data across devices

## User Stories

### US-001: User Login

As a registered user, I want to log in to my account, so that I can access my personalized content.

**UX Expectation:**
User enters email and password, clicks login, sees brief loading state, then lands on dashboard. Errors are shown inline below each field with clear recovery options. The experience should feel fast and secure.

**User Flow:**
[FigJam: https://www.figma.com/board/abc123/Login-Flow]

**Acceptance Criteria:**

Happy Path:
- [ ] User enters email and password in form fields
- [ ] User clicks "Sign In" button
- [ ] Show "Signing in..." with spinner during API call
- [ ] On success, redirect to dashboard
- [ ] Show welcome message with user's name

Validation:
- [ ] When email is empty, show "Email is required" below field
- [ ] When email format is invalid, show "Please enter a valid email"
- [ ] When password is empty, show "Password is required"
- [ ] Validation occurs on submit (not on blur)
- [ ] Errors clear when user starts typing in the errored field

Errors:
- [ ] When password is wrong, show "Incorrect password. Forgot password?" with link
- [ ] When email not found, show "No account found. Sign up?" with link
- [ ] When API times out, show "Taking longer than usual. Please retry." with retry button
- [ ] When server error (500), show "Something went wrong. Please try again."
- [ ] Preserve email field value on error (don't clear form)

States:
- [ ] Loading: Disable button, show spinner inside button, text "Signing in..."
- [ ] Empty: N/A (login page always shows form)

Permissions:
- [ ] When account is disabled, show "Account suspended. Contact support." with support link
- [ ] When email not verified, show "Please verify your email" with resend verification link
- [ ] After 5 failed attempts, lock for 15 minutes with countdown timer

Accessibility:
- [ ] Password field has show/hide toggle with aria-label
- [ ] Form submits on Enter key
- [ ] Tab order: email → password → remember me → sign in → forgot password
- [ ] Error messages announced by screen reader (role="alert")
- [ ] Touch targets minimum 44px on mobile

Edge Cases:
- [ ] When already logged in, redirect to dashboard
- [ ] When session exists in another tab, allow new login
- [ ] Deep link to protected page → login → redirect back to original page

---

### US-002: User Registration

As a new user, I want to create an account, so that I can save my preferences.

**UX Expectation:**
User fills out simple form with email and password, submits, receives verification email, clicks link, and lands on dashboard. Minimal friction - only ask for what's necessary.

**User Flow:**
[FigJam: https://www.figma.com/board/def456/Registration-Flow]

**Acceptance Criteria:**

Happy Path:
- [ ] User enters email address
- [ ] User enters password (with strength indicator)
- [ ] User confirms password
- [ ] User clicks "Create Account"
- [ ] Show "Creating account..." during API call
- [ ] On success, show "Check your email for verification link"
- [ ] After email verification, redirect to dashboard

Validation:
- [ ] When email is empty, show "Email is required"
- [ ] When email format invalid, show "Please enter a valid email"
- [ ] When email already registered, show "Email already in use. Sign in instead?" with link
- [ ] When password too short, show "Password must be at least 8 characters"
- [ ] When password missing requirements, show specific requirement (uppercase, number, etc.)
- [ ] When passwords don't match, show "Passwords do not match"
- [ ] Show password strength indicator (weak/medium/strong)

Errors:
- [ ] When API fails, show "Something went wrong. Please try again." with retry
- [ ] When rate limited, show "Too many attempts. Please wait X minutes."

States:
- [ ] Loading: Disable button, show spinner, text "Creating account..."
- [ ] Empty: N/A (registration always shows form)

Permissions:
- [ ] When already logged in, redirect to dashboard with message

Accessibility:
- [ ] Password requirements listed visibly for screen readers
- [ ] Strength indicator has text alternative (not just color)
- [ ] All fields properly labeled

Edge Cases:
- [ ] Verification link expires after 24 hours, show "Link expired. Request new one?"
- [ ] Resend verification available after 60 seconds

---

### US-003: Password Reset

As a user who forgot my password, I want to reset it, so that I can regain access to my account.

**UX Expectation:**
User clicks "Forgot password", enters email, receives reset link, clicks link, enters new password, and can log in. Simple 3-step process with clear feedback at each stage.

**User Flow:**
[FigJam: https://www.figma.com/board/ghi789/Password-Reset-Flow]

**Acceptance Criteria:**

Happy Path:
- [ ] User clicks "Forgot password?" link on login page
- [ ] User enters email address
- [ ] User clicks "Send Reset Link"
- [ ] Show "If an account exists, you'll receive an email"
- [ ] User receives email with reset link
- [ ] User clicks link, lands on "Create New Password" page
- [ ] User enters new password twice
- [ ] On success, show "Password updated" and redirect to login

Validation:
- [ ] When email empty, show "Email is required"
- [ ] When new password too weak, show requirements
- [ ] When passwords don't match, show "Passwords do not match"

Errors:
- [ ] Never reveal if email exists (security)
- [ ] When reset link expired (24h), show "Link expired. Request new one?"
- [ ] When reset link already used, show "Link already used. Request new one?"

States:
- [ ] Loading: Show spinner while sending email
- [ ] Success: Show generic message (don't confirm email exists)

Accessibility:
- [ ] Clear instructions at each step
- [ ] Email field auto-focused on page load

Edge Cases:
- [ ] Multiple reset requests - only latest link works
- [ ] User remembers password - provide "Back to login" link

---

## Constraints

- Must use existing OAuth2 infrastructure
- Must comply with GDPR (EU users)
- Session timeout: 30 days with "remember me", 24 hours without
- Password requirements: 8+ chars, 1 uppercase, 1 number

## Out of Scope

- Social login (Google, GitHub) - Phase 2
- Two-factor authentication - Phase 2
- Single sign-on (SSO) - Enterprise tier only
- Biometric authentication - Mobile app only

## Success Criteria

- 95% of login attempts complete in under 3 seconds
- Registration abandonment rate below 20%
- Password reset completion rate above 80%
- Zero security incidents related to authentication
- Support tickets for login issues below 5 per 1000 users
