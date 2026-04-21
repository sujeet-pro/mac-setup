---
title: Starship Prompt
---

# Starship Prompt

The shell prompt is powered by [Starship](https://starship.rs/), a fast, cross-shell prompt written in Rust.

## What Shows in the Prompt

The prompt displays contextual information based on your current directory:

- **Directory** -- current path (truncated)
- **Git branch** -- active branch name
- **Git status** -- staged, modified, untracked, etc.
- **Language versions** -- Node.js, Bun, Python, Java (only when relevant)
- **Command duration** -- elapsed time for long-running commands

## Config Location

The starship configuration file is located at:

```
~/.config/starship.toml
```

This file is symlinked from `configs/starship/starship.toml` in the mac-setup repo by the `shell` Ansible role.

## Git Status Indicators

Starship shows git repository status using these symbols:

| Symbol | Meaning    | Description                                |
| ------ | ---------- | ------------------------------------------ |
| `●`    | Staged     | Changes added to the staging area          |
| `✚`    | Modified   | Tracked files with unstaged modifications  |
| `…`    | Untracked  | New files not yet tracked by git           |
| `✖`    | Deleted    | Files removed from the working tree        |
| `»`    | Renamed    | Files that have been renamed               |
| `≠`    | Conflicts  | Merge conflicts that need resolution       |
| `⇡`    | Ahead      | Local commits not yet pushed to remote     |
| `⇣`    | Behind     | Remote commits not yet pulled              |
| `⇕`    | Diverged   | Branch has diverged from remote            |
| `⚑`    | Stashed    | Stashed changes exist                      |

### Example

A prompt showing a modified and staged file on a branch ahead of remote:

```
~/personal/mac-setup on main [●✚ ⇡1]
❯
```

## Language Detection

Starship auto-detects language versions based on files in the current directory. The version badge only appears when relevant project files are present:

| Indicator | Detected by                                   |
| --------- | --------------------------------------------- |
| Node.js   | `package.json`, `.node-version`, `.nvmrc`     |
| Bun       | `bun.lockb`, `bunfig.toml`                    |
| Python    | `pyproject.toml`, `requirements.txt`, `.py`   |
| Java      | `pom.xml`, `build.gradle`, `.java`            |

This keeps the prompt clean -- you only see version information when you are actually working in a project that uses that language.

## Disabled Modules

The following starship modules are disabled by default to keep the prompt minimal. They can be re-enabled in `starship.toml` if needed:

| Module       | Why disabled                                    |
| ------------ | ----------------------------------------------- |
| `aws`        | AWS context adds noise for most daily work      |
| `kubernetes` | Cluster info is better accessed via `kctx`/`kns`|
| `time`       | Wall clock time is available in the menu bar    |
| `battery`    | Battery status is visible in the macOS menu bar |

To enable a module, find or add its section in `~/.config/starship.toml` and set `disabled = false`:

```toml
[aws]
disabled = false
```
