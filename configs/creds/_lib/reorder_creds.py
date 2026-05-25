#!/usr/bin/env python3
"""reorder_creds.py — rewrite every $CREDS_HOME/<svc>/creds.sh so:

  * all comment lines and blank lines are dropped
  * every `export KEY=VALUE` is kept verbatim (value bytes untouched)
  * exports are grouped:
        1) non-secret  (key does NOT end with _CRED)  — alphabetical
        2) secret      (key DOES end with _CRED)      — alphabetical
        a single blank line separates the two groups
  * mode 0600, atomic temp+rename write
  * values are read into Python memory but NEVER printed or logged;
    the script reports key NAMES and counts only

The natural alphabetical sort groups related vars by their shared
prefix (DATADOG_*, GOOGLE_*, SLACK_*, …) without needing a hand-coded
grouping table. `_CRED` keys land at the bottom because the user can
visually skip over them once filled.

Usage:
    python3 reorder_creds.py
    python3 reorder_creds.py --dry-run
    python3 reorder_creds.py --root /path/to/creds-dir
"""
from __future__ import annotations

import argparse
import os
import re
import sys
from pathlib import Path

EXPORT_RE = re.compile(
    r"^\s*export\s+(?P<key>[A-Za-z_][A-Za-z0-9_]*)=(?P<rest>.*)$"
)
SKIP_DIRS = {"_lib", "logs"}


def reorder(text: str) -> tuple[str, list[str], list[str]]:
    """Return (new_text, non_secret_keys, secret_keys).

    Keeps only the first occurrence of each key (preserves whatever value
    the user has set there, even if accidentally duplicated).
    """
    by_key: dict[str, str] = {}
    for line in text.splitlines():
        m = EXPORT_RE.match(line)
        if not m:
            continue
        key = m.group("key")
        if key in by_key:
            continue
        # Re-emit with a single leading "export " (drops any leading whitespace)
        by_key[key] = f"export {key}={m.group('rest').rstrip()}"

    non_secret = sorted(k for k in by_key if not k.endswith("_CRED"))
    secret = sorted(k for k in by_key if k.endswith("_CRED"))

    lines: list[str] = []
    lines.extend(by_key[k] for k in non_secret)
    if non_secret and secret:
        lines.append("")  # separator
    lines.extend(by_key[k] for k in secret)

    out = "\n".join(lines)
    if out:
        out += "\n"
    return out, non_secret, secret


def run(root: Path, dry_run: bool) -> int:
    if not root.is_dir():
        print(f"reorder_creds: {root} is not a directory", file=sys.stderr)
        return 2
    changed = 0
    unchanged = 0
    for svc_dir in sorted(root.iterdir()):
        if not svc_dir.is_dir() or svc_dir.name in SKIP_DIRS:
            continue
        p = svc_dir / "creds.sh"
        if not p.is_file():
            continue
        text = p.read_text(encoding="utf-8")
        new_text, ns, sc = reorder(text)
        if new_text == text:
            unchanged += 1
            continue
        if dry_run:
            print(
                f"[dry-run] {svc_dir.name}: would reorder "
                f"{len(ns)} non-secret + {len(sc)} secret key(s), strip comments"
            )
            continue
        tmp = p.with_suffix(p.suffix + ".tmp")
        tmp.write_text(new_text, encoding="utf-8")
        os.chmod(tmp, 0o600)
        tmp.replace(p)
        print(
            f"{svc_dir.name}: reordered "
            f"({len(ns)} non-secret + {len(sc)} secret keys; comments stripped)"
        )
        changed += 1
    if changed == 0 and unchanged > 0 and not dry_run:
        print(f"nothing to do — {unchanged} file(s) already in canonical form")
    return 0


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument(
        "--root",
        type=Path,
        default=Path(os.environ.get("CREDS_DIR") or (Path.home() / ".config" / "creds")),
    )
    ap.add_argument("--dry-run", action="store_true", help="Report only; don't write.")
    args = ap.parse_args()
    return run(args.root, args.dry_run)


if __name__ == "__main__":
    sys.exit(main())
