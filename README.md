# mac-setup

A clean, minimal macOS development environment setup and dotfile management toolkit for a personal home Mac. No Ansible required.

## Highlights

- **Single `Brewfile`**: Minimal set of CLI tools, **Warp**, **JetBrains Toolbox**, **Zed**, **Docker Desktop**, **NordVPN + NordPass**, **Brave & Chrome**, **Rectangle/Maccy/Logi Options+**, and **JetBrainsMono Nerd Font**.
- **Junie CLI**: Installed automatically by `./setup.sh`.
- **Terminal-Agnostic CLI**: Modular Zsh (`zshenv.zsh`, `aliases.zsh`, `functions/`), **Starship**, `eza`, `bat`, `fzf`, `fd`, `ripgrep`, `zoxide`, `atuin`, `lazygit`, `git-delta`, and `mise` — works identically in Warp, JetBrains integrated terminal, and macOS Terminal.
- **Safe Dotfile Symlinking**: Mirrors `home/` directly into `$HOME` with timestamped backups of any existing non-symlink files.
- **Clean `.zshenv` Separation**: Public environment config lives in tracked `home/.config/zsh/zshenv.zsh`; private tokens stay in untracked `~/.zshenv`.

---

## Fresh Mac Setup

Follow **[MANUAL-SETUP.md](./MANUAL-SETUP.md)** for the full step-by-step checklist, including:
1. Pre-format backup checklist (repos, recovery codes, `.env` secrets, personal files)
2. Manual prerequisites (**Xcode Command Line Tools** & **Homebrew**)
3. **macOS system configuration commands** (Mac name/hostname, Firewall + Stealth Mode, Touch ID for `sudo`)
4. Running `./setup.sh`
5. Always-on system-level **NordVPN** + **NordPass** configuration
6. **Warp**, **JetBrains Toolbox**, **Junie CLI**, **Docker Desktop**, and fresh GitHub SSH key setup

### Quick Start (After Prerequisites)

```sh
git clone https://github.com/sujeet-pro/mac-setup.git ~/workspace/mac-setup
cd ~/workspace/mac-setup
./setup.sh
```

---

## Usage

```sh
./setup.sh                  # Full setup (Brewfile, Junie CLI, dotfiles, mise, macOS defaults)
./setup.sh --link           # Symlink dotfiles into $HOME and configure ~/.zshenv only
./setup.sh --macos-defaults # Apply macOS UI/Finder/Dock/keyboard defaults only
./setup.sh --validate       # Run environment health checks
./setup.sh --dump           # Dump installed Homebrew packages to Brewfile.local
./setup.sh --no-brew        # Run setup without brew bundle
./setup.sh --dry-run        # Preview actions without executing
```

---

## Directory Structure

```
mac-setup/
├── Brewfile                     # Homebrew formulae, casks, and JetBrainsMono Nerd Font
├── Brewfile.local               # Optional machine-local overrides (gitignored)
├── MANUAL-SETUP.md              # Prerequisites, macOS system commands, VPN & app config guide
├── setup.sh                     # Main setup orchestrator
├── bootstrap-remote.sh          # One-liner remote bootstrap helper
├── home/                        # Dotfiles mirrored to $HOME via symlinks
│   ├── .config/
│   │   ├── agents/              # Global AGENTS.md guidelines for Junie
│   │   ├── btop/                # btop monitor config
│   │   ├── gh/                  # GitHub CLI config
│   │   ├── git/                 # Global gitignore
│   │   ├── mise/                # Language runtime versions (Node, Python, Go, Java, etc.)
│   │   ├── starship.toml        # Starship prompt config (Nerd Font icons)
│   │   ├── zed/                 # Zed lightweight editor config
│   │   └── zsh/
│   │       ├── zshenv.zsh       # Public environment variables & PATH
│   │       ├── aliases.zsh      # Shell aliases (eza, bat, git, system)
│   │       └── functions/       # Interactive zsh functions (fif, fcd, flog, killport, etc.)
│   ├── .gitconfig               # Git configuration (with delta pager & Zed editor)
│   ├── .npmrc                   # npm configuration
│   ├── .zprofile                # Login shell configuration
│   └── .zshrc                   # Interactive shell configuration
└── scripts/
    ├── helpers/
    │   ├── link-dotfiles.sh     # Non-destructive dotfile symlinker
    │   ├── setup-zshenv.sh      # Safe ~/.zshenv loader configurator
    │   └── macos-defaults.sh    # macOS sensible defaults
    └── validate.sh              # System diagnostic & validator
```
