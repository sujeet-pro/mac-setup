"""Interactive textual TUI for `userscripts creds`.

Runs when the user invokes `userscripts creds` with no subcommand AND textual is
installed. Falls back to the plain `userscripts creds status` table otherwise.

Layout (single screen):
  Header
  ──────
  DataTable: service / auth / validator / status / message
  ──────
  RichLog: streaming output from validate/login
  Footer (key bindings)

Bindings:
  v   validate selected
  V   validate all (capital v)
  l   login selected (OAuth → connector.login(); token → guided getpass)
  r   refresh service list (re-runs `userscripts creds validate --json` for all)
  q   quit

Token-login flows that need keyboard input run by suspending the TUI
(textual's `suspend()` context), invoking the existing token_login.run()
which uses getpass, then resuming the TUI. The secret is never read
into the textual app's reactive state.
"""

from __future__ import annotations

import sys
from typing import Any

from . import aliases as _aliases
from . import connectors as _connectors
from . import meta as _meta
from . import token_login
from .env import load_zshenv
from .status import Result


def _tui_available() -> bool:
    try:
        import textual  # noqa: F401
        return True
    except ImportError:
        return False


def run() -> int:
    """Launch the TUI. Returns process exit code."""
    if not _tui_available():
        sys.stderr.write(
            "creds TUI requires `textual`. Install with one of:\n"
            "    uv tool install textual\n"
            "    pipx install textual\n"
            "    pip install --user textual\n"
            "Falling back to `userscripts creds status`.\n\n"
        )
        from .driver import _services_table
        print(_services_table())
        return 0

    if not sys.stdin.isatty() or not sys.stdout.isatty():
        sys.stderr.write("creds TUI requires a TTY. Falling back to `userscripts creds status`.\n\n")
        from .driver import _services_table
        print(_services_table())
        return 0

    load_zshenv()
    return _run_textual()


def _run_textual() -> int:
    # Imports here so the module loads even when textual is absent.
    from textual.app import App, ComposeResult
    from textual.binding import Binding
    from textual.containers import Vertical
    from textual.widgets import DataTable, Footer, Header, RichLog

    class CredsApp(App):
        CSS = """
        Screen { layout: vertical; }
        DataTable { height: 1fr; }
        RichLog { height: 12; border: solid $accent; }
        """
        BINDINGS = [
            Binding("v", "validate_selected", "Validate"),
            Binding("V", "validate_all", "Validate all"),
            Binding("l", "login_selected", "Login"),
            Binding("r", "refresh", "Refresh"),
            Binding("q", "quit", "Quit"),
        ]

        def compose(self) -> ComposeResult:
            yield Header(show_clock=False)
            with Vertical():
                yield DataTable(id="services", cursor_type="row", zebra_stripes=True)
                yield RichLog(id="log", highlight=True, markup=True, wrap=True)
            yield Footer()

        def on_mount(self) -> None:
            self.title = "creds — credential connector status"
            self.sub_title = "v=validate · V=all · l=login · r=refresh · q=quit"
            table: DataTable = self.query_one("#services", DataTable)
            table.add_columns("Service", "Auth", "Validator", "Status", "Message")
            self._populate_rows()

        def _populate_rows(self, results: dict[str, Result] | None = None) -> None:
            results = results or {}
            table: DataTable = self.query_one("#services", DataTable)
            table.clear()
            for name in _meta.all_names():
                m = _meta.get(name)
                validator = "yes" if m.has_connector else "—"
                r = results.get(name)
                status = r.state if r else "—"
                message = r.message if r else ""
                table.add_row(name, m.auth, validator, status, message, key=name)

        def _log_line(self, line: str) -> None:
            log: RichLog = self.query_one("#log", RichLog)
            log.write(line)

        # --- actions ---
        def action_quit(self) -> None:
            self.exit(0)

        def action_refresh(self) -> None:
            self._log_line("[bold]refresh[/] — validating all services with connectors…")
            self._validate_many(_connectors.NAMES)

        def action_validate_all(self) -> None:
            self.action_refresh()

        def action_validate_selected(self) -> None:
            svc = self._current_service()
            if not svc:
                return
            if svc not in _connectors.NAMES:
                self._log_line(f"[yellow]{svc}: no validator (config-only or token-only service)[/]")
                return
            self._log_line(f"[bold]validate[/] {svc} …")
            self._validate_many([svc])

        def action_login_selected(self) -> None:
            svc = self._current_service()
            if not svc:
                return
            m = _meta.get(svc)
            if m.auth == "hosted-oauth":
                self._log_line(
                    f"[yellow]{svc}[/]: hosted OAuth — handled by the MCP client. "
                    f"Set config vars: {', '.join(m.config_vars) or '(none)'}"
                )
                return
            if m.auth == "oauth" and m.has_login_fn:
                self._log_line(f"[bold]login[/] {svc} — running OAuth flow (suspending TUI)…")
                with self.suspend():
                    try:
                        mod = _connectors.load(svc)
                        result = mod.login()
                    except Exception as e:  # noqa: BLE001
                        result = Result(svc, "FAIL", f"login exception: {e}")
                self._log_line(self._format_result(result))
                return
            if m.auth == "token":
                self._log_line(f"[bold]login[/] {svc} — prompting for tokens (suspending TUI)…")
                with self.suspend():
                    result = token_login.run(m)
                self._log_line(self._format_result(result))
                return
            self._log_line(f"[red]{svc}: no login flow available (auth={m.auth})[/]")

        # --- helpers ---
        def _current_service(self) -> str | None:
            table: DataTable = self.query_one("#services", DataTable)
            if table.row_count == 0:
                return None
            row_key = table.coordinate_to_cell_key(table.cursor_coordinate).row_key
            return row_key.value

        def _validate_many(self, names: list[str]) -> None:
            results: dict[str, Result] = {}
            for n in names:
                if n not in _connectors.NAMES:
                    continue
                try:
                    mod = _connectors.load(n)
                    r = mod.validate()
                except Exception as e:  # noqa: BLE001
                    r = Result(n, "FAIL", f"unhandled: {e}")
                results[n] = r
                self._log_line(self._format_result(r))
            self._populate_rows(results)

        def _format_result(self, r: Result) -> str:
            color = {"OK": "green", "FAIL": "red", "MISCONFIGURED": "yellow", "SKIPPED": "grey50"}.get(
                r.state, "white"
            )
            extra = f" — {r.message}" if r.message else ""
            sample = f"  [grey50](sample: {r.sample})[/]" if r.sample else ""
            return f"[{color}]{r.state:>13}[/] {r.connector}{extra}{sample}"

    app = CredsApp()
    app.run()
    return 0
