#!/usr/bin/env bash
# Rotate the Slack app-config token pair using tooling.tokens.rotate.
#
# Slack app-config tokens (the "xoxe-…" pair used to manage app configuration
# via API) are single-use refresh tokens. This script:
#
#   1. POSTs the current $SLACK_APP_CONFIG_REFRESH_TOKEN_CRED to
#      https://slack.com/api/tooling.tokens.rotate
#   2. Parses the new access + refresh tokens from the response.
#   3. Writes BOTH back into $CREDS_HOME/slack/creds.sh in place
#      (preserves every other key + comment + ordering).
#
# Exit codes:
#   0 — rotated and creds.sh updated
#   2 — refresh token unset
#   3 — Slack rejected the rotate (token expired / invalid)
#
# After running, `source ~/.zshenv` (or open a new shell) to pick up the
# rotated tokens.
exec python3 "$(dirname "$0")/rotate.py" "$@"
