#!/usr/bin/env bash
# migrate-to-synced.sh — one-shot move of creds + adk + ssh + zshenv to ~/user-synced-data/.
# Runs from ~/personal/mac-setup/. After this completes:
#   - ~/.config/creds and ~/.agents-devkit are removed
#   - ~/.zshenv is a symlink into ~/user-synced-data/mac-setup/zshenv
#   - sensitive ~/.ssh files are symlinks into ~/user-synced-data/ssh
#   - ~/adk-data holds machine-local adk working dirs
#
# Re-running is a no-op (every step is guarded).
set -euo pipefail

# Paths (intentionally hardcoded — single-user one-shot)
SYNC="$HOME/user-synced-data"
ADK_LOCAL="$HOME/adk-data"
SNAPSHOT="$HOME/migration-snapshot-$(date -u +%Y%m%dT%H%M%SZ)"

say() { printf '  · %s\n' "$1"; }
abort() { printf '  ✗ %s\n' "$1"; exit 1; }

# --- pre-flight ------------------------------------------------------------
[ -d "$HOME/personal/mac-setup" ]      || abort "mac-setup repo missing at ~/personal/mac-setup"
[ -d "$HOME/personal/agents-devkit" ]  || abort "agents-devkit repo missing at ~/personal/agents-devkit"

mkdir -p "$SYNC" "$ADK_LOCAL"
mkdir -p "$SYNC/creds" "$SYNC/adk/config" "$SYNC/adk/memory" "$SYNC/ssh" "$SYNC/mac-setup"
chmod 700 "$SYNC/creds" "$SYNC/ssh" 2>/dev/null || true

# --- snapshot (rescue parachute) ------------------------------------------
say "snapshot → $SNAPSHOT (chmod 700)"
mkdir -p "$SNAPSHOT"
chmod 700 "$SNAPSHOT"
cp -a "$HOME/.zshenv"                "$SNAPSHOT/zshenv" 2>/dev/null || true
[ -d "$HOME/.config/creds" ]   && cp -a "$HOME/.config/creds"   "$SNAPSHOT/creds"   2>/dev/null || true
[ -d "$HOME/.agents-devkit" ]  && cp -a "$HOME/.agents-devkit"  "$SNAPSHOT/adk"     2>/dev/null || true
[ -d "$HOME/.ssh" ]            && cp -a "$HOME/.ssh"            "$SNAPSHOT/ssh"     2>/dev/null || true

