#!/usr/bin/env bash
# =============================================================================
# setup.sh — Personal Home Mac Setup & Configuration Manager
#
# Prerequisites (see MANUAL-SETUP.md):
#   1. Xcode Command Line Tools (xcode-select --install)
#   2. Homebrew (/bin/bash -c "$(curl -fsSL https://raw.githubusercontent.com/Homebrew/install/HEAD/install.sh)")
#
# Usage:
#   ./setup.sh                    # Full setup (Brewfile, Junie CLI, dotfiles, mise, macOS defaults)
#   ./setup.sh --link             # Symlink dotfiles into $HOME only
#   ./setup.sh --macos-defaults   # Apply macOS system defaults only
#   ./setup.sh --validate         # Run system validation checks
#   ./setup.sh --dump             # Dump installed brew packages to Brewfile.local
#   ./setup.sh --no-brew          # Skip Homebrew bundle installation
#   ./setup.sh --dry-run          # Preview actions without executing
# =============================================================================

set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
MODE="full"
DRY_RUN=false
NO_BREW=false

# Parse arguments
while [[ $# -gt 0 ]]; do
    case "$1" in
        --link|link)
            MODE="link"
            shift
            ;;
        --macos-defaults|macos-defaults)
            MODE="macos-defaults"
            shift
            ;;
        --validate|--doctor|validate|doctor)
            MODE="validate"
            shift
            ;;
        --dump|dump)
            MODE="dump"
            shift
            ;;
        --no-brew)
            NO_BREW=true
            shift
            ;;
        --dry-run)
            DRY_RUN=true
            shift
            ;;
        -h|--help)
            echo "Usage: ./setup.sh [--link] [--macos-defaults] [--validate] [--dump] [--no-brew] [--dry-run]"
            exit 0
            ;;
        *)
            echo "Unknown argument: $1" >&2
            echo "Run ./setup.sh --help for usage." >&2
            exit 1
            ;;
    esac
done

echo "=============================================="
echo " macOS Personal Setup — Mode: [$MODE]"
echo "=============================================="

# Helper invocation options
DRY_ARG=""
if [[ "$DRY_RUN" = true ]]; then
    DRY_ARG="--dry-run"
fi

# Mode: Validate only
if [[ "$MODE" == "validate" ]]; then
    bash "$SCRIPT_DIR/scripts/validate.sh"
    exit 0
fi

# Mode: Dump only
if [[ "$MODE" == "dump" ]]; then
    echo "Dumping installed Homebrew packages to Brewfile.local..."
    if [[ "$DRY_RUN" = true ]]; then
        echo "[Dry-Run] brew bundle dump --file='$SCRIPT_DIR/Brewfile.local' --force"
    else
        brew bundle dump --file="$SCRIPT_DIR/Brewfile.local" --force
        echo "✓ Exported to $SCRIPT_DIR/Brewfile.local"
    fi
    exit 0
fi

# Mode: Link dotfiles only
if [[ "$MODE" == "link" ]]; then
    bash "$SCRIPT_DIR/scripts/helpers/link-dotfiles.sh" $DRY_ARG
    bash "$SCRIPT_DIR/scripts/helpers/setup-zshenv.sh" $DRY_ARG
    exit 0
fi

# Mode: macOS defaults only
if [[ "$MODE" == "macos-defaults" ]]; then
    bash "$SCRIPT_DIR/scripts/helpers/macos-defaults.sh" $DRY_ARG
    exit 0
fi

# Verify manual prerequisites before running full setup
if ! xcode-select -p &>/dev/null; then
    echo "Error: Xcode Command Line Tools are not installed." >&2
    echo "Run: xcode-select --install (see MANUAL-SETUP.md)" >&2
    exit 1
fi

if [[ "$NO_BREW" = false ]] && ! command -v brew &>/dev/null; then
    echo "Error: Homebrew is not installed or not in PATH." >&2
    echo "See MANUAL-SETUP.md for Homebrew installation instructions." >&2
    exit 1
fi

# Full Setup Mode:
# 1. Install Homebrew Packages
if [[ "$NO_BREW" = false ]]; then
    echo ""
    echo "1. Installing Homebrew Packages..."

    install_bundle() {
        local file="$1"
        if [[ -f "$file" ]]; then
            echo "  Applying $file..."
            if [[ "$DRY_RUN" = true ]]; then
                echo "  [Dry-Run] brew bundle --file='$file'"
            else
                brew bundle --file="$file" || true
            fi
        fi
    }

    install_bundle "$SCRIPT_DIR/Brewfile"

    # Machine-local additions if present
    if [[ -f "$SCRIPT_DIR/Brewfile.local" ]]; then
        echo "  Applying machine-local Brewfile.local..."
        install_bundle "$SCRIPT_DIR/Brewfile.local"
    fi
fi

# 2. Install Junie CLI
echo ""
echo "2. Installing Junie CLI..."
if command -v junie &>/dev/null; then
    echo "  ✓ Junie CLI already installed: $(command -v junie)"
elif [[ "$DRY_RUN" = true ]]; then
    echo "  [Dry-Run] curl -fsSL https://junie.jetbrains.com/install.sh | bash"
else
    curl -fsSL https://junie.jetbrains.com/install.sh | bash
fi

# 3. Link Dotfiles & Configurations
echo ""
echo "3. Linking Dotfiles & App Configurations..."
bash "$SCRIPT_DIR/scripts/helpers/link-dotfiles.sh" $DRY_ARG

# 4. Configure ~/.zshenv
echo ""
echo "4. Configuring Environment..."
bash "$SCRIPT_DIR/scripts/helpers/setup-zshenv.sh" $DRY_ARG

# 5. Install Language Runtimes (mise)
echo ""
echo "5. Installing Language Runtimes (mise)..."
if command -v mise &>/dev/null; then
    if [[ "$DRY_RUN" = true ]]; then
        echo "  [Dry-Run] mise install"
    else
        mise install
    fi
else
    echo "  ⚠ mise not found; skipping runtime installation."
fi

# 6. Apply macOS System Defaults
echo ""
echo "6. Applying macOS System Defaults..."
bash "$SCRIPT_DIR/scripts/helpers/macos-defaults.sh" $DRY_ARG

echo ""
echo "=============================================="
echo " Setup Complete!"
echo " Next steps:"
echo "   1. Restart terminal or run: source ~/.zshrc"
echo "   2. Follow MANUAL-SETUP.md for NordVPN, Warp, JetBrains Toolbox & macOS system commands"
echo "=============================================="
