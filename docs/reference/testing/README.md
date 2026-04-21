---
title: Testing & Validation
---

# Testing & Validation

The mac-setup repo provides multiple levels of testing, from quick local checks to full end-to-end runs in a clean macOS VM.

## make validate

Runs a fast local validation script (`scripts/validate.sh`) that checks the current system state without making any changes.

```bash
make validate
```

**What it checks:**

| Check              | What it verifies                                              |
| ------------------ | ------------------------------------------------------------- |
| Tools installed    | Core CLI tools are available on `$PATH`                       |
| Symlinks correct   | Config files point to the repo (not stale or broken)          |
| Env vars set       | Required variables exist in the shell environment             |
| Git config         | `.gitconfig` resolves correctly with personal/work profiles   |
| Directories exist  | `~/personal`, `~/work`, and other expected dirs are present   |
| Docker context     | Docker/Colima context is configured                           |
| Fonts              | Required fonts are installed                                  |
| macOS defaults     | Key system defaults match expected values                     |

## make test

Runs validation plus an Ansible syntax check on the playbook.

```bash
make test
```

This catches YAML syntax errors, undefined variables, and invalid module usage before running the playbook.

## make check

Performs a dry-run of the full playbook with diff output, showing what **would** change without actually changing anything.

```bash
make check
```

This is useful for reviewing changes before applying them, especially after editing role vars or templates.

## make test-vm

Runs a full end-to-end test in an isolated macOS virtual machine using [Tart](https://tart.run/).

```bash
make test-vm
```

**The flow:**

1. **Clone VM** -- Clones a clean macOS base image to a temporary VM
2. **Boot headless** -- Starts the VM without a GUI
3. **rsync repo** -- Copies the current repo state into the VM
4. **Create test `.zshenv`** -- Generates a `.zshenv` with test values for all required env vars
5. **Install Homebrew + Ansible** -- Bootstraps prerequisites inside the VM
6. **Run playbook** -- Executes the full `setup.yml` playbook
7. **Validate** -- Runs `scripts/validate.sh` inside the VM
8. **Teardown** -- Stops and deletes the temporary VM

This is the most thorough test. It verifies the entire setup flow from scratch, exactly as a new user would experience it. The first run downloads a macOS VM image (~15 GB).

## make test-vm-debug

Same as `make test-vm` but keeps the VM alive after the run completes. This is useful for SSH-ing into the VM to investigate failures.

```bash
make test-vm-debug
```

The VM IP address and SSH credentials are printed at the end. You can connect with:

```bash
ssh admin@<vm-ip>
```

After debugging, stop and delete the VM manually.

## Cleanup Check

The `setup.sh --cleanup` command identifies packages and extensions installed on the system that are not tracked in the mac-setup repo.

```bash
./setup.sh --cleanup
```

**How it works:**

1. **Homebrew formulae** -- Compares `brew leaves` (installed top-level packages) against the configured `homebrew_formulae` list
2. **VS Code extensions** -- Compares `code --list-extensions` output against the configured `vscode_extensions` list
3. **Interactive review** -- For each untracked item, prompts you to either add it to the repo config or uninstall it

This keeps your system and repo in sync. Run it periodically or after installing something manually via `brew install`.
