#!/bin/bash

# Mac Setup Validation Script
# Checks that all tools are installed, configs are in place, and env vars are set.

set -u

RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m'

PASS=0
FAIL=0
WARN=0

pass() {
  echo -e "  ${GREEN}✓${NC} $1"
  ((PASS++))
}

fail() {
  echo -e "  ${RED}✗${NC} $1"
  ((FAIL++))
}

warn() {
  echo -e "  ${YELLOW}!${NC} $1"
  ((WARN++))
}

check_command() {
  if command -v "$1" &>/dev/null; then
    pass "$1"
  else
    fail "$1 — not found"
  fi
}

check_file() {
  if [ -e "$1" ]; then
    pass "$2"
  else
    fail "$2 — $1 missing"
  fi
}

check_symlink() {
  if [ -L "$1" ]; then
    pass "$2 (symlink)"
  elif [ -e "$1" ]; then
    warn "$2 — exists but not a symlink"
  else
    fail "$2 — $1 missing"
  fi
}

check_env() {
  local val="${!1:-}"
  if [ -n "$val" ]; then
    pass "$1 is set"
  else
    fail "$1 is not set"
  fi
}

echo ""
echo "=========================================="
echo "  Mac Setup Validation"
echo "=========================================="

# --- Homebrew formulae ---
echo ""
echo "Homebrew CLI tools:"
for cmd in ansible atuin aws bat btop colima delta difft docker eza fzf gh hurl jq kubectl helm lazygit mise rg shellcheck starship tldr yq zoxide; do
  check_command "$cmd"
done

# --- mise runtimes ---
echo ""
echo "mise runtime SDKs:"
check_mise_tool() {
  if mise which "$1" &>/dev/null; then
    pass "mise $1"
  else
    fail "mise $1 — not installed"
  fi
}

for tool in node bun yarn python uv java; do
  check_mise_tool "$tool"
done

# --- npm global packages ---
echo ""
echo "npm global packages:"
for pkg in mmdc excalidraw-cli; do
  if mise exec -- which "$pkg" &>/dev/null; then
    pass "$pkg"
  else
    fail "$pkg — not installed (npm install -g)"
  fi
done

# --- Homebrew casks (check apps exist) ---
echo ""
echo "Homebrew casks (applications):"
for app in "Cursor" "Visual Studio Code" "IntelliJ IDEA" "Zed" "Claude" "cmux" "Ghostty" "Bruno" "zoom.us" "Raycast" "Google Chrome" "Firefox" "Notion" "Slack" "WhatsApp"; do
  if [ -d "/Applications/${app}.app" ]; then
    pass "$app"
  else
    warn "$app — not in /Applications"
  fi
done

# --- Config files ---
echo ""
echo "Config files:"
check_symlink "$HOME/.zshrc" ".zshrc"
check_symlink "$HOME/.config/starship.toml" "starship.toml"
check_symlink "$HOME/.config/mise/config.toml" "mise/config.toml"
check_file "$HOME/.gitconfig" ".gitconfig"
check_file "$HOME/.config/git-configs/personal.gitconfig" "git-configs/personal.gitconfig"
check_file "$HOME/.config/git-configs/work.gitconfig" "git-configs/work.gitconfig"
check_file "$HOME/.ssh/config" ".ssh/config"
check_file "$HOME/.ssh/config.local" ".ssh/config.local"
check_symlink "$HOME/.aws/config" ".aws/config"
check_symlink "$HOME/.config/gh/config.yml" "gh/config.yml"
check_symlink "$HOME/.config/zed/settings.json" "zed/settings.json"
check_symlink "$HOME/.colima/default.yaml" ".colima/default.yaml"
check_symlink "$HOME/.config/ghostty/config" "ghostty/config"
check_symlink "$HOME/.config/btop/btop.conf" "btop/btop.conf"
check_symlink "$HOME/.claude/settings.json" "claude/settings.json"
check_file "$HOME/.config/raycast/script-commands" "raycast/script-commands"
check_file "$HOME/.gitignore-work" ".gitignore-work"

