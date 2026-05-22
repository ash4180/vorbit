---
name: explore
description: Use when user says "explore idea", "quick exploration", "brainstorm feature", "investigate approach", or "research options". Lightweight UX/product exploration before a PRD. Researches competitors via Mobbin, asks compare-and-contrast questions sharpened by what shipped apps do, drafts options + recommendation, and saves as a markdown file.
---

# Explore Skill

Quick idea exploration before PRD creation. Output stays at the UX/product level. Saves as a markdown file in the user's workspace.

**Core Process:** Scoping batch → Mobbin reference research → Informed questions (7-8) → Quota gate (10+ total) → Analyze options → Draft → Save.

> **MCP namespace**: `mcp__mobbin__*` (research, required). Announce the plugin+tool in chat once per session on the first MCP call (e.g. "Using `mcp__mobbin__search_screens` to research notification patterns"). Re-announce only when the namespace prefix changes.

## Scope Rules

Exploration is for **UX/product direction**, not implementation. The output document MUST NOT contain frontend file paths, line numbers, LOC estimates, "PR #1 / PR #2" breakdowns, code snippets, Tailwind/CSS classes, component prop names, hex colors, or token IDs. Implementation details belong in the PRD or implementation phase. If they surface here, capture as one "Follow-up questions for PRD" line and move on.

---

## Step 1: Scoping Batch (4 questions)

Use a single `AskUserQuestion` call with these prompts:

1. **Topic in one line** — describe the feature/problem in one sentence.
2. **Platform** — iOS / Android / Web / Multi-platform / Non-UI (backend, infra, process)
3. **Primary user** — who is the main user/persona?
4. **Prior research** — "Have you already studied competitors? If yes, name 1-3 with brief notes. If no, type 'none'."

Answer #4 routes Step 2 (named competitors → targeted Mobbin search; 'none' → full sweep). These 4 questions count toward the Step 4 quota.

---

## Step 2: Reference Research (Mobbin) — BEFORE deep questions

Research happens here so the deeper Step 3 questions can be sharpened by what shipped apps do.

**Gate checks:**
1. **Mobbin is connected** (`ToolSearch` for `"mobbin"`). If absent, ask the user to connect via `/mcp`. If they decline, record gap and skip to Step 3.
2. **Non-UI topic** → skip Mobbin, go to Step 3.
3. **Novel topic** ("nobody has built this") → say so out loud, skip to Step 3.

**Branch A — User named prior research in Step 1.**
1. Capture the named competitors and any URLs/notes into a "User-named references" subsection.
2. For each named competitor, do one targeted Mobbin search to pull clickable screen URLs.
3. Identify gaps the user *didn't* mention and search only those.
4. Don't duplicate the user's work.

**Branch B — No prior research (user said 'none').** Follow the synthesis format documented in the shared Mobbin reference. The minimum:

a. **Flow-pattern discovery** for multi-screen topics — present top 3 flow candidates from a flow-level Mobbin search and ask the user to pick one.

b. **Per-screen pattern synthesis** — `mcp__mobbin__search_screens({ query: "<purpose>", platform: "<ios|web>", limit: 8, mode: "deep" })`. Output 4–7 bullets per screen with app attribution and a clickable `[App](URL)` in every bullet. Distinguish "universal pattern" / "X did it first" / "combines X with Y".

**Both branches end with:**

1. **URL coverage check** (`Mobbin URL coverage: [N] bullets / [M] URLs`). If N ≠ M, extract missing URLs before continuing.
2. **Ask the user** which patterns should inform Step 3 and the Step 5 options.

---

## Step 3: Informed Questions (7-8 more)

Generate 7-8 questions specific to the topic, in batches of 3-4 via `AskUserQuestion`. Wait for each batch's answers before the next.

When Step 2 produced references, frame questions as comparisons against the patterns seen — make the user *choose* between concrete shipped patterns, not invent answers from scratch.

**Compare-and-contrast prompts** (when references exist):
- "Slack batches notifications by channel; Linear groups by project. Which model fits your team?"
- "Stripe shows errors inline next to fields; GitHub stacks them at the top. Which matches your form complexity?"

**Probe categories** (regardless of references): core functionality, scale, user control, error handling, constraints, real user scenarios.

When Step 2 was skipped, ask abstract questions but flag in the doc that references couldn't ground them.

---

## Step 4: Question Quota Gate

Before proceeding:
1. List every question asked across Step 1 (~4) and Step 3 (~7-8) with abbreviated answers.
2. Output: **"Questions asked: [N]/10+ (Step 1: [X], Step 3: [Y])"**
3. If N < 10 → return to Step 3 and ask more.

Non-negotiable.

---

## Step 5: Analyze

1. Summarize insights from all answers.
2. Identify root cause (not symptoms).
3. Propose 2-3 approaches with pros / cons / coarse effort (Low / Medium / High) / coarse risk.
4. If Step 2 produced reference patterns, weave them in — cite specific apps.
5. Recommend the option that best addresses constraints.

---

## Step 6: Draft in Chat

Show the complete exploration document in chat using the canonical template in `./output-schema.md` (sibling of this SKILL.md). Populate every required section. Omit **Reference Patterns** when Step 2 didn't run.

After showing the draft, ask: "Does this look good? Ready to save?"

---

## Step 7: Save Document

**Only proceed after user confirms the draft.**

Save the exploration document as a markdown file in the user's workspace folder.

Filename format: `explore-[topic-kebab-case].md`

---

## Step 8: Report

- File path of saved doc
- Summary of recommended approach
- Suggest next step: "Ready to create a PRD? Just say 'create PRD for [topic]'. If the direction is confirmed and you want a committed Figma mockup with real library components, say 'figma it' to promote via `/vorbit:design:figma`."

---

# Output Schema & Validation

**See `./output-schema.md`** (sibling of this SKILL.md) for required sections, options format, validation rules, and the markdown template the agent should populate in Step 6.
