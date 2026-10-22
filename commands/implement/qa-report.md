---
description: Run the branch QA checks and write a dated, human-readable QA report file
argument-hint: [optional: --skip-automated]
allowed-tools: Read, Write, Edit, Bash, Grep, Glob, Skill, ToolSearch, AskUserQuestion, Agent, SendMessage, mcp__plugin_playwright_playwright__*, mcp__plugin_linear_linear__*, mcp__claude_ai_Slack__slack_search_public_and_private
---

Use the **qa-report** skill.

For authorized browser testing, delegate to the **vorbit:qa-runner** subagent using the skill's prepare/resume handoff. Do not execute browser flows in the parent unless the caller explicitly overrides delegation.

**Input:** $ARGUMENTS
