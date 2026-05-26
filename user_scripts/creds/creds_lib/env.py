"""Best-effort loader for `~/.zshenv` + `$CREDS_HOME/<svc>/creds.sh` so the
CLIs work even when invoked from a non-login context (cron, GUI launchers,
IDE runners) where zsh has not exported variables yet.

Layout (since 2026-05-19, single-file):
    ~/.zshenv                       — identity + pointer to creds loader.
    $CREDS_HOME/<svc>/creds.sh  — per-service config + secrets in one
                                       file (mode 600). Sourced by
                                       $CREDS_HOME/loader.sh via a
                                       `for f in *; do source $f; done`
                                       loop that the regex parser cannot
                                       follow — so we glob+load it here.

We only read simple `export FOO=BAR` / `export FOO="BAR"` / `FOO=BAR`
assignments. Anything with command substitution or conditionals is ignored —
those should be sourced by an interactive shell first.

Already-set variables in `os.environ` always win.
"""

from __future__ import annotations

import os
import re
import shlex
from pathlib import Path

_LINE = re.compile(r"^\s*(?:export\s+)?([A-Za-z_][A-Za-z0-9_]*)=(.*)$")

CREDS_GLOBS = ("*/creds.sh",)


def _expand(value: str) -> str:
    # honor existing env in $VAR / ${VAR} / ~
    value = os.path.expandvars(value)
    if value.startswith("~"):
        value = os.path.expanduser(value)
    return value


def _load_file(p: Path) -> dict[str, str]:
    out: dict[str, str] = {}
    if not p.exists():
        return out
    try:
        text = p.read_text(encoding="utf-8", errors="replace")
    except OSError:
        return out

    for raw in text.splitlines():
        line = raw.strip()
        if not line or line.startswith("#"):
            continue
        m = _LINE.match(line)
        if not m:
            continue
        key, val = m.group(1), m.group(2).strip()
        if "$(" in val or "`" in val:
            continue  # skip command substitutions
        # Strip trailing inline comment that is NOT inside quotes.
        try:
            tokens = shlex.split(val, comments=True, posix=True)
        except ValueError:
            continue
        if not tokens:
            continue
        value = _expand(tokens[0])
        if key not in os.environ:
            os.environ[key] = value
            out[key] = value
    return out


def load_zshenv(path: Path | None = None) -> dict[str, str]:
    """Parse `~/.zshenv` + every `$CREDS_HOME/<svc>/creds.sh` and merge
    into os.environ without overwriting already-set vars. Returns the dict of
    values it set (useful for debugging)."""
    p = path or Path.home() / ".zshenv"
    out: dict[str, str] = _load_file(p)

    creds_root = Path(os.environ.get("CREDS_HOME") or os.environ.get("CREDS_DIR") or (Path.home() / ".config" / "creds"))
    if creds_root.is_dir():
        for pattern in CREDS_GLOBS:
            for f in sorted(creds_root.glob(pattern)):
                out.update(_load_file(f))

    return out
