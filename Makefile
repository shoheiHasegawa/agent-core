.PHONY: test secrets-encrypt secrets-decrypt ws-new ws-harvest ws-clean ws-list zk-audit vault-peek tasks-list tasks-add tasks-complete tasks-update calendar-events brief-saturday install-hooks validate-skills validate-orphans validate-cleanliness validate-links validate-tests check-all

EPIC ?=
REPOS ?= core-service
ISSUE ?=
CORE_SERVICE_DIR ?= ../core-service
ENV_FILE ?= config/conf.env
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

# ---------------------------------------------------------
# Workspace & Worktree Harness (方式A)
# ---------------------------------------------------------
ws-new:
	@if [ -z "$(EPIC)" ]; then echo "Usage: make ws-new EPIC=<name> [REPOS=core-service,agent-core] [ISSUE=123]"; exit 1; fi
	@uv run python tools/workspace_manager.py new --epic "$(EPIC)" --repos "$(REPOS)" $(if $(ISSUE),--issue "$(ISSUE)",)

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
# Quality Gate & Architecture Validation (Seatbelt Protected)
# ---------------------------------------------------------
test: validate-tests

ifeq ($(YOU_INC_SANDBOX_ACTIVE),1)

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

else

MAKE_CMD := $(MAKE)

check-all validate-skills validate-orphans validate-cleanliness validate-links validate-tests:
	@uv run python tools/sandbox_runner.py --role worker --worktree "$(CURDIR)" -- $(MAKE_CMD) $@

endif
