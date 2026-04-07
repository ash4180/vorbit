# Vorbit Rule Loading

Before applying any Vorbit workflow:

1. Resolve the project root with `git rev-parse --show-toplevel`, falling back to the current working directory.
2. Resolve `VORBIT_HOME`. If the env var is unset, use `~/.vorbit`.
3. Read the applicable durable rules in this order:
   - `$VORBIT_HOME/rules/universal/*.md`
   - `$VORBIT_HOME/rules/projects/<project-slug>/*.md`
   - `$VORBIT_HOME/rules/agents/codex/universal/*.md`
   - `$VORBIT_HOME/rules/agents/codex/projects/<project-slug>/*.md`
4. If the repo contains the Vorbit helper script, you may render the bundle instead:
   - `python3 scripts/vorbit-learning.py rules --agent codex --project-root <project-root>`
5. Pending learnings in `$VORBIT_HOME/pending/*.json` are review items only. Do not treat them as durable rules.

Project slug rule:
- If a project override exists in `.vorbit/config.toml`, use it.
- Otherwise derive the slug from the Vorbit config resolver.

