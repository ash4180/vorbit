# Vorbit Learn Workflow

Use for reviewing pending learnings and publishing durable rules.

1. Pending items live in `$VORBIT_HOME/pending/*.json`.
2. Every pending item must be reviewed before publication.
3. Scope options:
   - `agent-local`: only Codex should load it
   - `project-shared`: all agents should load it for this project
   - `universal-shared`: all agents should load it globally
4. Publish or reject via:
   - `python3 scripts/vorbit-learning.py approve <review-id> --approved-by <name>`
   - `python3 scripts/vorbit-learning.py reject <review-id> --reason <text>`
5. Never treat pending learnings as durable rules.

