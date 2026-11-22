# Manual Setup & System Configuration Guide

This guide covers everything you do **manually** before formatting your Mac and after reinstalling macOS:
0. **Before Formatting** (pre-format backup checklist)
1. Prerequisites (**Xcode Command Line Tools** & **Homebrew**)
2. **macOS system configuration commands** (Mac name/hostname, Firewall, Touch ID for `sudo`, FileVault)
3. Running the automated setup (`./setup.sh`)
4. **Always-on system-level VPN** (**NordVPN** + **NordPass**)
5. **Warp**, **JetBrains Toolbox**, **Junie CLI**, **Zed**, and **Docker Desktop**
6. **Git**, **fresh GitHub SSH key**, and private `~/.zshenv`
7. Productivity utilities (**Rectangle**, **Maccy**, **Logi Options+**)

---

## 0. Before Formatting (Pre-Format Checklist)

No manual app settings exports are required—start clean after formatting and let `./setup.sh` + cloud accounts handle the rest. Just verify these essentials before wiping:

1. **Commit & push Git repositories**:
   - Check `~/workspace/mac-setup` and all other repos in `~/workspace/` for uncommitted changes or unpushed branches.
2. **Verify account access & recovery outside this Mac**:
   - Confirm you have your **NordPass Master Password** and **Recovery Code** saved on your phone or another safe place.
   - Verify 2FA / passkey access for **Apple ID**, **GitHub**, **JetBrains**, and **NordVPN**.
3. **Secrets & local files**:
   - Save any gitignored project `.env` files or API keys into **NordPass Secure Notes**.
   - Check `~/Desktop`, `~/Documents`, `~/Downloads`, `~/Pictures`, and `~/Movies` for personal files not synced to cloud storage.
   - Dump any local Docker databases or volumes you want to keep.
4. **SSH keys**:
   - Do **not** back up `~/.ssh/` — you will generate a fresh Ed25519 SSH key after formatting and replace the old key on GitHub in Step 6.

---

## 1. Prerequisites (Before Running `./setup.sh`)

Open macOS **Terminal** and install the two manual prerequisites one by one:

1. **Xcode Command Line Tools** (wait for the GUI popup installer to finish before continuing):
```sh
xcode-select --install
```

2. **Homebrew**:
```sh
/bin/bash -c "$(curl -fsSL https://raw.githubusercontent.com/Homebrew/install/HEAD/install.sh)"
```

---

## 2. macOS System Configuration Commands

Run these commands once on a fresh Mac to configure system identity, security, and convenience settings (requires your admin password):

### Set Mac Name & Hostname
```sh
sudo scutil --set ComputerName "Sujeet's MacBook"
sudo scutil --set LocalHostName "Sujeets-MacBook"
sudo scutil --set HostName "Sujeets-MacBook"
sudo defaults write /Library/Preferences/SystemConfiguration/com.apple.smb.server NetBIOSName -string "Sujeets-MacBook"
dscacheutil -flushcache
```

### Enable Firewall & Stealth Mode
```sh
# Enable macOS Application Firewall
sudo /usr/libexec/ApplicationFirewall/socketfilterfw --setglobalstate on

# Enable Stealth Mode (don't respond to ICMP ping or unsolicited probes)
sudo /usr/libexec/ApplicationFirewall/socketfilterfw --setstealthmode on

# Verify status
sudo /usr/libexec/ApplicationFirewall/socketfilterfw --getglobalstate --getstealthmode
```

### Enable Touch ID for `sudo`
Persists across macOS updates via `/etc/pam.d/sudo_local`:
```sh
sed 's/^#auth/auth/' /etc/pam.d/sudo_local.template | sudo tee /etc/pam.d/sudo_local > /dev/null
```

### Verify FileVault Disk Encryption
```sh
fdesetup status
# If off, enable in: System Settings → Privacy & Security → FileVault
```

---

## 3. Clone & Run Automated Setup

Clone the repository and run the full automated setup (Brewfile, Junie CLI, dotfile symlinks, `mise` runtimes, and macOS defaults):
```sh
mkdir -p ~/workspace && git clone https://github.com/sujeet-pro/mac-setup.git ~/workspace/mac-setup && cd ~/workspace/mac-setup && ./setup.sh
```

Reload your shell:
```sh
exec zsh
```

Validate the installation:
```sh
~/workspace/mac-setup/setup.sh --validate
```

---

## 4. Always-On System-Level VPN & Password Manager

To ensure privacy and tracker blocking at the **system level** (covering every browser, terminal command, IDE, and background app—not just a single browser):

### NordVPN (Always-On System-Level Setup)
1. Open **NordVPN** and sign in.
2. Open **Settings → General**:
   - Enable **Launch at Login**.
