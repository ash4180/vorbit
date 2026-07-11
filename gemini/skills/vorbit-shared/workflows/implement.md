<!-- GENERATED from skills/implement/SKILL.md — edit the canonical file, then run: python3 -m vorbit_core.project_skills --write -->

# Implementation Skill

A disciplined, Test-Driven Development (TDD) workflow for implementing features or fixing bugs.

Read and follow `../references/execution-contract.md` before starting.

> **Linear tools**: Use the connected Linear tools shipped with Vorbit. Verify the available operation and parameter schema before calling it; never guess a verb or field name.

## Handle Loop Mode

**If `--loop` or `--cancel` is present, or the gemini implement-loop state file (see the implement-loop workflow) shows an active loop:**
Use the **implement-loop** skill for loop state management and sub-issue tracking.

**If no loop flags:** Continue with normal implementation below.

## Step 1: Resolve Input and Capabilities

Preflight required connectors: confirm each needed connector is configured in Gemini CLI and inspect its current operation/parameter schemas; never guess tool names. Only require Linear for a Linear issue or URL. A connection failure blocks Linear tracking, not implementation from a complete user-provided description.

## Step 2: Determine Context

**Priority order for finding issue:**

1. **IF args = Linear issue ID** (e.g., `ABC-123`): Fetch issue details from Linear
2. **IF args = Linear URL**: Extract issue ID from URL, fetch details
3. **IF no args, check conversation**: Look for Linear issue URLs from recent `$vorbit-epic` output
   - If found: "I see you just created [issue title]. Work on this one?" (Yes/No)
4. **IF nothing found**: Ask what to implement. Do not select assigned work without the user's request
5. **IF description only**: Work directly on what user describes (no Linear tracking)

For a Linear issue, record the issue ID and description update timestamp used as the requirement baseline. If it changes during implementation, stop and reconcile the new requirements.

## Step 3: Before Starting

For Linear issues:
- Read issue description for requirements
- Check parent issue for SDD and style findings
- Fetch the linked Linear PRD/specification ticket when available
- Map the issue to its `US-*`, globally unique `US-*.AC-*`, and `F*-S*` identifiers
- Confirm no implementation-affecting `TBD` remains
- Only after those gates pass, update the selected implementation issue to the team's exact In Progress state before editing code

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
4. **UI Patterns** → If present, invoke `$vorbit-ui-patterns`

### Check "File Changes"
If present:
1. This is your implementation plan
2. Treat listed paths as the approved plan, not proof that the current codebase still matches it
3. If code evidence requires a different path, explain why before editing and update the issue after approval
4. Never create a duplicate merely to match a stale path

### Detect UI Work
If issue involves UI components:
- Check for ui-patterns reference in issue
- If UI work detected, use ui-patterns skill for constraints
- Preserve the repository's existing styling and primitive stack; apply Tailwind or `motion/react` only when already present or explicitly approved

## Step 4: Learn Codebase Style

**CRITICAL: Before writing ANY code:**

1. **Find similar code** - Use `rg` to find similar features and call sites
2. **Study patterns** - Import style, naming conventions, file structure
3. **Test patterns** - How does project structure tests?
4. **Note 2-3 example files** - Use as style reference

**Rule**: Consistency > Novelty. This ensures code matches team's style.

## Step 4.5: Detect i18n/Localization Requirements

**Check if project uses ANY localization system:**

### Detection Strategy (framework-agnostic)

1. **Search for common i18n patterns**: check `package.json` for any i18n library (`i18n`, `intl`, `locale`, `translation`, `l10n`, `gettext`, `fluent`); look for locale/translation directories (`locales/`, `i18n/`, `translations/`, `messages/`, `lang/`) and translation files (`*.po`, `*.pot`, `*.mo`, `*.xliff`, `*.arb`, `en.json`, `en-US.json`)

2. **Check config files** for i18n setup:
   - `next.config.*` (Next.js)
   - `nuxt.config.*` (Nuxt)
   - `angular.json` (Angular)
   - `vue.config.*` or `vite.config.*` (Vue)
   - `.env*` files for locale settings
   - Any `i18n.*` config file

3. **Search source for translation function usage** — see the framework table below for the functions to grep

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

## Step 5: Handle Parent Issues

If the selected issue has open sub-issues, do not silently implement the whole tree. Show the queue from the parent's `## Implementation Order` section and ask the user to choose one sub-issue or explicitly start loop mode. Normal implementation owns one issue at a time; implement-loop owns multi-issue progression.

## Step 6: TDD Implementation

**RULE: Task is NOT done until tests pass.**

Keep the change within the selected issue. Do not add a frontend or backend counterpart unless its acceptance criteria require it.

For each task, follow Red/Green/Refactor:

- **Red**: When the repository has a runnable harness, write a failing test for the changed behavior first (follow the project's test patterns; confirm the focused test fails for the expected reason). If no suitable harness exists, agree on a real verification surface; do not invent a cheater test.
- **Green**: Write the minimum code to pass, following existing codebase patterns and the example files found earlier; no over-engineering.
- **Refactor**: Clean up, check coverage on new code, ensure no regressions. Remove dead code and unregistered placeholder TODOs (registered prototype mocks may remain until backend integration).

### If Creating Mock Data During Implementation
**Register mock in the resolved project registry** (`<storage_root>/projects/<project_slug>/mock-registry.json`; fallback `.vorbit/mock-registry.json`):

The registry root is `{ "version": "1.1", "mocks": [...] }`. The snippets below are individual entries appended to `mocks`.

**For mock files:**
```json
{
  "feature": "[Feature name]",
  "type": "file",
  "path": "src/path/to/mock.json",
  "endpoint": "proposed:GET /api/[resource]",
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
  "endpoint": "proposed:GET /api/[resource]",
  "stateType": "useState | zustand | redux | context",
  "createdBy": "implement",
  "createdAt": "[ISO timestamp]",
  "components": ["src/path/to/component.tsx"]
}
```
- Append to existing mocks array
- Every temporary application mock must be registered here before the task is done (test fixtures are excluded)
- This enables cleanup before backend handover

### Task Complete Criteria
Mark done only when every gate defined in Steps 3.5-6 above is satisfied.

## Step 7: On Task Completion

- Keep the implementation parent "In Progress" until a PR exists. Implementation sub-issues may move to "Done" after their own ACs and tests pass.
- Add a Linear comment with changed files, verification evidence, and remaining release steps.

## Step 8: On Feature Completion

Do not create a generic `memory.md`. Record durable decisions only in an existing repository-approved location, and only when future maintainers need them.

## Step 9: Report

- What was implemented
- Files changed
- Tests added/updated
- Next: `$vorbit-verify` to verify

## Quick Mode

For simple tasks (< 30 lines):
- Keep the same search, scope, and verification rules
- Skip issue ceremony only when no Linear issue was supplied
