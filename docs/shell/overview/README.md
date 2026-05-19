---
title: Shell Overview
---

# Shell Overview

The shell environment is built on **zsh** with a curated set of plugins and tools: Homebrew-managed plugins, starship prompt, fzf fuzzy finder, atuin shell history, zoxide smart navigation, and lazy completions for `kubectl`/`helm`.

## Architecture

```
zsh
 ├── Homebrew plugins (autosuggestions, syntax-highlighting, completions)
 ├── Starship prompt
 ├── fzf (fuzzy finder, with bat preview)
 ├── Atuin (searchable shell history)
 ├── Zoxide (smart cd, bound as `cd`)
 ├── bat / eza / ripgrep (modern CLI replacements)
 ├── mise (runtime version manager)
 └── bun, vite-plus, Antigravity, Coursier (per-tool env hooks)
```

## How .zshrc Is Organized

The `.zshrc` file is split into numbered sections that load in order. Each section has a single responsibility:

| Section | Name                              | What it does                                                                 |
| ------- | --------------------------------- | ---------------------------------------------------------------------------- |
| 0       | Early environment / Homebrew      | Detects and caches `BREW_PREFIX` (Apple Silicon or Intel)                    |
| 1       | General `PATH`                    | Prepends `~/.local/bin`, Homebrew bins, and Coursier bin                     |
| 2       | Language & version managers       | Activates `mise` (no direnv — mise handles project env via `.mise.toml`)     |
| 3       | Core zsh behavior & history       | 1M-line history, dedup, shared sessions, prefix-based up/down history search |
| 4       | Completion system                 | `compinit` + `bashcompinit`, menu-select, case-insensitive matching          |
| 5       | fzf + fd integration              | `Ctrl+R`/`Ctrl+T` keybindings, `bat` preview, git-aware default command      |
| 6       | Atuin (enhanced shell history)    | Replaces `Ctrl+R` with full-text history search                              |
| 8       | Aliases                           | File listing (eza), git, kubectl, docker, frontend (jq), bat, claude, etc.  |
| 8.1     | Lazy-loaded completions           | `kubectl`/`helm` completions sourced on first call (~200 ms saved at start)  |
| 9       | Visual / UX plugins & prompt      | `zsh-autosuggestions`, `starship`, then `zsh-syntax-highlighting` last       |
| 10      | Additional tools & completions    | Antigravity bin, `bun`, `vite-plus` env                                      |
| 11      | Smarter directory jumping         | Initializes `zoxide` last with `--cmd=cd` so `cd` does smart jumping         |
| MDM     | Netskope SSL trust                | Exports `NODE_EXTRA_CA_CERTS` / `SSL_CERT_FILE` when the bundles exist       |

> Numbering matches the comment headers in `configs/shell/.zshrc`. Section 7 is intentionally absent — `zoxide` was moved to the end (section 11) so its `chpwd` hook is not overwritten by other plugins.

## Key Design Decisions

### Lazy-Loaded Completions

kubectl and helm completions are loaded lazily on first use instead of at shell startup. This saves approximately **200ms** of shell init time. The completions are generated and cached on the first invocation of the respective command.

### Async Autosuggestions

zsh-autosuggestions runs asynchronously so that suggestion lookups do not block typing. This keeps the shell responsive even when history is large.

### Syntax Highlighting Loaded Last

zsh-syntax-highlighting is loaded as the last plugin. This is required for compatibility -- it must wrap all widgets after they have been defined by other plugins.

## Environment Variables

Core environment variables are set in `~/.zshenv` so they are available in all contexts (not just interactive shells):

| Variable                                       | Purpose                                                                          |
| ---------------------------------------------- | -------------------------------------------------------------------------------- |
| `PATH` (prepends `~/.local/share/mise/shims`)  | Makes mise-managed runtimes available to GUI apps and login shells               |
| `GIT_USER_NAME`                                | Used by Ansible templates to render `~/.gitconfig`                               |
| `GIT_ORGS`                                     | CSV `<org>:<folder>:<email>` — drives per-org includeIf in `~/.gitconfig`        |
| `SSH_KEY`                                      | Filename of the single SSH key (default: `id_ed25519`)                           |
| `*_CRED` (per service)                         | Secrets — set in `~/.config/creds/<svc>/creds.sh`, not in `~/.zshenv` directly   |

See `configs/shell/.zshenv.example` and the [Configuration guide](/mac-setup/guide/configuration) for the full list. `~/.zshenv` itself is **never committed**.
