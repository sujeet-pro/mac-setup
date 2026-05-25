"""Top-level `creds` CLI dispatcher.

Subcommands:
  validate   [svc ...] [--json|--list|--list-json] — probe one/many/all
  login      <svc>                                 — OAuth or guided token mint
  status                                           — services table (also default)
  rotate     <svc>                                 — invoke per-svc scripts/rotate.sh
  completion <shell>                               — emit shell completion script

Service names accept aliases: `jira` → `atlassian`, `gh` → `github`, etc.
"""

from __future__ import annotations

import argparse
import json
import shlex
import subprocess
import sys

from . import CREDS_DIR
from . import aliases as _aliases
from . import connectors as _connectors
from . import meta as _meta
from . import token_login
from .env import load_zshenv
from .logs import capture
from .status import Result, render


def _resolve_or_exit(name: str) -> str:
    try:
        return _aliases.resolve(name)
    except KeyError as e:
        print(f"error: {e}", file=sys.stderr)
        print("       run `creds status` to see all services + aliases.", file=sys.stderr)
        sys.exit(64)


def _services_table() -> str:
    rows: list[tuple[str, str, str, str]] = [("SERVICE", "AUTH", "VALIDATOR", "ALIASES")]
    for name in _meta.all_names():
        m = _meta.get(name)
        validator = "yes" if m.has_connector else "—"
        aliases = ", ".join(_aliases.aliases_for(name)) or "—"
        rows.append((name, m.auth, validator, aliases))
    widths = [max(len(r[i]) for r in rows) for i in range(len(rows[0]))]
    out: list[str] = []
    for i, r in enumerate(rows):
        out.append("  ".join(c.ljust(widths[j]) for j, c in enumerate(r)))
        if i == 0:
            out.append("  ".join("─" * w for w in widths))
    return "\n".join(out)


def _do_validate(services: list[str], as_json: bool) -> int:
    load_zshenv()
    names = services or list(_connectors.NAMES)
    results: list[Result] = []
    for n in names:
        if n not in _connectors.NAMES:
            results.append(Result(n, "SKIPPED", "no validator (config-only or token-only service)"))
            continue
        try:
            mod = _connectors.load(n)
        except KeyError:
            results.append(Result(n, "FAIL", "unknown connector"))
            continue
        try:
            results.append(mod.validate())
        except Exception as e:  # noqa: BLE001
            results.append(Result(n, "FAIL", f"unhandled exception: {e}"))

    if as_json:
        out = {
            "services": {
                r.connector: {
                    "status": r.state,
                    "message": r.message,
                    "missing_env": list(r.missing),
                    "sample": r.sample,
                }
                for r in results
            }
        }
        print(json.dumps(out, indent=2))
        rc = 0
        for r in results:
            if r.state == "FAIL":
                rc = max(rc, 1)
            elif r.state == "MISCONFIGURED":
                rc = max(rc, 2)
        if not results:
            rc = 3
        return rc

    return render(results)


def _do_login(svc: str) -> int:
    load_zshenv()
    m = _meta.get(svc)
    if m.has_login_fn:
        mod = _connectors.load(svc)
        try:
            result = mod.login()
        except Exception as e:  # noqa: BLE001
            import traceback
            traceback.print_exc()
            print(f"FAIL: {e}", file=sys.stderr)
            return 1
        return render([result])
    if m.auth == "token":
        return render([token_login.run(m)])
    if m.auth == "hosted-oauth":
        print(f"{svc}: OAuth is handled by the hosted MCP client — no local login needed.")
        print(f"       (set config vars: {', '.join(m.config_vars) or '(none)'})")
        return 0
    print(f"{svc}: no login flow available (auth={m.auth})", file=sys.stderr)
    return 64


def _emit_zsh_completion() -> int:
    services = _meta.all_names()
    all_aliases = sorted(_aliases.ALIASES.keys())
    rotate_services = [s for s in services if _meta.get(s).rotate_script]
    services_arr = " ".join(shlex.quote(s) for s in services)
    aliases_arr = " ".join(shlex.quote(a) for a in all_aliases)
    rotate_arr = " ".join(shlex.quote(s) for s in rotate_services)
    print(f"""#compdef creds

_creds() {{
  local -a subcommands services aliases rotate_services
  subcommands=(
    'validate:Probe connectors'
    'login:Run login flow for one service'
    'status:Print services table'
    'list:Alias for status'
    'rotate:Run rotation script for one service'
    'completion:Emit shell completion script'
  )
  services=({services_arr})
  aliases=({aliases_arr})
  rotate_services=({rotate_arr})

  if (( CURRENT == 2 )); then
    _describe -t commands 'creds subcommand' subcommands
    return
  fi
  case "$words[2]" in
    validate|login)
      _values 'service' $services $aliases
      ;;
    rotate)
      _values 'service' $rotate_services
      ;;
    completion)
      _values 'shell' zsh
      ;;
  esac
}}

compdef _creds creds
""")
    return 0


