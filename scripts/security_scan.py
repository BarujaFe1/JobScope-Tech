#!/usr/bin/env python3
"""Secret/PII scan over git-tracked files. Exit 1 on any finding.

Secret patterns: cloud/API keys, tokens, private keys, .env files.
PII patterns: CPF, e-mails (except placeholder domains), BR phone numbers.
"""

from __future__ import annotations

import re
import subprocess
import sys
from pathlib import Path

SECRET_PATTERNS: dict[str, re.Pattern[str]] = {
    "aws_access_key": re.compile(r"AKIA[0-9A-Z]{16}"),
    "github_token": re.compile(r"gh[pousr]_[A-Za-z0-9]{20,}"),
    "github_fine_grained": re.compile(r"github_pat_[A-Za-z0-9_]{20,}"),
    "slack_token": re.compile(r"xox[baprs]-[A-Za-z0-9-]+"),
    "anthropic_key": re.compile(r"sk-ant-[A-Za-z0-9_-]{20,}"),
    "openai_key": re.compile(r"sk-proj-[A-Za-z0-9_-]{20,}"),
    "generic_api_key_assign": re.compile(r"(?i)(api_?key|secret|password)\s*[:=]\s*['\"][^'\"\s]{12,}['\"]"),
    "private_key_block": re.compile(r"-----BEGIN [A-Z ]*PRIVATE KEY-----"),
}

PII_PATTERNS: dict[str, re.Pattern[str]] = {
    "cpf": re.compile(r"\b\d{3}\.?\d{3}\.?\d{3}[-.]?\d{2}\b"),
    "email": re.compile(r"\b[\w.%-]+@[\w.-]+\.[a-zA-Z]{2,}\b"),
    # require structure (country code / parens / separators) so numeric
    # data values (e.g. Jaccard decimals) don't false-positive
    "br_phone": re.compile(
        r"(?:\(?\+?\s?55\)?[\s-])?\(\d{2}\)\s?9?\d{4}[-\s]?\d{4}\b|\b9\s?\d{4}[-]\d{4}\b"
    ),
}

EMAIL_ALLOWLIST = {
    "@example.",  # RFC 2606 placeholders
    "@users.noreply.github.com",
    "@sentry.io",
    "@usp.br",  # author public contact in docs/commits metadata is intentional
}

SKIP_SUFFIXES = {".png", ".jpg", ".ico", ".svg", ".lock", ".woff", ".woff2"}
SKIP_NAMES = {"package-lock.json"}
ENV_FILENAMES = {".env", ".env.local", ".env.production"}


def tracked_files() -> list[Path]:
    out = subprocess.run(
        ["git", "ls-files"], capture_output=True, text=True, check=True
    ).stdout
    return [Path(line) for line in out.splitlines() if line]


def main() -> int:
    findings: list[str] = []
    for path in tracked_files():
        name = path.name.lower()
        if name in ENV_FILENAMES:
            findings.append(f"ENV_FILE {path}: environment file committed")
            continue
        if path.suffix.lower() in SKIP_SUFFIXES or name in SKIP_NAMES:
            continue
        try:
            content = path.read_text(encoding="utf-8")
        except (UnicodeDecodeError, OSError):
            continue

        for label, pattern in SECRET_PATTERNS.items():
            for match in pattern.finditer(content):
                findings.append(f"SECRET:{label} {path}:{content[:match.start()].count(chr(10)) + 1}")

        for label, pattern in PII_PATTERNS.items():
            for match in pattern.finditer(content):
                token = match.group(0)
                if label == "email" and any(a in token for a in EMAIL_ALLOWLIST):
                    continue
                findings.append(f"PII:{label} {path}:{content[:match.start()].count(chr(10)) + 1} -> {token}")

    if findings:
        print("SECURITY SCAN FAILED:")
        for f in sorted(set(findings)):
            print(f"  - {f}")
        return 1
    print("security scan: OK (no secrets/PII in tracked files)")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
