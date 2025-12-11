# Brainstorm: [TOPIC]

## 0. Context Questions (Fill this section, then run `/init:explore [topic]` again)

**Scope check:** What are the top 10 questions I should be asking for this project?
> Agent should LIST 10 specific questions here based on the topic.

**Context gap:** What should I know before giving you the best answer?
> Replace with specific context questions the agent identifies as gaps.

**Scenario planning:** What are the 3 most likely scenarios you'll face?
> Agent should propose 3 scenarios, user confirms/adjusts.

**Constraints:** Any budget, timeline, or technical limitations?
> This one is okay as-is, it's a direct question.

---

## 1. Context Summary (Agent fills after reading your answers)
**Key insights:** [Extracted from user answers above]
**Constraints identified:** [Budget, timeline, technical limitations from answers]

## 2. What's the problem?
[One sentence. What's broken? Focus on root cause, not symptoms.]

## 3. What are 2-3 ways to solve it?

### Option 1: [NAME]
How: [One sentence describing approach]
Pros: [Main benefit]
Cons: [Main drawback] 
Effort: [Low/Medium/High]
Risk: [Low/Medium/High]

### Option 2: [NAME]
How: [One sentence describing approach]
Pros: [Main benefit]
Cons: [Main drawback]
Effort: [Low/Medium/High]
Risk: [Low/Medium/High]

### Option 3: [NAME] (optional)
How: [One sentence describing approach]
Pros: [Main benefit]
Cons: [Main drawback]
Effort: [Low/Medium/High]
Risk: [Low/Medium/High]

## 4. Which one should we build?
[Which option and why? Consider effort vs impact, risk tolerance, and project constraints.]

## Validation Checklist
- [ ] Context section captures key user inputs and constraints
- [ ] Problem clearly identifies root cause
- [ ] Each option has concrete implementation approach
- [ ] Effort and risk honestly assessed
- [ ] Decision rationale addresses project constraints
- [ ] No option is obviously superior (otherwise why explore?)

---
Ready for PRD? Run: `/init:prd @local/current/docs/explore-[topic].md`