# User Scripts

Portable CLI scripts managed by this mac-setup repo. Each script is symlinked to
`~/.local/bin/<script-name>` so it's available from any directory.

## Structure

```
user_scripts/
├── README.md
├── <script-file>.sh              # Simple single-file script
├── <script-name>/                # Multi-file script (single entry point)
│   ├── index.sh (or index.py)    # Entry point (this gets symlinked)
│   └── ...                       # Supporting files
└── <pkg-name>/                   # Multi-binary tool
    ├── bin/<binary-1>            # Every file under bin/ gets symlinked
    ├── bin/<binary-2>            # to ~/.local/bin/<basename>
    └── ...                       # Library code (not symlinked)
```

Note: the credentials tooling that used to live here moved to
`configs/creds/_lib/` (managed by the dedicated `roles/creds/` Ansible role,
not by the generic user-scripts symlinker).

### Rules

1. **Single-file scripts** — place directly as `user_scripts/<name>.sh`
2. **Multi-file scripts** — create a folder `user_scripts/<name>/` with an `index.sh`
   (or `index.py`) as the entry point
3. **Multi-binary tools** — put each executable in `user_scripts/<pkg>/bin/`; every
   file there gets symlinked into `~/.local/bin/<filename>`. Shared library code
   sits next to `bin/` and is resolved at runtime via `Path(__file__).resolve()`.
4. **Config** goes in `~/.config/user_scripts/<script-name>.json5` (never in the repo)
5. Scripts must be executable (`chmod +x`)
6. Entry points should have a shebang line (`#!/usr/bin/env bash` or `#!/usr/bin/env python3`)

### Adding a new script

1. Create the file or folder under `user_scripts/`
2. Run `make update` — the Ansible role auto-discovers and symlinks everything
3. Validation is included in `make validate`

### Config convention

Scripts that need persistent config should use:

```
Default:  ~/.config/user_scripts/<script-name>.json5
Override: --config /path/to/custom-config.json5
```

The `~/.config/user_scripts/` directory is created automatically by the Ansible role.
