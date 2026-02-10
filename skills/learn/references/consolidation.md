# Document Consolidation

**All `.claude/rules/` files load eagerly into context at session start.** Every file consumes context tokens. Fewer, focused files = less waste.

## Before creating any new file:

1. **List existing files:** Glob `.claude/rules/*.md`
2. **Check for overlap:** Could this learning fit in an existing file?
   - UI, UX, frontend, components, layout, styling → **one file** (e.g., `ui.md`)
   - API, endpoints, HTTP, REST → **one file** (e.g., `api.md`)
   - Database, queries, migrations, models → **one file** (e.g., `database.md`)
   - Auth, login, sessions, tokens → **one file** (e.g., `auth.md`)
   - Build, deploy, CI, environment → **one file** (e.g., `build.md`)
   - Dependencies, packages, native modules → **one file** (e.g., `dependencies.md`)
3. **If an existing file covers the domain → append to it**, don't create a new one
4. **Never create files with overlapping domains** (e.g., don't have both `frontend.md` and `ui.md`)

## Keep entries concise:

Each entry in a rules file should be 1-3 lines max — a title and the key fact. Not paragraphs. The agent needs scannable reference material, not essays.

**Good:**
```
- **AsyncStorage mock required:** Any test importing from src/store needs jest.mock('@react-native-async-storage/async-storage') in jest.setup.js
```

**Bad:**
```
- **AsyncStorage mock:** themeStore.ts uses Zustand persist middleware with @react-native-async-storage/async-storage as the storage backend. In Jest, native modules do not exist, so ALL test suites that transitively import from src/store/index.ts will fail with the error "NativeModule: AsyncStorage is null". The fix is to add jest.mock('@react-native-async-storage/async-storage', () => require('@react-native-async-storage/async-storage/jest/async-storage-mock')) to your jest.setup.js file. The import chain is: any component importing from src/store -> themeStore.ts -> AsyncStorage.
```

## When to split:

Use `AskUserQuestion` to ask user about splitting **only when**:
- A single file has **20+ entries** (not line count — entry count)
- The entries clearly fall into 2+ distinct sub-topics

Otherwise, keep it in one file. Fewer files = less context overhead.
