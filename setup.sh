#!/bin/bash
set -e

SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
CLEANUP_ONLY=false

# Parse flags
for arg in "$@"; do
  case "$arg" in
    --cleanup) CLEANUP_ONLY=true ;;
    --help|-h)
      echo "Usage: ./setup.sh [--cleanup]"
      echo ""
      echo "  (no args)   Full setup: bootstrap + install + configure + cleanup check"
      echo "  --cleanup   Only run the cleanup check (detect unmanaged packages)"
      exit 0
      ;;
  esac
done

# Colors
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
BOLD='\033[1m'
NC='\033[0m'

# ──────────────────────────────────────────────
# Helpers
# ──────────────────────────────────────────────

# Extract YAML list items from a vars file between a start marker and the next
# top-level key. Usage: parse_yaml_list <file> <list_name>
parse_yaml_list() {
  local file="$1" key="$2"
  awk -v key="${key}:" '
    $0 ~ "^"key { found=1; next }
    found && /^[a-zA-Z_]/ { exit }
    found && /^  - / { sub(/^  - /, ""); sub(/[[:space:]]*#.*$/, ""); if ($0 != "") print }
  ' "$file"
}

# Append an item to a YAML list in a vars file.
# Usage: add_to_yaml_list <file> <list_name> <item>
add_to_yaml_list() {
  local file="$1" key="$2" item="$3"
  awk -v key="${key}:" -v item="  - ${item}" '
    $0 ~ "^"key { found=1; print; next }
    found && /^[a-zA-Z_]/ { print item; found=0 }
    found && /^$/ { print item; found=0 }
    { print }
    END { if (found) print item }
  ' "$file" > "${file}.tmp" && mv "${file}.tmp" "$file"
}

if [ "$CLEANUP_ONLY" = false ]; then

# ──────────────────────────────────────────────
# Bootstrap
# ──────────────────────────────────────────────

echo ""
echo "=========================================="
echo "  Mac Setup"
echo "=========================================="
echo ""

# 1. Xcode CLI tools
if ! xcode-select -p &>/dev/null; then
  echo -e "${YELLOW}Installing Xcode Command Line Tools...${NC}"
  xcode-select --install
  echo "Please wait for Xcode CLI tools to finish installing, then re-run this script."
  exit 1
else
  echo -e "${GREEN}✓ Xcode CLI tools installed${NC}"
fi

# 2. Homebrew
if ! command -v brew &>/dev/null; then
  echo -e "${YELLOW}Installing Homebrew...${NC}"
  /bin/bash -c "$(curl -fsSL https://raw.githubusercontent.com/Homebrew/install/HEAD/install.sh)"
  eval "$(/opt/homebrew/bin/brew shellenv)"
else
  echo -e "${GREEN}✓ Homebrew installed${NC}"
fi

# 3. Ansible
if ! command -v ansible-playbook &>/dev/null; then
  echo -e "${YELLOW}Installing Ansible...${NC}"
  brew install ansible
else
  echo -e "${GREEN}✓ Ansible installed${NC}"
fi

# 3b. Ansible community.general collection (provides homebrew, osx_defaults modules)
if ! ansible-galaxy collection list 2>/dev/null | grep -q community.general; then
  echo -e "${YELLOW}Installing Ansible community.general collection...${NC}"
  ansible-galaxy collection install community.general
else
  echo -e "${GREEN}✓ Ansible community.general collection installed${NC}"
fi

# 4. ~/.zshenv
if [ ! -f "$HOME/.zshenv" ]; then
  echo -e "${YELLOW}Creating ~/.zshenv from example template...${NC}"
  cp "$SCRIPT_DIR/configs/shell/.zshenv.example" "$HOME/.zshenv"
  echo ""
  echo -e "${RED}ACTION REQUIRED:${NC}"
  echo "  Edit ~/.zshenv and fill in your personal values (name, email, SSH keys, etc.)"
  echo "  Then re-run this script."
  echo ""
  echo "  vim ~/.zshenv"
  exit 1
else
  echo -e "${GREEN}✓ ~/.zshenv exists${NC}"
fi

# 5. Source .zshenv
echo "Sourcing ~/.zshenv..."
source "$HOME/.zshenv"

# Verify required vars
MISSING_VARS=()
for var in GIT_USER_NAME GIT_PERSONAL_EMAIL GIT_WORK_EMAIL SSH_PERSONAL_KEY SSH_WORK_KEY; do
  if [ -z "${!var:-}" ]; then
    MISSING_VARS+=("$var")
  fi
done

if [ ${#MISSING_VARS[@]} -gt 0 ]; then
  echo -e "${RED}Error: The following required variables are not set in ~/.zshenv:${NC}"
  for var in "${MISSING_VARS[@]}"; do
    echo -e "  ${RED}-${NC} $var"
  done
  echo ""
  echo "Please edit ~/.zshenv and fill in your values, then re-run this script."
  echo "  vim ~/.zshenv"
  exit 1
fi

echo -e "${GREEN}✓ Environment variables loaded${NC}"
echo ""

# ──────────────────────────────────────────────
# Run Ansible playbook (install + configure)
# ──────────────────────────────────────────────

echo "Running Ansible playbook..."
echo ""
cd "$SCRIPT_DIR"
ansible-playbook setup.yml --ask-become-pass

fi # end CLEANUP_ONLY check

# ──────────────────────────────────────────────
# Cleanup: detect unmanaged packages
# ──────────────────────────────────────────────

echo ""
echo "=========================================="
echo "  Cleanup Check"
echo "=========================================="
echo ""

HOMEBREW_VARS="$SCRIPT_DIR/roles/homebrew/vars/main.yml"
APPS_VARS="$SCRIPT_DIR/roles/apps/vars/main.yml"
UNMANAGED_FOUND=false

# Generic review function for unmanaged items.
# Usage: review_unmanaged <label> <yaml_file> <yaml_key> <uninstall_cmd> <items...>
#   label:         Display name (e.g. "Homebrew formulae")
#   yaml_file:     Path to the vars YAML file
#   yaml_key:      YAML list key to add to (e.g. "homebrew_formulae")
#   uninstall_cmd: Command prefix to remove an item (e.g. "brew uninstall")
#   items:         Newline-separated list of unmanaged items
review_unmanaged() {
  local label="$1" yaml_file="$2" yaml_key="$3" uninstall_cmd="$4" items="$5"

  local count
  count=$(echo "$items" | wc -l | tr -d ' ')
  echo -e "${YELLOW}Found $count $label not tracked by mac-setup:${NC}"
  echo "$items" | while read -r item; do
    echo -e "  ${BLUE}-${NC} $item"
  done
  echo ""
  echo -e "${BOLD}What would you like to do?${NC}"
  echo "  [a] Add all to mac-setup config ($yaml_key)"
  echo "  [r] Remove all from system"
  echo "  [i] Review individually"
  echo "  [s] Skip"
  read -r -p "> " choice </dev/tty
  case "$choice" in
    a|A)
      while IFS= read -r item; do
        add_to_yaml_list "$yaml_file" "$yaml_key" "$item"
      done <<< "$items"
      echo -e "${GREEN}Added to $yaml_file — commit when ready.${NC}"
      ;;
    r|R)
      while IFS= read -r item; do
        echo -e "  Removing ${RED}$item${NC}..."
        $uninstall_cmd "$item" 2>/dev/null || true
      done <<< "$items"
      ;;
    i|I)
      while IFS= read -r item; do
        echo ""
        echo -e "  ${BLUE}$item${NC}"
        echo "    [a] Add to mac-setup  [r] Remove  [s] Skip"
        read -r -p "    > " action </dev/tty
        case "$action" in
          a|A)
            add_to_yaml_list "$yaml_file" "$yaml_key" "$item"
            echo -e "    ${GREEN}Added to config${NC}"
            ;;
          r|R)
            $uninstall_cmd "$item" 2>/dev/null || true
            echo -e "    ${RED}Removed${NC}"
            ;;
          *) echo "    Skipped" ;;
        esac
      done <<< "$items"
      ;;
    *) echo "Skipped." ;;
  esac
  echo ""
}

