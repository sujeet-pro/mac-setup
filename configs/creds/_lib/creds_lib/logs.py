"""Run-log capture for the `creds_*` CLIs.

All CLI invocations tee stdout + stderr into a timestamped file under
`$CREDS_HOME/logs/` and prune anything older than `RETENTION_DAYS`
(default: 7). Override via the `CREDS_LOG_RETENTION_DAYS` env var.

Why under `$CREDS_HOME/` and not `/tmp`?
  * macOS routinely wipes `/tmp` on reboot; logs would disappear before
    you could read them.
  * Other connector state (token files) already lives in
    `$CREDS_HOME/`; keeping logs alongside avoids a second hidden
    location.
The 7-day prune keeps the directory from growing without bound.
"""

from __future__ import annotations

import datetime as _dt
import os
import sys
import time
from pathlib import Path
from typing import TextIO

from . import CREDS_DIR, ensure_dir

LOG_DIR = CREDS_DIR / "logs"
DEFAULT_RETENTION_DAYS = 7


def _retention_days() -> int:
    raw = os.environ.get("CREDS_LOG_RETENTION_DAYS")
    if not raw:
        return DEFAULT_RETENTION_DAYS
    try:
        n = int(raw)
        return n if n >= 0 else DEFAULT_RETENTION_DAYS
    except ValueError:
        return DEFAULT_RETENTION_DAYS


def prune(retention_days: int | None = None) -> int:
    """Delete log files older than `retention_days`. Returns count removed."""
    days = retention_days if retention_days is not None else _retention_days()
    if days <= 0 or not LOG_DIR.exists():
        return 0
    cutoff = time.time() - days * 86400
    removed = 0
    for p in LOG_DIR.glob("*.log"):
        try:
            if p.stat().st_mtime < cutoff:
                p.unlink()
                removed += 1
        except OSError:
            continue
    return removed


class _Tee:
    """File-like object that writes to several underlying streams."""

    def __init__(self, *streams: TextIO):
        self._streams = streams

    def write(self, data: str) -> int:  # type: ignore[override]
        n = 0
        for s in self._streams:
            try:
                n = s.write(data)
            except Exception:
                pass
        return n

    def flush(self) -> None:
        for s in self._streams:
            try:
                s.flush()
            except Exception:
                pass

    def isatty(self) -> bool:
        # Defer to the first stream (usually the real terminal) so the
        # colorization in status.py keeps working.
        return getattr(self._streams[0], "isatty", lambda: False)()


class capture:
    """Context manager that tees stdout/stderr to a log file.

    Usage:
        with capture("validate") as path:
            ...
            print("done")  # also written to `path`
    """

    def __init__(self, label: str):
        self.label = label
        self.path: Path | None = None
        self._fp: TextIO | None = None
        self._orig_out: TextIO | None = None
        self._orig_err: TextIO | None = None

    def __enter__(self) -> Path:
        ensure_dir(LOG_DIR)
        prune()  # opportunistic cleanup
        ts = _dt.datetime.now().strftime("%Y%m%d-%H%M%S")
        self.path = LOG_DIR / f"{self.label}-{ts}.log"
        self._fp = self.path.open("w", encoding="utf-8")
        # Write a small header so the file is self-describing.
        header = (
            f"# creds_{self.label} run at {_dt.datetime.now().isoformat(timespec='seconds')}\n"
            f"# argv: {sys.argv}\n"
            f"# cwd:  {os.getcwd()}\n"
            "# ---\n"
        )
        self._fp.write(header)
        self._fp.flush()

        self._orig_out, self._orig_err = sys.stdout, sys.stderr
        sys.stdout = _Tee(self._orig_out, self._fp)  # type: ignore[assignment]
        sys.stderr = _Tee(self._orig_err, self._fp)  # type: ignore[assignment]
        return self.path

    def __exit__(self, exc_type, exc, tb) -> None:
        try:
            if self._orig_out is not None:
                sys.stdout = self._orig_out
            if self._orig_err is not None:
                sys.stderr = self._orig_err
        finally:
            if self._fp is not None:
                try:
                    self._fp.flush()
                    self._fp.close()
                except Exception:
                    pass
