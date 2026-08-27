<!-- GENERATED from skills/teach/SKILL.md — edit the canonical file, then run: python3 -m vorbit_core.project_skills --write -->

# Teach Skill

Translate technical explanations into words a non-coder can act on. Simplify the wording, never the substance: every trade-off, risk, and number from the original survives, said simply.

Read and follow `../references/execution-contract.md` before starting.

## Pick the Mode

1. **No input** → find the last long or technical explanation in this conversation (usually a "why we need to change this" block) and run **Decision Card** mode on it.
2. **Pasted text or a named message** → Decision Card mode on that.
3. **A single word or short term** (e.g. `webkit`) → **Word Lesson** mode.
4. **A whole topic or question** (e.g. `how does login work`) → **Picture Lesson** mode.

## Mode 1: Decision Card

The user faced a wall of text and must decide something. Rebuild it as this exact card:

```markdown
**Problem:** [what is wrong, 1 line]
**Change:** [what will be different after, 1-2 lines]
**If we skip it:** [what breaks or stays risky, 1 line]
**Cost:** [time / money / effort, 1 line — "unknown" is allowed]
**Your decision:** [the exact question to answer, with the 2-3 possible answers]
```

Card rules:
- If the original had several risks or options, keep the count honest: name the biggest one, then say "and [N] smaller ones — ask to see them". Never silently drop any.
- Numbers survive as numbers. "About 2 hours" stays "about 2 hours".
- If no decision is actually needed, replace the last line with **What happens next:** [1 line].

## Mode 2: Word Lesson

Max 6 lines: what it is, why the user meets it, one example from their current project. One word per lesson.

## Mode 3: Picture Lesson

For a whole topic, text alone is not enough. Build one simple HTML page: big pictures, very few words.

Page rules:
- 3 to 6 panels, top to bottom. One panel is one step or one idea.
- Each panel: one big simple drawing (inline SVG) plus one caption of 10 words or less.
- The story uses the user's own project or product when possible, never an invented generic app.
- Self-contained file: no external images, fonts, or libraries.
- Captions follow the language rules below.
- Show the page the way the platform shows web pages: publish it as an artifact when the platform supports artifacts; otherwise save the file in a scratch folder outside the repo and give the user the path to open in a browser.
- Then reply in chat with 2 or 3 lines: what the page shows, plus the closing line from language rule 6.

Word Lessons and Decision Cards stay text. Make a picture page for them only when the user asks ("draw it", "show me").

## Language rules (both modes, hard limits)

1. A2 English. One idea per sentence. Max 12 words per sentence.
2. Whole chat reply fits in ~10 lines. The Picture Lesson page is separate and does not count.
3. Exactly ONE comparison, only to a design tool the user uses (Figma, components, auto-layout). No other metaphors or idioms.
4. At most one technical word kept per reply; explain it in parentheses in plain words.
5. The example comes from the user's own project or this conversation — never an invented generic app.
6. End with exactly one line: a yes/no check, the decision question, or one 1-minute try-it action.

## Follow-ups

- "more" → one level deeper, same rules, one new word max.
- "simpler" → smaller example, shorter sentences; never reuse the same sentences.
- "why" → teach the reason behind it, same rules.
- "show the rest" → list the smaller risks/options that were summarized, one line each.
- "draw it" / "show me" → turn the current card or lesson into a Picture Lesson page.

## Never

- Never do the work being explained: no project-file edits, no commands, no tickets, no Linear. The only file this skill may write is the Picture Lesson page, always outside the repo.
- Never change facts while simplifying; when unsure what the original meant, say so instead of guessing.
- Never stack topics — one card or one word per reply; offer the next as a question.
- Never say "it's simple" or "it's easy".
