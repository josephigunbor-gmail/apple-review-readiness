---
name: apple-review-readiness
description: Run before any App Store submission. Consolidates what Apple documents that it checks (App Review Guidelines, App Review and TestFlight pages, App Store Connect Help) with rejection-proven lessons: binary validation (asset catalogs, build stamps, version coherence), demo access, sign-in, in-app purchase, UGC, health and finance rules, and the submission-day run order. Every check is paired with its fix.
---

# Apple review readiness

One playbook for surviving Apple's machines and Apple's reviewers. Section 0 is
the official baseline (cited). Sections A, B, and D are field lessons — where
they confirm, sharpen, or go beyond the official text, that is stated.

## When to run

- **Internal TestFlight builds:** Section A only.
- **Any App Store SUBMISSION** (a version submitted for review): Sections
  0 + A + B + your per-app annex (see `ANNEX-TEMPLATE.md`) + D, in order, on
  submission day.
- **How this differs from a smoke test:** a cold-start smoke proves the build
  *behaves* on launch. This skill proves the build *and its listing* survive
  automated validation and a human reviewer. Neither substitutes for the
  other; both run.

## Standing verdict rules (never bend)

- A build's verdict (VALID / INVALID) is taken **only from a fresh App Store
  Connect read** (`GET /v1/builds`, or the Build Uploads list in the ASC web
  UI) — never from the upload or delivery response. Retract any interim
  verdict the moment a fresh read contradicts it.
- A rendered cold-start smoke that didn't run is never claimed passed. If
  your pipeline can't run a simulator/device smoke, say so and rely on
  TestFlight tap-through proof instead.
- A green test summary with skipped tests is **hollow**. Judge suites by the
  test-report tallies: 0 failed / 0 skipped.
- Fix **one variable per retry**. On rejection, read the Resolution Center
  text verbatim, fix the root cause, and never resubmit blind.

## SECTION 0 — The baseline: what Apple documents that it checks

Every citation below was verified by opening the page. "Field note" = how
real submissions relate.

**App Review Guidelines** — https://developer.apple.com/app-store/review/guidelines/

- *Before You Submit* — establishes the demo-account/demo-mode, live-backend,
  complete-metadata, and review-notes requirements that §B enforces.
- **1.2 User-Generated Content** — UGC apps must include a method for filtering
  objectionable material, a mechanism to report offensive content with timely
  responses, the ability to block abusive users, and published contact
  information.
- **1.4.1 Medical apps** — reviewed with greater scrutiny; must clearly
  disclose data and methodology behind accuracy claims and remind users to
  check with a doctor before making medical decisions. (§B health items.)
- **1.5 Developer Information** — the app and its Support URL must include an
  easy way to contact the developer.
- **2.1 App Completeness** — submissions must be final versions with all
  metadata and fully functional URLs; placeholder text and empty websites
  scrubbed; app tested on-device; demo account info included and the back-end
  service turned on if the app has a login; IAP items complete, up-to-date,
  visible to the reviewer and functional, or their absence explained in
  review notes (2.1(b)). Apple rejects binaries that crash or exhibit obvious
  technical problems.
- **2.3 Accurate Metadata** — 2.3.1(a): new features must be described with
  specificity in Notes for Review (generic descriptions will be rejected);
  2.3.2: description/screenshots must flag content that requires IAP;
  2.3.3: screenshots show the app *in use*, not title art, login, or splash
  screens; 2.3.6: answer age-rating questions honestly; 2.3.7: no prices or
  irrelevant phrases in metadata, names ≤ 30 characters; 2.3.9: display
  *fictional* account information in screenshots, never a real person's data;
  2.3.12: "What's New" must describe significant changes specifically.
- **3.1.1 In-App Purchase** — unlocking features/functionality must use IAP
  (no license keys, QR codes, or your own payment mechanisms for digital
  goods); restorable purchases need a restore mechanism. **3.1.2** governs
  auto-renewable subscriptions. **3.1.3(g)**: buying ads/"boosts" for posts
  in the same app must use IAP — a "feature my profile/post" product sits
  squarely here.
