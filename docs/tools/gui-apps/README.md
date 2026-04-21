---
title: GUI Applications
---

# GUI Applications

All Homebrew casks managed by the mac-setup repo. These are installed automatically when the Ansible playbook runs.

Source: `roles/homebrew/vars/main.yml` under `homebrew_casks`.

## Editors & IDEs

| Cask | Application | Notes |
|------|-------------|-------|
| `cursor` | Cursor | AI-native code editor (VS Code fork) |
| `visual-studio-code` | VS Code | Extensions managed in `roles/apps/vars/main.yml` |
| `intellij-idea` | IntelliJ IDEA | JetBrains Java/Kotlin IDE |
| `webstorm` | WebStorm | JetBrains JavaScript/TypeScript IDE |
| `pycharm` | PyCharm | JetBrains Python IDE |
| `datagrip` | DataGrip | JetBrains database IDE |
| `zed` | Zed | GPU-accelerated editor written in Rust |
| `antigravity` | Antigravity | Lightweight code editor |

## AI Tools

| Cask | Application | Notes |
|------|-------------|-------|
| `claude` | Claude | Anthropic desktop app |
| `claude-code` | Claude Code | CLI tool for Claude in the terminal |
| `cursor-cli` | Cursor CLI | Command-line interface for Cursor |

## API Client

| Cask | Application | Notes |
|------|-------------|-------|
| `bruno` | Bruno | Open-source API client; collections are git-synced as plain files |

## Terminal

| Cask | Application | Notes |
|------|-------------|-------|
| `ghostty` | Ghostty | GPU-accelerated terminal; configured via plain text at `configs/ghostty/config` |
| `cmux` | cmux | Ghostty-based terminal multiplexer |

## Browsers

| Cask | Application | Notes |
|------|-------------|-------|
| `firefox` | Firefox | Primary browser |
| `google-chrome` | Google Chrome | Secondary browser |

## Communication

| Cask | Application | Notes |
|------|-------------|-------|
| `slack` | Slack | Team messaging |
| `zoom` | Zoom | Video conferencing |

## Utilities

| Cask | Application | Notes |
|------|-------------|-------|
| `logi-options+` | Logi Options+ | Logitech mouse/keyboard customization |
| `notion` | Notion | Notes and docs |
| `raycast` | Raycast | Spotlight replacement; see [Raycast Scripts](../raycast/) |

## Fonts

| Cask | Application | Notes |
|------|-------------|-------|
| `font-jetbrains-mono-nerd-font` | JetBrainsMono Nerd Font | Patched with icons for terminal and editor use |

## External app detection

The Homebrew role runs with `accept_external_apps: true`. This means apps that were installed outside Homebrew (for example, Chrome downloaded from google.com) are detected and skipped rather than causing an error. Homebrew will not try to re-install or manage them.

## Apps not managed by Homebrew

Some apps should be installed through the Mac App Store instead:

- **WhatsApp** -- App Store provides automatic updates and iCloud integration
- **Bitwarden** -- App Store version has better Safari integration and system-level autofill

To add a new cask, edit `roles/homebrew/vars/main.yml` and add it to the `homebrew_casks` list, then run `make setup`.
