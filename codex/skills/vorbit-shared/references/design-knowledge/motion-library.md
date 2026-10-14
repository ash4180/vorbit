# Motion Library: vue-bits / reactbits

A catalog of ready-made web motion effects. Source: [vue-bits](https://github.com/DavidHDev/vue-bits) and [react-bits](https://github.com/DavidHDev/react-bits) by DavidHDev (same author, same effects for Vue and React, MIT license). **Reuse before rewriting.**

Motion tiers referenced below (same scale as `style-seeds.md`):

- **L1** calm: hover states plus soft entrance fades only
- **L2** smooth: scroll reveals, parallax, navigation changes
- **L3** cinematic: scroll-driven timelines, pinned sections, cursor effects

When the target project is plain HTML, port by the effect's own stack:

- CSS-only effect: copy the class + keyframes directly
- GSAP-driven: copy the logic (GSAP is framework-agnostic)
- Three.js / OGL driven: copy the canvas init logic
- Deeply tied to Vue/React lifecycle: extract an `init()` / `destroy()` function pair

---

## Baseline for L2+ pages

A page at tier L2 or above should include all 6 effect categories below. Missing one means the motion design is incomplete:

| Category | Minimum | Suggested placement |
|----------|---------|---------------------|
| Text animation, hero H1 | 1 | First-screen headline (entrance or persistent) |
| Text animation, section H2 | 1 | Section titles (scroll-triggered) |
| Text animation, body / label | 1 | Body text, eyebrow, code lines |
| Animation, element level | 1+ | Button magnet, card hover, cursor, decoration |
| Component, interactive | 1+ | Card stacks, galleries, menus, 3D cards |
| Background, atmosphere | 1 | Hero background or section underlay |

Aim for at least 4 signature moments per page. L3 pages: 6 to 8, never more than 10 (it gets noisy).

---

## Catalog (as of 2026-04)

### Text Animations (24)

| Name | One line | Fits | Tags |
|------|----------|------|------|
| ASCIIText | Text rebuilt from ASCII characters | Tech feel, terminal style | heavy, decorative |
| BlurText | Characters blur in one by one | General entrances | light, elegant |
| CircularText | Text laid on a circular path | Logo rings, badges | light, decorative |
| CountUp | Numbers roll up to a target value | Stats, KPIs | light, functional |
| CurvedLoop | Text flows in a loop along a curve | Marquees, quotes | light, decorative |
| DecryptedText | Scrambled characters decode to real text | Tech or crypto taglines | medium, tech |
| FallingText | Text falls and resettles with physics | Highlight paragraph decoration | heavy, playful |
| FuzzyText | Text trembles with noise | Glitch art | heavy, decorative |
| GlitchText | Glitch offsets plus color split | Cyberpunk | heavy, stylized |
| GradientText | Gradient-filled text (can flow) | Keywords, logos | light, general |
| RotatingText | Words cycle in place (typewriter alternative) | Hero verb cycling | light, functional |
| ScrambleText | Characters scramble then settle | Tech or docs eyebrows | light, tech |
| **ScrollFloat** | Floats in with scroll, holds exact position | **First pick for section H2** | light, general |
| **ScrollReveal** | Words or lines appear one by one on scroll | **First pick for body text** | light, general |
| ScrollVelocity | Text speed follows scroll speed | Decorative bands, parallax | medium, decorative |
| ShinyText | Metallic shine sweeps across text | CTAs, key taglines | light, brand |
| Shuffle | Characters shuffle positions | Transitions | medium, playful |
| **SplitText** | Characters, words, or lines stagger in | **First pick for hero H1** | light, classic |
| TextCursor | Cursor typing effect | Terminal feel, guidance copy | light, functional |
| TextPressure | Font weight follows mouse distance | Interactive hero titles | medium, experimental |
| TextTrail | Characters leave a visual trail | Parallax decoration | medium, decorative |
| TextType | Typewriter, character by character | Code blocks, command lines | light, functional |
| TrueFocus | Focus word sharp, the rest blurred | Guides the reader's eye | medium, functional |
| VariableProximity | Font gets bolder near the mouse | Variable font showcases | medium, experimental |

### Animations, element level (29)

| Name | One line | Tags |
|------|----------|------|
| AnimatedContent | General entrances (fade, slide, scale) | light, general |
| Antigravity | Elements push away as the mouse nears | medium, experimental |
| BlobCursor | Cursor becomes a morphing blob | medium, decorative |
| ClickSpark | Particles burst on click | light, feedback |
| Crosshair | Crosshair cursor | medium, experimental |
| Cubes | 3D cube grid self-rotating | heavy, decorative |
| ElectricBorder | Electric glow running along borders | medium, brand |
| FadeContent | Simple fade in | light, basic |
| GhostCursor | Cursor with a trailing ghost | light, decorative |
| GlareHover | Highlight sweeps a card on hover | light, brand |
| GradualBlur | Progressive blur | light, transition |
| ImageTrail | Mouse drags an image trail | heavy, playful |
| LaserFlow | Flowing laser lines | heavy, decorative |
| LogoLoop | Brand logos scroll in an endless band | light, functional |
| MagicRings | Decorative light rings | medium, decorative |
| **Magnet** | Element pulls toward the mouse | **First pick for CTAs** (light) |
| MagnetLines | Magnetic field line decoration | medium, decorative |
| MetaBalls | Fluid merging balls | heavy, decorative |
| MetallicPaint | Metallic paint sheen | medium, brand |
| Noise | Noise texture | light, base layer |
| OrbitImages | Images orbiting a center | medium, decorative |
| PixelTrail | Pixelated mouse trail | medium, stylized |
| PixelTransition | Pixelated transition | medium, transition |
| Ribbons | Floating ribbons | medium, decorative |
| ShapeBlur | Animated blurred shapes | medium, decorative |
| SplashCursor | Splash on mouse move | heavy, playful |
| StarBorder | Star points flowing along borders | medium, brand |
| StickerPeel | Sticker corner peel | medium, playful |
| TargetCursor | Targeting reticle cursor | medium, experimental |

### Components, interactive (30+)

| Name | One line | Tags |
|------|----------|------|
| AnimatedList | List items animate in | light, general |
| BorderGlow | Border glow that tracks the mouse | medium, brand |
| BounceCards | Cards spring open | medium, playful |
| BubbleMenu | Bubble menu | medium, playful |
| CardNav | Card-style navigation | light, general |
| **CardSwap** | Cards swap in a 3D stack | **First pick for hero card showcases** |
| Carousel | Basic carousel | light, general |
| ChromaGrid | Chromatic aberration grid | medium, stylized |
| CircularGallery | Circular gallery | medium, decorative |
| Counter | Animated counter | light, functional |
| DecayCard | Decaying card animation | medium, decorative |
| Dock | macOS-style dock | light, functional |
| DomeGallery | Spherical gallery | heavy, decorative |
| ElasticSlider | Elastic slider | light, functional |
| FlowingMenu | Flowing menu | medium, decorative |
| FlyingPosters | Posters flying through space | heavy, playful |
| Folder | Folder open animation | light, playful |
| GlassIcons | Glass icons | light, decorative |
| GlassSurface | Glass surface | medium, decorative |
| GooeyNav | Gooey navigation | medium, playful |
| InfiniteMenu | Infinite menu | medium, decorative |
| **InfiniteScroll** | Endless horizontal or vertical showcase band | **First pick for showcases** |
| **MagicBento** | Bento grid with hover light effects | **First pick for feature grids** |
| Masonry | Masonry layout | light, general |
| PillNav | Pill navigation | light, general |
| PixelCard | Pixelated card | medium, stylized |
| ProfileCard | 3D flipping profile card | light, playful |
| RollingGallery | Rolling wheel gallery | medium, decorative |
| **ScrollStack** | Cards stack while scrolling (pin + overlay) | **First pick for narrative cards** |
| **SpotlightCard** | Spotlight follows the mouse on a card | **First pick for feature cards** |
| Stack | Card stack | light, general |
| StaggeredMenu | Menu items stagger in | light, general |
| Stepper | Step indicator | light, functional |
| **TiltedCard** | 3D tilt (gyroscope or mouse) | **First pick for work showcases** |

### Backgrounds, atmosphere (38)

| Name | One line | Cost | Tags |
|------|----------|------|------|
| **Aurora** | Soft aurora flow | medium (WebGL) | **First pick for dark editorial** |
| Balatro | Playing-card texture | medium | stylized |
| Ballpit | Physics ball pit | heavy | playful |
| Beams | Sweeping light beams | medium | tech |
| ColorBends | Bending color fields | medium | artistic |
| DarkVeil | Dark veil | light | dark editorial backup |
| Dither | Dithered pixels | light | retro |
| DotGrid | Dot grid | light | minimal |
| EvilEye | Eye that tracks the cursor | medium | experimental |
| FaultyTerminal | Glitching terminal | medium | cyber |
| FloatingLines | Floating lines | light | minimal |
| Galaxy | Galaxy field | medium | tech |
| GradientBlinds | Gradient blinds | light | stylized |
| Grainient | Grainy gradient | light | editorial |
| GridDistortion | Distorting grid | medium | experimental |
| GridMotion | Flowing grid | light | tech |
| GridScan | Scanning grid lines | medium | cyber |
| Hyperspeed | Hyperspeed tunnel | heavy | cyber |
| Iridescence | Iridescent sheen | medium | brand |
| LetterGlitch | Wall of glitching characters | heavy | cyber |
| LightPillar | Pillar of light | medium | dramatic |
| LightRays | Radiating light rays | medium | dramatic |
| Lightning | Lightning | medium | dramatic |
| LineWaves | Line waves | light | minimal |
| LiquidChrome | Liquid chrome | medium | brand |
| LiquidEther | Liquid ether | medium | artistic |
| Orb | Energy orb | medium | decorative |
| Particles | Particle system | medium | general |
| PixelBlast | Pixel burst | heavy | cyber |
| PixelSnow | Pixel snow | light | seasonal |
| Plasma | Plasma | medium | artistic |
| Prism | Prism dispersion | medium | brand |
| PrismaticBurst | Prismatic burst | heavy | dramatic |
| Radar | Radar sweep | light | tech |
| RippleGrid | Rippling grid | medium | decorative |
| **Silk** | Flowing silk | medium | **works for dark and light editorial** |
| SoftAurora | Soft aurora (lightweight) | light | dark editorial backup |
| Squares | Squares | light | minimal |
| Threads | Fine threads | light | minimal |
| Waves | Waves | light | minimal |

---

## Recommended combos by style and scene

### Dark Editorial (Linear-like skeletons)
- Background: **Aurora** / **Silk** / **SoftAurora** / **Grainient**
- Hero H1: **SplitText** or **ShinyText** (keywords) + **GradientText** (keywords)
- H2: **ScrollFloat** or **BlurText**
- Body: **ScrollReveal**
- Animation: **Magnet** (CTA) + **GlareHover** (cards)
- Component: **CardSwap** / **ScrollStack** / **SpotlightCard** / **MagicBento**

### Dark Tech / Cyber (cursor / warp / cyberpunk)
- Background: **LetterGlitch** / **Beams** / **Hyperspeed** / **FaultyTerminal**
- Hero H1: **GlitchText** / **DecryptedText** / **ShinyText**
- H2: **SplitText**
- Body: **TextType** (code blocks) + **ScrambleText** (eyebrow)
- Animation: **ElectricBorder** / **ClickSpark**
- Component: **TiltedCard** / **PixelCard**

### Minimal Pure / Editorial Light
- Background: **DotGrid** / **FloatingLines** / **Grainient**
- Hero H1: **SplitText** (restrained) + **GradientText** (keywords only)
- H2: **ScrollFloat**
- Body: **ScrollReveal**
- Animation: **Magnet** (CTA, the only effect) + **FadeContent**
- Component: **CardNav** / **InfiniteScroll** / **Masonry**

### Playful Creative
- Background: **Iridescence** / **LiquidChrome** / **Plasma**
- Hero H1: **TextPressure** / **FallingText** / **BounceCards** copy
- H2: **Shuffle** / **SplitText**
- Body: **TextTrail** / **ScrollReveal**
- Animation: **ClickSpark** / **BlobCursor** / **StickerPeel**
- Component: **BounceCards** / **BubbleMenu** / **GooeyNav** / **FlyingPosters**

### Chinese Elegant
- Background: **Threads** / **FloatingLines** / **Grainient** (low contrast)
- Hero H1: **BlurText** (slow) + **GradientText** (ochre gradient)
- H2: **ScrollFloat**
- Body: **ScrollReveal** (line granularity, never per character; Chinese per-character is too choppy)
- Animation: **Magnet** (restrained)
- Component: **CircularGallery** / **Masonry**

### Warm Professional
- Background: **Silk** / **SoftAurora** / **Grainient**
- Hero H1: **SplitText** + **GradientText**
- H2: **ScrollFloat**
- Body: **ScrollReveal**
- Animation: **Magnet** + **GlareHover**
- Component: **MagicBento** / **SpotlightCard** / **InfiniteScroll**

Style fit beats spectacle: Dark Editorial should not use GlitchText, Playful should not use Aurora. Stay consistent with the page's mood.

---

## Performance principles

- Never run more than **2 heavy backgrounds** on one page (only 1 WebGL background)
- Mobile (< 640px) degrades automatically: heavy background becomes a static gradient; 3D components become 2D
- Cursor effects only under `matchMedia('(hover: hover)')`
- Every effect needs a `prefers-reduced-motion` fallback path
- At most 3 GSAP timelines per page (more fights for the main thread)

## Reuse rules

1. **Copy first**: vue-bits / reactbits source is MIT; keep the author credit and use it
2. **Porting layer**: when moving Vue / React code to vanilla HTML, turn props into data attributes or function parameters
3. **Credit placement**: add to the page footer or README: "Motion effects derived from [vue-bits](https://github.com/DavidHDev/vue-bits) by DavidHDev (MIT)"
