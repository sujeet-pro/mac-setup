# ~/.config/zsh/aliases.zsh - Shell Aliases

# Navigation & directory listing (eza)
if command -v eza &>/dev/null; then
  alias ls="eza --group-directories-first --icons=auto"
  alias ll="eza -la --group-directories-first --icons=auto --git --time-style=relative"
  alias l="eza -lah --group-directories-first --icons=auto --git"
  alias la="eza -a --group-directories-first --icons=auto"
  alias lt="eza --tree --level=2 --icons=auto"
  alias ltt="eza --tree --level=3 --icons=auto"
else
  alias ls="ls -G"
  alias ll="ls -lah"
  alias la="ls -a"
fi

# Modern CLI tools
if command -v bat &>/dev/null; then
  alias cat="bat --paging=never"
  alias batp="bat --plain"
fi

if command -v lazygit &>/dev/null; then
  alias lg="lazygit"
fi

if command -v btop &>/dev/null; then
  alias top="btop"
fi

# Directory jumping & shortcuts
alias ..="cd .."
alias ...="cd ../.."
alias ....="cd ../../.."
alias ~="cd ~"

# Git aliases
alias g="git"
alias gs="git status -sb"
alias ga="git add"
alias gaa="git add -A"
alias gc="git commit"
alias gcm="git commit -m"
alias gca="git commit --amend"
alias gco="git checkout"
alias gcb="git checkout -b"
alias gb="git branch"
alias gba="git branch -a"
alias gp="git push"
alias gpf="git push --force-with-lease"
alias gpl="git pull --rebase"
alias gd="git diff"
alias gds="git diff --staged"
alias gl="git log --oneline --graph --decorate -20"
alias gla="git log --oneline --graph --decorate --all"
alias grb="git rebase"
alias grba="git rebase --abort"
alias grbc="git rebase --continue"
alias gst="git stash"
alias gstp="git stash pop"

# macOS & system
alias reload="exec zsh"
alias brewup="brew update && brew upgrade && brew cleanup"
alias myip="curl -s https://ipinfo.io/ip"
alias ports="lsof -iTCP -sTCP:LISTEN -P -n"

# Helpers
alias grep="grep --color=auto"
alias df="df -h"
alias du="du -h -d 1"
