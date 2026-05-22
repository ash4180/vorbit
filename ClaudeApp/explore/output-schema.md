# Explore Output Schema & Validation (ClaudeApp)

Reference for the explore skill on Claude desktop (see SKILL.md for the imperative flow). Use this when drafting in Step 6 and validating before saving in Step 7.

## Required Sections

| Section | Required | Rules |
|---------|----------|-------|
| Context Summary | Yes | Key insights from ALL question answers (Step 1 scoping + Step 3 informed) |
| Problem Statement | Yes | One sentence, root cause focus |
| Reference Patterns | If Mobbin applicable | Patterns chosen in Step 2 with app attributions. Each bullet ends with `[App](Mobbin URL)` |
| Options | Yes | 2-3 approaches with pros/cons at UX level — NO file paths, LOC, or code |
| Recommendation | Yes | Which option and why, at UX/product level |

## Options Format

Each option must have:
- **Name**: Short descriptive name
- **How**: One sentence approach
- **Pros**: 2-3 benefits
- **Cons**: 2-3 drawbacks
- **Effort**: Low / Medium / High
- **Risk**: Low / Medium / High

## Validation Rules

- Context includes answers to 10+ questions
- Problem identifies root cause, not symptoms
- Each option has concrete approach (not vague), expressed at UX/product level
- Effort and risk honestly assessed at coarse Low / Medium / High level
- No option obviously superior (otherwise why explore?)
- Recommendation addresses constraints from context
- If Mobbin was applicable, document includes Reference Patterns section with app attributions AND every bullet has a clickable `[App](URL)` link (Mobbin returns inline images that render in your view but the saved markdown is text-only — URLs are mandatory)
- **Scope check**: document contains NO frontend file paths, line numbers, LOC estimates, PR breakdowns, code snippets, Tailwind/CSS classes, or i18n key planning.

## Template

```markdown
# Explore: [TOPIC]

## Context Summary
Key insights from conversation:
- [Answer to Q1 insight]
- ...
- [Answer to Q10 insight]

Constraints: [budget, timeline, compliance]
Competitors: [existing solutions mentioned]

## Reference Patterns (when Step 2 ran)

Flow direction: [chosen flow pick, or "single-screen"]

**Screen 1 — [name]**
- [element]: [reason] ([App](https://mobbin.com/...))
- [element]: [reason] ([App](https://mobbin.com/...))

**Screen 2 — [name]**
- ...

Gaps: [screens where Mobbin returned nothing]

## Problem Statement
[One sentence - root cause]

## Options

### Option 1: [Name]
**How**: [One sentence approach]
**Pros**:
- [Benefit 1]
- [Benefit 2]
**Cons**:
- [Drawback 1]
- [Drawback 2]
**Effort**: [Low/Medium/High]
**Risk**: [Low/Medium/High]

### Option 2: [Name]
...

## Recommendation
[Which option and why, addressing constraints]
```

## Save Format

ClaudeApp saves to local markdown file. Filename: `explore-[topic-kebab-case].md`.
