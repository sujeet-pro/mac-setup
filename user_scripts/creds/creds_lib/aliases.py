"""Alias resolution for service names.

Lets the user type `userscripts creds login jira` or `userscripts creds validate dd gh`
and have both resolved to the canonical service name. Aliases are case-insensitive.
"""

from __future__ import annotations

from .meta import REGISTRY

ALIASES: dict[str, str] = {
    # atlassian
    "jira": "atlassian",
    "confluence": "atlassian",
    "atl": "atlassian",
    # github
    "gh": "github",
    "github-com": "github",
    # datadog
    "dd": "datadog",
    "datadoghq": "datadog",
    # google
    "gws": "google",
    "gdrive": "google",
    "gmail": "google",
    "workspace": "google",
    # anthropic
    "claude": "anthropic",
    "claudeai": "anthropic",
    # looker
    "looker-bi": "looker",
    # mixpanel
    "mp": "mixpanel",
    # snowflake
    "sf": "snowflake",
    "snow": "snowflake",
    # statsig
    "stg": "statsig",
    # slack
    "sk": "slack",
}


def resolve(name: str) -> str:
    """Return the canonical service name, raising KeyError if unknown.

    Matching order: exact canonical → alias. Case-insensitive.
    """
    key = (name or "").strip().lower()
    if key in REGISTRY:
        return key
    if key in ALIASES:
        return ALIASES[key]
    raise KeyError(f"unknown service or alias: {name!r}")


def aliases_for(canonical: str) -> list[str]:
    return sorted(a for a, t in ALIASES.items() if t == canonical)
