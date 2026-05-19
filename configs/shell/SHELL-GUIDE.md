# Shell Features & Shortcuts Guide

Quick reference for all productivity tools and keybindings configured in this shell setup.

## Tool Overview

| Tool | Purpose | Config |
|------|---------|--------|
| **zsh** | Shell with completions, history sharing, fuzzy matching | `~/.zshrc` |
| **starship** | Fast, git-aware prompt with language indicators | `~/.config/starship.toml` |
| **fzf** | Fuzzy finder for files, history, and directories | Integrated in `.zshrc` |
| **bat** | Syntax-highlighted `cat` with line numbers | Aliased as `cat` |
| **eza** | Modern `ls` with icons and tree view | Aliased as `ll`, `tree` |
| **zoxide** | Smart `cd` that learns your most-used directories | Replaces `cd` |
| **atuin** | Enhanced shell history with full-text search | Replaces Ctrl+R |
| **delta** | Syntax-highlighted git diffs with side-by-side view | Git pager |
| **difftastic** | Structural/AST-aware diffs (ignores formatting changes) | Git alias `dft` |
| **lazygit** | Terminal UI for git operations | Aliased as `lg` |
| **ripgrep** | Fast code search (modern `grep`) | `rg` command |
| **jq** | JSON processor and pretty-printer | Aliased as `json` |
| **yq** | YAML processor (jq for YAML) | `yq` command |
| **hurl** | Plain-text HTTP test runner for CI | `.hurl` files in repos |
| **mise** | Runtime/tool version manager (node, python, java, etc.) | `~/.config/mise/config.toml` |

## Keyboard Shortcuts

### fzf (Fuzzy Finder)

| Shortcut | Action |
|----------|--------|
| `Ctrl+R` | Fuzzy search command history (enhanced by atuin) |
| `Ctrl+T` | Fuzzy search files in current directory (with bat preview) |
| `**<Tab>` | Inline fuzzy completion (e.g., `cd **<Tab>`, `vim **<Tab>`) |

### Atuin (Shell History)

| Shortcut | Action |
|----------|--------|
| `Ctrl+R` | Open atuin interactive history search |
| `Up/Down` | Prefix-based history search (type partial command first) |

> Atuin features: full-text search, per-directory history filtering, session-aware history, timestamps, duration tracking.

### Zsh Built-in

| Shortcut | Action |
|----------|--------|
| `Tab` | Auto-complete (with menu selection for multiple matches) |
| `Tab Tab` | Show completion menu |
| `Ctrl+A` | Move cursor to beginning of line |
| `Ctrl+E` | Move cursor to end of line |
| `Ctrl+W` | Delete word before cursor |
| `Ctrl+U` | Delete from cursor to beginning of line |
| `Ctrl+K` | Delete from cursor to end of line |
| `Ctrl+L` | Clear screen |
| `Ctrl+D` | Exit shell / delete char under cursor |
| `Alt+B` | Move back one word |
| `Alt+F` | Move forward one word |
| `Right Arrow` | Accept autosuggestion (zsh-autosuggestions) |

## Aliases

### File Operations

| Alias | Command | Description |
|-------|---------|-------------|
| `ll` | `eza -lah --icons --git` | Detailed file listing with icons |
| `la` | `eza -a --icons` | Show all files with icons |
| `lt` | `eza -lah --icons --sort=modified` | List files sorted by modification time |
| `tree` | `eza --tree --level=2 --icons` | Tree view (2 levels deep) |
| `cat` | `bat --paging=never` | Syntax-highlighted file viewing |
| `catp` | `bat --plain --paging=never` | Plain file viewing (no decorations) |

### Navigation

| Alias | Command | Description |
|-------|---------|-------------|
| `cd <pattern>` | `zoxide` | Smart jump to best-matching directory |
| `cdi <pattern>` | `zoxide interactive` | Fuzzy-select from matching directories |
| `..` | `cd ..` | Go up one directory |
| `...` | `cd ../..` | Go up two directories |
| `....` | `cd ../../..` | Go up three directories |

### Git

| Alias | Command | Description |
|-------|---------|-------------|
| `gs` | `git status` | Short status |
| `gp` | `git push` | Push |
| `gpl` | `git pull` | Pull |
| `gc` | `git commit` | Commit |
| `ga` | `git add` | Stage files |
| `gd` | `git diff` | Show unstaged changes |
| `gds` | `git diff --stat` | Diff summary (files changed) |
| `gdc` | `git diff --cached` | Show staged changes |
| `glog` | `git log --oneline --graph --decorate` | Compact log with graph |
| `gcl` | `git checkout $(branch \| fzf)` | Fuzzy-select local branch to checkout |
| `gcr` | `git checkout $(branch -r \| fzf)` | Fuzzy-select remote branch to checkout |
| `gbd` | `git branch \| fzf -m \| xargs git branch -d` | Fuzzy multi-select branches to delete |
| `lg` | `lazygit` | Open lazygit terminal UI |
| `git dft` | `difftastic` | Structural diff (ignores formatting) |

### Kubernetes

