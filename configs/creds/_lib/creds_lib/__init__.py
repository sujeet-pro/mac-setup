"""Stdlib-only helpers for the `creds_*` CLIs.

This package powers:
    creds_login_slack    creds_login_google    creds_validate

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
