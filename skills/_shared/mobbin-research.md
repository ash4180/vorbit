# Mobbin Research — Shared Synthesis Format

Reference loaded by `/vorbit:design:explore`, `/vorbit:design:figma`, and `/vorbit:design:pencil`. Each skill's SKILL.md handles when to call Mobbin and how the results feed downstream phases; this file covers the synthesis format (bullets, attribution, URL coverage) that the agent must follow.

## Per-screen synthesis (always)

For each anticipated screen, call:

```
mcp__mobbin__search_screens({ query: "<screen purpose>", platform: "<ios|web>", limit: 5-8, mode: "deep" })
```

Then **synthesize 4–7 bullets per screen** — NOT bare result lists. Each bullet:

- names a specific design element
- gives a brief reason or context
- attributes to one or more apps
- ends with a clickable Mobbin URL as `[App](URL)`

Distinguish:
- **"universal pattern"** / "every app includes this"
- **"X did it first"** (when one app is the originator)
- **"combines X with Y"** (when the pattern blends apps)

### Bullet template

```
**Screen <N> — <screen name>**
- <design element>: <brief reason or context> ([<App>](<mobbin URL>))
- <design element>: <brief reason or context> — universal pattern, e.g. [<App>](<mobbin URL>)
- <design element>: <brief reason or context> ([<App1>](<URL1>), [<App2>](<URL2>))
```

If a screen returns no usable references, write: `No Mobbin matches for <screen> — proceeding from library only.`

## URL coverage is non-negotiable

Mobbin returns inline base64 images **plus** URL metadata. The inline images may render in your client (Claude desktop renders them; Claude Code CLI usually doesn't) — **this does not substitute for URLs in the output document**. Saved exploration docs, Notion pages, and Figma mockup plans are text-only; without `[App](URL)` in every bullet, no one reading later can click through to verify.

After synthesizing, output the URL coverage check before continuing:

```
Mobbin URL coverage: [N] bullets / [M] URLs
```

If N ≠ M (any bullet missing a URL) → go back to the Mobbin response and extract URLs for each missing bullet. Don't proceed with gaps.

## Evidence rules

Every Mobbin-derived recommendation must include:

- App name.
- Screen URL or screen ID when available.
- Whether the observation is `observed directly` or `inferred`.
- Whether the pattern is `universal`, `app-specific`, or a combination of multiple apps.

**No 1:1 copying.** Extract layout, hierarchy, state behavior, and copy tone — do not copy brand styling, colors, fonts, or proprietary component details.

## Flow-pattern discovery (multi-screen topics)

For features spanning multiple connected screens (e.g. billing + plans + invoices, signup → profile → first-task), the **whole-flow pattern matters more than per-screen patterns**. Picking screens from different apps produces incoherent UX. Flow first, screens second.

Use the Mobbin capability mode recorded earlier:

- If Mobbin exposes a dedicated flow search tool, use it.
- If Mobbin only exposes screen search, use:
  `mcp__mobbin__search_screens({ query: "<full flow description>", platform: "<ios|web>", limit: 8, mode: "deep" })`
  Then group results by app, feature area, and recurring UI structure. These are **flow-pattern candidates**, not guaranteed Mobbin flow objects.

Report the top 3 candidates in chat using this format (one block per candidate):

```
**Flow Candidate <N> — <App / pattern name>**
- Fit: <why this matches the requested flow>
- Screens observed: <screen names or inferred stages>
- Strong patterns: <2-3 concrete patterns>
- Copy tone: <brief tone read>
- Evidence: <native flow metadata, or "inferred from screen results">
- Caveat: <missing screen, weak match, or none>
```

Then ask the user (via `AskUserQuestion` or in-chat prompt) which flow pattern should anchor the per-screen searches. The chosen pattern biases screen queries toward that app's conventions and copy tone.

Skip flow-pattern discovery only when the request is a single isolated screen.

## Borrow concept, use library (Figma & Pencil mockups)

When the mockup will be built against a linked design system:

- Pull the Mobbin reference for **layout, flow, and concept** — hierarchy, density, section order, copy register.
- Build the actual mockup using **our linked library components and variables**. Never copy Mobbin's colors, fonts, or specific components.
- If the Mobbin concept needs an element our library doesn't have, **never invent primitives in the main mockup**. Either:
  - **Add to library** (Phase 4A work; skip the element from this mockup until added), or
  - Create a **sibling reference frame** named `[Reference / Gap] <element name>` next to the mockup showing what's needed, so the gap is visible without polluting the mockup.

The user picks next steps from there.
