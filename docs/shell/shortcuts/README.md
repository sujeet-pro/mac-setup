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

| Alias   | Expands to          | Description                        |
| ------- | -------------------- | ---------------------------------- |
| `ls`    | `eza`                | Modern `ls` replacement with color |
| `ll`    | `eza -l`             | Long listing                       |
| `la`    | `eza -la`            | Long listing including hidden      |
| `lt`    | `eza --tree`         | Tree view                          |
| `tree`  | `eza --tree`         | Tree view (replaces `tree`)        |
| `cat`   | `bat`                | Syntax-highlighted file viewer     |
| `catp`  | `bat --plain`        | Plain output (no line numbers)     |

## Navigation

| Alias   | Action                                |
| ------- | ------------------------------------- |
| `..`    | `cd ..`                               |
| `...`   | `cd ../..`                            |
| `....`  | `cd ../../..`                         |
| `cd`    | Uses zoxide (`z`) for smart jumping   |

## Git Aliases

| Alias   | Expands to                     | Description                            |
| ------- | ------------------------------ | -------------------------------------- |
| `gs`    | `git status`                   | Status                                 |
| `gp`    | `git push`                     | Push                                   |
| `gpl`   | `git pull`                     | Pull                                   |
| `gc`    | `git commit`                   | Commit                                 |
| `ga`    | `git add`                      | Stage files                            |
| `gd`    | `git diff`                     | Diff unstaged changes                  |
| `gds`   | `git diff --staged`            | Diff staged changes                    |
| `gdc`   | `git diff --cached`            | Diff cached changes                    |
| `glog`  | `git log --oneline --graph`    | Compact log with graph                 |
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
| `kctx`  | `kubectx`                          | Switch cluster context     |
| `kns`   | `kubens`                           | Switch namespace           |
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

| Alias      | Description                                          |
| ---------- | ---------------------------------------------------- |
| `scripts`  | List scripts from `package.json` via jq              |
| `deps`     | List dependencies from `package.json` via jq         |
| `devdeps`  | List devDependencies from `package.json` via jq      |
| `killport` | Kill process on a given port                         |
| `json`     | Pretty-print JSON via jq                             |

## Tool Aliases

| Alias    | Expands to                                  | Description                        |
| -------- | ------------------------------------------- | ---------------------------------- |
| `cc`     | `claude --dangerously-skip-permissions`     | Claude Code (skip permissions)     |
| `cc-dev` | Claude Code in dev mode                     | Claude Code for development        |
| `reload` | `source ~/.zshrc`                           | Reload shell config                |
| `zshrc`  | `$EDITOR ~/.zshrc`                          | Edit shell config                  |
| `grep`   | `grep --color`                              | Grep with color output             |
