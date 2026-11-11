# Apple Review Readiness

An agent skill + one-page checklist for getting an iOS app through Apple's review —
built from Apple's own documentation and from real rejection scars.

Most pre-submission checklists cover what a human reviewer looks for. This one
covers **two layers**:

1. **Apple's documented baseline** — the App Review Guidelines, the App Review
   overview page, the TestFlight page, App Store Connect Help, and Apple's
   privacy/data-use documentation, distilled into checks with the guideline
   number attached to each one.
2. **The binary-validation layer most checklists miss** — the automated checks
   Apple's machines run before a human ever sees your app: icon asset catalogs
   that must be genuinely produced by `actool`, build-stamp (`DTXcode`/SDK)
   coherence, version mismatches that silently flip a processed build to
   **INVALID**, and verifying a build's state by reading App Store Connect
   fresh instead of trusting an upload response.

Every check in this repo comes paired with its **Fix** — the specific action
that clears it. A checklist that only tells you what's wrong is half a tool.

## Who it's for

- Indie and small-team iOS developers submitting to the App Store.
- Anyone building with a non-standard pipeline (CI without a Mac on the final
  step, cross-platform toolchains, alternative builders) — that's where the
  binary-validation failures live.
- Teams using AI coding agents: the playbook is written as an agent skill, so
  your agent can run it as a pre-submission gate instead of a human skimming
  a wiki page the night before a release.

## What's in here

| File | What it is |
|---|---|
| `SKILL.md` | The full playbook: when to run it, verdict rules, the official baseline (Section 0), machine validation (Section A), human-review readiness (Section B), and the submission-day run order (Section D). |
| `CHECKLIST.md` | The same thing as a one-page scannable checklist, for a human on submission day. |
| `ANNEX-TEMPLATE.md` | A blank per-app annex template — the per-app facts (IDs, stamp sources, demo access, app-specific traps) that belong in your **private** notes, not in a public repo. |
| `scanner/` | A bundled static source scanner — **not ours**: app-store-review-risk by Kristijan Kofiloski, vendored under the MIT License (see "The bundled scanner" below and `scanner/NOTICE.md`). |
| `LICENSE` | MIT — covers the skill, checklist, and annex template in this repo. The bundled scanner carries its own MIT license in `scanner/LICENSE`. |

## Install as an agent skill

Clone this repo into your agent's skills directory, e.g.:

```bash
git clone https://github.com/josephigunbor-gmail/apple-review-readiness \
  ~/.claude/skills/apple-review-readiness
```

(The exact folder differs by agent — Claude Code, Codex, and compatible tools
all discover skills as a folder containing a `SKILL.md`.) Then ask your agent
to run the apple-review-readiness skill before a submission.

## Run the checklist manually

Open `CHECKLIST.md` and work top to bottom:

- **Section A** runs for *every* upload, including internal TestFlight builds.
- **Everything** runs before an App Store submission.

The one rule that matters most: **take a build's verdict only from a fresh
App Store Connect read** — never from the upload tool's success message.
Upload responses lie by omission; the processed build resource doesn't.

## What's included — and whose it is

Two tools, two authors:

- **The skill, checklist, and annex template** (`SKILL.md`, `CHECKLIST.md`,
  `ANNEX-TEMPLATE.md`) — this project's own work, MIT (see `LICENSE`).
  They verify state and behavior: the documented baseline plus the
  binary-validation layer.
- **The bundled scanner** (`scanner/`) — **app-store-review-risk v0.3.3 by
  Kristijan Kofiloski**, a deterministic static scanner for your *source*
  (permission strings, required-reason APIs, steering language, private-API
  patterns). It is included here under the MIT License — his copyright and
  license text live in `scanner/LICENSE`, with provenance in
  `scanner/NOTICE.md`. Several checks in Sections A and B were folded in
  from comparing this playbook against it.

## The bundled scanner

Run it from this repo — no separate download needed:

```bash
# Option 1: install the bundled copy, then scan
python3 -m pip install ./scanner
app-store-review-risk /path/to/your-app --submitted-target YourAppTarget

# Option 2: run it in place, nothing installed
PYTHONPATH=scanner/src python3 -m app_store_review_risk /path/to/your-app
```

(Python 3.10+. The scanner also ships as a GitHub Action —
`scanner/action/action.yml`; from a workflow in your own repo, check out
this repo and reference it as a local action, e.g. `uses: ./scanner/action`.)

Discipline when you run it: verify each finding against your submitted
target's own files before acting — word-match hits in vendored code and
comments are noise — record dismissals with reasons, then let this playbook
make the final call.

Upstream is the canonical source and this vendored copy may lag it: star or
watch [Kofiloski/app-store-review-risk](https://github.com/Kofiloski/app-store-review-risk)
for the latest version.

## Keeping it current

Apple revises the guidelines and the upload requirements regularly. Section 0
citations were verified against Apple's live pages when this was published;
if a guideline number and its current text disagree, Apple's page wins —
open an issue or a PR.

This playbook is also maintained from live submission experience: when a
real build or review teaches a new lesson, the generalized pattern — check
plus fix, never any app-specific detail — is added here so the checklist
keeps growing.

## License

The skill, checklist, and annex template are MIT — see `LICENSE`. Use it,
fork it, ship your app. The bundled scanner under `scanner/` is
© Kristijan Kofiloski, likewise MIT — see `scanner/LICENSE` and
`scanner/NOTICE.md`.

---

*Published by Joseph Igunbor. Distilled from production submissions across
several shipping apps; the per-app details stay in private annexes, the
patterns are here.*
