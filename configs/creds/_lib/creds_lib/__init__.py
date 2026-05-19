"""Stdlib-only helpers for the `creds_*` CLIs.

This package powers:
    creds_login_slack    creds_login_google    creds_validate

All connector tokens / refresh-tokens live under `~/.config/creds/` by
default; per-connector env vars (e.g. `SLACK_CREDENTIALS_FILE`,
`GOOGLE_CREDENTIALS_FILE`) can override individual paths.
"""

from __future__ import annotations

import os
from pathlib import Path

CREDS_DIR = Path(os.environ.get("CREDS_DIR") or (Path.home() / ".config" / "creds"))


def ensure_dir(p: Path) -> Path:
    p.mkdir(parents=True, exist_ok=True)
    return p
