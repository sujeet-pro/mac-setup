#!/usr/bin/env python3
"""strip_aliases.py — remove tool-compat alias lines from every
~/.config/creds/<svc>/creds.sh in place.

An "alias" here is a line of the form:

    export X="$Y"      or      export X="${Y}"      or      export X=$Y

i.e. the RHS is exactly one variable reference. Path constants like

    export GOOGLE_CREDENTIALS_FILE="$HOME/.config/creds/google/google.token.json"

are NOT touched (their RHS combines `$HOME` with a path suffix, so the
regex won't match).

Also removes a single immediately-preceding "# Tool-compat alias …"
comment line if present, plus any blank line orphaned between two
removals — cosmetic only.

Safety:
  * Values stay in the file's untouched lines. The script only
    rewrites the file at line-level; it never prints values.
  * Reports key NAMES removed only.
  * Atomic write (temp + chmod 0600 + rename); idempotent.

Usage:
    python3 strip_aliases.py             # rewrites every <svc>/creds.sh
    python3 strip_aliases.py --dry-run   # preview only
    python3 strip_aliases.py --root /path/to/creds-dir
"""
from __future__ import annotations

import argparse
import os
import re
import sys
from pathlib import Path

EXPORT_RE = re.compile(
    r"^\s*export\s+(?P<key>[A-Za-z_][A-Za-z0-9_]*)=(?P<rhs>.*?)\s*(?:#.*)?$"
)
PURE_ALIAS_RHS = re.compile(r'^["\']?\$\{?[A-Za-z_][A-Za-z0-9_]*\}?["\']?$')

ALIAS_COMMENT_RE = re.compile(r"^\s*#.*\b(alias|tool-?compat|sdk[- ]compat)\b", re.IGNORECASE)

SKIP_DIRS = {"_lib", "logs"}


def strip(text: str) -> tuple[str, list[str]]:
    """Return (new_text, removed_keys)."""
    lines = text.splitlines()
    out: list[str] = []
    removed: list[str] = []
    i = 0
    while i < len(lines):
        line = lines[i]
        m = EXPORT_RE.match(line)
        if m and PURE_ALIAS_RHS.match(m.group("rhs").strip()):
            # Drop this line.  Also drop a single preceding "# alias …"
            # comment if it directly introduces this export.
            if out and ALIAS_COMMENT_RE.match(out[-1]):
                out.pop()
                # And drop a blank line above that, if any.
                if out and out[-1].strip() == "":
                    out.pop()
            removed.append(m.group("key"))
            i += 1
            continue
        out.append(line)
        i += 1

    # Collapse runs of blank lines created by removals.
    cleaned: list[str] = []
    for line in out:
        if line.strip() == "" and cleaned and cleaned[-1].strip() == "":
            continue
        cleaned.append(line)
    # Trim trailing blanks.
    while cleaned and cleaned[-1].strip() == "":
        cleaned.pop()
    text_out = "\n".join(cleaned) + "\n"
    return text_out, removed


def run(root: Path, dry_run: bool) -> int:
    if not root.is_dir():
        print(f"strip_aliases: {root} is not a directory", file=sys.stderr)
        return 2
    any_action = False
    for svc_dir in sorted(root.iterdir()):
        if not svc_dir.is_dir() or svc_dir.name in SKIP_DIRS:
            continue
        creds_p = svc_dir / "creds.sh"
        if not creds_p.is_file():
            continue
        text = creds_p.read_text(encoding="utf-8")
        new_text, removed = strip(text)
        if not removed:
            continue
        any_action = True
        if dry_run:
            print(f"[dry-run] {svc_dir.name}: would remove {len(removed)} alias(es): {', '.join(removed)}")
            continue
        tmp = creds_p.with_suffix(creds_p.suffix + ".tmp")
        tmp.write_text(new_text, encoding="utf-8")
        os.chmod(tmp, 0o600)
        tmp.replace(creds_p)
        print(f"{svc_dir.name}: removed {len(removed)} alias(es): {', '.join(removed)}")
    if not any_action:
        print("no alias exports found (already stripped?)")
    return 0


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument(
        "--root",
        type=Path,
        default=Path(os.environ.get("CREDS_DIR") or (Path.home() / ".config" / "creds")),
    )
    ap.add_argument("--dry-run", action="store_true", help="Report what would change; don't write.")
    args = ap.parse_args()
    return run(args.root, args.dry_run)


if __name__ == "__main__":
    sys.exit(main())
