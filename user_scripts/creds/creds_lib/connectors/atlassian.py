"""Atlassian (Jira/Confluence) — env-only validate.

Uses Basic auth: ATLASSIAN_USERNAME (email) + ATLASSIAN_API_TOKEN_CRED
against ATLASSIAN_SITE. Lists Jira projects and picks a random one.
"""

from __future__ import annotations

import random

from .. import http as _http
from ..status import Result, required_env

NAME = "atlassian"


def validate() -> Result:
    env, missing = required_env("ATLASSIAN_SITE", "ATLASSIAN_USERNAME", "ATLASSIAN_API_TOKEN_CRED")
    if missing:
        return Result(NAME, "MISCONFIGURED", "missing env", missing=missing)

    site = env["ATLASSIAN_SITE"].rstrip("/")
    auth = _http.basic_auth(env["ATLASSIAN_USERNAME"], env["ATLASSIAN_API_TOKEN_CRED"])
    status, _h, body = _http.request(
        "GET",
        f"{site}/rest/api/3/project/search",
        headers={"Authorization": auth, "Accept": "application/json"},
        params={"maxResults": 50},
    )
    j = _http.json_or_text(body)
    if status == 401:
        return Result(NAME, "FAIL", "401 unauthorized — bad email/token combination")
    if status >= 400 or not isinstance(j, dict):
        return Result(NAME, "FAIL", f"project/search HTTP {status} — {body[:200]}")
    projects = j.get("values") or []
    if not projects:
        return Result(NAME, "OK", "auth ok; 0 projects visible")
    pick = random.choice(projects)
    return Result(NAME, "OK", "project/search ok", sample=f"{pick.get('key')} — {pick.get('name')}")