# --- Homebrew formulae ---
# Use `brew leaves` to get only explicitly installed formulae (not deps).
# Also exclude packages already in the "absent" lists (Ansible handles those).
CONFIGURED_FORMULAE=$(parse_yaml_list "$HOMEBREW_VARS" "homebrew_formulae" | sort)
ABSENT_FORMULAE=$(parse_yaml_list "$HOMEBREW_VARS" "homebrew_formulae_absent" | sort)
KNOWN_FORMULAE=$(printf '%s\n%s' "$CONFIGURED_FORMULAE" "$ABSENT_FORMULAE" | sort -u)
INSTALLED_FORMULAE=$(brew leaves 2>/dev/null | sort)

UNMANAGED_FORMULAE=$(comm -23 <(echo "$INSTALLED_FORMULAE") <(echo "$KNOWN_FORMULAE"))

if [ -n "$UNMANAGED_FORMULAE" ]; then
  UNMANAGED_FOUND=true
  review_unmanaged "Homebrew formulae" "$HOMEBREW_VARS" "homebrew_formulae" "brew uninstall" "$UNMANAGED_FORMULAE"
fi

# --- Homebrew casks ---
CONFIGURED_CASKS=$(parse_yaml_list "$HOMEBREW_VARS" "homebrew_casks" | sort)
ABSENT_CASKS=$(parse_yaml_list "$HOMEBREW_VARS" "homebrew_casks_absent" | sort)
KNOWN_CASKS=$(printf '%s\n%s' "$CONFIGURED_CASKS" "$ABSENT_CASKS" | sort -u)
INSTALLED_CASKS=$(brew list --cask 2>/dev/null | sort)

UNMANAGED_CASKS=$(comm -23 <(echo "$INSTALLED_CASKS") <(echo "$KNOWN_CASKS"))

if [ -n "$UNMANAGED_CASKS" ]; then
  UNMANAGED_FOUND=true
  review_unmanaged "Homebrew casks" "$HOMEBREW_VARS" "homebrew_casks" "brew uninstall --cask" "$UNMANAGED_CASKS"
fi

# --- VS Code extensions ---
if command -v code &>/dev/null; then
  CONFIGURED_EXTENSIONS=$(parse_yaml_list "$APPS_VARS" "vscode_extensions" | tr '[:upper:]' '[:lower:]' | sort)
  INSTALLED_EXTENSIONS=$(code --list-extensions 2>/dev/null | tr '[:upper:]' '[:lower:]' | sort)

  UNMANAGED_EXTENSIONS=$(comm -23 <(echo "$INSTALLED_EXTENSIONS") <(echo "$CONFIGURED_EXTENSIONS"))

  if [ -n "$UNMANAGED_EXTENSIONS" ]; then
    UNMANAGED_FOUND=true
    review_unmanaged "VS Code extensions" "$APPS_VARS" "vscode_extensions" "code --uninstall-extension" "$UNMANAGED_EXTENSIONS"
  fi
fi

if [ "$UNMANAGED_FOUND" = false ]; then
  echo -e "${GREEN}✓ All installed packages are tracked by mac-setup${NC}"
fi

echo ""
echo "=========================================="
echo -e "  ${GREEN}Done!${NC} Restart your terminal or run: source ~/.zshrc"
echo "=========================================="
