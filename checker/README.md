# review_check.py — our own static checker

A small, dependency-free static checker for iOS app source trees, written
for this repo. It checks a handful of App Store review-readiness properties
that can genuinely be determined from source — and is explicit about the
ones that cannot.

```bash
python3 checker/review_check.py /path/to/your-app
python3 checker/review_check.py /path/to/your-app --json
python3 checker/review_check.py /path/to/your-app --include-vendor
```

Python 3.10+, standard library only. Nothing to install.

## The three rules this tool is built on

1. **Report only — it never blocks anything.** The exit code is 0 unless
   the invocation itself is invalid. A static scan cannot prove a
   rejection, so this tool advises; the submission decision (and the
   App Store Connect read-backs described in `../SKILL.md`) stays with
   you. Tools that hard-block a pipeline on word matches teach teams to
   override gates — the worst habit a ship process can learn.

2. **First-party code only.** By default the scan excludes vendored SDK
   checkouts (`Vendor/`, `Pods/`, `Carthage/`, `.build/`,
   `DerivedData/`), test targets, and CI configuration. Word-match hits
   in code you did not write are the largest single source of scanner
   false positives: a vendored SDK's internal CI fixture is not your
   staging backend, and its doc comment about cancelling timers is not
   your subscription flow. `--include-vendor` scans everything, when you
   really want that.

3. **Evidence or it didn't happen.** Every finding cites `file:line` and
   the matched text, names the guideline it maps to, and carries a
   concrete fix. Severities are only `warning` and `note` — there is no
   "critical", because a grep cannot establish that Apple will reject
   you. Detection also runs on comment-stripped source: comments are
   not code.

## What it checks

| Rule | Guideline | What it does |
|---|---|---|
| `PRIVACY-MANIFEST-APIS` | Required-reason API policy (ITMS-91053); 5.1.1 | Compares required-reason API usage in first-party Swift (UserDefaults, file timestamps, disk space, boot time, active keyboards) against the categories declared in `PrivacyInfo.xcprivacy`. Flags used-but-undeclared; reports declared-but-unused as a note only. |
| `ACCOUNT-DELETION` | 5.1.1(v) | Looks for an in-app account-deletion path. Absence is a warning to verify, worded as such — deletion labelled unusually will not be detected. |
| `SIWA-WITH-SOCIAL` | 4.8 | If third-party social sign-in is offered, checks that Sign in with Apple is present too. |
| `RESTORE-PURCHASES` | 3.1.1 | Demands a restore path **only** when auto-renewable subscription or non-consumable patterns are present. Consumable-only projects get a clean pass — consumables are not restorable by design. |
| `PRIVACY-POLICY-LINK` | 5.1.1 / 5.1.2 | Looks for a privacy policy URL or link in first-party code and resources. |

Every report ends with a **NOT STATICALLY CHECKABLE** section — demo
account liveness, listing text, screenshots, age-rating declarations,
IAP state in App Store Connect, privacy labels as entered, review
notes. No source scan can see those. The section is printed so that
their absence from the findings is never mistaken for a pass.

## What it deliberately does NOT do

- **No blocking, no hooks, no exit-code gates.** Wire it into CI as an
  informational step if you like; do not wire it as a veto.
- **No vendored-code scanning by default** (see above).
- **No App Store Connect state.** It reads a source tree, nothing else.
  Build verdicts still come only from fresh App Store Connect reads —
  see the main playbook.
- **No runtime claims.** It cannot tell you the app works, only that
  certain source-level properties hold.
- **Not a completeness promise.** Five rules, chosen because each one
  is deterministic enough to state with evidence. A short list that is
  right beats a long taxonomy that cries wolf.

## Verifying a finding

Open the cited line. If the evidence does not hold — the match is in a
string, a preview, a fixture that ships nowhere — dismiss the finding
and record the reason next to your submission notes. A finding you
cannot reproduce from its own citation is a bug in this tool; please
file it as one.
