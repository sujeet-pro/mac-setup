"""Stdlib-only helpers for the `userscripts creds` CLI.

This package powers `userscripts creds {validate, login, status, rotate, ...}`
(entry point at user_scripts/creds/index.py).

All connector tokens / refresh-tokens live under $CREDS_HOME;
per-connector env vars (e.g. `SLACK_CREDENTIALS_FILE`,
`GOOGLE_CREDENTIALS_FILE`) can override individual paths.
"""

from __future__ import annotations

import os
import sys
from pathlib import Path


def _creds_home() -> Path:
    val = os.environ.get("CREDS_HOME")
    if not val:
        sys.stderr.write(
            "creds: CREDS_HOME unset — set it in ~/.zshenv "
            "(see ~/personal/mac-setup/configs/shell/.zshenv.example)\n"
        )
        sys.exit(2)
    return Path(os.path.expanduser(val))


CREDS_DIR = _creds_home()


def ensure_dir(p: Path) -> Path:
    p.mkdir(parents=True, exist_ok=True)
    return p
