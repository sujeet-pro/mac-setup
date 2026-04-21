#!/bin/bash
set -euo pipefail

REPO_URL="${MAC_SETUP_REPO_URL:-https://github.com/sujeet-pro/mac-setup.git}"
DEST_DIR="${MAC_SETUP_DEST_DIR:-$HOME/personal/mac-setup}"

RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m'

echo ""
echo "=========================================="
echo "  Mac Setup Remote Bootstrap"
echo "=========================================="
echo "Repo: $REPO_URL"
echo "Dest: $DEST_DIR"
echo ""

# 1. Xcode CLI tools (provides git on macOS)
if ! xcode-select -p &>/dev/null; then
  echo -e "${YELLOW}Installing Xcode Command Line Tools (includes git)...${NC}"
  xcode-select --install
  echo ""
  echo -e "${RED}Please wait for Xcode CLI tools to finish installing, then re-run this script.${NC}"
  exit 1
else
  echo -e "${GREEN}✓ Xcode CLI tools installed${NC}"
fi

# 2. Verify git is available
if ! command -v git &>/dev/null; then
  echo -e "${RED}Error: git is not available after Xcode CLI tools install.${NC}"
  echo "Try restarting your terminal and running this script again."
  exit 1
fi
echo -e "${GREEN}✓ git available${NC}"

# 3. Clone or update repo
mkdir -p "$(dirname "$DEST_DIR")"

if [ -d "$DEST_DIR/.git" ]; then
  echo "Updating existing repo..."
  git -C "$DEST_DIR" pull --ff-only
else
  if [ -e "$DEST_DIR" ]; then
    echo -e "${RED}Error: $DEST_DIR exists but is not a git repo.${NC}"
    echo "Move or remove it, then re-run this script."
    exit 1
  fi
  echo "Cloning repo..."
  git clone "$REPO_URL" "$DEST_DIR"
fi

echo -e "${GREEN}✓ Repo ready at $DEST_DIR${NC}"
echo ""

# 4. Hand off to setup.sh
echo "Running setup..."
exec "$DEST_DIR/setup.sh"