- **Section 4 Design** — Apple's stated minimum design standards for approval.
- **4.2 Minimum Functionality** — the app must be elevated beyond a
  repackaged website; 4.2.2: not primarily marketing materials, web
  clippings, or a collection of links; 4.2.3: works on its own. (Keeping
  everything inside the app — no web-view doors that hand the user off to a
  browser — is stricter than 4.2 and also satisfies it.)
- **4.8 Login Services** — an app using a third-party/social login to
  authenticate the *primary account* must also offer an equivalent login
  service that limits collection to name + email, lets users keep their
  email private, and does not collect interactions for advertising without
  consent — in practice, Sign in with Apple. Exceptions: the app exclusively
  uses its own account system; education/enterprise apps on existing
  accounts; government/industry ID; clients for a specific third-party
  service. *Field note:* if your app offers Google/Facebook login for the
  primary account, Sign in with Apple is mandatory. An app using only its
  own email/password system sits inside the own-system exception **while it
  stays that way**; adding any social login re-triggers 4.8.
- **5.1.1(i) Privacy Policies** — privacy policy link required in the ASC
  metadata field AND in the app, easily accessible; it must state what data
  is collected, how, and all uses; confirm third parties sharing the data
  give the same or equal protection; explain retention/deletion and how
  users revoke consent or request deletion.
- **5.1.1(ii) Permission** — consent before collection; purpose strings
  must clearly and completely describe the use of the data.
- **5.1.1(v) Account Sign-In** — if the app supports account creation, it
  must also offer **account deletion within the app**; apps without
  significant account-based features must let people use them without a
  login; a mechanism to revoke social-network credentials must exist in-app.
- **5.1.1(ix) Regulated fields** — apps providing services in highly
  regulated fields (banking and financial services, healthcare are named) or
  requiring sensitive user information **should be submitted by the legal
  entity that provides the services, not by an individual developer**.
  *Watch item:* if your developer account is an individual and your app is
  a finance or health app, surface this before the first submission — never
  discover it in a rejection.
- **5.1.3 Health and Health Research** — health/fitness/medical data may
  not be used or disclosed to third parties for advertising, marketing, or
  use-based data mining; no personal health information in iCloud; disclose
  the specific health data collected. (§B health items.)
- **5.2.3 Audio/Video Downloading** — apps must not facilitate illegal file
  sharing or download media from third-party sources without explicit
  authorization. (Note: 5.2.3 as currently published is this media rule,
  under the 5.2 Intellectual Property umbrella — not a general "legal"
  clause.)

**App Review (overview)** — https://developer.apple.com/app-store/review/

- Establishes the review-information mechanics and Apple's published list of
  common issues: crashes and bugs, broken links (support + privacy links
  required for all apps), placeholder content, incomplete information,
  privacy-policy issues, unclear data access requests, inaccurate
  screenshots, substandard UI, web clippings/aggregators, repeated similar
  apps, copycats, misleading users, not enough lasting value, and submission
  by the incorrect entity. Apple states **over 40% of unresolved issues
  relate to Guideline 2.1** — completeness is the single biggest rejection
  family.
- Also establishes the appeals path (App Review Board), expedited review,
  and the bug-fix-submission option (§D step 12).

**TestFlight** — https://developer.apple.com/testflight/

- Internal testers: up to 100 team members, no beta review. External
  testers: up to 10,000, and **the first build must already be approved by
  App Review for TestFlight** (beta review); builds are automatically sent
  for review when added to a group; beta app description and beta review
  information are required for external sharing. *Field note:* an external
  group's public link shows "beta not found" until beta review clears, and
  a tester cannot be seated in an internal group until they have accepted
  their team invitation.

**Upload builds (App Store Connect Help)** —
https://developer.apple.com/help/app-store-connect/manage-builds/upload-builds/

