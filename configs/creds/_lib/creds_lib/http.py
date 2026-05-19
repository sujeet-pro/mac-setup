"""Tiny stdlib HTTP helper — no `requests` dependency."""

from __future__ import annotations

import base64
import json as _json
import ssl
import urllib.error
import urllib.parse
import urllib.request
from typing import Any


class HttpError(Exception):
    def __init__(self, status: int, body: str, url: str):
        super().__init__(f"HTTP {status} from {url}: {body[:300]}")
        self.status = status
        self.body = body
        self.url = url


def basic_auth(user: str, token: str) -> str:
    raw = f"{user}:{token}".encode()
    return "Basic " + base64.b64encode(raw).decode()


def request(
    method: str,
    url: str,
    *,
    headers: dict[str, str] | None = None,
    params: dict[str, Any] | None = None,
    data: dict[str, Any] | bytes | None = None,
    json_body: Any = None,
    verify_ssl: bool = True,
    timeout: float = 20.0,
) -> tuple[int, dict[str, str], str]:
    """Return (status, headers, body_text). Never raises on non-2xx — caller decides."""
    if params:
        sep = "&" if "?" in url else "?"
        url = url + sep + urllib.parse.urlencode(params)

    body: bytes | None = None
    hdrs = dict(headers or {})
    if json_body is not None:
        body = _json.dumps(json_body).encode()
        hdrs.setdefault("Content-Type", "application/json")
    elif isinstance(data, dict):
        body = urllib.parse.urlencode(data).encode()
        hdrs.setdefault("Content-Type", "application/x-www-form-urlencoded")
    elif isinstance(data, (bytes, bytearray)):
        body = bytes(data)

    req = urllib.request.Request(url, data=body, method=method.upper(), headers=hdrs)
    ctx = ssl.create_default_context()
    if not verify_ssl:
        ctx.check_hostname = False
        ctx.verify_mode = ssl.CERT_NONE
    try:
        with urllib.request.urlopen(req, timeout=timeout, context=ctx) as resp:
            return resp.status, dict(resp.headers), resp.read().decode("utf-8", "replace")
    except urllib.error.HTTPError as e:
        return e.code, dict(e.headers or {}), e.read().decode("utf-8", "replace")


def json_or_text(body: str) -> Any:
    try:
        return _json.loads(body)
    except Exception:
        return body
