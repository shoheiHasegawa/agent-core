.PHONY: secrets-encrypt secrets-decrypt ws-new ws-harvest ws-clean ws-list zk-audit vault-peek tasks-list tasks-add tasks-complete tasks-update calendar-events brief-saturday park-add park-list park-clear install-hooks validate-skills validate-orphans validate-cleanliness validate-links validate-tests check-all

EPIC ?=
REPOS ?= core-service
ISSUE ?=
OFFLINE ?=
RESET ?=
CORE_SERVICE_DIR ?= $(firstword $(wildcard ../core-service ../../../../core-service /Users/shoheihasegawa/you_inc/core-service))
ENV_FILE ?= $(firstword $(wildcard config/conf.env ../../config/conf.env ../../../../agent-core/config/conf.env /Users/shoheihasegawa/you_inc/agent-core/config/conf.env))
ARGS ?=

# ---------------------------------------------------------
# Official core-service CLI Wrappers (Stateless Execution)
# ---------------------------------------------------------
zk-audit:
	@PYTHONPATH="$(CORE_SERVICE_DIR)/src" uv run --project "$(CORE_SERVICE_DIR)" $(if $(wildcard $(ENV_FILE)),--env-file "$(ENV_FILE)",) python -m entrypoints.cli.main zk-audit

vault-peek:
	@PYTHONPATH="$(CORE_SERVICE_DIR)/src" uv run --project "$(CORE_SERVICE_DIR)" $(if $(wildcard $(ENV_FILE)),--env-file "$(ENV_FILE)",) python -m entrypoints.cli.main vault-peek

tasks-list:
	@PYTHONPATH="$(CORE_SERVICE_DIR)/src" uv run --project "$(CORE_SERVICE_DIR)" $(if $(wildcard $(ENV_FILE)),--env-file "$(ENV_FILE)",) python -m entrypoints.cli.main tasks-list $(ARGS)

tasks-add:
	@PYTHONPATH="$(CORE_SERVICE_DIR)/src" uv run --project "$(CORE_SERVICE_DIR)" $(if $(wildcard $(ENV_FILE)),--env-file "$(ENV_FILE)",) python -m entrypoints.cli.main tasks-add $(ARGS)

tasks-complete:
	@PYTHONPATH="$(CORE_SERVICE_DIR)/src" uv run --project "$(CORE_SERVICE_DIR)" $(if $(wildcard $(ENV_FILE)),--env-file "$(ENV_FILE)",) python -m entrypoints.cli.main tasks-complete $(ARGS)

tasks-update:
	@PYTHONPATH="$(CORE_SERVICE_DIR)/src" uv run --project "$(CORE_SERVICE_DIR)" $(if $(wildcard $(ENV_FILE)),--env-file "$(ENV_FILE)",) python -m entrypoints.cli.main tasks-update $(ARGS)

calendar-events:
	@PYTHONPATH="$(CORE_SERVICE_DIR)/src" uv run --project "$(CORE_SERVICE_DIR)" $(if $(wildcard $(ENV_FILE)),--env-file "$(ENV_FILE)",) python -m entrypoints.cli.main calendar-events $(ARGS)

brief-saturday:
	@PYTHONPATH="$(CORE_SERVICE_DIR)/src" uv run --project "$(CORE_SERVICE_DIR)" $(if $(wildcard $(ENV_FILE)),--env-file "$(ENV_FILE)",) python -m entrypoints.cli.main saturday-briefing $(ARGS)

park-add:
	@PYTHONPATH="$(CORE_SERVICE_DIR)/src" uv run --project "$(CORE_SERVICE_DIR)" $(if $(wildcard $(ENV_FILE)),--env-file "$(ENV_FILE)",) python -m entrypoints.cli.main park-add $(ARGS)

park-list:
	@PYTHONPATH="$(CORE_SERVICE_DIR)/src" uv run --project "$(CORE_SERVICE_DIR)" $(if $(wildcard $(ENV_FILE)),--env-file "$(ENV_FILE)",) python -m entrypoints.cli.main park-list $(ARGS)

park-clear:
	@PYTHONPATH="$(CORE_SERVICE_DIR)/src" uv run --project "$(CORE_SERVICE_DIR)" $(if $(wildcard $(ENV_FILE)),--env-file "$(ENV_FILE)",) python -m entrypoints.cli.main park-clear $(ARGS)

# ---------------------------------------------------------
# Workspace & Worktree Harness (方式A)
# ---------------------------------------------------------
ws-new:
	@if [ -z "$(EPIC)" ]; then echo "Usage: make ws-new EPIC=<name> [REPOS=core-service,agent-core] [ISSUE=123] [OFFLINE=1] [RESET=1]"; exit 1; fi
	@uv run python tools/workspace_manager.py new --epic "$(EPIC)" --repos "$(REPOS)" $(if $(ISSUE),--issue "$(ISSUE)",) $(if $(filter-out 0 false FALSE,$(OFFLINE)),--offline,) $(if $(filter-out 0 false FALSE,$(RESET)),--reset,)

ws-harvest:
	@if [ -z "$(EPIC)" ]; then echo "Usage: make ws-harvest EPIC=<name>"; exit 1; fi
	@uv run python tools/workspace_manager.py harvest --epic "$(EPIC)"

ws-clean:
	@if [ -z "$(EPIC)" ]; then echo "Usage: make ws-clean EPIC=<name>"; exit 1; fi
	@uv run python tools/workspace_manager.py clean --epic "$(EPIC)"

ws-list:
	@uv run python tools/workspace_manager.py list

# ---------------------------------------------------------
# Git Hook Installation
# ---------------------------------------------------------
install-hooks:
	@HOOKS_DIR=$$(git rev-parse --git-path hooks); \
	mkdir -p "$$HOOKS_DIR" && \
	cp tools/pre_handoff_verify.sh "$$HOOKS_DIR/pre-commit" && \
	chmod +x "$$HOOKS_DIR/pre-commit" && \
	echo "✅ Git pre-commit hook installed to $$HOOKS_DIR/pre-commit"

# ---------------------------------------------------------
# Secrets Management (sops)
# ---------------------------------------------------------
secrets-encrypt:
	@echo "Encrypting secrets..."
	@sops --encrypt --in-place .env || echo "Failed to encrypt. Check if .sops.yaml is configured and .env exists."

secrets-decrypt:
	@echo "Decrypting secrets..."
	@sops --decrypt --in-place .env || echo "Failed to decrypt. Check if you have the correct PGP/AGE keys."

# ---------------------------------------------------------
# Quality Gate & Architecture Validation
# ---------------------------------------------------------
validate-skills:
	@echo "Auditing skills..."
	@uv run python tools/audit_skills.py

validate-orphans:
	@echo "Auditing orphan scripts..."
	@uv run python tools/audit_orphan_scripts.py

validate-cleanliness:
	@echo "Validating cleanliness..."
	@uv run python tools/verify_cleanliness.py

validate-links:
	@echo "Validating markdown links..."
	@uv run python tools/check_markdown_links.py

validate-tests:
	@echo "Running unit tests..."
	@uv run python -m unittest discover -s tests -p "test_*.py"

check-all: validate-skills validate-orphans validate-cleanliness validate-links validate-tests
	@echo "✅ All agent-core Quality Gates passed!"