- Establishes that the bundle ID and version **in the bundle** associate a
  build with its ASC record, the build string uniquely identifies it, and a
  build must finish processing before it appears. Its supported-versions
  table requires an iOS app to be **built using Xcode 26 or later** for
  upload. *Field sharpening:* non-Xcode build routes satisfy this only
  because the submission build carries **genuine stamps harvested from a
  real Xcode-built build** — the stamps must be true, not typed (§A).

**User Privacy and Data Use** — https://developer.apple.com/app-store/user-privacy-and-data-use/

- Establishes Privacy Nutrition Labels (required to submit new apps and
  updates), privacy manifests for third-party SDK code (Xcode aggregates
  them into the privacy report used for the labels), and ATT consent rules.
  *Field note:* even if your app tracks nobody, labels must still be filed
  and must match the manifests and the actual data flows. SDKs that ship
  privacy manifests must keep them in the bundle.

## SECTION A — Automated validation (Apple's machines)

Run for every upload, internal or submission. Each check is paired with the
fix that clears it.

- [ ] **Genuine asset catalog (Assets.car).** The 1024 icon must live in an
  asset catalog produced by `actool` in a genuine Xcode build. Hand-built or
  stub catalogs fail validation.
  **Fix:** if your build pipeline can't run `actool`, harvest the catalog
  once from a genuine Xcode-built IPA of the same app (extract `Assets.car`,
  the launch-screen storyboard, and the flat icons) and reuse it in your
  pipeline. Record the harvest source in your private annex — never forge or
  synthesize a catalog.
- [ ] **Bundle ID ↔ ASC record exact.** The bundle ID in the binary must
  match the App Store Connect record character-for-character.
  **Fix:** read the bundle ID out of the built artifact (not your project
  settings — build variants and alternate trees drift) and compare it to the
  record before uploading. A wrong-tree build with a sibling bundle ID is a
  classic self-inflicted rejection.
- [ ] **Version coherence.** Store version == `MARKETING_VERSION`, bumped in
  the same commit as the store version. A mismatch between the bundle's
  marketing version and the version you're submitting under can flip a
  processed build to **INVALID_BINARY** after an apparently successful
  upload.
  **Fix:** bump the marketing version in the same change that creates the
  store version, and verify the built bundle's `CFBundleShortVersionString`
  against the ASC version before uploading.
- [ ] **Build number new and unused.** It must be greater than every build
  already in ASC for that version; a reused build number is rejected as a
  duplicate.
  **Fix:** query ASC for the highest existing build number during preflight
  and increment from there — don't trust the local project's number.
- [ ] **DT stamps present and genuine.** Missing `DT*` keys (DTXcode,
  DTSDKName, DTPlatformBuild, …) make the build read as an ancient SDK and
  draw validation errors (the 90725 / 90507 / 90534 family). Internal builds
  may carry your installed SDK's true stamps. A **submission** build must
  carry a genuine released-Xcode stamp set.
  **Fix:** harvest the full stamp set from a known-good build of the same
  app that was produced by a released Xcode, and apply that exact set to
  submission builds. Keep the per-app set in your private annex. Typed or
  guessed stamps are the failure, not the fix.
- [ ] **Entitlements + profile currency.** The provisioning profile must
  postdate every capability enablement and carry every declared entitlement.
  Sign in with Apple's capability enum is `APPLE_ID_AUTH` (not
  `SIGN_IN_WITH_APPLE`).
  **Fix:** after enabling any capability in the developer portal,
  regenerate the App Store profile before signing; signing with a stale
  profile fails at the profile step or silently drops the entitlement.
- [ ] **Signing pair verified locally.** Certificate and password are one
  matched pair from a single export.
  **Fix:** verify the pair offline before any upload (e.g.
  `openssl pkcs12 -legacy -in cert.p12 -passin … -noout` exits 0, and any
  encoded transport copy decodes byte-identical — compare sha256). Move
  secret values file→API only; never retype them. Modern OpenSSL-3 exports
  (PBES2 / MAC-sha256) are rejected by macOS `security import` with the same
  "MAC verification failed" message as a wrong password — export `-legacy`
  (MAC sha1, PBE-SHA1-3DES) and verify the format before uploading.
