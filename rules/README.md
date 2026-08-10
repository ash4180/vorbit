# Shared Vorbit Rules (versioned copies)

These are versioned copies of the machine-level rules in `~/.vorbit/rules/`.
Codex and Gemini read that folder at run time. Claude Code reads
`.claude/rules/` instead.

Install or update on a machine:

```bash
mkdir -p ~/.vorbit/rules/universal
cp rules/universal/*.md ~/.vorbit/rules/universal/
```

After editing a rule here, copy it to `~/.vorbit/rules/` again.
