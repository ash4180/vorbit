---
name: writing
description: Use when user asks to "write a blog post", "create an article", "draft content", "write about [topic]", "help me write", "content writing", "long-form writing", or wants to create blog posts, articles, or other long-form written content. Guides through structured questioning to produce high-quality, audience-focused content.
---

# Writing Skill

Create high-quality blog posts and articles through structured questioning. Every piece is tailored to the audience and purpose.

**Key Principle:** Understand audience first → Plan structure → Write with clear purpose → Review and refine.

---

## Step 1: Understand the Writing Task

Use `AskUserQuestion` to gather context (ask 2-4 questions per batch):

### Batch 1: Topic & Purpose
- "What topic should this piece cover?"
- "What's the main goal? (Educate, persuade, entertain, inform)"
- "What's the key takeaway you want readers to remember?"

### Batch 2: Audience
- "Who is the target reader? (Beginners, experts, general public)"
- "What does the reader already know about this topic?"
- "What problem does the reader have that this solves?"

### Batch 3: Format & Style
- "How long should it be? (500, 1000, 2000+ words)"
- "What tone? (Professional, casual, conversational, formal)"
- "Any specific style guidelines or brand voice to follow?"

### Batch 4: Details
- "Any key points that MUST be included?"
- "Any sources, data, or examples to reference?"
- "Anything to avoid mentioning?"

**DO NOT start writing until you have clear answers.**

---

## Step 2: Create Outline

Based on answers, create a structured outline:

```markdown
## Outline: [Title]

**Hook:** [Opening approach - question, stat, story, problem]

**Sections:**
1. [Section 1 title] - [What it covers]
2. [Section 2 title] - [What it covers]
3. [Section 3 title] - [What it covers]

**Key Points:**
- [Must-include point 1]
- [Must-include point 2]

**Conclusion:** [How to end - CTA, summary, question]

**Estimated length:** X words
```

Ask: "Does this outline look good? Any sections to add, remove, or reorder?"

**Get approval before writing.**

---

## Step 3: Write the Draft

Follow these writing principles:

### Opening (Hook)
- Start with something that grabs attention
- Options: surprising fact, question, story, bold statement, problem statement
- Avoid generic intros ("In today's world...")

### Body Sections
- One main idea per section
- Use clear topic sentences
- Include examples, data, or stories to support points
- Keep paragraphs short (3-5 sentences)
- Use transition words between sections

### Language
- Match the agreed tone
- Use active voice
- Avoid jargon unless audience expects it
- Explain technical terms when needed
- Keep sentences varied in length

### Conclusion
- Summarize key takeaways
- Include call-to-action if appropriate
- End with something memorable

---

## Step 4: Review Checklist

Before presenting the draft, verify:

**Content:**
- [ ] Addresses the target audience
- [ ] Achieves the stated purpose
- [ ] Includes all required key points
- [ ] Avoids excluded topics

**Structure:**
- [ ] Has clear hook
- [ ] Logical flow between sections
- [ ] Each section has one main idea
- [ ] Strong conclusion

**Style:**
- [ ] Matches requested tone
- [ ] Appropriate reading level for audience
- [ ] Active voice (mostly)
- [ ] No unnecessary jargon

**Length:**
- [ ] Within requested word count (±10%)

---

## Step 5: Present Draft

Show the complete draft to user in chat.

After the draft, ask:
- "What do you think of the draft?"
- "Any sections to expand, shorten, or change?"
- "Any tone adjustments needed?"

---

## Step 6: Revise

Based on feedback:
1. Make requested changes
2. Show revised version
3. Repeat until user is satisfied

---

## Step 7: Save Document

**Only after user approves final version.**

Save as markdown file in user's workspace folder.

Filename format: `[title-kebab-case].md`

---

## Step 8: Report

```
## Article Complete

**File:** [link to saved file]

### Summary
- Title: [title]
- Word count: X
- Sections: Y

### Ready for:
- Publishing to blog
- Further editing
- Conversion to other formats
```

---

## Writing Reference Guide

### Opening Hooks by Type

| Type | Example | Best For |
|------|---------|----------|
| Question | "Ever wondered why..." | Engaging curiosity |
| Statistic | "80% of users..." | Building credibility |
| Story | "Last week, I..." | Creating connection |
| Bold claim | "Everything you know about X is wrong" | Grabbing attention |
| Problem | "If you struggle with X..." | Addressing pain points |

### Tone Guidelines

| Tone | Characteristics | Avoid |
|------|-----------------|-------|
| **Professional** | Clear, authoritative, well-structured | Slang, emojis, casual phrases |
| **Casual** | Friendly, relaxed, conversational | Stiff language, complex sentences |
| **Conversational** | Like talking to a friend, uses "you" | Formal words, passive voice |
| **Formal** | Academic, precise, well-cited | Contractions, colloquialisms |

### Word Count Guide

| Length | Best For | Structure |
|--------|----------|-----------|
| 500 words | Quick tips, news updates | Hook + 2-3 points + conclusion |
| 1000 words | How-to guides, opinions | Hook + 4-5 sections + conclusion |
| 2000+ words | Deep dives, tutorials | Hook + 6+ sections + examples + conclusion |

### Common Mistakes to Avoid

- Starting with "In today's fast-paced world..."
- Ending with "In conclusion, we have seen that..."
- Using passive voice throughout
- Writing walls of text without breaks
- Forgetting the target audience mid-article
- No clear takeaway for the reader
