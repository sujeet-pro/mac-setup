# mac-setup

Automated macOS development environment setup using Ansible. Installs CLI tools, GUI apps, language runtimes, editor configs, shell setup, system defaults, and Raycast scripts — all from a single command.

Re-running is always safe. Everything is idempotent: installed tools are skipped, symlinks are verified, and unmanaged packages are flagged.

---

## Setup

### Option A: Fresh Mac (remote bootstrap)

Run this from any terminal — it installs Xcode CLI tools and git if needed, clones the repo, and runs the full setup:

```sh
bash -c "$(curl -fsSL https://raw.githubusercontent.com/sujeet-pro/mac-setup/main/bootstrap-remote.sh)"
```

The repo is cloned to `~/personal/mac-setup`. From there, all future runs use the local copy.

### Option B: Repo already cloned

```sh
cd ~/personal/mac-setup
./setup.sh
```

### What `setup.sh` does

1. Installs **Xcode CLI tools**, **Homebrew**, and **Ansible** (if missing)
2. Creates `~/.zshenv` from a template — asks you to fill in personal values (name, email, SSH keys, API tokens)
3. Runs the **Ansible playbook** — installs packages, symlinks configs, sets system defaults
4. Runs a **cleanup check** — detects installed packages not tracked in the repo and offers to add or remove them

---

## Day-to-day Usage

### Make targets

```sh
make setup       # Full bootstrap from scratch (setup.sh)
make update      # Update Homebrew packages and re-run playbook
make cleanup     # Detect unmanaged packages and offer to add/remove them
make check       # Dry-run: show what Ansible would change without applying
make validate    # Quick validation of tools, configs, symlinks, and env vars
make test        # validate + Ansible syntax check
make test-vm     # Full end-to-end test in a clean macOS VM (slow, first run ~15 GB)
```

### Editing configs

All config files under `configs/` are **symlinked** to their system locations. Editing either side updates both — changes flow directly between the repo and your system.

```
~/.zshrc                    →  configs/shell/.zshrc
~/.config/starship.toml     →  configs/shell/starship.toml
~/.config/mise/config.toml  →  configs/mise/config.toml
~/.config/ghostty/config    →  configs/ghostty/config
~/.config/zed/settings.json →  configs/zed/settings.json
~/.claude/settings.json     →  configs/claude/settings.json
~/.config/gh/config.yml     →  configs/gh/config.yml
~/.config/btop/btop.conf    →  configs/btop/btop.conf
~/.aws/config               →  configs/aws/config
~/.colima/default.yaml      →  configs/colima/default.yaml
~/Library/.../settings.json →  configs/vscode/settings.json
```

Edit a config, commit, push — done. On another machine, `git pull && make update` applies everything.

### Adding packages

- **Homebrew formula**: add to `homebrew_formulae` in `roles/homebrew/vars/main.yml`
- **Homebrew cask**: add to `homebrew_casks` in `roles/homebrew/vars/main.yml`
- **VS Code extension**: add to `vscode_extensions` in `roles/apps/vars/main.yml`

Or just install them normally and run `make cleanup` — it detects the new packages and offers to add them to the config.

### Adding app configs

1. Place config files under `configs/<app-name>/`
2. Add symlink tasks to the appropriate role in `roles/<role>/tasks/main.yml`
3. Add validation checks to `scripts/validate.sh`

---

## What Gets Installed

### CLI Tools (Homebrew)

| Category | Tools |
|---|---|
| Shell & prompt | zsh, zsh-autosuggestions, zsh-completions, zsh-syntax-highlighting, starship, fzf |
| Modern CLI | bat, eza, ripgrep, tlrc, zoxide |
| Dev tools | btop, difftastic, gh, git-delta, hurl, jq, lazygit, shellcheck, yq |
| Infra | ansible, mise |
| Containers | colima, docker, docker-buildx, docker-compose |
| Cloud | awscli, helm, kubernetes-cli |
| Shell history | atuin |

### Language Runtimes (mise)

| Tool | Version |
|---|---|
| node | lts |
| bun | latest |
| java | temurin-17 |
| python | 3.12 |
| uv | latest |
| yarn | 1 |

### GUI Apps (Homebrew Casks)

| Category | Apps |
|---|---|
| Editors & IDEs | Cursor, VS Code, IntelliJ IDEA, WebStorm, PyCharm, DataGrip, Zed, Antigravity |
| AI tools | Claude, Claude Code, Cursor CLI |
| API client | Bruno |
| Terminal | Ghostty, cmux |
| Browsers | Firefox, Google Chrome |
| Communication | Slack, Zoom |
| Utilities | Logi Options+, Notion, Raycast |
| Fonts | JetBrainsMono Nerd Font |

Apps installed outside Homebrew (e.g., Chrome from google.com) are detected and skipped — no duplicates.

### Raycast Script Commands

Developer productivity scripts, git-synced via the repo:

