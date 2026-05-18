---
name: explore
version: 1.4.0
description: Use when user says "explore idea", "quick exploration", "brainstorm feature", "investigate approach", "research options", or wants to do lightweight idea exploration before creating a full PRD. Stays at UX/product level — no frontend file changes. Researches competitors FIRST (Mobbin), then asks informed questions sharpened by what shipped apps do. Produces lo-fi HTML wireframes for new multi-screen UI and Chrome screenshots for fine-tuning existing UI. Saves to Notion or Anytype.
---

# Explore Skill

Quick idea exploration before PRD creation. Output stays at the UX/product level. Supports saving to Notion or Anytype. Mirrors how product owners actually work: a small scoping batch → competitor research (Mobbin) → informed questions sharpened by references → wireframes → analyze. Includes lo-fi HTML wireframes with click-through flow for new multi-screen UI topics, and Chrome browser screenshots for fine-tuning existing UI.

## Flow Order — Research Before Deep Questions

This skill puts competitor research **before** the bulk of questions, on purpose. The questions you can ask without seeing references are shallow ("what triggers a notification?"); the questions you can ask after seeing references are sharp ("Slack batches notifications by channel, Linear groups by project — which model fits your team's workflow?"). Don't revert to question-first — it produces generic options.

## Scope Rules — Stay High-Level

Exploration is for **UX/product direction**, not implementation. The output document MUST NOT contain:

- Frontend file paths or file names (e.g. `src/pages/Foo.tsx`, `SettingsSidebar.tsx:143`)
- Line numbers, LOC estimates ("~180 LOC", "338-LOC dialog"), or per-file work lists
- "PR #1 / PR #2" breakdowns, days-of-effort breakdowns, or "files touched" sections
- Code snippets, Tailwind/CSS classes, specific component prop names, or i18n key planning
- Hex colors, exact spacing values, or token IDs

The output document DOES contain:

- Problem statement at the product/UX level
- User scenarios and pain points
- Reference patterns from Mobbin (Step 5)
- Visual baseline — screenshot or lo-fi HTML wireframes (Step 6)
- UX direction options with **coarse** pros / cons / effort (Low / Medium / High) / risk
- Recommended direction at a conceptual level

Implementation specifics belong in `/vorbit:design:prd` or `/vorbit:implement:implement`. If they surface during exploration, capture them in a single "Follow-up questions for PRD" line and move on.

## Step 1: Detect Platform & Verify Connection

Read and follow `_shared/mcp-tool-routing.md` (glob for `**/skills/_shared/mcp-tool-routing.md`). Discover connected platforms, ask user which to use, and verify connection.

## Step 2: Scoping Batch (2-4 essential questions)

**Goal:** gather the minimum context needed to run Mobbin search well. Keep it tight — deeper questions come in Step 4 after research.

Use a single `AskUserQuestion` call with these 4 prompts:

1. **Topic in one line** — "Describe the feature/problem in one sentence."
2. **Platform** — iOS / Android / Web / Multi-platform / Non-UI (backend, infra, process)
3. **Primary user** — who is the main user/persona this is for?
4. **Prior research** — "Have you already studied competitors? If yes, name 1-3 with brief notes. If no, type 'none'."

The answer to #4 routes Step 3:
- User named competitors → Step 3 captures + validates those, uses Mobbin only for gaps
- User said 'none' → Step 3 runs a full Mobbin sweep

These 4 questions count toward the Step 5 quota (10+ total across Steps 2 and 4).

## Step 3: Reference Research (Mobbin) — BEFORE deep questions

Research happens here, before Step 4, so the deeper questions can be sharpened by what shipped apps actually do.

**Gate checks:**
1. **Mobbin is connected** (`ToolSearch` for `"mobbin"`). If absent, ask the user to connect Mobbin via `/mcp`. If they decline, record as gap and skip to Step 4 with no references.
2. **Non-UI topic** (platform answer in Step 2 was "Non-UI") — skip Mobbin entirely, go to Step 4.
3. **Novel topic** ("nobody has built this") — say so out loud, skip to Step 4.

