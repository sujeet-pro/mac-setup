# `~/.config/creds/` — credentials layout

Source of truth: `mac-setup/configs/creds/`. The `creds` Ansible role
scaffolds `~/.config/creds/` from these templates on every `make setup`.

Since 2026-05-19 the layout is **single-file per service**: every key —
secret and non-secret — lives in `<svc>/creds.sh`, mode 0600. The
former `config.sh` was retired; a one-time migration helper at
`configs/creds/_lib/consolidate_to_creds_sh.py` folds any leftover
`config.sh` into `creds.sh` in place (idempotent).

```
~/.config/creds/
├── loader.sh                 → symlink to mac-setup/configs/creds/loader.sh
│                              (sourced from ~/.zshenv; walks every <svc>/
│                              and sources creds.sh)
├── _lib/                     → symlink to mac-setup/configs/creds/_lib/
│   ├── creds_lib/            (Python validators + OAuth login flows)
│   ├── bin/                  (creds, creds_login_*, creds_validate;
│   │                          symlinked to ~/.local/bin via the role)
│   ├── merge_template.py     (the never-overwrite merger used by the role)
│   ├── inspect_keys.py       (read-only key-name dumper — never echoes values)
│   └── consolidate_to_creds_sh.py  (one-time migration; idempotent)
├── anthropic/
│   └── creds.sh              (ANTHROPIC_API_KEY_CRED + ANTHROPIC_API_KEY alias)
├── atlassian/
│   └── creds.sh              (ATLASSIAN_API_TOKEN_CRED, ATLASSIAN_SITE, ATLASSIAN_USERNAME)
├── bitbucket/
│   └── creds.sh              (BITBUCKET_TOKEN_CRED)
├── datadog/
│   └── creds.sh              (DATADOG_API_KEY_CRED, DATADOG_APP_KEY_CRED,
│                              DATADOG_API_KEY_ID, DATADOG_APP_KEY_ID,
│                              DATADOG_SITE, DATADOG_MCP_URL,
│                              + DD_* tool-compat aliases)
├── github/
│   └── creds.sh              (GITHUB_TOKEN_CRED + GITHUB_TOKEN alias)
├── google/
│   ├── creds.sh              (GOOGLE_CLIENT_ID_CRED, GOOGLE_CLIENT_SECRET_CRED,
│   │                          USER_GOOGLE_EMAIL, GOOGLE_CREDENTIALS_FILE,
│   │                          GOOGLE_WORKSPACE_MCP_CREDENTIALS_DIR,
│   │                          + GOOGLE_OAUTH_*/WORKSPACE_MCP_CREDENTIALS_DIR aliases)
│   ├── app.json              (OAuth scope superset — copied once)
│   ├── google.token.json     (refresh token, from `creds login google`)
│   └── scripts/              → repo (login.sh)
├── looker/
│   └── creds.sh              (LOOKER_CLIENT_ID_CRED, LOOKER_CLIENT_SECRET_CRED,
│                              LOOKER_BASE_URL, LOOKER_VERIFY_SSL, LOOKER_TIMEOUT,
│                              + LOOKER_CLIENT_ID/SECRET tool-compat aliases)
├── mixpanel/
│   └── creds.sh              (MIXPANEL_PROJECT_ID, MIXPANEL_REGION)
│                              (hosted OAuth — no secrets in this file)
├── npm/
│   └── creds.sh              (NPM_TOKEN_CRED + NPM_TOKEN alias)
├── okta/
│   └── creds.sh              (OKTA_APP_CLIENT_SECRET_CRED, OKTA_APP_CLIENT_ID,
│                              OKTA_ISSUER, OKTA_REDIRECT_URLS_LOCAL)
├── slack/
│   ├── creds.sh              (SLACK_CLIENT_SECRET_CRED,
│   │                          SLACK_APP_CONFIG_{ACCESS,REFRESH}_TOKEN_CRED,
│   │                          SLACK_APP_ID, SLACK_CLIENT_ID, SLACK_CREDENTIALS_FILE)
│   ├── app.json              (OAuth scopes + redirect_uri)
│   ├── slack.token.json      (bot + user tokens, from `creds login slack`)
│   └── scripts/              → repo (login.sh, rotate.{sh,py})
├── snowflake/
│   ├── creds.sh              (SNOWFLAKE_ACCESS_TOKEN_CRED, SNOWFLAKE_HOME,
│   │                          SNOWFLAKE_CONNECTION_NAME, SNOWFLAKE_SERVICE_CONFIG_FILE)
│   ├── connections.toml      (user-managed)
│   └── service-config.yaml   (user-managed)
├── statsig/
│   └── creds.sh              (STATSIG_CONSOLE_API_KEY_CRED)
└── logs/                     (rotation/login/validate logs, auto-pruned
                               after CREDS_LOG_RETENTION_DAYS, default 7d)
```

