# Manual Installation Guide

Step-by-step manual setup of everything this repo automates — for when you want
to bootstrap a Mac (or understand each piece) **without** running Ansible.

This guide mirrors the repo's source of truth:
- Packages → `roles/homebrew/vars/main.yml`
- Runtimes → `configs/mise/config.toml` + `roles/mise/vars/main.yml`
- Editor extensions → `roles/apps/vars/main.yml`
- Config symlinks → `roles/<role>/tasks/main.yml`
- System defaults → `roles/macos/vars/main.yml`

> **The automated path is still preferred.** Run `./setup.sh` (or `make setup`).
> Use this document for a fresh machine where you'd rather go piece by piece, for
> recovery, or as a reference for what each tool/setting is.

---

## 0. Conventions

- `$REPO` = this repo, assumed at `~/personal/mac-setup`.
- Commands are idempotent where possible; re-running is safe.
- Symlinks point **from** your home dir **to** files in `$REPO/configs/`.
- Never put secrets in the repo. Identity + secrets live in `~/.zshenv` and
  `$CREDS_HOME` (see step 3).

```sh
export REPO="$HOME/personal/mac-setup"
```

---

## 1. Prerequisites

```sh
# Xcode command-line tools (git, compilers, etc.)
xcode-select --install

# Homebrew
/bin/bash -c "$(curl -fsSL https://raw.githubusercontent.com/Homebrew/install/HEAD/install.sh)"

# Load brew into the current shell (Apple Silicon path)
eval "$(/opt/homebrew/bin/brew shellenv)"
```

Clone this repo:

```sh
mkdir -p ~/personal
git clone <your-remote> ~/personal/mac-setup
```

---

## 2. Homebrew formulae (CLI tools)

Install one by one, or all at once at the end of the section. Each line notes
what the tool does.

### Core shell & prompt
```sh
brew install zsh                      # shell
brew install zsh-autosuggestions      # fish-like inline suggestions
brew install zsh-completions          # extra completion definitions
brew install zsh-syntax-highlighting  # command syntax highlighting
brew install starship                 # cross-shell prompt
brew install fzf                      # fuzzy finder (keybindings set in step 11)
brew install git                      # version control
brew install git-filter-repo          # history rewriting
```

### GNU userland (macOS catch-up — installed g-prefixed: gls, gcp, gsed, …)
```sh
brew install coreutils findutils gawk gnu-sed gnu-tar grep
```

### Modern CLI replacements
```sh
brew install bat      # cat with syntax highlighting
brew install eza      # modern ls
brew install fd       # modern find
brew install ripgrep  # fast grep (rg)
brew install tlrc     # tldr client (simplified man pages)
brew install zoxide   # smarter cd (z)
```

### Dev tools
```sh
brew install actionlint   # lint GitHub Actions workflows
brew install btop         # resource monitor (config in step 12)
brew install difftastic   # structural diff
brew install gh           # GitHub CLI (config in step 12)
brew install git-delta    # better git diffs/pager
brew install hurl         # HTTP testing/runner
brew install jq           # JSON processor
brew install lazygit      # git TUI
brew install shellcheck   # shell script linter
brew install tree         # directory tree
brew install yq           # YAML processor
```

### Infra & automation
```sh
brew install ansible      # this repo's automation engine
brew install mise          # runtime version manager (step 9)
brew install opentofu     # Terraform-compatible IaC
```

### Cloud & infra
```sh
brew install awscli         # AWS CLI (config in step 13)
brew install cloudflared    # Cloudflare tunnel client
brew install helm           # Kubernetes package manager
brew install kubernetes-cli # kubectl
brew install okta-aws-cli   # Okta → AWS credential bridge
```

### Database
```sh
brew install libpq          # PostgreSQL client libs (psql)
brew install postgresql@18  # PostgreSQL server/client
```

### JVM tooling
```sh
brew install coursier       # Scala/JVM artifact + app manager
```

### Local AI
```sh
brew install ollama         # run LLMs locally
```

### Shell history
```sh
brew install atuin          # synced, searchable shell history (login in step 14)
```

