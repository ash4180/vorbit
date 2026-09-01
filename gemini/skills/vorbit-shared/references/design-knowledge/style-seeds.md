# Style Seeds

Ten preset style directions. Use them to turn a user's keywords ("dark and calm", "warm and playful") into starting design tokens fast. Show the closest seed to the user, confirm or mix, then refine into full tokens.

Each seed gives: palette, font pairing, radius and shadow baseline, and a motion tier.

Motion tiers used below:

- **L1** calm: hover states plus soft entrance fades only
- **L2** smooth: scroll reveals, parallax, navigation changes
- **L3** cinematic: scroll-driven timelines, pinned sections, cursor effects

---

## 1. Cream Editorial

**Keywords**: warm, editorial, magazine, restrained, paper feel
**Mood**: a well-typeset magazine spread open on screen

```
Palette:
  background #ECE7DE (warm cream)    surface #FFFFFF
  border #D5D0C7 (warm gray)         strong border #2A2A2A
  text #1A1A1A / #6B6560             accent #E8682A (orange)
Fonts:
  heading: Playfair Display (serif, 900)
  body: DM Sans (sans, 400-700)
  mono: JetBrains Mono
Radius: 16px    Shadow: hover only    Tier: L1
```

---

## 2. Dark Tech

**Keywords**: deep, neon, futuristic, tech, cyber
**Mood**: a deep-space station console, information glowing in the dark

```
Palette:
  background #0B0B0F                 surface rgba(255,255,255,0.03)
  border rgba(255,255,255,0.08)
  text #F0F0F0 / #8B8B8B             primary #00D4FF    secondary #8B5CF6
Fonts:
  heading: Space Grotesk (sans, 700)
  body: Inter (sans, 400-600)
  mono: Fira Code
Radius: 12px    Shadow: glow    Tier: L2-L3
Special: glassmorphism, flowing gradient backgrounds
```

---

## 3. Minimal Pure

**Keywords**: clean, whitespace, precise, quiet, premium
**Mood**: a single line of text on a gallery's white wall

```
Palette:
  background #FAFAFA                 surface #FFFFFF
  border #E8E8E8
  text #1A1A1A / #666666             accent #0066FF (links only)
Fonts:
  heading: Instrument Serif (serif, 400)
  body: DM Sans (sans, 400-500)
Radius: 8px    Shadow: very light    Tier: L1
Special: hierarchy built from large size contrast; no decoration
```

---

## 4. Warm Professional

**Keywords**: professional, trust, rounded, friendly, mature
**Mood**: a company that puts people at ease

```
Palette:
  background #FFFFFF                 surface #F8FAFC
  border #E2E8F0
  text #1E293B / #475569             primary #2563EB    secondary #F59E0B
Fonts:
  heading: Plus Jakarta Sans (sans, 700-800)
  body: Plus Jakarta Sans (sans, 400-500)
Radius: 12px    Shadow: soft layered    Tier: L1-L2
```

---

## 5. Playful Creative

**Keywords**: bold, fun, young, bouncy, handwritten
**Mood**: a birthday party invite made by a designer friend

```
Palette:
  background #FFF8F0                 surface #FFFFFF
  border #FFE0CC
  text #2D2D2D / #666666             primary #FF3366    secondary #FFD700    third #00CC88
Fonts:
  heading: Sora (sans, 700-800)
  body: Nunito (sans, 400-600)
  accent: Caveat (cursive, handwritten decoration)
Radius: 16-24px (large)    Shadow: colored    Tier: L2-L3
Special: blob decorations, handwritten notes, springy animation
```

---

## 6. Chinese Elegant

**Keywords**: ink, eastern, reserved, literary, whitespace
**Mood**: a letter written on rice paper

```
Palette:
  background #FAF8F5                 surface #FFFFFF
  border #E8E0D8
  text #2C2C2C / #5C5C5C             primary #C45C3C (ochre)    secondary #2C5F6E
Fonts:
  heading: Noto Serif SC (serif, 700)
  body: Noto Sans SC (sans, 400-500)
  accent: LXGW WenKai (kai script, decoration)
Radius: 4px (minimal)    Shadow: very light    Tier: L1
Special: line-height 1.8+, letter-spacing 0.02em, 800px container, 2em first-line indent
```

---

## 7. Cyberpunk

**Keywords**: glitch, grid, harsh, underground, data stream
**Mood**: neon data running inside a hacker terminal

```
Palette:
  background #0A0A0A                 surface #111111
  border #222222
  text #00FF41 / #888888             primary #FF0080    secondary #00FFFF
Fonts:
  heading: Orbitron (sans, 700-900)
  body: IBM Plex Mono (mono, 400)
Radius: 0px (all square)    Shadow: neon glow    Tier: L3
Special: glitch effects, scanlines, data-stream animation, typewriter
```

---

## 8. Organic Natural

**Keywords**: earth, handmade, soft, breathing, sustainable
**Mood**: handmade soap packaging at a country market

```
Palette:
  background #F5F0EB                 surface #FEFCF9
  border #DDD5CA
  text #3D3228 / #7A6E60             primary #5B8C5A (moss)    secondary #C4956A (clay)
Fonts:
  heading: Fraunces (serif, 600-700, optical size)
  body: Source Sans 3 (sans, 400-500)
Radius: 20px+ (round)    Shadow: warm, very soft    Tier: L1-L2
Special: hand-drawn texture backgrounds, irregular edges, soft gradients
```

---

## 9. Swiss Grid

**Keywords**: grid, rules, rational, black and white, red
**Mood**: a poster in a Bauhaus school hallway

```
Palette:
  background #FFFFFF                 surface #F5F5F5
  border #000000 (solid)
  text #000000 / #555555             accent #FF0000 (sparingly)
Fonts:
  heading: Helvetica Neue / Inter (sans, 700)
  body: Helvetica Neue / Inter (sans, 400)
Radius: 0px    Shadow: none    Tier: L1
Special: strict grid, bold rules, heavy negative space, asymmetric composition
```

---

## 10. Glassmorphism

**Keywords**: transparent, blur, light, layered, dreamy
**Mood**: sunlight falling through frosted glass onto a desk

```
Palette:
  background linear gradient #667eea to #764ba2
  surface rgba(255,255,255,0.15)
  border rgba(255,255,255,0.2)
  text #FFFFFF / rgba(255,255,255,0.7)
Fonts:
  heading: Outfit (sans, 600-700)
  body: Inter (sans, 400-500)
Radius: 16px    Shadow: large soft glow    Tier: L2
Special: backdrop-filter blur(12px), translucent layering, light animation
```

---

## Mixing rules

Users rarely match one seed exactly. Common mixes:

- "dark but restrained": Dark Tech palette + Minimal Pure motion tier and decoration rules
- "warm but fun": Warm Professional colors + Playful Creative radius and animation
- "Chinese + tech feel": Chinese Elegant fonts + Dark Tech palette
- "Swiss but modern": Swiss Grid layout and black-white + larger radius + L2 motion

When mixing, take **palette and fonts** from one seed and **motion and decoration rules** from another. Never mix two palettes.
