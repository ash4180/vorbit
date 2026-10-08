# Global Output Guidelines

## Before Coding

**Don't assume. Don't hide confusion. Surface tradeoffs.**

- State assumptions explicitly. If uncertain, ask — don't guess.
- If multiple interpretations exist, present them. Don't pick silently.
- If a simpler approach exists, say so. Push back when warranted.
- If something is unclear, stop. Name what's confusing. Ask.

## Philosophy

### Core Beliefs
- **Direct**: "That's broken" - no sugarcoating
- **Simple**: Eliminate special cases, not add more conditions  
- **Practical**: Solve real problems, not theoretical ones
- **Honest**: say plainly when code is broken, and why

### Simplicity Means
- Single responsibility per function/class
- Avoid premature abstractions
- No clever tricks - choose the boring solution
- If you need to explain it, it's too complex
- No error handling for impossible scenarios

### Engineering Standards
- If you need 3+ levels of indentation, redesign it
- Data structures matter more than code
- Never break existing functionality

## Error Handling

- **Fail fast** for critical errors that break core functionality
- **Log and continue** for optional features or recoverable issues
- **Graceful degradation** when external dependencies fail

### Testing
- Run tests using the project's test runner (via Bash).
- Do not use mock services in tests — use real implementations or test databases instead. Mock *data* for prototypes is fine.
- Do not move on to the next test until the current test is complete.
- If the test fails, consider checking if the test is structured correctly before deciding we need to refactor the codebase.
- Tests to be verbose so we can use them for debugging.
- Reframe tasks as tests when possible: "Fix bug" → "Write a failing test that reproduces it, then make it pass". Strong success criteria let the agent loop without constant clarification.

## Rules
- Search for existing code before writing new code. Reuse or extend it instead of adding a second function for the same job.
- Finish what you start: no partial implementations, placeholders, or dead code.
- Tests must be able to fail on real flaws.
- Follow the naming and structure already in the codebase.
- Prefer the simple, boring solution over a clever or abstract one. Separate concerns; release resources you open.
- Read a file before you modify it.
- Change only what the request needs. Leave adjacent code and formatting alone.

## This repository

`skills/<name>/SKILL.md` is the only authored source for skills. Files under `codex/skills/vorbit-shared/workflows/`, `gemini/skills/vorbit-shared/workflows/`, and the mirrored `references/` and `examples/` folders are generated. Edit the canonical skill, then run `python3 -m vorbit_core.project_skills --write`. `pytest` fails on stale outputs. `implement-loop.md` is hand-written per agent.
