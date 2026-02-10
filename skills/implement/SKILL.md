---
name: implement
version: 1.3.0
description: Use when user says "implement this", "build feature", "fix this bug", "code this", "work on issue", "start coding", or asks to implement from a Linear issue or description. Standard TDD workflow for coding tasks.
---

# Implementation Skill

A disciplined, Test-Driven Development (TDD) workflow for implementing features or fixing bugs.

## Handle Loop Mode

**If `--loop` or `--cancel` in arguments:**
Use the **implement-loop** skill for loop state management and sub-issue tracking.

**If no loop flags:** Continue with normal implementation below.

## Step 1: Detect Platform & Verify Connection

Read and follow the platform detection steps in `_shared/platform-detection.md` (glob for `**/skills/_shared/platform-detection.md`). Pass the detected platform to subsequent steps. If no PRD is needed, skip this step.

## Step 2: Determine Context

**Priority order for finding issue:**

1. **IF args = Linear issue ID** (e.g., `ABC-123`): Fetch issue details from Linear
2. **IF args = Linear URL**: Extract issue ID from URL, fetch details
3. **IF no args, check conversation**: Look for Linear issue URLs from recent `/vorbit:implement:epic` output
   - If found: "I see you just created [issue title]. Work on this one?" (Yes/No)
4. **IF nothing found**: Use `list_issues` with `assignee: "me"` to show assigned issues, ask which to work on
5. **IF description only**: Work directly on what user describes (no Linear tracking)

## Step 3: Before Starting

For Linear issues:
- Update issue status to "In Progress"
- Read issue description for requirements
- Check parent issue for SDD and style findings
- Check linked PRD if available:
  - **Notion PRD**: Use `notion-find` to fetch
  - **Anytype PRD**: Use `API-get-object` to fetch

## Step 3.5: Parse Enhanced Issue Format

**CRITICAL: If issue contains these sections, use them:**

### Check "Related Epic Acceptance Criteria"
If present:
1. Read the parent epic's ACs listed in the issue
2. These are your PRIMARY success criteria
3. **Rule:** Task is NOT done until ALL listed epic ACs are satisfied

### Check "Reuse & Patterns"
If present:
1. **Similar features** → Open and study these files FIRST
2. **Utilities** → Use these, DO NOT recreate
3. **Constants** → Use these, NO magic numbers allowed
4. **UI Patterns** → If present, invoke `/vorbit:design:ui-patterns`

### Check "File Changes"
If present:
1. This is your implementation plan
2. CREATE files at exact paths listed
3. MODIFY files at exact paths listed
4. **Rule:** Don't deviate without updating the issue

### Detect UI Work
If issue involves UI components:
- Check for ui-patterns reference in issue
- If UI work detected, use ui-patterns skill for constraints
- Follow: Tailwind, motion/react, accessibility primitives

## Step 4: Learn Codebase Style

**CRITICAL: Before writing ANY code:**

1. **Find similar code** - Grep for similar features in codebase
2. **Study patterns** - Import style, naming conventions, file structure
3. **Test patterns** - How does project structure tests?
4. **Note 2-3 example files** - Use as style reference

**Rule**: Consistency > Novelty. This ensures code matches team's style.

## Step 4.5: Detect i18n/Localization Requirements

**Check if project uses ANY localization system:**

### Detection Strategy (framework-agnostic)

1. **Search for common i18n patterns:**
```bash
# Check package.json for ANY i18n library
grep -E "i18n|intl|locale|translation|l10n|gettext|fluent" package.json 2>/dev/null

# Find locale/translation directories (check common locations)
find . -maxdepth 3 -type d \( -name "locales" -o -name "locale" -o -name "i18n" -o -name "translations" -o -name "messages" -o -name "lang" -o -name "languages" \) 2>/dev/null

# Check for translation files
find . -maxdepth 4 -type f \( -name "*.po" -o -name "*.pot" -o -name "*.mo" -o -name "*.xliff" -o -name "*.arb" -o -name "**/en.json" -o -name "**/en-US.json" \) 2>/dev/null | head -10
```

2. **Check config files** for i18n setup:
   - `next.config.*` (Next.js)
   - `nuxt.config.*` (Nuxt)
   - `angular.json` (Angular)
   - `vue.config.*` or `vite.config.*` (Vue)
   - `.env*` files for locale settings
   - Any `i18n.*` config file

3. **Grep for translation function usage:**
```bash
grep -rE "useTranslations|useIntl|useT|t\(|i18n\.|formatMessage|gettext|__|_t\(|\$t\(|trans\(" src/ app/ components/ --include="*.ts" --include="*.tsx" --include="*.js" --include="*.vue" --include="*.svelte" 2>/dev/null | head -10
```

### If i18n detected:

**Document the setup (note these for later):**
- **Translation file location**: Where are locale files stored?
- **Supported locales**: What languages exist? (e.g., `en`, `zh`, `es`)
- **Translation function**: How to use it? (varies by framework)
- **Key naming convention**: What pattern does project use?

