#!/bin/bash
set -euo pipefail

########################################
# End-to-end mac-setup test in a clean Tart macOS VM
#
# Requires: brew install cirruslabs/cli/tart
#
# What it does:
#   1. Clones a fresh macOS Sequoia VM image
#   2. Boots it headless
#   3. Copies the repo into the VM via rsync
#   4. Creates a test ~/.zshenv with dummy values
#   5. Installs Homebrew + Ansible, runs the playbook
#   6. Runs scripts/validate.sh
#   7. Tears down the VM
#
# Usage:
#   ./scripts/tart-test.sh              # full test
#   ./scripts/tart-test.sh --keep       # keep VM after test (for debugging)
########################################

RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BOLD='\033[1m'
NC='\033[0m'

VM_NAME="mac-setup-test-$$"
VM_IMAGE="ghcr.io/cirruslabs/macos-sequoia-base:latest"
VM_USER="admin"
VM_PASS="admin"
SSH_OPTS="-o StrictHostKeyChecking=no -o UserKnownHostsFile=/dev/null -o LogLevel=ERROR -o ConnectTimeout=5"
KEEP_VM=false
SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
REPO_DIR="$(cd "$SCRIPT_DIR/.." && pwd)"

# Parse args
for arg in "$@"; do
  case "$arg" in
    --keep) KEEP_VM=true ;;
    *) echo "Unknown arg: $arg"; exit 1 ;;
  esac
done

# --- Helpers ---

log()  { echo -e "${BOLD}==> $1${NC}"; }
ok()   { echo -e "  ${GREEN}✓${NC} $1"; }
warn() { echo -e "  ${YELLOW}!${NC} $1"; }
err()  { echo -e "  ${RED}✗${NC} $1"; }

ssh_vm() {
  sshpass -p "$VM_PASS" ssh $SSH_OPTS "$VM_USER@$VM_IP" "$@"
}

rsync_to_vm() {
  sshpass -p "$VM_PASS" rsync -az --delete \
    --exclude='.git' \
    --exclude='.claude' \
    --exclude='.DS_Store' \
    -e "ssh $SSH_OPTS" \
    "$1" "$VM_USER@$VM_IP:$2"
}

cleanup() {
  if [ "$KEEP_VM" = true ]; then
    warn "Keeping VM '$VM_NAME' (IP: ${VM_IP:-unknown}). Delete with: tart delete $VM_NAME"
    # Still need to stop the VM process
    kill "$VM_PID" 2>/dev/null || true
    return
  fi
  log "Cleaning up..."
  kill "$VM_PID" 2>/dev/null || true
  sleep 2
  tart delete "$VM_NAME" 2>/dev/null || true
  ok "VM deleted"
}

wait_for_ssh() {
  local max_attempts=60
  local attempt=0
  log "Waiting for VM SSH (up to ${max_attempts}s)..."

  while [ $attempt -lt $max_attempts ]; do
    if sshpass -p "$VM_PASS" ssh $SSH_OPTS "$VM_USER@$VM_IP" "echo ok" &>/dev/null; then
      ok "SSH ready"
      return 0
    fi
    sleep 1
    ((attempt++))
  done

  err "SSH not available after ${max_attempts}s"
  return 1
}

# --- Pre-flight ---

echo ""
echo "=========================================="
echo "  Mac Setup E2E Test (Tart VM)"
echo "=========================================="
echo ""

if ! command -v tart &>/dev/null; then
  err "Tart is not installed. Install with: brew install cirruslabs/cli/tart"
  exit 1
fi

if ! command -v sshpass &>/dev/null; then
  log "Installing sshpass (needed for non-interactive SSH)..."
  brew install sshpass 2>/dev/null || brew install esolitos/ipa/sshpass 2>/dev/null || {
    err "Could not install sshpass. Install manually: brew install esolitos/ipa/sshpass"
    exit 1
  }
fi

# --- Create and boot VM ---

# Clean up any leftover VM with same name pattern
for old_vm in $(tart list 2>/dev/null | grep "mac-setup-test-" | awk '{print $1}'); do
  warn "Deleting leftover test VM: $old_vm"
  tart delete "$old_vm" 2>/dev/null || true
done

log "Cloning fresh macOS VM ($VM_IMAGE)..."
log "  (first run downloads ~15 GB — subsequent runs use cache)"
tart clone "$VM_IMAGE" "$VM_NAME"
ok "VM cloned as '$VM_NAME'"

log "Starting VM headless..."
tart run "$VM_NAME" --no-graphics &
VM_PID=$!
trap cleanup EXIT

# Get VM IP (retry because DHCP takes a moment)
sleep 5
VM_IP=""
for i in $(seq 1 30); do
  VM_IP=$(tart ip "$VM_NAME" 2>/dev/null || true)
  if [ -n "$VM_IP" ]; then break; fi
  sleep 2
done

if [ -z "$VM_IP" ]; then
  err "Could not get VM IP"
  exit 1
fi
ok "VM IP: $VM_IP"

wait_for_ssh

# --- Run setup inside VM ---

log "Copying repo into VM..."
ssh_vm "mkdir -p ~/mac-setup"
rsync_to_vm "$REPO_DIR/" "~/mac-setup/"
ok "Repo synced"

log "Creating test ~/.zshenv..."
ssh_vm 'cat > ~/.zshenv << '"'"'ZSHENV'"'"'
export GIT_USER_NAME="Test User"
export GIT_PERSONAL_EMAIL="test@example.com"
export GIT_WORK_EMAIL="test@company.com"
export SSH_PERSONAL_KEY="id_ed25519_personal"
export SSH_WORK_KEY="id_ed25519_work"
ZSHENV'
ok "~/.zshenv created"

log "Installing Homebrew in VM..."
ssh_vm 'NONINTERACTIVE=1 /bin/bash -c "$(curl -fsSL https://raw.githubusercontent.com/Homebrew/install/HEAD/install.sh)"'
ok "Homebrew installed"

log "Installing Ansible in VM..."
ssh_vm 'eval "$(/opt/homebrew/bin/brew shellenv)" && brew install ansible'
ok "Ansible installed"

log "Running Ansible playbook (this takes a while)..."
PLAYBOOK_EXIT=0
ssh_vm 'source ~/.zshenv && eval "$(/opt/homebrew/bin/brew shellenv)" && cd ~/mac-setup && ansible-playbook setup.yml' || PLAYBOOK_EXIT=$?

if [ "$PLAYBOOK_EXIT" -ne 0 ]; then
  err "Ansible playbook failed (exit $PLAYBOOK_EXIT)"
  if [ "$KEEP_VM" = false ]; then
    warn "Re-run with --keep to debug: ./scripts/tart-test.sh --keep"
  fi
  exit 1
fi
ok "Playbook completed"

log "Running validation..."
VALIDATE_EXIT=0
ssh_vm 'source ~/.zshenv && eval "$(/opt/homebrew/bin/brew shellenv)" && cd ~/mac-setup && bash scripts/validate.sh' || VALIDATE_EXIT=$?

echo ""
echo "=========================================="
if [ "$VALIDATE_EXIT" -eq 0 ]; then
  echo -e "  ${GREEN}${BOLD}E2E TEST PASSED${NC}"
else
  echo -e "  ${RED}${BOLD}E2E TEST FAILED${NC} (validate exit $VALIDATE_EXIT)"
  if [ "$KEEP_VM" = false ]; then
    warn "Re-run with --keep to debug: ./scripts/tart-test.sh --keep"
  fi
fi
echo "=========================================="
echo ""

exit "$VALIDATE_EXIT"
