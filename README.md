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
| `LICENSE` | MIT. |

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

## Pair it with a source scanner

This playbook verifies state and behavior. For a deterministic static scan of
your *source* (permission strings, required-reason APIs, steering language,
private-API patterns), pair it with
[app-store-review-risk](https://github.com/Kofiloski/app-store-review-risk)
by Kristijan Kofiloski — a complementary scanner whose checks informed several
items in Sections A and B here. Run the scanner, verify each finding against
your submitted target's own files (word-match hits in vendored code and
comments are noise), record dismissals with reasons, then let this playbook
make the final call.

## Keeping it current

Apple revises the guidelines and the upload requirements regularly. Section 0
citations were verified against Apple's live pages when this was published;
if a guideline number and its current text disagree, Apple's page wins —
open an issue or a PR.

## License

MIT — see `LICENSE`. Use it, fork it, ship your app.

---

*Published by Joseph Igunbor. Distilled from production submissions across
several shipping apps; the per-app details stay in private annexes, the
patterns are here.*