### i18n Rules (universal):
- **NO hardcoded user-facing strings** - All UI text must use the project's translation system
- **ALL locales updated** - New keys must be added to EVERY locale file
- **Match existing patterns** - Follow the project's key naming convention
- **Handle plurals/interpolation** - Use the framework's syntax for dynamic content

### Common Frameworks Reference

| Framework | Common Library | Translation Function |
|-----------|---------------|---------------------|
| React/Next.js | `next-intl`, `react-intl`, `i18next` | `t()`, `useTranslations()`, `formatMessage()` |
| Vue/Nuxt | `vue-i18n`, `@nuxtjs/i18n` | `$t()`, `t()` |
| Angular | `@angular/localize`, `ngx-translate` | `$localize`, `translate.instant()` |
| Svelte | `svelte-i18n` | `$_()`, `$t()` |
| Flutter | `flutter_localizations`, `intl` | `AppLocalizations.of(context)` |
| Python | `gettext`, `babel` | `_()`, `gettext()` |
| Go | `go-i18n` | `localizer.Localize()` |
| Ruby/Rails | `i18n` gem | `t()`, `I18n.t()` |

**Rule**: If the project has ANY localization setup, missing translations = broken UX. This is a blocker.

## Step 5: Check for Sub-issues

**For parent issues (epics):**

1. Use `list_issues` with `parentId: [issue ID]` to fetch all sub-issues
2. Filter sub-issues that have the **Parallel** label
3. Group parallel sub-issues by shared dependencies
4. For each parallel group:
   - Use Task tool to spawn one agent per sub-issue
   - Each agent follows TDD approach below
   - Wait for all agents in group to complete before next group
5. Process non-parallel sub-issues sequentially after all parallel groups

## Step 6: TDD Implementation

**RULE: Task is NOT done until tests pass.**

**RULE**: If you implement backend API changes, also implement the corresponding frontend site API integration. Use explicit `TODO:` markers only for temporary placeholders.

For each task:

### Red (Write Test First)
- Create test that validates acceptance criteria
- Follow project's test file patterns
- Run test - **MUST FAIL** (proves test is valid)

### Green (Implement)
- Write the minimum code to pass the test
- Follow existing codebase patterns
- Match style of example files found earlier
- Use existing components/utilities
- No over-engineering

### Refactor
- Clean up code
- Check coverage on new code
- Ensure no regressions

### If Creating Mock Data During Implementation
**Register mock in `.claude/mock-registry.json`:**

**For mock files:**
```json
{
  "feature": "[Feature name]",
  "type": "file",
  "path": "src/path/to/mock.json",
  "endpoint": "GET /api/[resource]",
  "createdBy": "implement",
  "createdAt": "[ISO timestamp]",
  "components": ["src/path/to/component.tsx"]
}
```

**For mock state (useState, stores, context):**
```json
{
  "feature": "[Feature name]",
  "type": "state",
  "path": "src/path/to/component.tsx",
  "location": "useState:items (line 23)",
  "endpoint": "GET /api/[resource]",
  "stateType": "useState | zustand | redux | context",
  "createdBy": "implement",
  "createdAt": "[ISO timestamp]",
  "components": ["src/path/to/component.tsx"]
}
```
- Append to existing mocks array
- This enables cleanup before backend handover

### Task Complete Criteria
**ONLY mark done when:**
- [ ] Unit test exists and passes
- [ ] Code matches team's style
- [ ] No regressions in existing tests
- [ ] No mock data remains (check for `MOCK_`, mock imports, `.json` test data) **OR mocks registered in `.claude/mock-registry.json`**
- [ ] **All "Related Epic Acceptance Criteria" satisfied** (if present in issue)
- [ ] **File changes match planned paths** (if "File Changes" section exists)
- [ ] **Used utilities/constants from "Reuse & Patterns"** (no magic numbers, no recreated functions)
- [ ] **No dead code or leftover TODOs**
- [ ] **i18n complete** (if project has localization): All user-facing strings use translation system, keys added to ALL locale files

## Step 7: On Task Completion

- Update Linear status to "Done" or "In Review"
- Add comment: what was done, files changed

## Step 8: On Feature Completion

**After ALL tasks done, create memory.md:**

```markdown
# Feature: [Name]

## What Was Built
[Summary]

## Technical Decisions
[Why chose approach X]

## Lessons Learned
[What worked, what was hard]

## Code Patterns
[Reference README.md or CLAUDE.md if patterns documented there, otherwise note new patterns discovered]
```

## Step 9: Report

- What was implemented
- Files changed
- Tests added/updated
- memory.md location
- Next: `/vorbit:implement:verify` to verify

## Quick Mode

For simple tasks (< 30 lines):
- Just implement it
- Run existing tests
- Skip memory.md

