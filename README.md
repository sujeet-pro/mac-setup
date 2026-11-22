# mac-setup

A clean, minimal macOS development environment setup and dotfile management toolkit for a personal home Mac. No Ansible required.

## Fresh Mac Setup (Copy-Paste Step by Step)

Before formatting, review the [Pre-Format Checklist](./MANUAL-SETUP.md#0-before-formatting-pre-format-checklist). After reinstalling macOS, open **Terminal** and copy-paste each block one by one:

### 1. Install Xcode Command Line Tools
Wait for the macOS popup installer to finish before moving to Step 2.
```sh
xcode-select --install
```

### 2. Install Homebrew
```sh
/bin/bash -c "$(curl -fsSL https://raw.githubusercontent.com/Homebrew/install/HEAD/install.sh)"
```

### 3. Configure Mac Name, Firewall & Touch ID for `sudo`
```sh
sudo scutil --set ComputerName "Sujeet's MacBook"
sudo scutil --set LocalHostName "Sujeets-MacBook"
sudo scutil --set HostName "Sujeets-MacBook"
sudo defaults write /Library/Preferences/SystemConfiguration/com.apple.smb.server NetBIOSName -string "Sujeets-MacBook"
dscacheutil -flushcache
sudo /usr/libexec/ApplicationFirewall/socketfilterfw --setglobalstate on
sudo /usr/libexec/ApplicationFirewall/socketfilterfw --setstealthmode on
sed 's/^#auth/auth/' /etc/pam.d/sudo_local.template | sudo tee /etc/pam.d/sudo_local > /dev/null
```

### 4. Clone & Run Automated Setup
Installs `Brewfile` apps & CLI tools, **Junie CLI**, symlinks dotfiles, installs `mise` runtimes, and applies macOS defaults:
```sh
mkdir -p ~/workspace && git clone https://github.com/sujeet-pro/mac-setup.git ~/workspace/mac-setup && cd ~/workspace/mac-setup && ./setup.sh
```

### 5. Reload Shell
```sh
exec zsh
```

### 6. Validate Environment
```sh
~/workspace/mac-setup/setup.sh --validate
```

### 7. Set Git Email & Regenerate GitHub SSH Key
Replace `your-email@example.com` with your email:
```sh
EMAIL="your-email@example.com"
git config --file ~/.gitconfig.local user.email "$EMAIL"
ssh-keygen -t ed25519 -C "$EMAIL"
eval "$(ssh-agent -s)"
ssh-add --apple-use-keychain ~/.ssh/id_ed25519
```

Sign in to GitHub CLI:
```sh
gh auth login
```

Upload the new SSH key & verify connection (then delete the old key in **GitHub → Settings → SSH and GPG keys**):
```sh
gh ssh-key add ~/.ssh/id_ed25519.pub --title "Sujeet's MacBook" && ssh -T git@github.com
```

### 8. Authenticate Junie CLI & Add Private Tokens
```sh
junie
```

Add any personal API keys or private tokens to untracked `~/.zshenv`:
```sh
zed ~/.zshenv
```

### 9. Finish GUI App Configuration
Open **[MANUAL-SETUP.md](./MANUAL-SETUP.md)** for exact click-by-click settings:
- **NordVPN**: Sign in → Launch at Login → **NordLynx** → **Auto-Connect: Always** → **Internet Kill Switch** ON → **Threat Protection Pro** ON
- **NordPass**: Sign in → enable macOS **AutoFill & Passwords** + Brave/Chrome extensions
- **Warp**: Font → `JetBrainsMono Nerd Font`, Prompt → **Honor user's custom prompt (PS1)**
- **JetBrains Toolbox**: Sign in, install IDEs, enable **Generate shell scripts** (`~/.local/bin`)
- **Docker Desktop**: Accept license, set CPU/RAM + VirtioFS
- **Rectangle / Maccy / Logi Options+**: Grant Accessibility / Input Monitoring permissions

---

## Highlights

- **Single `Brewfile`**: Minimal set of CLI tools, **Warp**, **JetBrains Toolbox**, **Zed**, **Docker Desktop**, **NordVPN + NordPass**, **Brave & Chrome**, **Rectangle/Maccy/Logi Options+**, and **JetBrainsMono Nerd Font**.
- **Junie CLI**: Installed automatically by `./setup.sh`.
- **Terminal-Agnostic CLI**: Modular Zsh (`zshenv.zsh`, `aliases.zsh`, `functions/`), **Starship**, `eza`, `bat`, `fzf`, `fd`, `ripgrep`, `zoxide`, `atuin`, `lazygit`, `git-delta`, and `mise` — works identically in Warp, JetBrains integrated terminal, and macOS Terminal.
- **Safe Dotfile Symlinking**: Mirrors `home/` directly into `$HOME` with timestamped backups of any existing non-symlink files.
- **Clean `.zshenv` Separation**: Public environment config lives in tracked `home/.config/zsh/zshenv.zsh`; private tokens stay in untracked `~/.zshenv`.

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
