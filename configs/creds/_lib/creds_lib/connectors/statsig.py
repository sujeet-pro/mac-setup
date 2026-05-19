"""Statsig — env-only validate (Console API).

Reads STATSIG_CONSOLE_API_KEY_CRED (a `console-…` key). Lists gates and
picks a random one.
"""

from __future__ import annotations

import random

from .. import http as _http
from ..status import Result, required_env

NAME = "statsig"


def validate() -> Result:
    env, missing = required_env("STATSIG_CONSOLE_API_KEY_CRED")
    if missing:
        return Result(NAME, "MISCONFIGURED", "missing env", missing=missing)

    status, _h, body = _http.request(
        "GET",
        "https://statsigapi.net/console/v1/gates",
        headers={"STATSIG-API-KEY": env["STATSIG_CONSOLE_API_KEY_CRED"], "Accept": "application/json"},
    )
    j = _http.json_or_text(body)
    if status == 401 or status == 403:
        return Result(NAME, "FAIL", f"HTTP {status} — bad/insufficient STATSIG_CONSOLE_API_KEY_CRED")
    if status >= 400 or not isinstance(j, dict):
        return Result(NAME, "FAIL", f"/console/v1/gates HTTP {status} — {body[:200]}")
    gates = j.get("data") or []
    if not gates:
        return Result(NAME, "OK", "auth ok; 0 gates")
    pick = random.choice(gates)
    return Result(NAME, "OK", "/console/v1/gates ok", sample=str(pick.get("name") or pick.get("id")))
