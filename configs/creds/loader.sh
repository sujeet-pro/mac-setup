# ~/.config/creds/loader.sh — sourced from ~/.zshenv
#
# Walks every service folder under ~/.config/creds/ and sources `config.sh`
# (non-secret config) then `creds.sh` (secrets, chmod 600). Service folders
# without either file are skipped automatically — that's how `_lib/`, `logs/`,
# and any in-progress scaffolding stay out of the eval path.
#
# Managed by mac-setup (roles/creds). Edits to the rendered ~/.config/creds/
# copy are overwritten on the next playbook run; edit
# mac-setup/configs/creds/loader.sh and re-run instead.

for _svc in "$HOME/.config/creds"/*/; do
  [ -r "$_svc/config.sh" ] && . "$_svc/config.sh"
  [ -r "$_svc/creds.sh" ]  && . "$_svc/creds.sh"
done
unset _svc
