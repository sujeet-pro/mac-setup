SHELL := /bin/zsh
.PHONY: setup update check validate test test-vm cleanup help install-creds uninstall-creds

help: ## Show this help
	@grep -E '^[a-zA-Z_-]+:.*?## .*$$' $(MAKEFILE_LIST) | awk 'BEGIN {FS = ":.*?## "}; {printf "  \033[36m%-12s\033[0m %s\n", $$1, $$2}'

setup: ## Full bootstrap from scratch (setup.sh)
	./setup.sh

update: ## Update packages and re-run playbook
	brew update
	. ~/.zshenv && ansible-playbook setup.yml --ask-become-pass

cleanup: ## Detect unmanaged packages and offer to add/remove them
	./setup.sh --cleanup

check: ## Dry-run: show what would change without applying
	. ~/.zshenv && ansible-playbook setup.yml --check --diff

validate: ## Quick validation of tools, configs, symlinks, and env vars
	@bash scripts/validate.sh

test: validate ## Local test: validate + Ansible syntax check
	@echo ""
	@echo "Ansible syntax check..."
	@ansible-playbook setup.yml --syntax-check
	@echo ""
	@echo "All local tests passed."

test-vm: ## Full end-to-end test in a clean Tart macOS VM
	./scripts/tart-test.sh

test-vm-debug: ## Same as test-vm but keeps VM alive for debugging
	./scripts/tart-test.sh --keep

CREDS_BIN_DIR := $(HOME)/.local/bin
CREDS_REPO_BIN := $(CURDIR)/configs/creds/_lib/bin

install-creds: ## Symlink creds_login_* / creds_validate into ~/.local/bin (manual fallback; the `creds` Ansible role does this automatically)
	@mkdir -p $(CREDS_BIN_DIR)
	@for f in $(CREDS_REPO_BIN)/*; do \
		name=$$(basename $$f); \
		ln -sfn $$f $(CREDS_BIN_DIR)/$$name; \
		echo "  linked $(CREDS_BIN_DIR)/$$name -> $$f"; \
	done
	@echo "Done. Make sure $(CREDS_BIN_DIR) is on your PATH."

uninstall-creds: ## Remove creds_* symlinks from ~/.local/bin
	@for f in $(CREDS_REPO_BIN)/*; do \
		name=$$(basename $$f); \
		target=$(CREDS_BIN_DIR)/$$name; \
		if [ -L $$target ]; then rm -f $$target && echo "  removed $$target"; fi; \
	done
