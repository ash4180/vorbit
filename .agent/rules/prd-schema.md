# PRD Schema

Product Requirements Document rules for Notion integration.

## Required Sections

* **Name**: 3-8 words, no technical jargon
* **Description**: Max 100 characters
* **Problem**: Max 3 sentences, describes user pain not technical gap
* **Users**: Who has the problem
* **User Stories**: Format "As a [user], I want [goal], so that [benefit]" with acceptance criteria
* **User Flow**: Placeholder `[To be added via journey workflow]` until flow is added
* **Success Criteria**: Must contain measurable numbers (percentages, times, counts)
* **Constraints**: Budget, timeline, compliance (optional)
* **Out of Scope**: What we're NOT building (optional)

## Validation Rules

* Name must be 3-8 words with no technical jargon
* Problem describes user pain, not technical solution
* User stories use format: "As a [user], I want [goal], so that [benefit]"
* Each user story has acceptance criteria
* Success criteria must include numbers (percentages, times, counts)
* No placeholders like `[UNCLEAR]`, `[TBD]`, or empty sections (except User Flow)

## User Story Format

```
US-001: As a [user type], I want [goal], so that [benefit]
  Acceptance:
  - [Specific testable criterion]
  - [Another criterion]
```

* One goal per story
* Each story has acceptance criteria
* Stories map to issues in task tracker

## Success Criteria Format

* Include numbers (e.g., "95% of signups complete successfully")
* Must be verifiable (yes/no answer)
* Focus on business outcomes, not tech metrics

## Common Mistakes to Avoid

* "We need OAuth2 for authentication" → "Users cannot access personalized features without accounts" (Problem describes user pain)
* "Users should be happy with login" → "90% of users complete login in under 10 seconds" (Success criteria must have numbers)
* "OAuth2 JWT Token Auth Implementation" → "User Login and Signup" (Name avoids jargon)
