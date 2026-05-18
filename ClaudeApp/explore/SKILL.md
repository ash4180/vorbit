---
name: explore
description: Use when user says "explore idea", "quick exploration", "brainstorm feature", "investigate approach", "research options", or wants to do lightweight idea exploration before creating a full PRD. Stays at UX/product level — no frontend file changes. Researches competitors FIRST (Mobbin), then asks informed questions sharpened by what shipped apps do. Produces lo-fi HTML wireframes for new multi-screen UI and Chrome screenshots for fine-tuning existing UI. Saves output as markdown file.
---

# Explore Skill

Quick idea exploration before PRD creation. Output stays at UX/product level. Mirrors how product owners actually work: scoping batch → competitor research (Mobbin) → informed questions sharpened by references → visual baseline → analyze → draft → save.

**Core Process:** Scoping batch → Mobbin reference research → Informed questions (7-8) → Quota gate (10+ total) → Visual baseline → Analyze options → Draft → Save.

## Flow Order — Research Before Deep Questions

This skill puts competitor research **before** the bulk of questions, on purpose. The questions you can ask without seeing references are shallow ("what triggers a notification?"); the questions you can ask after seeing references are sharp ("Slack batches notifications by channel, Linear groups by project — which model fits your team?"). Don't revert to question-first — it produces generic options.

## Scope Rules — Stay High-Level

Exploration is for **UX/product direction**, not implementation. The output document MUST NOT contain:

- Frontend file paths or file names (e.g. `src/pages/Foo.tsx`, `SettingsSidebar.tsx:143`)
- Line numbers, LOC estimates, or per-file work lists
- "PR #1 / PR #2" breakdowns or days-of-effort breakdowns
- Code snippets, Tailwind/CSS classes, specific component prop names, or i18n key planning
- Hex colors, exact spacing values, or token IDs

DO include: problem statement at product/UX level, user scenarios, Mobbin reference patterns, visual baseline (screenshot or wireframes), UX direction options with **coarse** Low / Medium / High effort and risk, recommendation at a conceptual level.

Implementation details belong in the PRD or implementation phase. If they surface here, capture as one "Follow-up questions for PRD" line and move on.

---

## Step 1: Scoping Batch (2-4 essential questions)

**Goal:** gather the minimum context needed to run Mobbin search well. Keep it tight — deeper questions come in Step 3 after research.

Use a single `AskUserQuestion` call with these 4 prompts:

1. **Topic in one line** — "Describe the feature/problem in one sentence."
2. **Platform** — iOS / Android / Web / Multi-platform / Non-UI (backend, infra, process)
3. **Primary user** — who is the main user/persona this is for?
4. **Prior research** — "Have you already studied competitors? If yes, name 1-3 with brief notes. If no, type 'none'."

The answer to #4 routes Step 2:
- User named competitors → Step 2 captures + validates those, uses Mobbin only for gaps
- User said 'none' → Step 2 runs a full Mobbin sweep

These 4 questions count toward the Step 4 quota (10+ total across Steps 1 and 3).

---

## Step 2: Reference Research (Mobbin) — BEFORE deep questions

Research happens here, before Step 3, so the deeper questions can be sharpened by what shipped apps actually do.

**Gate checks:**
1. **Mobbin is connected** (`ToolSearch` for `"mobbin"`). If absent, ask the user to connect Mobbin via `/mcp`. If they decline, record gap and skip to Step 3 with no references.
2. **Non-UI topic** (platform answer in Step 1 was "Non-UI") — skip Mobbin entirely, go to Step 3.
3. **Novel topic** ("nobody has built this") — say so out loud, skip to Step 3.

**Branch A — User named prior research in Step 1.**
1. Capture the named competitors and any URLs/notes they provided into a "User-named references" subsection.
2. For each named competitor, do one targeted Mobbin search to pull screen URLs and screenshots that match their description — this turns the user's text reference into clickable, verifiable links.
3. Identify gaps — screens or patterns the user *didn't* mention but the flow needs. Run targeted Mobbin searches for those gaps only.
4. Don't duplicate what the user already studied — respect their work.

**Branch B — No prior research (user said 'none').**

a. **Flow-pattern discovery (multi-screen topics).** For features spanning multiple connected screens, search for the whole flow first; present top 3 flow candidates and ask the user to pick one. The chosen flow anchors per-screen searches.

b. **Per-screen pattern synthesis.** For each anticipated screen, call `mcp__mobbin__search_screens({ query: "<purpose>", platform: "<ios|web>", limit: 8, mode: "deep" })`. Synthesize 4–7 bullets per screen — NOT bare result lists. Each bullet: design element + brief reason + app attribution + **clickable Mobbin URL** as `[App](URL)` so the user can verify. Distinguish "universal pattern" / "every app does this" from "X did it first" from "combines X with Y".

