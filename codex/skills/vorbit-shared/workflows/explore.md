# Vorbit Explore Workflow

Use for lightweight idea exploration before PRD creation. **Stay high-level — NO frontend file paths, LOC estimates, code snippets, or PR breakdowns in the output. Those belong in `/vorbit-prd` or `/vorbit-implement`.**

> **MCP namespace**: This workflow uses `mcp__mobbin__*` for research. See `vorbit-shared/references/mcp-tool-routing.md` for the Plugin Tool Index and the announce-the-plugin rule.

**Flow order is research-first by design.** Scoping batch → Mobbin reference research → deeper questions sharpened by what shipped apps do → analyze. This matches how product owners actually work; reverting to question-first produces generic options.

1. Load Vorbit durable rules before doing anything else.
2. **Scoping batch (1 AskUserQuestion call, 4 prompts):** topic in one line / platform (iOS/Android/Web/Multi/Non-UI) / primary user / prior research (named competitors with notes, or "none"). Counts toward the 10+ quota in Step 5.
3. **Reference research (Mobbin) — BEFORE the deep questions.** Gate checks: Mobbin connected (`ToolSearch` for `"mobbin"`); non-UI topic → skip; novel topic → skip. **Branch A** (user named prior research in Step 2): capture their references, run targeted Mobbin searches per named competitor for clickable links, identify gaps and search only those. Don't duplicate their work. **Branch B** (user said "none"): flow-pattern discovery first for multi-screen topics (one Mobbin call with a flow-level query, pick top 3 candidates with user), then per-screen pattern synthesis (`mcp__mobbin__search_screens` with `limit: 8, mode: "deep"`). Output is 4–7 bullets per screen — design element + reason + app attribution + clickable Mobbin URL `[App](URL)` so user can verify (distinguish "universal" / "X did it first" / "combines X with Y"). NOT bare result lists. Both branches end with: user picks which patterns feed Step 4 and Step 6.
4. **Informed questions (7-8 more, batches of 3-4 via AskUserQuestion).** When Step 3 produced references, frame questions as compare-and-contrast against the patterns seen ("Slack batches by channel, Linear groups by project — which fits?") — not abstract probes. Probe core functionality, scale, user control, error handling, constraints, real user scenarios. When Step 3 was skipped, ask abstract questions but flag in the doc that references couldn't ground them.
5. **Question quota gate.** List every question asked across Step 2 (scoping) + Step 4 (informed) with abbreviated answers. Output: `Questions asked: [N]/10+ (Step 2: [X], Step 4: [Y])`. If N < 10, go back to Step 4 and ask more. Non-negotiable.
6. Analyze: summarize insights from all 10+ question answers, identify root cause (not symptoms), propose 2-3 approaches with coarse Low/Medium/High effort and risk, make a recommendation. If Step 3 produced reference patterns, weave them into the options — cite specific apps.
7. Draft exploration document in chat: Problem Statement, Context, **Reference Patterns** (only when Step 3 ran), Options (UX-level only — NO file paths, LOC, code), Recommendation.
8. Get user confirmation before saving.
9. Save to connected platform (Notion/Anytype) if user confirms.
10. Report: URL/ID, recommended approach. Next: `/vorbit-prd` for a Linear ticket, OR `/vorbit-figma` for a hi-fi Figma mockup with real library components when the direction is confirmed.
