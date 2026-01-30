# Vorbit

Product development workflows for Claude Code. TDD-first, Linear-integrated.

## Installation

```bash
# From Claude Code Marketplace
/install-plugin vorbit

# Manual
git clone https://github.com/ash4180/vorbit.git
claude --plugin-dir /path/to/vorbit
```

## Architecture

```
commands/
├── design/           # explore, prd, journey, prototype, webflow, ui-patterns
└── implement/        # epic, implement, verify, review

skills/               # Full workflow content (auto-triggered)
├── explore/          # Idea exploration
├── prd/              # PRD creation
├── journey/          # User flow diagrams
├── prototype/        # UI prototypes (registers mocks)
├── webflow/          # Webflow development
├── ui-patterns/      # UI constraints (accessibility, performance)
├── epic/             # Linear issue creation (enhanced)
├── implement/        # TDD implementation (registers mocks)
├── implement-cleanup-mocks/  # Mock cleanup & API contracts
├── verify/           # Acceptance verification
└── review/           # Linus-style code review
```

**Notion/Anytype** = PRDs, explorations, flows
**Linear** = Issue tracking (epics + sub-issues)
**Figma** = Design reference (optional)

## Commands

| Purpose | Command |
|---------|---------|
| Explore ideas | `/vorbit:design:explore [topic]` |
| Create PRD | `/vorbit:design:prd [feature]` |
| User flow diagram | `/vorbit:design:journey [feature]` |
| UI prototype | `/vorbit:design:prototype [feature]` |
| Webflow development | `/vorbit:design:webflow [figma-url]` |
| UI patterns | `/vorbit:design:ui-patterns [component]` |
| Create issues | `/vorbit:implement:epic [feature]` |
| Implement | `/vorbit:implement:implement [issue]` |
| Verify | `/vorbit:implement:verify [issue]` |
| Code review | `/vorbit:implement:review [file]` |
| Cleanup mocks | `/vorbit:implement:cleanup-mocks [feature]` |

## Enhanced Epic/Implement Workflow (v1.2.0)

### Sub-Issue Structure

Each sub-issue now includes:

| Section | Purpose |
|---------|---------|
| **Why This Is Needed** | Plain language for non-engineers |
| **Related Epic AC** | Acceptance criteria copied from parent epic |
| **Reuse & Patterns** | Existing code, utilities, constants to use |
| **File Changes** | Exact file paths with CREATE/MODIFY actions |
| **Test Criteria** | TDD requirements |

### Example Sub-Issue

```markdown
## Why This Is Needed
**What this does:** Creates the login screen for the app.
**Why it matters:** Users need to sign in to access their accounts.

## Related Epic Acceptance Criteria
> This sub-issue must satisfy:
- [ ] Users can sign in with email and password
- [ ] Invalid credentials show clear error

## Reuse & Patterns
**Similar features:** `src/components/auth/SignupForm.tsx`
**Constants:** Use `MAX_ATTEMPTS` from `src/constants/auth.ts`
**UI Patterns:** Run `/vorbit:design:ui-patterns`

## File Changes
| Action | File Path | Purpose |
|--------|-----------|---------|
| CREATE | `src/components/auth/LoginForm.tsx` | Login screen |
| CREATE | `src/tests/auth/login.test.ts` | Unit tests |

## Test Criteria (TDD)
- [ ] Test: Login with valid credentials succeeds
- [ ] Test: Login with wrong password shows error
```

### Implementation Verification

The implement skill now verifies:
- All Related Epic Acceptance Criteria satisfied
- File changes match planned paths
- Used utilities/constants from Reuse & Patterns
- No magic numbers
- No recreated functions

## Mock Cleanup Workflow (v1.3.0)

Clean handover from frontend prototyping to backend implementation.

### The Problem

During prototyping, mock data accumulates:
- Mock JSON files in `mocks/` folders
- Hardcoded `useState` with fake data
- Zustand/Redux stores with mock initial state

This confuses backend developers and pollutes the codebase.

### The Solution

**1. Mock Registry** - Prototype/implement skills now register all mocks:
```
.claude/mock-registry.json
```

