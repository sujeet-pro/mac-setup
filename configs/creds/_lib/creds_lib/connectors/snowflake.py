"""Snowflake — connections.toml + PAT (programmatic access token) validate.

Aligned with `agents-devkit/mcp/adk-mcp-snowflake.json` since 2026-05-19:

    SNOWFLAKE_HOME              ~/.config/creds/snowflake (Snowflake's native
                                 config root; holds connections.toml)
    SNOWFLAKE_CONNECTION_NAME   selects the [<name>] block in connections.toml
                                 (default: "adk", matching the MCP wrapper)
    SNOWFLAKE_ACCESS_TOKEN_CRED  Programmatic Access Token (PAT) — shell env
                                 only, never on disk; overrides any password
                                 baked into connections.toml.

Account / user / warehouse / role live in
`$SNOWFLAKE_HOME/connections.toml` under the named block:

    [adk]
    account = "XYZ-12345"
    user = "you@company.com"
    warehouse = "COMPUTE_WH"
    role = "ANALYST_ROLE"

We hit the SQL REST API (`/api/v2/statements`) directly with the PAT as a
Bearer token — keeps the validator stdlib-only (no snowflake-connector-python
dependency).
"""

from __future__ import annotations

import os
import random
from pathlib import Path

try:
    import tomllib  # py311+
except ImportError:  # pragma: no cover — py310 fallback
    import tomli as tomllib  # type: ignore[no-redef]

from .. import http as _http
from ..status import Result, required_env

NAME = "snowflake"


def _connections_path() -> Path:
    home = os.environ.get("SNOWFLAKE_HOME") or str(Path.home() / ".snowflake")
    return Path(os.path.expanduser(home)) / "connections.toml"


def _read_connection(name: str) -> tuple[dict[str, str] | None, str | None]:
    p = _connections_path()
    if not p.exists():
        return None, f"connections.toml not found at {p}"
    try:
        with p.open("rb") as f:
            data = tomllib.load(f)
    except (tomllib.TOMLDecodeError, OSError) as e:
        return None, f"failed to parse {p}: {e}"
    block = data.get(name)
    if not isinstance(block, dict):
        return None, f"no [{name}] block in {p}"
    return block, None


def validate() -> Result:
    env, missing = required_env("SNOWFLAKE_ACCESS_TOKEN_CRED")
    if missing:
        return Result(NAME, "MISCONFIGURED", "missing env", missing=missing)

    conn_name = os.environ.get("SNOWFLAKE_CONNECTION_NAME", "adk")
    conn, err = _read_connection(conn_name)
    if conn is None:
        return Result(NAME, "MISCONFIGURED", err or "unknown error reading connections.toml")

    account = conn.get("account")
    user = conn.get("user")
    if not account or not user:
        return Result(
            NAME,
            "MISCONFIGURED",
            f"[{conn_name}] in {_connections_path()} missing `account` or `user`",
        )

    base = f"https://{account.strip().replace('_', '-')}.snowflakecomputing.com"
    warehouse = conn.get("warehouse") or os.environ.get("SNOWFLAKE_WAREHOUSE")

    body_in = {"statement": "SHOW DATABASES", "timeout": 30}
    if warehouse:
        body_in["warehouse"] = warehouse

    status, _h, body = _http.request(
        "POST",
        f"{base}/api/v2/statements",
        headers={
            "Authorization": f"Bearer {env['SNOWFLAKE_ACCESS_TOKEN_CRED']}",
            "X-Snowflake-Authorization-Token-Type": "PROGRAMMATIC_ACCESS_TOKEN",
            "Accept": "application/json",
            "User-Agent": "mac-setup-creds/1.0",
        },
        json_body=body_in,
    )
    j = _http.json_or_text(body)
    if status == 401:
        return Result(NAME, "FAIL", "401 unauthorized — bad PAT or wrong user/account")
    if status >= 400 or not isinstance(j, dict):
        snippet = body[:200] if isinstance(body, str) else str(body)[:200]
        return Result(NAME, "FAIL", f"/api/v2/statements HTTP {status} — {snippet}")

    data = j.get("data") or []
    if not data:
        return Result(NAME, "OK", f"auth ok via [{conn_name}]; 0 databases visible (as {user})")
    row = random.choice(data)
    sample = row[1] if isinstance(row, list) and len(row) > 1 else str(row)
    return Result(NAME, "OK", f"SHOW DATABASES ok via [{conn_name}]", sample=str(sample))
