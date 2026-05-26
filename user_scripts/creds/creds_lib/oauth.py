"""Loopback OAuth helper (Authorization Code flow).

Spawns a one-shot HTTP server on 127.0.0.1, opens the browser to the
provider's authorize URL, captures `?code=…`, exchanges it for tokens,
and returns the parsed JSON.

Stdlib-only — no `requests`, no `flask`.
"""

from __future__ import annotations

import http.server
import secrets
import socket
import threading
import urllib.parse
import webbrowser
from dataclasses import dataclass
from typing import Any

from . import http as _http


@dataclass
class OAuthConfig:
    name: str                  # human label, e.g. "Slack"
    auth_url: str
    token_url: str
    client_id: str
    client_secret: str
    scope: str = ""
    user_scope: str = ""       # Slack uses `user_scope` instead of `scope`
    extra_authorize: dict[str, str] | None = None
    extra_token: dict[str, str] | None = None
    callback_path: str = "/oauth/callback"
    port: int = 0              # 0 -> pick a free port
    timeout_sec: int = 300
    # Hostname used in the redirect_uri sent to the IdP. Defaults to
    # 127.0.0.1, but some providers (Okta) require an exact-string match
    # against the registered callback, which often uses "localhost".
    # The HTTP server still binds to 127.0.0.1; "localhost" resolves to it.
    redirect_host: str = "127.0.0.1"


def _free_port() -> int:
    s = socket.socket()
    s.bind(("127.0.0.1", 0))
    port = s.getsockname()[1]
    s.close()
    return port


def run(cfg: OAuthConfig) -> dict[str, Any]:
    """Run the OAuth dance. Returns the token-endpoint JSON or raises."""
    port = cfg.port or _free_port()
    redirect_uri = f"http://{cfg.redirect_host}:{port}{cfg.callback_path}"
    state = secrets.token_urlsafe(24)

    params = {
        "client_id": cfg.client_id,
        "redirect_uri": redirect_uri,
        "response_type": "code",
        "state": state,
    }
    if cfg.scope:
        params["scope"] = cfg.scope
    if cfg.user_scope:
        params["user_scope"] = cfg.user_scope
    if cfg.extra_authorize:
        params.update(cfg.extra_authorize)

    authorize = cfg.auth_url + ("&" if "?" in cfg.auth_url else "?") + urllib.parse.urlencode(params)

    captured: dict[str, Any] = {}
    done = threading.Event()

    class Handler(http.server.BaseHTTPRequestHandler):
        def log_message(self, *_: Any) -> None:  # silence
            return

        def do_GET(self) -> None:  # noqa: N802
            parsed = urllib.parse.urlparse(self.path)
            if parsed.path != cfg.callback_path:
                self.send_response(404)
                self.end_headers()
                return
            qs = urllib.parse.parse_qs(parsed.query)
            captured["query"] = {k: v[0] for k, v in qs.items()}
            self.send_response(200)
            self.send_header("Content-Type", "text/html; charset=utf-8")
            self.end_headers()
            self.wfile.write(
                f"<h2>{cfg.name} login complete</h2>"
                "<p>You can close this tab and return to the terminal.</p>".encode()
            )
            done.set()

    srv = http.server.ThreadingHTTPServer(("127.0.0.1", port), Handler)
    t = threading.Thread(target=srv.serve_forever, daemon=True)
    t.start()

    print(f"→ Opening browser for {cfg.name} OAuth…")
    print(f"  If it doesn't open, paste this URL into your browser:\n  {authorize}\n")
    try:
        webbrowser.open(authorize, new=2, autoraise=True)
    except Exception:
        pass

    if not done.wait(timeout=cfg.timeout_sec):
        srv.shutdown()
        raise TimeoutError(f"{cfg.name} OAuth timed out after {cfg.timeout_sec}s")
    srv.shutdown()

    q = captured.get("query", {})
    if "error" in q:
        raise RuntimeError(f"{cfg.name} OAuth error: {q.get('error')} — {q.get('error_description', '')}")
    if q.get("state") != state:
        raise RuntimeError(f"{cfg.name} OAuth state mismatch (possible CSRF) — aborting")
    code = q.get("code")
    if not code:
        raise RuntimeError(f"{cfg.name} OAuth did not return a `code` parameter")

    form = {
        "grant_type": "authorization_code",
        "code": code,
        "redirect_uri": redirect_uri,
        "client_id": cfg.client_id,
        "client_secret": cfg.client_secret,
    }
    if cfg.extra_token:
        form.update(cfg.extra_token)

    status, _h, body = _http.request("POST", cfg.token_url, data=form)
    if status >= 400:
        raise RuntimeError(f"{cfg.name} token exchange failed: HTTP {status} {body[:300]}")
    parsed = _http.json_or_text(body)
    if not isinstance(parsed, dict):
        raise RuntimeError(f"{cfg.name} token exchange returned non-JSON: {body[:200]}")
    if parsed.get("ok") is False:  # Slack
        raise RuntimeError(f"{cfg.name} token exchange not ok: {parsed.get('error')}")
    return parsed
