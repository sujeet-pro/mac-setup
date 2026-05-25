#!/usr/bin/env python3
"""inspect_keys.py — print the env-var KEY NAMES declared under
$CREDS_HOME/<svc>/{creds,config}.sh.

Never prints VALUES. Only key names + their classification:
  - SECRET    : key ends with _CRED  (must live in creds.sh)
  - NON_SECRET: key does not end with _CRED
  - ALIAS     : the line is `export X="$Y"` — flagged separately so
                the canonical key Y can be cross-referenced

Output is machine-readable JSON by default; pass --human for a table.

Usage:
    python3 inspect_keys.py
    python3 inspect_keys.py --human
    python3 inspect_keys.py --root /path/to/creds-dir
"""
from __future__ import annotations

import argparse
import json
import os
import re
import sys
from pathlib import Path

EXPORT_LINE = re.compile(
    r'^\s*export\s+(?P<key>[A-Za-z_][A-Za-z0-9_]*)=(?P<rhs>.*?)\s*(?:#.*)?$'
)
ALIAS_RE = re.compile(r'^["\']?\$\{?(?P<ref>[A-Za-z_][A-Za-z0-9_]*)\}?["\']?$')

SKIP_DIRS = {"_lib", "logs"}


def classify(key: str, rhs: str) -> tuple[str, str | None]:
    """Return (classification, alias_target) — alias_target is None unless ALIAS."""
    is_secret = key.endswith("_CRED")
    m = ALIAS_RE.match(rhs.strip())
    if m:
        return ("ALIAS_SECRET" if is_secret else "ALIAS_NON_SECRET", m.group("ref"))
    return ("SECRET" if is_secret else "NON_SECRET", None)


def keys_in(path: Path) -> list[dict[str, object]]:
    if not path.is_file():
        return []
    out: list[dict[str, object]] = []
    seen: set[str] = set()
    for raw in path.read_text(encoding="utf-8", errors="replace").splitlines():
        stripped = raw.strip()
        if not stripped or stripped.startswith("#"):
            continue
        m = EXPORT_LINE.match(stripped)
        if not m:
            continue
        key, rhs = m.group("key"), m.group("rhs")
        if key in seen:
            continue
        seen.add(key)
        cls, alias = classify(key, rhs)
        rec: dict[str, object] = {"key": key, "class": cls}
        if alias:
            rec["alias_target"] = alias
        out.append(rec)
    return out


def inspect(root: Path) -> dict[str, dict[str, list[dict[str, object]]]]:
    report: dict[str, dict[str, list[dict[str, object]]]] = {}
    if not root.is_dir():
        return report
    for svc_dir in sorted(root.iterdir()):
        if not svc_dir.is_dir() or svc_dir.name in SKIP_DIRS:
            continue
        creds = keys_in(svc_dir / "creds.sh")
        config = keys_in(svc_dir / "config.sh")
        if not creds and not config:
            continue
        report[svc_dir.name] = {"creds.sh": creds, "config.sh": config}
    return report


def hygiene_findings(report: dict[str, dict[str, list[dict[str, object]]]]) -> list[str]:
    """Flag obvious convention violations (no value exposure)."""
    issues: list[str] = []
    secret_classes = {"SECRET", "ALIAS_SECRET"}
    for svc, files in report.items():
        for k in files.get("config.sh", []):
            if k["class"] in secret_classes:
                issues.append(f"{svc}/config.sh has _CRED key '{k['key']}' — must live in creds.sh")
        # Layout note (informational, not a violation under the single-file design)
        config_keys = [k["key"] for k in files.get("config.sh", [])]
        if config_keys:
            issues.append(f"{svc}/config.sh still present — should be merged into creds.sh (keys: {', '.join(config_keys)})")
    return issues


def render_human(report: dict[str, dict[str, list[dict[str, object]]]]) -> str:
    out: list[str] = []
    for svc, files in report.items():
        out.append(f"=== {svc} ===")
        for fname in ("config.sh", "creds.sh"):
            keys = files.get(fname, [])
            if not keys:
                continue
            out.append(f"  {fname}:")
            for k in keys:
                tag = k["class"]
                target = f" → {k['alias_target']}" if "alias_target" in k else ""
                out.append(f"    [{tag}] {k['key']}{target}")
        out.append("")
    issues = hygiene_findings(report)
    if issues:
        out.append("--- hygiene findings ---")
        out.extend(f"  ! {i}" for i in issues)
    return "\n".join(out)


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument(
        "--root",
        type=Path,
        default=Path(os.environ.get("CREDS_DIR") or (Path.home() / ".config" / "creds")),
    )
    ap.add_argument("--human", action="store_true", help="Tabular output instead of JSON.")
    args = ap.parse_args()

    report = inspect(args.root)
    if args.human:
        print(render_human(report))
    else:
        print(json.dumps(
            {"root": str(args.root), "services": report, "hygiene": hygiene_findings(report)},
            indent=2,
        ))
    return 0


if __name__ == "__main__":
    sys.exit(main())
