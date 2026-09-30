<!-- GENERATED from skills/explore/SKILL.md — edit the canonical file, then run: python3 -m vorbit_core.project_skills --write -->

> Skill assets: paths like `references/...` in this workflow resolve inside the installed `vorbit-explore` skill directory (a sibling of `vorbit-shared`).

# Explore Skill

Quick idea exploration before PRD creation. Every approved exploration is saved as a dated file in the worktree's `.vorbit/explore/` folder, so later work and daily reports can find it. Notion or Anytype is an optional extra copy.

Read and follow `../references/execution-contract.md` before starting.

Read `../references/glossary.md`: use the project's `CONTEXT.md` glossary terms when it exists, and record newly agreed terms there.

## Step 1: Detect Platform & Verify Connection

Preflight required connectors: confirm each needed connector is configured in Gemini CLI and inspect its current operation/parameter schemas; never guess tool names before any external call. The local save in Step 7 always happens. Notion/Anytype is optional: discover and verify it when the user wants an extra copy there, but lack of a connection must not block questioning, analysis, or the local save.

## Step 2: Resolve the PRD-Blocking Unknowns

Ask questions via plain-text chat questions until every unknown that would block a PRD is either answered or explicitly parked as unresolved. Depth is set by the information need, not a count: a well-specified idea may need 4 targeted questions; a vague one may need 15. Size each batch to what the user can answer comfortably.

Work in rounds. Each round asks every question that is answerable now; a question whose answer depends on another question still open in the same round waits for a later round. Mark a recommended option on every question. Facts are your job, never the user's: anything discoverable from the codebase, connected tools, or the web gets looked up between rounds — ask the user only for decisions. After each round of answers, recompute what became askable.

**UI/UX asks:** anything a user sees or does: screens, flows, steps, wording, empty, error, or loading states, visual design, or interactions. When unsure, treat the ask as UI/UX. For these asks the FIRST question batch must ask: "Is this for existing code or a fresh idea?" Existing code: read the relevant screens and components before analyzing, and ground every proposal in them. Fresh idea: skip the codebase and ground proposals in reference research only.

Cover these categories, skipping any the user's request already settles:
- Core functionality decisions
- Scale and performance needs
- User control and preferences
- Error handling and edge cases
- Constraints (budget, time, compliance)
- Existing solutions / competitors and real user scenarios

Before proceeding to Step 3, list each question asked with the user's answer (one line each), then list the unknowns that remain open. Open unknowns go to the PRD Handoff's unresolved decisions — never silently fill them with assumptions.

## Step 3: Research References (required)

Every exploration gathers real evidence before analyzing. Research is never skipped, and never replaced by what you remember about products.

**UI/UX asks run both Mobbin and web search.** Neither one replaces the other:
1. Named-brand asks ("like Linear", "like Stripe"): check `../references/design-knowledge/design-systems/INDEX.md` first. When a brand file exists, read it for exact colors, fonts, and guardrails instead of guessing from screenshots.
2. Mobbin: search screens, flows, and sections for the pattern. Flows also show steps, transitions, and motion worth borrowing. Mobbin tools may need loading first and their server name varies: look them up by the name "mobbin" (connector discovery) before deciding Mobbin is not connected.
3. Web search: search how real products solve the same problem, including products Mobbin lacks, their help docs, and UX write-ups.
4. For "existing code" asks, also read the current screens and components so proposals reuse what exists.

**Other asks run web search** for how real products, docs, or write-ups handle the same problem.

**Record every search.** Keep a list of each search actually run: the tool and the search words. It goes in the document's `Sources:` line. A tool that is missing or fails is written down, for example `Mobbin: not connected`, never skipped without a word.

Fresh-idea asks with no style reference: offer the closest presets from `../references/design-knowledge/style-seeds.md` as style-direction options.

Collect per candidate pattern: app name, what it does well, any motion worth borrowing, and its proof:
- **Link (always).** The Mobbin page link (`mobbin_url`) or the web page URL where you saw it.
- **Picture (Mobbin, always).** Download the screen picture (`image_url`) into `.vorbit/explore/YYYY-MM-DD-<topic>-refs/`, named `<app>-<short-label>.png` in lowercase with dashes. Mobbin picture links are short-lived, so a saved copy is the only one that keeps showing.
- **Picture (web, when possible).** Save a screenshot the same way when a browser tool can take one. Otherwise the link alone is enough.
- A picture that could not be saved gets `_no picture: [reason]_`. Never embed a picture that was not saved.

## Step 4: Analyze

