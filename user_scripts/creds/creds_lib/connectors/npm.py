"""npm registry — env-only validate.

Probes GET https://registry.npmjs.org/-/whoami with Bearer auth. Returns
{"username":"..."} on success. Works for classic publish tokens, automation
tokens, and granular access tokens alike.
"""

from __future__ import annotations

from .. import http as _http
from ..status import Result, required_env

NAME = "npm"


def validate() -> Result:
    env, missing = required_env("NPM_TOKEN_CRED")
    if missing:
        return Result(NAME, "MISCONFIGURED", "missing env", missing=missing)

    status, _h, body = _http.request(
        "GET",
        "https://registry.npmjs.org/-/whoami",
        headers={
            "Authorization": f"Bearer {env['NPM_TOKEN_CRED']}",
            "Accept": "application/json",
        },
    )
    if status == 401:
        return Result(NAME, "FAIL", "401 unauthorized — bad/expired token")
    j = _http.json_or_text(body)
    if status >= 400 or not isinstance(j, dict):
        return Result(NAME, "FAIL", f"/-/whoami HTTP {status} — {body[:200]}")
    user = j.get("username", "")
    if not user:
        return Result(NAME, "FAIL", f"/-/whoami returned no username — body: {body[:200]}")
    return Result(NAME, "OK", "/-/whoami ok", sample=user)
