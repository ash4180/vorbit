---
name: implement-cleanup-mocks
version: 1.0.0
description: Use when user says "cleanup mocks", "handover to backend", "remove mock data", "prepare for backend", or wants to clean up mock data and generate API contract docs before backend handover.
---

# Cleanup Mocks Skill

Clean up mock data created during prototyping/implementation and generate API contract documentation for backend handover.

## Purpose

When frontend development is ready for backend handover:
1. Generate API contract doc from mock data shapes
2. Update PRD in Notion with API requirements
3. Delete mock files and state
4. Leave clean branch for backend

> **Locate `_shared/`**: This skill ships as a plugin, so `_shared/` files live in the plugin cache, not your project. Before reading any `_shared/...` path below, run `ls -d ~/.claude/plugins/cache/local/vorbit/*/skills/_shared 2>/dev/null | head -1` and use the output as the absolute base for every `_shared/...` reference.

## Step 1: Detect Platform & Verify Connection

Read and follow `_shared/mcp-tool-routing.md`. Discover connected platforms, ask user which to use, and verify connection.

## Step 2: Load Mock Registry

**Check for mock registry file:**
```
.claude/mock-registry.json
```

**Registry format:** see `_shared/mock-registry.md` for the version 1.1 schema.

**IF registry exists:**
- Load and display registered mocks grouped by feature
- Ask: "Clean up mocks for which feature? (or 'all')"

**IF registry doesn't exist:**
- Scan codebase for mock patterns:
  - `**/mocks/*.json` - mock data files
  - `**/mocks/*.ts` - mock data exports
  - Files with `// TODO: Replace with real API`
  - `MOCK_` prefixed constants
  - **Mock state patterns:**
    - `useState(MOCK_` or `useState([{` with hardcoded data
    - `const [data, setData] = useState(mockData)`
    - Zustand/Redux stores with hardcoded initial state
    - Context providers with mock values
- Present findings grouped by type (files vs state) and ask which to clean up

## Step 3: Generate API Contract

**For each mock file being cleaned up:**

1. **Read mock file content** - extract data shape
2. **Infer endpoint** from filename/location:
   - `users.json` → `GET /api/users`
   - `user-detail.json` → `GET /api/users/:id`
   - Check for comments indicating endpoint
3. **Generate contract entry:**

```markdown
### [Endpoint Name]

**Endpoint:** `GET /api/users/:id`

**Description:** [Infer from feature name and data]

**Response Shape:**
```json
{
  "id": "string",
  "name": "string",
  "email": "string",
  "createdAt": "ISO date string"
}
```

**Example Response:**
```json
[Actual mock data - first item if array]
```

**Used by:** [List components that import this mock]
```

## Step 4: Collect Open Questions for Backend

Before assembling the contract, ask the user via `AskUserQuestion` whether there are open questions or decisions the backend team needs to make. Examples:
- "Should this endpoint paginate? If yes, cursor or offset?"
- "Authorization: per-user only, or also per-org?"
- "Soft-delete or hard-delete for the DELETE endpoint?"

If the user has nothing, drop the "Questions for Backend" section from the contract template. Don't auto-populate it with guesses — vague questions are worse than no questions. This step closes the gap where no upstream skill writes that section; without asking here, it stays empty.

## Step 5: Present API Contract for Review

**Show the complete API contract document**, populated with the endpoints generated in Step 3 — use the template in `./output-schema.md`.

**Ask:** "Does this API contract look correct? Ready to save to PRD?"

**Wait for confirmation before proceeding.**

## Step 6: Save API Contract to PRD

### If Notion PRD:
1. Use `notion-fetch` to get current PRD content
2. Use `notion-update-page` to append API Contract section:
   - Command: `insert_content_after`
   - Find appropriate location (after User Stories or at end)
   - Insert the API contract markdown

### If no platform detected:
1. Create local file: `docs/api-contracts/[feature-name].md`
2. Report file location

## Step 7: Clean Up Mock Files and State

**For each mock in cleanup scope:**

### 6.1 Mock Files
1. **Delete mock JSON/TS files** in `mocks/` folders
2. **Update imports** - replace mock imports with placeholder:
   ```tsx
   // BEFORE:
   import mockData from './mocks/data.json';
   // TODO: Replace with real API

   // AFTER:
   // TODO: Connect to real API - see PRD for contract
   // API endpoint: GET /api/users
   const data = null; // Backend will implement
   ```
3. **Remove empty mocks/ directories**

### 6.2 Mock State
1. **Replace hardcoded useState** with empty/loading state:
   ```tsx
   // BEFORE:
   const [users, setUsers] = useState([
     { id: 1, name: 'John' },
     { id: 2, name: 'Jane' }
   ]);

   // AFTER:
   // TODO: Connect to real API - GET /api/users
   const [users, setUsers] = useState<User[]>([]);
   const [loading, setLoading] = useState(true);
   ```

2. **Clean Zustand/Redux stores** - replace mock initial state:
   ```tsx
   // BEFORE:
   const useStore = create((set) => ({
     users: MOCK_USERS,
     // ...
   }));

   // AFTER:
   // TODO: Connect to real API - GET /api/users
   const useStore = create((set) => ({
     users: [],
     loading: true,
     // ...
   }));
   ```

3. **Clean Context providers** - replace mock values:
   ```tsx
   // BEFORE:
   <UserContext.Provider value={mockUserData}>

   // AFTER:
   // TODO: Connect to real API - GET /api/users/:id
   <UserContext.Provider value={null}>
   ```

### 6.3 Update Registry
- Remove cleaned entries from `.claude/mock-registry.json`

## Step 8: Report

**Present summary:**

```
## Mock Cleanup Complete

### API Contract
- Saved to: [Notion PRD URL / local file path]
- Endpoints documented: [count]

### Files Removed
- src/pages/Feature/mocks/data.json
- src/pages/Feature/mocks/users.json

### Files Updated
- src/pages/Feature/index.tsx (mock import → API placeholder)
- src/pages/Feature/components/List.tsx (mock import → API placeholder)

### Next Steps for Backend
1. Review API contract in PRD
2. Implement endpoints matching documented shapes
3. Frontend will connect via [API client pattern]
```

---

# Mock Registry Schema

See `_shared/mock-registry.md` for the `.claude/mock-registry.json` location, the version 1.1 format, registration rules, and what each entry captures.

---

# API Contract Template

See `./output-schema.md` for the full API Contract Template handed to backend.
