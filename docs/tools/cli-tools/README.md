---
title: CLI Tools
---

# CLI Tools

All 28 Homebrew formulae managed by the mac-setup repo, organized by category. These are installed automatically when the Ansible playbook runs.

Source: `roles/homebrew/vars/main.yml` under `homebrew_formulae`.

## Shell & Prompt

| Tool | Purpose | Config | Notes |
|------|---------|--------|-------|
| `zsh` | Default shell | `configs/shell/.zshrc` | macOS ships with zsh, but Homebrew keeps it up to date |
| `zsh-autosuggestions` | Fish-like suggestions as you type | -- | Loaded in `.zshrc`; suggests from history |
| `zsh-completions` | Additional completion definitions | -- | Extends built-in completions for common tools |
| `zsh-syntax-highlighting` | Colors valid/invalid commands as you type | -- | Red = not found, green = valid; catches typos before hitting Enter |
| `starship` | Cross-shell prompt | `configs/starship/starship.toml` | TOML config; shows git branch, runtime versions, exit codes, duration |
| `fzf` | Fuzzy finder | -- | Powers `Ctrl-R` history search and `Ctrl-T` file picker in the shell |

## Modern CLI Replacements

| Tool | Replaces | Why this tool | Config |
|------|----------|---------------|--------|
| `bat` | `cat` | Syntax highlighting, line numbers, git integration | `configs/bat/` |
| `eza` | `ls` | Icons, tree view, git status column, color by file type | Aliased as `ls`, `ll`, `la`, `lt` in `.zshrc` |
| `ripgrep` | `grep` | Fastest grep alternative; respects `.gitignore` by default | Aliased as `rg` |
| `tlrc` | `man` | Community-maintained cheat sheets with practical examples | Lightweight Rust client for tldr pages |
| `zoxide` | `cd` | Learns frequently visited directories, fuzzy matching with `z` | Initialized in `.zshrc` |

## Dev Tools

| Tool | Purpose | Config | Notes |
|------|---------|--------|-------|
| `btop` | System/process monitor | `configs/btop/btop.conf` | Full TUI with CPU, memory, network, disk graphs |
| `difftastic` | Structural diffs | -- | AST-aware diffs that understand language syntax, not just text |
| `gh` | GitHub CLI | `configs/gh/config.yml` | YAML config; PR creation, issue management, repo operations |
| `git-delta` | Syntax-highlighted git diffs | Configured in `configs/git/` | Used as the default git pager for `diff`, `log`, and `show` |
| `hurl` | HTTP API testing | -- | Plain-text `.hurl` files; great for CI pipelines and scripted tests |
| `jq` | JSON processor | -- | Pipe JSON through filters, extract fields, transform data |
| `lazygit` | Git TUI | `configs/lazygit/config.yml` | Aliased as `lg` in `.zshrc`; staging, committing, rebasing in a TUI |
| `shellcheck` | Shell script linter | -- | Catches common bash/zsh bugs and pitfalls |
| `yq` | YAML processor | -- | Like jq but for YAML; reads/writes YAML, JSON, XML, CSV, TSV |

## Infra & Automation

| Tool | Purpose | Notes |
|------|---------|-------|
| `ansible` | Configuration management | Runs the mac-setup playbook itself; also useful for work automation |
| `mise` | Runtime version manager | Manages Node, Python, Java, Bun, etc. See [Runtimes](../runtimes/) |

## Container Tools

| Tool | Purpose | Notes |
|------|---------|-------|
| `colima` | Container runtime | Free Docker Desktop alternative; runs a Linux VM with Docker daemon |
| `docker` | Container CLI | Talks to the colima-managed Docker daemon |
| `docker-buildx` | Extended builds | BuildKit-based builder; multi-platform images, cache mounts |
| `docker-compose` | Multi-container apps | Compose v2 plugin; define services in `docker-compose.yml` |

## Cloud & Infra

| Tool | Purpose | Notes |
|------|---------|-------|
| `awscli` | AWS CLI | Configure with `aws configure`; supports profiles and SSO |
| `helm` | Kubernetes package manager | Install, upgrade, and manage Kubernetes charts |
| `kubernetes-cli` | Kubernetes CLI (`kubectl`) | Cluster management, pod inspection, deployments |

## Shell History

| Tool | Purpose | Notes |
|------|---------|-------|
| `atuin` | Shell history manager | Full-text search across sessions, per-directory filtering, sync across machines |

## Tools intentionally not included

These tools were evaluated or previously installed and removed. The reason is listed for each.

| Tool | Reason for exclusion |
|------|---------------------|
| `tree` | Replaced by `eza --tree` (aliased as `lt`) |
| `fd` | `fzf` works well without it for this setup |
| `direnv` | `mise` handles project-level env vars natively |
| `aichat` | Using Claude CLI instead |
| `gemini-cli` | Using Claude CLI instead |
| `go` | Managed by `mise` when needed, not installed globally |
| `uv` | Managed by `mise`, not Homebrew |
| `hyperfine` | Niche -- install per-project if needed |
| `sd` | Niche -- install per-project if needed |
| `tokei` | Niche -- install per-project if needed |
| `k6` | Niche -- install per-project if needed |
| `watchexec` | Niche -- install per-project if needed |
| `zizmor` | Niche -- install per-project if needed |
| `actionlint` | Niche -- install per-project if needed |
| `gitleaks` | Niche -- install per-project if needed |
| `pre-commit` | Niche -- install per-project if needed |
| `buf` | Niche -- install per-project if needed |
| `protobuf` | Niche -- install per-project if needed |
| `cloudflare-wrangler` | Niche -- install per-project if needed |
| `graphviz` | Niche -- install per-project if needed |

To add a new formula, edit `roles/homebrew/vars/main.yml` and add it to the `homebrew_formulae` list, then run `make setup`.
