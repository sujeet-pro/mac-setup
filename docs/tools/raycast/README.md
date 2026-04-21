---
title: Raycast Scripts
---

# Raycast Scripts

[Raycast Script Commands](https://github.com/raycast/script-commands) are standalone scripts with special metadata headers that Raycast can discover and run. Unlike Raycast extensions (which are Node/Swift packages), script commands are simple bash or AppleScript files that live in a directory and are version-controlled with the rest of the mac-setup.

## Setup

After the Ansible playbook runs, the script commands directory is symlinked into place:

```
configs/raycast/script-commands/  -->  ~/.config/raycast/script-commands/  (symlink)
```

To register them with Raycast:

1. Open Raycast preferences (Raycast > Settings > Extensions > Script Commands)
2. Click "Add Script Directory"
3. Select `~/.config/raycast/script-commands`

After this one-time setup, all scripts in the directory are immediately available in Raycast.

## Available scripts

All 11 scripts managed by the mac-setup repo:

| Script | What it does | Input |
|--------|-------------|-------|
| `kill-port` | Kills the process running on a given port | Port number (e.g. `3000`) |
| `open-ghostty-here` | Opens a Ghostty terminal in the current Finder directory | -- |
| `open-in-zed` | Opens the current Finder directory in Zed editor | -- |
| `open-github-repo` | Opens the GitHub page for the current git repo in the browser | -- |
| `pretty-json-clipboard` | Formats the JSON in the clipboard and copies the pretty-printed version back | -- |
| `decode-base64` | Decodes a base64 string from input | Base64 string |
| `url-decode` | Decodes a URL-encoded string | Encoded string |
| `url-encode` | URL-encodes a string | Plain string |
| `toggle-dark-mode` | Toggles macOS dark/light appearance | -- |
| `toggle-hidden-files` | Toggles visibility of hidden files in Finder | -- |
| `flush-dns` | Flushes the macOS DNS cache | -- |

## How to add a new script

1. Create a new file in `configs/raycast/script-commands/`. Use a descriptive kebab-case name:

   ```bash
   touch configs/raycast/script-commands/my-new-script.sh
   chmod +x configs/raycast/script-commands/my-new-script.sh
   ```

2. Add the Raycast metadata headers at the top of the file. Here is the required format:

   ```bash
   #!/bin/bash

   # Required parameters:
   # @raycast.schemaVersion 1
   # @raycast.title My New Script
   # @raycast.mode compact
   # @raycast.packageName Developer

   # Optional parameters:
   # @raycast.icon <emoji>
   # @raycast.argument1 { "type": "text", "placeholder": "Description" }
   # @raycast.description What this script does

   # Your script logic here
   echo "Done"
   ```

3. The metadata fields:

   | Field | Required | Description |
   |-------|----------|-------------|
   | `schemaVersion` | Yes | Always `1` |
   | `title` | Yes | Name shown in Raycast |
   | `mode` | Yes | `compact` (inline result), `silent` (no output), or `fullOutput` (scrollable) |
   | `packageName` | Yes | Groups scripts in Raycast (e.g. `Developer`, `System`, `Navigation`) |
   | `icon` | No | Emoji shown next to the command |
   | `argument1..N` | No | Input arguments with type and placeholder |
   | `description` | No | Shown below the command name in Raycast |

4. For AppleScript-based commands (like `toggle-dark-mode`), use the `.applescript` extension and the `#!/usr/bin/osascript` shebang:

   ```applescript
   #!/usr/bin/osascript

   # Required parameters:
   # @raycast.schemaVersion 1
   # @raycast.title My AppleScript Command
   # @raycast.mode silent
   # @raycast.packageName System

   tell application "System Events"
     -- AppleScript logic here
   end tell
   ```

5. The script is automatically available in Raycast once saved (no restart needed).

## What cannot be automated

Raycast Script Commands are the only part of Raycast that can be fully managed through files. The following must be configured manually:

- **Raycast extensions** -- installed through the Raycast Store, not files
- **Hotkeys** -- assigned per-command in Raycast preferences
- **Settings** -- window behavior, theme, search preferences
- **Snippets** -- text expansion rules
- **Quicklinks** -- bookmarked URLs and searches

For these, use Raycast's built-in export/import feature:

1. Export: Raycast > Settings > Advanced > Export
2. This creates a `.rayconfig` file you can back up or share
3. Import: Raycast > Settings > Advanced > Import
