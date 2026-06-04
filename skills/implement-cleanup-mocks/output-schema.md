# Cleanup Mocks — Output Schema

## API Contract Template

The document handed to the backend team. Populate one "Required Endpoints" entry per endpoint generated in Step 3; drop the "Questions for Backend" section if the user has none.

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
{
  "field": "type"
}

**Response Shape:**
{
  "id": "string",
  "name": "string"
}

**Example Response:**
{
  "id": "123",
  "name": "Example"
}

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
