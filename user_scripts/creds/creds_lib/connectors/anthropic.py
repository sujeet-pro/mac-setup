"""Anthropic API — env-only validate.

Probes GET /v1/models with x-api-key + anthropic-version. The endpoint
returns the list of models the key has access to, so it doubles as an
auth check and a permission check (a key with no model access yields
an empty list rather than a 401).
"""

from __future__ import annotations

import random

from .. import http as _http
from ..status import Result, required_env

NAME = "anthropic"
API_VERSION = "2023-06-01"


def validate() -> Result:
    env, missing = required_env("ANTHROPIC_API_KEY_CRED")
    if missing:
        return Result(NAME, "MISCONFIGURED", "missing env", missing=missing)

    status, _h, body = _http.request(
        "GET",
        "https://api.anthropic.com/v1/models",
        headers={
            "x-api-key": env["ANTHROPIC_API_KEY_CRED"],
            "anthropic-version": API_VERSION,
            "Accept": "application/json",
        },
    )
    j = _http.json_or_text(body)
    if status == 401:
        return Result(NAME, "FAIL", "401 unauthorized — bad API key")
    if status >= 400 or not isinstance(j, dict):
        return Result(NAME, "FAIL", f"/v1/models HTTP {status} — {body[:200]}")
    models = j.get("data") or []
    if not models:
        return Result(NAME, "OK", "auth ok; 0 models visible")
    pick = random.choice(models)
    return Result(NAME, "OK", "/v1/models ok", sample=pick.get("id") or pick.get("display_name", ""))