### All formulae at once
```sh
brew install zsh zsh-autosuggestions zsh-completions zsh-syntax-highlighting \
  starship fzf git git-filter-repo coreutils findutils gawk gnu-sed gnu-tar grep \
  bat eza fd ripgrep tlrc zoxide actionlint btop difftastic gh git-delta hurl jq \
  lazygit shellcheck tree yq ansible mise opentofu awscli cloudflared helm \
  kubernetes-cli okta-aws-cli libpq postgresql@18 coursier ollama atuin
```

---

## 3. Environment variables (`~/.zshenv`)

The shell config is driven entirely by env vars. **Do this before rendering git /
ssh configs**, because the Ansible templates (and the manual steps below) read
these values.

1. Review the template (keys only — fill in your own values):
   ```sh
   bat $REPO/configs/shell/.zshenv.example
   ```
2. Create your real `~/.zshenv`. In this repo the canonical copy lives in your
   synced data dir and is symlinked:
   ```sh
   # repo's helper does this safely:
   bash $REPO/scripts/migrate-to-synced.sh
   # → creates ~/user-synced-data/mac-setup/zshenv and symlinks ~/.zshenv to it
   ```
   Or, fully manual: copy the example and edit it.
   ```sh
   cp $REPO/configs/shell/.zshenv.example ~/.zshenv
   $EDITOR ~/.zshenv
   ```
3. Per-machine overrides (never synced):
   ```sh
   printf '# Per-machine overrides for ~/.zshenv. Never synced.\n' > ~/.zshenv.local
   chmod 600 ~/.zshenv.local
   ```

**Required vars** (setup fails without them):
`GIT_USER_NAME`, `CREDS_HOME`, `ADK_CONFIG_HOME`, `ADK_DATA_HOME`,
`ADK_MEMORY_HOME`, `SSH_KEYS_HOME`, `MAC_SETUP_HOME`, `ADK_REPO_HOME`.

Other keys: `GIT_PERSONAL_EMAIL`, `GIT_WORK_EMAIL`, `GIT_WORK_GITHUB_ORGS`,
`GIT_WORK_BITBUCKET_ORGS`, `SSH_PERSONAL_KEY`, `SSH_WORK_KEY`, `EDITOR`,
`VISUAL`, `PATH`.

> 🔒 **Never** print or paste secret values. Presence-check only:
> `[ -n "${CREDS_HOME-}" ] && echo set || echo unset`

Reload:
```sh
source ~/.zshenv
```

---

## 4. Homebrew casks (GUI apps)

```sh
# Editors & IDEs
brew install --cask cursor          # primary VS Code-compatible editor
brew install --cask intellij-idea
brew install --cask zed             # default $EDITOR

# AI tools
brew install --cask claude          # Claude desktop
brew install --cask claude-code     # Claude Code (if not using native installer)
brew install --cask cursor-cli

# API clients
brew install --cask bruno

# Container runtime — provides docker / docker-compose / docker-buildx CLIs
brew install --cask orbstack
#   ⚠️ See "Container runtime" note below before choosing.

# Terminal
brew install --cask ghostty         # config in step 12
brew install --cask cmux            # terminal multiplexer (uses Ghostty)

# Browsers
brew install --cask firefox
brew install --cask google-chrome   # default browser

# Communication
brew install --cask slack
brew install --cask zoom

# Utilities
brew install --cask aws-vpn-client
brew install --cask logi-options+
brew install --cask notion
brew install --cask raycast         # launcher (config in step 14)
brew install --cask stats           # menu-bar system monitor

# Fonts
brew install --cask font-jetbrains-mono-nerd-font
```

### All casks at once
```sh
brew install --cask cursor intellij-idea zed claude claude-code cursor-cli \
  bruno orbstack ghostty cmux firefox google-chrome slack zoom aws-vpn-client \
  logi-options+ notion raycast stats font-jetbrains-mono-nerd-font
```

> **Container runtime note:** the repo currently declares **OrbStack**. Some
> machines instead run **colima** (`brew install colima docker docker-compose
> docker-buildx`). Pick one — don't run both. If you keep colima:
> `colima start` and skip the OrbStack cask.

---

## 5. mise runtimes & global npm packages

