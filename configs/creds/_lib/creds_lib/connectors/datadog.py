"""Datadog — env-only validate.

Uses DATADOG_API_KEY_CRED (+ DATADOG_APP_KEY_CRED for app-key-scoped
probes). Site defaults to `datadoghq.com`; override with DATADOG_SITE
(e.g. `datadoghq.eu`, `us3.datadoghq.com`).

Note: the agents-devkit Datadog MCP (Bits AI) reads DATADOG_MCP_URL —
that's the hosted MCP endpoint, separate from the public Datadog API
base used here. If you switch DATADOG_SITE you should update
DATADOG_MCP_URL accordingly.
"""

from __future__ import annotations

import os
import random

from .. import http as _http
from ..status import Result, required_env

NAME = "datadog"


def validate() -> Result:
    env, missing = required_env("DATADOG_API_KEY_CRED")
    if missing:
        return Result(NAME, "MISCONFIGURED", "missing env", missing=missing)

    site = (os.environ.get("DATADOG_SITE") or "datadoghq.com").strip("/")
    base = f"https://api.{site}"
    api_key = env["DATADOG_API_KEY_CRED"]
    app_key = os.environ.get("DATADOG_APP_KEY_CRED")

    status, _h, body = _http.request(
        "GET",
        f"{base}/api/v1/validate",
        headers={"DD-API-KEY": api_key},
    )
    j = _http.json_or_text(body)
    if status == 403 or (isinstance(j, dict) and j.get("valid") is False):
        return Result(NAME, "FAIL", "API key rejected by /api/v1/validate")
    if status >= 400:
        return Result(NAME, "FAIL", f"/api/v1/validate HTTP {status} — {body[:200]}")

    if not app_key:
        return Result(NAME, "OK", "/api/v1/validate ok (no APP key set — skipping list probe)")

    status, _h, body = _http.request(
        "GET",
        f"{base}/api/v1/dashboard",
        headers={"DD-API-KEY": api_key, "DD-APPLICATION-KEY": app_key},
    )
    j = _http.json_or_text(body)
    if status >= 400 or not isinstance(j, dict):
        return Result(NAME, "FAIL", f"/api/v1/dashboard HTTP {status} — {body[:200]}")
    dashboards = j.get("dashboards") or []
    if not dashboards:
        return Result(NAME, "OK", "API+APP key ok; 0 dashboards")
    pick = random.choice(dashboards)
    return Result(NAME, "OK", "/api/v1/dashboard ok", sample=pick.get("title") or pick.get("id"))
