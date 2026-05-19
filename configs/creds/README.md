# `~/.config/creds/` — credentials layout

Source of truth: `mac-setup/configs/creds/`. The `creds` Ansible role
scaffolds `~/.config/creds/` from these templates on every `make setup`.

```
~/.config/creds/
├── loader.sh                 → symlink to mac-setup/configs/creds/loader.sh
│                              (sourced from ~/.zshenv; walks every <svc>/
│                              folder and sources config.sh then creds.sh)
├── _lib/                     → symlink to mac-setup/configs/creds/_lib/
│   ├── creds_lib/            (Python validators + OAuth login flows)
│   ├── bin/                  (creds_login_*, creds_validate; symlinked to
│   │                          ~/.local/bin via the Ansible role)
│   └── merge_template.py     (the never-overwrite merger used by the role)
├── anthropic/
│   └── creds.sh              (ANTHROPIC_API_KEY_CRED)
├── atlassian/
│   ├── creds.sh              (ATLASSIAN_API_TOKEN_CRED)
│   └── config.sh             (ATLASSIAN_SITE, ATLASSIAN_USERNAME)
├── datadog/
│   ├── creds.sh              (DATADOG_API_KEY_CRED, DATADOG_APP_KEY_CRED)
│   └── config.sh             (DD_SITE, DATADOG_SITE, DD_MCP_URL)
├── github/
│   └── creds.sh              (GITHUB_TOKEN_CRED, alias → GITHUB_TOKEN)
├── google/
│   ├── creds.sh              (GOOGLE_CLIENT_SECRET_CRED)
│   ├── config.sh             (GOOGLE_CLIENT_ID, USER_GOOGLE_EMAIL, …)
│   ├── app.json              (OAuth scope superset — copied once, never
│   │                          overwritten by the role)
│   ├── google.token.json     (refresh token, written by creds_login_google)
│   └── scripts/              → symlink to repo
│       └── login.sh          (thin wrapper → creds_login_google)
├── looker/
│   ├── creds.sh              (LOOKER_CLIENT_SECRET_CRED)
│   └── config.sh             (LOOKER_SITE, LOOKER_CLIENT_ID, …)
├── mixpanel/
│   └── config.sh             (MIXPANEL_PROJECT_ID, MIXPANEL_REGION)
│                              (auth is OAuth in the hosted MCP — no creds.sh)
├── npm/
│   └── creds.sh              (NPM_TOKEN_CRED, alias → NPM_TOKEN)
├── okta/
│   ├── creds.sh              (OKTA_APP_CLIENT_SECRET_CRED)
│   └── config.sh             (OKTA_APP_CLIENT_ID, OKTA_REDIRECT_URLS_LOCAL)
├── slack/
│   ├── creds.sh              (SLACK_CLIENT_SECRET_CRED,
│   │                           SLACK_APP_CONFIG_{ACCESS,REFRESH}_TOKEN_CRED)
│   ├── config.sh             (SLACK_CLIENT_ID, SLACK_CREDENTIALS_FILE)
│   ├── app.json              (OAuth scopes + redirect_uri)
│   ├── slack.token.json      (bot + user tokens, from creds_login_slack)
│   └── scripts/              → symlink to repo
│       ├── login.sh          (wrapper → creds_login_slack)
│       └── rotate.{sh,py}    (POSTs SLACK_APP_CONFIG_REFRESH_TOKEN_CRED to
│                              tooling.tokens.rotate and writes both new
│                              tokens back into creds.sh, in place)
├── snowflake/
│   ├── creds.sh              (SNOWFLAKE_ACCESS_TOKEN_CRED)
│   ├── config.sh             (SNOWFLAKE_HOME, SNOWFLAKE_CONNECTION_NAME, …)
│   ├── connections.toml      (account/user/warehouse/role; user-managed)
│   └── service-config.yaml   (snowflake-labs-mcp tool allow-list; user-managed)
├── statsig/
│   └── creds.sh              (STATSIG_CONSOLE_API_KEY_CRED)
└── logs/                     (rotation/login/validate logs, auto-pruned
                               after CREDS_LOG_RETENTION_DAYS, default 7d)
```

## Naming convention

- **`<VAR>_CRED`** — every secret-bearing env var carries the `_CRED`
  suffix so `grep _CRED ~/.zshenv ~/.config/creds/**/creds.sh` lists every
  credential at a glance.
- **Tool-compat aliases** — when a third-party tool reads a specific
  un-suffixed env var (e.g. `gh` reads `GITHUB_TOKEN`, the Anthropic SDK
  reads `ANTHROPIC_API_KEY`, `npm` reads `NPM_TOKEN`), the matching
  `creds.sh` exports BOTH: `export X_CRED=...; export X="$X_CRED"`.
- **Non-secret vars** (URLs, usernames, client IDs, region pins) do
  NOT carry `_CRED`. They live in `config.sh`, not `creds.sh`.

## Setup behaviour

The Ansible role (`roles/creds/`) is **never-overwrite**:

1. On first install: each `<svc>/{creds,config}.sh.template` is copied to
   `~/.config/creds/<svc>/{creds,config}.sh` with the right mode (0600
   for `creds.sh`, 0644 for `config.sh`).
2. On every subsequent run: the merger (`_lib/merge_template.py`)
   - never touches an existing value,
   - appends any new keys from the template that aren't in the live
     file (with their template placeholder),
   - tags any live-file keys not in the template with
     `# untracked-by-mac-setup` so you can see what's outside the
     managed set.
3. Static files (`app.json`, `connections.toml`,
   `service-config.yaml`) are copied **once**; later edits stay.

## Commands

```bash
creds_login_google                          # mint a refresh token
creds_login_slack                           # mint bot + user tokens
creds_validate                              # probe every connector
creds_validate slack google                 # probe a subset
creds_validate --list                       # print connector names
~/.config/creds/slack/scripts/rotate.sh     # rotate Slack app-config tokens
```

## Exit codes (`creds_validate`)

| code | meaning                                                  |
| ---- | -------------------------------------------------------- |
| `0`  | every connector is `OK` or `SKIPPED`                     |
| `1`  | at least one connector returned `FAIL`                   |
| `2`  | no `FAIL`s, but at least one connector is `MISCONFIGURED` |
| `3`  | nothing to do (no connectors registered)                 |

## Rotation flow

1. Mint the new secret in the provider console.
2. Edit `~/.config/creds/<svc>/creds.sh` and replace the value (the
   file is `0600`; the merger never overwrites you).
3. `source ~/.zshenv` to reload (or open a new shell).
4. For OAuth services, re-run the matching `creds_login_*` flow.
5. `creds_validate <svc>` to confirm green.

For Slack app-config tokens specifically, `scripts/rotate.sh` performs
the entire flow programmatically (uses the current refresh token to
mint a fresh pair, then rewrites the two relevant lines in `creds.sh`
without touching anything else).
