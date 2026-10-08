# Motion Principles for UI/UX Explorations

Taste sources for proposing and demoing animation and micro-interactions, in priority order.

## Role models

1. **Emil Kowalski** (animations.dev, Sonner, Vaul; ex-Linear, ex-Vercel). Taste rules:
   - Animate only when it adds meaning: orientation, feedback, or continuity. No decoration-only motion.
   - Fast: 150-300ms for UI transitions. Never above 500ms for a common action.
   - Ease-out for most UI motion. Springs for gesture-driven or playful motion.
   - Origin-aware: an element animates from the place that triggered it (a menu grows from its button).
   - The more often an action runs, the subtler its motion.
2. **Rauno Freiberg** (Web Interface Guidelines, rauno.me craft). Micro-detail rules:
   - Respond on press, not only on release, when it makes the UI feel faster.
   - Hover, focus, and active states are designed, never browser defaults alone.
   - Optimistic UI: show the result immediately, reconcile in the background.
   - Small details compound: cursors, selection color, focus rings, overscroll.
3. **Dan Saffer** (Microinteractions). The structure for documenting each micro-interaction:
   - **Trigger**: what starts it (tap, hover, scroll, system event).
   - **Rules**: what happens, in what order.
   - **Feedback**: what the user sees, hears, or feels.
   - **Loops and modes**: what changes on repeat use or over time.

## Hard limits (aligned with the ui-patterns skill)

- Respect `prefers-reduced-motion`: every demo needs a reduced variant or no motion.
- Animate only compositor-friendly properties: `transform` and `opacity`. Never `width`, `height`, `top`, `left`, or `box-shadow`.
- Match the product's existing timing conventions before inventing new ones.

## Micro-interaction card (used in the solution artifact)

One card per key interaction:

- Name, plus the user-flow step it belongs to.
- Trigger, Rules, Feedback: one line each.
- Live demo: the interaction implemented in CSS. JS only when CSS cannot express it.
- Reference: the real app that proves the pattern, from Mobbin or the web.
