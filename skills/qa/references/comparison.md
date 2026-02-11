# QA Document Comparison

How to compare two QA documents and produce a coverage gap analysis.

## Input Formats

| Format | How to Read |
|---|---|
| **PDF** | Use Read tool (supports PDF natively) |
| **Excel (.xlsx)** | Ask user to download locally, read as PDF export or CSV |
| **CSV** | Read tool or Bash `cat` |
| **Google Sheets** | Ask user to export as CSV or download |
| **SharePoint/OneDrive** | Ask user to download locally — Chrome MCP cannot access iframe-based Office Online |
| **Notion page** | Use `notion-fetch` with page ID or URL |
| **Anytype object** | Use `API-get-object` with object ID |
| **Markdown file** | Read tool |

**Key limitation:** Authenticated URLs (SharePoint, Google Docs, Confluence, Jira) cannot be fetched directly. Always ask user to download the file locally.

## Step 1: Normalize Both Documents

Extract test cases from each document into a common format:

```
[ID] | [Description] | [Feature Area] | [Test Type] | [Priority]
```

If the external document doesn't have feature areas, infer from the test description:
- Mentions "incident" → Incident Management
- Mentions "alert" → Alerts
- Mentions "schedule" or "on-call" → On-Call
- Mentions "login" or "auth" → Authentication
- etc.

## Step 2: Feature Area Coverage Matrix

Build a comparison table:

```markdown
| Feature Area | Plan Cases | Doc Cases | Coverage | Key Gaps |
|---|---|---|---|---|
| Incident Management | 30 | 35 | Deep but partial | Missing: pagination URL sync, AI summary |
| Alerts | 17 | 1 | ~6% | Missing: filters, bulk actions, detail page |
| On-Call | 24 | 0 | 0% | Entirely untested |
| Authentication | 9 | 0 | 0% | Entirely untested |
```

**Coverage assessment scale:**
- **0%** — "Entirely untested"
- **1-25%** — "Minimal coverage"
- **25-50%** — "Partial coverage"
- **50-75%** — "Moderate coverage"
- **75-100%** — "Good coverage"
- **>100% (more doc cases than plan)** — "Deep but may have gaps in other areas"

## Step 3: Direct Overlap Mapping

Map test cases that exist in BOTH documents:

```markdown
| Plan Case | Doc Case | What |
|---|---|---|
| IM-01 | TC_001 | Incident page loads |
| IM-02 | TC_005, TC_006 | Search by ID / keyword |
| IM-15 | TC_002, TC_003 | Create incident |
```

## Step 4: Gap Analysis

### Gaps in the existing doc (what plan has, doc doesn't):

List feature areas with 0% coverage first, then areas with partial coverage noting specific missing test types.

### Additions from the doc (what doc has, plan doesn't):

These are valuable edge cases or depth the existing testers discovered. Common additions:
- **Concurrency tests** — multiple users acting simultaneously
- **Permission tests** — unauthorized user attempts
- **Performance tests** — large dataset behavior
- **Lifecycle tests** — full flow from create to close
- **Negative tests** — invalid inputs, error paths

## Step 5: Summary Statistics

```markdown
### Bottom Line

**Existing doc covers ~X% of the plan's scope.**
- Direct overlaps: N test cases
- Plan areas with 0% coverage: M
- Doc has K additional edge cases worth incorporating

**Recommendation:**
- [Incorporate doc's edge cases into sections X, Y, Z]
- [Prioritize testing areas A, B, C which have 0% coverage]
```

## Comparison Report Template

```markdown
# QA Coverage Comparison

## Documents Compared
- **Plan**: [name/URL] — X test cases across Y feature areas
- **Existing**: [name/URL] — Z test cases

## Coverage Matrix
[table from Step 2]

## Direct Overlaps (N cases)
[table from Step 3]

## Gaps: What Existing Doc Is Missing
[from Step 4]

## Additions: What Plan Should Incorporate
[from Step 4]

## Bottom Line
[from Step 5]
```
