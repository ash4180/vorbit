# EPIC: [EPIC_NAME]

**Created**: [DATE] | **Source PRD**: [PRD_FILE]

## Technical Context
**Language/Framework**: [Determined from codebase analysis]
**Dependencies**: [Existing systems to integrate with]
**Architecture**: [Current codebase patterns to follow]
**Testing Strategy**: [Existing test patterns to extend]

## Epics (Linear Issues)

One User Story = One Epic. Issue titles must be branch-friendly.

### Epic 1: add-user-registration
**Maps to**: US-001
**Description**: As a new user, I want to create an account, so that I can access personalized features
**Acceptance**: Given new user, When submitting valid email/password, Then account is created

Sub-issues (if needed):
- `implement-form-validation` - Add email/password validation
- `add-email-verification` - Send verification email on signup

### Epic 2: implement-password-reset
**Maps to**: US-002
**Description**: As a user, I want to reset my password, so that I can recover my account
**Acceptance**: Given existing user, When requesting reset, Then email is sent

Sub-issues (if needed):
- `setup-email-service` - Configure password reset emails

