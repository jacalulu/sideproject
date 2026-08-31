# Mermaid Dots — project guide for Claude

A kid-friendly dot-connecting puzzle game. The entire game is ONE
self-contained ~1MB HTML file: `public/mermaid-dots/index.html` (assets
embedded as data URLs; loose originals in `public/mermaid-dots/assets/`).
It ships three ways from this repo:

- **Web/PWA**: push to `master` → GitHub Pages deploys `public/`
  (`.github/workflows/deploy-pages.yml`).
- **iOS (iPhone + iPad)**: Actions → **iOS TestFlight** → Run workflow.
  Capacitor wrapper in `ios/`, lane in `fastlane/Fastfile`. Details and
  the six required secrets are in the README's iOS section — read it
  before touching signing; every rule in it was paid for with a failed
  run. Highlights: the distribution cert is a supplied .p12 secret
  (never let Xcode/fastlane mint certs on CI — a runner can't persist
  private keys, and Apple caps certificates), import it with
  `security import -f pkcs12` directly (fastlane's import_certificate
  wrapper rejects the file), fetch the profile per run via sigh, and
  select the newest Xcode on the runner (App Store Connect enforces a
  minimum SDK).
- Android: PWA install from the Pages URL; no store build.

## Versioning

- Build number = GitHub run number, set automatically. Never hand-edit.
- User-visible version: `MARKETING_VERSION` in
  `ios/App/App.xcodeproj/project.pbxproj` (currently 1.0). External
  TestFlight review is per-version, so bumping it re-triggers Beta App
  Review for external testers.
- TestFlight builds expire after 90 days; re-run the workflow to refresh.

## Working agreements (set by Jaclyn)

- **Manage pull requests end to end**: create the PR, merge it, watch CI,
  and fix failures without being asked. Small in-scope fixes: just do
  them. Genuine scope changes or destructive actions: ask first.
- **Never guess or assume — debug properly.** Read the actual error from
  the actual tool (wrappers like fastlane print *inferred* causes; the
  real error is often elsewhere). If the evidence isn't in the log,
  instrument first and act second. Label observed vs inferred. Verify
  changes locally (`ruby -c`, YAML parse, shell `bash -n`) before
  pushing.
- Anything on the Apple side (App Store Connect, certificates, tester
  invites) is Jaclyn's to click; provide exact steps and drafts, and ask
  for screenshots rather than assuming portal state.

## App Store facts (so they're never re-derived)

- Bundle ID `com.jacalulu.mermaiddots`, app name "Mermaid Dots",
  Team ID in the `APPLE_TEAM_ID` secret. iPad is already supported
  (`TARGETED_DEVICE_FAMILY = "1,2"`).
- The app collects nothing, has no network access, no ads, no purchases,
  no sign-in. Privacy policy (required for App Store submission) is
  served by Pages at `/privacy.html`. Export compliance is declared in
  Info.plist (`ITSAppUsesNonExemptEncryption = false`) — "Sign-in
  required" on TestFlight/review forms must be UNchecked.
- One device registration on the developer account is required for
  profile generation; it does not limit which devices install builds.