- [ ] **Encryption prompt pre-answered.** `ITSAppUsesNonExemptEncryption`
  set truthfully in Info.plist, so processing doesn't stall on the export
  compliance prompt.
  **Fix:** set the key (most apps that only use standard HTTPS/exempt crypto
  answer `false`) and re-check it whenever you add encryption code or a new
  SDK.
- [ ] **Privacy manifests in the bundle** for every SDK that ships one, with
  required-reason API declarations where the app/SDKs use listed APIs.
  **Fix:** confirm each SDK's `PrivacyInfo.xcprivacy` survives your build
  pipeline into the final bundle — several non-Xcode pipelines drop them —
  and add your own manifest for the app target.
- [ ] **Required-reason API cross-check (executable).** Grep your app's own
  source for the four required-reason categories — user defaults
  (`UserDefaults`, `@AppStorage`), file timestamps
  (`contentModificationDateKey`, `creationDateKey`, `attributesOfItem`),
  disk space (`volumeAvailableCapacity`, `systemFreeSize`), system boot
  time (`systemUptime`, `mach_absolute_time`, `CACurrentMediaTime`) — and
  confirm every category the app itself uses is declared in the app's OWN
  `PrivacyInfo.xcprivacy` with an approved reason code.
  **Fix:** SDK manifests cover SDK code only; they do not substitute for the
  app's own declarations. Add the missing category + reason code to the
  app manifest and rebuild. (Check folded in from the app-store-review-risk
  scanner comparison — see README.)
- [ ] **Purpose-string specificity test.** Every `NS*UsageDescription` in
  the shipped Info.plist must name the visible feature it serves.
  **Fix:** rewrite any string under ~12 characters or built from generic
  filler ("needed", "required", "we need access", "app requires access", or
  anything containing TODO/placeholder/lorem) to describe the concrete
  feature and what the data is used for — reviewers read these, and 5.1.1(ii)
  requires them to be clear and complete.
- [ ] **ATT / IDFA cross-check.** Grep the app source for
  `ATTrackingManager`, `ASIdentifierManager`, `advertisingIdentifier`.
  **Fix:** any hit ⇒ `NSUserTrackingUsageDescription` must exist, the ATT
  prompt timing must be deliberate, and the privacy label must declare
  tracking. No hits ⇒ the labels must say no tracking. Mismatched labels are
  a rejection and a trust problem; align code, manifest, and labels.
- [ ] **Linked libraries present in the shipped binary.** A library can
  compile yet be dropped at the link step — the build stays green while the
  feature it powers crashes on first use.
  **Fix:** write a binary-level check for the shipped executable (symbol
  presence for each linked library/framework the app depends on), calibrate
  it against a known-good and a known-bad build, and re-run it on **every**
  build. A library present in source and absent in the binary is a failed
  gate, not a warning.
- [ ] **Verdict from a fresh read.** Poll `GET /v1/builds` (the builds
  endpoint **rejects `sort` parameters** — never send one) until the
  processed build resource for the exact build number reads VALID.
  **Fix:** if it reads INVALID, fetch the build's processing issues before
  changing anything — fix the one cause named, not three guesses.
- [ ] **TestFlight attach is a separate step.** Upload ≠ seated.
  **Fix:** POST the build↔group relationship explicitly, then re-read the
  group and confirm the build is listed. Internal-group testers must first
  accept their **team invitation** — team invitations are web-UI only (the
  ASC API users resource refuses CREATE); a betaTester record returns 409
  before acceptance, 204 after.

## SECTION B — Human review readiness (Apple's reviewers)

Each check is paired with the fix that clears it.

- [ ] **Demo access works today.** An active demo account (or approved
  built-in demo mode) in the Review Notes, backend live for the whole review
  window (Guideline 2.1, Before You Submit).
  **Fix:** use the demo-instance pattern — a *separate* demo backend/database
  seeded with synthetic records only (dozens, at realistic shape), reviewer
  credentials in the Review Notes, and zero real user data anywhere in review
  materials. Test the demo login end-to-end on submission day, not from
  memory. Screenshots and demo data show fictional accounts only (2.3.9).