3. Open **Settings → Connection**:
   - **VPN Protocol**: Select **NordLynx** (WireGuard-based — fastest and most reliable for always-on use).
   - **Auto-Connect**: Enable **Always** on all networks (both Wi-Fi and Ethernet).
4. Open **Settings → Kill Switch**:
   - Enable **Internet Kill Switch** (blocks all internet traffic if the VPN tunnel drops, preventing accidental IP/tracker leaks).
5. Open **Threat Protection Pro** (sidebar):
   - Enable **Web Protection**, **Ad & Tracker Blocker**, and **Malware Protection** for OS-wide tracker blocking across all apps.
6. Verify your system-wide tunnel from the terminal:
   ```sh
   curl -s https://ipinfo.io | jq '{ip, city, region, country, org}'
   ```

### NordPass
1. Open **NordPass** and sign in.
2. Enable **System Settings → General → AutoFill & Passwords → NordPass** so passkeys and passwords work system-wide.
3. Install the **NordPass** browser extension in **Brave** and **Google Chrome**.

---

## 5. Terminal, Font & Developer Tools

All terminals and editors are standardized on **`JetBrainsMono Nerd Font`** (installed via `Brewfile`) for consistent icon-heavy rendering.

### Warp Terminal
1. Open **Warp → Settings → Appearance → Text**:
   - **Terminal Font**: `JetBrainsMono Nerd Font`
   - **Font Size**: `14` (or your preference)
2. Open **Warp → Settings → Appearance → Prompt**:
   - Select **Shell prompt (PS1)** / enable **Honor user's custom prompt (PS1)** so your **Starship** prompt and Nerd Font icons render identically in Warp, JetBrains integrated terminals, and macOS Terminal.

### JetBrains Toolbox & IDEs
1. Open **JetBrains Toolbox** and sign in to your JetBrains account.
2. Install your IDEs (e.g., **IntelliJ IDEA**, **WebStorm**, **DataGrip**).
3. In **Toolbox → Settings → Tools**:
   - Enable **Generate shell scripts** and set location to `~/.local/bin` (already in your `PATH`).
4. In any JetBrains IDE:
   - **Settings → Editor → Font**: `JetBrainsMono Nerd Font` (enable ligatures).
   - **Settings → Editor → Color Scheme → Console Font**: `JetBrainsMono Nerd Font`.
   - Enable **Settings Sync** (`Settings → Backup and Sync`) so font, keymaps, and themes sync automatically across all JetBrains IDEs.

### Junie CLI
`setup.sh` installs `junie` automatically. Authenticate once:
```sh
junie
# Choose "Continue with JetBrains account" on the welcome screen (or run /account inside Junie).
```

### Zed (Lightweight Editor)
- Pre-configured via `home/.config/zed/settings.json` with `JetBrainsMono Nerd Font` and dark theme.
- Use `zed ~/.zshenv` or `zed <file>` anytime for fast config edits.

### Docker Desktop
1. Open **Docker Desktop**, accept the license agreement, and sign in if needed.
2. Under **Settings → Resources**, adjust CPU/Memory limits to taste (e.g., 4–6 CPUs, 8 GB RAM) and enable **VirtioFS**.

---

## 6. Git, GitHub, SSH & Private Environment

### Local Git Email & Regenerate SSH Key
Generate a fresh Ed25519 SSH key for the newly formatted Mac, set your local Git email, and add the key to macOS Keychain (replace `your-email@example.com`):
```sh
EMAIL="your-email@example.com"
git config --file ~/.gitconfig.local user.email "$EMAIL"
ssh-keygen -t ed25519 -C "$EMAIL"
eval "$(ssh-agent -s)"
ssh-add --apple-use-keychain ~/.ssh/id_ed25519
```

Authenticate GitHub CLI:
```sh
gh auth login
```

Upload the new SSH key to GitHub and verify the connection:
```sh
gh ssh-key add ~/.ssh/id_ed25519.pub --title "Sujeet's MacBook" && ssh -T git@github.com
```
Then open **GitHub → Settings → SSH and GPG keys** and delete the old key from before the format.

### Private Environment Variables (`~/.zshenv`)
`~/.zshenv` is untracked and automatically sources `~/.config/zsh/zshenv.zsh`. Put personal API keys or private tokens in `~/.zshenv`:
```sh
zed ~/.zshenv
```

---

## 7. Productivity Utilities

- **Rectangle**: Open and grant Accessibility permission for window snapping shortcuts.
- **Maccy**: Open, enable **Launch at login**, and grant Accessibility permission for clipboard history.
- **Logi Options+**: Open, sign in to restore Logitech mouse/keyboard profiles, and grant Input Monitoring / Accessibility permissions.
