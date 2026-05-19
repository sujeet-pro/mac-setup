"""Google connector — OAuth (offline access) login + Drive validate.

Scope superset is sourced from `~/.config/creds/google/app.json`
(override path via $GOOGLE_APP_CONFIG_FILE), with a fallback to a
minimal Drive+Docs read-only set if the file is missing. The OAuth
dance asks for `access_type=offline` + `prompt=consent` so Google
issues a `refresh_token`, and we store it. Validate exchanges the
`refresh_token` for an access_token and lists files in Drive, then
picks a random one.
"""

from __future__ import annotations

import datetime as dt
import json
import os
import random
from pathlib import Path

from .. import http as _http
from .. import store
from ..oauth import OAuthConfig, run as oauth_run
from ..status import Result, required_env

NAME = "google"

_FALLBACK_SCOPES = [
    "https://www.googleapis.com/auth/documents.readonly",
    "https://www.googleapis.com/auth/drive.readonly",
]


def _app_config_path() -> Path:
    override = os.environ.get("GOOGLE_APP_CONFIG_FILE")
    if override:
        return Path(os.path.expandvars(os.path.expanduser(override)))
    return Path.home() / ".config" / "creds" / "google" / "app.json"


def _load_scopes() -> str:
    p = _app_config_path()
    try:
        with p.open("r", encoding="utf-8") as f:
            cfg = json.load(f)
    except FileNotFoundError:
        return " ".join(_FALLBACK_SCOPES)
    scopes = cfg.get("scopes") or _FALLBACK_SCOPES
    return " ".join(scopes)


def _token_path():
    return store.resolve_path(NAME, env_var="GOOGLE_CREDENTIALS_FILE")


def login() -> Result:
    env, missing = required_env("GOOGLE_CLIENT_ID_CRED", "GOOGLE_CLIENT_SECRET_CRED")
    if missing:
        return Result(NAME, "MISCONFIGURED", "Cannot start login.", missing=missing)

    scope = _load_scopes()

    tok = oauth_run(
        OAuthConfig(
            name="Google",
            auth_url="https://accounts.google.com/o/oauth2/v2/auth",
            token_url="https://oauth2.googleapis.com/token",
            client_id=env["GOOGLE_CLIENT_ID_CRED"],
            client_secret=env["GOOGLE_CLIENT_SECRET_CRED"],
            scope=scope,
            extra_authorize={"access_type": "offline", "prompt": "consent", "include_granted_scopes": "true"},
        )
    )
    refresh = tok.get("refresh_token")
    if not refresh:
        return Result(
            NAME,
            "FAIL",
            "Google did not return a refresh_token — revoke this app at "
            "https://myaccount.google.com/permissions and retry.",
        )

    path = _token_path()
    store.save(
        path,
        {
            "refresh_token": refresh,
            "scope": tok.get("scope"),
            "client_id": env["GOOGLE_CLIENT_ID_CRED"],
            "client_secret": env["GOOGLE_CLIENT_SECRET_CRED"],
            "generated_at": dt.datetime.utcnow().isoformat(timespec="seconds") + "Z",
        },
    )
    return Result(NAME, "OK", f"refresh_token saved → {path}")


def _exchange_refresh(refresh: str, client_id: str, client_secret: str) -> str | None:
    status, _h, body = _http.request(
        "POST",
        "https://oauth2.googleapis.com/token",
        data={
            "grant_type": "refresh_token",
            "refresh_token": refresh,
            "client_id": client_id,
            "client_secret": client_secret,
        },
    )
    j = _http.json_or_text(body)
    if status >= 400 or not isinstance(j, dict):
        return None
    return j.get("access_token")


def _mcp_env_warning() -> str:
    """Surface MCP-specific env-var gaps that don't break the OAuth probe but
    will break the agents-devkit `adk-mcp-google` (taylorwilsdon/workspace-mcp)
    server when it starts. Returns "" if everything is in place."""
    mcp_missing: list[str] = []
    if not os.environ.get("USER_GOOGLE_EMAIL"):
        mcp_missing.append("USER_GOOGLE_EMAIL")
    # Accept either the new canonical name or the legacy alias.
    if not (os.environ.get("GOOGLE_WORKSPACE_MCP_CREDENTIALS_DIR")
            or os.environ.get("WORKSPACE_MCP_CREDENTIALS_DIR")):
        mcp_missing.append("GOOGLE_WORKSPACE_MCP_CREDENTIALS_DIR")
    if mcp_missing:
        return f"  [adk-mcp-google missing: {', '.join(mcp_missing)}]"
    return ""


def validate() -> Result:
    path = _token_path()
    data = store.load(path)
    refresh = data.get("refresh_token")
    cid = data.get("client_id") or required_env("GOOGLE_CLIENT_ID_CRED")[0].get("GOOGLE_CLIENT_ID_CRED")
    csec = data.get("client_secret") or required_env("GOOGLE_CLIENT_SECRET_CRED")[0].get("GOOGLE_CLIENT_SECRET_CRED")
    if not refresh or not cid or not csec:
        return Result(
            NAME,
            "MISCONFIGURED",
            f"no refresh_token at {path}; run `creds login google` first",
        )

    access = _exchange_refresh(refresh, cid, csec)
    if not access:
        return Result(NAME, "FAIL", "refresh_token exchange failed (token expired or revoked)")

    status, _h, body = _http.request(
        "GET",
        "https://www.googleapis.com/drive/v3/files",
        headers={"Authorization": f"Bearer {access}"},
        params={"pageSize": 50, "fields": "files(id,name,mimeType)"},
    )
    j = _http.json_or_text(body)
    if status >= 400 or not isinstance(j, dict):
        return Result(NAME, "FAIL", f"drive.files.list HTTP {status} — {body[:200]}")
    files = j.get("files") or []
    msg_suffix = _mcp_env_warning()
    if not files:
        return Result(NAME, "OK", f"access token works; user has 0 visible Drive files{msg_suffix}")
    pick = random.choice(files)
    return Result(
        NAME,
        "OK",
        f"drive.files.list ok{msg_suffix}",
        sample=f"{pick.get('name')!r} ({pick.get('mimeType')})",
    )
