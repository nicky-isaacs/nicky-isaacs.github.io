#!/usr/bin/env python3
"""
PII guard — Claude Code Stop hook (project-scoped).

Scans recently modified or committed files for personal information that
should not live in a public git repository.

Exit codes:
  0  — no PII found, allow stop
  2  — PII found, re-invoke Claude with findings as context
"""

import json
import os
import re
import subprocess
import sys

# ── PII patterns ──────────────────────────────────────────────────────────────
LAST_NAME = "Isaacs"

PATTERNS = [
    # Last name: require a non-hyphen/non-letter boundary before it so
    # "nicky-isaacs" (GitHub slugs) doesn't false-positive.
    (r"(?<![a-zA-Z\-])" + re.escape(LAST_NAME) + r"(?![a-zA-Z])",
     re.IGNORECASE,
     "last name"),

    (r"[a-zA-Z0-9._%+\-]+@[a-zA-Z0-9.\-]+\.[a-zA-Z]{2,}",
     re.IGNORECASE,
     "email address"),

    (r"(\+?1[\s.\-]?)?\(?\d{3}\)?[\s.\-]\d{3}[\s.\-]\d{4}",
     0,
     "phone number"),

    # Street address: require full spelled-out type word (no Rd/St abbreviations)
    # to avoid false positives on things like "12 product teams" or "standards".
    (r"\b\d{1,4}\s+[A-Z][a-zA-Z]+(?: [A-Z][a-zA-Z]+)?\s+"
     r"(?:Street|Avenue|Boulevard|Drive|Road|Lane|Way|Court|Place|Circle|Terrace)\b",
     0,
     "street address"),

    (r"linkedin\.com/in/[a-zA-Z0-9_\-]+",
     re.IGNORECASE,
     "LinkedIn URL"),
]

# ── Allowlist ─────────────────────────────────────────────────────────────────
# Files permitted to contain PII-like strings (intentional or template).
ALLOWLIST_FILES = {
    "_config.yml",           # author.name is intentional public info
    "about.md",              # public bio — GitHub slug contains last name
    "_data/pii.yml",         # gitignored PII store — the correct place for PII
    "_data/pii.example.yml", # template with obvious placeholders
    "Gemfile", "Gemfile.lock", "Rakefile",
}

ALLOWLIST_PREFIXES = (
    "_site/",      # build output (gitignored)
    "_layouts/",   # Liquid templates — variable references, not literal PII
    "assets/",     # CSS, JS, images
    ".git/",
    ".claude/",    # this script itself
)

SKIP_EXTENSIONS = {
    ".pdf", ".png", ".jpg", ".jpeg", ".gif", ".ico",
    ".woff", ".woff2", ".ttf", ".eot", ".svg",
    ".lock", ".zip", ".tar", ".gz",
}


def get_target_files() -> set[str]:
    files: set[str] = set()

    cmds = [
        ["git", "diff", "--cached", "--name-only", "--diff-filter=ACMR"],
        ["git", "diff", "--name-only", "--diff-filter=ACMR"],
    ]
    # include last commit if a parent exists
    r = subprocess.run(
        ["git", "rev-parse", "--verify", "HEAD~1"],
        capture_output=True,
    )
    if r.returncode == 0:
        cmds.append(
            ["git", "diff", "HEAD~1", "HEAD", "--name-only", "--diff-filter=ACMR"]
        )

    for cmd in cmds:
        r = subprocess.run(cmd, capture_output=True, text=True)
        if r.returncode == 0 and r.stdout.strip():
            files.update(r.stdout.strip().splitlines())

    return {
        f for f in files
        if f
        and f not in ALLOWLIST_FILES
        and not any(f.startswith(p) for p in ALLOWLIST_PREFIXES)
        and not any(f.endswith(e) for e in SKIP_EXTENSIONS)
    }


def scan_file(path: str) -> list[tuple[str, int, str]]:
    findings = []
    if not os.path.isfile(path):
        return findings
    try:
        with open(path, encoding="utf-8", errors="ignore") as fh:
            for lineno, line in enumerate(fh, 1):
                for pattern, flags, label in PATTERNS:
                    if re.search(pattern, line, flags):
                        findings.append((label, lineno, line.rstrip()[:120]))
                        break
    except OSError:
        pass
    return findings


def main() -> None:
    try:
        data = json.loads(sys.stdin.read() or "{}")
    except Exception:
        data = {}

    # Prevent infinite re-invocation loops
    if data.get("stop_hook_active"):
        sys.exit(0)

    targets = get_target_files()
    if not targets:
        sys.exit(0)

    hits: list[tuple[str, str, int, str]] = []
    for path in sorted(targets):
        for label, lineno, snippet in scan_file(path):
            hits.append((path, label, lineno, snippet))

    if not hits:
        sys.exit(0)

    lines = [
        "⚠️  PII detected in modified or committed files.\n",
        "The following files appear to contain personal information that",
        "should not be committed to a public repository:\n",
    ]
    for path, label, lineno, snippet in hits:
        lines.append(f"  [{label}]  {path}:{lineno}")
        lines.append(f"    {snippet}\n")
    lines += [
        "Personal contact details belong in `_data/pii.yml` (gitignored),",
        "not in committed files. Please:",
        "  1. Remove or redact the PII from the files listed above.",
        "  2. Confirm with `git diff` or `git diff --cached`.",
        "  3. Ensure `_data/pii.yml` is in `.gitignore`.",
    ]

    output = "\n".join(lines)
    print(output)               # stdout → Claude re-invocation context
    print(output, file=sys.stderr)  # stderr → visible in transcript
    sys.exit(2)


if __name__ == "__main__":
    main()
