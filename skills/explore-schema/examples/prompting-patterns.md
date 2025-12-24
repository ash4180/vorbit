
## Context Gathering Questions

### Scope Discovery
Ask user to validate scope:
```
"For [topic], here are the top 10 questions we should answer:
1. [Question about core functionality]
2. [Question about user needs]
3. [Question about constraints]
...
Which of these are most important? What's missing?"
```

### Context Gaps
Before proposing solutions, ask:
```
"Before I give you options, what should I know about:
- Your current setup?
- Past attempts at solving this?
- Team preferences or constraints?"
```

### Scenario Prediction
Help user think through scenarios:
```
"Here are 3 likely scenarios you'll face with [topic]:
1. [Happy path scenario]
2. [Edge case scenario]
3. [Failure scenario]
Does this match your expectations? Any scenarios I'm missing?"
```

## Perspective Simulation

### User Role Play
Simulate the end user:
```
"If I were your user, I'd ask:
- [Question about UX]
- [Question about edge cases]
- [Question about errors]
How would you answer these?"
```

### Stakeholder Questions
Anticipate stakeholder concerns:
```
"Your [manager/client/team] might ask:
- Why this approach over alternatives?
- What's the risk if this fails?
- How long until we see results?
What are your answers?"
```

## Validation Questions

### Before Proceeding
Confirm understanding:
```
"Let me confirm:
- Problem: [restate problem]
- Constraints: [restate constraints]
- Success looks like: [restate success criteria]
Is this accurate?"
```

### Trade-off Clarification
When options have trade-offs:
```
"Option A is faster but riskier. Option B is safer but slower.
Which matters more for this project: speed or safety?"
```

## Question Quality Rules

| Instead of | Ask |
|------------|-----|
| "What do you want?" | "What problem are you trying to solve?" |
| "Is this okay?" | "What concerns do you have about this approach?" |
| "Any questions?" | "What's still unclear about [specific aspect]?" |
| Open-ended dump | Specific options with trade-offs |

## When to Ask vs Proceed

**Ask when:**
- Multiple valid approaches exist
- User context is unclear
- Trade-offs require user preference
- Assumptions could be wrong

**Proceed when:**
- Requirements are explicit
- Single obvious approach
- User said "just do it"
- Following established pattern
