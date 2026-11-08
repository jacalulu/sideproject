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

**iPhone & iPad via TestFlight:** the **iOS TestFlight** GitHub Actions
workflow builds a distribution-signed .ipa on a macOS runner and uploads it
to App Store Connect. To ship a new build: Actions tab -> iOS TestFlight ->
Run workflow. Builds land in TestFlight after ~10-15 min of Apple
processing; internal testers get them with no review. TestFlight builds
expire after 90 days, so re-run the workflow occasionally even without
changes.

How signing works (learned the hard way across 12 failed runs): a CI
runner is destroyed after every job, so Xcode's cloud-managed signing
mints and abandons a new certificate per run and can never produce a
distribution identity. Instead the Apple Distribution certificate is
created once (openssl CSR -> developer.apple.com), stored as a
base64-encoded, password-protected .p12 in repo secrets, imported into a
throwaway keychain per run with `security import -f pkcs12` (fastlane's
import wrapper rejects the file; the explicit format flag matters), and
the App Store provisioning profile is fetched fresh each run via `sigh`.
The build also selects the newest Xcode on the runner, because App Store
Connect enforces a minimum SDK and the image's default lags it. One
registered device on the developer account is required for Apple to issue
profiles; it does not limit which devices can install TestFlight builds.

Repo secrets required: `APPLE_TEAM_ID`, `APP_STORE_CONNECT_KEY_ID`,
`APP_STORE_CONNECT_ISSUER_ID`, `APP_STORE_CONNECT_KEY_B64` (the .p8,
base64), `IOS_DIST_CERT_P12` (the .p12, base64), `IOS_DIST_CERT_PASSWORD`.
If the distribution certificate is ever rotated, re-export with
`openssl pkcs12 -export -inkey dist.key -in dist.pem -out dist.p12
-keypbe PBE-SHA1-3DES -certpbe PBE-SHA1-3DES -macalg sha1` — modern
openssl's default PKCS#12 algorithms are rejected by macOS `security` as a
wrong password. The workflow validates the secret with a real
`security import` before building, so a bad bundle fails in ~20s with the
actual reason.

The privacy policy required for App Store submission is served by the
Pages deploy at `/privacy.html`.

**How to play**
- Start from the **adventure map**: a scrollable trail that dives down
  through eight ocean zones, from the sunlit surface (level 1) to the
  starlit trench (level 200), with fish, jellies and kelp moving along the
  way. Tap any level
  you've beaten to replay it (your stars and progress are never lost).
  After every win you return to the map and your mermaid hops forward
  to the next level on the trail.
- Drag a line between 2 or more matching sea friends to collect them.
- Close a **loop** (like a square) to splash away every friend of that kind!
  The friends that drop in next are never that kind, so one loop sets up
  the next. A bigger loop that wraps around other pieces bursts everything
  inside it like a bubble.
- Collect the friends shown at the top before the wave counter 🌊 runs out.
- From level 3, some friends are trapped in bubbles — swipe a bubbled friend
  as part of your matching line to pop it free (a loop rescues every bubbled
  friend of that kind on the board). Rescued friends swim to your aquarium.
- Run out of waves? Just try again — no penalty, ever. Miss the same level
  twice and **Finn's gift** offers 5 more waves on the same board.
- Every zone brings something new to the board, introduced by a one-picture
  story card the first time it appears:
  - **Sand** (a first taste from level 11, then all of Coral Cove, 26–50): clear friends on or next to a sandy tile
    to sweep it away.
  - **Anchors** (Kelp Forest, 51–75): they can't join a line; they sink a
    row every wave, faster if you clear underneath, and count when they
    reach the bottom.
  - **Crates** (Shipwreck Bay, 76–100): a line right next to a crate
    cracks it open.
  - **Oysters** (Pearl Palace, 101–125): two neighbouring clears, one to
    wake it and one for its pearl.
  - **Jelly power** (from Jellyfish Grove, 126+): a line of 6+ leaves a
    glowing jelly friend; using it bursts the 3×3 around it.
  - **Morgana's ink** (Twilight Deep and Starlight Trench, 151–200): a
    clear next to an ink blot wipes it away; a wave that touches no ink
    lets it creep onto a neighbouring friend (never past a quarter of the
    board).
  - Twilight Deep and Starlight Trench mix two of these per level. Every
    5th level of a zone is a breather with no mechanic.
- **Stars** are the challenge, not the gate: finishing with 40% of the
  waves left earns 3 stars, 20% earns 2. That means out-playing the
  playtest bot, which wins with about a quarter left.
- **Pause** (bottom left during a level) holds keep playing, start over,
  adventure map and sound, so a stray tap can't end a level.
- A first-time win plays that level's **fun fact** (with a "Maybe later"
  skip) before the map.