**Both branches end with:** ask the user which patterns should inform the deeper questions in Step 3 and the options in Step 6.

---

## Step 3: Informed Questions (7-8 more, sharpened by Step 2)

**Now** ask the deeper questions. Generate 7-8 questions specific to the topic, in batches of 3-4 via `AskUserQuestion`. Wait for each batch's answers before asking the next.

When Step 2 produced references, frame questions as comparisons against the patterns seen — not abstract probes. The goal is to make the user *choose* between concrete shipped patterns, not invent answers from scratch.

**Compare-and-contrast prompts** (when references exist):
- "Slack batches notifications by channel; Linear groups by project. Which model fits your team?"
- "Notion's sidebar uses a project switcher at top; Asana keeps projects flat. Which scales for your user count?"
- "Stripe shows errors inline next to fields; GitHub stacks them at the top. Which matches your form complexity?"

**Probe categories** (regardless of references):
- Core functionality decisions
- Scale and performance needs
- User control and preferences
- Error handling and edge cases
- Constraints (budget, time, compliance)
- User scenarios — "Describe 3 real scenarios where this matters"

**When Step 2 was skipped** (Mobbin unavailable / non-UI / novel topic): ask abstract questions, but flag in the output doc that references couldn't ground them.

**DO NOT proceed until total questions (Step 1 scoping + Step 3 informed) ≥ 10.**

---

## Step 4: Question Quota Gate

Before proceeding, you MUST:
1. List every question asked across **both** Step 1 (scoping, ~4) and Step 3 (informed, ~7-8), with the user's answer abbreviated to one line each.
2. Output: **"Questions asked: [N]/10+ (Step 1: [X], Step 3: [Y])"**
3. If N < 10 → return to Step 3 and ask more questions

This gate is non-negotiable.

---

## Step 5: Lo-fi HTML Wireframe (UI topics only)

For UI topics, **always produce a lo-fi HTML wireframe** of the proposed layout. When the topic is fine-tuning an existing page, also capture a Chrome screenshot first to ground the wireframe.

### Step 5a — As-is screenshot baseline (Mode A only: fine-tuning EXISTING UI)

1. `ToolSearch` for `"mcp__claude-in-chrome__navigate"`. If Chrome MCP isn't connected, ask the user to paste a screenshot or run `/mcp` and retry.
2. Get the URL via `AskUserQuestion` if not already named. Do NOT guess.
3. Capture: `mcp__claude-in-chrome__tabs_context_mcp` → `tabs_create_mcp` (open URL) → `read_page`.
4. Save the screenshot reference as the as-is anchor in the doc.

### Step 5b — Proposed wireframe (always for UI topics)

Generate one self-contained HTML file per screen under `./.claude/wireframes/<topic-slug>/`:

- **Mode A (fine-tune):** Usually a single `proposed.html` mirroring the screenshot structure with the change applied. Multi-page only when the fine-tune spans pages.
- **Mode B (new UI):** One file per screen + `index.html` linking them with `← Prev | Next →` nav so the user can walk the flow.

**Ensure gitignore.** Read the project's `.gitignore`. If it already excludes `.claude/` or `.claude/wireframes/`, do nothing. Otherwise append `.claude/wireframes/` (create the file if missing). Wireframes are ephemeral and must not leak into PRs.

### Step 5c — Iterate via Chrome (optional)

Open the wireframe in Chrome via `mcp__claude-in-chrome__navigate` and tell the user: "Wireframe is at `file://…`. Open it and name a labeled box (e.g. *the [Card: Recent activity] one*) and I'll update." Use `mcp__claude-in-chrome__find` to locate elements by label, then regenerate the file.

### Lo-fi rules (apply to BOTH Mode A and Mode B)

Non-negotiable. This is a wireframe, not a mockup.

- **Tailwind via CDN only:** `<script src="https://cdn.tailwindcss.com"></script>`. No build step, no custom CSS.
- **Grayscale only.** `bg-gray-*`, `text-gray-*`, `border-gray-*`. No brand colors, no hex.
- **Labeled placeholder boxes** for every UI primitive — no real shadcn components, no real copy:
  - `<div class="border rounded p-3 text-sm text-gray-600">[Button: Save]</div>`
  - `<div class="border rounded p-4">[Card: Recent activity]</div>`
