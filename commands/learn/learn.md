---
description: Explain code or teach concepts. No BS.
---

# Learn Command

## Your Task

- **Read standards:** Check `./CLAUDE.md` and `~/.claude/CLAUDE.md` for output guidelines
- **Understand input:** Parse what the user wants explained or learned
- **Project context:** How does this fit into the overall project architecture?
- **No jargon:** If a 10-year-old can't follow, simplify more
- **Step by step:** What happens first, second, third
- **Real analogies:** Compare to everyday stuff

## Output Mode

**Quick explanation** (specific code/line/concept):
- Answer inline, no file saved

**Deep dive** (broad topic, learning session):
- Save to `tools/current/learning/learn-[topic].md`
- Include "Try This" exercises

## Output Format

```
# [Topic/Code Name]

## What This Is
[One sentence: what problem does this solve?]

## Why This Matters Here
[How this fits into the project - why would you care?]

## How It Works
[Step by step breakdown - like explaining to a 10-year-old]

## Real Example
[Working code that does something useful]

## Try This (deep dive only)
[Specific next steps they can take]

## Common Mistakes
[What people get wrong + how to fix]
```
