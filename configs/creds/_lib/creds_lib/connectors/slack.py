"""Slack connector — OAuth login + validate.

Login flow follows the reference impl in ConnectorsService.ts:
    https://slack.com/oauth/v2/authorize   →   https://slack.com/api/oauth.v2.access
Requests BOTH `scope=` (bot) and `user_scope=` (user) so the resulting
token file holds an `xoxb-…` bot token AND an `xoxp-…` user token. The
scope superset is sourced from `$CREDS_HOME/slack/app.json` (override
path via $SLACK_APP_CONFIG_FILE), so the same file feeds both this
login flow and the agents-devkit Slack MCP wrapper.
"""

from __future__ import annotations

import datetime as dt
import json
import os
import random
import urllib.parse
from pathlib import Path

from .. import http as _http
from .. import store
from ..oauth import OAuthConfig, run as oauth_run
from ..status import Result, required_env

NAME = "slack"

# Fallback scopes used only if the app.json file is missing or unreadable.
# Keep in sync with the comment in app.json.
_FALLBACK_BOT_SCOPES = [
    "channels:history", "channels:read", "chat:write",
    "emoji:read", "groups:history", "groups:read",
    "reactions:read", "reactions:write",
]
_FALLBACK_USER_SCOPES = list(_FALLBACK_BOT_SCOPES)


def _app_config_path() -> Path:
    override = os.environ.get("SLACK_APP_CONFIG_FILE")
    if override:
        return Path(os.path.expandvars(os.path.expanduser(override)))
    from .. import CREDS_DIR
    return CREDS_DIR / "slack" / "app.json"


def _load_app_config() -> dict:
    p = _app_config_path()
    try:
        with p.open("r", encoding="utf-8") as f:
            return json.load(f)
    except FileNotFoundError:
        return {}


def _load_scopes(cfg: dict) -> tuple[str, str]:
    """Return (bot_scope_csv, user_scope_csv). Falls back to a built-in set."""
    bot = cfg.get("bot_scopes") or _FALLBACK_BOT_SCOPES
    user = cfg.get("user_scopes") or _FALLBACK_USER_SCOPES
    return ",".join(bot), ",".join(user)


def _parse_redirect_uri(cfg: dict) -> tuple[int, str] | tuple[None, None]:
    """Parse `redirect_uri` from app.json into (port, callback_path).

    Slack rejects the OAuth flow if the redirect URI does not exactly
    match the one registered in the Slack app config, so the user pins
    it here. Returns (None, None) when unset → oauth.run picks a free
    port and uses its default callback path.
    """
    uri = cfg.get("redirect_uri")
    if not uri:
        return None, None
    parsed = urllib.parse.urlparse(uri)
    if parsed.hostname not in ("127.0.0.1", "localhost"):
        raise RuntimeError(
            f"slack/app.json redirect_uri must be loopback (127.0.0.1/localhost), got {parsed.hostname!r}"
        )
    if not parsed.port:
        raise RuntimeError(f"slack/app.json redirect_uri must include a port: {uri!r}")
    return parsed.port, parsed.path or "/oauth/callback"


def _token_path():
    return store.resolve_path(NAME, env_var="SLACK_CREDENTIALS_FILE")


def login() -> Result:
    env, missing = required_env("SLACK_CLIENT_ID", "SLACK_CLIENT_SECRET_CRED")
    if missing:
        return Result(NAME, "MISCONFIGURED", "Cannot start login.", missing=missing)

    cfg = _load_app_config()
    bot_scope, user_scope = _load_scopes(cfg)
    port, callback_path = _parse_redirect_uri(cfg)

    oauth_kwargs = dict(
        name="Slack",
        auth_url="https://slack.com/oauth/v2/authorize",
        token_url="https://slack.com/api/oauth.v2.access",
        client_id=env["SLACK_CLIENT_ID"],
        client_secret=env["SLACK_CLIENT_SECRET_CRED"],
        scope=bot_scope,
        user_scope=user_scope,
    )
    if port is not None:
        oauth_kwargs["port"] = port
        oauth_kwargs["callback_path"] = callback_path

    tok = oauth_run(OAuthConfig(**oauth_kwargs))
    # Slack oauth.v2.access returns:
    #   { ok, access_token: "xoxb-...", token_type: "bot", scope, bot_user_id,
    #     team, authed_user: { id, access_token: "xoxp-...", scope, token_type } }
    user = tok.get("authed_user") or {}
    bot_token = tok.get("access_token")
    user_token = user.get("access_token")
    if not bot_token and not user_token:
        return Result(NAME, "FAIL", "Slack returned neither bot nor user access_token.")

    path = _token_path()
    store.save(
        path,
        {
            "bot_token": bot_token,
            "bot_scope": tok.get("scope"),
            "bot_user_id": tok.get("bot_user_id"),
            "user_id": user.get("id"),
            "user_token": user_token,
            "user_scope": user.get("scope"),
            "token_type": user.get("token_type"),
            "team": tok.get("team"),
            "generated_at": dt.datetime.utcnow().isoformat(timespec="seconds") + "Z",
        },
    )
    team_name = (tok.get("team") or {}).get("name", "?")
    kinds = ", ".join(k for k, present in [("bot", bot_token), ("user", user_token)] if present)
    return Result(NAME, "OK", f"saved {kinds} token(s) for team={team_name} → {path}")


def validate() -> Result:
    path = _token_path()
    data = store.load(path)
    # Prefer user token for read-side validation (covers channels the bot
    # hasn't been invited to). Fall back to bot token.
    token = data.get("user_token") or data.get("bot_token")
    if not token:
        return Result(
            NAME,
            "MISCONFIGURED",
            f"no token at {path}; run `creds_login_slack` first",
        )

    # list, then pick a random one
    status, _h, body = _http.request(
        "GET",
        "https://slack.com/api/conversations.list",
        headers={"Authorization": f"Bearer {token}"},
        params={"limit": 100, "exclude_archived": "true", "types": "public_channel,private_channel"},
    )
    j = _http.json_or_text(body)
    if status >= 400 or not isinstance(j, dict) or not j.get("ok"):
        err = j.get("error") if isinstance(j, dict) else body[:200]
        return Result(NAME, "FAIL", f"conversations.list HTTP {status} — {err}")

    channels = j.get("channels") or []
    if not channels:
        return Result(NAME, "OK", "token works but user is in 0 channels")
    pick = random.choice(channels)
    return Result(NAME, "OK", "conversations.list ok", sample=f"#{pick.get('name')} ({pick.get('id')})")
