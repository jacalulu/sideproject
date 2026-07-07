sideproject
===========

## 🧜‍♀️ Mermaid Dots

A kid-friendly dot-connecting puzzle game (in the spirit of Two Dots) with
**no ads, no purchases, no lives, no timers** — just fun.

**To play:** open `public/mermaid-dots/index.html` in any browser
(double-click the file, or serve the `public/` folder). Works with mouse
or touch, so it's great on a phone or tablet.

**To play on a phone (the "TestFlight for Android" setup):** every push
to `master` deploys `public/` to GitHub Pages
(`.github/workflows/deploy-pages.yml`). Open
`https://jacalulu.github.io/sideproject/mermaid-dots/` in Chrome on
Android and choose **Add to Home screen** — the game installs as a
fullscreen app (PWA manifest + service worker). Each later merge to
`master` redeploys, and the installed app picks up the new version the
next time it's opened (the service worker fetches network-first). No
app store, no build step, no review queue.

**How to play**
- Start from the **adventure map**: a scrollable trail that winds up
  through the ocean zones, ten levels per zone painting. Tap any level
  you've beaten to replay it (your stars and progress are never lost);
  winning always unlocks the next level on the trail.
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

**The cast (the "Ocean Princess" theme).** Original characters, generated
with Gemini Nano Banana in a painterly bioluminescent style and embedded in
the game:
- **Ophelia** and **Jaclyn** — pick your mermaid on the start screen; she
  cheers when you win (with **Maestro** the lobster conductor).
- **Finn** the worried little fish encourages you on the try-again screen.
- **Morgana** the sea witch is why friends are bubble-trapped from level 8.
- **King Nerio** congratulates you when you finish each 10-level zone.

**Art & tech.** Painterly zone backgrounds, glowing painterly characters,
an animated win screen (an 8-frame Nano Banana flipbook of your mermaid
dancing), a looping background tune composed by Lyria (ducks under the
narrated fun facts), and a liquid-glass UI (frosted board panel, glass
bubble tokens, glass HUD —
plain CSS `backdrop-filter` + canvas, so it works on iPad Safari). All images
are WebP embedded as data URLs and the Fredoka font (OFL license) is inlined:
the whole game is still ONE self-contained ~1 MB HTML file with no
dependencies. Progress, chosen mermaid, and sound setting persist in the
browser.

The loose asset files live in `public/mermaid-dots/assets/`; the build that
embeds them into `index.html` is a small script — regenerate by replacing an
asset and re-inlining it as a base64 data URL in the `ASSETS` object.
