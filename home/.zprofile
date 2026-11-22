# ~/.zprofile - Login shell configuration
# Evaluated on login shells (terminal session startup)

# Fast zero-fork Homebrew environment setup (avoids spawning `brew shellenv` on every tab)
if [ -x "/opt/homebrew/bin/brew" ]; then
    export HOMEBREW_PREFIX="/opt/homebrew"
    export HOMEBREW_CELLAR="/opt/homebrew/Cellar"
    export HOMEBREW_REPOSITORY="/opt/homebrew"
    export INFOPATH="/opt/homebrew/share/info:${INFOPATH:-}"
elif [ -x "/usr/local/bin/brew" ]; then
    export HOMEBREW_PREFIX="/usr/local"
    export HOMEBREW_CELLAR="/usr/local/Cellar"
    export HOMEBREW_REPOSITORY="/usr/local/Homebrew"
    export INFOPATH="/usr/local/share/info:${INFOPATH:-}"
fi

# Re-prepend user & Homebrew paths after macOS /etc/zprofile (`path_helper`) reorders PATH
typeset -U path PATH
path=(
    "$HOME/.local/bin"
    "$HOME/bin"
    ${HOMEBREW_PREFIX:+"$HOMEBREW_PREFIX/bin"}
    ${HOMEBREW_PREFIX:+"$HOMEBREW_PREFIX/sbin"}
    "$HOME/.cargo/bin"
    $path
)

# Ensure Docker Desktop CLI binaries are available if not already linked
if [ -d "/Applications/Docker.app/Contents/Resources/bin" ]; then
    path+=("/Applications/Docker.app/Contents/Resources/bin")
fi
export PATH
