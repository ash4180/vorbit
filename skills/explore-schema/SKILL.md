---
name: explore-schema
description: Structure for exploration documents. Use when creating explorations or validating explore output format.
---

# Explore Schema

Structure for quick idea exploration before PRD creation.

## Context Gathering

Use **AskUserQuestion** tool to gather context conversationally:

1. **Generate 10 questions** specific to the topic and present them to user
   - Questions should probe key decisions, trade-offs, and unknowns
   - Let user answer or add their own questions

2. **Competitors** - Who are the main competitors or existing solutions?

3. **User scenarios** - What are 3 real scenarios users will face?

4. **Constraints** - Budget, timeline, or technical limitations?

## Required Sections

1. **Context Summary** - Key insights from conversation
   - What we learned from the 10 questions
   - Constraints identified

2. **Problem Statement** - One sentence, root cause focus

3. **Options** (2-3 approaches)
   - Name
   - How (one sentence)
   - Pros/Cons
   - Effort: Low/Medium/High
   - Risk: Low/Medium/High

4. **Recommendation** - Which option and why

## Validation Rules

- Context captures user inputs and constraints
- Problem identifies root cause, not symptoms
- Each option has concrete approach
- Effort and risk honestly assessed
- Decision rationale addresses constraints
- No option obviously superior (otherwise why explore?)

## Output Format

For template structure, see [references/template.md](references/template.md).

## Examples

- [prompting-patterns.md](examples/prompting-patterns.md) - How to ask better questions