# --- migrate creds ---------------------------------------------------------
say "migrate creds → $SYNC/creds"
if [ -d "$HOME/.config/creds" ]; then
  for svc_dir in "$HOME/.config/creds"/*/; do
    [ -d "$svc_dir" ] || continue
    name="$(basename "$svc_dir")"
    case "$name" in _lib|logs) continue ;; esac          # _lib is a symlink to repo; logs are machine-local
    if [ ! -e "$SYNC/creds/$name" ]; then
      mv "$svc_dir" "$SYNC/creds/$name"
      say "  moved $name"
    fi
  done
fi
find "$SYNC/creds" -name 'creds.sh'     -type f -exec chmod 600 {} +
find "$SYNC/creds" -name '*.token.json' -type f -exec chmod 600 {} +
find "$SYNC/creds" -name 'app.json'     -type f -exec chmod 644 {} +

# --- migrate adk config + memory -------------------------------------------
say "migrate adk config → $SYNC/adk/config"
if [ -d "$HOME/.agents-devkit/config" ] && [ ! -L "$HOME/.agents-devkit/config" ]; then
  for f in "$HOME/.agents-devkit/config"/* "$HOME/.agents-devkit/config"/.[!.]*; do
    [ -e "$f" ] || continue
    name="$(basename "$f")"
    [ -e "$SYNC/adk/config/$name" ] || mv "$f" "$SYNC/adk/config/$name"
  done
fi

say "migrate adk memory → $SYNC/adk/memory"
if [ -d "$HOME/.agents-devkit/memory" ] && [ ! -L "$HOME/.agents-devkit/memory" ]; then
  for f in "$HOME/.agents-devkit/memory"/* "$HOME/.agents-devkit/memory"/.[!.]*; do
    [ -e "$f" ] || continue
    name="$(basename "$f")"
    [ -e "$SYNC/adk/memory/$name" ] || mv "$f" "$SYNC/adk/memory/$name"
  done
fi

# --- migrate adk data dirs → ~/adk-data -----------------------------------
say "migrate adk data → $ADK_LOCAL"
for dir in handoff improve investigations legacy logs repos \
           skill-explain skill-investigate skill-pr-review skill-review \
           skill-setup skill-sync tui; do
  src="$HOME/.agents-devkit/$dir"
  dst="$ADK_LOCAL/$dir"
  [ -e "$src" ] || continue
  [ -L "$src" ] && continue
  [ -e "$dst" ] || mv "$src" "$dst"
done

# Tear down the (now empty) ~/.agents-devkit and ~/.config/creds
if [ -d "$HOME/.agents-devkit" ]; then
  rmdir "$HOME/.agents-devkit/config"  2>/dev/null || true
  rmdir "$HOME/.agents-devkit/memory"  2>/dev/null || true
  rmdir "$HOME/.agents-devkit"         2>/dev/null || {
    say "  ~/.agents-devkit not empty — leftover files at:"
    find "$HOME/.agents-devkit" -mindepth 1 -maxdepth 3 | sed 's/^/      /'
  }
fi
if [ -d "$HOME/.config/creds" ]; then
  rm -f "$HOME/.config/creds/loader.sh" "$HOME/.config/creds/_lib"  # repo-symlinks, obsolete
  rmdir "$HOME/.config/creds/logs" 2>/dev/null || true
  rmdir "$HOME/.config/creds"      2>/dev/null || {
    say "  ~/.config/creds not empty — leftover files at:"
    find "$HOME/.config/creds" -mindepth 1 -maxdepth 3 | sed 's/^/      /'
  }
fi

# --- migrate ssh -----------------------------------------------------------
say "migrate ssh → $SYNC/ssh"
for f in id_ed25519 id_ed25519.pub config.local known_hosts; do
  src="$HOME/.ssh/$f"; dst="$SYNC/ssh/$f"
  if [ -f "$src" ] && [ ! -L "$src" ] && [ ! -e "$dst" ]; then
    mv "$src" "$dst"; say "  moved $f"
  fi
done
for pem in "$HOME/.ssh"/*.pem; do
  [ -f "$pem" ] && [ ! -L "$pem" ] || continue
  dst="$SYNC/ssh/$(basename "$pem")"
  [ -e "$dst" ] || mv "$pem" "$dst"
done
# perms
chmod 700 "$SYNC/ssh"
find "$SYNC/ssh" -name 'id_*'   ! -name '*.pub' -exec chmod 600 {} +
find "$SYNC/ssh" -name '*.pem'                  -exec chmod 600 {} +
[ -f "$SYNC/ssh/config.local" ] && chmod 600 "$SYNC/ssh/config.local"
find "$SYNC/ssh" -name '*.pub'                  -exec chmod 644 {} +
[ -f "$SYNC/ssh/known_hosts"  ] && chmod 644 "$SYNC/ssh/known_hosts"
# symlinks back into ~/.ssh/
for f in "$SYNC/ssh"/*; do
  [ -e "$f" ] || continue
  name="$(basename "$f")"
  if [ ! -e "$HOME/.ssh/$name" ]; then
    ln -s "$f" "$HOME/.ssh/$name"; say "  linked ~/.ssh/$name"
  fi
done

# --- migrate ~/.zshenv -----------------------------------------------------
say "migrate ~/.zshenv → $SYNC/mac-setup/zshenv"
NEW_ZSHENV="$SYNC/mac-setup/zshenv"
if [ ! -e "$NEW_ZSHENV" ]; then
  # Build NEW zshenv = (new HOME block from template) + (user's existing exports)
  TEMPLATE="$HOME/personal/mac-setup/configs/shell/.zshenv.example"
  # Extract the HOME block from the template (everything up to the "Git identity" section header)
  awk '
    /^# --- Git identity/ { in_id=1; next }
    in_id && /^# ---/      { in_id=0 }
    !in_id                  { print }
  ' "$TEMPLATE" > "$NEW_ZSHENV.tmp"
  # Append user's actual GIT_*, SSH_*, CLAUDE_CODE_* lines from old ~/.zshenv (preserve values).
  grep -E '^export (GIT_|SSH_|CLAUDE_CODE_)' "$HOME/.zshenv" >> "$NEW_ZSHENV.tmp" || true
  mv "$NEW_ZSHENV.tmp" "$NEW_ZSHENV"
  chmod 600 "$NEW_ZSHENV"
fi
# Symlink ~/.zshenv → synced
if [ -e "$HOME/.zshenv" ] && [ ! -L "$HOME/.zshenv" ]; then
  rm "$HOME/.zshenv"
fi
[ -L "$HOME/.zshenv" ] || ln -s "$NEW_ZSHENV" "$HOME/.zshenv"
# ~/.zshenv.local touch
if [ ! -e "$HOME/.zshenv.local" ]; then
  printf '# Per-machine overrides for ~/.zshenv. Never synced.\n' > "$HOME/.zshenv.local"
  chmod 600 "$HOME/.zshenv.local"
fi

# --- verify ---------------------------------------------------------------
say "verifying"
[ -L "$HOME/.zshenv" ]                          || abort "~/.zshenv is not a symlink"
[ -L "$HOME/.ssh/id_ed25519" ] || [ ! -f "$SYNC/ssh/id_ed25519" ] || abort "~/.ssh/id_ed25519 is not a symlink"
[ -f "$SYNC/creds/anthropic/creds.sh" ]         || abort "creds.sh not at $SYNC/creds/anthropic"
[ -f "$SYNC/adk/config/core.yaml" ]             || abort "core.yaml not at $SYNC/adk/config"
[ -d "$ADK_LOCAL/repos" ] || [ ! -d "$HOME/.agents-devkit/repos" ] || abort "adk repos still in legacy path"

cat <<EOF

  migration done.
   snapshot at: $SNAPSHOT  (delete after a few days of green operation)
   open a NEW terminal so the symlinked ~/.zshenv loads, then run:
     cd ~/personal/mac-setup && make update     # re-applies ansible w/ new env vars
     cd ~/personal/agents-devkit && uv run python install.py    # re-applies adk

EOF