- [ ] **Every sign-in provider visible AND functional on a cold start.** The
  sign-in screen must draw its options without waiting on a network fetch
  that can fail silently — a shipped build once lost its social sign-in
  buttons entirely on cold start while unit tests stayed green.
  **Fix:** render sign-in buttons unconditionally from local state. A
  provider that is temporarily unavailable may appear disabled *with an
  explanation* — never vanished. Prove the Sign in with Apple round-trip on
  a real device before submission; reviewers tap every door.
- [ ] **Sign in with Apple present** wherever third-party login exists
  (4.8), with hide-my-email working end to end.
  **Fix:** link identity-provider accounts by verified email so a
  private-relay address still lands the user in the right account.
- [ ] **Account deletion inside the app** (5.1.1(v)), end to end.
  **Fix:** deletion must remove the server account and synced state, wipe
  on-device data, and return the app to first-run state on relaunch. Test
  the whole path, not just the button's existence.
- [ ] **Privacy policy + support URLs live**, reachable without sign-in,
  returning the right content, and matching what the listing says (1.5,
  5.1.1(i)).
  **Fix:** fetch both URLs yourself on submission day; broken links are a
  named common rejection, and "it worked last month" is not a check.
- [ ] **Age rating answered honestly** (2.3.6). Metadata itself stays
  appropriate for all audiences (2.3.8).
  **Fix:** answer the questionnaire against the *shipped features*, not the
  roadmap or an old draft. If internal notes disagree about expected
  ratings, reconcile them against the feature list at entry time — copy
  neither answer set blindly.
- [ ] **IAP readiness.** The Paid Apps agreement, banking, and tax forms
  must be **Active**. While an agreement sits at "Processing", StoreKit
  returns **no products at all** — every app on the account looks broken in
  review even though the IAPs themselves are approved.
  **Fix:** verify Active status in ASC → Business before any submission
  that touches IAP, and confirm each product actually returns in the app.
  Products must be complete, priced, territories set, visible and
  functional in the app or explained in Review Notes (2.1(b), 2.3.2,
  3.1.1); consumables never expire; a restore path exists for restorable
  purchases.
- [ ] **UGC safeguards real, described truthfully** (1.2): objectionable
  material filtering, report mechanism with timely response, block, delete,
  published contact info.
  **Fix:** if your moderation model is post-first (media posts immediately,
  moderation by report/block/delete after the fact), say exactly that in
  the listing and review notes. Never claim pre-moderation or an approval
  queue that does not exist — the reviewer will post something and find out.
- [ ] **No placeholder anything** — no lorem, test, or "coming soon"
  content in the build or the metadata (2.1; placeholder content is a named
  common rejection).
  **Fix:** grep the metadata and bundle for `lorem`, `TODO`, `coming soon`,
  `placeholder`, and your own dev codenames before submitting.
- [ ] **No steering language.** Grep the app and the listing for
  external-purchase steering ("subscribe on the web", "purchase on our
  website", "checkout session", "Stripe checkout", "billing portal",
  "manage subscription on our website").
  **Fix:** any hit must be checked against the CURRENT external-purchase
  rules for every enabled storefront — the US rule does not apply globally,
  and entitlement + disclosure requirements differ by storefront and app
  category. When in doubt, remove the language; an in-app purchase or a
  silent settings page is safer than a clever link. (Check folded in from
  the app-store-review-risk scanner comparison.)
- [ ] **Background modes justified.** Every `UIBackgroundModes` entry in
  the shipped Info.plist maps to a visible user-facing feature.
  **Fix:** remove modes you can't justify, and explain in the Review Notes
  any mode a reviewer cannot trigger naturally (e.g. background audio,
  background fetch driven by server events). (Check folded in from the
  app-store-review-risk scanner comparison.)
