#!/usr/bin/env bash
# validate.sh — Validates mac-setup environment, tools, and symlinks
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
REPO_ROOT="$(cd "$SCRIPT_DIR/.." && pwd)"

echo "=== mac-setup System Validation ==="
errors=0
warnings=0

check_cmd() {
    local cmd="$1"
    local required="${2:-true}"
    if command -v "$cmd" &>/dev/null; then
        echo "  ✓ $cmd found: $(which "$cmd")"
    else
        if [[ "$required" == "true" ]]; then
            echo "  ✗ $cmd NOT found (required)"
            errors=$((errors + 1))
        else
            echo "  ⚠ $cmd NOT found (optional)"
            warnings=$((warnings + 1))
        fi
    fi
}

check_symlink() {
    local target="$1"
    local label="$2"
    if [[ -L "$target" ]]; then
        local dest
        dest="$(readlink "$target")"
        if [[ -e "$target" ]]; then
            echo "  ✓ $label symlinked -> $dest"
        else
            echo "  ✗ $label broken symlink -> $dest"
            errors=$((errors + 1))
        fi
    elif [[ -e "$target" ]]; then
        echo "  ⚠ $label exists but is not a symlink"
        warnings=$((warnings + 1))
    else
        echo "  ✗ $label is missing"
        errors=$((errors + 1))
    fi
}

echo ""
echo "1. Checking Core Commands..."
check_cmd brew true
check_cmd git true
check_cmd zsh true
check_cmd mise true
check_cmd starship true
check_cmd rg true
check_cmd fd true
check_cmd bat true
check_cmd eza true
check_cmd delta true
check_cmd gh true
check_cmd jq true
check_cmd zoxide true
check_cmd atuin false
check_cmd junie false
check_cmd zed false
check_cmd docker false

echo ""
echo "2. Checking Dotfile Symlinks..."
check_symlink "${HOME}/.zshrc" "~/.zshrc"
check_symlink "${HOME}/.zprofile" "~/.zprofile"
check_symlink "${HOME}/.gitconfig" "~/.gitconfig"
check_symlink "${HOME}/.config/starship.toml" "~/.config/starship.toml"
check_symlink "${HOME}/.config/mise/config.toml" "~/.config/mise/config.toml"
check_symlink "${HOME}/.config/zed/settings.json" "~/.config/zed/settings.json"
check_symlink "${HOME}/.config/zsh/zshenv.zsh" "~/.config/zsh/zshenv.zsh"
check_symlink "${HOME}/.config/zsh/aliases.zsh" "~/.config/zsh/aliases.zsh"

echo ""
echo "3. Checking ~/.zshenv..."
if [[ -f "${HOME}/.zshenv" ]]; then
    if grep -q "zshenv.zsh" "${HOME}/.zshenv"; then
        echo "  ✓ ~/.zshenv correctly loads ~/.config/zsh/zshenv.zsh"
    else
        echo "  ⚠ ~/.zshenv does not source ~/.config/zsh/zshenv.zsh"
        warnings=$((warnings + 1))
    fi
else
    echo "  ✗ ~/.zshenv missing"
    errors=$((errors + 1))
fi

echo ""
echo "=== Validation Summary ==="
echo "Errors:   $errors"
echo "Warnings: $warnings"

if [[ $errors -eq 0 ]]; then
    echo "🎉 System is healthy and well-configured!"
    exit 0
else
    echo "❌ Issues found. Please review the errors above."
    exit 1
fi
