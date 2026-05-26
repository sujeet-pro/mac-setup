#!/usr/bin/env python3
"""userscripts creds — credential management dispatcher.

Forwards remaining arguments to creds_lib.driver.main(). Subcommands:
  validate [svc ...] [--json|--list|--list-json]   probe one/many/all
  login    <svc>                                   OAuth or guided token mint
  status                                           services table (also default)
  rotate   <svc>                                   rotate provider-side credentials
  completion <shell>                               emit shell completion script

Run `userscripts creds --help` for the full list.
"""

from __future__ import annotations

import pathlib
import sys

_HERE = pathlib.Path(__file__).resolve().parent
sys.path.insert(0, str(_HERE))

from creds_lib.driver import main  # noqa: E402

if __name__ == "__main__":
    raise SystemExit(main(sys.argv[1:]))
