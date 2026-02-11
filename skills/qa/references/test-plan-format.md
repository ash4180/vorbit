# Test Plan Format Reference

## Test Type Taxonomy

| Type | Meaning | When to Use |
|---|---|---|
| **Smoke** | "Does it turn on?" — page loads, critical elements visible | Every page/route gets at least one |
| **Functional** | A specific feature works correctly | Interactive elements: filters, dropdowns, forms, sorting, pagination |
| **E2E** | Full user flow, start to finish | Create → edit → delete; full lifecycle flows |
| **Edge Case** | Unusual inputs, boundary conditions, race conditions | Concurrency, empty states, bulk operations, timezone issues, DST, invalid input |
| **Validation** | Data integrity and format enforcement | Required fields, email format, numeric ranges, data accuracy |
| **Security** | Authentication, authorization, permissions | Auth redirects, RBAC, token expiry, unauthorized access |
| **Performance** | Speed, scale, responsiveness under load | Large datasets (1000+ rows), slow network, many concurrent users |
| **Regression** | Known bug that must stay fixed | Reference the original bug ID or description |
| **Integration** | External service connections | OAuth flows, webhooks, Slack/email notifications, API connections |
| **Content** | Correct data renders in correct sections | All subsections present, data matches source |

## Priority Tiers

| Tier | Criteria | Depth Target |
|---|---|---|
| **P0** | Core business flows — the reason users open the app | 15-30 test cases per area |
| **P1** | Important supporting features — users need these regularly | 8-15 test cases per area |
| **P2** | Secondary features — configuration, analytics, settings | 5-10 test cases per area |

## Test Case Table Format (Notion)

Each feature area uses tables with this structure:

```
<table fit-page-width="true" header-row="true">
<tr color="blue_bg">
<td>**#**</td>
<td>**Test Case**</td>
<td>**Expected Behavior**</td>
<td>**Type**</td>
</tr>
<tr>
<td>[PREFIX]-[NN]</td>
<td>[Short action description]</td>
<td>[What should happen — specific, testable, no ambiguity]</td>
<td>[Type from taxonomy]</td>
</tr>
</table>
```

### ID Prefixes

Use 2-3 letter prefixes per feature area. Examples:

| Area | Prefix | Example |
|---|---|---|
| Incident Management | IM | IM-01, IM-02 |
| Incident Detail | ID | ID-01, ID-02 |
| Incident Lifecycle | IL | IL-01, IL-02 |
| Alerts | AL | AL-01, AL-02 |
| Alert Detail | AD | AD-01, AD-02 |
| On-Call | OC | OC-01, OC-02 |
| Escalation Policy | EP | EP-01, EP-02 |
| Navigation | NV | NV-01, NV-02 |
| Authentication | AU | AU-01, AU-02 |

Use 2-digit zero-padded numbers (01, 02... 99).

## Notion Page Structure

```
<callout icon="icon" color="blue_bg">
  **QA Test Plan** for [project]. **N test cases** across M feature areas
  with edge cases, concurrency, permissions, and performance scenarios.
  Validated against [env] on [date].
</callout>
<table_of_contents/>
---
# 1. [Feature Area] (P0)
## 1.1 [Sub-area] (`/route`)
[test case table]
## 1.2 [Sub-area] (`/route`)
[test case table]
---
# 2. [Feature Area] (P0)
[tables]
---
...
# N. Known Issues to Verify
<callout icon="bug" color="red_bg">
  [numbered list of known bugs found during validation]
</callout>
---
<callout icon="chart" color="gray_bg">
  **Total: X test cases** | Smoke: N | Functional: N | E2E: N | Edge Case: N | ...
  **Coverage**: M feature areas | **Priority**: P0 (...) > P1 (...) > P2 (...)
</callout>
```

## Writing Good Test Cases

### Expected Behavior Rules

1. **Be specific** — "Table shows 10 rows with pagination showing total count" not "Table works"
2. **Be testable** — A tester should know exactly what to verify
3. **Include edge states** — "If empty, shows 'No data' message" not just "Shows data"
4. **Note known bugs** — Bold + inline reference: "**Known bug: breadcrumb shows wrong page name.**"
5. **Include data** — "Options show SEV0-SEV6" not just "Dropdown works"

### Edge Case Categories to Always Consider

| Category | Examples |
|---|---|
| **Empty state** | No data, first-time user, no config |
| **Boundary values** | 0 items, 1 item, max items, page size boundary |
| **Invalid input** | Special characters, XSS attempts, SQL injection, empty strings |
| **Concurrency** | Two users editing same record, race conditions on status change |
| **Permissions** | Unauthorized user, wrong role, deactivated user |
| **Bulk operations** | Select all, bulk delete, bulk update |
| **Real-time** | Changes from other sessions, WebSocket disconnection |
| **Network** | Slow response, timeout, API error during form submit |
| **State transitions** | Invalid transitions (e.g., closed → acknowledged), double-click prevention |
| **Timezone/locale** | DST transitions, date format per locale, UTC vs local |
| **Cascade effects** | Delete entity with dependencies, deactivate user with active assignments |
| **Duplicate handling** | Duplicate names, re-inviting existing member, overlapping schedules |
