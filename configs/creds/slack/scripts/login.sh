#!/usr/bin/env bash
# Thin wrapper around `creds_login_slack` so users can find it next to
# the rest of the per-service helpers. Forwards every argument through.
exec creds_login_slack "$@"
