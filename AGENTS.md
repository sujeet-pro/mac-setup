# AGENTS.md — mac-setup Development Guide

Personal home macOS development environment setup and dotfile management toolkit without Ansible.

## Architecture

- **Homebrew Bundle**:
  - `Brewfile` — single minimal bundle for personal home Mac (CLI tools, Warp, JetBrains Toolbox, Zed, Docker Desktop, NordVPN, NordPass, Brave, Chrome, Rectangle, Maccy, Logi Options+, JetBrainsMono Nerd Font).
  - `Brewfile.local` — optional machine-specific local overrides (gitignored).
- **Junie CLI**: Installed via official install script inside `setup.sh`.
- **Dotfiles & Configurations** (`home/`):
  - Directly mirrored to `$HOME` via safe symlinks created by `./setup.sh --link`.
  - App configs: `.config/starship.toml`, `.config/mise/config.toml`, `.config/zed/`, `.config/gh/`, `.config/btop/`, etc.
  - Zsh modular setup: `.config/zsh/zshenv.zsh` (public env), `.config/zsh/aliases.zsh`, `.config/zsh/functions/`.
- **Environment Separation**:
  - Public environment variables live in `home/.config/zsh/zshenv.zsh`.
  - `~/.zshenv` remains untracked and automatically sources `~/.config/zsh/zshenv.zsh` without overwriting private tokens.
- **Manual Setup (`MANUAL-SETUP.md`)**:
  - Documents manual prerequisites (Xcode CLT, Homebrew), macOS system commands (Mac hostname, Firewall, Touch ID for `sudo`), always-on NordVPN + NordPass setup, and app configurations.

## Common Commands

```sh
./setup.sh                  # Full setup (Brewfile, Junie CLI, dotfiles, mise, macOS defaults)
./setup.sh --link           # Symlink dotfiles into $HOME only
./setup.sh --macos-defaults # Apply macOS system defaults
./setup.sh --validate       # Run environment validation
./setup.sh --dump           # Dump local Homebrew state to Brewfile.local
./setup.sh --dry-run        # Preview actions without executing
```

## Conventions

- No secrets in the repository — keep tokens in `~/.zshenv` or local `.env` files.
- Keep `Brewfile` minimal and focused on tools actually used on a personal home Mac.
- All symlinking must be non-destructive (back up existing non-symlink files with timestamp).
