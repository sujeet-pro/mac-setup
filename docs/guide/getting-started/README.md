---
title: Getting Started
---

# Getting Started

This guide walks you through setting up the mac-setup repo on a new or existing Mac.

## Setup Paths

### Option A: Fresh Mac (Remote Bootstrap)

If you are starting from a brand-new Mac with nothing installed, run this single command in Terminal:

```bash
bash -c "$(curl -fsSL https://raw.githubusercontent.com/sujeet-pro/mac-setup/main/bootstrap-remote.sh)"
```

This script handles everything automatically:

1. Installs Xcode Command Line Tools (needed for `git` and compilers)
2. Installs `git` if not already present
3. Clones the repo to `~/personal/mac-setup`
4. Runs `setup.sh` to complete the full setup

### Option B: Repo Already Cloned

If you already have the repo cloned locally:

```bash
cd ~/personal/mac-setup && ./setup.sh
```

## What setup.sh Does

The setup script runs these steps in order:

1. **Xcode CLI Tools** -- Ensures Xcode Command Line Tools are installed
2. **Homebrew** -- Installs Homebrew if missing, updates it if present
3. **Ansible** -- Installs Ansible via Homebrew and adds the `community.general` collection
4. **~/.zshenv** -- Creates `~/.zshenv` from the `.zshenv.example` template if it does not already exist
5. **Playbook run** -- Executes the Ansible playbook to install packages, symlink configs, and configure the system
6. **Cleanup check** -- Verifies no orphaned packages remain

## First-Time Checklist

After setup completes, do these before anything else:

1. **Edit `~/.zshenv`** -- the file is organized into sections. Fill in the **REQUIRED** section first:
   - `GIT_USER_NAME` -- your full name for git commits
   - `GIT_ORGS` -- CSV of `<github-org>:<folder>:<email>` triples; first entry is the default identity. Example:
     ```bash
     export GIT_ORGS="sujeet-pro:~/personal:sujeet@personal.com,Quince-Engineering:~/work:sujeet@quince.com"
     ```
   - `SSH_KEY` -- filename of the single SSH key used everywhere (defaults to `id_ed25519`)

   API tokens / MCP configs are NOT set in `~/.zshenv`. They live under `~/.config/creds/<svc>/{creds.sh,config.sh}` and are auto-sourced by `~/.config/creds/loader.sh`. After `make setup`, those files are scaffolded with placeholders — fill them in per service as you need them.

2. **Generate SSH keys** if you have not already:
   ```bash
   ssh-keygen -t ed25519 -C "your-email@example.com"
   ```

3. **Restart your terminal** so all env vars and shell config take effect.

4. **Re-run setup** to render templated configs (`.gitconfig`, `.ssh/config`) with your new values:
   ```bash
   make setup
   ```

## Day-to-Day Commands

All common operations are available as `make` targets:

| Command         | What it does                                                    |
| --------------- | --------------------------------------------------------------- |
| `make setup`    | Full setup (same as `./setup.sh`)                               |
| `make update`   | Pull latest changes and re-run the playbook                     |
| `make cleanup`  | Remove packages not listed in config (keeps system tidy)        |
| `make check`    | Dry-run the playbook to see what would change                   |
| `make validate` | Run validation checks to verify everything is correctly linked  |
| `make test`     | Run the Ansible playbook in check mode with verbose output      |

## Re-running Is Safe

Every task in the playbook is **idempotent** -- running it multiple times produces the same result as running it once. If a package is already installed, it is skipped. If a symlink already points to the right place, it is left alone. If a config file has not changed, it is not rewritten.

This means you can run `make setup` or `make update` as often as you like without worrying about breaking anything. It is the recommended way to apply changes after editing any config in the repo.
