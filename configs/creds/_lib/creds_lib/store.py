"""Read/write JSON credential files under `~/.config/creds/`."""

from __future__ import annotations

import json
import os
import stat
from pathlib import Path
from typing import Any

from . import CREDS_DIR, ensure_dir


def default_token_path(app: str) -> Path:
    return CREDS_DIR / f"{app}.token.json"


def resolve_path(app: str, env_var: str | None = None) -> Path:
    """Resolve token path for `app`, honoring an env override like SLACK_CREDENTIALS_FILE."""
    if env_var and os.environ.get(env_var):
        return Path(os.path.expandvars(os.path.expanduser(os.environ[env_var])))
    return default_token_path(app)


def load(path: Path) -> dict[str, Any]:
    if not path.exists():
        return {}
    with path.open("r", encoding="utf-8") as f:
        return json.load(f)


def save(path: Path, data: dict[str, Any]) -> Path:
    ensure_dir(path.parent)
    tmp = path.with_suffix(path.suffix + ".tmp")
    with tmp.open("w", encoding="utf-8") as f:
        json.dump(data, f, indent=2, sort_keys=True)
        f.write("\n")
    os.chmod(tmp, stat.S_IRUSR | stat.S_IWUSR)  # 0600
    tmp.replace(path)
    return path
