"""Mixpanel — reachability probe (no env required).

The agents-devkit Mixpanel MCP (`mcp.mixpanel.com/mcp`) is a hosted server
that authenticates via OAuth on first connect (browser pop, cached) — no env
vars. So this connector just confirms the MCP server is reachable from this
machine; the real auth happens inside the MCP client (Claude Code, Cursor,
etc.) on first tool use.

Project is resolved server-side from the authenticated identity; pin the
canonical `project_id` in `~/.config/adk/overrides.yaml.repos[*].mixpanel`
so skills don't ask.
"""

from __future__ import annotations

from .. import http as _http
from ..status import Result

NAME = "mixpanel"

_MCP_URL = "https://mcp.mixpanel.com/mcp"

# Standard MCP initialize handshake — server should reply (200 + session-id) or
# challenge for OAuth (401/403). Either is "reachable".
_INIT_BODY = {
    "jsonrpc": "2.0",
    "id": 1,
    "method": "initialize",
    "params": {
        "protocolVersion": "2025-03-26",
        "capabilities": {},
        "clientInfo": {"name": "mac-setup-creds-validate", "version": "1.0"},
    },
}


def validate() -> Result:
    status, _h, body = _http.request(
        "POST",
        _MCP_URL,
        headers={"Accept": "application/json, text/event-stream"},
        json_body=_INIT_BODY,
        timeout=15.0,
    )
    # 200 = handshake accepted; 401/403 = reachable, expects OAuth in the
    # client; 405 = wrong method (server up).
    if status in (200, 401, 403, 405):
        suffix = "" if status == 200 else f" (HTTP {status} — OAuth handled by MCP client)"
        return Result(NAME, "OK", f"hosted MCP reachable{suffix}")
    snippet = body[:200] if isinstance(body, str) else ""
    return Result(NAME, "FAIL", f"hosted MCP unreachable — HTTP {status} {snippet}")
