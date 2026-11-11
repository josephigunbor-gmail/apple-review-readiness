# Apple review readiness — the one-page checklist

Run Section A for every upload. Run everything before an App Store submission.
Full reasoning and the fix for every item: `SKILL.md` in this repo. Verdicts
only from fresh App Store Connect reads — never from an upload response.

## 0 · What Apple says it checks (official baseline)

- [ ] Demo account or demo mode provided, backend live (Guidelines 2.1, Before You Submit)
- [ ] No crashes, no placeholder content, all URLs functional (2.1)
- [ ] IAP items complete, visible to the reviewer, functional — or explained in notes (2.1(b))
- [ ] Screenshots show the app in use, fictional accounts only (2.3.3, 2.3.9)
- [ ] New features described specifically in Notes for Review (2.3.1(a))
- [ ] Description/screenshots flag anything that costs extra (2.3.2)
- [ ] Age-rating questions answered honestly (2.3.6)
- [ ] Unlocking features uses In-App Purchase only (3.1.1); post "boosts" use IAP (3.1.3(g))
- [ ] App is more than a repackaged website (4.2)
- [ ] Social login present ⇒ Sign in with Apple offered too (4.8)
- [ ] Privacy policy linked in the listing AND in the app; states collection, uses, third parties, deletion (5.1.1(i))
- [ ] Purpose strings explain every data access clearly (5.1.1(ii))
- [ ] Account creation ⇒ account deletion inside the app (5.1.1(v))
- [ ] Regulated-field apps submitted by the providing legal entity (5.1.1(ix))
- [ ] Health data never used for ads/mining; no health info in iCloud (5.1.3)
- [ ] UGC apps: filter + report + block + published contact info (1.2)
- [ ] Medical apps disclose methodology; "check with a doctor" present (1.4.1)
- [ ] Support contact easy to find in app and Support URL (1.5)
- [ ] Privacy labels filed; SDK privacy manifests in the bundle (User Privacy and Data Use)
- [ ] TestFlight: internal groups need no review; a group's first external build needs beta approval (TestFlight)

## A · Automated validation (every upload)

- [ ] 1024 icon sits in a genuine Xcode-built Assets.car (harvested from a real build, never hand-built or forged)
- [ ] Bundle ID in the built artifact matches the App Store Connect record exactly
- [ ] Store version == MARKETING_VERSION, bumped in the same commit
- [ ] Build number new and higher than every build already in Connect
- [ ] DT* stamps present; submission build carries the app's genuine released-Xcode stamp set (per-app values in your private annex)
- [ ] Profile postdates capability changes and carries every entitlement (Sign in with Apple = `APPLE_ID_AUTH`)
- [ ] Signing cert + password verified as a matched pair before upload; legacy PKCS#12 format if macOS must import it
- [ ] `ITSAppUsesNonExemptEncryption` answered truthfully in Info.plist
- [ ] Required-reason APIs the app's own code uses (UserDefaults, file timestamps, disk space, boot time) are declared in the app's OWN PrivacyInfo.xcprivacy — SDK manifests don't substitute
- [ ] Every purpose string is specific to its visible feature — no short or generic filler ("needed", "required", "we need access")
- [ ] ATT/IDFA APIs in app code ⇒ `NSUserTrackingUsageDescription` + tracking declared in labels; none in code ⇒ labels say no tracking
- [ ] Fresh `GET /v1/builds` read shows this build VALID (no `sort` param — the endpoint rejects it)
- [ ] Build explicitly attached to its TestFlight group; group re-read confirms it

## B · Human review

- [ ] Demo account signs in today; demo backend is a separate instance; demo data is 100% synthetic
- [ ] Cold start, signed out: EVERY sign-in button visible without waiting on the network
- [ ] Sign in with Apple round-trip proven on a real device
- [ ] Account deletion works end to end (server + on-device wipe, first-run state on relaunch)
- [ ] Privacy + support URLs return 200 with the right content, no sign-in wall
- [ ] Paid Apps agreement + banking + tax read **Active** (Processing = StoreKit serves nothing, on every app)
- [ ] IAP products return in the app, priced, territories set; restore path exists for restorable purchases
- [ ] UGC: report/block/delete all work; listing never claims pre-moderation you don't do
- [ ] Nothing anywhere says "coming soon", lorem, or test
- [ ] No external-purchase steering language ("subscribe on the web", "Stripe checkout", "billing portal", …) — or the current storefront rules are checked for every enabled storefront
- [ ] Every `UIBackgroundModes` entry maps to a visible feature and is explained in Review Notes
- [ ] No screen kicks the user out to a browser; password reset finishes in-app
- [ ] Health apps: self-checks never presented as diagnosis; "not a substitute for professional care" + crisis info in the listing; crisis features work signed-out and offline
- [ ] Voice features: no voiceprint/biometric derivation without written notice + release; live-only features record and store nothing
- [ ] Vendored SDK patches verified at the binary level on this exact build (calibrated check, not source review)
- [ ] Review Notes explain every non-obvious feature like the reviewer is a stranger

## C · Per-app annex (private — do not publish)

Keep one annex per app in your own private notes using `ANNEX-TEMPLATE.md`,
and run it alongside this checklist on submission day. Typical annex items:

- [ ] Built from the correct source tree/branch for this app
- [ ] Stamp set + asset catalog harvested from this app's known-good source build
- [ ] Demo/review accounts still active for the whole review window
- [ ] Age-rating answers reconciled against shipped features at entry time
- [ ] App-specific binary checks pass (vendored SDK patches, patched frameworks)
- [ ] App-specific consent gates and regulated-field watch items reviewed
- [ ] Release discipline for this app confirmed (who may release, manual vs automatic)

## D · Submission day, in order

1. [ ] Final build frozen; Section A green; fresh read: VALID
2. [ ] Static source scanner run (e.g. app-store-review-risk); every finding verified against the submitted target's own files; dismissals recorded with reasons
3. [ ] Build attached to the version; version page re-read to confirm
4. [ ] Cold-start smoke + full regression checklist pass on this build; tallies read (0 failed / 0 skipped)
5. [ ] Metadata + screenshots + privacy labels + age rating verified **on Apple's side**
6. [ ] Demo access tested today; Review Notes complete
7. [ ] Submit → fresh read shows WAITING_FOR_REVIEW
8. [ ] Rejection? Read Resolution Center verbatim → fix root cause → log a new regression item → resubmit (never blind)
9. [ ] Approved + manual release? Release only on the account owner's word → fresh read shows READY_FOR_SALE before saying "live"
