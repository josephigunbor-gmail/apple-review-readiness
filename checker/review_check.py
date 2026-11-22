#!/usr/bin/env python3
"""review_check.py — a first-party-only, report-only App Store review-readiness
static checker.

    python3 review_check.py <project-path> [--json] [--include-vendor]

Design rules (see checker/README.md for the full rationale):

  * REPORT ONLY. This tool never blocks a build, a submission, or anything
    else. Its exit code is 0 unless the invocation itself is invalid.
  * FIRST-PARTY CODE ONLY by default. Vendored SDK checkouts (Vendor/,
    Pods/, Carthage/, .build/, DerivedData/), test targets, and CI config
    are excluded from the scan, because word-match hits in code you did not
    write — and do not ship as your own — are the single largest source of
    scanner false positives. Pass --include-vendor to scan everything.
  * EVIDENCE OR IT DIDN'T HAPPEN. Every finding cites file:line and the
    matched text. Severities are only "warning" and "note" — a static scan
    cannot prove a rejection, so nothing here is labelled "critical".
  * COMMENTS ARE NOT CODE. Detection runs on comment-stripped source, so a
    doc comment about cancelling timers is not a subscription flow.

Standard library only. Python 3.10+.
"""

import argparse
import json
import os
import plistlib
import re
import sys

VERSION = "1.0.0"

# --------------------------------------------------------------------------
# Scan scope
# --------------------------------------------------------------------------

# Directories that hold code the submitting team did not write, or that are
# not part of the submitted app target. Pruned during the walk.
VENDOR_DIR_NAMES = {
    "Vendor", "Vendors", "Pods", "Carthage", "DerivedData",
    ".build", ".git", "node_modules", "checkouts", ".github",
}

CODE_EXTS = {".swift"}
TEXT_EXTS = {".swift", ".plist", ".strings", ".storyboard", ".xib"}


def is_test_dir(name):
    return name.endswith("Tests") or name.endswith("UITests")


def collect_files(root, include_vendor):
    """Return (code_files, text_files, manifests, stats) as relative paths."""
    code_files, text_files, manifests = [], [], []
    stats = {"scanned_files": 0, "excluded_files": 0}
    for dirpath, dirnames, filenames in os.walk(root):
        rel_dir = os.path.relpath(dirpath, root)
        keep = []
        for d in dirnames:
            if not include_vendor and (d in VENDOR_DIR_NAMES or is_test_dir(d)):
                stats["excluded_files"] += sum(
                    len(fs) for _, _, fs in os.walk(os.path.join(dirpath, d)))
                continue
            keep.append(d)
        dirnames[:] = keep
        for name in filenames:
            rel = os.path.normpath(os.path.join(rel_dir, name))
            ext = os.path.splitext(name)[1]
            if name == "PrivacyInfo.xcprivacy":
                manifests.append(rel)
                stats["scanned_files"] += 1
            elif ext in TEXT_EXTS:
                text_files.append(rel)
                stats["scanned_files"] += 1
                if ext in CODE_EXTS:
                    code_files.append(rel)
            else:
                stats["excluded_files"] += 1
    return sorted(code_files), sorted(text_files), sorted(manifests), stats


# --------------------------------------------------------------------------
# Source reading: comments are stripped (string-aware) before detection, so
# doc comments and commented-out code cannot produce findings.
# --------------------------------------------------------------------------

def strip_comments(text):
    """Return the source lines with // and /* */ comments removed.

    String literals are preserved (a URL inside a string is evidence, not a
    comment). This is a light lexical pass, not a full Swift parser.
    """
    out_lines = []
    in_block = False
    for raw in text.splitlines():
        res = []
        i, n = 0, len(raw)
        in_str = False
        while i < n:
            ch = raw[i]
            nxt = raw[i + 1] if i + 1 < n else ""
            if in_block:
                if ch == "*" and nxt == "/":
                    in_block = False
                    i += 2
                    continue
                i += 1
                continue
            if in_str:
                res.append(ch)
                if ch == "\\" and i + 1 < n:
                    res.append(raw[i + 1])
                    i += 2
                    continue
                if ch == '"':
                    in_str = False
                i += 1
                continue
            if ch == "/" and nxt == "*":
                in_block = True
                i += 2
                continue
            if ch == "/" and nxt == "/":
                break
            if ch == '"':
                in_str = True
            res.append(ch)
            i += 1
        out_lines.append("".join(res))
    return out_lines