**Branch A — User named prior research in Step 2.**
1. Capture the named competitors and any URLs/notes they provided into a "User-named references" subsection.
2. For each named competitor, do one targeted Mobbin search to pull screen URLs and screenshots that match their description — this turns the user's text reference into clickable, verifiable links.
3. Identify gaps — screens or patterns the user *didn't* mention but the flow needs. Run targeted Mobbin searches for those gaps only.
4. Don't duplicate what the user already studied — respect their work.

**Branch B — No prior research (user said 'none').**

a. **Flow-pattern discovery (multi-screen topics).** For features that span multiple connected screens, search for the whole flow first via `mcp__mobbin__search_screens` with a flow-level query. Present top 3 flow candidates and use AskUserQuestion to pick one. The chosen flow anchors per-screen searches.

b. **Per-screen pattern synthesis.** For each anticipated screen/section:
`mcp__mobbin__search_screens({ query: "<purpose>", platform: "<ios|web>", limit: 8, mode: "deep" })`

Synthesize 4-7 bullets per screen — NOT bare result lists. Each bullet: design element + brief reason + app attribution + **Mobbin URL as a clickable markdown link** (`[App](URL)`). Distinguish "universal pattern" / "every app does this" from "X did it first" from "combines X with Y". The Mobbin URLs come from each search result — every claim should be backed by a clickable link so the user can verify.

**Both branches end with:** use AskUserQuestion: "Which patterns should inform the deeper questions in Step 4 and the options in Step 7?" Reference findings by number. These choices feed Step 4 (Informed Questions) and Step 7 (Analyze).

## Step 4: Informed Questions (7-8 more, sharpened by Step 3)

**Now** ask the deeper questions. Generate 7-8 questions specific to the topic, in batches of 3-4 via AskUserQuestion. Wait for each batch's answers before asking the next.

When Step 3 produced references, frame questions as comparisons against the patterns seen — not abstract probes. The goal is to make the user *choose* between concrete shipped patterns, not invent answers from scratch.

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

**When Step 3 was skipped** (Mobbin unavailable / non-UI / novel topic): ask abstract questions, but flag in the output doc that references couldn't ground them.

**DO NOT proceed until total questions (Step 2 scoping + Step 4 informed) ≥ 10.**

## Step 5: Question Quota Gate

Before proceeding to Step 6, you MUST:
1. List every question asked across **both** Step 2 (scoping, ~4) and Step 4 (informed, ~7-8), with the user's answer abbreviated to one line each.
2. Output: **"Questions asked: [N]/10+ (Step 2: [X], Step 4: [Y])"**
3. If N < 10 → use AskUserQuestion to ask more in Step 4 and update the list
4. If user declined to answer some → still counts toward quota if asked

NEVER proceed to Step 6 with fewer than 10 questions asked. This gate is non-negotiable.

## Step 6: Lo-fi HTML Wireframe (UI topics only)

For UI topics, **always produce a lo-fi HTML wireframe** of the proposed layout. When the topic is fine-tuning an existing page, also capture a Chrome screenshot first so the wireframe is grounded in what already exists, not what the agent imagines.

### Step 6a — As-is screenshot baseline (Mode A only: fine-tuning EXISTING UI)

Run this sub-step when the topic is an enhancement to a live, already-shipped page or feature.

