#!/usr/bin/env python3
"""Slack app-config token rotation — see rotate.sh for prose.

Reads:   $SLACK_APP_CONFIG_REFRESH_TOKEN_CRED   (from creds.sh / loader)
Writes:  $CREDS_HOME/slack/creds.sh         (values for ACCESS + REFRESH)

Idempotent only in the sense that re-running consumes the new refresh token
once it has been rotated; calling rotate.py twice in a row WILL succeed the
first time and fail the second (single-use refresh).
"""
from __future__ import annotations

import json
import os
import re
import shlex
import stat
import sys
import urllib.parse
import urllib.request
from pathlib import Path

CREDS_FILE = Path.home() / ".config" / "creds" / "slack" / "creds.sh"
REFRESH_VAR = "SLACK_APP_CONFIG_REFRESH_TOKEN_CRED"
ACCESS_VAR = "SLACK_APP_CONFIG_ACCESS_TOKEN_CRED"
ROTATE_URL = "https://slack.com/api/tooling.tokens.rotate"


def _slack_rotate(refresh: str) -> dict:
    data = urllib.parse.urlencode({"refresh_token": refresh}).encode()
    req = urllib.request.Request(
        ROTATE_URL,
        data=data,
        method="POST",
        headers={"Content-Type": "application/x-www-form-urlencoded"},
    )
    with urllib.request.urlopen(req, timeout=20) as resp:
        body = resp.read().decode("utf-8", "replace")
    parsed = json.loads(body)
    if not isinstance(parsed, dict) or parsed.get("ok") is not True:
        raise RuntimeError(f"slack rejected rotate: {parsed.get('error') or body[:200]}")
    return parsed


_KV = re.compile(
    r"^(?P<lead>\s*)(?P<exp>(?:#\s*)?export\s+)(?P<key>[A-Za-z_][A-Za-z0-9_]*)=.*$"
)


def _update_in_place(path: Path, updates: dict[str, str]) -> set[str]:
    """Rewrite `path` so each KEY in `updates` has its new value; preserve all
    other lines verbatim. Returns the set of keys that were actually replaced."""
    if not path.exists():
        raise FileNotFoundError(f"creds.sh not found at {path}; run setup first")
    out_lines: list[str] = []
    replaced: set[str] = set()
    for line in path.read_text(encoding="utf-8").splitlines():
        m = _KV.match(line)
        if m and m.group("key") in updates:
            key = m.group("key")
            # Drop the `#` from `# export` if present — we now have a real value.
            lead = m.group("lead")
            quoted = shlex.quote(updates[key])
            out_lines.append(f"{lead}export {key}={quoted}")
            replaced.add(key)
        else:
            out_lines.append(line)
    # If any target key was missing entirely, append it under a small header.
    missing = set(updates) - replaced
    if missing:
        if out_lines and out_lines[-1].strip() != "":
            out_lines.append("")
        out_lines.append("# --- appended by slack/scripts/rotate.py ---")
        for key in sorted(missing):
            out_lines.append(f"export {key}={shlex.quote(updates[key])}")
            replaced.add(key)
    text = "\n".join(out_lines)
    if not text.endswith("\n"):
        text += "\n"

    # Atomic write, preserving 0600 mode.
    tmp = path.with_suffix(path.suffix + ".tmp")
    tmp.write_text(text, encoding="utf-8")
    os.chmod(tmp, stat.S_IRUSR | stat.S_IWUSR)  # 0600
    tmp.replace(path)
    return replaced


def main() -> int:
    refresh = os.environ.get(REFRESH_VAR)
    if not refresh or refresh.startswith("PLACEHOLDER"):
        print(
            f"slack/rotate: {REFRESH_VAR} is unset or still a placeholder. "
            f"Mint the initial pair at https://api.slack.com/authentication/config-tokens "
            f"and paste both into {CREDS_FILE}.",
            file=sys.stderr,
        )
        return 2

    try:
        resp = _slack_rotate(refresh)
    except Exception as e:  # noqa: BLE001
        print(f"slack/rotate: {e}", file=sys.stderr)
        return 3

    new_access = resp.get("token")
    new_refresh = resp.get("refresh_token")
    if not (new_access and new_refresh):
        print(f"slack/rotate: response missing tokens: keys={list(resp)}", file=sys.stderr)
        return 3

    replaced = _update_in_place(
        CREDS_FILE,
        {ACCESS_VAR: new_access, REFRESH_VAR: new_refresh},
    )
    exp_human = resp.get("exp")
    print(
        f"slack/rotate: updated {', '.join(sorted(replaced))} in {CREDS_FILE} "
        f"(new token expires at unix {exp_human})"
    )
    print("→ run `source ~/.zshenv` or open a new shell to pick up the new tokens.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