`mise` reads `~/.config/mise/config.toml`. Symlink the repo's config, then install:

```sh
mkdir -p ~/.config/mise
ln -sf "$REPO/configs/mise/config.toml" ~/.config/mise/config.toml

mise install   # installs every runtime pinned in config.toml
```

Pinned runtimes (from `configs/mise/config.toml`):

| Tool   | Version     |
|--------|-------------|
| bun    | latest      |
| go     | latest      |
| java   | temurin-21  |
| node   | lts         |
| python | 3.12        |
| uv     | latest      |
| yarn   | 1           |

Global npm packages (installed on the mise-managed Node):
```sh
npm install -g diagramkit excalidraw-cli vite-plus
```

---

## 6. Cursor editor extensions

Settings symlink + extensions (CLI installs):

```sh
# Settings
mkdir -p "$HOME/Library/Application Support/Cursor/User"
ln -sf "$REPO/configs/cursor/settings.json" \
  "$HOME/Library/Application Support/Cursor/User/settings.json"

# Extensions
for ext in \
  anthropic.claude-code astro-build.astro-vscode biomejs.biome \
  bradlc.vscode-tailwindcss christian-kohler.path-intellisense eamodio.gitlens \
  humao.rest-client mermaidchart.vscode-mermaid-chart pomdtr.excalidraw-editor \
  redhat.vscode-xml tamasfe.even-better-toml usernamehw.errorlens \
  yoavbls.pretty-ts-errors dbaeumer.vscode-eslint esbenp.prettier-vscode \
  aaron-bond.better-comments editorconfig.editorconfig gruntfuggly.todo-tree \
  inferrinizzard.prettier-sql-vscode jock.svg mechatroner.rainbow-csv \
  mkhl.shfmt oxc.oxc-vscode streetsidesoftware.code-spell-checker \
  timonwong.shellcheck vitest.explorer vscode-icons-team.vscode-icons ; do
  cursor --install-extension "$ext"
done
```

---

## 7. Shell configuration

```sh
# .zshrc
ln -sf "$REPO/configs/shell/.zshrc" ~/.zshrc

# .zprofile — Homebrew init for login shells (created once, not overwritten)
cat > ~/.zprofile <<'EOF'
# Initialize Homebrew (must be in .zprofile for login shells)
eval "$(/opt/homebrew/bin/brew shellenv)"
EOF

# Starship prompt config
mkdir -p ~/.config
ln -sf "$REPO/configs/shell/starship.toml" ~/.config/starship.toml
```

(`~/.zshenv` and `~/.zshenv.local` were set up in step 3.)

Reload your shell:
```sh
exec zsh
```

---

## 8. Git configuration

The repo renders `~/.gitconfig` from a Jinja2 template using your env vars. To do
it manually, configure the equivalents:

```sh
mkdir -p ~/.config/git-configs

# Identity (from your env)
git config --global user.name  "$GIT_USER_NAME"
git config --global user.email "$GIT_PERSONAL_EMAIL"

# Better diffs (you installed delta + difftastic)
git config --global core.pager "delta"
git config --global interactive.diffFilter "delta --color-only"
git config --global delta.navigate true
```

### Per-org configs (conditional includes)
For each `org:folder:email` in `GIT_WORK_GITHUB_ORGS` / `GIT_WORK_BITBUCKET_ORGS`,
create `~/.config/git-configs/<org>.gitconfig` with the org email, and add a
`[includeIf "gitdir:<folder>/"]` block to `~/.gitconfig`. (The Ansible template
generates these automatically — prefer `make setup` if you have many orgs.)

### SSH commit signing
```sh
git config --global gpg.format ssh
git config --global user.signingkey "$HOME/.ssh/${SSH_PERSONAL_KEY}.pub"
git config --global commit.gpgsign true
git config --global gpg.ssh.allowedSignersFile ~/.config/git-configs/allowed_signers

# allowed_signers maps your email → public key
printf '%s %s\n' "$GIT_PERSONAL_EMAIL" "$(cat ~/.ssh/${SSH_PERSONAL_KEY}.pub)" \
  > ~/.config/git-configs/allowed_signers
```

