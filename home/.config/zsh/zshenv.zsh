# ~/.config/zsh/zshenv.zsh - Public environment variables
# Sourced by ~/.zshenv on every Zsh invocation (login, interactive, non-interactive)

# Detect Homebrew prefix
if [ -z "$BREW_PREFIX" ]; then
    if [ -x "/opt/homebrew/bin/brew" ]; then
        export BREW_PREFIX="/opt/homebrew"
    elif [ -x "/usr/local/bin/brew" ]; then
        export BREW_PREFIX="/usr/local"
    fi
fi

# Ensure essential paths are in PATH
typeset -U path PATH
path=(
    "$HOME/.local/bin"
    "$HOME/bin"
    ${BREW_PREFIX:+"$BREW_PREFIX/bin"}
    ${BREW_PREFIX:+"$BREW_PREFIX/sbin"}
    "$HOME/.cargo/bin"
    $path
)
export PATH

# Default editors & tools
export EDITOR="vim"
export VISUAL="zed --wait"
export PAGER="less"
export LESS="-R -F -X"

# Locale
export LANG="en_US.UTF-8"
export LC_ALL="en_US.UTF-8"

# Tool configs
export STARSHIP_CONFIG="$HOME/.config/starship.toml"
export MAC_SETUP_HOME="${MAC_SETUP_HOME:-$HOME/workspace/mac-setup}"
export HOMEBREW_NO_ENV_HINTS=1
export SHELL_SESSIONS_DISABLE=1