1. **Check Chrome browser tools are connected.** `ToolSearch` for `"mcp__claude-in-chrome__navigate"`. If not connected, ask the user to paste a screenshot directly OR run `/mcp` and retry. Without a baseline, the agent will end up redesigning rather than fine-tuning.
2. **Get the URL.** Use what the user named. If unknown, **use AskUserQuestion**: "What's the URL of the page to screenshot? (staging, prod, or localhost)" — do NOT guess or invent a URL.
3. **Capture the page** using Chrome tools:
   - `mcp__claude-in-chrome__tabs_context_mcp` first (don't reuse tab IDs from prior sessions).
   - `mcp__claude-in-chrome__tabs_create_mcp` to open the URL in a new tab.
   - `mcp__claude-in-chrome__read_page` (or the screenshot tool) to capture the rendered page.
4. **Save the baseline reference** — screenshot path/URL goes into the exploration doc as the "as-is" anchor.

### Step 6b — Proposed wireframe (always for UI topics)

Generate one self-contained HTML file per screen under `./.claude/wireframes/<topic-slug>/`:

- **Mode A (fine-tune):** Usually a single `proposed.html` mirroring the screenshot's structure with the change applied. Multi-page only when the fine-tune spans pages.
- **Mode B (new UI):** One file per screen plus `index.html` linking them in flow order — `screen-01-<name>.html`, `screen-02-<name>.html`, … with `← Prev | Next →` nav so the user can walk the flow.

For both modes:

1. **Identify the screen list.** Mode A: from the screenshot. Mode B: from the Mobbin flow candidate in Step 3 (if it ran) or from user scenarios.
2. **Apply the lo-fi rules below** — non-negotiable.
3. **Save** the folder path. Mode A also references the baseline screenshot in the same folder.
4. **Ensure the wireframes folder is gitignored.** Read the project's `.gitignore`. If it already excludes `.claude/` or `.claude/wireframes/`, do nothing. Otherwise append `.claude/wireframes/` to `.gitignore` (create the file if it doesn't exist). Wireframes are ephemeral lo-fi artifacts and must not leak into PRs.

### Step 6c — Iterate via Chrome (optional)

When the user describes a change, use `mcp__claude-in-chrome__find` (or `read_page`) to locate the labeled element, then regenerate the wireframe file with the change applied.

### Lo-fi rules (apply to BOTH Mode A and Mode B)

These are non-negotiable. This is a wireframe, not a mockup.

- **Tailwind via CDN only:** `<script src="https://cdn.tailwindcss.com"></script>`. No build step, no custom CSS file.
- **Grayscale only.** Use `bg-gray-*`, `text-gray-*`, `border-gray-*`. No brand colors. No `bg-blue-500`. No hex.
- **Labeled placeholder boxes** for every UI primitive — no real shadcn components, no real copy:
  - `<div class="border rounded p-3 text-sm text-gray-600">[Button: Save]</div>`
  - `<div class="border rounded p-4">[Card: Recent activity]</div>`
  - `<div class="border rounded p-3 text-sm text-gray-500">[Input: Email address]</div>`
- **Real layout** — flex, grid, padding, spacing — matching the screenshot (Mode A) or Mobbin reference (Mode B). Structure is committed; styling is not.
- **Labels are the bridge to hi-fi.** `[Button: Save]` later maps cleanly to a real `Button/Primary` library component when this wireframe is promoted to `/vorbit:design:figma`. Pick label names that match library component names.
- **No Figma MCP** in this step — Figma Code Connect is a hi-fi handoff tool and does not belong in lo-fi. Keep wireframes as pure HTML+Tailwind generated from intent.

### Skip case — Non-UI topic

If the topic is backend, infra, process, or anything without a visual surface, skip Step 6 entirely. Note in the doc: "Visual Baseline: skipped (non-UI topic)".

## Step 7: Analyze

After gathering context:
1. Summarize insights from all question answers (Step 2 scoping + Step 4 informed)
2. Identify root cause (not symptoms)
3. Propose 2-3 approaches with pros / cons / coarse effort (Low / Medium / High) / coarse risk
4. **If Step 3 produced reference patterns**, weave them into the options — cite specific apps (e.g., "Option 1: Notion-style sidebar + project switcher")
5. **If Step 6 generated wireframes or captured a screenshot**, reference it from the options ("Option 2 matches Wireframe Screen 3" or "Option 1 keeps the current layout from the screenshot")
6. Make recommendation addressing constraints

