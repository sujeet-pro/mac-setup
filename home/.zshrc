########################################
# ~/.zshrc - Modular Shell Configuration
########################################

# 0. Environment & Homebrew
if [ -z "$BREW_PREFIX" ]; then
    if [ -x "/opt/homebrew/bin/brew" ]; then
        export BREW_PREFIX="/opt/homebrew"
    elif [ -x "/usr/local/bin/brew" ]; then
        export BREW_PREFIX="/usr/local"
    fi
fi

# 1. Shell History
HISTFILE="$HOME/.zsh_history"
HISTSIZE=50000
SAVEHIST=50000

setopt EXTENDED_HISTORY          # Write timestamp and duration to history
setopt HIST_EXPIRE_DUPS_FIRST    # Expire duplicate entries first when trimming
setopt HIST_IGNORE_DUPS          # Don't record an entry if it's identical to the previous
setopt HIST_IGNORE_ALL_DUPS      # Delete old duplicate entry when a new duplicate is added
setopt HIST_IGNORE_SPACE         # Don't record commands starting with a leading space
setopt HIST_FIND_NO_DUPS         # Do not display duplicate lines when searching history
setopt HIST_SAVE_NO_DUPS         # Do not write duplicate lines to the history file
setopt HIST_REDUCE_BLANKS        # Remove superfluous blanks from history lines
setopt INC_APPEND_HISTORY        # Write to history file immediately upon command execution
setopt SHARE_HISTORY             # Share history across concurrent zsh sessions

# 2. Key Bindings (Emacs style default with home/end fixes)
bindkey -e
bindkey '^[[H' beginning-of-line
bindkey '^[[F' end-of-line
bindkey '^[[3~' delete-char
bindkey '^[[1;5C' forward-word
bindkey '^[[1;5D' backward-word

# 3. Completions & Functions Path
typeset -U fpath
fpath=(
    "$HOME/.config/zsh/completions"
    "$HOME/.config/zsh/functions"
    ${BREW_PREFIX:+"$BREW_PREFIX/share/zsh/site-functions"}
    ${BREW_PREFIX:+"$BREW_PREFIX/share/zsh-completions"}
    $fpath
)

autoload -Uz compinit
# Cache completions for fast startup
if [ -n "$(find ~/.zcompdump -mtime +1 2>/dev/null)" ]; then
    compinit
else
    compinit -C
fi

# Completion Styling
zstyle ':completion:*' matcher-list 'm:{a-zA-Z}={A-Za-z}' 'r:|[._-]=* r:|=*' 'l:|=* r:|=*'
zstyle ':completion:*' list-colors "${(s.:.)LS_COLORS}"
zstyle ':completion:*' menu select
zstyle ':completion:*:descriptions' format '[%d]'
zstyle ':completion:*:warnings' format 'No matches for: %d'

# 4. Load Custom Functions
if [ -d "$HOME/.config/zsh/functions" ]; then
    for fn in "$HOME/.config/zsh/functions"/*(N-.); do
        autoload -Uz "$fn"
    done
fi

# 5. Aliases & Configurations
[[ -f "$HOME/.config/zsh/aliases.zsh" ]] && source "$HOME/.config/zsh/aliases.zsh"
[[ -f "$HOME/.zshrc.local" ]] && source "$HOME/.zshrc.local"

# 6. Runtime & Version Manager (mise)
if command -v mise &>/dev/null; then
    eval "$(mise activate zsh)"
fi

# 7. Shell History Integration (atuin)
if command -v atuin &>/dev/null; then
    eval "$(atuin init zsh)"
fi

# 8. Interactive Fuzzy Finder (fzf)
if command -v fzf &>/dev/null; then
    if [ -f "$BREW_PREFIX/opt/fzf/shell/completion.zsh" ]; then
        source "$BREW_PREFIX/opt/fzf/shell/completion.zsh"
    fi
    if [ -f "$BREW_PREFIX/opt/fzf/shell/key-bindings.zsh" ]; then
        source "$BREW_PREFIX/opt/fzf/shell/key-bindings.zsh"
    fi
    export FZF_DEFAULT_OPTS='--height 40% --layout=reverse --border --inline-info'
    if command -v fd &>/dev/null; then
        export FZF_DEFAULT_COMMAND='fd --type f --hidden --exclude .git'
        export FZF_CTRL_T_COMMAND="$FZF_DEFAULT_COMMAND"
        export FZF_ALT_C_COMMAND='fd --type d --hidden --exclude .git'
    fi
fi

# 9. Prompt (starship)
if command -v starship &>/dev/null; then
    eval "$(starship init zsh)"
fi

# 10. Zsh Plugins
if [ -f "$BREW_PREFIX/share/zsh-autosuggestions/zsh-autosuggestions.zsh" ]; then
    source "$BREW_PREFIX/share/zsh-autosuggestions/zsh-autosuggestions.zsh"
fi

if [ -f "$BREW_PREFIX/share/zsh-syntax-highlighting/zsh-syntax-highlighting.zsh" ]; then
    source "$BREW_PREFIX/share/zsh-syntax-highlighting/zsh-syntax-highlighting.zsh"
fi

# 11. Directory Jumping (zoxide - MUST be at the end)
if command -v zoxide &>/dev/null; then
    eval "$(zoxide init --cmd=cd zsh)"
fi
