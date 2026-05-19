"""Looker — env-only validate.

Looker API uses a /login endpoint that swaps client_id/client_secret for
a short-lived access_token. We then list dashboards and pick a random
one. LOOKER_VERIFY_SSL=false disables TLS verification (matches existing
.zshenv setting).
"""

from __future__ import annotations

import os
import random

from .. import http as _http
from ..status import Result, required_env

NAME = "looker"


def _verify_ssl() -> bool:
    return (os.environ.get("LOOKER_VERIFY_SSL", "true").strip().lower() not in {"0", "false", "no", "off"})


def validate() -> Result:
    env, missing = required_env("LOOKER_SITE", "LOOKER_CLIENT_ID", "LOOKER_CLIENT_SECRET_CRED")
    if missing:
        return Result(NAME, "MISCONFIGURED", "missing env", missing=missing)

    site = env["LOOKER_SITE"].rstrip("/")
    base = f"{site}/api/4.0" if not site.endswith("/api/4.0") else site
    verify = _verify_ssl()

    # Looker self-hosted instances behind a corporate TLS proxy can take
    # 20-40s for the first /login round-trip; the /dashboards list can be slow
    # too on instances with many dashboards. Default to 2 min, overridable.
    timeout = float(os.environ.get("LOOKER_TIMEOUT", "120"))
    status, _h, body = _http.request(
        "POST",
        f"{base}/login",
        data={"client_id": env["LOOKER_CLIENT_ID"], "client_secret": env["LOOKER_CLIENT_SECRET_CRED"]},
        verify_ssl=verify,
        timeout=timeout,
    )
    j = _http.json_or_text(body)
    if status == 404:
        return Result(NAME, "FAIL", "/api/4.0/login returned 404 — check LOOKER_SITE host")
    if status >= 400 or not isinstance(j, dict) or not j.get("access_token"):
        return Result(NAME, "FAIL", f"/api/4.0/login HTTP {status} — {body[:200]}")
    token = j["access_token"]

    status, _h, body = _http.request(
        "GET",
        f"{base}/dashboards",
        headers={"Authorization": f"Bearer {token}"},
        verify_ssl=verify,
        timeout=timeout,
    )
    j = _http.json_or_text(body)
    if status >= 400 or not isinstance(j, list):
        # /dashboards returns a JSON array on success
        return Result(NAME, "FAIL", f"/dashboards HTTP {status} — {body[:200]}")
    if not j:
        return Result(NAME, "OK", "login ok; 0 dashboards visible")
    pick = random.choice(j)
    return Result(NAME, "OK", "/dashboards ok", sample=pick.get("title") or pick.get("id"))
