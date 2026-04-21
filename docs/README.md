---
layout: DocHome
title: Mac Setup
tagline: Automated macOS development environment setup using Ansible
install: bash -c "$(curl -fsSL https://raw.githubusercontent.com/sujeet-pro/mac-setup/main/bootstrap-remote.sh)"
actions:
  - text: Get Started
    link: /guide/getting-started
    theme: brand
  - text: View on GitHub
    link: https://github.com/sujeet-pro/mac-setup
    theme: alt
features:
  - title: One Command Setup
    details: Single command bootstraps a complete macOS dev environment from scratch — Xcode tools, Homebrew, Ansible, packages, configs, and system defaults.
  - title: Fully Idempotent
    details: Safe to re-run anytime. Installed tools are skipped, broken symlinks are fixed, and unmanaged packages are flagged for review.
  - title: Git-Synced Configs
    details: All configs are symlinked from the repo. Edit locally, commit, push — another machine just needs git pull and make update.
  - title: Work & Personal Separation
    details: Directory-based git config with conditional includes. Work repos use work email, personal repos use personal email. Mise files are auto-ignored in work repos.
  - title: Modern CLI Toolchain
    details: Rust-based replacements for common tools — eza, bat, ripgrep, zoxide, starship, fzf, atuin — all pre-configured with sensible defaults.
  - title: Cleanup Detection
    details: Automatically detects packages installed outside the repo and offers to track them or remove them, keeping your system and repo in sync.
---
