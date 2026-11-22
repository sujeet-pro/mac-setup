#!/usr/bin/env bash
# macos-defaults.sh — Applies macOS system and UI defaults
set -euo pipefail

DRY_RUN=false

for arg in "$@"; do
    case "$arg" in
        --dry-run) DRY_RUN=true ;;
    esac
done

echo "Applying macOS system defaults..."

run_defaults() {
    if [[ "$DRY_RUN" = true ]]; then
        echo "[Dry-Run] defaults write $*"
    else
        defaults write "$@" 2>/dev/null || echo "  ⚠ Skipped sandboxed/restricted domain '$1' (grant Full Disk Access if needed)"
    fi
}

# --- NSGlobalDomain (Keyboard, Text, UI) ---
# Fast key repeat rate
run_defaults NSGlobalDomain KeyRepeat -int 2
run_defaults NSGlobalDomain InitialKeyRepeat -int 15

# Disable press-and-hold for keys in favor of key repeat
run_defaults NSGlobalDomain ApplePressAndHoldEnabled -bool false

# Disable automatic autocorrection & smart substitutions
run_defaults NSGlobalDomain NSAutomaticCapitalizationEnabled -bool false
run_defaults NSGlobalDomain NSAutomaticDashSubstitutionEnabled -bool false
run_defaults NSGlobalDomain NSAutomaticPeriodSubstitutionEnabled -bool false
run_defaults NSGlobalDomain NSAutomaticQuoteSubstitutionEnabled -bool false
run_defaults NSGlobalDomain NSAutomaticSpellingCorrectionEnabled -bool false

# Expand save and print panels by default
run_defaults NSGlobalDomain NSNavPanelExpandedStateForSaveMode -bool true
run_defaults NSGlobalDomain NSNavPanelExpandedStateForSaveMode2 -bool true
run_defaults NSGlobalDomain PMPrintingExpandedStateForPrint -bool true
run_defaults NSGlobalDomain PMPrintingExpandedStateForPrint2 -bool true

# Instant window resize speed
run_defaults NSGlobalDomain NSWindowResizeTime -float 0.001

# Show all filename extensions
run_defaults NSGlobalDomain AppleShowAllExtensions -bool true

# --- Finder ---
# Show path bar and status bar
run_defaults com.apple.finder ShowPathbar -bool true
run_defaults com.apple.finder ShowStatusBar -bool true

# Default to List view and skip extension-change nags
run_defaults com.apple.finder FXPreferredViewStyle -string "Nlsv"
run_defaults com.apple.finder FXEnableExtensionChangeWarning -bool false

# Keep folders on top when sorting by name
run_defaults com.apple.finder _FXSortFoldersFirst -bool true

# When performing a search, search the current folder by default
run_defaults com.apple.finder FXDefaultSearchScope -string "SCcf"

# Avoid creating .DS_Store files on network or USB volumes
run_defaults com.apple.desktopservices DSDontWriteNetworkStores -bool true
run_defaults com.apple.desktopservices DSDontWriteUSBStores -bool true

# --- Dock ---
# Automatically hide and show the Dock with snappy animations
run_defaults com.apple.dock autohide -bool true
run_defaults com.apple.dock autohide-delay -float 0
run_defaults com.apple.dock autohide-time-modifier -float 0.15
run_defaults com.apple.dock expose-animation-duration -float 0.1
run_defaults com.apple.dock launchanim -bool false
run_defaults com.apple.dock show-recents -bool false
run_defaults com.apple.dock tilesize -int 48

# --- Trackpad & Mouse ---
# Enable tap to click
run_defaults com.apple.driver.AppleBluetoothMultitouch.trackpad Clicking -bool true
run_defaults com.apple.AppleMultitouchTrackpad Clicking -bool true

# --- Screenshots ---
# Save crisp PNG screenshots without drop shadows into ~/screen-captures
if [[ "$DRY_RUN" != true ]]; then
    mkdir -p "${HOME}/screen-captures"
fi
run_defaults com.apple.screencapture location -string "${HOME}/screen-captures"
run_defaults com.apple.screencapture type -string "png"
run_defaults com.apple.screencapture disable-shadow -bool true

# --- TextEdit ---
# Use plain text mode for new documents
run_defaults com.apple.TextEdit RichText -int 0

if [[ "$DRY_RUN" = true ]]; then
    echo "[Dry-Run] killall Finder Dock"
else
    killall Finder Dock 2>/dev/null || true
fi

echo "macOS defaults applied."
echo "Note: Keyboard/trackpad changes may require logging out and back in to take full effect."