# --- VS Code ---
echo ""
echo "VS Code:"
VSCODE_DIR="$HOME/Library/Application Support/Code/User"
check_symlink "$VSCODE_DIR/settings.json" "VS Code settings.json"

# --- Env vars ---
echo ""
echo "Environment variables:"
check_env GIT_USER_NAME
check_env GIT_ORGS
check_env SSH_KEY

# --- Git config resolution ---
echo ""
echo "Git config resolution:"
RESOLVED_NAME=$(git config --global user.name 2>/dev/null || echo "")
if [ -n "$RESOLVED_NAME" ]; then
  pass "git user.name = $RESOLVED_NAME"
else
  fail "git user.name not set"
fi

# --- Directories ---
echo ""
echo "Directories:"
check_file "$HOME/personal" "~/personal"

# Check each org's mapped folder (from GIT_ORGS).
if [ -n "${GIT_ORGS:-}" ]; then
  IFS=',' read -ra _ORGS <<< "$GIT_ORGS"
  for entry in "${_ORGS[@]}"; do
    IFS=':' read -r _name _folder _email <<< "$entry"
    _folder=$(echo "$_folder" | xargs)
    [ -z "$_folder" ] && continue
    expanded_dir="${_folder/#\~/$HOME}"
    if [ -d "$expanded_dir" ]; then
      pass "$_folder (org: $(echo "$_name" | xargs))"
    else
      warn "$_folder — folder for org '$(echo "$_name" | xargs)' does not exist yet"
    fi
  done
fi

# --- Docker runtime ---
echo ""
echo "Docker runtime:"
DOCKER_CONTEXT=$(docker context show 2>/dev/null || echo "__unknown__")
if [ "$DOCKER_CONTEXT" = "colima" ]; then
  pass "docker context = colima"
else
  warn "docker context is $DOCKER_CONTEXT (expected colima)"
fi

# --- Font check ---
echo ""
echo "Fonts:"
if [ -f "$HOME/Library/Fonts/JetBrainsMonoNerdFont-Regular.ttf" ] || \
   fc-list 2>/dev/null | grep -qi "JetBrainsMono Nerd Font"; then
  pass "JetBrainsMono Nerd Font installed"
else
  warn "JetBrainsMono Nerd Font — not detected"
fi

# --- macOS defaults ---
echo ""
echo "macOS defaults:"

check_default() {
  local domain="$1" key="$2" expected="$3" label="$4"
  local actual
  actual=$(defaults read "$domain" "$key" 2>/dev/null || echo "__unset__")
  if [ "$actual" = "$expected" ]; then
    pass "$label = $expected"
  else
    warn "$label — expected $expected, got $actual"
  fi
}

check_default com.apple.screencapture location "$HOME/screen-captures" "Screenshot location"
check_default com.apple.dock autohide 1 "Dock autohide"
check_default com.apple.dock tilesize 36 "Dock tile size"
check_default com.apple.dock show-recents 0 "Dock show-recents"
check_default com.apple.finder AppleShowAllFiles 1 "Finder show hidden files"
check_default NSGlobalDomain KeyRepeat 2 "KeyRepeat"
check_default NSGlobalDomain InitialKeyRepeat 15 "InitialKeyRepeat"
check_default com.apple.desktopservices DSDontWriteNetworkStores 1 "No .DS_Store on network"
check_default com.apple.desktopservices DSDontWriteUSBStores 1 "No .DS_Store on USB"

# --- Summary ---
echo ""
echo "=========================================="
TOTAL=$((PASS + FAIL + WARN))
echo -e "  ${GREEN}${PASS} passed${NC}  ${RED}${FAIL} failed${NC}  ${YELLOW}${WARN} warnings${NC}  (${TOTAL} total)"
echo "=========================================="

if [ "$FAIL" -gt 0 ]; then
  exit 1
fi
