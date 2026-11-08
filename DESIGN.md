# Mermaid Dots — Design

The full rules live in the shared **Mermaid Dots Style Guide**
(https://claude.ai/artifact/GPE4pwNk6WJsEVxNofRgfZ), where Jaclyn and Claude
edit and comment on them together. This page is the short version for the
code. When the two disagree, the style guide wins; update this page to match.

**The one-line rule:** a child must tell every piece apart in a glance, and
nothing on screen competes with the friends.

## Principles

1. Readable in a glance: each friend has its own colour *and* silhouette.
2. Flat, always: no outlines, white sticker borders, shadows, gradients or gloss.
3. Faces kept simple: two dot eyes and a small smile.
4. No grid: friends float on plain sand. The board is always full, and a line
   only joins direct neighbours.
5. Room to breathe: a friend fills about 60–70% of its spacing.
6. Quiet chrome: pills, mission bar, buttons, toasts and cards are shell white.
7. Show, don't tell: pictures and motion teach; no instruction text on the board.
8. Motion is the reward: pops, bounces, loops and a living map.

## Colour tokens (as used in `index.html`)

| Role | Hex | Where |
| --- | --- | --- |
| Starfish | `#F27D3A` | `TYPES` |
| Shell | `#F0629E` | `TYPES` |
| Fish | `#3473CC` | `TYPES` |
| Turtle | `#63A852` | `TYPES` |
| Octopus | `#9B62BA` | `TYPES` |
| Pearl clam | `#F2BF2A` | `TYPES` |
| Sand (play screen) | `#E8E0CB` | `SAND` |
| Shell white (chrome) | `#FAF3EA` | `boardColor`, `--boardBg` |
| Deep ink (text) | `#1F2D4F` | `--ink` |
| Gold (stars only) | `#FFC94A` | map stars |
| Trap bubble ring | `#6CC7E0` | `bakeSprites` |

Map bands, three per zone from light to dark, are `SEA_BANDS`: lagoon
turquoise, coral pink, kelp green, shipwreck teal, pearl lilac, jellyfish
violet, twilight blue, starlight navy.

## Type

Baloo 2 (700–800) for numbers, labels and headings; Nunito for sentences a
grown-up reads aloud. Counts are always numerals (`9/15`).

## Art

- Board pieces (`piece*`, `p*`), map scenery (`m<zone>_<nn>`) and the three
  mermaids (`hero*`, `celeb*`) come from sprite sheets made with
  `tools/stickers/`. Loose copies are in `public/mermaid-dots/assets/`.
- The map is code: `drawSea` paints the bands and places stickers by a fixed
  seed (`buildSeaLayout`); each sticker moves by its motion type
  (`drawSticker`), and everything holds still under Reduce Motion.
- Everything else is flat too since the Nov 2026 audit: the cast (Finn,
  Morgana, King Nerio, the Maestro), icons and zone emblems, button icons,
  the aquarium's friends, decorations and tank, the logo, the splash and
  the app icon. Buttons are solid friend colours; cards, chips and pills are
  shell white (the "STYLE GUIDE PASS" CSS block). Image calls now go to the
  Gemini API directly (`GEMINI_API_KEY`); see `tools/stickers/`.