**Stay high-level** — re-read the Scope Rules section at the top before drafting options. No file paths, no LOC, no code.

## Step 8: Draft in Chat

Show the complete exploration document in chat using the canonical **Template** at the bottom of this file (under "Explore Schema & Validation"). Populate every required section with the actual content from Steps 2–7. Omit the **Reference Patterns** section when Step 3 didn't run, and omit the **Visual Baseline** section when Step 6 was skipped (non-UI or single-screen).

**After showing the draft, ask:** "Does this look good? Ready to save?"

## Step 9: Save Document

**Only proceed after user confirms the draft.**

Save using the platform selected in Step 1. Follow the "Save Content" section in `_shared/mcp-tool-routing.md`. Pass the exploration content as markdown body. Link to the wireframe folder or screenshot from the doc (do not paste binary content into the platform body).

## Step 10: Report

- URL or object ID (if saved)
- Platform used (Notion/Anytype)
- Wireframe folder path (`./.claude/wireframes/<topic-slug>/`) for UI topics
- As-is screenshot reference for Mode A
- Recommended approach summary
- **Next steps** — present both, let the user pick:
  - `/vorbit:design:prd` — capture as a Linear PRD ticket
  - `/vorbit:design:figma` — promote the lo-fi wireframe to a hi-fi Figma mockup (real library components, Code Connect mapping). Recommended when the wireframe direction is confirmed and you want a committed design before implementation.

---

# Explore Schema & Validation

## Required Sections

| Section | Required | Rules |
|---------|----------|-------|
| Context Summary | Yes | Key insights from ALL question answers |
| Problem Statement | Yes | One sentence, root cause focus |
| Reference Patterns | If Mobbin applicable | Patterns chosen in Step 3 with app attributions |
| Visual Baseline | If UI topic (Step 6 ran) | Always: path to lo-fi HTML wireframe folder. Mode A also includes the as-is Chrome screenshot URL. Skip only for non-UI topics (note explicitly). |
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
- If Mobbin was applicable (connected + topic has shipped-app comparables), document includes Reference Patterns section with app attributions
- Every UI topic produces a lo-fi HTML wireframe folder (`./.claude/wireframes/<topic-slug>/`)
- Mode A (fine-tune existing) additionally captures a Chrome screenshot as the as-is baseline
- Mode B (new UI) wireframe folder contains `index.html` + one HTML file per screen with `← Prev | Next →` nav
- Wireframes follow the lo-fi rules: Tailwind CDN, grayscale only, labeled placeholder boxes — no real components, no real copy, no Figma MCP
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

## Reference Patterns (when Step 3 ran)

Flow direction: [chosen flow pick, or "single-screen"]

**Screen 1 — [name]**
- [element]: [reason] ([app(s)])
- [element]: [reason] ([app(s)])

**Screen 2 — [name]**
- ...

Gaps: [screens where Mobbin returned nothing]

## Visual Baseline (when Step 6 ran)

Mode: [A — Fine-tune existing | B — New UI | Skipped — non-UI]

- **Wireframe folder** (always, for UI topics): `./.claude/wireframes/<topic-slug>/`
- **As-is screenshot baseline** (Mode A only): URL captured `https://…`
- **Skipped**: reason — non-UI topic

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

## Notion Mapping

| Notion Field | Explore Field | Notes |
|--------------|---------------|-------|
| Name | Topic | title property |
| Type | `["Exploration"]` | multi_select, if exists |

Content goes in page body as markdown.

## Anytype Mapping

| Anytype Field | Explore Field | Notes |
|---------------|---------------|-------|
| name | Topic | object name |
| body | Full exploration content | markdown format |
| type_key | "page" | or custom type if available |
