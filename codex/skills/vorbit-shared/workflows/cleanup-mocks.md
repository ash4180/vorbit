<!-- GENERATED from skills/implement-cleanup-mocks/SKILL.md — edit the canonical file, then run: python3 -m vorbit_core.project_skills --write -->

# Cleanup Mocks Skill

Clean up mock data created during prototyping/implementation and generate API contract documentation for backend handover.

Read and follow `../references/execution-contract.md` before starting.

## Purpose

When frontend development is ready for backend integration:
1. Inventory application mocks and the exact UI fields they support
2. Confirm and save an API contract
3. Integrate the real repository-native API path when it exists
4. Remove mocks only after the real path passes tests

## Step 1: Resolve Contract Destination

Use the linked Linear PRD/specification ticket when available. Otherwise use `docs/api-contracts/[feature-name].md`. Do not require an external platform to produce a local contract.

## Step 2: Load Mock Registry

Read `../references/mock-registry.md` for the registry schema, field semantics, and storage-root resolution, then load the registry from the resolved path.

Cleanup-specific reading notes:
- Iterate `mocks[]` grouped by `feature`; `type` determines removal mechanics — `path` for `file` entries, `path` plus `location`/`stateType` for `state` entries.
- An `endpoint` still carrying the `proposed:` prefix is an unconfirmed inference — resolve it in the contract before treating it as fact.
- An entry is removable only after Step 6 passes: real integration green and every path in `components` verified free of mock imports.

**IF registry exists:**
- Load and display registered mocks grouped by feature
- Ask: "Clean up mocks for which feature? (or 'all')"

**IF registry doesn't exist:**
- Scan production source for mock patterns, excluding tests, fixtures, stories, seeds, examples, and static demo/sample content:
  - `**/mocks/*.json` - mock data files
  - `**/mocks/*.ts` - mock data exports
  - Files with `// TODO: Replace with real API`
  - `MOCK_` prefixed constants
  - **Mock state patterns** only when code evidence ties them to a temporary API substitute:
    - `useState(MOCK_` or `useState([{` with hardcoded data
    - `const [data, setData] = useState(mockData)`
    - Zustand/Redux stores with hardcoded initial state
    - Context providers with mock values
- Present findings grouped by type and evidence. A hardcoded initial state alone is not proof that data is disposable.

## Step 3: Generate API Contract

**For each mock file being cleaned up:**

1. **Read mock file content** - extract data shape
2. **Propose endpoint** from filename/location and existing client conventions:
   - `users.json` → `GET /api/users`
   - `user-detail.json` → `GET /api/users/:id`
   - Check for comments and existing routes indicating endpoint
   - Label any unverified method/path/auth detail as a question; never turn an inference into a contract fact
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

**Show the complete API contract document** — use the API Contract Template below, filled with the endpoint sections generated in Step 3.

**Ask:** "Does this inventory and API contract look correct? Ready to save it?"

**Wait for confirmation before proceeding.**

## Step 5: Save Approved Contract

1. Append the approved contract to the linked Linear PRD/specification ticket when authorized, using the current connector's verified update operation.
2. Otherwise create `docs/api-contracts/[feature-name].md`.
3. Record the source mock paths, approval date, and source issue revision/update timestamp.

## Step 6: Integrate Before Removing

1. Preflight the real backend endpoint and the repository's API client pattern.
2. If the endpoint, auth, or required response semantics do not exist, stop with `needs_backend`. Keep the working mocks; contract generation is still a valid completed output.
3. When the real API exists, write an integration test at the existing data boundary and observe it fail for the missing connection.
4. Implement the repository-native client/adapter and switch the single mock integration boundary to it. Presentational components continue to receive props.
5. Verify loading, success, empty, and error behavior required by the approved contract and ACs.
6. Run the focused and relevant regression suites.
7. Only after the real path passes, prove each mock has no remaining production consumers, delete it, remove empty directories, and update the registry atomically.

Never replace working mock behavior with `null`, empty arrays, permanent loading state, or TODO-only placeholders. That is a broken partial implementation, not cleanup.

## Step 7: Report

Report:
- terminal status: `completed`, `needs_backend`, `blocked`, or `failed`
- contract destination and revision
- endpoint details confirmed vs still unknown
- integration and regression evidence
- files updated and mocks removed
- remaining registered mocks and next owner/action

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

- All fields shown are actively used by frontend components — the documented shapes are exact
- Dates are ISO 8601; ID types and nullability must match the approved contract exactly

## Questions for Backend
[Any unclear requirements or decisions needed]
```
