"""Bitbucket Cloud — env-only validate.

Uses Basic auth: BITBUCKET_USERNAME + BITBUCKET_TOKEN_CRED against the
Bitbucket Cloud API.

Probe strategy is scope-aware. Newer Bitbucket API tokens are commonly
minted without the `account` scope, so /user 403s even when the token
is valid. When BITBUCKET_WORKSPACE is set we hit /repositories/<ws>
first — that needs only the `repository` scope and proves both auth
and workspace access in one shot. Otherwise we fall back to /workspaces,
and finally /user.

BITBUCKET_URL is informational only; the Cloud API base is fixed at
https://api.bitbucket.org/2.0.
"""

from __future__ import annotations

import os
import random

from .. import http as _http
from ..status import Result, required_env

NAME = "bitbucket"
API_BASE = "https://api.bitbucket.org/2.0"


def _auth_error(status: int, body: str, endpoint: str) -> Result | None:
    if status == 401:
        return Result(NAME, "FAIL", "401 unauthorized — bad username/app-password combination")
    if status == 403:
        return Result(NAME, "FAIL", f"403 forbidden on {endpoint} — token lacks required scope")
    return None


def validate() -> Result:
    env, missing = required_env("BITBUCKET_USERNAME", "BITBUCKET_TOKEN_CRED")
    if missing:
        return Result(NAME, "MISCONFIGURED", "missing env", missing=missing)

    auth = _http.basic_auth(env["BITBUCKET_USERNAME"], env["BITBUCKET_TOKEN_CRED"])
    headers = {"Authorization": auth, "Accept": "application/json"}

    workspace = os.environ.get("BITBUCKET_WORKSPACE", "").strip()
    if workspace:
        endpoint = f"/repositories/{workspace}"
        status, _h, body = _http.request(
            "GET",
            f"{API_BASE}{endpoint}",
            headers=headers,
            params={"pagelen": 50, "fields": "values.name,values.slug"},
        )
        err = _auth_error(status, body, endpoint)
        if err:
            return err
        if status == 404:
            return Result(NAME, "FAIL", f"workspace `{workspace}` not found (or no access)")
        j = _http.json_or_text(body)
        if status >= 400 or not isinstance(j, dict):
            return Result(NAME, "FAIL", f"{endpoint} HTTP {status} — {body[:200]}")
        repos = j.get("values") or []
        if not repos:
            return Result(NAME, "OK", f"auth ok; 0 repos in `{workspace}`")
        pick = random.choice(repos)
        return Result(NAME, "OK", f"{endpoint} ok", sample=pick.get("name") or pick.get("slug"))

    endpoint = "/workspaces"
    status, _h, body = _http.request(
        "GET",
        f"{API_BASE}{endpoint}",
        headers=headers,
        params={"pagelen": 50, "fields": "values.slug,values.name"},
    )
    err = _auth_error(status, body, endpoint)
    if err is None and status < 400:
        j = _http.json_or_text(body)
        if isinstance(j, dict):
            workspaces = j.get("values") or []
            if not workspaces:
                return Result(NAME, "OK", "auth ok; 0 workspaces visible")
            pick = random.choice(workspaces)
            return Result(NAME, "OK", f"{endpoint} ok", sample=pick.get("slug") or pick.get("name"))

    endpoint = "/user"
    status, _h, body = _http.request("GET", f"{API_BASE}{endpoint}", headers=headers)
    err = _auth_error(status, body, endpoint)
    if err:
        return err
    j = _http.json_or_text(body)
    if status >= 400 or not isinstance(j, dict):
        return Result(NAME, "FAIL", f"{endpoint} HTTP {status} — {body[:200]}")
    return Result(NAME, "OK", f"{endpoint} ok", sample=j.get("username") or j.get("display_name", ""))