- **My Aquarium**: the tank where rescued and unlocked friends swim (tap
  one to tickle it); a **sticker album** of 16 friends, two per zone,
  unlocked at each zone's level 12 and 25; and a **shop** of 8 decorations
  bought with stars. The aquarium button toggles it; a dot on the button
  means something new.

**Infinite levels.** Levels are generated from a seeded difficulty curve, so
level N is always the same puzzle and there is no last level. The curve ramps
over roughly the first 60 levels and then gently plateaus:

| What changes            | When                                    |
|-------------------------|-----------------------------------------|
| Creature colors         | 4 → 5 at level 3 → 6 at level 14        |
| Board size              | 6×6 → 7×7 at level 12 → 8×8 at level 40 |
| Collection goals        | 2 kinds → 3 kinds at level 8            |
| Bubble traps            | start at level 3, up to 12 per board    |
| Ocean zone (map)        | 8 named zones of 25 levels per 200-level *chapter* |

Within each 5-level block difficulty rises then resets, so a tough level is
followed by a breather. Every level is winnable and retries are always free.

Mechanic levels get extra waves for each piece, measured rather than
guessed: a greedy bot plays the real game code on every level 1–200 (with
unlimited waves, to measure what each sand tile, anchor, crate, oyster
and ink blot
actually costs), and the budgets are set so mechanic levels win about as
often as their zone's breather levels. The same runs proved no level can
deadlock (two dead ends found this way were fixed: anchors stuck over
unmatched friends, and lone sand tiles).

**Difficulty pass (Nov 2026, "more obstacles").** About 40% more of each
piece, sand from level 11, and from Kelp Forest on two of every five levels
bring back an older piece; every fifth level of a zone stays a breather.
Spare waves were cut by about 6 per level and the per-piece wave costs
retuned (sand 0.6, anchor 2.4, crate 1.25, oyster 2.5, ink 1.8). Bot results,
4 runs of all 200 levels: win rate 56% -> 48% (levels 1-50: 66% -> 55%),
obstacle pieces 1,348 -> 2,180, zero deadlocks.

**The cast.** Original characters in the game's flat style:
- **Ophelia**, **Violet** and **Daphne** (Violet and Daphne are identical
  twins: Violet wears purple, Daphne yellow). Pick your mermaid on the start
  screen; she rides the map with you and dances when you win.
- **Finn** the worried little fish encourages you on the try-again screen.
- **Morgana** the sea witch is why friends are bubble-trapped from level 5;
  swipe them into a matching line to rescue them into your aquarium. Her
  ink creeps across the board in the deepest zones.
- **King Nerio** congratulates you when you finish each 25-level zone, and
  throws a big splashy **Chapter Complete** party at level 200.
- Finn, Morgana, King Nerio and the Maestro still use their earlier painted
  art; redrawing them flat is next on the style guide's build plan.

**The look.** Flat, friendly and bright: six bold friends with simple faces
floating on plain sand, shell-white controls, and a map made of flat colour
bands with animated scenery stickers (see `DESIGN.md` and the style guide;
art pipeline in `tools/stickers/`).

**App icon.** Ophelia the mermaid (`AppIcon-512@2x.png` for iOS; PWA icons
in `public/mermaid-dots/icon-*.png`).

**Art & tech.** Flat illustrated pieces and scenery from sprite sheets, a living
map drawn in code, a looping background tune composed by Lyria (ducks under the
narrated fun facts), pre-narrated fun facts — every host reads their own
facts in their own voice (gpt-audio via OpenRouter: deep King Nerio,
theatrical Maestro, shy Finn, velvet Morgana, bright mermaid; clips in
`assets/facts/`, Web Speech API as the offline fallback), and a
liquid-glass UI (frosted board panel, glass
bubble tokens, glass HUD —
plain CSS `backdrop-filter` + canvas, so it works on iPad Safari).
Dialog cards sit on a light pearl surface with dark sea-ink text; one
coral-pink/aqua accent pair carries every screen. The emoji icons are
replaced by a matching candy-glass icon set and eight zone emblems
(generated with Nano Banana Pro as sticker sheets, then sliced and
background-keyed — see `assets/ico-*.webp`, `assets/zone-*.webp`), and
every character sticker idles with a subtle CSS "alive" float, tuned per
personality (Finn flutters, King Nerio barely sways). All images
are WebP embedded as data URLs and the Fredoka font (OFL license) is inlined:
the whole game is still ONE self-contained ~4.3 MB HTML file with no
dependencies. Progress, chosen mermaid, and sound setting persist in the
browser; in the iOS app every save is also mirrored to native storage
(Capacitor Preferences) and reconciled on launch, so iOS clearing the web
view's storage can't reset her progress. Haptics use Capacitor Haptics.

The loose asset files live in `public/mermaid-dots/assets/`; embed or
replace one with `python3 tools/embed_assets.py public/mermaid-dots/index.html key=path`.
