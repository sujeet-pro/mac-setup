"""Safe read/write helpers for $CREDS_HOME/<svc>/creds.sh files.

We never echo a credential value to stdout/stderr. `set_value()` reads the
file into memory, replaces the value of a specific `export KEY=...` line,
and writes atomically back with the file's existing mode (usually 0600).
"""

from __future__ import annotations

import os
import re
import shlex
import stat
from pathlib import Path

from . import CREDS_DIR

# Matches `export KEY=...` (uncommented) and captures key+value.
_EXPORT_LINE = re.compile(
    r"^(?P<lead>\s*)export\s+(?P<key>[A-Za-z_][A-Za-z0-9_]*)=(?P<val>.*)$"
)


def creds_sh_path(svc: str) -> Path:
    return CREDS_DIR / svc / "creds.sh"


def keys_in_file(path: Path) -> list[str]:
    """Return uncommented `export KEY=...` keys in file order."""
    if not path.is_file():
        return []
    out: list[str] = []
    for line in path.read_text(encoding="utf-8").splitlines():
        m = _EXPORT_LINE.match(line)
        if m:
            out.append(m.group("key"))
    return out


def has_placeholder(path: Path, key: str) -> bool:
    """True if the line `export KEY=...` still has PLACEHOLDER_FILL_ME."""
    if not path.is_file():
        return False
    for line in path.read_text(encoding="utf-8").splitlines():
        m = _EXPORT_LINE.match(line)
        if m and m.group("key") == key:
            return "PLACEHOLDER_FILL_ME" in m.group("val")
    return False


def set_value(path: Path, key: str, value: str) -> bool:
    """Replace the value of `export KEY=...` with `value`.

    Atomic write; preserves the file's existing mode. Returns True if the
    key was found and updated, False if the key isn't declared in the file.
    The value never leaves this function via print/log.
    """
    if not path.is_file():
        raise FileNotFoundError(path)
    quoted = shlex.quote(value)
    new_lines: list[str] = []
    found = False
    for line in path.read_text(encoding="utf-8").splitlines():
        m = _EXPORT_LINE.match(line)
        if m and m.group("key") == key and not found:
            new_lines.append(f'{m.group("lead")}export {key}={quoted}')
            found = True
        else:
            new_lines.append(line)
    if not found:
        return False
    new_text = "\n".join(new_lines)
    if not new_text.endswith("\n"):
        new_text += "\n"
    st = path.stat()
    tmp = path.with_suffix(path.suffix + ".tmp")
    tmp.write_text(new_text, encoding="utf-8")
    os.chmod(tmp, stat.S_IMODE(st.st_mode))
    tmp.replace(path)
    return True
