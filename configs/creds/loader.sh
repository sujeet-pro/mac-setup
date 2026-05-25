# configs/creds/loader.sh — sourced from ~/.zshenv via:
#   . "$MAC_SETUP_HOME/configs/creds/loader.sh"
#
# Walks every service folder under $CREDS_HOME and sources its
# `creds.sh` (which carries both non-secret config and secrets in one
# file, since 2026-05-19; chmod 600 because the file holds tokens for
# any service that has them). Service folders without a creds.sh are
# skipped automatically — that's how `_lib/`, `logs/`, and any
# in-progress scaffolding stay out of the eval path.
#
# Managed by mac-setup (roles/creds). Sourced directly from repo via
# $MAC_SETUP_HOME — no ~/.config/creds/ copy involved.

: "${CREDS_HOME:?CREDS_HOME unset — set it in ~/.zshenv (see configs/shell/.zshenv.example)}"

for _svc in "$CREDS_HOME"/*/; do
  [ -r "$_svc/creds.sh" ] && . "$_svc/creds.sh"
done
unset _svc
