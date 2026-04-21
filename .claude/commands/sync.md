Sync the mac-setup repo with the current system state. Follow these steps:

## 1. Homebrew packages

Run `brew leaves` (formulae) and `brew list --cask` (casks). Compare with `roles/homebrew/vars/main.yml`. Report any packages installed on the system but missing from the repo, and any listed in the repo but not installed.

## 2. VS Code extensions

Run `code --list-extensions`. Compare with both `roles/apps/vars/main.yml` (vscode_extensions) and `.vscode/extensions.json` (recommendations). Report differences — both files should stay in sync with each other and with what's installed.

## 3. macOS defaults

Read the current values for each default listed in `roles/macos/vars/main.yml` using `defaults read`. Compare with the values defined in the vars file. Report any that differ from what the repo expects.

## 4. Config files

For each config file below, compare the current system file with the repo copy. If the system file is a symlink pointing to the repo, it is already in sync — skip it. For non-symlinked or diverged files, show the diff.

| System path | Repo path |
|-------------|-----------|
| `~/.zshrc` | `configs/shell/.zshrc` |
| `~/.config/starship.toml` | `configs/shell/starship.toml` |
| `~/.config/gh/config.yml` | `configs/gh/config.yml` |
| `~/.config/zed/settings.json` | `configs/zed/settings.json` |
| `~/.config/mise/config.toml` | `configs/mise/config.toml` |
| `~/.config/ghostty/config` | `configs/ghostty/config` |
| `~/.config/btop/btop.conf` | `configs/btop/btop.conf` |
| `~/.aws/config` | `configs/aws/config` |
| `~/.colima/default.yaml` | `configs/colima/default.yaml` |
| `~/Library/Application Support/Code/User/settings.json` | `configs/vscode/settings.json` |
| `~/.claude/settings.json` | `configs/claude/settings.json` |
| `~/.gitignore-work` | `configs/git/gitignore-work` |

## 5. Update repo files

Present all differences found above and ask the user which changes to apply. For approved changes, update the corresponding files in the repo. Keep the existing formatting and comment structure.

## 6. Validate

Run `make validate` to verify everything passes after changes.
