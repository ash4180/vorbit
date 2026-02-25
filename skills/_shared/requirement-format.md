# Requirement Format Reference

Shared format for acceptance criteria across PRD and Epic skills.
Adapted from [OpenSpec](https://github.com/Fission-AI/OpenSpec) — scenario-based specs with RFC 2119 requirement strength.

## AC Structure

```markdown
#### AC-{n}: {Short descriptive name}
{Requirement statement — use MUST or SHOULD for strength}

**Scenario: {scenario name}**
- GIVEN {precondition} _(optional — omit when obvious)_
- WHEN {trigger or user action}
- THEN {observable outcome}
- AND {additional outcome} _(repeatable)_
```

### Structural rules (agent parsing)

| Marker | Meaning | Required |
|--------|---------|----------|
| `#### AC-{n}:` | AC boundary — starts a new acceptance criterion | Yes |
| First line after header | Requirement statement with MUST or SHOULD | Yes |
| `**Scenario: ...**` | Named scenario block | At least one, unless constraint-only |
| `GIVEN` | Precondition / test setup | Optional |
| `WHEN` | Trigger / user action | Required per scenario |
| `THEN` | Primary observable outcome | Required per scenario |
| `AND` | Additional assertion | Optional, repeatable |

### Requirement strength

| Keyword | Meaning | Agent reads as |
|---------|---------|----------------|
| **MUST** | Required — failure is a bug | Implement + blocking test |
| **SHOULD** | Expected — skip needs explicit justification | Implement + test, can deprioritize |

If something is neither MUST nor SHOULD, it doesn't belong in the AC list.

## AC Types

### Behavioral (has scenarios)

Standard user-facing or system behavior. One or more scenarios demonstrate how it works.

```markdown
#### AC-1: Email validation
Form MUST validate email format before submission.

**Scenario: Invalid email**
- WHEN user submits form with malformed email
- THEN error message appears below the email field

**Scenario: Valid email**
- WHEN user submits form with valid email
- THEN form proceeds to next step
```

### Constraint (no scenarios needed)

Performance budgets, security requirements, or architectural constraints. The requirement statement is directly testable.

```markdown
#### AC-5: Response time budget
API endpoints MUST respond within 200ms at p95.

#### AC-6: Accessibility
All interactive elements SHOULD be keyboard-navigable.
```

### Multi-condition (GIVEN for preconditions)

When behavior depends on prior state, user role, or system condition.

```markdown
#### AC-3: Admin bulk delete
Admin users MUST be able to delete multiple items at once.

**Scenario: Admin selects items**
- GIVEN user has admin role
- WHEN user selects 3 items and clicks "Delete"
- THEN confirmation dialog shows count of selected items
- AND items are removed after confirmation

**Scenario: Non-admin cannot bulk delete**
- GIVEN user has viewer role
- WHEN user views item list
- THEN bulk delete option is not visible
```

## Observable vs Internal

THEN/AND clauses MUST describe observable behavior — what a user sees, an API returns, or a file contains. Never internal state.

| Observable (use this) | Internal (don't use this) |
|---|---|
| User sees error toast with message | Error state is set to true |
| API returns 400 with validation errors | Validation function returns false |
| Preview updates within 500ms | useEffect triggers re-render |
| File is written to `~/.config/app.json` | `writeFile()` is called |
| Loading spinner appears | `isLoading` becomes true |
| Table shows 10 rows sorted by date | Query returns sorted results |
| Button becomes disabled | `disabled` prop is set |

## Test Derivation (agent rules)

Agents derive test criteria mechanically from ACs. No guessing.

### Behavioral ACs → E2E tests

```
AC-1: Email validation (MUST)

Scenario: Invalid email
- WHEN user submits form with malformed email     → test setup + action
- THEN error message appears below the email field → assertion 1

Scenario: Valid email
- WHEN user submits form with valid email          → test setup + action
- THEN form proceeds to next step                  → assertion 1

Derived:
  E2E: Submit malformed email -> verify error message below field (from AC-1)
  E2E: Submit valid email -> verify form advances to next step (from AC-1)
```

### Multi-condition ACs → E2E tests with setup

```
AC-3: Admin bulk delete (MUST)

Scenario: Admin selects items
- GIVEN user has admin role                        → test setup
- WHEN user selects 3 items and clicks "Delete"    → action
- THEN confirmation dialog shows count             → assertion 1
- AND items are removed after confirmation         → assertion 2

Derived:
  E2E: Log in as admin, select 3 items, click Delete -> verify confirmation shows "3 items" (from AC-3)
  E2E: Log in as admin, confirm deletion -> verify items removed from list (from AC-3)
```

### Constraint ACs → direct assertion

```
AC-5: Response time budget (MUST)
  → E2E: Measure p95 latency across API endpoints -> verify < 200ms

AC-6: Accessibility (SHOULD)
  → E2E: Tab through all interactive elements -> verify focus order matches visual order
```

### Derivation rules

| AC element | Maps to |
|------------|---------|
| GIVEN | Test setup / precondition |
| WHEN | Test action |
| THEN | One E2E assertion |
| AND | One additional assertion |
| Constraint statement | Direct assertion from prose |
| MUST | Blocking test — must pass |
| SHOULD | Expected test — can defer |

## Confidence Levels (Explore skill only)

When requirements surface during exploration before PRD:
- **High**: User confirmed explicitly, or constraint is external/contractual
- **Medium**: Inferred from context, plausible but not confirmed
- **Low**: Agent assumption, needs validation in PRD phase
