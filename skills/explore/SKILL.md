---
name: explore
version: 1.6.0
description: Use when user says "explore idea", "quick exploration", "brainstorm feature", "investigate approach", or "research options". Lightweight UX/product exploration before a PRD. Block-mines references from Mobbin (and Dribbble/Pinterest via browser MCP) at multiple grains (section/pattern/component/page-archetype/flow), produces a **visual moodboard** with embedded screenshots (not text-only URLs), and saves to Notion or Anytype. Each mined block becomes a structured row that feeds /prd's component_mapping_intent. No lo-fi mockups — with a complete linked DS, lo-fi adds no value; references ground decisions in shipped evidence instead.

# Explore Skill

Quick idea exploration before PRD creation. Output stays at the UX/product level — research-only, **no Figma writes, no lo-fi mockups**. The saved document is a **visual moodboard** with embedded reference screenshots so designers can scan inspiration without chasing URLs. Saves to Notion or Anytype.

> **MCP namespace**: This skill uses `mcp__mobbin__*` for primary research and `mcp__claude-in-chrome__*` or `mcp__plugin_playwright_playwright__*` for screenshotting non-Mobbin references (Dribbble / Pinterest / arbitrary URLs). See `_shared/mcp-tool-routing.md` for the Plugin Tool Index and the announce-the-plugin rule.

> **Locate `_shared/`**: This skill ships as a plugin, so `_shared/` files live in the plugin cache, not your project. Before reading any `_shared/...` path below, run `ls -d ~/.claude/plugins/cache/local/vorbit/*/skills/_shared 2>/dev/null | head -1` and use the output as the absolute base for every `_shared/...` reference.

> **UX patterns reference**: Senior UX product designer knowledge lives in `_shared/ux-knowledge/`. When sharpening Step 4 compare-and-contrast prompts, consult `question-matrix.md` for question categories. When checking whether Step 6 options cover edge cases, consult `edge-case-catalog.md`. When user is unsure between approaches, consult `ux-philosophy.md` for decision frameworks. Read directly — no need to invoke `/vorbit:design:ux` for these lookups.

## Scope Rules

Exploration is for **UX/product direction**, not implementation. The output document MUST NOT contain frontend file paths, line numbers, LOC estimates, "PR #1 / PR #2" breakdowns, code snippets, Tailwind/CSS classes, component prop names, hex colors, or token IDs. Implementation specifics belong in `/vorbit:design:prd` or `/vorbit:implement:implement`. If they surface during exploration, capture them in a single "Follow-up questions for PRD" line and move on.

**No Figma writes, no lo-fi mockups.** With a complete linked DS available downstream, lo-fi adds no value — it would just be drawing rectangles labeled "card" when the real component is already there. References ground decisions in shipped evidence; lo-fi mockups would invent layouts that bias `/vorbit:design:figma`'s Phase 2 mapping. Keep `/explore` research-only.

## Step 1: Detect Platform & Verify Connection

Read and follow `_shared/mcp-tool-routing.md`. Discover connected save platforms (Notion or Anytype), ask the user which to use, and verify connection.

## Step 2: Scoping Batch (4 questions)

Use a single `AskUserQuestion` call with these prompts:

1. **Topic in one line** — describe the feature/problem in one sentence.
2. **Platform** — iOS / Android / Web / Multi-platform / Non-UI (backend, infra, process)
3. **Primary user** — who is the main user/persona?
4. **Prior research** — "Have you already studied competitors? If yes, name 1-3 with brief notes. If no, type 'none'."

## Step 3: Reference Research + Block-Mining — BEFORE deep questions

Research happens here so the deeper Step 4 questions can be sharpened by what shipped apps do. Beyond Mobbin's flow-level/screen-level synthesis, **mine references at multiple grains** — every reusable insight is a candidate "block" that may feed `/vorbit:design:prd`'s Component Mapping Intent.

**Block grains** (tag every block-level reference with one of these):
- `section` — a composed area like "search bar + filter chips + results list"
- `pattern` — a UI behavior, e.g. "how Linear handles bulk select"
- `component` — a specific atomic treatment, e.g. "this card with avatar + 3 action buttons"
- `page-archetype` — a whole-page structure, e.g. "list-detail layout with sidebar"
- `flow` — a multi-screen sequence

