sideproject
===========

## 🧜‍♀️ Mermaid Dots

A kid-friendly dot-connecting puzzle game (in the spirit of Two Dots) with
**no ads, no purchases, no lives, no timers** — just fun.

**To play:** open `public/mermaid-dots/index.html` in any browser
(double-click the file, or serve the `public/` folder). Works with mouse
or touch, so it's great on a phone or tablet.

**How to play**
- Drag a line between 2 or more matching sea friends to collect them.
- Close a **loop** (like a square) to splash away every friend of that kind!
- Collect the friends shown at the top before the wave counter 🌊 runs out.
- From level 8, some friends are trapped in bubbles — clear next to a bubble
  to pop it and set them free.
- Run out of waves? Just try again — no penalty, ever.

**Infinite levels.** Levels are generated from a seeded difficulty curve, so
level N is always the same puzzle and there is no last level. The curve ramps
over roughly the first 60 levels and then gently plateaus:

| What changes            | When                                    |
|-------------------------|-----------------------------------------|
| Creature colors         | 4 → 5 at level 6 → 6 at level 20        |
| Board size              | 6×6 → 7×7 at level 15 → 8×8 at level 50 |
| Collection goals        | 2 kinds → 3 kinds at level 12           |
| Bubble traps            | start at level 8, up to 10 per board    |
| Ocean zone (background) | new zone every 10 levels, 8 zones cycle |

Within each 5-level block difficulty rises then resets, so a tough level is
followed by a breather. Every level is winnable and retries are always free.

All art is drawn in code (canvas), the Fredoka font (OFL license) is embedded,
and the whole game is a single self-contained HTML file with no dependencies.
Progress (current level) and the sound setting are saved in the browser.

**Want custom art?** The game can use provided assets instead of the built-in
drawings — good formats are SVG (or transparent PNG at 512×512) for creatures,
wide transparent PNGs for background layers, short MP3/OGG clips for sounds,
and WOFF2 for fonts. Drop them in `public/mermaid-dots/assets/` and wire them
in where the sprites are baked.