After gathering context:
1. Summarize insights from all question answers
2. Identify root cause (not symptoms)
3. Propose 2-3 approaches with pros/cons/effort/risk
4. Make recommendation addressing constraints
5. UI/UX asks: define the key animations and micro-interactions of the recommended approach, following `references/motion-principles.md` (from this skill's installed directory). Name concrete candidate effects from `../references/design-knowledge/motion-library.md` and respect its performance principles.

## Step 5: Build the Solution Page (UI/UX asks, automatic)

After analysis, build one self-contained visual HTML page presenting the recommended solution. Save it as `.vorbit/explore/YYYY-MM-DD-<topic>.html` (folder rules in Step 7), where `<topic>` is a short lowercase-hyphenated name. Do not ask permission first; this page is part of the exploration deliverable.

Build the page yourself as one self-contained HTML file, drawing the diagrams and charts with inline SVG or CSS. There is no online publishing step.

The page explains the solution with pictures, so the user understands it without reading long text:
- The user flow of the recommended approach, drawn as a step-by-step diagram.
- The options compared side by side in a visual chart or comparison graphic.
- The reference patterns from research: app name, the saved picture, and a link to the source.
- One micro-interaction card per key interaction, with a live CSS demo, using the card shape in `references/motion-principles.md` (from this skill's installed directory). Follow its role models and hard limits, including `prefers-reduced-motion`.

The page presents the solution. It is not a pixel-perfect mockup and not a PRD.

## Step 6: Draft in Chat

**Show the complete exploration document in chat for review**, using the Template in the schema section below.

**After showing draft, ask:** "Does this look good? Ready to save?"

## Step 7: Save Document

**Only proceed after user confirms the draft.**

1. **Local save (always).** Resolve the root per `../references/spec-files.md`, run its `.gitignore` guard, and write the approved document to `<root>/.vorbit/explore/YYYY-MM-DD-<topic>.md` — the same date and topic as the Step 5 page. Use today's local date. Never overwrite an earlier exploration; add `-2`, `-3` when the name is taken. Outside a git repository, ask the user for a folder instead.
2. **Extra copy (optional).** If a connected destination was selected, also save via the connected platform's current content-creation tools (inspect schemas first) and pass the exploration content as markdown body.

An exploration document is a decision input, not a PRD source of truth. Do not label it a PRD or create implementation issues from it directly. The PRD workflow imports the confirmed decisions into the branch `prd.md`.

## Step 8: Report

- Local file path of the research document
- Solution page path, plus its published link when there is one (UI/UX asks)
- URL or object ID and platform (Notion/Anytype), if the extra copy was saved
- Recommended approach summary
- Unresolved decisions to carry into PRD clarification (do not silently convert them into requirements)
- Next: `$vorbit-prd [pasted PRD Handoff or local export]` (include the exploration URL only as provenance)

---

# Explore Schema & Validation

## Validation Rules

- All Template sections present: Context Summary, Problem Statement, Options, Recommendation, PRD Handoff
- Context resolves every PRD-blocking unknown or lists it as an unresolved decision
- Problem identifies root cause, not symptoms
- 2-3 options, each with a concrete approach (not vague) and 2-3 pros/cons
- Effort and risk honestly assessed
- No option obviously superior (otherwise why explore?)
- Recommendation addresses constraints from context
- PRD Handoff separates confirmed decisions from unresolved questions
- Sources lists the real searches run: UI/UX asks need at least one Mobbin search and one web search; other asks need at least one web search. A missing tool counts only when its line says why
- Every reference pattern has a source link. Every Mobbin pattern has a saved picture or a `_no picture:` reason. Picture paths are relative to the document
- UI/UX asks only: Reference Patterns present with at least 2 real products found by those searches, and the solution page is saved in `.vorbit/explore/` and linked from the document
- The approved document is saved in `.vorbit/explore/` with the date and branch in its header

## Template

```markdown
# Explore: [TOPIC]

Date: [YYYY-MM-DD] | Branch: [branch name]
Solution page: [YYYY-MM-DD-topic.html] ([published link, if any]) (UI/UX asks only)
Sources: [each search actually run, e.g. Mobbin flows "team switcher"; web "PagerDuty all teams label"; or Mobbin: not connected]

## Context Summary
Key insights from conversation:
- [One line per resolved unknown]

Constraints: [budget, timeline, compliance from follow-up]
Competitors: [existing solutions mentioned]

## Problem Statement
[One sentence - what's the root cause?]

## Reference Patterns (UI/UX asks only)
- [App name]: [what it does well] ([link to Mobbin screen or web page])
  ![App name](YYYY-MM-DD-topic-refs/app-short-label.png)
- [App name]: [motion worth borrowing] ([link])
  _no picture: web page, no browser tool this run_

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

## PRD Handoff
**Confirmed decisions:**
- [Explicit user choice]

**Unresolved decisions:**
- [Question for PRD clarification — do not convert to a requirement]
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
