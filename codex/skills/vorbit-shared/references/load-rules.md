# Vorbit Rule Loading

Rules are maintained manually — add `.md` files to the folders below by hand. There is no automatic capture.

Before applying any Vorbit workflow:

1. Resolve the project root with `git rev-parse --show-toplevel`, falling back to the current working directory.
2. Resolve `VORBIT_HOME`. If the env var is unset, use `~/.vorbit`.
3. Read the applicable durable rules in this order:
   - `$VORBIT_HOME/rules/universal/*.md`
   - `$VORBIT_HOME/rules/projects/<project-slug>/*.md`
   - `$VORBIT_HOME/rules/agents/codex/universal/*.md`
   - `$VORBIT_HOME/rules/agents/codex/projects/<project-slug>/*.md`

Project slug rule:
- If a project override exists in `.vorbit/config.toml`, use it.
- Otherwise derive the slug from the Vorbit config resolver.

