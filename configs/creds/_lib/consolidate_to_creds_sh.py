#!/usr/bin/env python3
"""consolidate_to_creds_sh.py — one-time migration: fold every
$CREDS_HOME/<svc>/config.sh into the same directory's creds.sh, then
delete config.sh.

Safety:
  * Values are read into Python memory only to perform the rewrite. They
    are never printed to stdout/stderr. The script reports key NAMES and
    counts only.
  * If a key already exists in creds.sh, the config.sh line is dropped
    (the existing creds.sh value wins). This preserves the user's
    deliberate edits when keys live in both files.
  * Atomic write: temp file first, chmod 0600, then rename.
  * Idempotent: re-running after migration is a no-op (`config.sh` no
    longer exists, so each service reports "nothing to do").

Usage:
    python3 consolidate_to_creds_sh.py
    python3 consolidate_to_creds_sh.py --dry-run
    python3 consolidate_to_creds_sh.py --root /path/to/creds-dir
"""
from __future__ import annotations

import argparse
import os
import re
import sys
from pathlib import Path

EXPORT_RE = re.compile(r"^\s*export\s+([A-Za-z_][A-Za-z0-9_]*)=")
SKIP_DIRS = {"_lib", "logs"}


def parse_keys(text: str) -> list[str]:
    out: list[str] = []
    for line in text.splitlines():
        m = EXPORT_RE.match(line)
        if m:
            out.append(m.group(1))
    return out


def merge(creds_text: str, config_text: str) -> tuple[str, list[str], list[str]]:
    """Return (merged_text, keys_added, keys_skipped_as_duplicate)."""
    existing = set(parse_keys(creds_text))
    kept_lines: list[str] = []
    added: list[str] = []
    skipped: list[str] = []
    for line in config_text.splitlines():
        m = EXPORT_RE.match(line)
        if m:
            key = m.group(1)
            if key in existing:
                skipped.append(key)
                continue
            added.append(key)
            existing.add(key)
        kept_lines.append(line)

    body = "\n".join(kept_lines).rstrip("\n")
    base = creds_text.rstrip("\n")
    if base and body:
        merged = base + "\n\n# --- merged from former config.sh ---\n" + body + "\n"
    elif body:
        merged = body + "\n"
    else:
        merged = base + ("\n" if base else "")
    return merged, added, skipped


def migrate(root: Path, dry_run: bool) -> int:
    if not root.is_dir():
        print(f"consolidate: {root} is not a directory", file=sys.stderr)
        return 2

    any_action = False
    for svc_dir in sorted(root.iterdir()):
        if not svc_dir.is_dir() or svc_dir.name in SKIP_DIRS:
            continue
        config_p = svc_dir / "config.sh"
        creds_p = svc_dir / "creds.sh"
        if not config_p.is_file():
            continue
        any_action = True

        config_text = config_p.read_text(encoding="utf-8", errors="replace")
        creds_text = creds_p.read_text(encoding="utf-8", errors="replace") if creds_p.is_file() else ""
        merged, added, skipped = merge(creds_text, config_text)

        if dry_run:
            print(
                f"[dry-run] {svc_dir.name}: would add {len(added)} key(s) "
                f"[{', '.join(added) or '-'}]; would drop "
                f"{len(skipped)} duplicate(s) [{', '.join(skipped) or '-'}]"
            )
            continue

        tmp = creds_p.with_suffix(creds_p.suffix + ".tmp")
        tmp.write_text(merged, encoding="utf-8")
        os.chmod(tmp, 0o600)
        tmp.replace(creds_p)
        config_p.unlink()
        print(
            f"{svc_dir.name}: merged {len(added)} key(s) into creds.sh "
            f"[{', '.join(added) or '-'}], dropped {len(skipped)} duplicate(s) "
            f"[{', '.join(skipped) or '-'}], deleted config.sh"
        )
    if not any_action:
        print("nothing to do — no config.sh files present (already consolidated?)")
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
    return migrate(args.root, args.dry_run)


if __name__ == "__main__":
    sys.exit(main())
