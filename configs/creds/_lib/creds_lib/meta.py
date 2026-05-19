"""Per-service metadata for the unified `creds` driver.

The connector modules under `creds_lib/connectors/` are about validation
logic — what URL to hit, how to parse the response. This file is about
WHO each service is: display name, auth flavor, where to mint a token,
which env-var keys it owns. The `creds login <svc>` flow uses this to
prompt for the right secrets without coupling that flow to per-connector
code.
"""

from __future__ import annotations

from dataclasses import dataclass, field


@dataclass(frozen=True)
class ServiceMeta:
    name: str
    display: str
    auth: str  # "oauth" | "token" | "hosted-oauth" | "config-only"
    mint_url: str | None = None
    secret_vars: tuple[str, ...] = ()
    config_vars: tuple[str, ...] = ()
    # Does creds_lib.connectors.<name> exist with a validate() function?
    has_connector: bool = False
    # Does that connector also expose an OAuth login() function?
    has_login_fn: bool = False
    # Filename under ~/.config/creds/<svc>/scripts/ if rotation is supported.
    rotate_script: str | None = None


REGISTRY: dict[str, ServiceMeta] = {
    "anthropic": ServiceMeta(
        name="anthropic",
        display="Anthropic API",
        auth="token",
        mint_url="https://console.anthropic.com/settings/keys",
        secret_vars=("ANTHROPIC_API_KEY_CRED",),
    ),
    "atlassian": ServiceMeta(
        name="atlassian",
        display="Atlassian (Jira + Confluence)",
        auth="token",
        mint_url="https://id.atlassian.com/manage-profile/security/api-tokens",
        secret_vars=("ATLASSIAN_API_TOKEN_CRED",),
        config_vars=("ATLASSIAN_SITE", "ATLASSIAN_USERNAME"),
        has_connector=True,
    ),
    "datadog": ServiceMeta(
        name="datadog",
        display="Datadog",
        auth="token",
        mint_url="https://app.datadoghq.com/organization-settings/api-keys",
        secret_vars=("DATADOG_API_KEY_CRED", "DATADOG_APP_KEY_CRED"),
        config_vars=("DD_SITE", "DD_MCP_URL"),
        has_connector=True,
    ),
    "github": ServiceMeta(
        name="github",
        display="GitHub",
        auth="token",
        mint_url="https://github.com/settings/tokens",
        secret_vars=("GITHUB_TOKEN_CRED",),
    ),
    "google": ServiceMeta(
        name="google",
        display="Google Workspace",
        auth="oauth",
        secret_vars=("GOOGLE_CLIENT_SECRET_CRED",),
        config_vars=("GOOGLE_CLIENT_ID", "USER_GOOGLE_EMAIL", "WORKSPACE_MCP_CREDENTIALS_DIR"),
        has_connector=True,
        has_login_fn=True,
    ),
    "looker": ServiceMeta(
        name="looker",
        display="Looker",
        auth="token",
        mint_url=None,  # instance-specific; admin UI → Users → <you> → Edit Keys
        secret_vars=("LOOKER_CLIENT_SECRET_CRED",),
        config_vars=("LOOKER_SITE", "LOOKER_CLIENT_ID", "LOOKER_VERIFY_SSL"),
        has_connector=True,
    ),
    "mixpanel": ServiceMeta(
        name="mixpanel",
        display="Mixpanel (hosted OAuth MCP)",
        auth="hosted-oauth",
        config_vars=("MIXPANEL_PROJECT_ID", "MIXPANEL_REGION"),
        has_connector=True,
    ),
    "npm": ServiceMeta(
        name="npm",
        display="npm registry",
        auth="token",
        mint_url="https://www.npmjs.com/settings/~/tokens",
        secret_vars=("NPM_TOKEN_CRED",),
    ),
    "okta": ServiceMeta(
        name="okta",
        display="Okta (sample-app OAuth)",
        auth="token",
        mint_url=None,
        secret_vars=("OKTA_APP_CLIENT_SECRET_CRED",),
        config_vars=("OKTA_APP_CLIENT_ID", "OKTA_REDIRECT_URLS_LOCAL"),
    ),
    "slack": ServiceMeta(
        name="slack",
        display="Slack",
        auth="oauth",
        secret_vars=(
            "SLACK_CLIENT_SECRET_CRED",
            "SLACK_APP_CONFIG_ACCESS_TOKEN_CRED",
            "SLACK_APP_CONFIG_REFRESH_TOKEN_CRED",
        ),
        config_vars=("SLACK_CLIENT_ID",),
        has_connector=True,
        has_login_fn=True,
        rotate_script="rotate.sh",
    ),
    "snowflake": ServiceMeta(
        name="snowflake",
        display="Snowflake",
        auth="token",
        mint_url=None,
        secret_vars=("SNOWFLAKE_ACCESS_TOKEN_CRED",),
        config_vars=("SNOWFLAKE_HOME", "SNOWFLAKE_CONNECTION_NAME"),
        has_connector=True,
    ),
    "statsig": ServiceMeta(
        name="statsig",
        display="Statsig",
        auth="token",
        mint_url="https://console.statsig.com/api_keys",
        secret_vars=("STATSIG_CONSOLE_API_KEY_CRED",),
        has_connector=True,
    ),
}


def all_names() -> list[str]:
    return sorted(REGISTRY.keys())


def get(name: str) -> ServiceMeta:
    if name not in REGISTRY:
        raise KeyError(f"unknown service: {name}")
    return REGISTRY[name]
