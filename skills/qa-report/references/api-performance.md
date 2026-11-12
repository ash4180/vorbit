# Compare DEV and PROD API speed

Use this for API-backed QA flows. PROD decides API speed acceptance unless the requirement names another environment. DEV is useful for finding slow operations, but its timing alone does not decide production performance.

## Define a comparable check

- Use the PRD/plan's response-time target and measurement. Distinguish full response time from time to first byte, server processing time, and whole-page readiness; they cannot substitute for one another. With no target, record timings and `Needs decision — API speed target missing`; never invent a passing limit.
- Resolve the actual production endpoint and test access from documented project configuration or the caller. Use the same operation, method, relevant parameters, role, and comparable response size/data volume. Record the environment, request origin, network/throttling conditions, cache state when known, and timestamp. A small cached response or an authentication error cannot prove a large authenticated query is fast.
- Confirm deployment equivalence for the API behavior under test. A frontend-only change can use its unchanged production API. If the branch changes the backend operation and that change is not deployed, production is a baseline only; the changed API's speed remains unverified. State any comparison mismatch instead of claiming DEV is slower because of its environment.

## Measure and save the evidence

1. Reuse the project's existing timing tests, browser network timings, or a current production monitoring source for the exact operation. For direct requests, measure through response completion and verify the expected status and response content. A runner pass line with no duration is insufficient. Do not use a fast error response as a speed pass.
2. Follow the plan's sampling rule. If it has none, take five sequential, normal-volume requests per environment, keep every duration including the first, and report median and slowest. For a simple per-request limit, all five must meet it. Do not claim a five-request sample proves a population percentile such as p95; use the required monitoring window/sample and statistic when the target specifies one.
3. Keep PROD probes read-only and bounded. Do not point the full DEV suite at PROD or replay create/update/delete/payment operations just to measure them. For mutating operations, use available production telemetry for the matching operation, or an already-authorized test-account flow. If safe access or comparable observations are unavailable, mark the production check `Blocked` and continue other QA work.
4. Save raw samples or a durable observation link in this run's evidence folder, keyed by check ID and environment. Include method, sanitized endpoint/parameters, timestamp, sample count, metric, limit, response validation, relevant deployment version, and measurement conditions. Preserve failures/timeouts rather than discarding them and sampling until the test passes. Keep credentials and private payloads out of evidence.
5. For browser-measured flows, retain the screen recording and link the corresponding timing data. For direct API requests or monitoring, the timing log/source is the evidence; a video of a terminal is not required.

## Decide the result

| Evidence | API speed result |
|---|---|
| Equivalent PROD operation returns the expected response and meets the defined speed target; DEV is slow | **Passed — PROD verified**. Keep DEV's measured slowness as an environment note. |
| Both environments meet the target | **Passed — DEV and PROD verified**. |
| Equivalent PROD operation misses the target | **Failed** for speed; investigate and retain the observations. DEV passing cannot clear it. |
| PROD returns an unexpected status/content or errors/timeouts occur | Cannot pass; report the response failure or access blocker as applicable. |
| PROD access, samples, or comparable deployed behavior are missing | **Blocked / Not tested**, with the missing prerequisite. |
| Target or required comparison is unclear | **Needs decision**, with measurements and the unresolved point. |

This resolves API response time only. It does not clear a wrong result, broken interaction, frontend rendering delay, full-page loading target, human-only check, or missing browser recording. If an older check combines API speed and functionality, all its functional assertions still need their own evidence before the check can pass.

### When the DEV runner failed its speed assertion

Keep the collector's `status`, `qa_status`, exit code, and raw totals unchanged. A PROD resolution is a report-level assessment with additional evidence, never a fabricated green DEV run.

For each affected test, confirm that its only failure is the API-duration assertion, the target allows PROD acceptance, equivalent PROD measurements pass, and every functional assertion was actually completed successfully with the required recording. If a timeout stopped the test early, complete and record the remaining functional checks; do not infer they would pass. A flaky retry or any other unresolved failure remains a blocker.

Then label that test's assessed QA result `Passed — PROD speed verified; DEV timing failed`, linking both sets of evidence. Count it once in assessed QA totals and show raw DEV runner totals separately. In the plan, leave the failed `QP#` command unchecked with its original failure note and add `**PROD speed resolution:** [test IDs, target, evidence, functional verification]`. That command's unchecked state does not block readiness **only when every outstanding failure is accounted for by these verified speed resolutions and no other test, setup, runner, or evidence gap remains**. Never tick the failed command or remove its failure history.

## Show the comparison clearly

Example format only; replace these numbers with actual measurements:

| Check / operation | Target | DEV | PROD | QA result | Evidence |
|---|---|---|---|---|---|
| QA7 — Load customer list | Full response ≤ 500 ms for each request | 5 requests; median 2,400 ms; slowest 2,800 ms | 5 requests; median 180 ms; slowest 255 ms | Passed — PROD verified; DEV slow | [DEV timings](relative-path), [PROD timings](relative-path) |

Include deployment equivalence and measurement conditions below the table. If PROD evidence is only a baseline, say so in the result cell. Use the same result and explanation in the local report and the Notion copy.