- **Real layout** — flex, grid, padding — matching the screenshot (Mode A) or Mobbin reference (Mode B).
- **Labels bridge to hi-fi.** `[Button: Save]` later maps to a real `Button/Primary` library component when this wireframe is promoted to `/vorbit:design:figma`. Pick label names matching library component names.
- **No Figma MCP** in this step — Code Connect is hi-fi handoff tooling, wrong layer.

### Skip case — Non-UI topic

If the topic is backend, infra, process, or anything without a visual surface, skip Step 5 entirely. Note: "Visual Baseline: skipped (non-UI topic)".

---

## Step 6: Analyze

After gathering context:
1. Summarize insights from all question answers (Step 1 scoping + Step 3 informed)
2. Identify root cause (not symptoms)
3. Propose 2-3 approaches with pros / cons / coarse effort (Low / Medium / High) / coarse risk
4. **If Step 2 produced reference patterns**, weave them into the options — cite specific apps
5. **If Step 5 generated wireframes or captured a screenshot**, reference it from the options
6. Make recommendation addressing constraints

**Stay high-level** — re-read the Scope Rules section at the top before drafting options.

---

## Step 7: Draft in Chat

Show the complete exploration document in chat using the canonical **Template** at the bottom of this file. Populate every required section. Omit **Reference Patterns** when Step 2 didn't run; omit **Visual Baseline** when Step 5 was skipped.

**After showing the draft, ask:** "Does this look good? Ready to save?"

---

## Step 8: Save Document

**Only proceed after user confirms the draft.**

Save the exploration document as a markdown file in the user's workspace folder.

Filename format: `explore-[topic-kebab-case].md`

Link to the wireframe folder or screenshot from the doc (do not paste binary content).

---

## Step 9: Report

- File path of saved doc
- Wireframe folder path (`./.claude/wireframes/<topic-slug>/`) for UI topics
- As-is screenshot reference for Mode A
- Summary of recommended approach
- Suggest next step: "Ready to create a PRD? Just say 'create PRD for [topic]'. If the wireframe direction is confirmed and you want a committed Figma mockup with real library components, say 'figma it' to promote via `/vorbit:design:figma`."

---

# Explore Schema & Validation

## Required Sections

| Section | Required | Rules |
|---------|----------|-------|
| Context Summary | Yes | Key insights from ALL question answers |
| Problem Statement | Yes | One sentence, root cause focus |
| Reference Patterns | If Mobbin applicable | Patterns chosen in Step 2 with app attributions |
| Visual Baseline | If UI topic (Step 5 ran) | Mode A: link to Chrome screenshot. Mode B: path to wireframe folder. Mode C: explicitly note skipped. |
| Options | Yes | 2-3 approaches at UX level — NO file paths, LOC, or code |
| Recommendation | Yes | Which option and why, at UX/product level |

## Options Format

Each option must have:
- **Name**: Short descriptive name
- **How**: One sentence approach (UX-level, not implementation)
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
- If Mobbin was applicable, document includes Reference Patterns section with app attributions
- If UI topic with existing live page, Visual Baseline links to a Chrome screenshot
- If UI topic with new multi-screen flow, Visual Baseline links to the lo-fi HTML wireframe folder
- **Scope check**: document contains NO frontend file paths, line numbers, LOC estimates, PR breakdowns, code snippets, Tailwind/CSS classes, or i18n key planning. If any appear, strip them and move to a single "Follow-up questions for PRD" line.

## Template

```markdown
# Explore: [TOPIC]

## Context Summary
Key insights from conversation:
- [Answer to Q1 insight]
- [Answer to Q2 insight]
- ...
- [Answer to Q10 insight]

Constraints: [budget, timeline, compliance from follow-up]
Competitors: [existing solutions mentioned]

## Reference Patterns (when Step 2 ran)

Flow direction: [chosen flow pick, or "single-screen"]

**Screen 1 — [name]**
- [element]: [reason] ([app(s)])
- [element]: [reason] ([app(s)])

**Screen 2 — [name]**
- ...

Gaps: [screens where Mobbin returned nothing]

## Visual Baseline (when Step 5 ran)

Mode: [A — Chrome screenshot | B — Lo-fi HTML wireframes | C — Skipped]

- Mode A: URL captured: `https://…` · Screenshot reference: [link or path]
- Mode B: Wireframe folder: `./.claude/wireframes/<topic-slug>/` · Entry point: `./.claude/wireframes/<topic-slug>/index.html` · Screens: [count] · Flow order: [Screen 1 → Screen 2 → …]
- Mode C: Reason for skip: [single-screen tweak / non-UI topic]

## Problem Statement
[One sentence - what's the root cause?]

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

### Option 3: [Name]
...

## Recommendation
[Which option and why, addressing constraints]
```
