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

**iPhone via TestFlight:** the repo already carries everything the build
needs — a Capacitor iOS project (`ios/`, `capacitor.config.json`), a
Fastlane lane (`fastlane/Fastfile`), and a manual **iOS TestFlight**
GitHub Actions workflow that builds on a macOS runner and uploads using
cloud-managed signing. No Mac required: the runner is the Mac, and Xcode
creates the certificate and provisioning profile itself from the API key,
so there is nothing to generate or download by hand.

One-time Apple setup (about 20 minutes, all in the browser):

1. **Register the App ID.** developer.apple.com -> Certificates, Identifiers
   & Profiles -> Identifiers -> + -> App IDs -> App. Bundle ID (explicit):
   `com.jacalulu.mermaiddots`. This must match `appId` in
   `capacitor.config.json` and `PRODUCT_BUNDLE_IDENTIFIER` in the Xcode
   project exactly.
2. **Create the app record.** appstoreconnect.apple.com -> Apps -> + -> New
   App. Platform iOS, name `Mermaid Dots`, pick the bundle ID from step 1,
   and give it any SKU (e.g. `mermaid-dots-1`).
3. **Grab the Team ID.** developer.apple.com -> Membership details. It is the
   10-character code -> secret `APPLE_TEAM_ID`.
4. **Create an App Store Connect API key.** App Store Connect -> Users and
   Access -> Integrations -> App Store Connect API -> + . Give it the
   **App Manager** role. Download the `.p8` file — Apple lets you download it
   exactly once. The page shows the **Key ID** (-> `APP_STORE_CONNECT_KEY_ID`)
   and, above the table, the **Issuer ID** (-> `APP_STORE_CONNECT_ISSUER_ID`).
5. **Base64-encode the key** so it survives as a secret:
   `base64 -i AuthKey_XXXXXXXXXX.p8 | pbcopy` -> `APP_STORE_CONNECT_KEY_B64`.
6. **Add the four secrets.** GitHub repo -> Settings -> Secrets and variables
   -> Actions -> New repository secret, for each of `APPLE_TEAM_ID`,
   `APP_STORE_CONNECT_KEY_ID`, `APP_STORE_CONNECT_ISSUER_ID`,
   `APP_STORE_CONNECT_KEY_B64`.
7. **Run it.** Actions tab -> **iOS TestFlight** -> Run workflow. It takes
   roughly 10-20 minutes; Apple then processes the build for another
   10-15 minutes before it shows up.
8. **Install on the phone.** App Store Connect -> your app -> TestFlight ->
   Internal Testing -> add yourself as a tester. Internal testers (up to 100
   people on your own team) get builds immediately with **no App Store
   review**. Install Apple's TestFlight app on the iPhone and the build
   appears there.

Every later run of the workflow ships a new build; the build number is the
GitHub run number, so it always increases. To change the user-visible
version, bump `MARKETING_VERSION` in `ios/App/App.xcodeproj/project.pbxproj`.

Going beyond TestFlight to a public App Store listing is a separate step and
*does* require review: screenshots, a description, a privacy policy URL, and
an App Privacy questionnaire. The game collects nothing and talks to no
server (progress lives in `localStorage`), so that questionnaire is all
"No" — but note that a kids-category listing brings extra review scrutiny.

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