def _do_rotate(svc: str) -> int:
    m = _meta.get(svc)
    if not m.rotate_script:
        print(f"{svc}: no rotation script defined.", file=sys.stderr)
        return 64
    path = CREDS_DIR / svc / "scripts" / m.rotate_script
    if not path.is_file():
        print(f"{svc}: rotation script missing at {path}", file=sys.stderr)
        return 1
    return subprocess.call([str(path)])


def main(argv: list[str] | None = None) -> int:
    p = argparse.ArgumentParser(
        prog="creds",
        description=(
            "Unified CLI for the $CREDS_HOME/ credential layout. "
            "Service names accept aliases (jira→atlassian, gh→github, dd→datadog, …). "
            "Run `creds status` to see them all."
        ),
        formatter_class=argparse.RawDescriptionHelpFormatter,
    )
    sub = p.add_subparsers(dest="cmd")

    pv = sub.add_parser("validate", help="Probe connectors")
    pv.add_argument("services", nargs="*", help="Subset; default = every service with a validator")
    pv.add_argument("--json", action="store_true", help="Emit machine-readable JSON")
    pv.add_argument("--list", action="store_true", help="Print connector names and exit")
    pv.add_argument(
        "--list-json",
        action="store_true",
        help="Print all services + aliases as JSON (for shell completion / /adk-setup --check)",
    )
    pv.add_argument("--no-log", action="store_true", help="Don't tee output to $CREDS_HOME/logs/")

    pl = sub.add_parser("login", help="Run login flow for one service")
    pl.add_argument("service", help="Service name (canonical or alias)")
    pl.add_argument("--no-log", action="store_true", help="Don't tee output to $CREDS_HOME/logs/")

    sub.add_parser("status", help="Print services table (default when no subcommand given)")
    sub.add_parser("list", help="Alias for `status`")

    pr = sub.add_parser("rotate", help="Run rotation script for one service")
    pr.add_argument("service", help="Service name (canonical or alias)")

    pc = sub.add_parser("completion", help="Emit shell completion script")
    pc.add_argument("shell", choices=["zsh"], help="Shell to generate completion for")

    args = p.parse_args(argv)

    if args.cmd is None:
        # No subcommand: launch the interactive TUI when on a TTY, else
        # fall back to the plain status table. The TUI module handles its
        # own textual-not-installed degradation.
        if sys.stdin.isatty() and sys.stdout.isatty():
            from .tui import run as _tui_run
            return _tui_run()
        print(_services_table())
        return 0

    if args.cmd in ("list", "status"):
        print(_services_table())
        return 0

    if args.cmd == "validate":
        if args.list:
            for n in _connectors.NAMES:
                print(n)
            return 0
        if args.list_json:
            out = [
                {
                    "name": n,
                    "auth": _meta.get(n).auth,
                    "has_connector": _meta.get(n).has_connector,
                    "aliases": _aliases.aliases_for(n),
                }
                for n in _meta.all_names()
            ]
            print(json.dumps(out, indent=2))
            return 0
        services = [_resolve_or_exit(s) for s in args.services]
        if args.no_log:
            return _do_validate(services, args.json)
        with capture("validate") as log_path:
            rc = _do_validate(services, args.json)
            if not args.json:
                print(f"# log: {log_path}")
        return rc

    if args.cmd == "login":
        svc = _resolve_or_exit(args.service)
        if args.no_log:
            return _do_login(svc)
        with capture(f"login-{svc}") as log_path:
            rc = _do_login(svc)
            print(f"# log: {log_path}")
        return rc

    if args.cmd == "rotate":
        svc = _resolve_or_exit(args.service)
        return _do_rotate(svc)

    if args.cmd == "completion":
        if args.shell == "zsh":
            return _emit_zsh_completion()
        return 64

    return 0
