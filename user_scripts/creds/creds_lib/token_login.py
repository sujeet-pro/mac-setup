"""Guided token-mint login for services that use long-lived API tokens.

For each *_CRED variable the service owns, prompt the user with no-echo
(`getpass.getpass`) and write the value into $CREDS_HOME/<svc>/creds.sh
in place via `creds_sh_io.set_value`. The value never enters stdout/stderr
or any agent's context — only the boolean outcome does.
"""

from __future__ import annotations

import getpass
import subprocess
import sys

from . import creds_sh_io
from .meta import ServiceMeta
from .status import Result


def _open_url(url: str) -> None:
    """Best-effort: open the mint URL in the system browser. Silent on failure."""
    try:
        if sys.platform == "darwin":
            subprocess.run(["open", url], check=False, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
        elif sys.platform.startswith("linux"):
            subprocess.run(["xdg-open", url], check=False, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
    except OSError:
        pass


def run(meta: ServiceMeta) -> Result:
    if meta.auth != "token":
        return Result(meta.name, "FAIL", f"{meta.name} is not a token-auth service (auth={meta.auth})")
    if not meta.secret_vars:
        return Result(meta.name, "FAIL", f"{meta.name} has no secret_vars declared in meta")

    path = creds_sh_io.creds_sh_path(meta.name)
    if not path.is_file():
        return Result(
            meta.name,
            "FAIL",
            f"missing {path} — run `ansible-playbook setup.yml --tags creds` first",
        )

    print(f"─── login: {meta.display} ───")
    if meta.mint_url:
        print(f"  mint URL: {meta.mint_url}  (opening in browser)")
        _open_url(meta.mint_url)
    else:
        print("  (no mint URL — obtain the token from the service's admin UI)")
    print(f"  prompting for: {', '.join(meta.secret_vars)}")
    print(f"  values are read with no echo and written to {path} (0600)")
    print(f"  the values are never displayed back to you or any agent")
    print()

    updated: list[str] = []
    for key in meta.secret_vars:
        try:
            value = getpass.getpass(f"  {key}: ")
        except (EOFError, KeyboardInterrupt):
            print()
            return Result(meta.name, "FAIL", "aborted by user")
        value = value.strip()
        if not value:
            return Result(meta.name, "FAIL", f"empty value entered for {key}")
        if not creds_sh_io.set_value(path, key, value):
            return Result(
                meta.name,
                "FAIL",
                f"{key} is not declared in {path} — template drift; re-run the creds Ansible role",
            )
        updated.append(key)

    return Result(
        meta.name,
        "OK",
        f"wrote {len(updated)} value(s); re-source ~/.zshenv (or open a new shell) to pick them up",
    )
