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
2. Update PRD in Notion or Anytype with API requirements
3. Delete mock files and state
4. Leave clean branch for backend

## Step 1: Detect Platform & Verify Connection

Read and follow the platform detection steps in `_shared/platform-detection.md` (glob for `**/skills/_shared/platform-detection.md`). Pass the detected platform to subsequent steps.

## Step 2: Load Mock Registry

**Check for mock registry file:**
```
.claude/mock-registry.json
```

**Registry format:**
```json
{
  "version": "1.0",
  "mocks": [
    {
      "feature": "user-profile",
      "path": "src/pages/UserProfile/mocks/user.json",
      "endpoint": "GET /api/users/:id",
      "createdBy": "prototype",
      "createdAt": "2024-01-15T10:00:00Z"
    }
  ]
}
```

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

## Step 4: Present API Contract for Review

**Show complete API contract document:**

```markdown
# API Contract - [Feature Name]

Generated from frontend mock data for backend implementation.

## Overview
- Feature: [Feature name]
- Generated: [Date]
- Mock files cleaned: [Count]

## Required Endpoints

[Generated endpoint sections from Step 3]

## Notes for Backend
- Response shapes are based on frontend UI requirements
- All fields shown are actively used by frontend components
- Frontend expects these exact field names (case-sensitive)
```

**Ask:** "Does this API contract look correct? Ready to save to PRD?"

**Wait for confirmation before proceeding.**

## Step 5: Save API Contract to PRD

### If Notion PRD:
1. Use `notion-fetch` to get current PRD content
2. Use `notion-update-page` to append API Contract section:
   - Command: `insert_content_after`
   - Find appropriate location (after User Stories or at end)
   - Insert the API contract markdown

### If Anytype PRD:
1. Use `API-get-object` to fetch current PRD content
2. Use `API-update-object` to append API Contract section to the PRD body
   - Find appropriate location (after User Stories or at end)
   - Insert the API contract markdown

### If no platform detected:
1. Create local file: `docs/api-contracts/[feature-name].md`
2. Report file location

## Step 6: Clean Up Mock Files and State

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

## Step 7: Report

**Present summary:**

```
## Mock Cleanup Complete

### API Contract
- Saved to: [Notion PRD URL / Anytype object ID / local file path]
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

## Registry File Location
```
.claude/mock-registry.json
```

## Registry Format
```json
{
  "version": "1.1",
  "mocks": [
    {
      "feature": "string - feature/epic name",
      "type": "file | state",
      "path": "string - relative path to file",
      "location": "string - for state: line number or function name",
      "endpoint": "string - inferred API endpoint (e.g., GET /api/users)",
      "stateType": "useState | zustand | redux | context (only for type: state)",
      "createdBy": "string - 'prototype' | 'implement'",
      "createdAt": "string - ISO 8601 timestamp",
      "components": ["string - paths to components using this mock"]
    }
  ]
}
```

## Registration Rules

**When to register (in prototype/implement skills):**

### Mock Files
- Any file created in a `mocks/` folder
- Any JSON file with mock data shape
- Any file with `// TODO: Replace with real API` comment

### Mock State
- `useState` with hardcoded array/object data (not primitives)
- Zustand/Redux store initial state with mock data
- Context providers with mock values
- Any state marked with `// TODO: Replace with real API`

**What to capture:**
- Feature name (from page/component folder)
- Type: `file` or `state`
- File path
- Location (for state: line number, hook name, or store name)
- Inferred endpoint
- State type (for state: useState, zustand, redux, context)
- Which skill created it
- Timestamp
- Components that use it

---

# API Contract Template

```markdown
# API Contract - [Feature Name]

> Generated from frontend mock data for backend implementation.
> Date: [Generated date]

## Overview

| Item | Value |
|------|-------|
| Feature | [Feature name] |
| PRD | [Link to PRD] |
| Frontend Status | Ready for backend |
| Mock files | [Count] cleaned |

## Required Endpoints

### 1. [Endpoint Name]

| Property | Value |
|----------|-------|
| Method | GET/POST/PUT/DELETE |
| Path | `/api/resource/:id` |
| Auth | Required/Optional |

**Request Body (if POST/PUT):**
```json
{
  "field": "type"
}
```

**Response Shape:**
```json
{
  "id": "string",
  "name": "string"
}
```

**Example Response:**
```json
{
  "id": "123",
  "name": "Example"
}
```

**Used by components:**
- `src/pages/Feature/index.tsx`
- `src/pages/Feature/components/List.tsx`

---

## Implementation Notes

- All field names are case-sensitive
- Frontend expects exact shapes documented above
- Dates should be ISO 8601 format
- IDs can be string or number (frontend handles both)

## Questions for Backend
[Any unclear requirements or decisions needed]
```