class SourceIndex:
    """Comment-stripped lines for every scanned file, plus raw text."""

    def __init__(self, root, code_files, text_files):
        self.code_lines = {}   # rel -> [stripped line, ...]
        self.raw_text = {}     # rel -> raw text (text-scope files)
        for rel in text_files:
            path = os.path.join(root, rel)
            try:
                with open(path, encoding="utf-8", errors="replace") as fh:
                    raw = fh.read()
            except OSError:
                continue
            self.raw_text[rel] = raw
            if rel in code_files or rel.endswith(".swift"):
                self.code_lines[rel] = strip_comments(raw)

    def search(self, patterns, scope="code"):
        """First match per pattern: (pattern, rel, lineno, snippet)."""
        hits = []
        lines_map = self.code_lines if scope == "code" else {
            rel: txt.splitlines() for rel, txt in self.raw_text.items()}
        for pat in patterns:
            rx = re.compile(pat) if isinstance(pat, str) else pat
            found = None
            for rel in sorted(lines_map):
                for lineno, line in enumerate(lines_map[rel], 1):
                    m = rx.search(line)
                    if m:
                        found = (pat if isinstance(pat, str) else pat.pattern,
                                 rel, lineno, line.strip()[:120])
                        break
                if found:
                    break
            if found:
                hits.append(found)
        return hits

    def search_all(self, pattern, scope="code"):
        """Every match of one pattern: [(rel, lineno, snippet)]."""
        rx = re.compile(pattern) if isinstance(pattern, str) else pattern
        out = []
        lines_map = self.code_lines if scope == "code" else {
            rel: txt.splitlines() for rel, txt in self.raw_text.items()}
        for rel in sorted(lines_map):
            for lineno, line in enumerate(lines_map[rel], 1):
                if rx.search(line):
                    out.append((rel, lineno, line.strip()[:120]))
        return out


# --------------------------------------------------------------------------
# Findings
# --------------------------------------------------------------------------

class Rule:
    def __init__(self, rule_id, title, guideline):
        self.id = rule_id
        self.title = title
        self.guideline = guideline
        self.findings = []   # dicts: severity, message, evidence, fix
        self.notes = []      # pass / informational lines (strings)

    def warn(self, message, evidence=None, fix=None):
        self.findings.append({"severity": "warning", "message": message,
                              "evidence": evidence, "fix": fix})

    def note(self, message, evidence=None, fix=None):
        self.findings.append({"severity": "note", "message": message,
                              "evidence": evidence, "fix": fix})

    def passed(self, message):
        self.notes.append(message)

    @property
    def status(self):
        if any(f["severity"] == "warning" for f in self.findings):
            return "WARNING"
        if self.findings:
            return "NOTE"
        return "PASS"


def ev(hit):
    """Format a search hit as an evidence string."""
    _, rel, lineno, snippet = hit
    return f"{rel}:{lineno} — {snippet}"


# --------------------------------------------------------------------------
# Rule 1 — privacy manifest vs required-reason API usage
# --------------------------------------------------------------------------