| Alias | Command | Description |
|-------|---------|-------------|
| `k` | `kubectl` | Short kubectl |
| `kg` | `kubectl get` | Get resources |
| `kga` | `kubectl get all -A` | Get all resources across namespaces |
| `klo` | `kubectl logs -f` | Follow logs |
| `kctx` | `kubectl config use-context` | Switch context |
| `kns` | `kubectl config set-context --current --namespace` | Switch namespace |
| `kdesc` | `kubectl describe` | Describe a resource |
| `kaf` | `kubectl apply -f` | Apply from file |

> `kubectl` and `helm` are wrapped in lazy-loading functions: their completions
> are only sourced on first invocation, saving ~200 ms of shell startup.

### Docker

| Alias | Command | Description |
|-------|---------|-------------|
| `dps` | `docker ps` | Running containers |
| `dpsa` | `docker ps -a` | All containers |
| `di` | `docker images` | List images |
| `dex` | `docker exec -it` | Exec into container |
| `dlogs` | `docker logs -f` | Follow container logs |

### Frontend Development

| Alias | Command | Description |
|-------|---------|-------------|
| `scripts` | `jq '.scripts' package.json` | View package.json scripts |
| `deps` | `jq '.dependencies' package.json` | View production dependencies |
| `devdeps` | `jq '.devDependencies' package.json` | View dev dependencies |
| `killport <port>` | `lsof -ti:<port> \| xargs kill -9` | Kill process on a specific port |
| `json` | `jq '.'` | Pretty-print JSON (pipe into it) |

### Other

| Alias | Command | Description |
|-------|---------|-------------|
| `cc` | `claude --dangerously-skip-permissions --chrome` | Quick Claude Code session (only if `claude` is installed) |
| `cursor-cli` | `agents` | Cursor CLI (only if `agents` is on PATH) |
| `aws-whoami` | `aws sts get-caller-identity` | Check current AWS identity |
| `reload` | `source ~/.zshrc` | Reload shell config |
| `zshrc` | `$EDITOR ~/.zshrc` | Edit shell config in `$EDITOR` |
| `grep` | `grep --color=auto` | Grep with color output |

## Git Integration (delta + difftastic)

All `git diff`, `git log -p`, and `git show` output is automatically rendered with delta:
- Syntax highlighting
- Side-by-side view
- Line numbers
- Hyperlinks to files

For structural diffs that ignore formatting, use `git dft`:
```sh
git dft           # diff working tree
git dft --staged  # diff staged changes
```

Navigate delta output:
| Key | Action |
|-----|--------|
| `n` | Jump to next file |
| `N` | Jump to previous file |
| `q` | Quit |

## lazygit Shortcuts

Open with `lg`. Key panels:

| Key | Panel |
|-----|-------|
| `1` | Status |
| `2` | Files |
| `3` | Branches |
| `4` | Commits |
| `5` | Stash |
| `Space` | Stage/unstage file |
| `c` | Commit |
| `p` | Pull |
| `P` | Push |
| `r` | Rebase |
| `s` | Stash |
| `?` | Show all keybindings |

## Prompt Indicators (Starship)

The prompt shows context-aware information:

```
~/work/project  main ●✚…⇡
❯
```

| Indicator | Meaning |
|-----------|---------|
| `●` | Staged changes |
| `✚` | Modified files |
| `…` | Untracked files |
| `✖` | Deleted files |
| `»` | Renamed files |
| `≠` | Merge conflicts |
| `⇡` | Ahead of remote |
| `⇣` | Behind remote |
| `⇕` | Diverged from remote |
| `⚑` | Stashed changes |

Language versions (Node, Bun, Python, Java) appear automatically when relevant project files are detected.

## Productivity Tips

1. **Find any file fast**: `Ctrl+T` → type partial name → Enter
2. **Jump to any project**: `cd proj` → zoxide takes you to `~/work/project`
3. **Recall complex commands**: `Ctrl+R` → type keywords from anywhere in the command
4. **Review git changes**: `lg` → navigate visually, stage hunks, commit, push
5. **Check API responses**: `curl -s api/endpoint | json`
6. **Kill stuck dev server**: `killport 3000`
7. **Browse project scripts**: `scripts` in any npm project
8. **Search code fast**: `rg "TODO" --type ts` or `rg "function.*fetch" -g "*.tsx"`
9. **Structural diff**: `git dft` to see meaningful changes, ignoring whitespace/formatting
10. **Test APIs in CI**: Create `.hurl` files with request/response assertions

## Corporate / Machine-specific Integrations

The end of `.zshrc` includes a few hooks that activate only when the matching
files or binaries are present, so the same config works on personal and
work laptops:

- **Netskope SSL trust** — when `/Library/Application Support/Netskope/Certificates/netskope+certifi-ca-bundle.pem` exists, it is exported as `SSL_CERT_FILE` and the plain Netskope CA as `NODE_EXTRA_CA_CERTS`. Managed by MDM, do not edit.
- **Bun** — `~/.bun/_bun` completions are sourced if present.
- **Vite+** — `~/.vite-plus/env` is sourced if present.
- **Antigravity** — `~/.antigravity/antigravity/bin` is added to `PATH`.
- **Coursier** — `~/Library/Application Support/Coursier/bin` is added to `PATH` for Scala tooling.
