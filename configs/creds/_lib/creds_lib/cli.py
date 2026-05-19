"""Top-level CLI entrypoints used by the bin wrappers."""

from __future__ import annotations

import argparse
import sys
import traceback

from . import connectors as _connectors
from .env import load_zshenv
from .logs import capture
from .status import Result, render


def _do_login(name: str) -> int:
    load_zshenv()
    try:
        mod = _connectors.load(name)
    except KeyError as e:
        print(f"error: {e}", file=sys.stderr)
        return 64
    login = getattr(mod, "login", None)
    if login is None:
        print(f"error: connector `{name}` has no OAuth login flow", file=sys.stderr)
        return 64
    try:
        result: Result = login()
    except Exception as e:  # noqa: BLE001
        traceback.print_exc()
        print(f"FAIL: {e}", file=sys.stderr)
        return 1
    return render([result])


def login_main(name: str, argv: list[str] | None = None) -> int:
    p = argparse.ArgumentParser(
        prog=f"creds_login_{name}",
        description=f"Run the OAuth login flow for the `{name}` connector "
        f"and save the resulting credentials under ~/.config/creds/. "
        f"A timestamped run log is written under ~/.config/creds/logs/.",
    )
    p.add_argument(
        "--no-log",
        action="store_true",
        help="Don't tee output to ~/.config/creds/logs/.",
    )
    args = p.parse_args(argv)

    if args.no_log:
        return _do_login(name)
    with capture(f"login-{name}") as log_path:
        rc = _do_login(name)
        print(f"# log: {log_path}")
    return rc


def validate_main(argv: list[str] | None = None) -> int:
    p = argparse.ArgumentParser(
        prog="creds_validate",
        description="Validate every configured credentials connector. "
        "Each connector reports OK / MISCONFIGURED / FAIL. A timestamped "
        "run log is written under ~/.config/creds/logs/ (auto-pruned "
        "after 7 days; override with CREDS_LOG_RETENTION_DAYS).",
    )
    p.add_argument(
        "connectors",
        nargs="*",
        help=f"Optional subset; default = all of: {', '.join(_connectors.NAMES)}",
    )
    p.add_argument("--list", action="store_true", help="Print known connectors and exit")
    p.add_argument("--no-log", action="store_true", help="Don't tee output to ~/.config/creds/logs/.")
    args = p.parse_args(argv)

    if args.list:
        for n in _connectors.NAMES:
            print(n)
        return 0

    def _run() -> int:
        load_zshenv()
        names = args.connectors or _connectors.NAMES
        results: list[Result] = []
        for n in names:
            try:
                mod = _connectors.load(n)
            except KeyError:
                results.append(Result(n, "FAIL", "unknown connector"))
                continue
            try:
                results.append(mod.validate())
            except Exception as e:  # noqa: BLE001
                results.append(Result(n, "FAIL", f"unhandled exception: {e}"))
        return render(results)

    if args.no_log:
        return _run()
    with capture("validate") as log_path:
        rc = _run()
        print(f"# log: {log_path}")
    return rc
