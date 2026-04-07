---
description: Inspect Vorbit's canonical pending learning queue and review items before publication
argument-hint: "[optional: project name | approve all]"
allowed-tools: Read, Write, Edit, Grep, Glob, AskUserQuestion
---

Use the **learn** skill to inspect and process pending learnings.

1. Resolve the Vorbit store root (`VORBIT_HOME`, then `~/.vorbit/config.toml`, then `~/.vorbit`)
2. Check `pending/*.json` for pending review items
3. If nothing is pending → output "Nothing to process." and stop
4. For each pending item: inspect the proposed scope, rule, destination, and source agent
5. Require explicit approval or rejection before publishing anything durable

**Input:** $ARGUMENTS
