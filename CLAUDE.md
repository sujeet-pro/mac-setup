# mac-setup

Ansible-based macOS development environment setup. Runs on localhost to install
packages, configure apps, set system defaults, and symlink/template config files.

## Architecture

- **Playbook**: `setup.yml` — orchestrates all roles in order
- **Roles** (under `roles/`): homebrew, mise, shell, git, ssh, apps, aws, dev-tools, macos
- **`configs/`** — all app config files, organized by app (deployed to the system via symlinks)
- **Templates** (Jinja2) for config with personal data (`.gitconfig`, `.ssh/config`) — live in `roles/<role>/templates/`
- **Env vars** live in `~/.zshenv` (never committed) — see `configs/shell/.zshenv.example`
- **Repo-specific config** (`.vscode/`, `.claude/commands/`, `CLAUDE.md`) stays at the root — these configure how to work on THIS repo, not the system

## Key Files

| File | Purpose |
|------|---------|
| `setup.yml` | Main Ansible playbook |
| `setup.sh` | One-command bootstrap (installs Xcode tools, Homebrew, Ansible) |
| `Makefile` | Convenience targets: setup, update, check, validate, test, test-vm |
| `configs/` | All app configuration files, organized by app |
| `roles/homebrew/vars/main.yml` | Homebrew formulae and casks lists |
| `roles/apps/vars/main.yml` | VS Code extensions list |
| `roles/macos/vars/main.yml` | macOS system defaults values |
| `scripts/validate.sh` | Quick validation of tools, configs, symlinks, env vars, defaults |

## Adding Packages

- **Homebrew formula**: add to `homebrew_formulae` in `roles/homebrew/vars/main.yml`
- **Homebrew cask**: add to `homebrew_casks` in `roles/homebrew/vars/main.yml`
- **VS Code extension**: add to `vscode_extensions` in `roles/apps/vars/main.yml`
  AND to `recommendations` in `.vscode/extensions.json`

## Adding App Configs

- Place config files under `configs/<app-name>/`
- Add symlink tasks to the appropriate role in `roles/<role>/tasks/main.yml`
- Add validation checks to `scripts/validate.sh`
- Update the sync command in `.claude/commands/sync.md`

## Testing

```sh
make validate     # Quick check: tools, configs, symlinks, env vars, defaults
make test         # validate + Ansible syntax check
make check        # Dry-run: show what would change
make test-vm      # Full end-to-end in a clean macOS VM (slow, first run ~15 GB)
```

## Conventions

- No secrets in the repo — personal data goes through env vars and templates
- Use fully-qualified Ansible module names (`ansible.builtin.file`, `community.general.osx_defaults`)
- Every task must have tags
- Keep vars in `roles/<role>/vars/main.yml`, tasks in `roles/<role>/tasks/main.yml`
- App configs go in `configs/<app>/`, repo-specific configs stay at root
- Prefer `community.general.osx_defaults` over raw `defaults write` commands
