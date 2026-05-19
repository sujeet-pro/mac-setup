########################################
# ~/.zshrc - Shell configuration
########################################

########################################
# 0. Early environment / Homebrew setup
########################################

# Detect and cache the Homebrew prefix.
# This lets us reference plugin paths (zsh-autosuggestions, syntax-highlighting, etc.)
# without hardcoding /opt/homebrew or /usr/local.
if command -v brew &>/dev/null; then
  export BREW_PREFIX="${BREW_PREFIX:-$(brew --prefix)}"
else
  # Fallback for typical Apple Silicon setup (adjust if needed).
  export BREW_PREFIX="/opt/homebrew"
fi

########################################
# 1. General PATH configuration
########################################

# Prefer user-local bin for personal scripts or tools.
export PATH="$HOME/.local/bin:$PATH"

# Add Homebrew's binary directories to PATH so all brew-installed tools are available.
export PATH="$BREW_PREFIX/bin:$BREW_PREFIX/sbin:$PATH"
export PATH="$PATH:/Users/sujeet/Library/Application Support/Coursier/bin"
########################################
# 2. Language & version managers
########################################

# --- mise --------------------------------------------------------------------
# mise manages runtime/tool versions globally and per project.
if command -v mise &>/dev/null; then
  eval "$(mise activate zsh)"
fi

# Note: direnv is not used — mise handles env vars natively via [env] in .mise.toml

########################################
# 3. Core Zsh behavior & history
########################################

# Use emacs-style keybindings in the shell (the default, but set explicitly).
bindkey -e

# History file location and size.
export HISTFILE="$HOME/.zsh_history"   # Where command history is stored.
export HISTSIZE=1000000                # Number of lines kept in memory.
export SAVEHIST=1000000                # Number of lines saved to HISTFILE.

# History behavior tuning:
setopt APPEND_HISTORY          # Append to the history file instead of overwriting it.
setopt SHARE_HISTORY           # Share history across all open shell sessions.
setopt INC_APPEND_HISTORY      # Write each command to history as soon as it is executed.
setopt HIST_IGNORE_ALL_DUPS    # Remove older duplicates, keep only the latest command.
setopt HIST_IGNORE_SPACE       # Don't save commands starting with a space.
setopt HIST_REDUCE_BLANKS      # Strip superfluous whitespace before saving.
setopt HIST_VERIFY             # After !-style expansion, let you edit before running.
setopt HIST_FIND_NO_DUPS       # Don't display duplicates in history search.

# Prefix-based history search with arrow keys:
# Type the beginning of a command, then use Up/Down to cycle matching history entries.
bindkey '^[[A' history-beginning-search-backward   # Up arrow
bindkey '^[[B' history-beginning-search-forward    # Down arrow

########################################
# 4. Completion system configuration
########################################

# Initialize Zsh completion system (must come before plugins that rely on it).
autoload -Uz compinit
compinit

# Bash compat layer for aws_completer and similar tools
autoload -Uz bashcompinit && bashcompinit

# Completion styling
zstyle ':completion:*' menu select           # Use a menu interface when multiple matches exist.
zstyle ':completion:*' matcher-list 'm:{a-z}={A-Z}' 'r:|=*' 'l:|=*'  # Case-insensitive & fuzzy matches.
zstyle ':completion:*' list-colors "${(s.:.)LS_COLORS}"
zstyle ':completion:*:descriptions' format '[%d]'
zstyle ':completion:*' squeeze-slashes true

setopt COMPLETE_IN_WORD                      # Allow completion in the middle of words.
setopt AUTO_MENU                             # Automatically show completion menu on repeated Tab.
setopt AUTO_LIST                             # List choices when completion is ambiguous.

########################################
# 5. Fuzzy finder (fzf) + fd integration
########################################

# fzf provides powerful fuzzy search for history and files.
if command -v fzf &>/dev/null; then
  # Load fzf Zsh integration (Ctrl+R for history, Ctrl+T for files, Alt+C for dirs).
  source <(fzf --zsh)

  export FZF_DEFAULT_COMMAND='git ls-files --cached --others --exclude-standard 2>/dev/null || find . -type f'
  export FZF_CTRL_T_COMMAND="$FZF_DEFAULT_COMMAND"
  export FZF_DEFAULT_OPTS='--height 40% --reverse --border --ansi'

  # Show syntax-highlighted file previews (requires bat) in Ctrl+T.
  if command -v bat &>/dev/null; then
    export FZF_CTRL_T_OPTS="--preview 'bat --color=always --style=numbers --line-range=:500 {}'"
  fi
fi

########################################
# 6. Atuin (enhanced shell history)
########################################

# Atuin replaces basic Ctrl+R with full-text fuzzy search across all sessions,
# per-directory history filtering, and optional cross-machine sync.
if command -v atuin &>/dev/null; then
  eval "$(atuin init zsh)"
fi

########################################
# 8. Aliases
########################################

# --- File listing (eza) ---
if command -v eza &>/dev/null; then
  alias ls='eza'
  alias ll="eza -lah --icons --git"
  alias la="eza -a --icons"
  alias l="eza -a --icons --git"
  alias tree="eza --tree --level=2 --icons"
  alias lt="eza -lah --icons --sort=modified"
else
  alias ll="ls -lah"
fi

# --- Directory movement ---
alias ..="cd .."
alias ...="cd ../.."
alias ....="cd ../../.."