| Script | Action |
|---|---|
| Kill Port | Kill process on a given port |
| Open Ghostty Here | Open terminal in current Finder directory |
| Open in Zed | Open Finder directory in Zed editor |
| Open GitHub Repo | Open current repo in browser |
| Pretty JSON | Format JSON from clipboard |
| Decode Base64 | Decode clipboard contents |
| URL Encode/Decode | Encode or decode clipboard contents |
| Toggle Dark Mode | Switch macOS appearance |
| Toggle Hidden Files | Show/hide dotfiles in Finder |
| Flush DNS | Clear macOS DNS cache |

After setup, add `~/.config/raycast/script-commands` as a Script Command directory in Raycast (Extensions > Script Commands > Add Script Directory).

### macOS System Defaults

| Category | Settings |
|---|---|
| Screenshots | Save to `~/screen-captures`, PNG format, no shadow |
| Finder | Show hidden files, search current folder, no extension-change warning |
| Dock | Autohide, size 36, scale effect, no recent apps, zero delay |
| Keyboard | Fast repeat (2), short initial delay (15), key repeat over accents |
| Trackpad | Tracking speed 2.5 |
| Mission Control | Don't rearrange Spaces by use, fast animation |
| Desktop Services | No `.DS_Store` on network or USB volumes |
| General UI | Expanded save/print panels, save to disk, no quarantine dialog |
| Default apps | Chrome (browser), Ghostty (terminal), Zed (editor via `$EDITOR`) |

---

## How It Works

### Environment variables (`~/.zshenv`)

Personal data (name, email, SSH key names, API tokens) lives in `~/.zshenv`, which is **never committed**. On first run, `setup.sh` copies `configs/shell/.zshenv.example` to `~/.zshenv` and asks you to fill it in.

Ansible templates use these env vars to generate git and SSH configs, so personal data stays out of the repo.

### Templated configs

Some configs contain personal data and are rendered from Jinja2 templates instead of symlinked:

| System file | Template |
|---|---|
| `~/.gitconfig` | `roles/git/templates/gitconfig.j2` |
| `~/.gitconfig-personal` | `roles/git/templates/gitconfig-personal.j2` |
| `~/.gitconfig-work` | `roles/git/templates/gitconfig-work.j2` |
| `~/.ssh/config` | `roles/ssh/templates/ssh_config.j2` |

### Work vs personal repos

Git is configured with conditional includes based on directory:

- `~/work/` repos use work email and `.gitignore-work` (which ignores `.mise.toml` files — since mise is a personal tool, not shared with the team)
- `~/personal/` repos use personal email and include mise files normally

### Cleanup check

After running the playbook, `setup.sh` compares what's installed against what's configured:

- **Homebrew formulae** — `brew leaves` vs `roles/homebrew/vars/main.yml`
- **Homebrew casks** — `brew list --cask` vs `roles/homebrew/vars/main.yml`
- **VS Code extensions** — `code --list-extensions` vs `roles/apps/vars/main.yml`

For each unmanaged package, you can **add it to the repo**, **remove it from the system**, or **skip** it.

---

## Repository Structure

```
mac-setup/
├── configs/                        # App config files (symlinked to system)
│   ├── aws/config
│   ├── btop/btop.conf
│   ├── claude/settings.json
│   ├── colima/default.yaml
│   ├── gh/config.yml
│   ├── ghostty/config
│   ├── git/gitignore-work
│   ├── mise/config.toml
│   ├── raycast/script-commands/    # Raycast scripts (11 scripts)
│   ├── shell/.zshrc, starship.toml, .zshenv.example, SHELL-GUIDE.md
│   ├── vscode/settings.json
│   └── zed/settings.json
├── roles/                          # Ansible roles
│   ├── homebrew/                   # Homebrew formulae + cask installation
│   ├── mise/                       # Runtime/SDK installation via mise
│   ├── shell/                      # .zshrc, .zprofile, starship (symlinks)
│   ├── git/                        # .gitconfig files (templates from env vars)
│   ├── ssh/                        # .ssh/config (template with config.local)
│   ├── apps/                       # VS Code, Zed, GH CLI, Ghostty, Claude, Raycast, btop
│   ├── aws/                        # AWS CLI config
│   ├── dev-tools/                  # fzf keybindings, Colima, project directories
│   └── macos/                      # macOS system defaults + default apps
├── scripts/
│   ├── validate.sh                 # Quick validation script
│   └── tart-test.sh                # Full VM end-to-end test
├── setup.sh                        # Entry point: bootstrap + playbook + cleanup
├── bootstrap-remote.sh             # Remote one-liner (clones repo + runs setup.sh)
├── setup.yml                       # Ansible playbook
├── Makefile                        # Convenience targets
├── settings-manual.md              # Things requiring manual setup
└── ansible.cfg                     # Ansible configuration
```

## Testing

```sh
make validate         # Seconds — checks tools, symlinks, env vars, defaults
make test             # Seconds — validate + Ansible syntax check
make test-vm          # 30+ min — full end-to-end in a clean macOS Sequoia VM
make test-vm-debug    # Same but keeps VM alive for debugging (ssh admin@<IP>)
```

## Manual Setup

Some things can't be automated. See [settings-manual.md](settings-manual.md) for:
- Apps not in Homebrew (Perplexity, App Store apps)
- MDM/work-managed apps
- Raycast extensions and hotkeys
- Atuin login, Antigravity auth
- SSH key generation
- Browser extensions