**2. Cleanup Command** - When ready for backend:
```bash
/vorbit:implement:cleanup-mocks user-profile
```

**What it does:**
| Step | Action |
|------|--------|
| 1 | Load mocks from registry (or scan codebase) |
| 2 | Generate API contract from mock data shapes |
| 3 | Save contract to Notion PRD |
| 4 | Delete mock files and reset state |
| 5 | Leave TODO comments for backend connection |

### API Contract Output

```markdown
### GET /api/users/:id

**Response Shape:**
{
  "id": "string",
  "name": "string",
  "email": "string"
}

**Used by:** src/pages/UserProfile/index.tsx
```

### Mock Registry Format

```json
{
  "mocks": [
    {
      "feature": "user-profile",
      "type": "file",
      "path": "src/pages/UserProfile/mocks/user.json",
      "endpoint": "GET /api/users/:id",
      "createdBy": "prototype"
    }
  ]
}
```

## UI Patterns Skill

Based on [ui-skills.com](https://ui-skills.com). Enforces:

| Constraint | Rule |
|------------|------|
| **Styling** | Tailwind CSS only |
| **Animations** | motion/react, max 200ms |
| **Primitives** | Radix/React Aria (accessible) |
| **Class logic** | `cn()` utility |

Auto-triggered when implementing UI components.

## Defensive Hooks

Automatic code quality enforcement via Claude Code hooks.

| Hook | Event | Behavior |
|------|-------|----------|
| **Auto-Format** | PostToolUse:Edit | Runs Biome or Prettier after file edits |
| **Auto-Validate** | PostToolUse:Edit | Runs tsc/mypy/pyright/go build (blocks on errors) |
| **Console.log Audit** | Stop | Warns about debug statements at session end |
| **Push Warning** | PreToolUse:Bash | Reminds to review before `git push` |

**Formatter Priority:** Biome > Prettier (detects from project config)

**Validator Detection:**
- TypeScript: `tsconfig.json` → `tsc --noEmit`
- Python: `pyproject.toml` with `[tool.mypy]` or `[tool.pyright]` → mypy/pyright
- Go: `go.mod` → `go build ./...`

**Test the hooks:**
```bash
cd hooks/tests
./test-post-edit-format.sh
./test-post-edit-validate.sh
./test-stop-console-log-audit.sh
./test-pre-push-warning.sh
```

## Loop Mode (Ralph Wiggum Pattern)

Automatically iterate until task complete. Named after Ralph - keeps going until it gets it right.

Original technique: [ghuntley.com/ralph](https://ghuntley.com/ralph/)

```bash
/vorbit:implement:implement ABC-123 --loop
```

**How it works:**
1. Fetches Linear issue acceptance criteria
2. Runs TDD implementation
3. Checks if all criteria met
4. If not done → Ralph tries again
5. If done → exits with completion signal

**Cancel:** `/vorbit:implement:implement ABC-123 --cancel`

**Default limits:**
- Max iterations: 50
- Completion signal: "All acceptance criteria met"

## Skills

| Skill | Version | Purpose |
|-------|---------|---------|
| explore | 1.1.0 | 10+ questions before options |
| prd | 1.1.0 | 3-8 word name, numbered success criteria |
| journey | 1.1.0 | Max 15 nodes, FigJam diagrams |
| prototype | 1.1.0 | Mocks under feature folder, registers to registry |
| webflow | 1.1.0 | Figma optional, templates with page slots |
| ui-patterns | 1.0.0 | Tailwind, Radix, motion/react constraints |
| epic | 1.2.0 | Enhanced sub-issues with full context |
| implement | 1.3.0 | Verifies against epic ACs, registers mocks |
| implement-cleanup-mocks | 1.0.0 | API contract generation, mock cleanup |
| verify | 1.1.0 | Acceptance criteria validation |
| review | 1.1.0 | Linus-style brutal honesty |

## Requirements

- Support for Claude Code, Codex, Gemini
- Linear MCP
- Notion MCP or Anytype MCP
- Figma MCP (optional)
- Webflow MCP (for webflow command)

## License

MIT
