"""Okta connector — OIDC Authorization Code login + /userinfo validate.

login() runs the standard loopback OAuth dance with `offline_access` so
Okta returns a refresh_token, then writes everything (refresh_token,
client_id, client_secret, discovered token+userinfo URLs) to
$CREDS_HOME/okta.token.json.

validate() reads that file, exchanges the refresh_token for a fresh
access_token, and hits the OIDC /userinfo endpoint to surface
preferred_username / email as the sample.

Endpoints are auto-discovered from `${OKTA_ISSUER}/.well-known/openid-configuration`,
so the connector works with both the org-level auth server
(`https://acme.okta.com`) and a custom auth server
(`https://acme.okta.com/oauth2/<id>`).
"""

from __future__ import annotations

import datetime as dt
import os
import urllib.parse
from pathlib import Path

from .. import http as _http
from .. import store
from ..oauth import OAuthConfig, run as oauth_run
from ..status import Result, required_env

NAME = "okta"
_SCOPES = "openid profile email offline_access"


def _token_path() -> Path:
    return store.resolve_path(NAME)


def _discover(issuer: str) -> dict | None:
    base = issuer.rstrip("/")
    status, _h, body = _http.request(
        "GET",
        f"{base}/.well-known/openid-configuration",
        headers={"Accept": "application/json"},
    )
    if status >= 400:
        return None
    j = _http.json_or_text(body)
    return j if isinstance(j, dict) else None


def _parse_redirect_uri(uri: str) -> tuple[str, int, str]:
    parsed = urllib.parse.urlparse(uri)
    if parsed.hostname not in ("127.0.0.1", "localhost"):
        raise RuntimeError(
            f"OKTA_REDIRECT_URLS_LOCAL must be a loopback URL, got {parsed.hostname!r}"
        )
    if not parsed.port:
        raise RuntimeError(f"OKTA_REDIRECT_URLS_LOCAL must include a port: {uri!r}")
    return parsed.hostname, parsed.port, parsed.path or "/callback"


def login() -> Result:
    env, missing = required_env(
        "OKTA_ISSUER",
        "OKTA_APP_CLIENT_ID",
        "OKTA_APP_CLIENT_SECRET_CRED",
        "OKTA_REDIRECT_URLS_LOCAL",
    )
    if missing:
        return Result(NAME, "MISCONFIGURED", "Cannot start login.", missing=missing)

    disco = _discover(env["OKTA_ISSUER"])
    if not disco:
        return Result(
            NAME,
            "FAIL",
            f"OIDC discovery failed at {env['OKTA_ISSUER']}/.well-known/openid-configuration",
        )
    auth_url = disco.get("authorization_endpoint")
    token_url = disco.get("token_endpoint")
    userinfo_url = disco.get("userinfo_endpoint")
    if not auth_url or not token_url:
        return Result(NAME, "FAIL", "discovery doc missing authorization/token endpoints")

    host, port, callback_path = _parse_redirect_uri(env["OKTA_REDIRECT_URLS_LOCAL"])

    tok = oauth_run(
        OAuthConfig(
            name="Okta",
            auth_url=auth_url,
            token_url=token_url,
            client_id=env["OKTA_APP_CLIENT_ID"],
            client_secret=env["OKTA_APP_CLIENT_SECRET_CRED"],
            scope=_SCOPES,
            port=port,
            callback_path=callback_path,
            redirect_host=host,
        )
    )
    refresh = tok.get("refresh_token")
    if not refresh:
        return Result(
            NAME,
            "FAIL",
            "Okta did not return a refresh_token — check that the app is "
            "configured with `offline_access` and `Refresh Token` grant type.",
        )

    path = _token_path()
    store.save(
        path,
        {
            "refresh_token": refresh,
            "access_token": tok.get("access_token"),
            "id_token": tok.get("id_token"),
            "scope": tok.get("scope"),
            "token_url": token_url,
            "userinfo_url": userinfo_url,
            "client_id": env["OKTA_APP_CLIENT_ID"],
            "client_secret": env["OKTA_APP_CLIENT_SECRET_CRED"],
            "issuer": env["OKTA_ISSUER"],
            "generated_at": dt.datetime.utcnow().isoformat(timespec="seconds") + "Z",
        },
    )
    return Result(NAME, "OK", f"refresh_token saved → {path}")


def _exchange_refresh(refresh: str, token_url: str, client_id: str, client_secret: str) -> str | None:
    status, _h, body = _http.request(
        "POST",
        token_url,
        data={
            "grant_type": "refresh_token",
            "refresh_token": refresh,
            "client_id": client_id,
            "client_secret": client_secret,
            "scope": _SCOPES,
        },
    )
    j = _http.json_or_text(body)
    if status >= 400 or not isinstance(j, dict):
        return None
    return j.get("access_token")


def validate() -> Result:
    path = _token_path()
    data = store.load(path)
    refresh = data.get("refresh_token")
    token_url = data.get("token_url")
    userinfo_url = data.get("userinfo_url")
    cid = data.get("client_id")
    csec = data.get("client_secret")
    if not (refresh and token_url and cid and csec):
        return Result(
            NAME,
            "MISCONFIGURED",
            f"no usable token at {path}; run `userscripts creds login okta` first",
        )

    if not userinfo_url:
        issuer = (data.get("issuer") or os.environ.get("OKTA_ISSUER") or "").rstrip("/")
        if not issuer:
            return Result(NAME, "MISCONFIGURED", "userinfo_url missing in token file and OKTA_ISSUER unset")
        disco = _discover(issuer)
        userinfo_url = (disco or {}).get("userinfo_endpoint")
        if not userinfo_url:
            return Result(NAME, "FAIL", "could not discover userinfo_endpoint")

    access = _exchange_refresh(refresh, token_url, cid, csec)
    if not access:
        return Result(NAME, "FAIL", "refresh_token exchange failed (expired or revoked — re-login)")

    status, _h, body = _http.request(
        "GET",
        userinfo_url,
        headers={"Authorization": f"Bearer {access}", "Accept": "application/json"},
    )
    j = _http.json_or_text(body)
    if status == 401:
        return Result(NAME, "FAIL", "/userinfo 401 — access token rejected")
    if status >= 400 or not isinstance(j, dict):
        return Result(NAME, "FAIL", f"/userinfo HTTP {status} — {body[:200]}")

    label = j.get("preferred_username") or j.get("email") or j.get("name") or j.get("sub", "?")
    return Result(NAME, "OK", "/userinfo ok", sample=label)