# Category -> (manifest category name, strong patterns, weak patterns).
# Weak patterns only count when the same line names the API surface that
# makes them required-reason usage (avoids flagging e.g. a model's own
# `creationDate` property, which is not a required-reason API).
REQUIRED_REASON_APIS = {
    "UserDefaults": (
        "NSPrivacyAccessedAPICategoryUserDefaults",
        [r"\bUserDefaults\b", r"@AppStorage\b"],
        [],
    ),
    "FileTimestamp": (
        "NSPrivacyAccessedAPICategoryFileTimestamp",
        [r"NSFileCreationDate", r"NSFileModificationDate",
         r"NSURLCreationDateKey", r"NSURLContentModificationDateKey",
         r"FileAttributeKey\.(creationDate|modificationDate)"],
        [r"\.(creationDate|contentModificationDate)\b"],
    ),
    "DiskSpace": (
        "NSPrivacyAccessedAPICategoryDiskSpace",
        [r"attributesOfFileSystem", r"volumeAvailableCapacity",
         r"NSFileSystemFreeSize", r"NSFileSystemSize"],
        [],
    ),
    "SystemBootTime": (
        "NSPrivacyAccessedAPICategorySystemBootTime",
        [r"\bsystemUptime\b", r"mach_absolute_time"],
        [],
    ),
    "ActiveKeyboards": (
        "NSPrivacyAccessedAPICategoryActiveKeyboards",
        [r"\bactiveInputModes\b"],
        [],
    ),
}
WEAK_CONTEXT = re.compile(r"resourceValues|attributesOfItem|FileManager|URLResource")


def rule_privacy_manifest(root, index, manifests):
    rule = Rule(
        "PRIVACY-MANIFEST-APIS",
        "Privacy manifest declares every required-reason API the code uses",
        "Apple required-reason API policy (upload check ITMS-91053); "
        "App Review Guideline 5.1.1",
    )
    # What the first-party code actually uses.
    used = {}  # category label -> (manifest category, evidence hit)
    for label, (manifest_cat, strong, weak) in REQUIRED_REASON_APIS.items():
        hits = index.search(strong)
        if not hits and weak:
            for pat in weak:
                for rel, lineno, snippet in index.search_all(pat):
                    line = index.code_lines[rel][lineno - 1]
                    if WEAK_CONTEXT.search(line):
                        hits = [(pat, rel, lineno, snippet)]
                        break
                if hits:
                    break
        if hits:
            used[label] = (manifest_cat, hits[0])

    # What the manifest(s) declare.
    declared = {}  # manifest category -> manifest rel path
    parse_errors = []
    for rel in manifests:
        try:
            with open(os.path.join(root, rel), "rb") as fh:
                plist = plistlib.load(fh)
        except Exception as exc:  # unreadable manifest is itself a finding
            parse_errors.append((rel, str(exc)))
            continue
        for entry in plist.get("NSPrivacyAccessedAPITypes") or []:
            cat = entry.get("NSPrivacyAccessedAPIType")
            if cat:
                declared[cat] = rel

    for rel, exc in parse_errors:
        rule.warn(f"Privacy manifest {rel} could not be parsed ({exc}); "
                  "Apple rejects unreadable manifests at upload.",
                  evidence=rel,
                  fix="Fix the plist so it parses, then re-run this check.")

    if not manifests:
        if used:
            cats = ", ".join(sorted(c for c, _ in used.values()))
            rule.warn(
                "No PrivacyInfo.xcprivacy found in first-party scope, but "
                f"first-party code uses required-reason APIs ({cats}).",
                evidence=ev(next(iter(used.values()))[1]),
                fix="Add a PrivacyInfo.xcprivacy to the app target declaring "
                    "each used category under NSPrivacyAccessedAPITypes, "
                    "each with an approved reason code.")
        else:
            rule.note("No PrivacyInfo.xcprivacy found in first-party scope "
                      "and no required-reason API usage detected. A manifest "
                      "is still expected if any bundled SDK requires one.")
        return rule

    manifest_list = ", ".join(manifests)
    for label, (manifest_cat, hit) in sorted(used.items()):
        if manifest_cat not in declared:
            rule.warn(
                f"{label} is used in first-party code but "
                f"{manifest_cat} is not declared in "
                f"NSPrivacyAccessedAPITypes ({manifest_list}).",
                evidence=ev(hit),
                fix=f"Add an entry to NSPrivacyAccessedAPITypes with "
                    f"NSPrivacyAccessedAPIType = {manifest_cat} and an "
                    "approved NSPrivacyAccessedAPITypeReasons value "
                    "(e.g. CA92.1 for UserDefaults read by the app itself).")
    used_cats = {c for c, _ in used.values()}
    for cat, rel in sorted(declared.items()):
        if cat not in used_cats:
            rule.note(
                f"{cat} is declared in {rel} but no matching first-party "
                "usage was detected. Declared-but-unused is not a rejection "
                "risk; the category may be needed by a bundled SDK's own "
                "manifest instead — verify before removing.")
    if not rule.findings:
        rule.passed(
            "Every required-reason API category used in first-party code "
            f"is declared ({manifest_list}).")
    return rule


