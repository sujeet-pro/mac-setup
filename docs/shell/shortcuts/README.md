---
title: Shortcuts & Aliases
---

# Shortcuts & Aliases

A complete reference of keyboard shortcuts and shell aliases configured by the mac-setup repo.

## fzf Shortcuts

| Shortcut          | Action                                          |
| ----------------- | ----------------------------------------------- |
| `Ctrl+R`          | Search shell history (via atuin)                |
| `Ctrl+T`          | Find files with bat preview                     |
| `**` then `<Tab>` | Inline fuzzy completion for paths and arguments |

## Zsh Built-in Shortcuts

| Shortcut       | Action                                    |
| -------------- | ----------------------------------------- |
| `Tab`          | Autocomplete (menu-select with cycling)   |
| `Ctrl+A`       | Move cursor to beginning of line          |
| `Ctrl+E`       | Move cursor to end of line                |
| `Ctrl+W`       | Delete word before cursor                 |
| `Ctrl+U`       | Delete from cursor to beginning of line   |
| `Ctrl+K`       | Delete from cursor to end of line         |
| `Ctrl+L`       | Clear screen                              |
| `Ctrl+D`       | Delete character under cursor (or exit)   |
| `Alt+B`        | Move cursor back one word                 |
| `Alt+F`        | Move cursor forward one word              |
| `Up` / `Down`  | Prefix-based history search               |
| `Right Arrow`  | Accept autosuggestion                     |

## File Aliases

| Alias   | Expands to                                | Description                                |
| ------- | ----------------------------------------- | ------------------------------------------ |
| `ls`    | `eza`                                     | Modern `ls` replacement with color & icons |
| `ll`    | `eza -lah --icons --git`                  | Long listing with hidden files + git info  |
| `la`    | `eza -a --icons`                          | All files with icons                       |
| `l`     | `eza -a --icons --git`                    | All files with icons + git info            |
| `lt`    | `eza -lah --icons --sort=modified`        | Long listing sorted by modification time   |
| `tree`  | `eza --tree --level=2 --icons`            | Tree view (2 levels deep)                  |
| `cat`   | `bat --paging=never`                      | Syntax-highlighted file viewer             |
| `catp`  | `bat --plain --paging=never`              | Plain output (no decorations)              |

## Navigation

| Alias   | Action                                |
| ------- | ------------------------------------- |
| `..`    | `cd ..`                               |
| `...`   | `cd ../..`                            |
| `....`  | `cd ../../..`                         |
| `cd`    | `zoxide` (initialized with `--cmd=cd`); fall back to plain `cd` on no match |
| `cdi`   | Interactive fuzzy directory jump via zoxide |

## Git Aliases

| Alias   | Expands to                     | Description                            |
| ------- | ------------------------------ | -------------------------------------- |
| `gs`    | `git status`                   | Status                                 |
| `gp`    | `git push`                     | Push                                   |
| `gpl`   | `git pull`                     | Pull                                   |
| `gc`    | `git commit`                   | Commit                                 |
| `ga`    | `git add`                      | Stage files                            |
| `gd`    | `git diff`                     | Diff unstaged changes                  |
| `gds`   | `git diff --stat`              | Diff summary (files changed)           |
| `gdc`   | `git diff --cached`            | Diff staged (cached) changes           |
| `glog`  | `git log --oneline --graph --decorate` | Compact log with graph             |
| `gcl`   | fzf branch selector            | Checkout local branch (fuzzy)          |
| `gcr`   | fzf remote branch selector     | Checkout remote branch (fuzzy)         |
| `gbd`   | fzf branch delete              | Delete branch (fuzzy select)           |
| `lg`    | `lazygit`                      | Terminal UI for git                    |
| `git dft` | `difftastic`                 | Structural diff via git config         |

## Kubernetes Aliases

| Alias   | Expands to                         | Description                |
| ------- | ---------------------------------- | -------------------------- |
| `k`     | `kubectl`                          | Short kubectl              |
| `kg`    | `kubectl get`                      | Get resources              |
| `kga`   | `kubectl get all`                  | Get all resources          |
| `klo`   | `kubectl logs`                     | View pod logs              |
| `kctx`  | `kubectl config use-context`              | Switch cluster context     |
| `kns`   | `kubectl config set-context --current --namespace` | Switch namespace |
| `kdesc` | `kubectl describe`                 | Describe a resource        |
| `kaf`   | `kubectl apply -f`                 | Apply from file            |

## Docker Aliases

| Alias   | Expands to                         | Description                |
| ------- | ---------------------------------- | -------------------------- |
| `dps`   | `docker ps`                        | List running containers    |
| `dpsa`  | `docker ps -a`                     | List all containers        |
| `di`    | `docker images`                    | List images                |
| `dex`   | `docker exec -it`                  | Interactive exec into container |
| `dlogs` | `docker logs`                      | View container logs        |

## Frontend Aliases

| Alias        | Description                                                |
| ------------ | ---------------------------------------------------------- |
| `scripts`    | List scripts from `package.json` via jq                    |
| `deps`       | List dependencies from `package.json` via jq               |
| `devdeps`    | List devDependencies from `package.json` via jq            |
| `json`       | Pretty-print JSON via jq                                   |
| `killport N` | Kill the process listening on TCP port `N` (`lsof` + kill) |

## AWS Aliases

| Alias         | Expands to                       | Description                |
| ------------- | -------------------------------- | -------------------------- |
| `aws-whoami`  | `aws sts get-caller-identity`    | Check current AWS identity |

## Tool Aliases

| Alias        | Expands to                                            | Description                                  |
| ------------ | ----------------------------------------------------- | -------------------------------------------- |
| `cc`         | `claude --dangerously-skip-permissions --chrome`      | Quick Claude Code session (only if `claude`) |
| `cursor-cli` | `agents`                                              | Cursor CLI (only if `agents` is on PATH)     |
| `lg`         | `lazygit`                                             | Terminal UI for git                          |
| `reload`     | `source ~/.zshrc`                                     | Reload shell config                          |
| `zshrc`      | `$EDITOR ~/.zshrc`                                    | Edit shell config                            |
| `grep`       | `grep --color=auto`                                   | Grep with color output                       |

## Lazy-Loaded Completions

`kubectl` and `helm` completions are not sourced at startup. They are wrapped
in small functions that source the completion script on first invocation, then
delegate to the real command. This saves roughly **200 ms** of shell startup
time. `aws_completer` is wired up via `complete -C aws_completer aws` when the
binary is present.
