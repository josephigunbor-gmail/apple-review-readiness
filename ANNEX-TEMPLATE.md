# Per-app annex — TEMPLATE

**Keep the filled annexes PRIVATE.** This template is the public part: the
*shape* of the per-app record that Section C of the playbook assumes. Your
filled values — app IDs, bundle IDs, stamp sets, demo credentials, internal
paths — are operationally sensitive. Keep them in a private repo, a password
manager, or a local notes file. Never commit a filled annex to a public
repository, and never paste one into a public issue or PR.

Copy this file once per app, fill every field, and run the filled annex
alongside `CHECKLIST.md` on submission day.

---

## App identity

- App name (as in App Store Connect):
- ASC app ID (numeric):
- Bundle ID:
- SKU:
- Developer team ID:
- Primary category / secondary category:

## Current state (date-stamp every update)

- Live version / build + state (e.g. READY_FOR_SALE):
- Version in review / in preparation + attached build:
- Latest internal (TestFlight) build + processing state:
- TestFlight groups (names; note internal vs external):

## Build provenance

- Source tree / repo + branch this app builds from (one canonical tree —
  note any sibling trees that must NOT be built from, and why):
- Build pipeline (Xcode / CI / alternative toolchain) + the one runbook that
  describes it:

## Validation assets

- Stamp-set source build: the known-good build produced by a released Xcode
  whose DT stamp set (DTXcode / DTSDKName / DTPlatformBuild / …) submission
  builds must carry. Record: build number, where its artifact lives, the
  exact stamp values.
- Asset catalog source: where the genuine `Assets.car` (+ launch storyboard
  + flat icons) was harvested from, and where the harvested copy is stored.
- Signing: profile name, capabilities it must carry, where the matched
  cert/password pair is verified (never store the values here — pointer
  only).

## Review access

- Demo pattern for this app (demo account / demo instance / demo mode):
- Demo data: how many synthetic records, what shape, where the demo backend
  lives:
- Review accounts that must stay active through the review window, and who
  owns keeping them alive:
- Review Notes location (draft file or ASC field owner):

## Listing

- Listing copy source of truth (file/doc) and whether it's entered in ASC:
- Screenshots: required sizes, capture plan, fictional-data confirmation,
  last verified-on-Apple's-side date:
- Age rating: expected outcome, the questionnaire answers that drive it,
  and any internal disagreements to reconcile at entry time:
- Privacy labels: declared data types, last reconciled against manifests +
  actual data flows on (date):

## IAP (if any)

- Product IDs, types (consumable / non-consumable / subscription), prices,
  territories, approval state:
- Restore behavior for restorable products:
- Agreement dependency: Paid Apps agreement / banking / tax status last
  read Active on (date):

## App-specific traps

The named, scar-earned items for THIS app. For each: what breaks, how it's
checked, and the proof that clears it. Examples of the shape (yours will
differ):

- [ ] Vendored-SDK binary check: which patched SDK behavior is verified in
      the compiled binary, the checker that does it, and the known-good /
      known-bad builds it was calibrated against.
- [ ] Consent gates: which attestations/consents gate which flows, where
      consent is recorded, and what existing-user grandfathering applies.
- [ ] Sign-in: which providers exist, which round-trips are proven on a
      device, which are still unproven.
- [ ] Regulated-field watch items (e.g. Guideline 5.1.1(ix) entity rule):
      status, and when it must be surfaced.
- [ ] Features that must work signed-out / offline, and how that's proven.

## Release discipline

- Release type (automatic / manual):
- Who may release, and any standing authorizations (or explicit
  "never release without asking" notes):
- Post-release verification: the fresh ASC read that proves READY_FOR_SALE.
