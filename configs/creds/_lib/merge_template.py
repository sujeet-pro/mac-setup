#!/usr/bin/env python3
"""Merge a creds template into a live creds file without overwriting values.

Used by `roles/creds/` to install / refresh `~/.config/creds/<svc>/creds.sh`
and `~/.config/creds/<svc>/config.sh` from the per-3P templates under
`mac-setup/configs/creds/<svc>/`.

Behaviour:
    1. If TARGET does not exist → copy SOURCE verbatim, set mode.
    2. If TARGET exists:
       - Parse SOURCE and TARGET for `export KEY=...` / `# export KEY=...`
         declarations (the latter is a commented placeholder, still tracked).
       - For every KEY tracked in SOURCE but missing from TARGET → append the
         SOURCE line under a clearly-delimited "auto-added" trailer.
       - For every KEY present in TARGET but NOT tracked in SOURCE → ensure
         there is a `# untracked-by-mac-setup` comment on the line immediately
         above. Idempotent — never duplicates the comment.
    3. Never edits an existing tracked key's value.

Exit code:
    0 = no changes or merge succeeded.
    Non-zero = unrecoverable error (missing source, unwritable target, etc.).

Stdlib only. Read every line; preserve user formatting / comments / order.
"""
from __future__ import annotations

import argparse
import datetime as dt
import os
import re
import shutil
import stat
import sys
from pathlib import Path

# Match `export KEY=...` or `# export KEY=...` (a commented placeholder).
# The KEY-extraction works for both forms; the value is everything after `=`.
_EXPORT_LINE = re.compile(
    r"""^
        (?P<lead>\s*\#?\s*)                # optional leading comment marker + ws
        export\s+
        (?P<key>[A-Za-z_][A-Za-z0-9_]*)    # the variable name
        =                                  # assignment
        (?P<val>.*)$                       # value
    """,
    re.VERBOSE,
)

_UNTRACKED_MARKER = "# untracked-by-mac-setup"
_ADDED_HEADER = "# --- auto-added by mac-setup"


def _parse_keys(text: str) -> set[str]:
    """Return the set of every KEY declared (export or commented export)."""
    out: set[str] = set()
    for line in text.splitlines():
        m = _EXPORT_LINE.match(line)
        if m:
            out.add(m.group("key"))
    return out


def _line_key(line: str) -> str | None:
    m = _EXPORT_LINE.match(line)
    return m.group("key") if m else None


def _new_target(source: Path, target: Path, mode: int) -> None:
    target.parent.mkdir(parents=True, exist_ok=True)
    shutil.copyfile(source, target)
    os.chmod(target, mode)


def _merge(source_text: str, target_text: str) -> tuple[str, list[str], list[str]]:
    """Return (new_target_text, keys_added, keys_marked_untracked)."""
    source_keys = _parse_keys(source_text)
    target_lines = target_text.splitlines()
    target_keys = _parse_keys(target_text)

    # --- Step 1: ensure every untracked line has the marker comment above it ---
    marked: list[str] = []
    new_lines: list[str] = []
    for idx, line in enumerate(target_lines):
        key = _line_key(line)
        if key and key not in source_keys:
            # Check the line directly above (in the output stream) for an
            # existing marker; if absent, insert one.
            prev = new_lines[-1].strip() if new_lines else ""
            if not prev.startswith(_UNTRACKED_MARKER):
                # Preserve indentation of the export line for the comment.
                indent = re.match(r"^(\s*)", line).group(1)
                new_lines.append(f"{indent}{_UNTRACKED_MARKER} — remove or migrate to a tracked key")
                marked.append(key)
        new_lines.append(line)

    # --- Step 2: append any tracked keys missing from the target ---
    missing = sorted(source_keys - target_keys)
    if missing:
        # Pull the original source line for each missing key (preserves the
        # template's intended placeholder value + any inline comment).
        src_by_key: dict[str, str] = {}
        for line in source_text.splitlines():
            k = _line_key(line)
            if k and k in missing and k not in src_by_key:
                src_by_key[k] = line
        if new_lines and new_lines[-1].strip() != "":
            new_lines.append("")
        ts = dt.date.today().isoformat()
        new_lines.append(f"{_ADDED_HEADER} on {ts} — fill these in then remove this header ---")
        for k in missing:
            new_lines.append(src_by_key.get(k, f"# export {k}="))

    # Preserve a trailing newline (POSIX hygiene).
    text = "\n".join(new_lines)
    if not text.endswith("\n"):
        text += "\n"
    return text, missing, marked


def main(argv: list[str] | None = None) -> int:
    p = argparse.ArgumentParser(description=__doc__.split("\n", 1)[0])
    p.add_argument("source", type=Path, help="Path to template file (in repo).")
    p.add_argument("target", type=Path, help="Path to live file (under ~/.config/creds/<svc>/).")
    p.add_argument(
        "--mode",
        type=lambda s: int(s, 8),
        default=0o600,
        help="Octal mode for newly-created targets (default: 0600 for creds.sh; pass 0644 for config.sh).",
    )
    p.add_argument(
        "--quiet",
        action="store_true",
        help="Suppress per-file 'no change' lines; still report mutations.",
    )
    args = p.parse_args(argv)

    if not args.source.is_file():
        print(f"merge_template: source missing: {args.source}", file=sys.stderr)
        return 2

    if not args.target.exists():
        _new_target(args.source, args.target, args.mode)
        print(f"merge_template: created {args.target}")
        return 0

    src_text = args.source.read_text(encoding="utf-8")
    tgt_text = args.target.read_text(encoding="utf-8")
    new_text, added, marked = _merge(src_text, tgt_text)

    if new_text == tgt_text:
        if not args.quiet:
            print(f"merge_template: no change   {args.target}")
        return 0

    # Atomic write preserves mode + ownership of the existing target.
    st = args.target.stat()
    tmp = args.target.with_suffix(args.target.suffix + ".tmp")
    tmp.write_text(new_text, encoding="utf-8")
    os.chmod(tmp, stat.S_IMODE(st.st_mode))
    tmp.replace(args.target)

    bits = []
    if added:
        bits.append(f"added {len(added)} key(s): {', '.join(added)}")
    if marked:
        bits.append(f"marked {len(marked)} untracked: {', '.join(marked)}")
    print(f"merge_template: updated {args.target} — {'; '.join(bits)}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
