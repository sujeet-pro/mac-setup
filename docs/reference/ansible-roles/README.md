---
title: Ansible Roles
---

# Ansible Roles

The mac-setup repo uses 9 Ansible roles, each responsible for a specific area of system configuration. This page documents what each role does, its tags, and the key files it manages.

## Playbook Flow

The main playbook `setup.yml` runs in this order:

### Pre-tasks

Before any role runs, the playbook:

1. **Checks Homebrew** -- verifies that `brew` is installed and accessible
2. **Gets Homebrew prefix** -- determines the Homebrew installation path (architecture-dependent)
3. **Validates env vars** -- confirms required environment variables are set in `~/.zshenv`

### Role Execution Order

Roles run sequentially in this order:

1. homebrew
2. mise
3. shell
4. git
5. ssh
6. apps
7. aws
8. dev-tools
9. macos

### Post-tasks

After all roles complete, a completion message is displayed confirming success.

---

## 1. homebrew

**Tags:** `homebrew`, `packages`

Updates Homebrew, then installs or removes formulae and casks based on the configured lists.

| Action | Details |
| ------ | ------- |
| Updates Homebrew | Runs `brew update` |
| Installs formulae | From `homebrew_formulae` list |
| Installs casks | From `homebrew_casks` list with `accept_external_apps: true` |
| Removes unlisted | Removes formulae/casks no longer in the lists |

**Key files:**
- `roles/homebrew/vars/main.yml` -- formulae and casks lists
- `roles/homebrew/tasks/main.yml` -- installation tasks

---

## 2. mise

**Tags:** `mise`, `runtimes`

Manages runtime versions (Node.js, Python, Java, etc.) via mise.

| Action | Details |
| ------ | ------- |
| Symlinks config | Links mise configuration to `~/.config/mise/` |
| Trusts config | Runs `mise trust` on the config file |
| Installs runtimes | Installs all configured runtime versions |
| Reshims | Rebuilds shims after installation |
| Global npm packages | Installs npm packages that should be available globally |

**Key files:**
- `configs/mise/` -- mise configuration files
- `roles/mise/tasks/main.yml` -- installation and setup tasks

---

## 3. shell

**Tags:** `shell`, `zsh`

Sets up the complete shell environment.

| Action | Details |
| ------ | ------- |
| Symlinks `.zshrc` | Links from `configs/shell/.zshrc` |
| Creates `.zprofile` | Writes Homebrew initialization (`eval "$(brew shellenv)"`) |
| Symlinks `starship.toml` | Links from `configs/starship/starship.toml` to `~/.config/` |
| Copies `.zshenv.example` | Creates `~/.zshenv` from template if missing |

**Key files:**
- `configs/shell/.zshrc` -- main shell configuration
- `configs/shell/.zshenv.example` -- template for environment variables
- `configs/starship/starship.toml` -- prompt configuration
- `roles/shell/tasks/main.yml` -- symlink and setup tasks

---

## 4. git

**Tags:** `git`

Configures git with personal and work profiles using Jinja2 templates.

| Action | Details |
| ------ | ------- |
| Renders `.gitconfig` | Main git config from template (uses env vars) |
| Renders `.gitconfig-personal` | Personal profile (name, email, SSH key) |
| Renders `.gitconfig-work` | Work profile (name, email, SSH key) |
| Symlinks `.gitignore-work` | Work-specific gitignore rules |

Templates use environment variables (`GIT_USER_NAME`, `GIT_PERSONAL_EMAIL`, `GIT_WORK_EMAIL`, etc.) to populate personal data without committing secrets.

**Key files:**
- `roles/git/templates/` -- Jinja2 templates for git configs
- `roles/git/tasks/main.yml` -- rendering and linking tasks

---

## 5. ssh

**Tags:** `ssh`

Sets up SSH configuration with support for multiple keys.

| Action | Details |
| ------ | ------- |
| Creates `.ssh` directory | Ensures `~/.ssh` exists with correct permissions |
| Renders `ssh_config` | Main SSH config from template |
| Creates `config.local` | Creates a local override file if missing |

**Key files:**
- `roles/ssh/templates/` -- Jinja2 template for SSH config
- `roles/ssh/tasks/main.yml` -- directory and config setup tasks

---

## 6. apps

**Tags:** `apps`

Configures application settings by symlinking config files and installing extensions.

| Action | Details |
| ------ | ------- |
| VS Code config | Symlinks settings and keybindings |
| Zed config | Symlinks settings and keymap |
| GH CLI config | Symlinks GitHub CLI configuration |
| Ghostty config | Symlinks terminal configuration |
| Claude config | Symlinks Claude Code configuration |
| Raycast config | Symlinks Raycast script commands and settings |
| btop config | Symlinks system monitor configuration |
| VS Code extensions | Installs extensions from configured list |

**Key files:**
- `configs/` -- all application config files, organized by app
- `roles/apps/vars/main.yml` -- VS Code extensions list
- `roles/apps/tasks/main.yml` -- symlink and install tasks

---

## 7. aws

**Tags:** `aws`

Configures AWS CLI.

| Action | Details |
| ------ | ------- |
| Symlinks AWS config | Links from `configs/aws/` to `~/.aws/` |

**Key files:**
- `configs/aws/` -- AWS configuration files
- `roles/aws/tasks/main.yml` -- symlink tasks

---

## 8. dev-tools

**Tags:** `dev-tools`

Sets up miscellaneous development tools and directories.

| Action | Details |
| ------ | ------- |
| fzf keybindings | Installs fzf shell keybindings |
| Project directories | Creates `~/personal` and `~/work` directories |
| Colima config | Symlinks Colima (Docker runtime) configuration |

**Key files:**
- `configs/colima/` -- Colima configuration
- `roles/dev-tools/tasks/main.yml` -- setup tasks

---

## 9. macos

**Tags:** `macos`, `defaults`

Applies all macOS system defaults and restarts affected services.

| Action | Details |
| ------ | ------- |
| System defaults | Applies all configured `defaults write` commands |
| Restarts Dock | Applies Dock-related changes |
| Restarts Finder | Applies Finder-related changes |
| Restarts SystemUIServer | Applies UI-related changes |

See the [macOS System Defaults](/mac-setup/reference/macos-defaults) page for the complete list of defaults.

**Key files:**
- `roles/macos/vars/main.yml` -- all defaults values
- `roles/macos/tasks/main.yml` -- defaults and restart tasks