- [ ] **The app is self-contained.** No doors that kick the user out to a
  browser; closing any in-app web view returns to the app; password reset
  completes in-app.
  **Fix:** route unavoidable web content through an in-app browser view
  with a clear return path, and finish account flows (especially password
  reset) natively. This is also the 4.2 answer: the app is plainly more
  than the website in a wrapper.
- [ ] **Every hub/grid tile destination actually opens.** A tile can
  render perfectly — live data, correct counts — and still never
  navigate. The failure mode seen in the field: a press-feedback
  `ButtonStyle` (scale/shrink on press) applied to a `NavigationLink`
  inside a grid embedded in a list row; the custom style replaces the
  link's internal button machinery and the tap never becomes a
  navigation on device. Static tests and green builds do not catch
  it — the screen looks right in every screenshot.
  **Fix:** style belongs on `Button`s only, never on a
  `NavigationLink`. Build hub tiles as `Button`s that append to a
  `NavigationStack` path (or otherwise drive navigation explicitly),
  enforce the construction statically (grep: no `NavigationLink`
  block carries a `.buttonStyle(`), and put "tap every hub tile;
  each destination presents" on the on-device checklist for every
  build.
- [ ] **Share/action sheets present immediately on tap.** Never gate
  presenting a share sheet on an asynchronous download (e.g. fetching a
  cover image first) — on a slow connection the tap looks dead, with no
  spinner and no feedback. A two-step presentation flag that can be
  consumed while still empty desyncs and kills every later tap too.
  **Fix:** preload any share asset quietly in the background when the
  screen opens (with a time limit), and present the sheet immediately on
  tap with whatever is ready — image if it loaded, text + link if it
  didn't. The sheet must never be able to open empty.
- [ ] **Share payload is one combined message.** Handing other apps
  separate text, link, and image items lets the receiving app pick the
  item type it prefers — most pick the bare link and silently drop the
  text, so hashtags, bio, and pitch never arrive.
  **Fix:** assemble the pitch, bio, hashtags, then the link into a single
  text item, with the image as its own item beside it. Verify the share
  end to end in a receiving app that is *not* Apple's Messages (which
  merges everything and hides the bug) — e.g. Messenger or WhatsApp —
  and confirm text, hashtags, and link arrive together.
- [ ] **Health claims disciplined.** Medical and mental-health apps get
  1.4.1 scrutiny.
  **Fix:** disclose data and methodology; present validated questionnaires
  (e.g. PHQ-9/GAD-7) as self-checks, never diagnosis; carry "not a
  substitute for professional care" plus crisis-line information in the
  listing; make crisis features (safety plan, grounding tool, one-tap
  crisis lines) work **signed-out and offline** — a reviewer in a fresh
  install is exactly the person who needs them reachable. Health data is
  never shared for advertising or mining, and no personal health
  information goes in iCloud (5.1.3).
- [ ] **Voice features — biometric caution.** Voice recordings can become
  biometric identifiers the moment you derive voiceprints from them.
  **Fix:** never derive voiceprints or biometric templates from voice
  features without written notice + release (Illinois BIPA is the strictest
  template, but similar laws exist elsewhere). If a voice feature is
  live-only by design, keep it that way: no recording, transcription, or
  storage path may exist in the feature.
- [ ] **Vendored SDK patches — verify at the binary level.** If you patch
  a vendored SDK (source-level workaround for an SDK defect), source review
  cannot prove the patch survived compilation and linking.
  **Fix:** write a binary-level check for the shipped executable (symbol
  presence/absence, direct-call vs. selector dispatch — whatever
  distinguishes patched from stock in your case), calibrate it against a
  known-good and a known-bad build, and re-run it on **every** build. A
  patched-in-source, stock-in-binary build ships the crash you already
  fixed once.
- [ ] **Review Notes written for a stranger.** New and non-obvious features
  described with specificity (2.3.1(a)), demo credentials, IAP locations
  and explanations, consent gates, and anything the reviewer cannot reach
  without help.
  **Fix:** assume the reviewer has never seen your app, has ten minutes,
  and will reject under 2.1 rather than guess. Write the notes that make
  guessing unnecessary.

