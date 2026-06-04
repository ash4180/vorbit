# Mock Registry

Single source of truth for `.claude/mock-registry.json` — the manifest of mock data created by `/prototype` and `/implement`, and consumed by `/implement-cleanup-mocks` at backend handover. Producers write entries; cleanup reads them to know exactly what to strip.

## Registry file location

```
.claude/mock-registry.json
```

## Format (version 1.1)

```json
{
  "version": "1.1",
  "mocks": [
    {
      "feature": "string — feature/epic name",
      "type": "file | state",
      "path": "string — relative path to the file",
      "location": "string — for state only: line number, hook name, or store name",
      "endpoint": "string — inferred API endpoint, e.g. GET /api/users/:id",
      "stateType": "useState | zustand | redux | context — for type: state only",
      "createdBy": "prototype | implement",
      "createdAt": "string — ISO 8601 timestamp",
      "components": ["string — paths to components using this mock"]
    }
  ]
}
```

Create the registry file if it doesn't exist; otherwise append to the `mocks` array. Set `createdBy` to the skill writing the entry (`prototype` or `implement`).

## When to register (producers: `/prototype`, `/implement`)

**Mock files** — any file in a `mocks/` folder, any JSON with a mock data shape, any file carrying a `// TODO: Replace with real API` comment.

**Mock state** — `useState` with hardcoded array/object data (not primitives); Zustand/Redux store initial state with mock data; Context providers with mock values; any state marked `// TODO: Replace with real API`.

## What to capture per entry

Feature name (from the page/component folder) · `type` (`file` or `state`) · file path · `location` (state only: line number, hook, or store name) · inferred endpoint · `stateType` (state only) · which skill created it · ISO 8601 timestamp · the components that consume it.
