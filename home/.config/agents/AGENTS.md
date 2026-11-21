# AGENTS.md — Global Agent Guidelines

Universal operating rules for Junie CLI and JetBrains AI agents.

## Core Rules
1. **Direct & Actionable**: Avoid unnecessary verbosity and unsolicited tutorials.
2. **Safety First**: Never commit secrets or force push without explicit confirmation.
3. **Use Modern CLI Tools**:
   - `rg` over grep
   - `fd` over find
   - `bat` over cat
   - `gh` for GitHub interactions
   - `mise` for tool runtime versioning
4. **Environment Awareness**: Read environment variables rather than guessing paths.
