# Manual Settings & Installations

Things that cannot be automated via Homebrew/Ansible and require manual setup.

## Manually Installed Applications

These apps are NOT available as Homebrew casks and must be installed manually:

| App | Source | Notes |
|-----|--------|-------|
| Perplexity | [perplexity.ai](https://www.perplexity.ai/) | Download from website or App Store |
| Air.app | Unknown | Not available via Homebrew |

## MDM / Work-Managed Applications

These are deployed by your organization's IT/MDM and should NOT be added to mac-setup:

| App | Purpose |
|-----|---------|
| Self Service | Company app catalog (Jamf) |
| Okta Verify | SSO/MFA authentication |
| AWS VPN Client | VPN access |
| Falcon (CrowdStrike) | Endpoint security |

## Default Applications (set by Ansible)

| Type | Application | Set via |
|------|-------------|---------|
| Default browser | Google Chrome | macOS LaunchServices (automated) |
| Default terminal | Ghostty | macOS LaunchServices handler (automated) |
| Default editor | Zed | `EDITOR`/`VISUAL` env vars in `~/.zshenv` |

## Manual Configuration Steps

### Raycast
- Import settings/extensions manually (Raycast > Settings > Advanced > Export/Import)
- Extensions and hotkeys are not automatable via CLI

### Logi Options+
- Configure mouse/keyboard buttons and scroll behavior manually
- Settings are stored in Logitech's cloud sync

### Bitwarden
- Log in and configure browser extensions separately
- Enable biometric unlock in desktop app settings

### Atuin
- Run `atuin login` to sync shell history across machines
- Or run `atuin register` for first-time setup

### Antigravity
- Already configured via `.zshrc` PATH addition
- Login/auth must be done manually: `antigravity auth login`

### Vite+
- Already configured via `.zshrc` env source
- Login/setup must be done manually

### Claude Code
- Settings are managed by this repo (`configs/claude/settings.json`)
- MCP server configs, skills, and agents are managed separately (not by this repo)
- Global `CLAUDE.md` is user-specific and not tracked

### Zoom
- Sign in after installation
- Configure audio/video settings manually

### Bruno
- API collections are per-project and not tracked here

### macOS System Settings (not yet automated)
- Desktop & Dock hot corners
- Accessibility settings
- Login items (which apps start at login)
- Check `roles/macos/` for what IS automated via `osx_defaults`

### SSH Keys
- Generate keys manually: `ssh-keygen -t ed25519 -C "email@example.com"`
- Add to GitHub/GitLab/Bitbucket manually
- Keys are never stored in this repo (only filenames are referenced via env vars)

### Git GPG/SSH Signing
- Configure commit signing keys manually if desired
- Not currently automated in the Ansible roles

### Browser Extensions
- Install browser extensions manually (Bitwarden, uBlock Origin, etc.)
- Browser sync may handle this if signed in

### App Store Apps
- No App Store apps are currently managed by this repo
- If using `mas` CLI, apps can be added to automation later
