# Notion Database Mapping

## Target Database

**Ask user where to save PRD:**
- Database name (search Notion)
- Specific page URL
- "Skip" to not save

Use Notion MCP `notion-search` to find database by name.

## Field Mapping

| Notion Field | PRD Field | Type | Required | Notes |
|--------------|-----------|------|----------|-------|
| `Name` | Feature name | title | Yes | 3-8 words |
| `Description` | One-line summary | text | Yes | Max 100 chars |
| `Type` | Document type | multi_select | No | Set to `["PRD"]` if field exists |
| `URL` | External link | url | No | Figma or other reference |
| `Created Date` | Timestamp | created_time | Auto | System-generated |

**Note:** Adapt to team's actual database schema. Not all fields may exist.

## Page Content Structure

The PRD content goes in the page body using Notion markdown:

```markdown
## Problem
[Problem statement - max 3 sentences]

## Target Users
[Who has this problem]

## User Stories

### US-001: [Story title]
As a [user type], I want [goal], so that [benefit]

**Acceptance Criteria:**
- [ ] Criterion 1
- [ ] Criterion 2

### US-002: [Story title]
As a [user type], I want [goal], so that [benefit]

**Acceptance Criteria:**
- [ ] Criterion 1
- [ ] Criterion 2

## Constraints
[Budget, timeline, compliance limits]

## Out of Scope
- [What we're NOT building]
- [Another exclusion]

## Success Criteria
- [Measurable outcome 1]
- [Measurable outcome 2]
```

## API Call Example

```javascript
// Step 1: Ask user for database
const location = await askUser("Where should I save this PRD?");

// Step 2: Search for database
const db = await notion.search({ query: location, query_type: "internal" });

// Step 3: Create page
await notion.createPage({
  parent: { data_source_id: db.id },
  properties: {
    "Name": "User Authentication Flow",
    "Description": "Secure login/signup for web and mobile users",
    "Type": ["PRD"]  // Only if field exists
  },
  content: "## Problem\n..."
});
```