# --------------------------------------------------------------------------
# Rule 2 — account deletion (Guideline 5.1.1(v))
# --------------------------------------------------------------------------

def rule_account_deletion(index):
    rule = Rule(
        "ACCOUNT-DELETION",
        "Apps that create accounts offer in-app account deletion",
        "App Review Guideline 5.1.1(v)",
    )
    patterns = [
        r"(?i)delete\s+my\s+account",
        r"(?i)delete\s+account",
        r"deleteAccount",
        r"requestAccountDeletion",
        r"account-delete",
        r"account/delete",
        r"(?i)erase\s+(my\s+)?account",
    ]
    hits = index.search(patterns)
    if hits:
        rule.passed(
            "In-app account-deletion path found in first-party code: "
            + ev(hits[0]))
    else:
        rule.warn(
            "No in-app account-deletion path was found in first-party code. "
            "If the app supports account creation, Guideline 5.1.1(v) "
            "requires offering account deletion inside the app (not only on "
            "a website). Deletion labelled unusually, or hosted in a web "
            "view, will not be detected here — verify manually before "
            "concluding it is missing.",
            fix="Add a delete-account flow in the app's account/settings "
                "UI that initiates full account deletion, or confirm the "
                "existing flow and dismiss this warning with that evidence.")
    return rule


# --------------------------------------------------------------------------
# Rule 3 — Sign in with Apple alongside third-party social sign-in (4.8)
# --------------------------------------------------------------------------

SOCIAL_PATTERNS = [
    r"GIDSignIn", r"GoogleSignIn", r"signInWithGoogle",
    r"FBSDK", r"FacebookLogin",
    r"(?i)continue with (?!apple\b)[a-z]+",
    r"(?i)sign in with (?!apple\b)[a-z]+",
]
SIWA_PATTERNS = [
    r"ASAuthorization", r"SignInWithAppleButton",
    r"ASAuthorizationAppleIDProvider",
]


def rule_siwa(index):
    rule = Rule(
        "SIWA-WITH-SOCIAL",
        "Third-party social sign-in is paired with Sign in with Apple",
        "App Review Guideline 4.8",
    )
    social = index.search(SOCIAL_PATTERNS)
    if not social:
        rule.passed("No third-party social sign-in detected in first-party "
                    "code; Guideline 4.8 does not apply.")
        return rule
    siwa = index.search(SIWA_PATTERNS)
    if siwa:
        rule.passed(
            "Third-party social sign-in present (" + ev(social[0]) +
            ") and Sign in with Apple present (" + ev(siwa[0]) + ").")
    else:
        rule.warn(
            "Third-party social sign-in is offered (" + ev(social[0]) +
            ") but no Sign in with Apple implementation was found. "
            "Guideline 4.8 requires an equivalent privacy-preserving "
            "sign-in option — in practice, Sign in with Apple.",
            evidence=ev(social[0]),
            fix="Add Sign in with Apple (AuthenticationServices) wherever "
                "the third-party sign-in is offered.")
    return rule


# --------------------------------------------------------------------------
# Rule 4 — Restore Purchases, only where it actually applies
# --------------------------------------------------------------------------

STOREKIT_PATTERNS = [r"import StoreKit", r"\bProduct\.products\b"]
SUBSCRIPTION_PATTERNS = [
    r"autoRenewable", r"Product\.SubscriptionInfo", r"subscriptionStatus",
    r"isEligibleForIntroOffer",
]
NONCONSUMABLE_PATTERNS = [r"nonConsumable", r"\.nonConsumable\b"]
RESTORE_PATTERNS = [
    r"AppStore\.sync", r"restoreCompletedTransactions",
    r"(?i)restore purchases", r"func restore",
]


