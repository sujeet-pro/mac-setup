# ~/.config/creds/loader.sh — sourced from ~/.zshenv
#
# Walks every service folder under ~/.config/creds/ and sources its
# `creds.sh` (which carries both non-secret config and secrets in one
# file, since 2026-05-19; chmod 600 because the file holds tokens for
# any service that has them). Service folders without a creds.sh are
# skipped automatically — that's how `_lib/`, `logs/`, and any
# in-progress scaffolding stay out of the eval path.
#
# Managed by mac-setup (roles/creds). The rendered ~/.config/creds/
# copy is a symlink to mac-setup/configs/creds/loader.sh; edit the
# source and re-run `make install-creds` to update it.

for _svc in "$HOME/.config/creds"/*/; do
  [ -r "$_svc/creds.sh" ] && . "$_svc/creds.sh"
done
unset _svc
