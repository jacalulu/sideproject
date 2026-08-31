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
- Start from the **adventure map**: a scrollable trail that winds up
  through the ocean zones, ten levels per zone painting. Tap any level
  you've beaten to replay it (your stars and progress are never lost).
  After every win you return to the map and your mermaid hops forward
  to the next level on the trail.
- Drag a line between 2 or more matching sea friends to collect them.
- Close a **loop** (like a square) to splash away every friend of that kind!
- Collect the friends shown at the top before the wave counter 🌊 runs out.
- From level 8, some friends are trapped in bubbles — swipe a bubbled friend
  as part of your matching line to pop it free (a loop rescues every bubbled
  friend of that kind on the board). Rescued friends swim to your aquarium.
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
- **Morgana** the sea witch is why friends are bubble-trapped from level 8;
  swipe them into a matching line to rescue them into your aquarium.
- **King Nerio** congratulates you when you finish each 10-level zone.

**Art & tech.** Painterly zone backgrounds, glowing painterly characters,
an animated win screen (an 8-frame Nano Banana flipbook of your mermaid
dancing), a looping background tune composed by Lyria (ducks under the
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
the whole game is still ONE self-contained ~1 MB HTML file with no
dependencies. Progress, chosen mermaid, and sound setting persist in the
browser.

The loose asset files live in `public/mermaid-dots/assets/`; the build that
embeds them into `index.html` is a small script — regenerate by replacing an
asset and re-inlining it as a base64 data URL in the `ASSETS` object.
