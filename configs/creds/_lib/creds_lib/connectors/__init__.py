"""Connector registry.

Each connector module exposes:
    NAME           : str
    validate()     -> creds_lib.status.Result
    login()        -> creds_lib.status.Result   (optional; only for OAuth ones)
"""

from __future__ import annotations

from importlib import import_module
from types import ModuleType

# Order matters — printed in this order by `creds_validate`.
NAMES: list[str] = [
    "slack",
    "google",
    "atlassian",
    "datadog",
    "looker",
    "mixpanel",
    "snowflake",
    "statsig",
]


def load(name: str) -> ModuleType:
    if name not in NAMES:
        raise KeyError(f"unknown connector: {name}")
    return import_module(f".{name}", package=__name__)


def all_modules() -> list[ModuleType]:
    return [load(n) for n in NAMES]