### Global pre-commit hook
```sh
mkdir -p ~/.git-hooks
ln -sf "$REPO/configs/git/hooks/pre-commit" ~/.git-hooks/pre-commit
git config --global core.hooksPath ~/.git-hooks
```

---

## 9. SSH configuration

```sh
mkdir -p ~/.ssh && chmod 700 ~/.ssh

# Symlink synced keys/certs from $SSH_KEYS_HOME (id_*, *.pem, config.local, known_hosts)
for f in "$SSH_KEYS_HOME"/id_* "$SSH_KEYS_HOME"/*.pem \
         "$SSH_KEYS_HOME"/config.local "$SSH_KEYS_HOME"/known_hosts; do
  [ -e "$f" ] && ln -sf "$f" ~/.ssh/"$(basename "$f")"
done

# Render ~/.ssh/config (Ansible uses a template; if doing fully manual, write it
# yourself and Include ~/.ssh/config.local at the top). Then:
chmod 600 ~/.ssh/config
```

### Generate a key (if you don't have one)
```sh
ssh-keygen -t ed25519 -C "$GIT_PERSONAL_EMAIL"
# Add the public key to GitHub: Settings > SSH and GPG keys > New SSH key
```

---

## 10. AWS configuration

```sh
mkdir -p ~/.aws
ln -sf "$REPO/configs/aws/config" ~/.aws/config
# Credentials are obtained via okta-aws-cli / aws sso — never stored in the repo.
```

---

## 11. fzf key bindings

```sh
"$(brew --prefix)/opt/fzf/install" --key-bindings --completion --no-update-rc
```

Creates `~/.fzf.zsh` (sourced by `.zshrc`), enabling `Ctrl-R`, `Ctrl-T`, `Alt-C`.

---

## 12. Application configs (symlinks)

```sh
# GitHub CLI
mkdir -p ~/.config/gh
ln -sf "$REPO/configs/gh/config.yml" ~/.config/gh/config.yml

# Zed
mkdir -p ~/.config/zed
ln -sf "$REPO/configs/zed/settings.json" ~/.config/zed/settings.json

# Ghostty (also used by cmux)
mkdir -p ~/.config/ghostty
ln -sf "$REPO/configs/ghostty/config" ~/.config/ghostty/config

# Claude Code
mkdir -p ~/.claude
ln -sf "$REPO/configs/claude/settings.json" ~/.claude/settings.json

# btop
mkdir -p ~/.config/btop
ln -sf "$REPO/configs/btop/btop.conf" ~/.config/btop/btop.conf
```

### Dev directories
```sh
mkdir -p ~/personal ~/work
```

---

## 13. Raycast script commands

```sh
mkdir -p ~/.config/raycast/script-commands
# Symlink any scripts the repo ships:
for f in "$REPO"/configs/raycast/script-commands/*; do
  [ -e "$f" ] && ln -sf "$f" ~/.config/raycast/script-commands/"$(basename "$f")"
done
```

Then in Raycast: **Extensions → Script Commands → Add Script Directory →**
`~/.config/raycast/script-commands`. Set Raycast's hotkey (recommended `Cmd+Space`,
replacing Spotlight).

---

## 14. macOS system defaults

Run these `defaults write` commands (translated from `roles/macos/vars/main.yml`),
then restart the affected services at the end.

### Screenshots
```sh
mkdir -p ~/screen-captures
defaults write com.apple.screencapture location ~/screen-captures
defaults write com.apple.screencapture type png
defaults write com.apple.screencapture disable-shadow -bool true
```

### Finder
```sh
defaults write com.apple.finder AppleShowAllFiles -bool true
defaults write com.apple.finder FXDefaultSearchScope -string "SCcf"   # search current folder
defaults write com.apple.finder FXEnableExtensionChangeWarning -bool false
```

### Dock
```sh
defaults write com.apple.dock autohide -bool true
defaults write com.apple.dock tilesize -int 36
defaults write com.apple.dock mineffect -string scale
defaults write com.apple.dock show-recents -bool false
defaults write com.apple.dock autohide-delay -float 0
defaults write com.apple.dock mru-spaces -bool false              # don't rearrange Spaces
defaults write com.apple.dock expose-animation-duration -float 0.1
```

