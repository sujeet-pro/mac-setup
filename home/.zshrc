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

# 1. Shell History & Navigation Ergonomics
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
setopt SHARE_HISTORY             # Share history across concurrent zsh sessions (implies immediate append)

setopt AUTO_CD                   # Type directory name to cd into it
setopt AUTO_PUSHD                # Maintain directory stack automatically
setopt PUSHD_IGNORE_DUPS         # Avoid duplicate entries in directory stack
setopt PUSHD_SILENT              # Don't print directory stack on pushd/popd
setopt INTERACTIVE_COMMENTS      # Allow # comments in interactive commands

# Helper: cache tool init scripts and regenerate automatically when binary upgrades
_zsh_cache_dir="${XDG_CACHE_HOME:-$HOME/.cache}/zsh"
[[ -d "$_zsh_cache_dir" ]] || mkdir -p "$_zsh_cache_dir"
_zsh_cached_eval() {
    local name="$1" bin="$2"
    shift 2
    local bin_path cache_file
    bin_path="$(command -v "$bin" 2>/dev/null)" || return 0
    cache_file="${_zsh_cache_dir}/${name}.zsh"
    if [[ ! -s "$cache_file" || "$bin_path" -nt "$cache_file" ]]; then
        "$@" >| "$cache_file" 2>/dev/null
    fi
    source "$cache_file"
}

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
# Pure-Zsh glob check (zero subshell forks) — rebuild zcompdump at most once per 24h
_zcompdump="${HOME}/.zcompdump"
if [[ ! -f "$_zcompdump" || -n ${_zcompdump}(#qN.mh+24) ]]; then
    compinit -u -d "$_zcompdump"
    { [[ -f "$_zcompdump" && ( ! -f "${_zcompdump}.zwc" || "$_zcompdump" -nt "${_zcompdump}.zwc" ) ]] && zcompile "$_zcompdump" } &!
else
    compinit -C -u -d "$_zcompdump"
fi
unset _zcompdump

# Completion Styling
zstyle ':completion:*' matcher-list 'm:{a-zA-Z}={A-Za-z}' 'r:|[._-]=* r:|=*' 'l:|=* r:|=*'
zstyle ':completion:*' list-colors "${(s.:.)LS_COLORS}"
zstyle ':completion:*' menu select
zstyle ':completion:*' use-cache on
zstyle ':completion:*' cache-path "${_zsh_cache_dir}/zcompcache"
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

# 6. Runtime & Version Manager (mise — run live; its output embeds current PATH)
if command -v mise &>/dev/null; then
    eval "$(mise activate zsh)"
fi

# 7. Shell History Integration (atuin)
_zsh_cached_eval atuin-init atuin atuin init zsh

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

# 9. Prompt (starship — skip under dumb terminals)
if [[ "${TERM:-}" != "dumb" ]]; then
    _zsh_cached_eval starship-init starship starship init zsh
fi

# 10. Zsh Plugins (async autosuggestions + syntax highlighting)
ZSH_AUTOSUGGEST_USE_ASYNC=1
ZSH_AUTOSUGGEST_BUFFER_MAX_SIZE=20
ZSH_AUTOSUGGEST_MANUAL_REBIND=1
if [ -f "$BREW_PREFIX/share/zsh-autosuggestions/zsh-autosuggestions.zsh" ]; then
    source "$BREW_PREFIX/share/zsh-autosuggestions/zsh-autosuggestions.zsh"
fi

if [ -f "$BREW_PREFIX/share/zsh-syntax-highlighting/zsh-syntax-highlighting.zsh" ]; then
    source "$BREW_PREFIX/share/zsh-syntax-highlighting/zsh-syntax-highlighting.zsh"
fi

# 11. Directory Jumping (zoxide - MUST be at the end)
_zsh_cached_eval zoxide-init zoxide zoxide init --cmd=cd zsh
