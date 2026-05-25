"""GitHub — env-only validate.

Probes GET /user with Bearer auth, then GET /user/repos to pick a
random repo as the sample. Works with both classic PATs and fine-grained
tokens. A token with only repo scope but no user:read will still pass
the /user/repos probe — we fall back to that on 403 from /user.
"""

from __future__ import annotations

import random

from .. import http as _http
from ..status import Result, required_env

NAME = "github"
API_BASE = "https://api.github.com"


def _headers(token: str) -> dict[str, str]:
    return {
        "Authorization": f"Bearer {token}",
        "Accept": "application/vnd.github+json",
        "X-GitHub-Api-Version": "2022-11-28",
        "User-Agent": "creds-validate",
    }


def validate() -> Result:
    env, missing = required_env("GITHUB_TOKEN_CRED")
    if missing:
        return Result(NAME, "MISCONFIGURED", "missing env", missing=missing)

    headers = _headers(env["GITHUB_TOKEN_CRED"])

    status, _h, body = _http.request("GET", f"{API_BASE}/user", headers=headers)
    if status == 401:
        return Result(NAME, "FAIL", "401 unauthorized — bad/expired token")
    user_ok = status < 400
    user_login = ""
    if user_ok:
        j = _http.json_or_text(body)
        if isinstance(j, dict):
            user_login = j.get("login", "")

    status, _h, body = _http.request(
        "GET",
        f"{API_BASE}/user/repos",
        headers=headers,
        params={"per_page": 50, "sort": "updated"},
    )
    if status == 401:
        return Result(NAME, "FAIL", "401 unauthorized on /user/repos — bad/expired token")
    if status == 403:
        if user_ok:
            return Result(NAME, "OK", "/user ok (token lacks repo scope)", sample=user_login)
        return Result(NAME, "FAIL", "403 forbidden on /user and /user/repos — token has no usable scope")
    j = _http.json_or_text(body)
    if status >= 400 or not isinstance(j, list):
        if user_ok:
            return Result(NAME, "OK", "/user ok", sample=user_login)
        return Result(NAME, "FAIL", f"/user/repos HTTP {status} — {body[:200]}")
    if not j:
        return Result(NAME, "OK", "auth ok; 0 repos visible", sample=user_login)
    pick = random.choice(j)
    return Result(NAME, "OK", "/user/repos ok", sample=pick.get("full_name") or pick.get("name", ""))
