---
title: Customization
---

# Customization

This guide covers common ways to extend or modify the mac-setup setup.

## Adding a Homebrew Formula

1. Open `roles/homebrew/vars/main.yml`
2. Add the formula name to the `homebrew_formulae` list
3. Run `make setup`

Alternatively, install the formula normally with `brew install <name>`, then run `make cleanup` -- the cleanup step will detect it as unmanaged and prompt you to either add it to the list or remove it.

## Adding a Homebrew Cask

Same pattern as formulae, but use the `homebrew_casks` list in `roles/homebrew/vars/main.yml`.

```yaml
homebrew_casks:
  - firefox
  - rectangle
  - your-new-cask    # add here
```

The playbook sets `accept_external_apps: true`, which means apps that were installed outside of Homebrew (e.g., downloaded directly from a website) are detected and skipped rather than causing an error.

## Adding a VS Code Extension

1. Open `roles/apps/vars/main.yml`
2. Add the extension identifier to the `vscode_extensions` list
3. Run `make setup`

Extension identifiers use the `publisher.extension` format (e.g., `ms-python.python`). You can find the identifier on the VS Code Marketplace or by running `code --list-extensions`.

## Adding an App Config

To bring a new application's config under management:

1. **Place config files** in `configs/<app>/` -- mirror the structure the app expects
2. **Add a symlink task** to the relevant role in `roles/<role>/tasks/main.yml`:
   ```yaml
   - name: Symlink <app> config
     ansible.builtin.file:
       src: "{{ repo_dir }}/configs/<app>/config-file"
       dest: "~/.config/<app>/config-file"
       state: link
       force: true
   ```
3. **Add validation** to `scripts/validate.sh` to verify the symlink is correct:
   ```bash
   check_symlink "$HOME/.config/<app>/config-file" "$MAC_SETUP_DIR/configs/<app>/config-file"
   ```

## Adding a Raycast Script Command

Raycast script commands live in `configs/raycast/script-commands/`. To add one:

1. Create a new `.sh`, `.py`, or `.applescript` file in that directory
2. Include the required Raycast metadata headers at the top of the file:
   ```bash
   #!/bin/bash

   # Required parameters:
   # @raycast.schemaVersion 1
   # @raycast.title My Script
   # @raycast.mode compact

   # Optional parameters:
   # @raycast.icon 
   # @raycast.packageName My Package

   echo "Hello from Raycast"
   ```
3. Make the file executable: `chmod +x configs/raycast/script-commands/my-script.sh`

The Ansible playbook uses a `find` task to auto-discover all script files in that directory, so no additional configuration is needed.

## Removing Packages

To stop managing a formula or cask:

1. Remove it from `homebrew_formulae` or `homebrew_casks` in `roles/homebrew/vars/main.yml`
2. Uninstall it manually:
   - `brew uninstall <formula>`
   - `brew uninstall --cask <cask>`

The playbook only installs; it never uninstalls. Run `make cleanup` afterwards if you want to confirm nothing is left untracked.

## Adding Mise Runtimes

To add or change globally managed runtimes (Node.js, Python, Go, etc.):

1. Edit `configs/mise/config.toml`
2. Add or update the tool version:
   ```toml
   [tools]
   node = "lts"
   python = "3.12"
   go = "latest"       # add new runtime here
   ```
3. Run `make setup` to install the runtime

## Adding npm Global Packages

To add globally installed npm packages (managed through Mise's Node.js):

1. Open `roles/mise/vars/main.yml`
2. Add the package name to the `npm_global_packages` list:
   ```yaml
   npm_global_packages:
     - prettier
     - eslint
     - your-package    # add here
   ```
3. Run `make setup`