def rule_restore(index):
    rule = Rule(
        "RESTORE-PURCHASES",
        "Restore path exists if (and only if) restorable products are sold",
        "App Review Guideline 3.1.1",
    )
    storekit = index.search(STOREKIT_PATTERNS)
    if not storekit:
        rule.passed("No StoreKit usage detected in first-party code.")
        return rule
    restorable = index.search(SUBSCRIPTION_PATTERNS + NONCONSUMABLE_PATTERNS)
    if not restorable:
        consumable_mentions = sum(
            1 for rel, txt in index.raw_text.items()
            if rel.endswith(".swift") and "consumable" in txt.lower())
        extra = (f" {consumable_mentions} first-party file(s) describe the "
                 "products as consumables." if consumable_mentions else "")
        rule.passed(
            "StoreKit is used, but no auto-renewable subscription or "
            "non-consumable patterns were found in first-party code." +
            extra + " Consumables are not restorable by design, so no "
            "Restore Purchases UI is required.")
        return rule
    restore = index.search(RESTORE_PATTERNS)
    if restore:
        rule.passed(
            "Restorable product patterns present (" + ev(restorable[0]) +
            ") and a restore mechanism was found (" + ev(restore[0]) + ").")
    else:
        rule.warn(
            "Restorable products are sold (" + ev(restorable[0]) + ") but "
            "no restore mechanism (AppStore.sync, Transaction restore, or a "
            "Restore Purchases action) was found in first-party code.",
            evidence=ev(restorable[0]),
            fix="Add a visible Restore Purchases action that calls "
                "AppStore.sync() and re-delivers non-consumables / active "
                "subscriptions.")
    return rule


# --------------------------------------------------------------------------
# Rule 5 — privacy policy link in the app
# --------------------------------------------------------------------------

PRIVACY_PATTERNS = [
    r"https?://[^\s\"'\)]*privac[^\s\"'\)]*",
    r"Link\(\s*\"Privacy",
    r"\"Privacy [Pp]olicy\"",
    r"\bprivacyPolicy\b",
    r"PrivacyPolicyView",
]


def rule_privacy_policy(index):
    rule = Rule(
        "PRIVACY-POLICY-LINK",
        "Privacy policy is reachable from inside the app",
        "App Review Guideline 5.1.1 / 5.1.2",
    )
    hits = index.search(PRIVACY_PATTERNS, scope="text")
    if hits:
        rule.passed("Privacy policy reference found: " + ev(hits[0]))
    else:
        rule.warn(
            "No privacy policy URL or link was found in first-party code "
            "or resources. The policy must be reachable from inside the "
            "app as well as in the App Store Connect metadata field.",
            fix="Add a privacy policy link (Link/Button opening the "
                "hosted policy URL) in settings or the sign-in screen.")
    return rule


# --------------------------------------------------------------------------
# What no static tool can check — printed in every report, never "found".
# --------------------------------------------------------------------------

NOT_STATICALLY_CHECKABLE = [
    ("Demo / review account",
     "Whether the review credentials saved in App Store Connect still "
     "sign in today, and whether the backend they reach is up on review "
     "day."),
    ("Listing text",
     "Title, subtitle, description, keywords and promotional text as "
     "entered in App Store Connect for this version."),
    ("Screenshots and app previews",
     "Presence, required sizes, and whether they show the build actually "
     "being submitted."),
    ("Age-rating declarations",
     "The age-rating questionnaire answers and content descriptors filed "
     "in App Store Connect."),
    ("In-app purchase state",
     "Whether each product exists in App Store Connect, is cleared for "
     "sale, priced, and carries its review screenshot."),
    ("App Privacy labels",
     "Whether the data-use answers entered in App Store Connect match "
     "what the submitted binary actually does at runtime."),
    ("Review notes",
     "The notes, contact details, and attachments saved with the review "
     "submission."),
]


# --------------------------------------------------------------------------
# Rendering
# --------------------------------------------------------------------------