### Keyboard
```sh
defaults write NSGlobalDomain KeyRepeat -int 2          # fast repeat
defaults write NSGlobalDomain InitialKeyRepeat -int 15  # short delay
defaults write NSGlobalDomain ApplePressAndHoldEnabled -bool false  # enable key repeat
```

### Trackpad
```sh
defaults write NSGlobalDomain com.apple.trackpad.scaling -float 2.5
```

### Desktop Services (no .DS_Store on network/USB)
```sh
defaults write com.apple.desktopservices DSDontWriteNetworkStores -bool true
defaults write com.apple.desktopservices DSDontWriteUSBStores -bool true
```

### General UI
```sh
defaults write NSGlobalDomain NSNavPanelExpandedStateForSaveMode  -bool true
defaults write NSGlobalDomain NSNavPanelExpandedStateForSaveMode2 -bool true
defaults write NSGlobalDomain PMPrintingExpandedStateForPrint  -bool true
defaults write NSGlobalDomain PMPrintingExpandedStateForPrint2 -bool true
defaults write NSGlobalDomain NSDocumentSaveNewDocumentsToCloud -bool false  # save to disk
defaults write com.apple.LaunchServices LSQuarantine -bool false             # no "are you sure" dialog
```

### Security
```sh
defaults write com.apple.screensaver askForPasswordDelay -int 0  # require password immediately
```

### TextEdit
```sh
defaults write com.apple.TextEdit RichText -int 0                  # plain text
defaults write com.apple.TextEdit PlainTextEncoding -int 4         # UTF-8
defaults write com.apple.TextEdit PlainTextEncodingForWrite -int 4
```

### Activity Monitor
```sh
defaults write com.apple.ActivityMonitor IconType -int 5      # show CPU in Dock icon
defaults write com.apple.ActivityMonitor ShowCategory -int 0
```

### Safari & Chrome
```sh
# Safari prefs are sandboxed — may need to be toggled via Safari > Settings > Advanced
defaults write com.apple.Safari IncludeDevelopMenu -bool true 2>/dev/null || true
defaults write com.google.Chrome AppleEnableSwipeNavigateWithScrolls -bool false
```

### Apply
```sh
killall Dock; killall Finder; killall SystemUIServer
```

### Default applications (require a click)
- **Browser:** Chrome → Settings → Default browser → Make default
- **Terminal:** Ghostty registers as handler on first launch
- **Editor:** set via `$EDITOR`/`$VISUAL` (= `zed`) in `~/.zshenv`

---

## 15. Post-install sign-ins & manual steps

These can't be scripted:

| Item | Action |
|------|--------|
| **Atuin** | `atuin register -u <user> -e <email>` or `atuin login -u <user>` to sync history |
| **Raycast** | Import settings; set hotkey; add script-commands dir (step 13) |
| **Logi Options+** | Configure mouse/keyboard buttons (settings live in Logitech cloud) |
| **Slack / Zoom / Notion** | Sign in |
| **Claude desktop / Claude Code** | Sign in; MCP servers, skills, agents are managed outside this repo |
| **Bruno** | Load API collections per-project (not tracked here) |
| **OrbStack / colima** | Start the runtime; verify `docker ps` works |
| **SSH key → GitHub/GitLab/Bitbucket** | Add the public key in each provider's settings |
| **Browser extensions** | Install manually (or via browser sync) |

### Manually installed apps (no Homebrew cask)
| App | Source |
|-----|--------|
| Perplexity | [perplexity.ai](https://www.perplexity.ai/) or App Store |
| Air.app | Direct download |

### MDM / work-managed (do **not** add to this repo)
Self Service (Jamf), Okta Verify, AWS VPN Client, CrowdStrike Falcon.

---

## 16. Verify

```sh
cd $REPO
make validate   # checks tools, configs, symlinks, env vars, macOS defaults
```

Or spot-check manually:
```sh
which starship zoxide eza bat fd rg lazygit gh mise   # tools on PATH
ls -la ~/.zshrc ~/.gitconfig ~/.config/starship.toml   # symlinks resolve
mise ls                                                # runtimes installed
```
