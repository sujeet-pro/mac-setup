---
title: Manual Setup
---

# Manual Setup

Some tools and configurations cannot be automated and require manual steps after the playbook runs.

## Apps Requiring Manual Install

These apps are not available via Homebrew and must be installed manually:

| App         | Source                          | Notes                    |
| ----------- | ------------------------------- | ------------------------ |
| Perplexity  | [perplexity.ai](https://perplexity.ai) | AI search assistant |
| Air.app     | Direct download                 | Screen recording tool    |

## MDM / Work Apps

Do **not** add these to the mac-setup repo. They are managed by your organization:

- Self Service
- Okta Verify
- AWS VPN Client
- CrowdStrike Falcon

## Default Applications

| Role     | Application | How to verify          |
| -------- | ----------- | ---------------------- |
| Browser  | Chrome      | System Settings > Default Browser |
| Terminal | Ghostty     | Set via Ghostty preferences       |
| Editor   | Zed         | Set via `$EDITOR` env var         |

## Post-Install Steps

After running the playbook for the first time, complete these manual configurations:

### Raycast

1. Open Raycast and import settings from backup (if available)
2. Add the script commands directory: `~/personal/mac-setup/configs/raycast/script-commands/`
3. Configure keyboard shortcut (recommended: `Cmd+Space` replacing Spotlight)

### Logi Options+

Download and install from [Logitech](https://www.logitech.com/en-us/software/logi-options-plus.html). Configure mouse/keyboard settings to your preference.

### Bitwarden

Install from the App Store or direct download. Log in with your account credentials.

### Atuin

Register or log in to sync shell history across machines:

```bash
atuin register -u <username> -e <email>
# or
atuin login -u <username>
```

### Antigravity

Authenticate with your account:

```bash
antigravity auth login
```

### Vite+

Install and configure as needed for your frontend development workflow.

### Claude Code

MCP server configurations are managed separately from this repo. Configure them via the Claude Code settings UI or `~/.claude/` directory.

### Zoom

Open Zoom and sign in with your account.

### Bruno

API collections are stored per-project and are not managed by this repo. Open Bruno and load collections from your project directories.

## SSH Keys

Generate a new SSH key pair if you do not already have one:

```bash
ssh-keygen -t ed25519 -C "your-email@example.com"
```

Then add the public key to your accounts:

1. **GitHub** -- Settings > SSH and GPG keys > New SSH key

After adding the key, set `SSH_KEY` in `~/.zshenv` to its filename (default: `id_ed25519`) and re-run `make setup` to render the SSH and git configs.

## Browser Extensions

Browser extensions must be installed manually from the Chrome Web Store or your browser's extension marketplace. These are not managed by the mac-setup repo.

## App Store Apps

The following apps are installed from the Mac App Store and are not currently managed by the playbook:

- WhatsApp
- Bitwarden (also available as direct download)

To install, open the App Store and search for each app.
