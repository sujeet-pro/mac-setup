---
title: Shell Overview
---

# Shell Overview

The shell environment is built on **zsh** with a curated set of plugins and tools: Homebrew-managed plugins, starship prompt, fzf fuzzy finder, atuin shell history, and zoxide smart navigation.

## Architecture

```
zsh
 ├── Homebrew plugins (autosuggestions, syntax-highlighting, completions)
 ├── Starship prompt
 ├── fzf (fuzzy finder)
 ├── Atuin (searchable shell history)
 └── Zoxide (smart cd)
```

## How .zshrc Is Organized

The `.zshrc` file is split into numbered sections that load in order. Each section has a single responsibility:

| Section | Name                  | What it does                                                        |
| ------- | --------------------- | ------------------------------------------------------------------- |
| 0       | Homebrew setup        | Sources Homebrew shell environment                                  |
| 1       | PATH                  | Adds custom directories to `$PATH`                                  |
| 2       | mise activation       | Activates mise for runtime version management                       |
| 3       | History               | Configures 1M lines, deduplication, shared across sessions          |
| 4       | Completions           | Case-insensitive matching, menu-select UI                           |
| 5       | fzf integration       | Loads fzf keybindings and completion                                |
| 6       | Atuin                 | Initializes atuin for searchable history                            |
| 7       | Zoxide                | Initializes zoxide for smart directory jumping                      |
| 8       | Aliases               | All shell aliases (files, git, docker, kubernetes, etc.)            |
| 9       | Plugins & prompt      | Loads autosuggestions, syntax highlighting, and starship prompt      |

## Key Design Decisions

### Lazy-Loaded Completions

kubectl and helm completions are loaded lazily on first use instead of at shell startup. This saves approximately **200ms** of shell init time. The completions are generated and cached on the first invocation of the respective command.

### Async Autosuggestions

zsh-autosuggestions runs asynchronously so that suggestion lookups do not block typing. This keeps the shell responsive even when history is large.

### Syntax Highlighting Loaded Last

zsh-syntax-highlighting is loaded as the last plugin. This is required for compatibility -- it must wrap all widgets after they have been defined by other plugins.

## Environment Variables

Core environment variables are set in `~/.zshenv` so they are available in all contexts (not just interactive shells):

| Variable  | Value | Purpose                            |
| --------- | ----- | ---------------------------------- |
| `EDITOR`  | `zed` | Default editor for git, etc.       |
| `VISUAL`  | `zed` | Visual editor for interactive use  |

Additional variables like `GIT_USER_NAME`, `GIT_PERSONAL_EMAIL`, and SSH key paths are also set in `.zshenv`. See the [Configuration guide](/mac-setup/guide/configuration) for the full list.
