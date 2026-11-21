#!/usr/bin/env bash
# link-dotfiles.sh — Safely symlinks all dotfiles from home/ into $HOME
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
REPO_ROOT="$(cd "$SCRIPT_DIR/../.." && pwd)"
HOME_DIR="${REPO_ROOT}/home"
TARGET_DIR="${HOME}"

DRY_RUN=false
FORCE=false

for arg in "$@"; do
    case "$arg" in
        --dry-run) DRY_RUN=true ;;
        --force|-f) FORCE=true ;;
    esac
done

if [[ ! -d "$HOME_DIR" ]]; then
    echo "Error: Directory $HOME_DIR does not exist." >&2
    exit 1
fi

echo "Linking dotfiles from $HOME_DIR to $TARGET_DIR..."

TIMESTAMP="$(date +%Y%m%d%H%M%S)"

# Traverse all files in home/
find "$HOME_DIR" -type f -o -type l | while read -r src_file; do
    rel_path="${src_file#$HOME_DIR/}"
    dest_file="${TARGET_DIR}/${rel_path}"
    dest_dir="$(dirname "$dest_file")"

    # Ensure parent directory exists
    if [[ "$DRY_RUN" = true ]]; then
        echo "[Dry-Run] mkdir -p '$dest_dir'"
    else
        mkdir -p "$dest_dir"
    fi

    # Check if target already points to source
    if [[ -L "$dest_file" ]]; then
        current_target="$(readlink "$dest_file" || true)"
        if [[ "$current_target" == "$src_file" ]]; then
            echo "  ✓ Already linked: $rel_path"
            continue
        fi
        # Remove old symlink
        if [[ "$DRY_RUN" = true ]]; then
            echo "[Dry-Run] rm '$dest_file'"
        else
            rm "$dest_file"
        fi
    elif [[ -e "$dest_file" ]]; then
        # Back up existing file
        backup_file="${dest_file}.bak-${TIMESTAMP}"
        echo "  ⚠ Existing file found: $rel_path -> Backing up to $(basename "$backup_file")"
        if [[ "$DRY_RUN" = true ]]; then
            echo "[Dry-Run] mv '$dest_file' '$backup_file'"
        else
            mv "$dest_file" "$backup_file"
        fi
    fi

    # Create symlink
    if [[ "$DRY_RUN" = true ]]; then
        echo "[Dry-Run] ln -s '$src_file' '$dest_file'"
    else
        ln -s "$src_file" "$dest_file"
        echo "  🔗 Linked: $rel_path"
    fi
done

echo "Dotfiles linking complete."
