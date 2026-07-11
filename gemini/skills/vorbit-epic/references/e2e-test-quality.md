# E2E Test Quality

Apply these rules when writing E2E test criteria for any sub-issue, regardless of stack.

1. **Use real data shapes.** Sample the real system output before creating a fixture such as an API response, seed, file, or event payload. Never simplify a fixture from assumptions.
2. **Assert observable output.** Check what the user or downstream system sees: rendered state or navigation for UI, response and persisted state for APIs, and final files/messages/external state for scripts or services. Exit codes, logs, and intermediate variables alone are insufficient.
3. **Cover every material branch.** Happy, error, empty, and retry paths each need an E2E check when present.
4. **Make assertions non-vacuous.** Assert that a resource exists before asserting its content. A negative content assertion against a missing resource proves nothing.
5. **Exercise the integrated system.** Use real HTTP, database, and file I/O at the E2E boundary. Reserve mocked internals for unit tests.
