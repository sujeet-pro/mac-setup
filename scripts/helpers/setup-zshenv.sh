#!/usr/bin/env bash
# setup-zshenv.sh — Configures ~/.zshenv to load public environment variables safely
set -euo pipefail

TARGET="${HOME}/.zshenv"
SOURCE_SNIPPET='if [[ -r ~/.config/zsh/zshenv.zsh ]]; then source ~/.config/zsh/zshenv.zsh; fi'
DRY_RUN=false

for arg in "$@"; do
    case "$arg" in
        --dry-run) DRY_RUN=true ;;
    esac
done

echo "Checking ~/.zshenv configuration..."

if [[ ! -f "$TARGET" ]]; then
    echo "  Creating initial ~/.zshenv..."
    if [[ "$DRY_RUN" = true ]]; then
        echo "[Dry-Run] touch '$TARGET' && chmod 600 '$TARGET'"
    else
        touch "$TARGET"
        chmod 600 "$TARGET"
    fi
fi

if grep -q "zshenv.zsh" "$TARGET" 2>/dev/null; then
    echo "  ✓ ~/.zshenv already loads ~/.config/zsh/zshenv.zsh"
else
    echo "  Appending public zshenv loader to ~/.zshenv..."
    if [[ "$DRY_RUN" = true ]]; then
        echo "[Dry-Run] Appending loader snippet to $TARGET"
    else
        cat << 'EOF' >> "$TARGET"

# Load public environment variables from mac-setup
if [[ -r ~/.config/zsh/zshenv.zsh ]]; then
    source ~/.config/zsh/zshenv.zsh
fi
EOF
        echo "  ✓ Successfully updated ~/.zshenv"
    fi
fi
