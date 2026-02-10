# Review Rules

- **Layered review pipeline:** Layer 1: static analysis (biome, ruff, mypy, tsc). Layer 2: blast radius — map changed files → imports → callers. Layer 3: parallel AI agents with blast radius context. Print consolidated terminal report, don't save to file.
- **pr-review-toolkit agents:** 6 specialized agents available: code-reviewer, silent-failure-hunter, type-design-analyzer, pr-test-analyzer, comment-analyzer, code-simplifier. Orchestrate in parallel via Layer 3 of the review pipeline.
