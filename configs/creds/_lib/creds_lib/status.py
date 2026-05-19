"""Per-connector status records used by `creds_validate`."""

from __future__ import annotations

import os
import sys
from dataclasses import dataclass, field
from typing import Iterable, Literal


def _color_enabled() -> bool:
    return sys.stdout.isatty() and os.environ.get("NO_COLOR") is None


def _c(code: str, s: str) -> str:
    return f"\x1b[{code}m{s}\x1b[0m" if _color_enabled() else s


State = Literal["OK", "MISCONFIGURED", "FAIL", "SKIPPED"]


@dataclass
class Result:
    connector: str
    state: State
    message: str = ""
    sample: str = ""  # e.g. the random item picked for the list-then-pick probe
    missing: list[str] = field(default_factory=list)  # missing env var names

    def line(self) -> str:
        badge = {
            "OK": _c("32;1", "  OK "),
            "MISCONFIGURED": _c("33;1", "MISC."),
            "FAIL": _c("31;1", "FAIL "),
            "SKIPPED": _c("90;1", "SKIP "),
        }[self.state]
        head = f"[{badge}] {self.connector:<10}"
        parts = [head]
        if self.message:
            parts.append(self.message)
        if self.sample:
            parts.append(_c("90", f"(sample: {self.sample})"))
        if self.missing:
            parts.append(_c("33", f"missing: {', '.join(self.missing)}"))
        return "  ".join(parts)


def render(results: Iterable[Result]) -> int:
    """Print results; return process exit code (0 only if every connector is OK or SKIPPED)."""
    rc = 0
    any_seen = False
    for r in results:
        any_seen = True
        print(r.line())
        if r.state == "FAIL":
            rc = max(rc, 1)
        elif r.state == "MISCONFIGURED":
            rc = max(rc, 2)
    if not any_seen:
        print("no connectors registered")
        rc = 3
    return rc


def required_env(*names: str) -> tuple[dict[str, str], list[str]]:
    """Pull the listed env vars; return (present, missing)."""
    present: dict[str, str] = {}
    missing: list[str] = []
    for n in names:
        v = os.environ.get(n)
        if v:
            present[n] = v
        else:
            missing.append(n)
    return present, missing