## SECTION C — Per-app annexes (keep them private)

Section C of the original playbook holds per-app facts: ASC app ID, bundle
ID, the stamp-set source build, demo access details, age-rating calls, and
each app's named traps. Those values are operationally sensitive and
app-specific, so they don't belong in a public repo.

Use `ANNEX-TEMPLATE.md` in this repo to keep one annex per app in your own
private notes, and run the matching annex alongside Sections 0/A/B/D on
submission day.

## SECTION D — Submission-day run order

1. Freeze the final build through your pipeline. Build number unused;
   store version == MARKETING_VERSION in the same commit.
2. Section A all green; **fresh ASC read shows the build VALID**.
3. Attach the build to the store version; re-read the version page and
   confirm the intended build is the one attached.
4. Cold-start smoke on the actual build, plus the app's full regression
   checklist; read the test-report tallies (0 failed / 0 skipped) — never
   the summary alone.
5. Run a static source scan (see "Third-party scanner pass" below) and
   disposition every finding.
6. Metadata entered and **verified on Apple's side** after saving: name
   (≤30), subtitle (≤30), keywords (≤100), description (≤4000), What's New
   specific (2.3.12), promotional text current.
7. Screenshots present for every required size, showing the app in use
   (2.3.3), fictional data only (2.3.9); verify on Apple's side that they
   landed on the right version and localizations.
8. Privacy labels + age rating entered and consistent with the binary
   (manifests, purpose strings, actual data flows).
9. IAP (if the version touches it): products ready, prices/territories
   set, and the Paid Apps agreement + banking + tax read **Active** in ASC.
10. Demo access tested end-to-end **today**: demo account signs in, backend
    live, Review Notes carry credentials + feature + IAP explanations.
11. Privacy policy and support URLs fetched live: 200, right content, no
    sign-in wall.
12. Submit. Then read the version state back **fresh** (WAITING_FOR_REVIEW)
    — the submit click is not the proof.
13. On rejection: read the Resolution Center message verbatim and in full;
    note the guideline number(s); fix the root cause, not the symptom; use
    the Resolution Center reply when clarification alone resolves it; the
    App Review Board appeal exists (§0 overview) for genuine
    misunderstandings. Never resubmit the same build blind. **Log the
    rejection and its fix as a new permanent item in the app's regression
    checklist the same day.**
14. On approval with MANUAL release: release only on the account owner's
    explicit say-so. After release, verify READY_FOR_SALE by a fresh read
    before saying "live."

**Third-party scanner pass.** Before submission (after step 4, before the
submit in step 12), also run a deterministic static scanner against the app
tree — run the bundled scanner in `scanner/` (vendored from upstream
[app-store-review-risk](https://github.com/Kofiloski/app-store-review-risk);
see `scanner/NOTICE.md`), whose comparison against this playbook added
several checks to §A/§B. Its
greps (permission strings, required-reason APIs, steering language,
private-API patterns, placeholder text) catch a class this playbook
otherwise states only in prose. Treat its findings as leads, not verdicts:
verify every finding's file path belongs to the submitted target's own
source before acting — word-match hits in `Vendor/`, comments, and test
hosts are noise. Record dismissed findings with reasons in a config file in
the app repo (e.g. `.appstore-review-risk.yml`) so the next run starts from
the dispositions rather than from scratch.

## ASC API quirks (general, keep by the tools)

- The builds endpoint rejects `sort` parameters — omit them.
- When building a JWT for the ASC API, the key ID is a distinct claim
  (`kid` header) — a classic argument-order bug is putting the issuer ID
  where the key ID belongs.
- TestFlight seating is never automatic — explicit relationship POST +
  re-read (§A).
- Team invitations: web UI only; the API cannot create them (§0/§A).
- External-group public links stay "beta not found" until beta review
  clears the group's first build (§0 TestFlight).
