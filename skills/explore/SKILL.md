---
name: explore
version: 1.5.0
description: Use when user says "explore idea", "quick exploration", "brainstorm feature", "investigate approach", or "research options". Lightweight UX/product exploration before a PRD. Researches competitors via Mobbin, asks compare-and-contrast questions sharpened by what shipped apps do, drafts options + recommendation, and saves to Notion or Anytype.
---

# Explore Skill

Quick idea exploration before PRD creation. Output stays at the UX/product level. Saves to Notion or Anytype.

> **MCP namespace**: This skill uses `mcp__mobbin__*` for research. See `_shared/mcp-tool-routing.md` for the Plugin Tool Index and the announce-the-plugin rule.

> **Locate `_shared/`**: This skill ships as a plugin, so `_shared/` files live in the plugin cache, not your project. Before reading any `_shared/...` path below, run `ls -d ~/.claude/plugins/cache/local/vorbit/*/skills/_shared 2>/dev/null | head -1` and use the output as the absolute base for every `_shared/...` reference.

> **UX patterns reference**: Senior UX product designer knowledge lives in `_shared/ux-knowledge/`. When sharpening Step 4 compare-and-contrast prompts, consult `question-matrix.md` for question categories. When checking whether Step 6 options cover edge cases, consult `edge-case-catalog.md`. When user is unsure between approaches, consult `ux-philosophy.md` for decision frameworks. Read directly — no need to invoke `/vorbit:design:ux` for these lookups.

## Scope Rules

Exploration is for **UX/product direction**, not implementation. The output document MUST NOT contain frontend file paths, line numbers, LOC estimates, "PR #1 / PR #2" breakdowns, code snippets, Tailwind/CSS classes, component prop names, hex colors, or token IDs. Implementation specifics belong in `/vorbit:design:prd` or `/vorbit:implement:implement`. If they surface during exploration, capture them in a single "Follow-up questions for PRD" line and move on.

## Step 1: Detect Platform & Verify Connection

Read and follow `_shared/mcp-tool-routing.md`. Discover connected save platforms (Notion or Anytype), ask the user which to use, and verify connection.

## Step 2: Scoping Batch (4 questions)

Use a single `AskUserQuestion` call with these prompts:

1. **Topic in one line** — describe the feature/problem in one sentence.
2. **Platform** — iOS / Android / Web / Multi-platform / Non-UI (backend, infra, process)
3. **Primary user** — who is the main user/persona?
4. **Prior research** — "Have you already studied competitors? If yes, name 1-3 with brief notes. If no, type 'none'."

## Step 3: Reference Research (Mobbin) — BEFORE deep questions

Research happens here so the deeper Step 4 questions can be sharpened by what shipped apps do.

**Gate checks:**
1. **Mobbin is connected** (`ToolSearch` for `"mobbin"`). If absent, ask the user to connect via `/mcp`. If they decline, record gap and skip to Step 4.
2. **Non-UI topic** → skip Mobbin, go to Step 4.
3. **Novel topic** ("nobody has built this") → say so out loud, skip to Step 4.

**Branch A — User named prior research in Step 2.**
1. Capture the named competitors and any URLs/notes into a "User-named references" subsection.
2. For each named competitor, do one targeted Mobbin search to pull clickable screen URLs.
3. Identify gaps the user *didn't* mention and search only those.
4. Don't duplicate the user's work.

**Branch B — No prior research (user said 'none').** Follow `_shared/mobbin-research.md` for the full synthesis format. The minimum:

a. **Flow-pattern discovery** for multi-screen topics — present top 3 flow candidates from a flow-level Mobbin search and let the user pick one.

b. **Per-screen pattern synthesis** — 4–7 bullets per screen with app attribution and a clickable `[App](URL)` in every bullet.

**Both branches end with:**

1. **URL coverage check** (`Mobbin URL coverage: [N] bullets / [M] URLs`). If N ≠ M, extract missing URLs before continuing.
2. **Use AskUserQuestion** to ask which patterns should inform Step 4 and the Step 6 options.

## Step 4: Informed Questions (7-8 more)

Generate 7-8 questions specific to the topic, in batches of 3-4 via `AskUserQuestion`. Wait for each batch's answers before the next.

When Step 3 produced references, frame questions as comparisons against the patterns seen — make the user *choose* between concrete shipped patterns, not invent answers from scratch.

**Compare-and-contrast prompts** (when references exist):
- "Slack batches notifications by channel; Linear groups by project. Which model fits your team?"
- "Stripe shows errors inline next to fields; GitHub stacks them at the top. Which matches your form complexity?"

**Probe categories** (regardless of references): core functionality, scale, user control, error handling, constraints, real user scenarios.

When Step 3 was skipped, ask abstract questions but flag in the doc that references couldn't ground them.

## Step 5: Question Quota Gate

Before proceeding:
1. List every question asked across Step 2 (~4) and Step 4 (~7-8) with abbreviated answers.
2. Output: **"Questions asked: [N]/10+ (Step 2: [X], Step 4: [Y])"**
3. If N < 10 → return to Step 4 and ask more.

Non-negotiable.

## Step 6: Analyze

1. Summarize insights from all answers.
2. Identify root cause (not symptoms).
3. Propose 2-3 approaches with pros / cons / coarse effort (Low / Medium / High) / coarse risk.
4. If Step 3 produced reference patterns, weave them in — cite specific apps (e.g., "Option 1: Notion-style sidebar + project switcher").
5. Recommend the option that best addresses constraints.

## Step 7: Draft in Chat

Show the complete exploration document in chat using the canonical template in `./output-schema.md` (sibling of this SKILL.md). Populate every required section with content from Steps 2-6. Omit **Reference Patterns** when Step 3 didn't run.

After showing the draft, ask: "Does this look good? Ready to save?"

## Step 8: Save Document

**Only proceed after user confirms the draft.**

Save using the platform selected in Step 1. Follow the "Save Content" section in `_shared/mcp-tool-routing.md`.

## Step 9: Report

- URL or object ID (if saved)
- Platform used (Notion/Anytype)
- Recommended approach summary
- **Next steps** — present both, let the user pick:
  - `/vorbit:design:prd` — capture as a Linear PRD ticket.
  - `/vorbit:design:figma` — promote the direction to a hi-fi Figma mockup with real library components and Code Connect mapping.

---

# Output Schema & Validation

**See `./output-schema.md`** (sibling of this SKILL.md) for the required sections table, options format, validation rules, the markdown template the agent should populate in Step 7, and the Notion / Anytype mapping tables.
