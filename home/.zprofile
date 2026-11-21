# ~/.zprofile - Login shell configuration
# Evaluated on login shells (terminal session startup)

# Ensure Homebrew is in PATH
if [ -x "/opt/homebrew/bin/brew" ]; then
    eval "$(/opt/homebrew/bin/brew shellenv)"
elif [ -x "/usr/local/bin/brew" ]; then
    eval "$(/usr/local/bin/brew shellenv)"
fi