## Naming convention

- **`<VAR>_CRED`** — every secret-bearing env var carries the `_CRED`
  suffix so `grep _CRED ~/.config/creds/**/creds.sh` lists every
  credential at a glance. The user's rule: anything that must be kept
  secret (API keys, OAuth client secrets, refresh tokens, PATs) ends
  with `_CRED`. Anything that doesn't is non-secret and lives in the
  same file without the suffix.
- **Tool-compat aliases** — when a third-party tool reads a specific
  un-suffixed env var (e.g. `gh` reads `GITHUB_TOKEN`, the Anthropic
  SDK reads `ANTHROPIC_API_KEY`, the Datadog SDK reads `DD_API_KEY`,
  the Google workspace-mcp reads `GOOGLE_OAUTH_CLIENT_ID`), the
  matching `creds.sh` exports BOTH: `export X_CRED=...; export X="$X_CRED"`.
- **Non-secret vars** (URLs, usernames, client IDs without `_CRED`,
  region pins) live in the same `creds.sh` as the secrets — just
  without the suffix. The file is still 0600 because it contains
  secrets too.

## Diagnostic helpers

```bash
python3 ~/.config/creds/_lib/inspect_keys.py            # JSON: every key + classification
python3 ~/.config/creds/_lib/inspect_keys.py --human    # tabular
python3 ~/.config/creds/_lib/consolidate_to_creds_sh.py --dry-run   # preview migration
python3 ~/.config/creds/_lib/consolidate_to_creds_sh.py             # run it
```

Both helpers operate on key NAMES only — never echo a credential value.

## Setup behaviour

The Ansible role (`roles/creds/`) is **never-overwrite**:

1. On first install: each `<svc>/creds.sh.template` is copied to
   `~/.config/creds/<svc>/creds.sh` with mode 0600.
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

The unified `creds` CLI is the preferred entry point. Service names
accept aliases — `creds login jira` resolves to `atlassian`, `creds
validate dd gh` resolves to `datadog` + `github`. Run `creds status`
(or just `creds`) to see every service alongside its aliases.

```bash
creds                                       # status table (services × auth × aliases)
creds status                                # same as above
creds validate                              # probe every service that has a connector
creds validate slack google                 # probe a subset
creds validate jira --json                  # JSON output (alias resolves to atlassian)
creds validate --list                       # connector names, one per line
creds validate --list-json                  # all services + aliases (shell completion / /adk-setup --check)

creds login google                          # OAuth — refresh-token flow
creds login slack                           # OAuth — bot/user-token flow
creds login github                          # token — opens mint URL, prompts with no echo, writes to creds.sh
creds login jira                            # token — alias resolution works on login too

creds rotate slack                          # invokes ~/.config/creds/slack/scripts/rotate.sh
```

Run `creds` with no subcommand on a TTY for an interactive textual TUI
(services table + login/validate/refresh actions + streaming log).
Requires `textual`:

```bash
uv tool install textual    # preferred
pipx install textual       # alternative
pip install --user textual # last resort
```

If `textual` isn't installed, `creds` falls back to the same table that
`creds status` prints.

The legacy entrypoints stay for muscle memory and back-compat:
`creds_validate`, `creds_login_google`, `creds_login_slack`.

The guided `creds login <token-svc>` flow uses `getpass.getpass` — the
value is read with no echo and written directly to
`~/.config/creds/<svc>/creds.sh` (0600). The value never enters
stdout/stderr, never appears in the log file, and is not exposed to
any agent reading the conversation.

## Exit codes (`creds validate` and legacy `creds_validate`)

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
4. For OAuth services, re-run `creds login <svc>` (or the legacy
   `creds_login_<svc>` wrapper).
5. `creds validate <svc>` to confirm green.

For Slack app-config tokens specifically, `scripts/rotate.sh` performs
the entire flow programmatically (uses the current refresh token to
mint a fresh pair, then rewrites the two relevant lines in `creds.sh`
without touching anything else).