# --- Git shortcuts ---
alias gs="git status"
alias gp="git push"
alias gpl="git pull"
alias gc="git commit"
alias ga="git add"
alias gd="git diff"
alias gds="git diff --stat"
alias gdc="git diff --cached"
alias glog="git log --oneline --graph --decorate"
alias gcl='git checkout $(git branch | fzf | sed "s/^[* ]*//")'
alias gcr='git checkout $(git branch -r | fzf | sed "s/^[* ]*//" | sed "s/origin\///")'
alias gbd='git branch | fzf -m | xargs git branch -d'
alias lg="lazygit"

# --- Kubernetes shortcuts ---
alias k='kubectl'
alias kg='kubectl get'
alias kga='kubectl get all -A'
alias klo='kubectl logs -f'
alias kctx='kubectl config use-context'
alias kns='kubectl config set-context --current --namespace'
alias kdesc='kubectl describe'
alias kaf='kubectl apply -f'

# --- Docker shortcuts ---
alias dps='docker ps'
alias dpsa='docker ps -a'
alias di='docker images'
alias dex='docker exec -it'
alias dlogs='docker logs -f'

# --- AWS shortcuts ---
alias aws-whoami="aws sts get-caller-identity"

# --- Frontend shortcuts ---
if command -v jq &>/dev/null; then
  alias scripts="jq '.scripts' package.json"
  alias deps="jq '.dependencies' package.json"
  alias devdeps="jq '.devDependencies' package.json"
  alias json="jq '.'"
fi
killport() { lsof -ti "tcp:$1" | xargs kill -9; }

# --- Tools shortcuts ---
if command -v claude &>/dev/null; then
  alias cc="claude --dangerously-skip-permissions --chrome"
fi
if command -v agents &>/dev/null; then
  alias cursor-cli="agents"
fi

# --- Quick file viewing (bat) ---
if command -v bat &>/dev/null; then
  alias cat="bat --paging=never"
  alias catp="bat --plain --paging=never"
fi

# --- Misc ---
alias reload='source ~/.zshrc'
alias zshrc='$EDITOR ~/.zshrc'
alias grep='grep --color=auto'

# --- Lazy-loaded completions ---
# kubectl — lazy load to avoid ~200ms startup cost
function kubectl() {
  if ! type __start_kubectl &>/dev/null; then
    source <(command kubectl completion zsh)
  fi
  command kubectl "$@"
}

# helm completions (lazy)
function helm() {
  if ! type __start_helm &>/dev/null; then
    source <(command helm completion zsh)
  fi
  command helm "$@"
}

# AWS completer
if command -v aws_completer &>/dev/null; then
  complete -C aws_completer aws
fi

########################################
# 9. Visual / UX plugins & prompt
########################################

# --- Autosuggestions ---------------------------------------------------------
# Shows greyed-out suggestions as you type, based on your history and completion.
# Accept suggestion with Right-arrow or End key.
if [ -f "$BREW_PREFIX/share/zsh-autosuggestions/zsh-autosuggestions.zsh" ]; then
  source "$BREW_PREFIX/share/zsh-autosuggestions/zsh-autosuggestions.zsh"
fi

ZSH_AUTOSUGGEST_STRATEGY=(history completion)
ZSH_AUTOSUGGEST_BUFFER_MAX_SIZE=20
ZSH_AUTOSUGGEST_USE_ASYNC=true

# --- Starship prompt ---------------------------------------------------------
# Starship is a fast, git-aware prompt written in Rust.
# It reads configuration from ~/.config/starship.toml.
if command -v starship &>/dev/null; then
  eval "$(starship init zsh)"
fi

# --- Syntax highlighting (should be last) ------------------------------------
# Colors commands, options and paths as you type, helping to catch mistakes early.
# This plugin should be sourced at the end of ~/.zshrc for best compatibility.
if [ -f "$BREW_PREFIX/share/zsh-syntax-highlighting/zsh-syntax-highlighting.zsh" ]; then
  source "$BREW_PREFIX/share/zsh-syntax-highlighting/zsh-syntax-highlighting.zsh"
fi

########################################
# 10. Additional completions
########################################

# bun completions (tab completion only — no env injection)
[ -s "$HOME/.bun/_bun" ] && source "$HOME/.bun/_bun"

########################################
# 11. Smarter directory jumping (zoxide) — MUST be last
########################################

# zoxide is a smarter `cd`: it tracks frequently used paths and lets you jump via:
#   cd <pattern>    -> jumps to the most likely directory matching the pattern.
#   cdi <pattern>   -> interactive fuzzy selection.
# NOTE: zoxide must be initialized at the very end of .zshrc so its chpwd hook
# is not overwritten by other plugins.
if command -v zoxide &>/dev/null; then
  eval "$(zoxide init --cmd=cd zsh)"
fi

########################################
# End of ~/.zshrc
########################################

# >>> Netskope SSL Certificate Trust (v2) >>>
# Deployed by MDM — re-injected on every device sync. Removing it manually
# only sticks until the next MDM check-in. Left in place intentionally.
NETSKOPE_CA="/Library/Application Support/Netskope/Certificates/netskope-ca-bundle.pem"
NETSKOPE_MERGED_CA="/Library/Application Support/Netskope/Certificates/netskope+certifi-ca-bundle.pem"
if [ -f "$NETSKOPE_CA" ]; then
    export NODE_EXTRA_CA_CERTS="$NETSKOPE_CA"
fi
if [ -f "$NETSKOPE_MERGED_CA" ]; then
    export SSL_CERT_FILE="$NETSKOPE_MERGED_CA"
fi
# <<< Netskope SSL Certificate Trust (v2) <<<
