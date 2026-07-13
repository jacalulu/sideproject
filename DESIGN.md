# Mermaid Dots — Design System

One page that defines every visual decision in the game, so new work stays
consistent. The rule of thumb: **the world is painterly, the interface is
sea glass, the stickers are candy.**

## 1. The three material layers

| Layer | What it's for | Treatment |
|---|---|---|
| **World** | Zone backgrounds, splash keyart, the named cast | Painterly, bioluminescent, dimensional (original Nano Banana art). Never flattened. |
| **Sea glass** | Everything the player touches: HUD pills, dialog cards, button chips, board frost | Translucent glass with `backdrop-filter` blur. Dark water glass for HUD (white text), pale pearl glass for dialog cards (dark ink text). CSS-drawn, never baked into images. |
| **Candy stickers** | All generated icons and board pieces | Chunky, rounded, simplified shapes; soft gradients; one crisp glossy highlight; thin soft white sticker outline with a gentle glow. Generated from one master style (see §5). |

## 2. Color tokens (`:root` in index.html)

| Token | Value | Role |
|---|---|---|
| `--coral` / `--coral-deep` | `#fb7aa8` / `#ef5590` | Primary action: main buttons, selection, highlights |
| `--aqua` / `--aqua-deep` | `#4db4ec` / `#1e88c9` | Secondary action: alternate buttons, informational icons |
| `--gold` | `#ffd166` | Stars and celebration ONLY — never for chrome |
| `--ink` / `--ink-soft` | `#164672` / `#41719d` | Text on pearl surfaces (headings / body) |

Per-creature colors live in the `TYPES` table (used for glows, rings,
confetti) and are part of each creature's identity — don't reassign them.

## 3. Typography

- **Baloo 2** (600/700, inlined woff2) — display face: headings, buttons,
  HUD, toasts, labels, canvas text on the map.
- **Nunito** (600/800, inlined woff2) — body face: card paragraphs, fun
  facts, any full sentence a child (or parent) reads.
- Headings use `text-wrap:balance`; paragraphs use `text-wrap:pretty`.
- Numbers that change (goal counts) use `font-variant-numeric:tabular-nums`.

## 4. Layout & spacing

- HUD is two rows: goals capsule centered on top; level pill (zone emblem
  badge + stacked text) left, one-line wave counter right.
- Bottom bar: four glass chips with lowercase labels, centered.
- Radii scale: pills `999`, cards `32`, tiles/HUD `22`, progress bars `3`.
- The title screen shows **no chrome** — HUD and button bar appear after Play.
- Dialogs own the screen: HUD sits below the overlay backdrop (z 9 vs z 10)
  and dims; only the button bar stays above (z 12).

## 5. Generated art pipeline (sticker sheets)

All icons/pieces come from **one master style prompt** anchored on
`scratchpad` sheet `sheet-pieces.png` (the six board creatures):

> chunky, rounded, simplified shapes; soft gradients; one crisp glossy
> highlight; thin soft white sticker outline with gentle glow; palette
> restricted to the tokens in §2 plus soft cream/lavender/seafoam.

Process: generate a grid sticker sheet (Nano Banana Pro via OpenRouter,
with the pieces sheet as a style reference image) → key out the fake
checkerboard background by neutral-gray luminance → slice by connected
components → downscale to ≤192px webp → copy to `assets/` → re-embed as
base64 in the `ASSETS` object. Icons are flat stickers; button bodies,
bubbles, and glass are drawn in CSS/canvas, never baked into the art.

## 6. Motion

- Every character sticker idles: one asymmetric keyframe (float + tiny
  tilt + a breath), personality set per character via CSS vars
  (`--d1` duration, `--rot` tilt, `--dy` travel). Finn flutters (2.4s),
  King Nerio barely sways (8.6s). Characters sharing a screen get
  negative `animation-delay`s so they never sync.
- Transforms only (GPU-cheap); everything respects
  `prefers-reduced-motion`.
- Bigger moments escalate: flipbook (8 frames) → full-screen video.

## 7. Iconography rules

- No emoji in chrome. Emoji are allowed only inside playful toast copy.
- Every icon exists as `assets/ico-*.webp` (UI), `assets/zone-*.webp`
  (zone emblems), or `assets/btn-*.webp` (button/HUD stickers).
- Zone emblems appear at three sizes: HUD badge (30px), map chip (~r·0.8),
  fact-card line (17px).