def render_text(project, stats, include_vendor, manifests, rules):
    lines = []
    lines.append("=" * 72)
    lines.append("App Review Readiness — static source check")
    lines.append("REPORT ONLY: this tool never blocks a build or a "
                 "submission. Exit code is always 0.")
    lines.append("=" * 72)
    lines.append(f"Project: {project}")
    scope = "first-party code (vendored/test/build dirs excluded)"
    if include_vendor:
        scope = "ALL files (--include-vendor)"
    lines.append(f"Scope: {scope}")
    lines.append(f"Files scanned: {stats['scanned_files']}  |  "
                 f"files excluded: {stats['excluded_files']}")
    if manifests:
        lines.append("Privacy manifests (first-party): "
                     + ", ".join(manifests))
    else:
        lines.append("Privacy manifests (first-party): none found")
    lines.append("")
    for rule in rules:
        lines.append("-" * 72)
        lines.append(f"[{rule.id}] {rule.title}")
        lines.append(f"Maps to: {rule.guideline}")
        lines.append(f"Status: {rule.status}")
        for note in rule.notes:
            lines.append(f"  PASS — {note}")
        for f in rule.findings:
            lines.append(f"  {f['severity'].upper()} — {f['message']}")
            if f.get("evidence"):
                lines.append(f"    Evidence: {f['evidence']}")
            if f.get("fix"):
                lines.append(f"    Fix: {f['fix']}")
        lines.append("")
    lines.append("-" * 72)
    lines.append("NOT STATICALLY CHECKABLE — verify in App Store Connect")
    lines.append("No source scan can see these. They are listed so their "
                 "absence from the findings above is not mistaken for a "
                 "pass:")
    for name, desc in NOT_STATICALLY_CHECKABLE:
        lines.append(f"  * {name}: {desc}")
    lines.append("")
    warnings = sum(1 for r in rules
                   for f in r.findings if f["severity"] == "warning")
    notes = sum(1 for r in rules
                for f in r.findings if f["severity"] == "note")
    passed = sum(1 for r in rules if r.status == "PASS")
    lines.append("-" * 72)
    lines.append(f"Summary: {passed}/{len(rules)} rules passed, "
                 f"{warnings} warning(s), {notes} note(s).")
    lines.append("Verify every finding against the cited line before "
                 "acting on it; dismiss with a recorded reason when the "
                 "evidence does not hold.")
    return "\n".join(lines) + "\n"


def render_json(project, stats, include_vendor, manifests, rules):
    return {
        "tool": "review_check.py",
        "version": VERSION,
        "report_only": True,
        "project": project,
        "scope": {
            "include_vendor": include_vendor,
            "files_scanned": stats["scanned_files"],
            "files_excluded": stats["excluded_files"],
            "privacy_manifests": manifests,
        },
        "rules": [
            {
                "id": r.id,
                "title": r.title,
                "guideline": r.guideline,
                "status": r.status,
                "passes": r.notes,
                "findings": r.findings,
            }
            for r in rules
        ],
        "not_statically_checkable": [
            {"item": name, "verify": desc}
            for name, desc in NOT_STATICALLY_CHECKABLE
        ],
    }


def main(argv=None):
    parser = argparse.ArgumentParser(
        description="First-party-only, report-only App Store "
                    "review-readiness static checker.")
    parser.add_argument("project", help="Path to the app project tree")
    parser.add_argument("--json", action="store_true",
                        help="Emit JSON instead of text")
    parser.add_argument("--include-vendor", action="store_true",
                        help="Also scan vendored/test/build directories "
                             "(default: excluded)")
    args = parser.parse_args(argv)

    root = os.path.abspath(args.project)
    if not os.path.isdir(root):
        print(f"error: {root} is not a directory", file=sys.stderr)
        return 2

    code_files, text_files, manifests, stats = collect_files(
        root, args.include_vendor)
    index = SourceIndex(root, set(code_files), text_files)

    rules = [
        rule_privacy_manifest(root, index, manifests),
        rule_account_deletion(index),
        rule_siwa(index),
        rule_restore(index),
        rule_privacy_policy(index),
    ]

    if args.json:
        print(json.dumps(
            render_json(root, stats, args.include_vendor, manifests, rules),
            indent=2))
    else:
        print(render_text(root, stats, args.include_vendor, manifests,
                          rules), end="")
    return 0


if __name__ == "__main__":
    sys.exit(main())