**Gate checks:**
1. **Mobbin is connected** (`ToolSearch` for `"mobbin"`). If absent, ask the user to connect via `/mcp`. If they decline, record gap and use browser MCP for direct screenshotting from Dribbble/Pinterest/etc.
2. **Non-UI topic** → skip Mobbin block-mining, go to Step 4 (still ask about prior research).
3. **Novel topic** ("nobody has built this") → say so out loud, skip to Step 4.

**Branch A — User named prior research in Step 2.**
1. Capture the named competitors and any URLs/notes into a "User-named references" subsection.
2. For each named competitor, do one targeted Mobbin search to pull clickable screen URLs **and the screenshot image URLs Mobbin returns**.
3. Identify gaps the user *didn't* mention and search only those.
4. Don't duplicate the user's work.

**Branch B — No prior research (user said 'none').** Follow `_shared/mobbin-research.md` for the full synthesis format. The minimum:

a. **Flow-pattern discovery** for multi-screen topics — present top 3 flow candidates from a flow-level Mobbin search and let the user pick one.

b. **Per-screen pattern synthesis** — 4–7 bullets per screen with app attribution and a clickable `[App](URL)` in every bullet.

c. **Block-mining pass** — for each strong pattern surfaced, ask: "is this a section, pattern, component, page-archetype, or flow?" Record it as a block with grain, source URL, screenshot URL, 1–2 sentence note, and a proposed_block_name. The proposed_block_name becomes the key in `/vorbit:design:prd`'s Component Mapping Intent. Example: `search-with-filters` (grain: `pattern`, source: Linear inbox, note: search input with inline filter chips, multi-select).

**Non-Mobbin sources (Dribbble / Pinterest / arbitrary URLs):** Use browser MCP (`mcp__claude-in-chrome__*` or `mcp__plugin_playwright_playwright__*`) to navigate and screenshot. Save the screenshot file path so Step 7 / Step 8 can embed it in the saved doc.

**Both branches end with:**

1. **URL coverage check** (`Mobbin URL coverage: [N] bullets / [M] URLs`). If N ≠ M, extract missing URLs before continuing.
2. **Screenshot coverage check** — every mined block should have a screenshot URL OR a captured screenshot path. Blocks without a visual become text-only fallbacks (record as `screenshot: missing`).
3. **Use AskUserQuestion** to ask which patterns should inform Step 4 and which blocks to keep for Step 7's moodboard.

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

Show the complete exploration document in chat using the canonical template in `./output-schema.md` (sibling of this SKILL.md). Populate every required section with content from Steps 2-6. Omit **Reference Patterns** and **Blocks Mined** when Step 3 didn't run.

In chat, screenshots are referenced by URL or file path (chat can't render embedded images). The actual embedding happens in Step 8 when the document lands in Notion or Anytype.

After showing the draft, ask: "Does this look good? Ready to save?"

## Step 8: Save Document with Embedded Screenshots

**Only proceed after user confirms the draft.**

Save using the platform selected in Step 1. Follow the "Save Content" section in `_shared/mcp-tool-routing.md`.

**Visual moodboard embedding (REQUIRED):** the saved doc must include the screenshot images inline next to each block, not just URLs. Designers think in pixels; URL-only output is designer-hostile.

- **Notion** — use `mcp__notion__notion-create-pages` with image blocks. Mobbin screenshot URLs go directly as the `url` field of an image block; locally captured Dribbble/Pinterest screenshots get uploaded (or hosted) first.
- **Anytype** — embed via the platform's image-block equivalent (check the Anytype MCP schema for the supported image-block shape).

For each mined block, the doc renders:

```
**[proposed_block_name]** · grain: [section|pattern|component|page-archetype|flow]
[embedded screenshot image]
Source: [App](URL)
Note: [1–2 sentences on what's interesting]
```

This is the structured shape `/vorbit:design:prd` consumes to seed its Component Mapping Intent section.

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
